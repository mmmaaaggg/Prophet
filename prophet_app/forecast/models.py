#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author  : MG
@Time    : 2018/3/30 22:25
@File    : models.py
@contact : mmmaaaggg@163.com
@desc    : 
"""
from datetime import datetime
from prophet_app import db, User


class CompInfo(db.Model):
    """
    组合信息
    """
    __tablename__ = 'comp_info'
    comp_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    create_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    create_dt = db.Column(db.DateTime, default=datetime.now())
    calc_method = db.Column(db.String(20))

    def __init__(self, name=None, calc_method=None, create_user_id=None):
        self.name = name
        self.create_user_id = create_user_id
        self.calc_method = calc_method
        # self.create_dt = create_dt if create_dt else datetime.now()


class CompData(db.Model):
    """
    每日的投资组合变化信息
    """
    __tablename__ = 'comp_data'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comp_id = db.Column(db.Integer, db.ForeignKey("CompInfo.comp_id"))
    wind_code = db.Column(db.String(20))
    trade_date = db.Column(db.Date)
    weight = db.Column(db.Float)


class DailyCompareResult(db.Model):
    """
    每日组合预期与实际比较结果
    """
    __tablename__ = 'daily_compare_result'
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


class WindStockInfo(db.Model):
    """
    股票基本信息
    """
    __tablename__ = 'wind_stock_info'
    wind_code = db.Column(db.String(20), primary_key=True)
    trade_code = db.Column(db.String(20))
    sec_name = db.Column(db.String(20))
    ipo_date = db.Column(db.Date)
    delist_date = db.Column(db.Date)
    exch_city = db.Column(db.String(20))
    exch_eng = db.Column(db.String(20))
    mkt = db.Column(db.String(20))
    prename = db.Column(db.String(2000))
