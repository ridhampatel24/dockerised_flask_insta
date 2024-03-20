from flask import Blueprint, render_template,current_app,redirect,url_for,flash
from flask import Flask, request, jsonify,session
from flask_sqlalchemy import SQLAlchemy
from ..extensions import *
from config import Config
from app.models import db, User,Post
from app.views.authentication import token_required
from flask import current_app
from werkzeug.utils import secure_filename
import datetime
import time
import os
import jwt
from app.views import authentication
from app.views.post import save_picture


profile_bp = Blueprint('profile', __name__)

def get_current_user(username):
    return User.query.filter_by(username=username).first()

@profile_bp.route('/')
@token_required
def profile():
    token_data = jwt.decode(session.get('access_token'),Config.SECRET_KEY, algorithms=['HS256'])
    user_email = token_data.get('email')
    user = User.query.filter_by(email=user_email).first()
    followers = user.followers.count()  
    following = user.followed.count()  
    posts=Post.query.filter_by(user_id=user.id).all()
    total_post=len(posts)
    bio=""
    if(user.bio):
        bio=user.bio
    profile_picture=""
    if(user.profile_picture):

        
        profile_picture=user.profile_picture

    return render_template('profile/profile.html',posts=posts,username=user.username,total_post=total_post,profile_picture=profile_picture,bio=bio,followers=followers,following = following)

@profile_bp.route('/<username>')
@token_required
def user_profile(username):
    user=User.query.filter_by(username=username).first()
    posts=Post.query.filter_by(user_id=user.id).all()
    followers = user.followers.count()  
    following = user.followed.count()  
    
    total_post=len(posts)
    bio=""
    if(user.bio):
        bio=user.bio
    user_profile_picture=""
    if(user.profile_picture):
        user_profile_picture=user.profile_picture
    current_user = get_current_user(session.get('username'))
    current_user_picture=""
    if(current_user.profile_picture):
        current_user_picture=current_user.profile_picture
    is_following = current_user.is_following(user) if current_user else False

    return render_template('profile/user_profile.html',posts=posts,username=user.username,total_post=total_post,profile_picture=current_user_picture,user_profile_picture=user_profile_picture,bio=bio,is_following=is_following,followers=followers,following = following)





@profile_bp.route('/delete/<int:post_id>', methods=['POST'])
@token_required
def delete_post(post_id):
    post = Post.query.get(post_id)
    if post:
        db.session.delete(post)
        db.session.commit()
    return redirect(url_for('profile.profile'))


@profile_bp.route('/setting')
@token_required
def setting():

    token_data = jwt.decode(session.get('access_token'),Config.SECRET_KEY, algorithms=['HS256'])
    user_email = token_data.get('email')


    user = User.query.filter_by(email=user_email).first()
    bio="Enter your bio"
    if(user.bio):
        bio=user.bio
    profile_picture=""
    if(user.profile_picture):

        
        profile_picture=user.profile_picture
    print(user.profile_picture)
    print(bio)
    return render_template('profile/setting.html',profile_picture=profile_picture,bio=bio)

@profile_bp.route('/upload', methods=['GET','POST'])
@token_required
def profile_picture():
    if request.method=='POST':
        data=request.form
        
        profile_picture = request.files['file']
        picture_path = save_picture(profile_picture,'profile_picture')
        token_data = jwt.decode(session.get('access_token'),Config.SECRET_KEY, algorithms=['HS256'])
        user_email = token_data.get('email')


        user = User.query.filter_by(email=user_email).first()
        user.profile_picture = picture_path
        db.session.commit()
    return redirect(url_for('profile.setting'))
    

@profile_bp.route('/update', methods=['GET','POST'])
@token_required
def update_profile():
    if request.method=='POST':
        data=request.form

        username=data.get('username')
        if(not username):
            username=session.get('username')
        bio=data.get('bio')

        print(username)
        print(bio)

        
        token_data = jwt.decode(session.get('access_token'),Config.SECRET_KEY, algorithms=['HS256'])
        user_email = token_data.get('email')


        user = User.query.filter_by(email=user_email).first()
        user.username=username
        session['username']=username
        user.bio=bio
        db.session.commit()
    return redirect(url_for('profile.setting'))


@profile_bp.route('/update/password', methods=['GET','POST'])
@token_required
def update_password():
    if request.method=='POST':
        data=request.form

        password=data.get('password')
        rpassword=data.get('rpassword')

        if password != rpassword:
            message = 'Passwords do not match'
            flash('Passwords do not match', 'error')
        else:

        
        
            token_data = jwt.decode(session.get('access_token'),Config.SECRET_KEY, algorithms=['HS256'])
            user_email = token_data.get('email')


            user = User.query.filter_by(email=user_email).first()
            user.set_password(password)

        
            db.session.commit()
            flash('Password updated successfully', 'success')
    return redirect(url_for('profile.setting'))

@profile_bp.route('/search', methods=['GET','POST'])
@token_required
def search():
    
    current_user = get_current_user(session.get('username'))
    current_user_picture=""
    if(current_user.profile_picture):
        current_user_picture=current_user.profile_picture
    if request.method == 'POST':
        search_query = request.form.get('query')
        if search_query:
            users = User.query.filter(User.username.ilike(f'%{search_query}%')).all()
            return render_template('profile/search.html', users=users,profile_picture=current_user_picture)
    return render_template('profile/search.html',profile_picture=current_user_picture)






@profile_bp.route('/follow/<username>',methods=['POST'])
@token_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    current_user = get_current_user(session.get('username'))
    if user == current_user:
        
        return redirect(url_for('profile.user_profile', username=username))
   
    current_user.follow(user)
    db.session.commit()
   
    return redirect(url_for('profile.user_profile', username=username))


@profile_bp.route('/unfollow/<username>',methods=['POST'])
@token_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    current_user = get_current_user(session.get('username'))
    if user == current_user:
        
        return redirect(url_for('profile.user_profile', username=username))
   
    current_user.unfollow(user)
    db.session.commit()
   
    return redirect(url_for('profile.user_profile', username=username))