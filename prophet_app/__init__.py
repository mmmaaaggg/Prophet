#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author  : MG
@Time    : 2018/3/27 10:42
@File    : __init__.py.py
@contact : mmmaaaggg@163.com
@desc    : 
"""
from flask_user import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Define the User data model. Make sure to add flask_user UserMixin !!!
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    # User authentication information
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')

    # User email information
    email = db.Column(db.String(255), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime())

    # User information
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    first_name = db.Column(db.String(100), nullable=False, server_default='')
    last_name = db.Column(db.String(100), nullable=False, server_default='')


class MDStockDaily(db.Model):

    __tablename__ = "wind_stock_daily"
    __bind_key__ = 'db_md'
    trade_date = db.Column(db.Date, primary_key=True)
    wind_code = db.Column(db.String(20), primary_key=True)
    close = db.Column(db.Float)