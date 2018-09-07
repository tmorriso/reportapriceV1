from flask_wtf import FlaskForm
from wtforms import Form, validators, StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SubmitField, SelectField, DecimalField, IntegerField, TextField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from wtforms_alchemy.fields import QuerySelectField
from app.models import User, Service, Company
from app import db
import phonenumbers
from flask import g

# Auxillary functions
def service_query():
    return Service.query

def company_query():   
        return Company.query

def company_query2():
        city = g.city
        service_id = g.service_id
        #return Company.query.filter(Company.company_city==city)
        return Company.query.filter(Company.company_city == city, Company.services.any(id=service_id))

city_choices = [('','Enter a city'), ('Boise','Boise, ID')]
city_choices_2 = ['Boise','Grand Junction','Portland']
state_choices = [('CO','Colorado'), ('ID','Idaho'), ('OR', 'Oregon')]

#This doesn't work, asked question on stack overflow
def city_query():
    return Company.query.group_by(Company.company_city)


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class PostForm(FlaskForm):
    service = QuerySelectField(query_factory=service_query, allow_blank=True, blank_text='Select a Service', get_label='title', validators=[
        DataRequired()])
    company = QuerySelectField(query_factory=company_query, allow_blank=True, blank_text='Select a Company', get_label='company_display')
    price = DecimalField('What price did you pay?', validators=[
        DataRequired()])
    rating = SelectField('Leave a rating ', choices = [('1', '1 Star'), ('2', '2 Stars'), ('3', '3 Stars'), ('4', ' 4 Stars'), ('5', '5 Stars')], validators=[
        DataRequired()])
    post = TextAreaField('Leave a Review', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')

class PostForm2(FlaskForm):
    company = QuerySelectField('What company provided the service?', query_factory=company_query2, allow_blank=True, blank_text='Enter Company Name', get_label='company_display', validators=[
        DataRequired()])
    price = DecimalField('What price did you pay?', validators=[
        DataRequired()])
    rating = SelectField('Leave a rating ', choices = [('1', '1 Star'), ('2', '2 Stars'), ('3', '3 Stars'), ('4', ' 4 Stars'), ('5', '5 Stars')], validators=[
        DataRequired()])
    post = TextAreaField('Leave a Review', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')
    
class ExploreForm(FlaskForm):
    service = QuerySelectField('What service would you like to report?', query_factory=service_query, allow_blank=True, blank_text='Enter a Service', get_label='title', validators=[
        DataRequired()])
    city = SelectField('What city are you located in?',choices = city_choices, validators=[DataRequired()])
    
    submit = SubmitField('Submit')

class CompanyForm(FlaskForm):
    company_name=StringField('Company Name', validators=[DataRequired()])
    company_address=StringField('Street Address', validators=[DataRequired()])
    company_city=StringField('City', validators=[DataRequired()])
    company_state=SelectField('State', choices = state_choices, validators=[DataRequired()])
    company_zipcode=StringField('Zip Code', validators=[DataRequired()]) 
    company_website=StringField('Website URL', validators=[DataRequired()]) 
    company_phone_number=StringField('Phone Number', validators=[DataRequired()])
    company_email=StringField('Email (Optional)')
    submit = SubmitField('Submit')

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        company = Company.query.filter_by(company_name=self.company_name.data, company_address=self.company_address.data).first()
        if company is not None:
            self.company_name.errors.append('Company already exists at that address')
            return False

        return True

    def validate_company_city(self, company_city):
        if company_city.data not in city_choices_2:
            raise ValidationError('We are not available in this city yet.')

    def validate_company_phone_number(self, field):
        if len(field.data) > 16 or len(field.data) < 4:
            raise ValidationError('Invalid phone number.')
        try:
            try:
                input_number = phonenumbers.parse(field.data)
                if not (phonenumbers.is_valid_number(input_number)):
                    raise ValidationError('Invalid phone number.')
            except:
                input_number = phonenumbers.parse("+1"+field.data)
                if not (phonenumbers.is_valid_number(input_number)):
                    raise ValidationError('Invalid phone number.')
        except:
            raise ValidationError('Invalid phone number.')


