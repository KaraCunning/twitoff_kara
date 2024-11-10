"""definine all our apps that brings everything together"""
from os import getenv
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from .predict import predict_user
from .models import DB, User, Tweet
from .twitter import add_or_update_user, update_all_users, get_all_users



def create_app():
    """Creating the create_app factory"""
    # syntax for creating a new flask app
    app = Flask(__name__)

    # database configurations
    app.config['SQLALCHEMY_DATABASE_URI'] = getenv("DATABASE_URI")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # register our database with the app
    DB.init_app(app)

    #my_var = "Twitoff App"

    @app.route('/')
    def root():
        """"when someone visits the homepage, returns on the screen
        info from base.html and the browser title = Home"""
        return render_template('base.html', title="Home", users=User.query.all())
    
    @app.route('/populate')
    def populate():
        add_or_update_user('ryanallred')
        add_or_update_user('nasa')
        return render_template('base.html', title='Populate')

    @app.route('/bananas')
    def bananas():
        """"when someone visits the homepage, returns on the screen
        info from base.html and the browser title = Bananas"""
        return render_template('base.html', title='Bananas')
    
    @app.route('/update')
    def update():
        '''updates all users'''
        usernames = get_all_usernames()
        for username in usernames:
            add_or_update_user(username)
        return "All users have been updated"

    @app.route('/reset')
    def reset():
        """dropping all the tables and re-creating them each time"""
        # drop all tables
        DB.drop_all()
        # recreate all the tables according to the
        # indicated schema  in models.py
        DB.create_all()
        #return "database has been reset"
        return render_template('base.html', title='Reset Database')
    return app
    @app.route('/user', methods=["POST"])
    @app.route('/user/<name>', methods=["GET"])
    def user(name=None, message=''):
        # we either take name that was passed in or we pull it
        # from our request.values which would be accessed through the
        # user submission
        name = name or request.values['user_name']
        try:
            if request.method == 'POST':
                add_or_update_user(name)
                message = "User {} Successfully added!".format(name)

            tweets = User.query.filter(User.username == name).one().tweets

        except Exception as e:
            message = "Error adding {}: {}".format(name, e)

            tweets = []

        return render_template("user.html", title=name, tweets=tweets, message=message)

    @app.route('/compare', methods=["POST"])
    def compare():
        user0, user1 = sorted(
            [request.values['user0'], request.values["user1"]])

        if user0 == user1:
            message = "Cannot compare users to themselves!"

        else:
            # prediction returns a 0 or 1
            prediction = predict_user(
                user0, user1, request.values["tweet_text"])
            message = "'{}' is more likely to be said by {} than {}!".format(
                request.values["tweet_text"],
                user1 if prediction else user0,
                user0 if prediction else user1
            )

        return render_template('prediction.html', title="Prediction", message=message)

    return app