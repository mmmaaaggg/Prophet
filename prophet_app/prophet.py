from flask import Flask, render_template, render_template_string
from flask_login import LoginManager
from flask_mail import Mail
from flask_user.forms import LoginForm
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter
from prophet_app.forecast import forecast_blueprint
from prophet_app import db, User


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

    mail = Mail(app)                                # Initialize Flask-Mail
    return app


def route(app, db):

    # Setup Flask-User
    db_adapter = SQLAlchemyAdapter(db, User)        # Register the User model
    user_manager = UserManager(db_adapter, app)     # Initialize Flask-User

    @app.route('/')
    def hello_world():
        return render_template('index.html')

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
    @login_required                                 # Use of @login_required decorator
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


if __name__ == '__main__':
    app = create_init()
    app.run(host='0.0.0.0', debug=True)
