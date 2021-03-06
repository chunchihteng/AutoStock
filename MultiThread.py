# -- coding: UTF-8 --
import numpy as np
from numpy import genfromtxt
import pandas as pd
import time
from utils import *
import traceback
import threading
import Queue
import sys
class WorkerThread(threading.Thread):
    def __init__(self, task_queue):
        threading.Thread.__init__(self)
        self.task_queue = task_queue

    def run(self):
        while True:
            func, args, result_queue = self.task_queue.get()
            if func is None:
                break
            try:
                result = func(*args)
            except:
                result = ExceptionInfo()
            result_queue.put((result, args))

#----------------------------------------------------------------------------

class ThreadPool(object):
    def __init__(self, num_threads):
        assert num_threads >= 1
        self.task_queue = Queue.Queue()
        self.result_queues = dict()
        self.num_threads = num_threads
        for idx in xrange(self.num_threads):
            thread = WorkerThread(self.task_queue)
            thread.daemon = True
            thread.start()

    def add_task(self, func, args=()):
        assert hasattr(func, '__call__') # must be a function
        if func not in self.result_queues:
            self.result_queues[func] = Queue.Queue()
        self.task_queue.put((func, args, self.result_queues[func]))

    def get_result(self, func, verbose_exceptions=True): # returns (result, args)
        result, args = self.result_queues[func].get()
        if isinstance(result, ExceptionInfo):
            if verbose_exceptions:
                print '\n\nWorker thread caught an exception:\n' + result.traceback + '\n',
            raise result.type, result.value
        return result, args

    def finish(self):
        for idx in xrange(self.num_threads):
            self.task_queue.put((None, (), None))

    def __enter__(self): # for 'with' statement
        return self

    def __exit__(self, *excinfo):
        self.finish()

    def process_items_concurrently(self, info, process_func=lambda x: x, pre_func=lambda x: x, post_func=lambda x: x, max_items_in_flight=None):
        if max_items_in_flight is None: max_items_in_flight = self.num_threads * 4
        assert max_items_in_flight >= 1
        results = []
        retire_idx = [0]

        def task_func(c, e_list, info):
            return process_func(c, e_list, info)
           
        def retire_result():
            out, out2 = self.get_result(task_func)
            results[out2[0]] = out #processed
            while retire_idx[0] < len(results) and results[retire_idx[0]] is not None:
                yield post_func(results[retire_idx[0]])
                results[retire_idx[0]] = None
                retire_idx[0] += 1

        c = 0
        for e1, sp in enumerate(info['sps']):
            for e2, sl in enumerate(info['sls']):           
                for e3, buy_d in enumerate(info['buy_ds']): 
                    for e4, sell_d in enumerate(info['sell_ds']):
                        for e5, buy_v in enumerate(info['buy_val']):
                            for e6, sell_v in enumerate(info['sell_val']):
                                results.append(None)
                                e_list = [e1, e2, e3, e4, e5, e6]
                                infos = dict()
                                infos['sp'], infos['sl'] = sp, sl
                                infos['buy_d'], infos['sell_d'], infos['buy_v'], infos['sell_v'] = buy_d, sell_d, buy_v, sell_v
                                infos['days'] = info['days']
                                infos['buy_func'], infos['sell_func'] = info['buy_func'], info['sell_func']
                                self.add_task(func=task_func, args=(c, e_list, infos))
                                while retire_idx[0] < c - max_items_in_flight + 2:
                                    for res in retire_result(): yield res
                                c += 1
        while retire_idx[0] < len(results):
            for res in retire_result(): yield res

class ExceptionInfo(object):
    def __init__(self):
        self.type, self.value = sys.exc_info()[:2]
        self.traceback = traceback.format_exc()