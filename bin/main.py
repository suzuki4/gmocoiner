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
import random
import time

import os
#os.chdir("/Users/user/git/gmocoiner/bin")
import logging
import logging.config
logging.config.fileConfig("../conf/logging.ini")
logger = logging.getLogger(__name__)

#class parent: setLevel=print
#class tmp: info=print; debug=print; warning=print; parent=parent
#logger = tmp

from common import log_info, handle_error, notify_slack, slack_msg, slack_warning
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
    
    # 取引可能日かチェック
    unix_days = int(time.time() / 60 / 60 / 24)
    interval_trade_days = conf.getint(symbol, "interval_trade_days")
    if unix_days % interval_trade_days:
        # 割り切れなかったら
        return f"\n{symbol} is not in tradable date: {unix_days} / {interval_trade_days}"
    
    # DAI情報から上限価格を取得
    resp = gmo.ticker(symbol='DAI')
    ticker = resp.json()
    dai_price = float((float(ticker['data'][0]['bid']) + float(ticker['data'][0]['ask'])) / 2)
    no_order_dai_volume = conf.getfloat(symbol, "no_order_dai_volume")
    limit_price = no_order_dai_volume * dai_price
    
    # ティッカー情報を取得
    resp = gmo.ticker(symbol=symbol)
    ticker = resp.json()
    
    price = int((int(ticker['data'][0]['bid']) + int(ticker['data'][0]['ask'])) / 2)
    if price >= limit_price:
        return f"\n{symbol} is over limit price: {limit_price:,.0f}yen({no_order_dai_volume:,.0f}DAI)"
    unit = conf.getfloat(symbol, "unit")
    digit = len(str(unit)) - 2
    set_amount = conf.getfloat(symbol, "amount")
    minimum_volume = conf.getfloat(symbol, "minimum")
    volume = max(round(set_amount / price, digit), minimum_volume)
    
    # 確率で数量を調整する
    amount = price * volume
    if amount < set_amount:
        p = (set_amount - amount) / (price * unit) 
        if random.random() < p:
            volume += unit
            slack_warning(f"\n{symbol} volume added {unit}")
            #(p * (volume + unit) + (1-p) * volume) * price

    elif amount > set_amount:
        p = (amount - set_amount) / (price * unit) 
        if random.random() < p:
            volume -= unit
            slack_warning(f"\n{symbol} volume subtracted {unit}")
            #(p * (volume - unit) + (1-p) * volume) * price

    resp = gmo.order(symbol=symbol, side='BUY',
                     executionType='LIMIT', size=volume, price=price)
    return f"\n{symbol} price:{price} volume:{volume} amount:{amount} status:{resp}"


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
