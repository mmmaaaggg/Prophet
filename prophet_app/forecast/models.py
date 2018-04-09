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


class PortfolioInfo(db.Model):
    """
    组合信息
    """
    __tablename__ = 'pl_info'
    pl_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True)
    create_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    create_dt = db.Column(db.DateTime, default=datetime.now())
    calc_method = db.Column(db.String(20))

    def __init__(self, name=None, calc_method=None, create_user_id=None):
        self.name = name
        self.create_user_id = create_user_id
        self.calc_method = calc_method
        # self.create_dt = create_dt if create_dt else datetime.now()


class PortfolioData(db.Model):
    """
    每日的投资组合变化信息
    """
    __tablename__ = 'pl_data'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pl_id = db.Column(db.Integer, db.ForeignKey("pl_info.pl_id"))
    wind_code = db.Column(db.String(20))
    trade_date = db.Column(db.Date)
    weight = db.Column(db.Float)

    __table_args__ = (
        db.UniqueConstraint('pl_id', 'wind_code', 'trade_date', name='uix_pl_data_pl_id_wind_code_trade_date'),
    )


class PortfolioReturnRate(db.Model):
    """
    每日的投资组合变化信息
    """
    __tablename__ = 'pl_rr'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pl_id = db.Column(db.Integer, db.ForeignKey("pl_info.pl_id"))
    trade_date = db.Column(db.Date)
    rr = db.Column(db.Float)

    __table_args__ = (
        db.UniqueConstraint('pl_id', 'trade_date', name='uix_pl_rr_pl_id_trade_date'),
    )


class PortfolioCompareResult(db.Model):
    """
    每日组合预期与实际比较结果
    """
    __tablename__ = 'pl_compare_result'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    exp_pl_id = db.Column(db.Integer, db.ForeignKey('pl_info.pl_id'))
    real_pl_id = db.Column(db.Integer, db.ForeignKey('pl_info.pl_id'))
    trade_date = db.Column(db.Date)
    compare_method = db.Column(db.String(20))
    exp_value = db.Column(db.Float)
    real_value = db.Column(db.Float)
    result = db.Column(db.SmallInteger)
    shift_value = db.Column(db.Float)
    shift_rate = db.Column(db.Float)

    __table_args__ = (
        db.UniqueConstraint('exp_pl_id', 'real_pl_id', 'trade_date', name='uix_pl_compare_result'),
    )


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
