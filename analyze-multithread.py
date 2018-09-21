# -- coding: UTF-8 --
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.dates import DateFormatter, WeekdayLocator, \
    DayLocator, MONDAY, date2num, num2date
#from matplotlib.finance import candlestick_ohlc
import datetime
import numpy as np
from numpy import genfromtxt
import pandas as pd
import time
from draw import *
from utils import *
import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
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


def task(c, e_list, info):
    sp, sl = info['sp'], info['sl']
    buy_d, sell_d, buy_v, sell_v = info['buy_d'], info['sell_d'], info['buy_v'], info['sell_v']
    days = info['days']
    buy_func, sell_func = info['buy_func'], info['sell_func']

    is_print = False
    s = SellSignal(stop_profit_point=sp, stop_loss_point=sl, sell_func=sell_func, bar_del=sell_d)
    b = BuySignal(updown_thr=5, buy_func=buy_func, bar_del=buy_d)
    all_earn = []            

    for e, dt in enumerate(days.date):
        now_long_price = []
        earn = 0
        info_len = len(days.date[dt].high)
        buy_point_list = np.zeros((info_len))
        sell_point_list = np.zeros((info_len))
        for i in range(2, len(days.date[dt].high)):                    
            if b.run_val(now_long_price, days.date[dt], i, val_type=buy_v) == True:
                now_long_price += [days.date[dt].open[i]]
                buy_point_list[i] = -10
                continue
                
            if s.run_val(now_long_price, days.date[dt].close[i-1], days.date[dt], i, val_type=sell_v) == True:
                delta = np.sum(days.date[dt].open[i]-np.array(now_long_price))-1.5*len(now_long_price)
                earn += delta
                now_long_price = []
                sell_point_list[i] = -10 
                
        all_earn += [earn]
    all_earn = np.array(all_earn)*50
    return e_list, (round(np.mean(all_earn), 2), round(np.min(all_earn), 2), round(np.max(all_earn), 2), int(np.sum([1 for e in all_earn if e >0])), int(np.sum([1 for e in all_earn if e <0])))

def eval(days, buy_func, sell_func):
    print buy_func, sell_func
    sps = [8,9,10] 
    sps = range(0, 20)
    sls = [5,6,7] 
    sls = range(0, 20)
    buy_ds = range(-20, 10)
    sell_ds = range(-20, 10)
    buy_val = range(136)
    sell_val = range(3)
    score = np.zeros((len(sps), len(sls), len(buy_ds), len(sell_ds), len(buy_val), len(sell_val)))

    info = dict()
    info['sps'], info['sls'] = sps, sls
    info['buy_ds'], info['sell_ds'], info['buy_val'], info['sell_val'] = buy_ds, sell_ds, buy_val, sell_val
    info['days'] = days
    info['buy_func'], info['sell_func'] = buy_func, sell_func

    f = open('log.txt', 'w') 
    with ThreadPool(20) as pool:
        for e, v in pool.process_items_concurrently(info, process_func=task, max_items_in_flight=100):
            print e, v
            f.write('-'.join([str(ee) for ee in list(e)])+','+','.join([str(vv) for vv in list(v)])+'\n')
            score[e[0], e[1], e[2], e[3], e[4], e[5]] = v[0]

    f.close()
    if is_print == False:
        idx = np.where(np.max(score) == score)
        for i in range(len(idx[0])):
            print sps[idx[0][i]], sls[idx[1][i]], buy_ds[idx[2][i]], sell_ds[idx[3][i]], buy_val[idx[4][i]], sell_val[idx[5][i]], np.max(score)

eval(days, buy_func='KD_GC', sell_func='KD_DC')
