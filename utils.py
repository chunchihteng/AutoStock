import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.dates import DateFormatter, WeekdayLocator, \
    DayLocator, MONDAY, date2num, num2date
from mpl_finance import candlestick_ohlc
import datetime
import numpy as np
from numpy import genfromtxt
import os
import pandas as pd
import time
from collections import OrderedDict


def get_stock(file_list_name):
	stock_name = []
	stock_list = dict()
	for s in np.loadtxt(file_list_name):
		path = os.path.join('data', str(int(s))+'.csv')
		if os.path.isfile(path) is True:
			stock_name.append(str(int(s)))
			stock_list[str(int(s))] = path
	return stock_name, stock_list

def processDate(ch_time):
    t = ch_time.split("/")
    return "%d%s%s"%(int(t[0])+1911, t[1].zfill(2), t[2].zfill(2))

def get_stock_data(stock_list, stock_no, end_dt):
	data = pd.read_csv(stock_list[str(stock_no)], sep='\n')

	date, volume, price = [], [], []

	for e, row in enumerate(data.values):
		try:
			items = row[0].split(",")
			if "--" in items or "---" in items:
				continue
			if processDate(items[0]) == "20180113":
				continue

			date += [processDate(items[0])]
			volume += [int(float(items[1]))]
			price += [[float(items[3]), float(items[4]), float(items[5]), float(items[6])]]

		except Exception as e: 
			print(e)

	date, volume, price = np.array(date), np.array(volume), np.array(price)

	date_correct, idx = True, -1
	while end_dt >= 19800101:
		find_idx = np.where(date == str(end_dt))[0]
		if len(find_idx) == 0: # not exists
			end_dt -= 1
			date_correct = False
		else:
			idx = find_idx[0]
			break

	if idx == -1:
		return np.array([]), np.array([]), np.array([]), False

	date, volume, price = date[:idx+1], volume[:idx+1], price[:idx+1]
	d2n = date2num(datetime.date(end_dt//10000, (end_dt%10000)//100, end_dt%100))
	date2n = np.array([[float(i)] for i in range(int(d2n)-len(date)+1, int(d2n)+1, 1)])
	return date2n, volume, price, date_correct
