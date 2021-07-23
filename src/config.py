#!/usr/bin/python3

from os import environ


class Config():
    def __init__(self):
        self.__cf_wallet = \
            ['WALLET', environ.get('WALLET', None)]
        self.__cf_coin = \
            ['COIN', environ.get('COIN', 'eth')]
        self.__cf_coin_full = \
            ['COIN_FULL', environ.get('COIN_FULL', 'ethereum')]
        self.__cf_fiat = \
            ['FIAT', environ.get('FIAT', 'usd')]
        self.__cf_theorical_hrate = \
            ['THEORICAL_HRATE', float(environ.get('THEORICAL_HRATE', 100))]
        self.__cf_pay_amount = \
            ['PAY_AMOUNT', int(environ.get('PAY_AMOUNT', 50))]
        self.__cf_influx_host = \
            ['INFLUX_HOST', environ.get('INFLUX_HOST', None)]
        self.__cf_influx_db = \
            ['INFLUX_DB', environ.get('INFLUX_DB', None)]
        self.__cf_influx_port = \
            ['INFLUX_PORT', int(environ.get('INFLUX_PORT', 8086))]
        self.__cf_influx_user = \
            ['INFLUX_USER', environ.get('INFLUX_USER', None)]
        self.__cf_influx_pass = \
            ['INFLUX_PASS', environ.get('INFLUX_PASS', None)]
        self.__cf_schedule_update = \
            ['SCHEDULE_UPDATE_S', int(environ.get('SCHEDULE_UPDATE_S', 60))]
        self.__cf_purge = \
            ['PURGE', environ.get('PURGE', "")]
        self.__error = []
        self.__check_config()

    def __check_config(self):
        for entry in filter(lambda ent: '__cf_' in ent, self.__dict__):
            if self.__dict__[entry][1] is None:
                self.__error.append(self.__dict__[entry][0])

    @property
    def conf_array(self):
        conf_array = []
        for entry in filter(lambda ent: '__cf_' in ent, self.__dict__):
            conf_array.append(
                [self.__dict__[entry][0], self.__dict__[entry][1]])
        return conf_array

    @property
    def wallet(self):
        return self.__cf_wallet[1]

    @property
    def fiat(self):
        return self.__cf_fiat[1]

    @property
    def coin(self):
        return self.__cf_coin[1]

    @property
    def coin_full(self):
        return self.__cf_coin_full[1]

    @property
    def pay_amount(self):
        return self.__cf_pay_amount[1]

    @property
    def theorical_hrate(self):
        return self.__cf_theorical_hrate[1]

    @property
    def influx_host(self):
        return self.__cf_influx_host[1]

    @property
    def influx_db(self):
        return self.__cf_influx_db[1]

    @property
    def influx_port(self):
        return self.__cf_influx_port[1]

    @property
    def influx_user(self):
        return self.__cf_influx_user[1]

    @property
    def influx_pass(self):
        return self.__cf_influx_pass[1]

    @property
    def schedule_update(self):
        return self.__cf_schedule_update[1]

    @property
    def purge(self):
        return self.__cf_purge[1]

    @property
    def error(self):
        return self.__error


conf = Config()
