#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author  : MG
@Time    : 2018/4/2 9:56
@File    : data_analysis.py
@contact : mmmaaaggg@163.com
@desc    : 通过后台现场对数据进行定期分析
"""
from collections import OrderedDict
from datetime import date, timedelta
from prophet_app import db
from prophet_app.forecast.models import PortfolioInfo, PortfolioData, PortfolioReturnRate
import pandas as pd
from prophet_app.utils.fh_utils import str_2_date, date_2_str
from prophet_app.utils.db_utils import with_db_session
from prophet_app.config import config
import logging

logger = logging.getLogger()


def update_pl_rr(pl_id, trade_date_from, trade_date_to):
    """
    更新指定日期范围内组合每日收益率
    :param pl_id:
    :param trade_date_from:
    :param trade_date_to:
    :return:
    """
    trade_date_from = str_2_date(trade_date_from)
    trade_date_to = str_2_date(trade_date_to)
    # pl_info = db.session.query(PortfolioInfo).get(pl_id)
    # 获取日期段数据
    sql_str = """select dt_to.pl_id, ifnull( dt_frm.date_frm, date(%s)) date_from, dt_to.date_to
from
(
    SELECT pl_id, max(trade_date) date_to
    FROM pl_data
    WHERE pl_id = %s AND trade_date <= %s
) dt_to
left JOIN
(
    select pl_id,max(trade_date) date_frm
    FROM pl_data
    WHERE pl_id = %s AND trade_date <= %s
) dt_frm
on dt_frm.pl_id = dt_to.pl_id"""
    trade_date_range_df = pd.read_sql(sql_str, db.engine,
                                      params=[trade_date_from, pl_id, trade_date_to, pl_id, trade_date_from])
    if trade_date_range_df.shape[0] == 0:
        logger.debug('pl_id: %d[%s-%s] 没有数据',
                     pl_id, trade_date_from, trade_date_to)
        return
    elif trade_date_range_df.shape[0] > 1:
        logger.warning('pl_id: %d[%s-%s] 存在 %d 条记录',
                       pl_id, trade_date_from, trade_date_to, trade_date_range_df.shape[0])
        return

    # 获取日期段内的全部组合
    date_to = trade_date_range_df['date_to'][0]
    date_frm = trade_date_range_df['date_from'][0]
    sql_str = """select id, pl_id, wind_code, trade_date, weight from pl_data
where pl_id = %s and trade_date between %s and %s"""
    pl_data_df_all = pd.read_sql(sql_str, db.engine, params=[pl_id, date_frm, date_to])
    if pl_data_df_all.shape[0] == 0:
        logger.warning('pl_id: %d[%s-%s] 没有有效的数据[%s - %s]',
                       pl_id, trade_date_from, trade_date_to, date_to, date_frm)
        return
    dfg = pl_data_df_all.groupby('trade_date')
    trade_date_sorted_dic = OrderedDict()
    trade_date_sorted_list = []
    for trade_date_g, pl_data_df in dfg:
        trade_date_sorted_list.append(trade_date_g)
        trade_date_sorted_dic[trade_date_g] = {'pl_df': pl_data_df[["wind_code", "weight"]].set_index('wind_code')}

    # 计算各个时间点的组合对应的日期范围
    if len(trade_date_sorted_list) == 1:
        trade_date_g = trade_date_sorted_list[0]
        trade_date_range_frm = trade_date_from if trade_date_g < trade_date_from else trade_date_g
        if trade_date_range_frm > trade_date_to:
            logger.warning('pl_id: %d[%s-%s] 日期范围 [%s - %s] 无效',
                           pl_id, trade_date_from, trade_date_to, trade_date_range_frm, trade_date_to)
            return
        trade_date_sorted_dic[trade_date_g]['date_from'] = trade_date_range_frm
        trade_date_sorted_dic[trade_date_g]['date_to'] = trade_date_to
    else:
        # 按日期从小到大排序
        trade_date_sorted_list.sort()
        for idx in range(1, len(trade_date_sorted_list)):
            trade_date_last = trade_date_sorted_list[idx - 1]
            trade_date_cur = trade_date_sorted_list[idx]
            trade_date_cur_1 = trade_date_cur - timedelta(days=1)
            trade_date_range_frm = trade_date_from if trade_date_from > trade_date_last else trade_date_last
            trade_date_range_to = trade_date_cur_1 if trade_date_cur_1 < trade_date_to else trade_date_to
            if trade_date_range_frm > trade_date_range_to:
                logger.debug('pl_id: %d[%s-%s] %d 日期范围 [%s - %s] 无效',
                             pl_id, trade_date_from, trade_date_to, idx, trade_date_range_frm, trade_date_range_to)
                continue
            trade_date_sorted_dic[trade_date_g]['date_from'] = trade_date_range_frm
            trade_date_sorted_dic[trade_date_g]['date_to'] = trade_date_range_to

    # 分阶段计算收益率
    rr_s_list = []
    for num, (trade_date_g, data_dic) in enumerate(trade_date_sorted_dic.items()):
        if 'date_from' in data_dic:
            rr_s = calc_protfolio_rr(**data_dic)
            rr_s_list.append(rr_s)
    # 合并计算结果
    rr_tot_s = pd.concat(rr_s_list).rename('rr')
    rr_tot_df = pd.DataFrame(rr_tot_s)
    rr_tot_df['pl_id'] = pl_id
    # TODO: 更新数据库
    with with_db_session(db.engine) as session:
        session.execute(
            'delete from pl_rr where trade_date between :trade_date_from and :trade_date_to and pl_id = :pl_id',
            params={"trade_date_from": date_2_str(rr_tot_s.index.min()),
                    "trade_date_to": date_2_str(rr_tot_s.index.max()),
                    'pl_id': pl_id}
        )
        session.commit()
    rr_tot_df.to_sql("pl_rr", db.engine, if_exists='append')
    return rr_tot_s


def calc_protfolio_rr(date_from, date_to, pl_df):
    """
    计算日期区间投资组合收益率
    :param date_from:
    :param date_to:
    :param pl_df: wind_code 为index, weight 列为权重
    :return:
    """
    if pl_df is None or pl_df.shape[0] == 0:
        logger.warning('pl_df [%s - %s]: 没有数据', date_from, date_to)
        return
    # 对 weight 进行 normalize
    pl_df['weight'] = pl_df['weight'] / pl_df['weight'].sum()
    # 构建 in 子句中的字符串，将 wind_code 连接起来
    in_list_str = "'" + "','".join(pl_df.index) + "'"

    # 构筑sql 获取每只股票日期段前一个交易日(date_from - 1)，到最后一个交易日(date_to)
    # select dt_to.wind_code, ifnull( dt_frm.date_frm, date('2018-01-01')) date_frm, dt_to.date_to
    # from
    # (
    #     SELECT wind_code, max(trade_date) date_to
    #     FROM wind_stock_daily
    #     WHERE trade_date <= '2018-05-01'
    #     and wind_code in ('000001.SZ', '000002.SZ')
    #     group by wind_code
    # ) dt_to
    # left JOIN
    # (
    #     select wind_code,max(trade_date) date_frm
    #     FROM wind_stock_daily
    #     WHERE trade_date < '2018-01-01'
    #     and wind_code in ('000001.SZ', '000002.SZ')
    #     group by wind_code
    # ) dt_frm
    # on dt_frm.wind_code = dt_to.wind_code
    sql_str = """select dt_to.wind_code, ifnull( dt_frm.date_frm, date(%s)) date_from, dt_to.date_to
from
(
    SELECT wind_code, max(trade_date) date_to
    FROM wind_stock_daily
    WHERE trade_date <= %s
    and wind_code in ({0})
    group by wind_code
) dt_to
left JOIN
(
    select wind_code,max(trade_date) date_frm
    FROM wind_stock_daily
    WHERE trade_date < %s  -- 需要找到前一个交易日的日期，因此是 小于号
    and wind_code in ({0})
    group by wind_code
) dt_frm
on dt_frm.wind_code = dt_to.wind_code""".format(in_list_str)
    # 获取日期区间
    # TODO: db.engine 提出按为股票行情数据对应的engine
    trade_date_range_df = pd.read_sql(sql_str, db.get_engine(bind=config.BIND_DB_NAME_MD), params=[date_from, date_to, date_from])
    if trade_date_range_df.shape[0] == 0:
        logger.debug('%d[%s-%s] 没有数据', date_from, date_to)
        return
    # 分别计算每日收益率
    rr_list = []
    for idx, trade_date_range_dic in trade_date_range_df.to_dict('index').items():
        wind_code = trade_date_range_dic["wind_code"]
        rr_s = calc_asset_rr(**trade_date_range_dic) * pl_df.loc[wind_code, 'weight']
        rr_list.append(rr_s)
    # 整理成df index为日期 column 为股票代码
    rr_df = pd.DataFrame(rr_list).T
    rr_s = rr_df.mean(axis=1)
    # 对日期字段进行过滤
    is_fit = (rr_s.index >= date_from) & (rr_s.index <= date_to)
    ret_s = rr_s[is_fit]
    return ret_s


def calc_asset_rr(wind_code, date_from, date_to) -> pd.Series:
    """
    计算资产日期区间的收益率
    :param wind_code:
    :param date_from:
    :param date_to:
    :return:
    """
    sql_str = """select trade_date, close from wind_stock_daily where wind_code=%s and trade_date between %s and %s order by trade_date"""
    md_df = pd.read_sql(sql_str, db.get_engine(bind=config.BIND_DB_NAME_MD), params=[wind_code, date_from, date_to],
                        index_col='trade_date')
    rr_s = md_df["close"].pct_change().fillna(0).rename(wind_code)
    return rr_s


if __name__ == "__main__":
    from prophet_app.prophet import create_init

    app = create_init()
    # 测试 update_pl_rr(pl_id, trade_date_from, trade_date_to)
    pl_id, trade_date_from, trade_date_to = 1, '2018-01-01', '2018-5-1'
    update_pl_rr(pl_id, trade_date_from, trade_date_to)
