#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  6 16:04:17 2020

@author: user
"""

import sys
from slack_sdk import WebClient
import traceback

import logging
logger = logging.getLogger(__name__)

from parameter import Conf, Args
conf = Conf().conf
args = Args().args
slack_client = WebClient(conf.get("slack", "token"))


def notify_slack(start=True, channel=None):
    
    def _notify_slack(func):         
        def wrapper(*arg, **kwargs):
            if start:
                slack_msg(f'Start {args}.', channel=channel)
            ret = func(*arg, **kwargs)
            slack_msg(f'End {args}.', channel=channel)
            return ret
        return wrapper
    return _notify_slack
    

def slack_msg(msg, channel=None):
    
    if channel is None:
        channel = conf.get("slack", "channel")
        
    slack_client.chat_postMessage(channel=channel, text=msg)


def slack_error(msg, channel=None):
    
    msg = f"<!channel> ERROR: {msg}"
    slack_msg(msg, channel)


def slack_warning(msg, channel=None):
    
    msg = f"WARNING: {msg}"
    slack_msg(msg, channel)
    	

def log_info(func):    

    def wrapper(*args, **kwargs):
        logger.info(f"Start {func.__name__}.")
        ret = func(*args, **kwargs)
        logger.info(f"End {func.__name__}.")
        return ret

    return wrapper


def log_debug(func):    

    def wrapper(*args, **kwargs):
        logger.debug(f"Start {func.__name__}.")
        ret = func(*args, **kwargs)
        logger.debug(f"End {func.__name__}.")
        return ret

    return wrapper


def handle_error(_continue=True):    
    
    def _handle_error(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                #msg = f"{str(type(e))} {str(e)}"
                #logger.error(msg)
                logger.exception(e)
                #slack_error(msg)
                slack_error(traceback.format_exc())
                if _continue:
                    logger.info("Continue process.")
                else:
                    sys.exit(1)
        return wrapper
    return _handle_error
