#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  6 16:04:17 2020

@author: user
"""

import os
import datetime
import pandas as pd
import argparse
import configparser

class Singleton:

    def __new__(cls, *args, **kargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(Singleton, cls).__new__(cls)

        return cls._instance


class Conf(Singleton):
    
    def __init__(self, path="../conf/config.ini"):
        self.conf = configparser.ConfigParser()
        self.conf.optionxform = str
        self.conf.read(path)


class Args(Singleton):
    
    def __init__(self):        
        parser = argparse.ArgumentParser()
        parser.add_argument("func_args", nargs="+", action="store", type=str, help="func and args")
        parser.add_argument("--log_debug", action="store_true")        
        self.args = vars(parser.parse_args())

