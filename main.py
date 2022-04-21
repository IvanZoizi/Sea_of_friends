from urllib.request import urlopen

from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, current_user, login_required

import os
import json
import random

from data import db_session
from forms.register import RegisterForm
from forms.login import LoginForm
from data.user import User
from data.private_post import PrivatePost
from data.reguser import RegUser
from forms.post import PostForm
from data.public_post import PublicPost

from mail import send_mail


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hakatonchik_one_love'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    db_session.global_init('db/user.db')

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


@app.route('/')
def base_window():
    db_sess = db_session.create_session()
    return 'Привет'


@app.route('/register', methods=['GET', "POST"])
def register():
    db_sess = db_session.create_session()
    form = RegisterForm()
    if form.validate_on_submit():
        user = RegUser()
        user.name = form.name.data
        user.email = form.email.data
        user.hashed_password = user.set_password(form.password.data)
        url = 'http://ipinfo.io/json'
        response = urlopen(url)
        data = json.load(response)
        user.location = data['loc']
        db_sess.add(user)
        db_sess.commit()
        send_mail(form.email.data)
        return redirect('/')
    return render_template('forms.html', form=form)


@app.route('/login', methods=['GET', "POST"])
def login():
    db_sess = db_session.create_session()
    form = LoginForm()
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        print(user)
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', form=form, message='Некорректный логин или пароль')
    return render_template('login.html', form=form)


@app.route('/login/<string:email>')
def authokey(email):
    db_sess = db_session.create_session()
    reg_user = db_sess.query(RegUser).filter(RegUser.email == email).first()
    if reg_user:
        user = User()
        user.name = reg_user.name
        user.email = reg_user.email
        user.hashed_password = reg_user.hashed_password
        user.location = reg_user.location
        user.interests = reg_user.interests
        db_sess.add(user)
        db_sess.commit()
    return redirect('/')


@login_required
@app.route('/add/post')
def add_post():
    db_sess = db_session.create_session()
    form = PostForm()
    if form.validate_on_submit():
        if form.private:
            post = PrivatePost()
            post.creater = current_user.id
            post.content = form.content.data
            db_sess.add(post)
            db_sess.commit()
        else:
            post = PublicPost()
            post.creater = current_user.id
            post.content = form.content.data
            db_sess.add(post)
            db_sess.commit()
            return render_template('/')

    return render_template('')


if __name__ == '__main__':
    main()