#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author  : MG
@Time    : 2018/3/30 17:47
@File    : forecast.py
@contact : mmmaaaggg@163.com
@desc    : 
"""
from os import path
from prophet_app.forecast import forecast_blueprint
from flask import Blueprint, render_template
import logging

logger = logging.getLogger()
#  已经迁移大哦 __init__ 文件
# __name__.split('.')[-1] 相当于 forecast 文件名
# 目标文件默认使用 templates/forecast 下的文件
# file_name = __name__.split('.')[-1]
# forecast_blueprint = Blueprint(file_name, __name__, template_folder=path.join(path.pardir, 'templates', file_name))


@forecast_blueprint.route('/prophet')
def go_prophet():
    print('get request')
    return render_template('submit_prophet.html')