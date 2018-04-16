from flask import Flask, render_template, render_template_string
from flask_login import LoginManager
from flask_mail import Mail
from flask_user.forms import LoginForm
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter
from prophet_app.forecast import forecast_blueprint
from prophet_app import db, User
import logging

logger = logging.getLogger()


def create_app(config_path, db):
    app = Flask(__name__, static_url_path='')
    app.debug = True
    # app.secret_key = 'M!@#$@#$%#$%alksdjf;lkj'

    # 添加 BluePrint
    app.register_blueprint(forecast_blueprint, url_prefix='/forecast')

    # app.config.from_object(__name__+'.ConfigClass')
    app.config.from_object(config_path)

    # Initialize Flask extensions
    # db = SQLAlchemy(app)                            # Initialize Flask-SQLAlchemy
    # reference : http://flask-sqlalchemy.pocoo.org/2.3/contexts/
    app.app_context().push()
    db.init_app(app)

    # Create all database tables
    db.create_all()

    mail = Mail(app)  # Initialize Flask-Mail
    return app


def route(app, db):
    # Setup Flask-User
    db_adapter = SQLAlchemyAdapter(db, User)  # Register the User model
    user_manager = UserManager(db_adapter, app)  # Initialize Flask-User

    @app.route('/')
    def hello_world():
        return render_template('top.html')

    @app.route('/index')
    def index():
        return render_template('index.html')

    @app.route('/base')
    def home_page():
        # return render_template_string("""
        #     {% extends "base.html" %}
        #     {% block content %}
        #         <h2>Basic Home page</h2>
        #         <p>This page can be accessed by anyone.</p><br/>
        #         <p><a href={{ url_for('home_page') }}>Home page</a> (anyone)</p>
        #         <p><a href={{ url_for('members_page') }}>Members page</a> (login required)</p>
        #     {% endblock %}
        #     """)
        return render_template('base.html')

    # The Members page is only accessible to authenticated users
    @app.route('/members')
    @login_required  # Use of @login_required decorator
    def members_page():
        return render_template_string("""
            {% extends "base.html" %}
            {% block content %}
                <h2>Members page</h2>
                <p>This page can only be accessed by authenticated users.</p><br/>
                <p><a href={{ url_for('home_page') }}>Home page</a> (anyone)</p>
                <p><a href={{ url_for('members_page') }}>Members page</a> (login required)</p>
            {% endblock %}
            """)

    return app


def create_init():
    # app_md = create_app('prophet_app.config.ConfigClass_MD', db_md)
    app = create_app('prophet_app.config.config', db)
    route(app, db)

    return app


def init_test_data():
    """
    初始化基础数据以及测试数据
    :return:
    """
    from prophet_app.forecast.models import PortfolioData, PortfolioInfo, PortfolioCompareInfo
    from prophet_app.utils.fh_utils import str_2_date
    from sqlalchemy.exc import IntegrityError
    import json

    # 插入测试数据 系统初始化基础组合
    try:
        db.session.add(PortfolioInfo(pl_id=1, name='沪深300指数',
                                     date_from=str_2_date('2005-01-01'), date_to=None,
                                     create_user_id=1, access_type='public'))
        db.session.commit()
        db.session.add(
            PortfolioData(pl_id=1, wind_code='000300.SH', asset_type='index', trade_date=str_2_date('2005-01-01'),
                          weight=1))
        db.session.commit()
        logger.info('初始化基础投资组合数据...成功')
    except IntegrityError:
        logger.exception('初始化基础投资组合数据异常')
        db.session.rollback()

    # 插入测试数据 测试投资组合
    try:
        db.session.add(PortfolioInfo(pl_id=2, name='testpl1',
                                     date_from=str_2_date('2018-03-05'), date_to=str_2_date('2018-08-26'),
                                     create_user_id=1))
        db.session.commit()
        db.session.add(
            PortfolioData(pl_id=2, wind_code='000886.SZ', asset_type='stock', trade_date=str_2_date('2018-03-05'),
                          weight=0.5))
        db.session.add(
            PortfolioData(pl_id=2, wind_code='002273.SZ', asset_type='stock', trade_date=str_2_date('2018-03-05'),
                          weight=0.5))
        db.session.add(
            PortfolioData(pl_id=2, wind_code='002137.SZ', asset_type='stock', trade_date=str_2_date('2018-03-26'),
                          weight=0.5))
        db.session.add(
            PortfolioData(pl_id=2, wind_code='002273.SZ', asset_type='stock', trade_date=str_2_date('2018-03-26'),
                          weight=0.5))
        db.session.commit()
        logger.info('初始化测试投资组合数据...成功')
    except IntegrityError:
        logger.exception('初始化测试投资组合数据异常')
        db.session.rollback()

    # 插入比较规则
    try:
        db.session.add(PortfolioCompareInfo(name='比较组合大小',
                                            date_from=str_2_date('2018-03-05'), date_to=str_2_date('2018-04-04'),
                                            params=json.dumps({
                                                'compare_type': 'rel.rr',
                                                'compare_method': '>',
                                                'asset_type_1': 'portfolio',
                                                'asset_type_2': 'portfolio',
                                                'asset_1': 2,
                                                'asset_2': 1,
                                                'date_start': '2018-01-01',
                                            }),
                                            status='ok', create_user_id=1,
                                            ))
        db.session.add(PortfolioCompareInfo(name='沪深300不跌破3100',
                                            date_from=str_2_date('2018-03-05'), date_to=str_2_date('2018-04-04'),
                                            params=json.dumps({
                                                'compare_type': 'abs.fix_point',
                                                'compare_method': '>',
                                                'asset_type_1': 'index',
                                                'asset_type_2': 'value',
                                                'asset_1': '000300.SH',
                                                'asset_2': 3100,
                                                'date_start': '2018-01-01',
                                            }),
                                            status='ok', create_user_id=1,
                                            ))
        db.session.add(PortfolioCompareInfo(name='沪深300在4000上下100震荡',
                                            date_from=str_2_date('2018-03-05'), date_to=str_2_date('2018-04-04'),
                                            params=json.dumps({
                                                'compare_type': 'abs.fix_point',
                                                'compare_method': 'between',
                                                'asset_type_1': 'index',
                                                'asset_type_2': 'value',
                                                'asset_type_3': 'value',
                                                'asset_1': '000300.SH',
                                                'asset_2': 3900,
                                                'asset_3': 4100,
                                                'date_start': '2018-01-01',
                                            }),
                                            status='ok', create_user_id=1,
                                            ))

        db.session.commit()
        logger.info('初始化投资组合比较信息...成功')
    except IntegrityError:
        logger.exception('初始化投资组合比较信息异常')
        db.session.rollback()


if __name__ == '__main__':
    app = create_init()
    app.run(host='0.0.0.0', debug=True)
    # init_test_data()
