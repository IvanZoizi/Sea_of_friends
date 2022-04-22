from urllib.request import urlopen

from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, current_user, login_required, logout_user

import os
import json

from data.comments import Comments
from data.private_comments import PrivateComments
from forms.comments import CommentForm
from data import db_session
from forms.register import RegisterForm
from forms.login import LoginForm
from data.user import User
from data.private_post import PrivatePost
from data.reguser import RegUser
from forms.post import PostForm
from data.public_post import PublicPost
from forms.communities import CommunitiesForm
from data.communities import Communities

from mail import send_mail

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hakatonchik_one_love'
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


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
    posts = db_sess.query(PublicPost).all()
    return render_template('index.html', message=posts, current_user=current_user)


@app.route('/register', methods=['GET', "POST"])
def register():
    db_sess = db_session.create_session()
    form = RegisterForm()
    if request.method == 'POST':
        user = RegUser()
        user.name = form.name.data
        user.email = form.email.data
        user.hashed_password = user.set_password(form.password.data)
        user.telegram = form.telegram.data
        if form.location.data:
            user.location = form.location.data
        else:
            url = 'http://ipinfo.io/json'
            response = urlopen(url)
            data = json.load(response)
            loc = ','.join(data['loc'].split(','))
            user.location = loc
        interes = []
        if form.music.data:
            interes.append('Музыка')
        if form.book.data:
            interes.append("Книги")
        if form.kitchen.data:
            interes.append("Еда")
        if form.sport.data:
            interes.append("Спорт")
        if form.picture.data:
            interes.append("Рисование")
        if form.movie.data:
            interes.append("Фильма, сериалы")
        if form.turizm.data:
            interes.append("Туризм")
        user.interests = ';'.join(interes)
        try:
            db_sess.add(user)
            db_sess.commit()
        except Exception as e:
            return render_template('forms.html', form=form, message='Ошибка в логине/пароле')
        send_mail(form.email.data)
        return redirect('/')
    return render_template('forms.html', form=form)


@app.route('/login', methods=['GET', "POST"])
def login():
    db_sess = db_session.create_session()
    form = LoginForm()
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == form.email.data).first()
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
        user.telegram = reg_user.telegram
        db_sess.add(user)
        db_sess.commit()
    return redirect('/')


@login_required
@app.route('/add/post', methods=["GET", "POST"])
def add_post():
    db_sess = db_session.create_session()
    form = PostForm()
    if form.validate_on_submit():
        post = PublicPost()
        post.creater = current_user.id
        post.content = form.content.data
        db_sess.add(post)
        db_sess.commit()
        return redirect('/')
    return render_template('add_post.html', form=form, current_user=current_user)


@app.route('/add/communities', methods=['GET', "POST"])
def add_communities():
    db_sess = db_session.create_session()
    form = CommunitiesForm()
    if form.validate_on_submit():
        groups = db_sess.query(Communities).filter(Communities.creater == current_user.id).all()
        if groups:
            return render_template('add_communitie.html', message='Вы уже являетесь создателем одной группы', form=form)
        group = Communities()
        group.creater = current_user.id
        group.name = form.name.data
        group.interes = form.interes.data
        group.city = form.location.data
        group.description = form.interes.data
        group.collaborators = str(current_user.id)
        interes = []
        if form.music.data:
            interes.append('Музыка')
        if form.book.data:
            interes.append("Книги")
        if form.kitchen.data:
            interes.append("Еда")
        if form.sport.data:
            interes.append("Спорт")
        if form.picture.data:
            interes.append("Рисование")
        if form.movie.data:
            interes.append("Фильма, сериалы")
        if form.turizm.data:
            interes.append("Туризм")
        group.interests = ';'.join(interes)
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        lis = user.groups.split(';|;')
        if lis[0] != '':
            lis.append(group.name)
        else:
            lis[0] = group.name
        user.groups = ';|;'.join(lis)
        db_sess.add(group)
        db_sess.commit()
        return redirect('/communities')
    return render_template('add_communitie.html', form=form)


@app.route('/delete/communities/<int:id>')
@login_required
def delete_communities(id):
    db_sess = db_session.create_session()
    group = db_sess.query(Communities).filter(Communities.id == id).first()
    if current_user.id == group.creater:
        posts = db_sess.query(PrivatePost).filter(PrivatePost.creater == current_user.id).all()
        coms = db_sess.query(PrivateComments).filter(PrivateComments.creater == current_user.id).all()
        for i in zip(posts, coms):
            try:
                db_sess.delete(i[0])
            except Exception:
                pass
            try:
                db_sess.delete(i[1])
            except Exception:
                pass
        db_sess.delete(posts)
        db_sess.delete(coms)
        db_sess.delete(group)
        db_sess.commit()
    return redirect('/communities')


@app.route('/communities')
def communities():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        communities = db_sess.query(Communities).order_by(Communities.interes.like(current_user.interests)).all()
    else:
        communities = db_sess.query(Communities).all()
    return render_template('communities.html', lis=communities, current_user=current_user)


@app.route('/person/account/<int:id>')
def personal_account(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    posted = db_sess.query(PublicPost).filter(PublicPost.creater == id).all()
    interes = ', '.join(user.interests.split(';'))
    print(user.groups.split(';|;'))
    groups = ', '.join([i for i in user.groups.split(';|;') if i != ''])
    print(groups)
    return render_template('user.html', user=user, posted=posted, current_user=current_user, interes=interes,
                           groups=groups)


@app.route('/seach/friend', methods=['GET', 'POST'])
@login_required
def seach():
    try:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if request.method == 'POST':
            if request.form['please'] == '':
                url = 'http://ipinfo.io/json'
                response = urlopen(url)
                data = json.load(response)
                loc = ','.join(data['loc'].split(','))
                user.location = loc
                db_sess.commit()
            else:
                user.location = request.form['please']
                db_sess.commit()
        ids = list()
        lis = list()
        users = db_sess.query(User).all()
        for i in users:
            lis.append(list(map(float, i.location.split(','))))
            ids.append(f'<a href="/person/account/{i.id}">Профиль пользователя {i.name} </a>')
        data = {'lis': lis, 'content': ids}
        return render_template('seach.html', center=list(map(float, user.location.split(','))), ids=json.dumps(ids),
                               data=data)
    except Exception as e:
        abort(404)


@login_required
@app.route('/delete/post/<int:state>/<int:id>')
def delete_post(state, id):
    db_sess = db_session.create_session()
    post = None
    if state == 1:
        post = db_sess.query(PrivatePost).filter(PrivatePost.id == id).filter(
            PrivatePost.creater == current_user.id).first()
    elif state == 2:
        post = db_sess.query(PublicPost).filter(PublicPost.id == id).filter(
            PublicPost.creater == current_user.id).first()
    if post:
        coms = db_sess.query(PrivateComments).filter(PrivateComments.private_post == id).all()
        for i in coms:
            db_sess.delete(i)
        db_sess.delete(post)
        db_sess.commit()
    return redirect('/communities/' + str(id))


@app.route('/communities/<int:id>')
def communities_one(id):
    db_sess = db_session.create_session()
    communities = db_sess.query(Communities).filter(Communities.id == id).first()
    if not communities:
        return redirect('/communities')
    posted = db_sess.query(PrivatePost).filter(PrivatePost.group == id).all()
    if current_user.is_authenticated:
        admin = True if communities.creater == current_user.id else False
        collabarators = True if str(current_user.id) in communities.collaborators else False
    else:
        admin = False
        collabarators = False
    return render_template('communiti.html', current_user=current_user, admin=admin, collabarators=collabarators,
                           communities=communities, posted=posted)


@app.route('/add/post/<int:id>', methods=["GET", "POST"])
@login_required
def add_post_private(id):
    db_sess = db_session.create_session()
    communities = db_sess.query(Communities).filter(Communities.id == id).first()
    form = PostForm()
    if form.validate_on_submit():
        if current_user.id == communities.creater:
            post = PrivatePost()
            post.creater = current_user.id
            post.content = form.content.data
            post.group = id
            db_sess.add(post)
            db_sess.commit()
            return redirect('/communities' + str(id))
        else:
            return render_template('add_post.html', messgae='Вы не являетесь создателем даннной группы', form=form)
    return render_template('add_post.html', form=form)


@app.route("/add/comment/<int:id>", methods=['GET', 'POST'])
@login_required
def add_comments(id):
    db_sess = db_session.create_session()
    form = CommentForm()
    if form.validate_on_submit():
        com = Comments()
        com.creater = current_user.id
        com.content = form.name.data
        com.post = id
        db_sess.add(com)
        db_sess.commit()
        return redirect('/add/comment/' + str(id))
    coms = db_sess.query(Comments).filter(Comments.post == id).all()
    return render_template('add_comments.html', form=form, current_user=current_user, com=coms)


@app.route('/comment/post/<int:id>', methods=["GET", "POST"])
@login_required
def add_comments_private(id):
    db_sess = db_session.create_session()
    form = CommentForm()
    if form.validate_on_submit():
        com = PrivateComments()
        com.creater = current_user.id
        com.content = form.name.data
        com.private_post = id
        db_sess.add(com)
        db_sess.commit()
        return redirect('/comment/post/' + str(id))
    coms = db_sess.query(PrivateComments).filter(PrivateComments.private_post == id).all()
    return render_template('add_comments.html', form=form, current_user=current_user, com=coms)


@app.route('/join/<int:id>')
@login_required
def join_communite(id):
    db_sess = db_session.create_session()
    com = db_sess.query(Communities).filter(Communities.id == id).first()
    lis = com.collaborators.split('|')
    lis.append(str(current_user.id))
    com.collaborators = '|'.join(lis)
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    lis = user.groups.split(';|;')
    lis.append(com.name)
    user.groups = ';|;'.join(lis)
    db_sess.commit()
    return redirect('/communities/' + str(id))


@app.route('/leave/<int:id>')
@login_required
def leave_com(id):
    db_sess = db_session.create_session()
    com = db_sess.query(Communities).filter(Communities.id == id).first()
    lis = com.collaborators.split('|')
    lis.remove(str(current_user.id))
    com.collaborators = '|'.join(lis)
    db_sess.commit()
    return redirect('/communities/' + str(id))


if __name__ == '__main__':
    main()
