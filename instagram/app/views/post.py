from flask import Blueprint, render_template,current_app,redirect,url_for
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

post_bp = Blueprint('post', __name__)


def save_picture(file,location):
    # Define the directory where uploaded pictures will be saved
    UPLOADS_DIR = os.path.join(current_app.root_path, 'static', f"{location}")
    
    if not os.path.exists(UPLOADS_DIR):
        os.makedirs(UPLOADS_DIR)
    
    # Generate a unique filename for the uploaded picture
    filename = secure_filename(file.filename)
    file_path =os.path.join(UPLOADS_DIR,filename)
    file_path2=f"/{location}/{filename}"
    
    # Save the uploaded picture to the filesystem
    file.save(file_path)
    
    # Return the path of the saved file
    return file_path2

@post_bp.route('/addpost', methods=['GET','POST'])
@token_required
def addpost():
    data=request.form
    caption=data.get('caption')
    picture_file = request.files['addPostUrl']
    picture_path = save_picture(picture_file,'uploads')
    token_data = jwt.decode(session.get('access_token'),Config.SECRET_KEY, algorithms=['HS256'])
    user_email = token_data.get('email')


    user = User.query.filter_by(email=user_email).first()
    new_post = Post(picture=picture_path, caption=caption, user_id=user.id,username=user.username)

    db.session.add(new_post)
    db.session.commit()
    return redirect(url_for('authentication.home'))


