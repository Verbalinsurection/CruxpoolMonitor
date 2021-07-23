#!/usr/bin/python3

from datetime import datetime

import CruxpoolFetcher as CF
import CryptoWalletFetcher as CWF
from logger import LOG


class Data():
    __date_time_format = "%Y-%m-%dT%H:%M:%S.%fZ"

    def __init__(self, wallet, fiat_code, theorical, pay_amount):
        self.__coin_info = CWF.Coin(fiat_code, 'ravencoin')
        self.__pool_info = CF.CruxpoolHelper(
            'rvn', wallet, theorical, pay_amount)
        self.__wallet_info = CWF.RvnWallet(wallet)
        self.__theorical = theorical
        self.__status = {}

    def update(self):
        dt_update = datetime.utcnow().strftime(self.__date_time_format)

        try:
            LOG.debug('Update coin info')
            if self.__coin_info.update():
                self.__status.update(
                    {'coin': self.__coin_info.last_update.strftime(
                        self.__date_time_format)})
            else:
                LOG.warning('Update coin info failed: ' +
                            str(self.__coin_info.last_error))
        except AttributeError as e:
            LOG.warning('Update coin info failed: ' + str(e))

        try:
            LOG.debug('Update pool info')
            if self.__pool_info.update():
                self.__status.update(
                    {'pool': self.__pool_info.stat_time.strftime(
                        self.__date_time_format)})
            else:
                LOG.warning('Update pool info failed: ' +
                            str(self.__pool_info.last_error))
        except AttributeError as e:
            LOG.warning('Update pool info failed: ' + str(e))

        try:
            LOG.debug('Update wallet info')
            if self.__wallet_info.update():
                self.__status.update({'wallet': dt_update})
            else:
                LOG.warning('Update wallet info failed: ' +
                            str(self.__wallet_info.last_error))
        except AttributeError as e:
            LOG.warning('Update wallet info failed: ' + str(e))

    def __data_status(self, dt_point):
        fields = {}
        for entry in self.__status:
            fields[entry] = self.__status[entry]

        return {
            'measurement': 'status',
            'time': dt_point,
            'fields': fields,
        }

    def __data_wallet(self, dt_point):
        fields = {}
        fields['balance_crypto'] = self.__wallet_info.balance
        fields['balance_fiat'] = round(
            self.__wallet_info.balance * self.__coin_info.price, 2)

        return {
            'measurement': 'wallet',
            'time': dt_point,
            'fields': fields,
            'tags': {
                'wallet': self.__wallet_info.wallet,
                'fiat': self.__coin_info.fiat,
            }
        }

    def __data_coin(self, dt_point):
        fields = {}
        fields['price'] = self.__coin_info.price
        fields['ath'] = self.__coin_info.ath
        fields['pc_24h'] = self.__coin_info.pc_24h

        return {
            'measurement': 'coin',
            'time': dt_point,
            'fields': fields,
            'tags': {
                'fiat': self.__coin_info.fiat,
            }
        }

    def __data_pool_info(self, dt_point):
        fields = {}
        fields['reported'] = self.__pool_info.hrate_reported
        fields['actual'] = self.__pool_info.hrate_current
        fields['reference'] = self.__pool_info.hrate_ref
        fields['valid'] = self.__pool_info.valid_shares
        fields['stale'] = self.__pool_info.stale_shares
        fields['reject'] = self.__pool_info.invalid_shares
        fields['unpaid'] = self.__pool_info.balance
        fields['hrate_3h'] = self.__pool_info.hrate_3h
        fields['hrate_day'] = self.__pool_info.hrate_day
        fields['coin_min'] = self.__pool_info.coin_min
        fields['earn_hour'] = self.__pool_info.earn_hour
        fields['earn_day'] = self.__pool_info.earn_day
        fields['earn_month'] = self.__pool_info.earn_month
        fields['earn_week'] = self.__pool_info.earn_week
        fields['next_payout'] = datetime.isoformat(
                    self.__pool_info.next_payout)
        fields['unpaid_next'] = self.__pool_info.unpaid_at_next

        return {
            'measurement': 'pool',
            'time': dt_point,
            'fields': fields,
            'tags': {
                'wallet': self.__pool_info.wallet,
                'pool': self.__pool_info.pool_name,
            }
        }

    def __data_worker_info(self, dt_point, worker):
        fields = {}
        fields['reported'] = worker.hrate_reported
        fields['actual'] = worker.hrate_current
        fields['hrate_3h'] = worker.hrate_3h
        fields['hrate_day'] = worker.hrate_day
        fields['valid'] = worker.shares
        fields['stale'] = worker.stale_shares
        fields['reject'] = worker.invalid_shares

        return {
            'measurement': 'worker',
            'time': dt_point,
            'fields': fields,
            'tags': {
                'wallet': self.__pool_info.wallet,
                'pool': self.__pool_info.pool_name,
                'worker': worker.name,
            }
        }

    def __data_payout(self, dt_point, payout):
        fields = {}
        fields['amount'] = payout.amount

        return {
            'measurement': 'payouts',
            'time': datetime.isoformat(payout.paid_on),
            'fields': fields,
            'tags': {
                'wallet': self.__pool_info.wallet,
                'pool': self.__pool_info.pool_name,
            }
        }

    @property
    def formated_data(self):
        dt_point = datetime.utcnow().strftime(self.__date_time_format)

        data_points = []
        try:
            data_points.append(self.__data_wallet(dt_point))
            data_points.append(self.__data_coin(dt_point))
            data_points.append(self.__data_pool_info(dt_point))
            for worker in self.__pool_info.workers:
                data_points.append(self.__data_worker_info(dt_point, worker))
            self.__status.update({'data': dt_point})
            data_points.append(self.__data_status(dt_point))
        except AttributeError as e:
            LOG.error('Unable to create data points: ' + str(e))
            return None

        return data_points

    @property
    def formated_payouts(self):
        dt_point = datetime.utcnow().strftime(self.__date_time_format)

        data_points = []
        try:
            for payout in self.__pool_info.payouts:
                data_points.append(self.__data_payout(dt_point, payout))
        except AttributeError as e:
            LOG.error('Unable to create data points: ' + str(e))
            return None

        return data_points
