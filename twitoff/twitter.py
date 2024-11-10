'''Handles connection to NotTiwtter API using NotTweepy'''
from os import getenv
import sys
sys.path.insert(0, '/Users/karacunningham/Desktop/twitoff_kara')
import not_tweepy as tweepy
import spacy
from .models import DB, User, Tweet

# getting our environment variables
key = getenv('TWITTER_API_KEY')
secret = getenv('TWITTER_API_KEY_SECRET')

#NotTwitter = tweepy.API(getenv('NOT_TWITTER_URL'))

# Connect to the Twitter API
TWITTER_AUTH = tweepy.OAuthHandler(key, secret)
TWITTER = tweepy.API(TWITTER_AUTH)

def add_or_update_user(username):
    '''Takes the user name and pulls user from Twitter API'''
    
    try:
        # gets back twitter user object
        twitter_user = TWITTER.get_user(username)
        # Either updates or adds user to our DB
        db_user = (User.query.get(twitter_user.id)) or User(
            id=twitter_user.id, username=username)
        DB.session.add(db_user)  # Add user if don't exist

        # Grabbing tweets from "twitter_user"
        tweets = twitter_user.timeline(
            count=200,
            exclude_replies=True,
            include_rts=False,
            tweet_mode="extended",
            since_id=db_user.newest_tweet_id
        )

        # check to see if the newest tweet in the DB is equal to the newest tweet from the Twitter API, if they're not equal then that means that the user has posted new tweets that we should add to our DB. 
        if tweets:
            db_user.newest_tweet_id = tweets[0].id

        # tweets is a list of tweet objects
        for tweet in tweets:
            # type(tweet) == object
            # Turn each tweet into a word embedding. (vectorization)
            tweet_vector = vectorize_tweet(tweet.text)
            db_tweet = Tweet(
                id=tweet.id,
                text=tweet.text,
                vect=tweet_vector
            )
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)

    except Exception as e:
        print(f"Error processing {username}: {e}")
        raise e

    else:
        DB.session.commit()
# Helper function to get all usernames
def get_all_usernames():
    """Returns a list of all usernames in the database."""
    return [user.username for user in User.query.all()]

# Take a tweet text and turn it into
# an embedding "vector"
nlp = spacy.load('my_model/')

def vectorize_tweet(tweet_text):
    '''def to turn tweet text into word embedding'''
    return nlp(tweet_text).vector

def update_all_users():
    '''create an update route to update all users when called'''
    usernames = []
    Users = User.query.all()
    for user in Users:
        add_or_update_user(user.username)

    return usernames