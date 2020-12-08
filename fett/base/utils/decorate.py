#! /usr/bin/env python3

import logging, time, sys
from functools import wraps

def debugWrap (func):
    @wraps(func)
    def wrappedFn(*args, **kwargs):
        try:
            caller = sys._getframe(1).f_code.co_name
        except:
            caller = 'unknown-caller'
        if (('targetId' in kwargs) and (kwargs['targetId'] is not None)):
            targetInfo = f"<target{kwargs['targetId']}>: "
        else:
            targetInfo = ''
        logging.debug(f"{targetInfo}Entering <{func.__name__}>. [called from <{caller}>]") 
        #logging.debug(f">>>> args={args}, kwargs={kwargs}") #super-duper debug
        ret = func(*args, **kwargs)
        logging.debug(f"Exitting <{func.__name__}>.")
        return ret
    return wrappedFn

def timeWrap(func):
    @wraps(func)
    def wrappedFn(*args, **kwargs):
        startTime = time.time()
        ret = func(*args, **kwargs)
        minutes, seconds = divmod(time.time() - startTime, 60)
        logging.debug("[Time Elapsed in <{}>]={:0>2}:{:0>2}".format(func.__name__,int(minutes),int(seconds)))
        return ret
    return wrappedFn
