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
from flask import Blueprint, render_template
import logging

logger = logging.getLogger()
forecast_blueprint = Blueprint('auth', __name__, template_folder=path.join(path.pardir, 'templates', 'forecaset'))


@forecast_blueprint.route('/prophet')
def go_prophet():
    print('get request')
    return render_template('submit_prophet.html')