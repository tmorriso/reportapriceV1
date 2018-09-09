from flask import render_template, flash, redirect, url_for, request, g
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, ExploreForm, CompanyForm, PostForm2
from flask_login import current_user, login_user
from app.models import User, Post, Listing, Service, Company
from flask_login import logout_user, login_required
from datetime import datetime

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = ExploreForm()
    if form.validate_on_submit():
        form_service = form.service.data
        return redirect(url_for('find', service=form_service.id))

    return render_template("index_temp.html", title='Home', form=form)

@app.route('/search', methods=['GET', 'POST'])
def search():
    page = request.args.get('page', 1, type=int)
    form = ExploreForm()
    if form.validate_on_submit():
        service = form.service.data
        return redirect(url_for('find', service=service.id))
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
                page, app.config['POSTS_PER_PAGE'], False)
        
    next_url = url_for('find', service=service.id, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('find', service=service.id, page=posts.prev_num) \
        if posts.has_prev else None

    return render_template("index.html", title='Explore', posts=posts.items,
                          next_url=next_url, prev_url=prev_url, form=form)
    
@app.route('/find/<service>', methods=['GET', 'POST'])
def find(service):
    page = request.args.get('page', 1, type=int)
    form = ExploreForm()
    if form.validate_on_submit():
        form_service = form.service.data
        return redirect(url_for('find', service=form_service.id))
    else:
        listings = Listing.query.filter(Listing.service_id==service)
        for listing in listings:
            posts = Post.query.filter(Post.service_id==listing.service_id, Post.company_id==listing.company_id)
            listing.calculate_averages(posts)
        listings = listings.order_by(Listing.average_price).paginate(page, app.config['POSTS_PER_PAGE'], False)
        all_posts = Post.query.filter(Post.service_id == listing.service_id)
        average_price = find_average(all_posts)
        service_name = listing.service.title

    next_url = url_for('find', service=service, page=listings.next_num) \
        if listings.has_next else None
    prev_url = url_for('find', service=service, page=listings.prev_num) \
        if listings.has_prev else None

    return render_template("find.html", title='Explore', listings=listings.items, average_price=average_price, service_name=service_name,
                          next_url=next_url, prev_url=prev_url, form=form)

# @app.route('/report', methods=['GET', 'POST'])
# #@login_required
# def report():
#     form = PostForm()
#     if form.validate_on_submit():
#         service = form.service.data
#         company = form.company.data
#         service.add_company(company)
#         listing = Listing.query.filter(Listing.company_id == company.id, Listing.service_id == service.id).all()
#         if len(listing) == 0:
#             # If Listing doesn't exist create it
#             listing = Listing(service_id=service.id, company_id=company.id)
#             db.session.add(listing)
#             db.session.commit()
#         else:
#             listing = listing[0]
#         if current_user.is_authenticated:
#             post = Post(body=form.post.data, author=current_user, 
#                 service_id=service.id, company_id=company.id, 
#                 price=form.price.data, rating=form.rating.data, listing=listing)
#         else:
#             post = Post(body=form.post.data,
#                 service_id=service.id, company_id=company.id, 
#                 price=form.price.data, rating=form.rating.data, listing=listing)
#         db.session.add(post)
#         db.session.commit()

#         flash('Your report is now live!')
#         return redirect(url_for('search'))
#     return render_template('report.html', title='Report', form=form)

@app.route('/report', methods=['GET', 'POST'])
#@login_required
def report():
    if 'service_id' in locals():
        print(service_id, city)
    form = ExploreForm()
    if form.validate_on_submit():
        service = form.service.data
        city = form.city.data
        return redirect(url_for('report_2', service_id = service.id, city = city))
    return render_template('report.html', title='Report', form1=form)

@app.route('/report_2/<city>/<service_id>', methods=['GET', 'POST'])
#@login_required
def report_2(city, service_id):
    g.service_id=service_id
    g.city=city
    form = PostForm2()
    if form.validate_on_submit():
        service = Service.query.filter(Service.id == service_id).first()
        company = form.company.data
        listing = Listing.query.filter(Listing.company_id == company.id, Listing.service_id == service.id).all()
        if len(listing) == 0:
            # If Listing doesn't exist create it
            listing = Listing(service_id=service.id, company_id=company.id)
            db.session.add(listing)
            db.session.commit()
        else:
            listing = listing[0]
        if current_user.is_authenticated:
            post = Post(body=form.post.data, author=current_user, 
                service_id=service.id, company_id=company.id, 
                price=form.price.data, rating=form.rating.data, listing=listing)
        else:
            post = Post(body=form.post.data,
                service_id=service.id, company_id=company.id, 
                price=form.price.data, rating=form.rating.data, listing=listing)
        db.session.add(post)
        db.session.commit()

        flash('Your report is now live!')
        return redirect(url_for('search'))
    return render_template('report.html', title='Report', form3=form)

@app.route('/add_company', methods=['GET', 'POST'])
#@login_required
def add_company():
    form = CompanyForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            company = Company(company_name=form.company_name.data, company_address=form.company_address.data,
                company_city=form.company_city.data, company_state=form.company_state.data, 
                company_zipcode=form.company_zipcode.data, company_website=form.company_website.data, 
                company_phone_number=form.company_phone_number.data, company_email = form.company_email.data, 
                author=current_user)  
        else:
            company = Company(company_name=form.company_name.data, company_address=form.company_address.data,
                company_city=form.company_city.data, company_state=form.company_state.data, 
                company_zipcode=form.company_zipcode.data, company_website=form.company_website.data, 
                company_phone_number=form.company_phone_number.data,
                company_email = form.company_email.data)
        db.session.add(company)
        db.session.commit()

        flash('Thank you, the company has been added!')
        return redirect(url_for('index'))
    return render_template('report.html', title='Report', form2=form)


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


# Auxillary Functions
def find_average(posts):
        if posts.count() != 0:
            total = 0
            for post in posts:
                total += post.price
            average = round(total/posts.count(),2)
        else:
            average = "NA"    
        return average

