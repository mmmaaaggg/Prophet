#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author  : MG
@Time    : 2018/3/30 22:25
@File    : models.py
@contact : mmmaaaggg@163.com
@desc    : 
"""

from prophet_app import db, User


class CompInfo(db.Model):
    """
    组合信息
    """
    __tablename__ = 'CompInfo'
    comp_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    create_user_id = db.Column(db.Integer, db.ForeignKey())
    create_dt = db.Column(db.DateTime, server_default)
    calc_method = db.Column(db.String(20))


class CompData(db.Model):
    """
    每日的投资组合变化信息
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comp_id = db.Column(db.Integer, db.ForeignKey("CompInfo.comp_id"))
    wind_code = db.Column(db.String(20))
    trade_date = db.Column(db.Date)
    weight = db.Column(db.Float)


class DailyCompareResult(db.Model):
    """
    每日组合预期与实际比较结果
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    exp_comp_id = db.Column(db.Integer, db.ForeignKey('CompInfo.comp_id'))
    real_comp_id = db.Column(db.Integer, db.ForeignKey('CompInfo.comp_id'))
    trade_date = db.Column(db.Date)
    compare_method = db.Column(db.String(20))
    exp_value = db.Column(db.Float)
    real_value = db.Column(db.Float)
    result = db.Column(db.SmallInteger)
    shift_value = db.Column(db.Float)
    shift_rate = db.Column(db.Float)

