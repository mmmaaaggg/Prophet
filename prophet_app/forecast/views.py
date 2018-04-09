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
from prophet_app import db
from flask import Blueprint, render_template, request, session, url_for, redirect
import logging
from prophet_app.forecast.models import PortfolioInfo, PortfolioData, PortfolioCompareResult
from prophet_app.forecast.forms import PortfolioInfoForm
from flask.views import MethodView

logger = logging.getLogger()
#  已经迁移大哦 __init__ 文件
# __name__.split('.')[-1] 相当于 forecast 文件名
# 目标文件默认使用 templates/forecast 下的文件
# file_name = __name__.split('.')[-1]
# forecast_blueprint = Blueprint(file_name, __name__, template_folder=path.join(path.pardir, 'templates', file_name))


@forecast_blueprint.route('/list')
def go_prophet():
    print('get request')
    # form = CompInfoForm()
    # form.calc_method.choices = [('mean_rr', '收益率均值'), ('ma20', 'MA20')]
    data = PortfolioInfo.query.all()
    # print(form.name)
    return render_template('list.html', data=data)


class ProphetCreateOrEdit(MethodView):

    def get(self, id_=None):
        if id_:
            pl_info = db.session.query(PortfolioInfo).get(id_)
            form = PortfolioInfoForm(request.form, obj=pl_info)
        else:
            print('get request ProphetCreateOrEdit')
            pl_info = PortfolioInfo()
            form = PortfolioInfoForm()

        form.calc_method.choices = [('mean_rr', '收益率均值'), ('ma20', 'MA20')]
        return render_template('submit_prophet.html', form=form)

    def post(self, id_=None):

        if id_:
            comp_info = db.session.query(PortfolioInfo).get(id_)
        else:
            comp_info = PortfolioInfo()
            user_id = session.get('user_id')
            form = PortfolioInfoForm(request.form)
            form.populate_obj(comp_info)
            comp_info.create_user_id=user_id

        db.session.add(comp_info)
        db.session.commit()
        # return render_template('submit_prophet.html', form=form)
        return redirect(url_for('.go_prophet'))
