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
    date_from = db.Column(db.Date)
    date_to = db.Column(db.Date)
    create_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    create_dt = db.Column(db.DateTime, default=datetime.now())
    access_type = db.Column(db.String(20), server_default="private", default='private')

    def __init__(self, pl_id=None, name=None, date_from=None, date_to=None, create_user_id=None, access_type='private'):
        self.pl_id = pl_id
        self.name = name
        self.date_from = date_from
        self.date_to = date_to
        self.create_user_id = create_user_id
        self.access_type = access_type
        # self.create_dt = create_dt if create_dt else datetime.now()


class PortfolioData(db.Model):
    """
    每日的投资组合变化信息
    """
    __tablename__ = 'pl_data'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pl_id = db.Column(db.Integer, db.ForeignKey("pl_info.pl_id"))
    wind_code = db.Column(db.String(20))
    asset_type = db.Column(db.String(20))
    trade_date = db.Column(db.Date)
    weight = db.Column(db.Float)

    __table_args__ = (
        db.UniqueConstraint('pl_id', 'wind_code', 'trade_date', name='uix_pl_data_pl_id_wind_code_trade_date'),
    )

    def __init__(self, pl_id=None, wind_code=None, asset_type=None, trade_date=None, weight=None):
        self.pl_id = pl_id
        self.wind_code = wind_code
        self.asset_type = asset_type
        self.trade_date = trade_date
        self.weight = weight


class PortfolioValueDaily(db.Model):
    """
    每日的投资组合变化信息
    """
    __tablename__ = 'pl_value_daily'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pl_id = db.Column(db.Integer, db.ForeignKey("pl_info.pl_id"))
    trade_date = db.Column(db.Date)
    rr = db.Column(db.Float)

    __table_args__ = (
        db.UniqueConstraint('pl_id', 'trade_date', name='uix_pl_value_daily_pl_id_trade_date'),
    )


class PortfolioCompareInfo(db.Model):
    """
    投资组合比较
    """
    __tablename__ = 'pl_compare_info'
    comp_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    date_from = db.Column(db.Date)
    date_to = db.Column(db.Date)
    status = db.Column(db.String(20))
    # params
    # compare_type :
    #   'abs.fix_point', 'abs.rr', 'rel.fix_point', 'rel.rr' 绝对比较（固定点位，绝对收益率）、相对比较（固定点位，绝对收益率）
    # compare_method: '>', '<', 'between'  'between' 的情况下需要存在 value1 value2
    # asset_type_1, asset_type_2:
    #   'index', 'stock', 'future', 'portfolio'
    params = db.Column(db.String(1000))
    create_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    create_dt = db.Column(db.DateTime, default=datetime.now())
    desc = db.Column(db.Text)

    def __init__(self, comp_id=None, name=None, date_from=None, date_to=None, status=None, params=None, create_user_id=None):
        self.comp_id = comp_id
        self.name = name
        self.date_from = date_from
        self.date_to = date_to
        self.status = status
        self.params = params
        self.create_user_id = create_user_id


class PortfolioCompareResult(db.Model):
    """
    每日组合预期与实际比较结果
    """
    __tablename__ = 'pl_compare_result'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comp_id = db.Column(db.Integer, db.ForeignKey('pl_compare_info.comp_id'))
    trade_date = db.Column(db.Date)
    asset_1 = db.Column(db.Float)
    asset_2 = db.Column(db.Float)
    asset_3 = db.Column(db.Float)
    result = db.Column(db.SmallInteger)
    shift_value = db.Column(db.Float)
    shift_rate = db.Column(db.Float)

    __table_args__ = (
        db.UniqueConstraint('comp_id', 'trade_date', name='uix_pl_compare_result'),
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

