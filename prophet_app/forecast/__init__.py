#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author  : MG
@Time    : 2018/3/30 17:43
@File    : __init__.py.py
@contact : mmmaaaggg@163.com
@desc    : 
"""

from os import path
from flask import Blueprint, render_template
import logging

logger = logging.getLogger()
# __name__.split('.')[-1] 相当于 forecast 文件名
# 目标文件默认使用 templates/forecast 下的文件
file_name = __name__.split('.')[-1]
print('file_name:', __name__)
forecast_blueprint = Blueprint(file_name, __name__, template_folder=path.join(path.pardir, 'templates', file_name))

from prophet_app.forecast.views import *