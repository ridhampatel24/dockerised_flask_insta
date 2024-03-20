from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from .extensions import db

bcrypt = Bcrypt()

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    profile_picture = db.Column(db.String(255), nullable=True)
    bio=db.Column(db.String(255), nullable=True)
    posts = db.relationship('Post', back_populates='user')

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
    )


    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

   
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    
    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    
    def followed_posts(self):
        followed_posts = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own_posts = Post.query.filter_by(user_id=self.id)
        return followed_posts.union(own_posts).order_by(Post.timestamp.desc())
    

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    picture = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username=db.Column(db.String(255),nullable=False)

    # Define relationship with User model
    user = db.relationship('User', back_populates='posts')

    def __repr__(self):
        return f"<Post {self.id}>"
    
