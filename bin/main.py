#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  6 16:04:17 2020

@author: user
"""

import sys
sys.path.append("..")
from gmocoiner import GMOCoin
import json

import os
#os.chdir("/Users/user/git/huia/bin")
import logging
import logging.config
logging.config.fileConfig("../conf/logging.ini")
logger = logging.getLogger(__name__)

#class parent: setLevel=print
#class tmp: info=print; debug=print; warning=print; parent=parent
#logger = tmp

from common import log_info, handle_error, notify_slack, slack_msg
from parameter import Conf, Args
conf = Conf().conf
args = Args().args
    
TARGETS = ["BTC", "ETH"]

@handle_error(False)
@notify_slack()
@log_info
def tsumitate():
    
    apikey = conf["gmo"]["apikey"]
    secret = conf["gmo"]["secret"]
    
    gmo = GMOCoin(apikey, secret, late_limit=True, logger=None)
    
    msg = "-- order --"
    for symbol in TARGETS:
        msg += order(gmo, symbol)
    slack_msg(msg)
        
    show_status(gmo)
    

def order(gmo, symbol):
    # ティッカー情報を表示
    resp = gmo.ticker(symbol=symbol)
    ticker = resp.json()
    
    price = int((int(ticker['data'][0]['bid']) + int(ticker['data'][0]['ask'])) / 2)
    unit = conf.getfloat(symbol, "unit")
    digit = len(str(unit)) - 2
    amount = conf.getfloat(symbol, "amount")
    volume = round(amount / price, digit)

    resp = gmo.order(symbol=symbol, side='BUY',
                     executionType='LIMIT', size=volume, price=price)
    msg = f"\n{symbol} price:{price} volume:{volume} amount:{price*volume} status:{resp}"
    
    return msg


def show_status(gmo):
    
    msg = "-- active_orders --"
    for symbol in TARGETS:
        resp = gmo.activeorders(symbol)
        msg += f"\n{symbol} "
        msg += json.dumps(resp.json()['data'])
    
    msg += "\n\n-- latest_executions --"
    for symbol in TARGETS:
        resp = gmo.latestexecutions(symbol)
        msg += f"\n{symbol} "
        msg += json.dumps(resp.json()['data'])
    slack_msg(msg)


if __name__ == '__main__':

    logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("chardet.charsetprober").setLevel(logging.WARNING)
    
    logger.info(f"conf: [setting]: {dict(conf.items('setting'))}")
    logger.info(f"args: {args}")
    if args["log_debug"] or conf.getboolean("setting", "log_debug"):
        logger.parent.setLevel(logging.DEBUG)
     
    if len(args["func_args"]) == 1:
        eval(args["func_args"][0])()
    else:
        eval(args["func_args"][0])(*args["func_args"][1:])
