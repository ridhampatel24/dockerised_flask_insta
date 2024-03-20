from flask import Flask
from config import Config
from app.views.authentication import auth_bp
from app.views.post import post_bp
from app.views.profile import profile_bp
from .extensions import db,migrate,mail,csrf
from itsdangerous import URLSafeTimedSerializer
from datetime import timedelta


def create_app():
    app = Flask(__name__)
    
    app.config.from_object(Config)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://akshar:Akshar3208@db/instagram'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Replace with your email server
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USERNAME'] = '1277keyur@gmail.com'
    app.config['MAIL_DEFAULT_SENDER'] = '1277keyur@gmail.com'   # Replace with your email credentials
    app.config['MAIL_PASSWORD'] = 'lekgqvjsyhracgje'
    app.config['JWT_SECRET_KEY'] = 'adfafadfadfasfsdffsadfddc'
    

    db.init_app(app)
    
    migrate.init_app(app,db)
    mail.init_app(app)
    csrf.init_app(app)
   
   
    app.register_blueprint(auth_bp,url_prefix="/auth")
    app.register_blueprint(post_bp,url_prefix="/post")
    app.register_blueprint(profile_bp,url_prefix="/profile")

    return app
