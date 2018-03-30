from flask import Flask, render_template, render_template_string
from flask_login import LoginManager
from flask_mail import Mail
from flask_user.forms import LoginForm
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter
from prophet_app.controllers.forecast import forecast_blueprint
from flask import Blueprint


def create_app(config_path):
    app = Flask(__name__, static_url_path='')
    app.debug = True
    app.secret_key = 'M!@#$@#$%#$%alksdjf;lkj'

    # 添加 BluePrint
    app.register_blueprint(forecast_blueprint, url_prefix='/forecast')

    # app.config.from_object(__name__+'.ConfigClass')
    app.config.from_object(config_path)

    # Initialize Flask extensions
    db = SQLAlchemy(app)                            # Initialize Flask-SQLAlchemy
    mail = Mail(app)                                # Initialize Flask-Mail

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

    # Create all database tables
    db.create_all()

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


if __name__ == '__main__':
    app = create_app('prophet_app.config.ConfigClass')
    app.run(host='0.0.0.0', debug=True)
