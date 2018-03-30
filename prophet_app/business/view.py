#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author  : MG
@Time    : 2018/3/30 13:43
@File    : view.py
@contact : mmmaaaggg@163.com
@desc    : 
"""
from flask import render_template, request, redirect, url_for
from flask.views import MethodView
from prophet_app.business import business
import logging
logger = logging.getLogger()


@business.route('/prophet')
def go_prophet():
    print('get request')
    return render_template('business/submit_prophet.html')

# class do_prophet(MethodView):
#     def get(self):
#         return render_template()