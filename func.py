import numpy as np
color = ['green', 'brown', 'purple', 'blue']
def MA(close, period, duration):
	ma = []
	for i in range(duration-1,-1,-1):
		ma += [round(np.mean([float(d) for d in close[len(close)-i-period:len(close)-i]]),2)]
	return ma

def EMA(close, period, duration):
	ema23 = np.zeros((len(close))) 
	for i in range(1, len(close)):
		ema23[i] = close[i]*(2./23.) + ema23[i-1]*(21./23.) 
	return ema23[-duration:]

def indicator_line(price, indicator, duration):
	line = []
	for e, idx in enumerate(indicator):
		if idx[0] == 'MA':
			line += [[MA(price, idx[1], duration), color[e]]]
		elif idx[0] == 'EMA':
			line += [[EMA(price, idx[1], duration), color[e]]]
	return line
