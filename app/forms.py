from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SubmitField, SelectField, DecimalField, IntegerField, TextField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from wtforms_alchemy.fields import QuerySelectField
from app.models import User, Service, Company
from app import db

# Auxillary functions
def service_query():
    return Service.query

def company_query():
        # city = g.city
        # service = g.service
        return Company.query


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

    
class ExploreForm(FlaskForm):
    service = QuerySelectField(query_factory=service_query, allow_blank=True, blank_text='Enter a Service', get_label='title', validators=[
        DataRequired()])
    #city = QuerySelectField(query_factory=city_query, allow_blank=True, blank_text='Enter a City', get_label='company_city', validators=[
    #   DataRequired()])
    city = SelectField(choices = [('','Enter a city'), ('Boise','Boise, ID')], validators=[DataRequired()])
    
    submit = SubmitField('Submit')

