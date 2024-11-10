'''SQLAlchemy User and Tweet models for our database'''
from flask_sqlalchemy import SQLAlchemy

# Create a DB object from the SQLAlchemy class
DB = SQLAlchemy()

# Making a User table using SQLAlchemy
class User(DB.Model):
    """ Class representing the user of twitoff
    creating a User Table with SQLAlchemy"""
    # id column
    id = DB.Column(DB.BigInteger, primary_key=True)
    # username column
    username = DB.Column(DB.String, nullable=False)
    # keeps track of id for the newest tweet said by the user
    newest_tweet_id = DB.Column(DB.BigInteger)
    # backref is as-if we had added a tweets list to the User class
    # tweets = []

    def __repr__(self):
        return "<User: {}>".format(self.username)


class Tweet(DB.Model):
    """ Class representing the Tweet the user has typed in twitoff.
    Keeps track of the Tweets for each user"""
    # id column
    id = DB.Column(DB.BigInteger, primary_key=True)
    # text column using Unicode to allow for emoji's, links and special characters
    text = DB.Column(DB.Unicode(300))
    vect = DB.Column(DB.PickleType, nullable=False)
    # user_id column (foreign / secondary key)
    user_id = DB.Column(DB.BigInteger, DB.ForeignKey(
        'user.id'), nullable=False)
    # user column creates a two-way link between a user object and a tweet object
    # backref can now find the User by the Tweet or find the Tweet by the User
    user = DB.relationship('User', backref=DB.backref('tweets', lazy=True))


    def __repr__(self):
        return "<Tweet: {}>".format(self.text)
