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

	open_p, high_p, low_p, close_p = price[:,0], price[:,1], price[:,2], price[:,3]
	infos = indicator_line(close_p, indicator, duration)
	for info in infos:
		ax.plot(date[-duration:], info[0], c=info[1], lw=0.8)
	plt.show()

	fig1 = plt.figure(figsize=(20,3)); ax1 = plt.subplot2grid((6,4),(1,0),rowspan=4, colspan=4)
	peak = np.array([idx for idx in range(1, len(high_p)-1) if high_p[idx-1] <= high_p[idx] and high_p[idx] >= high_p[idx+1]])
	bottom = np.array([idx for idx in range(1, len(low_p)-1) if low_p[idx-1] >= low_p[idx] and low_p[idx] <= low_p[idx+1]])
	mapp = np.zeros((len(low_p)))
	for p in peak: mapp[p] = 1
	for b in bottom: mapp[b] = -1

	m = close_p >= open_p
	v_color = []
	for e, mm in enumerate(m):
		if e in peak:
			v_color.append('green')
		elif e in bottom:
			v_color.append('brown')
		else:
			v_color.append('white')
		# elif mm == True:
		# 	v_color.append('red')
		# else:
		# 	v_color.append('black')

	for e1, b in enumerate(bottom[:-2]):
		b1, b2, b3 = b, bottom[e1+1], bottom[e1+2]
		for e2 in range(len(peak)-1):
			if b1 < peak[e2] < b2 and b2 < peak[e2+1] < b3:
				if high_p[b1] < close_p[b2]:
					v_color[b1] = 'purple'

		# try:

		# 	nearest_peak = i+1+np.where(mapp[i+1:]==1)
		# 	second_nearest_peak = nearest_peak+1+np.argmax(mapp[nearest_peak+1:])
		# 	nearest_bottom = i+1+np.argmin(mapp[i+1:])
		# 	if nearest_peak > nearest_bottom:
		# 		continue
		# 	if nearest_bottom > second_nearest_peak:
		# 		continue
		# 	if close_p[i] > close_p[nearest_bottom]:
		# 		continue
		# 	if close_p[i] < open_p[i]:
		# 		continue
		# 	# print nearest_peak, nearest_bottom
		# 	v_color[i] = 'purple'
		# except:
		# 	continue
		

	draw_volume(volume, date, v_color, duration, ax1)
	plt.show()