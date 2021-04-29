#Team Fish (Madelyn Mao, Andrew Jiang, Benjamin Gallai)
#SoftDev 
#P3 -- ArRESTed Development, JuSt in Time
#2020-4-25

from flask import Flask,session            #facilitate flask webserving
from flask import render_template   #facilitate jinja templating
from flask import request, redirect           #facilitate form submission
from datetime import datetime
import os
import sqlite3   #enable control of an sqlite database
import json
import tweepy #twitter API for python
import requests
import random

DB_FILE="discobandit.db"
db = sqlite3.connect(DB_FILE, check_same_thread = False) #open if file exists, otherwise create
c = db.cursor()               #facilitate db ops -- you will use cursor to trigger db events

##benjamin
c.execute('CREATE TABLE IF NOT EXISTS users(ID INTEGER NOT NULL PRIMARY KEY, Username text NOT NULL, Password text, Bio text);')
c.execute('CREATE TABLE IF NOT EXISTS posts(ID INTEGER NOT NULL PRIMARY KEY, UserID text NOT NULL, Title text NOT NULL, Text text, Date text);')
db.commit()
app = Flask(__name__)    #create Flask object
app.secret_key = os.urandom(24)

with open("keys/key_api0.txt", "r") as nyt_key:
	nytapi_key = nyt_key.readline()[:-1] #NYT
with open("keys/key_api1.txt", "r") as twitter_keys:
	twapi_key = twitter_keys.readline()[:-1]
	twapi_secret_key = twitter_keys.readline()[:-1]
	twbearer_token = twitter_keys.readline()[:-1]
	twaccess_token = twitter_keys.readline()[:-1]
	twaccess_secret_token = twitter_keys.readline()[:-1] # Twitter
#key2 = open("keys/key_api2.txt", "r").read() # Spotify

#tweepy authentication stuff
auth = tweepy.OAuthHandler(twapi_key, twapi_secret_key)
auth.set_access_token(twaccess_token, twaccess_secret_token)
api = tweepy.API(auth)

@app.route("/") #, methods=['GET', 'POST'])
def disp_loginpage():
	if 'username' in session:
		return render_template('response.html', user = session['username'], status = True)
	else:
		return render_template('login.html',status=False)

@app.route("/auth") # , methods=['GET', 'POST'])
def authenticate():
    problem = 'none'
    if request.args['username'] == '' or request.args['password'] == '': #Check if fields are filled
        return render_template('error.html', error = 'Some fields are empty, try again')     
    print("\n\n\n")
    print("***DIAG: this Flask obj ***")
    print(app)
    print("***DIAG: request obj ***")
    print(request)
    print("***DIAG: request.args ***")
    print(request.args)
    print("***DIAG: request.args['username']  ***")
    print(request.args['username'])
    print("***DIAG: request.headers ***")
    print(request.headers)
    username = request.args['username']
    password = request.args['password']
    c = db.cursor()
    c.execute('SELECT * FROM users WHERE username=? AND password = ?', (username,password))
    data = c.fetchall()

    if data: 
            session['username'] = username
            session['password'] = password
            c.execute('SELECT ID FROM users WHERE username=? AND password = ?', (username,password))
            userid = c.fetchone()
            session['UserID'] = int(userid[0])
            #print(userid) #diagnostic
            return render_template('response.html', user = request.args['username'], tweet_trends = get_tweets(), article = get_article(), status=True)

    else:
        c.execute('SELECT * FROM users WHERE username=?', (username,))
        username_data = c.fetchall()
        if len(username_data)==0:
            return render_template('error.html',status=False,error="User isn't registered. Please create an account.")
        else:
            return render_template('error.html',status=False,error="Incorrect Username/Password.")

def get_tweets():
	trends = api.trends_place(1)
	trend_limit = 10
	trend_links = []
	for topic in trends[0]['trends'][:10]:
		trend_links += [topic['url']]
	return trend_links

def get_articles():
	top_articles = requests.get('https://api.nytimes.com/svc/topstories/v2/home.json?api-key=' + nytapi_key).json()['results']
	your_article_index = random.randint(0,len(top_articles) - 1)
	your_article = top_articles[your_article_index]
	return [your_article['title'], your_article['abstract'], your_article['url'], your_article['byline']]

# sign up for an account, signup.html takes username, password, bio 
# check if username is unique, add password specifications if desired

@app.route("/signup") #methods = ['GET','POST'])
def signup():
        global usercount
        c = db.cursor()
        username = request.args['newusername']
        password = request.args['newpassword']
        bio = request.args['bio']
        c.execute('SELECT * FROM users WHERE username=?', (username,))
        data = c.fetchall()
        if len(data) > 0:
            return render_template('error.html', error = 'A user with that username already exists.')
        params = (username,password,bio)
        c.execute('INSERT INTO users(Username,Password,Bio) VALUES(?,?,?)', params)
        db.commit()
        return render_template('login.html',status=False)

# middle method, going straight to signup doesn't work. renders the actual signup page    
@app.route("/newuser", methods = ['GET','POST'])
def newuser():
        return render_template('signup.html',status=False)


if __name__ == "__main__": #false if this file imported as module
    #enable debugging, auto-restarting of server when this file is modified
    app.debug = True 
    app.run()
