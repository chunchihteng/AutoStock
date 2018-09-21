# -- coding: UTF-8 --
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.dates import DateFormatter, WeekdayLocator, \
    DayLocator, MONDAY, date2num, num2date
from matplotlib.finance import candlestick_ohlc
import datetime
import numpy as np
from numpy import genfromtxt
import pandas as pd
import time
from draw import *
from utils import *
import matplotlib.pyplot as plt
from matplotlib.finance import candlestick_ohlc
import os
from Analyze import *
from Pattern import *
import traceback
from MultiThread import *

import pickle
data = pd.read_csv('TX00/TX00_50000.csv') #, encoding='utf-8')
items = [i for i in data]
time = data[items[0]]
infos = dict()
idx = []

sign = dict()
sign['up'] = data['Up-Down'][4][:2]
sign['down'] = data['Up-Down'][1][:2]
sign['K_up'] = data['9-K'][5][-2:]
sign['K_down'] = data['9-K'][0][-2:]

load_data = False
if load_data == True:
    days = Days()
    for i in range(50000):
        h, m = time[i].split(' ')[-1].split(':')[0], time[i].split(' ')[-1].split(':')[1]
        dt = time[i].split(' ')[0]
        if 8*60+45 <= int(h)*60+int(m) <= 13*60+45: #13*60+45:
            idx += [i]
        else:
            continue
        d = process(data, i, sign)
        print i, d
        days.update(dt, d)


    with open('0917-infos_50000.pkl', 'wb') as output:
        pickle.dump(days, output, pickle.HIGHEST_PROTOCOL)
else:
    with open('0917-infos_50000.pkl', 'rb') as input:
        days = pickle.load(input)

def draw_plot(data, buy_point_list, sell_point_list):
    fig = plt.figure(figsize=(20,10)); ax = plt.subplot2grid((6,4),(1,0),rowspan=4, colspan=4)
    fig.set_size_inches(20,10)
    price = []
    for i in range(len(data.high)):
        price += [[data.open[i], data.high[i], data.low[i], data.close[i]]]
    price = np.array(price)
    low_price = np.min(price)
    price = price - low_price
    date = np.arange(len(price)) 
    
    K_graph = np.concatenate((date.reshape(len(price), 1), price), axis=1)
    candlestick_ohlc(ax, K_graph, width=0.6, colorup='r', colordown='black')
    ax.plot(date.tolist(), data.MA5-low_price, c='black', lw=0.8)
    ax.plot(date.tolist()[19:], data.MA20-low_price, c='blue', lw=0.8)
    ax.bar(date.tolist(), buy_point_list.tolist(), color='green')
    ax.bar(date.tolist(), sell_point_list.tolist(), color='purple')
    plt.show()
    
    fig1 = plt.figure(figsize=(20,3)); ax1 = plt.subplot2grid((6,4),(1,0),rowspan=4, colspan=4)
    ax1.plot(date.tolist(), map(abs, data.K), c='red', lw=0.8)
    ax1.plot(date.tolist(), map(abs, data.D), c='blue', lw=0.8)
    ax1.plot(date.tolist(), 3*np.array(map(abs, data.D))-2*np.array(map(abs, data.K)), c='green', lw=0.8)
    ax1.plot(date.tolist(), np.ones(len(date))*50, c='black', lw=0.8)
    plt.show()

    fig2 = plt.figure(figsize=(20,3)); ax2 = plt.subplot2grid((6,4),(1,0),rowspan=4, colspan=4)
    ax2.plot(date.tolist(), map(abs, data.RSI), c='red', lw=0.8)
    ax2.plot(date.tolist(), np.ones(len(date))*50, c='black', lw=0.8)
    plt.show()

def task(c, e1, e2, e3, sp, sl, d, days, buy_func, sell_func):
    is_print = False
    s = SellSignal(stop_profit_point=sp, stop_loss_point=sl, sell_func=sell_func)
    b = BuySignal(updown_thr=5, buy_func=buy_func, bar_del=d)
    all_earn = []            

    for e, dt in enumerate(days.date):
        now_long_price = []
        earn = 0
        info_len = len(days.date[dt].high)
        buy_point_list = np.zeros((info_len))
        sell_point_list = np.zeros((info_len))
        for i in range(2, len(days.date[dt].high)):                    
            if b.run_val(now_long_price, days.date[dt], i) == True:
                now_long_price += [days.date[dt].open[i]]
                buy_point_list[i] = -10
                if is_print == True:
                    print "buy", i, now_long_price
                continue
                
            #print "cur", i, days.date[dt].open[i], now_long_price
            if s.run_val(now_long_price, days.date[dt].close[i-1], days.date[dt], i) == True:
                delta = np.sum(days.date[dt].open[i]-np.array(now_long_price))-4.5*len(now_long_price)
                earn += delta
                if is_print == True:
                    print "earn", days.date[dt].open[i], delta
                now_long_price = []
                sell_point_list[i] = -10 
                
        all_earn += [earn]
        if is_print == True:
            print dt, earn
            draw_plot(days.date[dt], buy_point_list, sell_point_list)
    all_earn = np.array(all_earn)*50
#     print all_earn
#     print (e1, e2, e3), all_earn
    return (e1, e2, e3), (round(np.mean(all_earn), 2), round(np.min(all_earn), 2), round(np.max(all_earn), 2), np.sum([1 for e in all_earn if e >=0]), np.sum([1 for e in all_earn if e <=0]))

def eval(days, buy_func, sell_func):
    print buy_func, sell_func
    sps = [4] 
    sps = range(0, 60)
    sls = [14] 
    sls = range(0, 60)
    ds = [4] 
    ds = range(-10, 11)
    score = np.zeros((len(sps), len(sls), len(ds)))
    is_print = False
    max_earn = -500000
    
                
    with ThreadPool(10) as pool:
        for e, v in pool.process_items_concurrently(sps, sls, ds, days, buy_func, sell_func, process_func=task, max_items_in_flight=100):
            if v[0] >= 0:
                print e, v 
            score[e[0], e[1], e[2]] = v[0]
            if e[2] == ds[-1]:
                print e
#             if e[1] == 59:
#                 fig1 = plt.figure(figsize=(20,3)); ax1 = plt.subplot2grid((6,4),(1,0),rowspan=4, colspan=4)
#                 ax1.plot(range(len(score)), score[e[0], :, 0], c='red', lw=0.8)
#                 plt.show()
    
#     print task(0, 0, 0, 0, 8, 27, 4, days, buy_func, sell_func)
    np.save('KD_GC.npy', score)
    if is_print == False:
        idx = np.where(np.max(score) == score)
        for i in range(len(idx[0])):
            print idx[0][i], idx[1][i], idx[2][i], np.max(score)
eval(days, buy_func='KD_GC', sell_func='KD_DC')
