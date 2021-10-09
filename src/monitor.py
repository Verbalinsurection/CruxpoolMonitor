#!/usr/bin/python3

from time import sleep

import schedule

from config import conf
from data_colector import Data
from influx import Idbc
from logger import LOG
import CruxpoolFetcher as CF


__version__ = '1.1.7'


def data_process():
    LOG.debug('Starting data process')

    idbc = Idbc(conf.influx_db,
                conf.influx_host,
                conf.influx_user,
                conf.influx_pass,
                conf.influx_port)

    rvndata = Data(conf.wallet,
                   conf.fiat,
                   conf.theorical_hrate,
                   conf.pay_amount,
                   conf.coin,
                   conf.coin_full)

    rvndata.update()

    formated_data = rvndata.formated_data
    if formated_data is None:
        LOG.error('No data for InfluxDb')
        return
    for data_line in formated_data:
        LOG.debug(data_line)

    LOG.debug('Writing data to InfluxDb')
    if not idbc.write_data(formated_data):
        LOG.error('Error on writing data to InfluxDb')
        LOG.error(idbc.last_error)

    formated_payouts = rvndata.formated_payouts
    if formated_payouts is None:
        LOG.error('No payouts data for InfluxDb')
        return
    for data_line in formated_payouts:
        LOG.debug(data_line)

    LOG.debug('Writing payouts data to InfluxDb')
    if not idbc.write_data(formated_payouts, 'daily'):
        LOG.error('Error on writing data to InfluxDb')
        LOG.error(idbc.last_error)

    formated_history = rvndata.formated_history
    if formated_history is None:
        LOG.error('No history data for InfluxDb')
        return
    for data_line in formated_history:
        LOG.debug(data_line)

    LOG.debug('Writing history data to InfluxDb')
    if not idbc.write_data(formated_history, 'daily'):
        LOG.error('Error on writing data to InfluxDb')
        LOG.error(idbc.last_error)

    LOG.debug('Data process done')


if __name__ == "__main__":
    if len(conf.error) > 0:
        for err in conf.error:
            LOG.critical('Environment variable not set: ' + err)
        exit(1)

    title = 'Ravencoin Mining Monitor - ' + __version__
    fetcher_version = '(fetcher version: ' + CF.__version__ + ')'

    LOG.info('╔' + '═' * 78 + '╗')
    LOG.info('║' + title.center(78, ' ') + '║')
    LOG.info('║' + fetcher_version.center(78, ' ') + '║')
    LOG.info('╟' + '─' * 78 + '╢')
    for confentry in conf.conf_array:
        LOG.info('║ ' + confentry[0].ljust(18) +
                 '\t-> ' + str(confentry[1]).ljust(54) + '║')
    LOG.info('╚' + '═' * 78 + '╝')

    if conf.purge == "PURGE":
        LOG.warning('Purge DB')
        idbc = Idbc(conf.influx_db,
                    conf.influx_host,
                    conf.influx_user,
                    conf.influx_pass,
                    conf.influx_port)
        idbc.purge()

    data_process()

    schedule.every(conf.schedule_update).seconds.do(data_process)

    while True:
        schedule.run_pending()
        sleep(1)
