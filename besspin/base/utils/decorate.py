#! /usr/bin/env python3

import logging, time, sys
from functools import wraps

def getTargetInfo (*args, targetId=None, **kwargs):
    if (targetId is not None):
        return f"<target{targetId}>: "
    elif ((len(args)>0) and hasattr(args[0],'targetId')): #for methods in commonTarget
        return f"<target{getattr(args[0],'targetId')}>: "
    else:
        return ''

def debugWrap (func):
    @wraps(func)
    def wrappedFn(*args, **kwargs):
        try:
            caller = sys._getframe(1).f_code.co_name
        except:
            caller = 'unknown-caller'
        logging.debug(f"{getTargetInfo(*args, **kwargs)}Entering <{func.__name__}>. [called from <{caller}>]")
        #logging.debug(f"{getTargetInfo(*args, **kwargs)}>>>> args={args}, kwargs={kwargs}") #super-duper debug
        ret = func(*args, **kwargs)
        logging.debug(f"{getTargetInfo(*args, **kwargs)}Exitting <{func.__name__}>.")
        return ret
    return wrappedFn

def timeWrap(func):
    @wraps(func)
    def wrappedFn(*args, **kwargs):
        startTime = time.time()
        ret = func(*args, **kwargs)
        minutes, seconds = divmod(time.time() - startTime, 60)
        logging.debug("{}[Time Elapsed in <{}>]={:0>2}:{:0>2}".format(getTargetInfo(*args, **kwargs),func.__name__,
                                                                    int(minutes),int(seconds)))
        return ret
    return wrappedFn
