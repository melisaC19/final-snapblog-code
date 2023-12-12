from flask import Flask, render_template, request, redirect, session, g, url_for
from database import *
import datetime
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = "kdjfdlkjhfsdkjhfdskj56kjsdhdskjhfkjs"
app.config['SESSION_TYPE'] = 'filesystem'
bcrypt = Bcrypt(app) 

create_db()
create_tables()

def check_loggedin_user():
    username = session.get("username")
    if username is None:
        g.user = None
    else:
        g.user = get_user(username)

@app.route("/feed")
def feed():
    check_loggedin_user()
    page = request.args.get('page', 1, type=int)
    tweets_per_page = 10  
    tweets = get_all_tweets()
    total_tweets = len(tweets)
    total_pages = (total_tweets + tweets_per_page - 1) // tweets_per_page
    start_index = (page - 1) * tweets_per_page
    end_index = start_index + tweets_per_page
    tweets_to_display = tweets[start_index:end_index]

    return render_template('feed.html', tweets=tweets_to_display, total_pages=total_pages, page=page)

if __name__ == '__main__':
    app.run(debug=True)

@app.route("/register", methods=['GET', 'POST'])
def register():
    check_loggedin_user()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        birthdate = request.form.get('birthdate')
        email = request.form.get('email')
        try:
            datetime.date.fromisoformat(birthdate)
        except ValueError:
            return render_template("register.html", message="Incorrect data format, should be YYYY-MM-DD")
        if password != password2:
            return render_template("register.html", message="Passwords do not match.")
        else:
            user = get_user(username)
            if user is not None:
                return render_template("register.html", message="Username already taken.")
            else:
                add_user(username, bcrypt.generate_password_hash(password).decode('utf-8'), birthdate, email)
                return redirect("/login")
    else:
        return render_template("register.html")
    

@app.route("/login", methods=['GET', 'POST'])
def login():
    check_loggedin_user()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = get_user(username)
        if user is None:
            return render_template("login.html", message="User not found")
        else:
            if bcrypt.check_password_hash(user[2], password):
                session["username"] = username
                return redirect("/feed")
            else:
                return render_template("login.html", message="Wrong password")      
    else:
        return render_template("login.html")
    
@app.route("/tweet", methods=['POST'])
def tweet():
    check_loggedin_user()
    
    text = request.form.get('tweet')
    add_tweet(text, g.user[0])
    return redirect("/feed")

@app.route("/logout")
def logout():
    session.pop("username")
    return redirect("/feed")

@app.route("/profile")
def profile():
    check_loggedin_user()
    if g.user:
        user_id = g.user[0]
        user_data = get_user_by_id(user_id)
        tweets = get_tweets_by_user_id(user_id)
        return render_template('profile.html', user=user_data, tweets=tweets)
    else:
        return redirect(url_for('login'))