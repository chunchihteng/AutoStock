import numpy as np

class SellSignal():
    def __init__(self, stop_profit_point, stop_loss_point, sell_func, bar_del):
        self.stop_profit_point = stop_profit_point
        self.stop_loss_point = stop_loss_point
        if sell_func == 'KD_DC': self.func = KD_DC()
        elif sell_func == 'KD_Dec': self.func = KD_Dec()
        elif sell_func == 'MA5_Dec': self.func = MA5_Dec()
        self.bar_del = bar_del

    def run_val(self, now_long_price, cur_price, data, idx, val_type=0):
    	if len(now_long_price) == 0:
    		return False
    	if idx == len(data.high)-1:
    		return True
    	#print "sell val", idx, cur_price - now_long_price, cur_price, now_long_price
        s1 = self.stop_profit(now_long_price, cur_price)
        s2 = self.stop_loss(now_long_price, cur_price)
        s3 = self.func.thr(data, idx)
        s4 = self.pre_bar(data, idx)
        if val_type == 0:
            return s1 or s2 or s3
        elif val_type == 1:
            return s1 or s2 or s3 or s4
        elif val_type == 2:
            return s1 or s2 or (s3 and s4)

    def stop_profit(self, now_long_price, price):
        return np.sum(price - min(now_long_price) >= self.stop_profit_point) > 0

    def stop_loss(self, now_long_price, price):
        return np.sum(max(now_long_price) - price >= self.stop_loss_point) > 0

    def pre_bar(self, data, idx):
    	return data.close[idx-1] - data.open[idx-1] <= self.bar_del
    


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

    def run_val(self, now_long_price, data, idx, val_type=0):
        s3 = count_max(data.updown, idx) >= self.updown_thr
        s1 = now_long_price == [] 
        s2 = self.func.thr(data, idx)	        
        s4 = self.pre_bar(data, idx)
        v1 = self.func_v1(data, idx)
        v2 = self.func_v2(data, idx)
        v3 = self.func_v3(data, idx)
        v4 = self.func_v4(data, idx)
        if val_type %4 == 0:   s = s3 and (s1 or val_type %8 >=4) and s2
        elif val_type %4 == 1: s = s3 and (s1 or val_type %8 >=4) and s2 and s4
        elif val_type %4 == 2: s = s3 and (s1 or val_type %8 >=4) and s4
        elif val_type %4 == 3: s = s3 and (s1 or val_type %8 >=4) and (s2 or s4)
        
        if s == True: return True

        if val_type < 8: v = True
        elif 8 <= val_type < 16: v = v1
        elif 16 <= val_type < 24: v = v2
        elif 24 <= val_type < 32: v = v3
        elif 32 <= val_type < 40: v = v4
        elif 40 <= val_type < 48: v = v3 or v1
        elif 48 <= val_type < 56: v = v3 and v1  
        elif 56 <= val_type < 64: v = v2 or v1
        elif 64 <= val_type < 72: v = v2 and v1      
        elif 72 <= val_type < 80: v = (v3 or v1) or v4
        elif 80 <= val_type < 88: v = (v3 or v1) and v4		
        elif 88 <= val_type < 96: v = (v3 and v1) or v4
        elif 96 <= val_type < 104: v = (v3 and v1) and v4
        elif 104 <= val_type < 112: v = (v2 or v1) or v4
        elif 112 <= val_type < 120: v = (v2 or v1) and v4
        elif 120 <= val_type < 128: v = (v2 and v1) or v4
        elif 128 <= val_type < 136: v = (v2 and v1) and v4

        return v

    def pre_bar(self, data, idx):
        return data.close[idx-1] -data.open[idx-1] >= self.bar_del
    	
    def func_v1(self, data, idx):
        return data.vol[idx-1] > data.vol[idx-2]*2
    def func_v2(self, data, idx):
    	return data.vol[idx-1] > 1000
    def func_v3(self, data, idx):
    	return data.vol[idx-1] > 1500
    def func_v4(self, data, idx):
    	if idx < 5:
    		return False
    	return data.vol[idx-1] > np.mean(data.vol[idx-1-4:idx-1])

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
