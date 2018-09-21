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

# from func import compute
from func import *

def draw_volume(volume, date, color, duration, ax):
	data = np.array([float(d) for d in volume[-duration:]])  
	ax.bar(np.squeeze(date[-duration:]), data, color=color[-duration:])
   
def draw_plot(date, volume, price, duration, indicator=None):
    
	mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
	alldays = DayLocator()              # minor ticks on the days
	dayFormatter = DateFormatter('%d')      # e.g., 12
	weekFormatter = DateFormatter('%b %d')  # e.g., Jan 12

	fig = plt.figure(figsize=(20,10)); ax = plt.subplot2grid((6,4),(1,0),rowspan=4, colspan=4)
	fig.set_size_inches(20,10)

	K_graph = np.concatenate((date, price), axis=1)[-duration:]   
	candlestick_ohlc(ax, K_graph, width=0.6, colorup='r', colordown='black')

	close_p = price[:,3]
	open_p = price[:,0]
	high_p = price[:,1]
	low_p = price[:,2]
	infos = indicator_line(close_p, indicator, duration)
	lines = []
	for e, info in enumerate(infos):
		lines += [ax.plot(date[-duration:], info[0], c=info[1], lw=0.8, label=indicator[e][0]+'-'+str(indicator[e][1]))]
	handles, labels = ax.get_legend_handles_labels()
	ax.legend(handles, labels)
	plt.show()

	fig1 = plt.figure(figsize=(20,3)); ax1 = plt.subplot2grid((6,4),(1,0),rowspan=4, colspan=4)
	m = close_p >= open_p
	v_color = []
	for e, mm in enumerate(m):
		if mm == True:
			v_color.append('red')
		else:
			v_color.append('black')

	draw_volume(volume, date, v_color, duration, ax1)
	plt.show()
