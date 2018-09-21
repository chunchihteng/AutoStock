import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.dates import DateFormatter, WeekdayLocator, \
    DayLocator, MONDAY, date2num, num2date
from mpl_finance import candlestick_ohlc



class SellSignal():
    def __init__(self, stop_profit_point, stop_loss_point, sell_func, bar_del):
        self.stop_profit_point = stop_profit_point
        self.stop_loss_point = stop_loss_point
        if sell_func == 'KD_DC': self.func = KD_DC()
        elif sell_func == 'KD_Dec': self.func = KD_Dec()
        elif sell_func == 'MA5_Dec': self.func = MA5_Dec()
        self.bar_del = bar_del

    def run_val(self, now_long_price, cur_price, data, idx):
    	if len(now_long_price) == 0:
    		return False
    	if idx == len(data.high)-1:
    		return True
    	#print "sell val", idx, cur_price - now_long_price, cur_price, now_long_price
    	# if data.MA20[idx-2] > data.MA20[idx-1]:
    	# 	return True
        s1 = self.stop_profit(now_long_price, cur_price)
        s2 = self.stop_loss(now_long_price, cur_price)
        s3 = self.func.thr(data, idx)
        s4 = self.pre_bar(data, idx)
        return s1 or s2 or s3 or s4

    def stop_profit(self, now_long_price, price):
        return np.sum(price - min(now_long_price) >= self.stop_profit_point) > 0

    def stop_loss(self, now_long_price, price):
        return np.sum(max(now_long_price) - price >= self.stop_loss_point) > 0

    def pre_bar(self, data, idx):
    	if data.close[idx-1] - data.open[idx-1] <= self.bar_del:
    		return True
    	else:
    		return False
class KD_DC():
    def thr(self, data, i):
        if i < 2: return False
        if abs(data.K[i-2]) > abs(data.D[i-2]) and abs(data.K[i-1]) < abs(data.D[i-1]): return True
        else: return False
class KD_Dec():
    def thr(self, data, i):
        if data.D[i-1] < 0: return True
        else: return False
class MA5_Dec():
    def thr(self, data, i):
        if abs(data.MA5[i-1]) < abs(data.MA5[i-2]): return True
        else: return False

class BuySignal():
    def __init__(self, updown_thr, buy_func, bar_del):
        if buy_func == 'KD_GC': self.func = KD_GC()
        self.updown_thr = updown_thr
        self.bar_del = bar_del

    def run_val(self, now_long_price, data, idx):
    	# if idx < 21:
    	# 	return False
    	s1 = now_long_price == [] or True
        s2 = self.func.thr(data, idx)
        s3 = count_max(data.updown, idx) >= self.updown_thr
        s4 = self.pre_bar(data, idx)
        # s4 = data.MA20[idx-2-19] < data.MA20[idx-1-19]
        return s1 and (s2 and s4) and s3#or s2 or s3
    def pre_bar(self, data, idx):
    	if data.close[idx-1] -data.open[idx-1] >= self.bar_del:
    		return True
    	else:
    		return False

def count_max(updown, idx, pass_n_days=10):
    updown = updown[max(0, idx-pass_n_days-1):idx-1]
    tmp = np.zeros((len(updown)))
    tmp[0] = updown[0]
    for i in range(1, len(updown)):
        tmp[i] = max(tmp[i-1]+updown[i], updown[i])
    return max(tmp)


class KD_GC():
	def thr(self, data, i):
		if i < 2:
			return False
		if abs(data.K[i-1]) > 50:
			return False
		if 3*abs(data.D[i-1]) - 2*abs(data.K[i-1]) > 50:
			return False

		if abs(data.MA5[i-1]) < abs(data.MA5[i-2]):
			return False
		if (abs(data.K[i-2]) < abs(data.D[i-2])) and (abs(data.K[i-1]) > abs(data.D[i-1])-0.2):
			# print i, data.K[i-2], data.K[i-1], data.D[i-2], data.D[i-1]
			return True
		else:
			return False
