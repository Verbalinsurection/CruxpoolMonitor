#!/usr/bin/python3

from influxdb import InfluxDBClient, exceptions
from logger import LOG


class Idbc():
    """Class idbc (InfluxDB Client)."""

    def __init__(self, if_db, if_host, if_user, if_pass, if_port=8086):
        """Init idbc class."""
        self.__db = if_db
        self.__client = InfluxDBClient(
            if_host, if_port, if_user, if_pass, if_db)
        self.__init_db()

    def write_data(self, data_points, policy=None):
        self.last_error = None
        try:
            return self.__client.write_points(data_points, None, None, policy)
        except (ConnectionError, exceptions.InfluxDBClientError) as e:
            self.last_error = str(e)
            return False

    def purge(self):
        self.last_error = None
        try:
            self.__client.drop_database(self.__db)
            self.__client.create_database(self.__db)
            self.__init_db()
        except (ConnectionError, exceptions.InfluxDBClientError) as e:
            self.last_error = str(e)
            return False

    def __init_db(self):
        daily_found = False
        for policy in self.__client.get_list_retention_policies():
            LOG.debug('Retention policy found: ' + policy['name'])
            LOG.debug('  Duration: ' + policy['duration'])
            LOG.debug('  Default: ' + str(policy['default']))

            if policy['name'] == 'daily':
                daily_found = True

            if policy['name'] == 'autogen' \
                    and policy['duration'] != '960h0m0s':
                LOG.info('Modify autogen policy')
                self.__client.alter_retention_policy(
                    'autogen', self.__db, '40d', 1, True)
            elif policy['name'] == 'daily' \
                    and policy['duration'] != '0s':
                LOG.info('Modify daily policy')
                self.__client.alter_retention_policy(
                    'daily', self.__db, 'INF', 1, False)

        if not daily_found:
            LOG.info('Create daily policy')
            self.__client.create_retention_policy('daily', 'INF', 1)

        cq_gain = 'SELECT (last(unpaid) - min(unpaid))' \
            ' + ((max(unpaid) - first(unpaid))' \
            ' * (ceil((last(unpaid) - min(unpaid))' \
            ' / (max(unpaid) - first(unpaid))) - 1)) AS daily_gain' \
            ' INTO ' + self.__db + '.daily.pool' \
            ' FROM ' + self.__db + '.autogen.pool' \
            ' GROUP BY time(1d)'

        cq_wallet = 'SELECT max(balance_fiat) AS balance_fiat, ' \
            'max(balance_eth) AS balance_eth' \
            ' INTO ' + self.__db + '.daily.wallet' \
            ' FROM ' + self.__db + '.autogen.wallet' \
            ' GROUP BY time(1d)'

        cq_gain_comp = 'CREATE CONTINUOUS QUERY downsample_gain' \
            ' ON ethereum_mining BEGIN ' + cq_gain + ' END'
        cq_wallet_comp = 'CREATE CONTINUOUS QUERY downsample_wallet' \
            ' ON ethereum_mining BEGIN ' + cq_wallet + ' END'

        cq_gain_found = False
        cq_wallet_found = False
        for l_cq in self.__client.get_list_continuous_queries():
            if self.__db not in l_cq:
                continue
            for cq in l_cq[self.__db]:
                LOG.debug('Continuous query found: ' + cq['name'])
                LOG.debug('  Query: ' + cq['query'])
                if cq['name'] == 'downsample_gain':
                    cq_gain_found = True
                elif cq['name'] == 'downsample_wallet':
                    cq_wallet_found = True

                if cq['name'] == 'downsample_gain' \
                        and cq['query'] != cq_gain_comp:
                    LOG.info('Modify continuous query for gain')
                    self.__client.drop_continuous_query('downsample_gain')
                    self.__client.create_continuous_query('downsample_gain',
                                                          cq_gain)
                elif cq['name'] == 'downsample_wallet' \
                        and cq['query'] != cq_wallet_comp:
                    LOG.info('Modify continuous query for wallet')
                    self.__client.drop_continuous_query('downsample_wallet')
                    self.__client.create_continuous_query('downsample_wallet',
                                                          cq_wallet)

        if not cq_gain_found:
            LOG.info('Create continuous query for gain')
            self.__client.create_continuous_query('downsample_gain',
                                                  cq_gain)

        if not cq_wallet_found:
            LOG.info('Create continuous query for wallet')
            self.__client.create_continuous_query('downsample_wallet',
                                                  cq_wallet)
