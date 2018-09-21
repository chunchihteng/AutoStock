import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.dates import DateFormatter, WeekdayLocator, \
    DayLocator, MONDAY, date2num, num2date
from matplotlib.finance import candlestick_ohlc
import datetime
import numpy as np
from numpy import genfromtxt
import os
import pandas as pd
import time
from collections import OrderedDict

def predict_price(open_p, close_p, high_p, previous_day=0, display=False):
	if previous_day != 0:
		open_p = open_p[:previous_day]; close_p = close_p[:previous_day]; high_p = high_p[:previous_day]
	item = [">10MA", ">20MA", ">60MA", "RSI GX", "10-20 GX", "20-60 GX", "10-60 GX", "H.Y. Highest"] #"diverge", "Previous High Peak"]
	fullfill = []
	print_info = OrderedDict()
	print_info['done'] = 0; print_info['<2%'] = 0; print_info['2%~5%'] = 0; print_info['5%~8%'] = 0; print_info['>8%'] = 0
	info = dict()

	for i in item:        
		if ">10MA" == i: bottleneck = MA(close_p, 9, 1)[-1]
		elif ">20MA" == i: bottleneck = MA(close_p, 19, 1)[-1]
		elif ">60MA" == i: bottleneck = MA(close_p, 59, 1)[-1]
		elif "diverge" == i: bottleneck = max(2*close_p[-10]-close_p[-20], 1.2*close_p[-10]-0.2*close_p[-60], 1.5*close_p[-20]-0.5*close_p[-60])
		elif "RSI GX" == i:
			up, down = (close_p >= open_p)*close_p, (close_p < open_p)*close_p
			RSI6, RSI12 = np.sum(up[-6:])/(np.sum(up[-6:])+np.sum(down[-6:])), np.sum(up[-12:])/(np.sum(up[-12:])+np.sum(down[-12:]))
			if RSI6 >= RSI12:
				bottleneck = close_p[-1]
			else:
				if np.sum(up[-11:-5])+np.sum(down[-11:-5]) < 0:
					continue
				bottleneck = (np.sum(up[-11:])*np.sum(down[-5:])-np.sum(up[-5:])*np.sum(down[-11:]))/(np.sum(up[-11:-5])+np.sum(down[-11:-5]))
		elif "10-20 GX" == i: bottleneck = np.sum(close_p[-19:-9])-np.sum(close_p[-9:])
		elif "20-60 GX" == i: bottleneck = np.sum(close_p[-59:-19])/2.0-np.sum(close_p[-19:])
		elif "10-60 GX" == i: bottleneck = np.sum(close_p[-59:-9])/5.0-np.sum(close_p[-9:])
		elif "H.Y. Highest" == i: bottleneck = max(close_p[-280:])
		elif "Previous High Peak" == i:
			it = -2
			bottleneck = 0
			while it > -250:
				if high_p[it] > high_p[it-1] and high_p[it] > high_p[it+1]:
					bottleneck = high_p[it]
					if high_p[it] >= close_p[-1]:
						bottleneck = high_p[it]
						break
					it -= 1

			if bottleneck == 0:
				bottleneck = close_p[it]
		if display is True: print i, bottleneck, bottleneck-close_p[-1]

		grow_ratio = round(((bottleneck-close_p[-1])/close_p[-1])*100.0,2)

		if grow_ratio <= 0: 
			fullfill.append(i)
			print_info['done'] += 1
			continue
		elif grow_ratio < 2: print_info['<2%'] += 1
		elif grow_ratio < 5: print_info['2%~5%'] += 1
		elif grow_ratio < 8: print_info['5%~8%'] += 1
		else: print_info['>8%'] += 1
		info[i] = grow_ratio

	value = print_info['>8%']*1e4+print_info['5%~8%']*1e3+print_info['2%~5%']*1e2+print_info['<2%']*1e1+print_info['done']
	return fullfill, info, print_info, value, [MA(close_p, 10, 5), MA(close_p, 20, 5), MA(close_p, 60, 5)]


