from flask import Blueprint, render_template,current_app,redirect,url_for
from flask import Flask, request, jsonify,session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from ..extensions import *
from config import Config
from app.models import db, User,Post

from functools import wraps
import jwt
import datetime
import time

auth_bp = Blueprint('authentication', __name__)





serializer = URLSafeTimedSerializer(Config.SECRET_KEY)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        access_token = session.get('access_token')
        
       

        if not access_token:
            return 'Token is missing!', 403

        try:
            data = jwt.decode(access_token,  Config.SECRET_KEY,algorithms=["HS256"])
            print(data)
        except jwt.ExpiredSignatureError:
            return 'Token has expired!', 403
        except jwt.InvalidTokenError:
            return 'Token is invaliddfdf!', 403

        return f(*args, **kwargs)

    return decorated

def generate_tokens(email):
    expiration_date = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    expiration_date_refresh = datetime.datetime.utcnow() + datetime.timedelta(days=1)
           
    access_token = jwt.encode({'email': email, 'exp': expiration_date}, Config.SECRET_KEY,algorithm="HS256")
    refresh_token = jwt.encode({'email': email,'exp': expiration_date_refresh},Config.SECRET_KEY,algorithm="HS256")

    return access_token, refresh_token




@auth_bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if passwords match
        if password != confirm_password:
            message = 'Passwords do not match'
        else:
            if User.query.filter_by(email=email).first():
                message = 'Email is already registered'
            else:
                # Create new user instance
                new_user = User(username=username, email=email)
                new_user.set_password(password)

                # Save user to database
                db.session.add(new_user)
                db.session.commit()

                # Generate token for email verification
                token = serializer.dumps(email, salt='email-confirm')
                print("hello")
                try:
                    print("hello")
                    confirmation_url = f"http://localhost:5000/auth/confirm_email/{token}"
                    message = Message(subject='Confirm your email', recipients=[email])
                    message.body = f'Click on the link to confirm your email: {confirmation_url}'
                    mail.send(message)
                except Exception as e:
                    print(e)

        return render_template('authentication/register.html', message="Please check your email for verification")

    return render_template('authentication/register.html')

@auth_bp.route('/confirm_email/<token>', methods=['GET'])
def confirm_email(token):
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=3600)  
    except SignatureExpired:
        return render_template('authentication/confirmemail.html', message="Token expired. Please try registering again.")
        

    user = User.query.filter_by(email=email).first()
    if not user:
        return render_template('authentication/confirmemail.html', message="User not found")
       

    user.confirmed = True
    db.session.commit()
    return render_template('authentication/confirmemail.html', message="Email confirm succesfull")







# @auth_bp.route('/refresh',methods=['POST'])
# def refresh():
#     refresh_token = request.form['refresh_token']
#     try:
#         decoded_refresh_token = jwt.decode(refresh_token, Config.SECRET_KEY)
#         email = decoded_refresh_token.get('email')
#         access_token, new_refresh_token = generate_tokens(email)
#         # Update tokens in session
#         session['access_token'] = access_token
#         session['refresh_token'] = new_refresh_token
#         return jsonify({'access_token': access_token.decode('utf-8')})
#     except jwt.ExpiredSignatureError:
#         return 'Expired refresh token!', 401
#     except jwt.InvalidTokenError:
#         return 'Invalid refresh token!', 401
   

   


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')
        user =User.query.filter_by(email=email).first()
        print("hello")
        print(user.confirmed)
        if user and user.check_password(password) and user.confirmed:
            access_token, refresh_token = generate_tokens(email)
            print("hello2")
            session['access_token'] = access_token
            session['refresh_token'] = refresh_token
            session['username']=user.username
            print(refresh_token)
            print(access_token)
            

            return redirect(url_for('authentication.home'))
        else:
            print("hello3")
            if not user.confirmed:
                return render_template('authentication/login.html',message="please confirm your email")
            else:

                return render_template('authentication/login.html',message="Invalid credentials")
    else:
        return render_template('authentication/login.html',message="")
    

@auth_bp.route('/logout')
@token_required
def logout():
    session.clear()
    
    # Redirect to the login page or any other desired page
    return redirect(url_for('authentication.login'))



    
@auth_bp.route('/home')
@token_required
def home():
    posts_data = db.session.query(
        Post,
        User.username,
        User.profile_picture
    ).join(
        User, Post.user_id == User.id
    ).all()
    

    user=User.query.filter_by(username=session.get('username')).first()
    user_profile_picture=""
    if(user.profile_picture):
        user_profile_picture=user.profile_picture


    return render_template('home.html',posts=posts_data,profile_picture=user_profile_picture)