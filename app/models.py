from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db
from flask_login import UserMixin
from app import login
from hashlib import md5
from uszipcode import ZipcodeSearchEngine
from sqlalchemy import and_

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def filter_posts(self, service, location, company, rating):
        search = ZipcodeSearchEngine()
        if service != "None" and location != "None" and company == 'None' and rating == 'None':
            res = search.by_city(location)
            city_zips = []
            for i in range (0,len(res)):
                city_zips.append(res[i].Zipcode)
        
        return Post.query.join(Company).filter(Company.company_zipcode.in_(city_zips), Post.service_id == service)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float)
    rating = db.Column(db.Integer)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id')) 


    def __repr__(self):
        return '<Post {}>'.format(self.body)

class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    average_price = db.Column(db.Float)
    average_rating = db.Column(db.Float)
    posts = db.relationship('Post', backref='listing', lazy='dynamic')

    def __repr__(self):
        return '<Listing {}>'.format(self.id)

    def calculate_averages(self, posts):
        total_rating = 0
        total_price = 0
        count = 0 
        for post in posts:
            if post.service == self.service and post.company == self.company:
                total_price += post.price
                total_rating += post.rating
                count += 1
        self.average_price = round(total_price/count, 2)
        self.average_rating = round(total_rating/count, 1)

companies_services = db.Table('companies_services',
    db.Column('service_id', db.Integer, db.ForeignKey('service.id')),
    db.Column('company_id', db.Integer, db.ForeignKey('company.id'))
)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer)
    title = db.Column(db.String(120))
    posts = db.relationship('Post', backref='service', lazy='dynamic')
    listings = db.relationship('Listing', backref='service', lazy='dynamic')
    companies = db.relationship(
        'Company', secondary=companies_services,
        backref=db.backref('services', lazy='dynamic'), lazy='dynamic')
    service_attributes = db.relationship('Service_Attributes', backref='service', lazy='dynamic')

    def add_company(service, company):
        if not service.is_offered(company):
            service.companies.append(company)

    def remove_company(service, company):
        if service.is_offered(company):
            service.companies.remove(company)

    def is_offered(service, company):
        return service.companies.filter(
            companies_services.c.company_id == company.id).count() > 0

    def icon(service):
        icon_path = '../static/' + service.title + '.png'
        return icon_path

    def service_posts(service):
        return Post.query.filter_by(service_id=service.id)

    def __repr__(self):
        return '<Service {}>'.format(self.title)

class Service_Attributes(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    attribute = db.Column(db.String(120))
    value = db.Column(db.String(120))
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))

   
    def __repr__(self):
        return '<Service_Attributes {}>'.format(self.value)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(120))
    company_address = db.Column(db.String(120))
    company_city = db.Column(db.String(120))
    company_state = db.Column(db.String(120))
    company_zipcode = db.Column(db.String(120))
    company_website = db.Column(db.String(120))
    company_phone_number = db.Column(db.String(120))
    company_email = db.Column(db.String(120))
    posts = db.relationship('Post', backref='company', lazy='dynamic')
    listings = db.relationship('Listing', backref='company', lazy='dynamic')

    def __repr__(self):
        return '<Company {}>'.format(self.company_name)



@login.user_loader
def load_user(id):
    return User.query.get(int(id))

