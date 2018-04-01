#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author  : MG
@Time    : 2018/3/30 22:25
@File    : forms.py
@contact : mmmaaaggg@163.com
@desc    : 
"""

from flask_wtf import FlaskForm
import wtforms


class CompInfoForm(FlaskForm):
    name = wtforms.StringField('组合名称')
    calc_method = wtforms.SelectField('计算方法')
    create_user_id = wtforms.StringField('创建用户')

