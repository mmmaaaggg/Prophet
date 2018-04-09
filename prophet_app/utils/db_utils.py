#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author  : MG
@Time    : 2018/4/8 21:11
@File    : db_utils.py
@contact : mmmaaaggg@163.com
@desc    : 数据库相关工具
"""
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import sessionmaker


class SessionWrapper:
    """用于对session对象进行封装，方便使用with语句进行close控制"""

    def __init__(self, session):
        self.session = session

    def __enter__(self) -> Session:
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
        # logger.debug('db session closed')


def with_db_session(engine, expire_on_commit=True):
    """创建session对象，返回 session_wrapper 可以使用with语句进行调用"""
    db_session = sessionmaker(bind=engine, expire_on_commit=expire_on_commit)
    session = db_session()
    return SessionWrapper(session)
