from peewee import *

import os
import datetime

from playhouse.db_url import connect
from flask_login import UserMixin

# DB = SqliteDatabase('booksom.sqlite')
DATABASE = connect(os.environ.get('DATABASE_URL') or 'sqlite:///booksom.sqlite')

class BaseModel(Model):
    class Meta:
        database = DATABASE

class User(UserMixin, BaseModel):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField()

class Book(BaseModel):
    title = CharField(unique=True)
    author =  CharField()
    cover = CharField()
    genre = CharField()
    isbn = CharField()
    notes = CharField()
    owner = ForeignKeyField(User, backref='books')

class UserProfile(BaseModel):
    username = ForeignKeyField(User, backref='user')
    profilepic = CharField()
    name = CharField()
    location = CharField()
    # favebook = ForeignKeyField(Book, backref='user')
    favebook = CharField()
    wishlist = CharField()

class Post(BaseModel):
    title = CharField()
    author = ForeignKeyField(User, backref='posts')
    post = CharField()
    date = DateTimeField(default=datetime.datetime.now)

class Comment(BaseModel):
    comment = CharField()
    author = ForeignKeyField(User, backref='comments')
    postid = ForeignKeyField(Post, backref='comments')
    date = DateTimeField(default=datetime.datetime.now)

def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Book, Post, Comment, UserProfile], safe=True)
    DATABASE.close()