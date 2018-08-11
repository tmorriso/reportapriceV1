from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, ExploreForm
from flask_login import current_user, login_user
from app.models import User, Post
from flask_login import logout_user, login_required
from datetime import datetime


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return redirect(url_for('find', service='index'))
    # page = request.args.get('page', 1, type=int)
    # form = ExploreForm()
    # if form.validate_on_submit():
    #     service = form.service.data
    #     return redirect(url_for('find', service=service))

    # posts = Post.query.order_by(Post.timestamp.desc()).paginate(
    #             page, app.config['POSTS_PER_PAGE'], False)
    # next_url = url_for('index', page=posts.next_num) \
    #     if posts.has_next else None
    # prev_url = url_for('index', page=posts.prev_num) \
    #     if posts.has_prev else None

    # return render_template("index.html", title='Live Feed', posts=posts.items,
    #                       next_url=next_url, prev_url=prev_url, form=form)

@app.route('/find/<service>', methods=['GET', 'POST'])
def find(service):
    page = request.args.get('page', 1, type=int)
    form = ExploreForm()
    if form.validate_on_submit():
        service = form.service.data
        return redirect(url_for('find', service=service))
    if service == 'index':
        posts = Post.query.order_by(Post.timestamp.desc()).paginate(
                page, app.config['POSTS_PER_PAGE'], False)
    else:
        posts = Post.query.filter_by(service_id=service).order_by(Post.timestamp.desc()).paginate(
                page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('find', service=service, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('find', service=service, page=posts.prev_num) \
        if posts.has_prev else None

    return render_template("index.html", title='Explore', posts=posts.items,
                          next_url=next_url, prev_url=prev_url, form=form)

@app.route('/report', methods=['GET', 'POST'])
#@login_required
def report():
    form = PostForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            post = Post(body=form.post.data, author=current_user, 
                service_id=form.service.data, company_id=form.company.data, 
                price=form.price.data, rating=form.rating.data)
        else:
            post = Post(body=form.post.data,
                service_id=form.service.data, company_id=form.company.data, 
                price=form.price.data, rating=form.rating.data)
        db.session.add(post)
        db.session.commit()
        flash('Your report is now live!')
        return redirect(url_for('index'))
    return render_template('report.html', title='Report', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))

