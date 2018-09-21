# -- coding: UTF-8 --
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.dates import DateFormatter, WeekdayLocator, \
    DayLocator, MONDAY, date2num, num2date
from mpl_finance import candlestick_ohlc
import datetime
import numpy as np
from numpy import genfromtxt
import time
from draw import *
from utils import *
import os
import pandas as pd
import Pattern
from collections import OrderedDict

class OneDay():
    def __init__(self, ):
        self.open = []
        self.high = []
        self.low = []
        self.close = []
        self.updown = []
        self.vol = []
        self.MA5 = []
        self.MA10 = []
        self.K = []
        self.D = []
        self.RSI = []
        self.MA20 = []
    def add(self, o, h, l, c, ud, v, m5, m10, k, d, r):
        self.open = [o] + self.open
        self.high = [h] + self.high
        self.low = [l] + self.low
        self.close = [c] + self.close
        self.updown = [ud] + self.updown
        self.vol = [v] + self.vol
        self.MA5 = [m5] + self.MA5
        self.MA10 = [m10] + self.MA10
        self.K = [k] + self.K
        self.D = [d] + self.D
        self.RSI = [r] + self.RSI
        if len(self.close) >= 20:
            self.MA20 = [np.mean(self.close[:20])] + self.MA20



class Days():
    def __init__(self):
        self.date = OrderedDict() #dict()

    def update(self, date, data):
        if date not in self.date:
            self.date[date] = OneDay()
        self.date[date].add(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10])

def process_ud(data):
    global sign
    if len(data) == 1:
        return 0
    else:
        if data[:2] == sign['up']:
            return int(data[2:])
        elif data[:2] == sign['down']:
            return -int(data[2:])

def process_KD(data):
    global sign
    for i in range(len(data)):
        if data[i] == '.':
            break
    value = float(data[:i+3])
    if len(data) == len(data[:i+3]):
        return value
    if data[i+3:] == sign['K_up']:
        return value
    elif data[i+3:] == sign['K_down']:
        return -value
def process_dMA(data):
    global sign
    if data[-2:] == sign['K_up']:
        value = float(data[:-2])
        return value
    elif data[-2:] == sign['K_down']:
        value = float(data[:-2])
        return -value
    else:
        return float(data)


sign = 0
def process(data, r, sign2):
    global sign
    sign = sign2
    o = data['Open'][r]
    h = data['High'][r]
    l = data['Low'][r]
    c = data['Close'][r]
    ud = process_ud(data['Up-Down'][r])
    v = data['Vol.'][r]
    m5 = float(data['MA5'][r])
    m10 = float(data['MA10'][r])
    k = process_KD(data['9-K'][r])
    d = process_KD(data['9-D'][r])
    r = process_KD(data['5-RSI'][r])
    return o, h, l, c, ud, v, m5, m10, k, d, r

