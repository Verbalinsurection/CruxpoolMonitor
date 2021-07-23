#!/usr/bin/python3

# import CruxpoolFetcher as CF
from data_colector import Data

__version__ = '1.0.0'


data = Data('RFTFnUwbUM7KGXQTS14cbRaHGK94CGKeA3', 'eur', 100, 50)
data.update()

print(data.formated_data)
print(data.formated_payouts)
