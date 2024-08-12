from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField, SelectField, EmailField, PasswordField, SubmitField, validators
from wtforms.validators import DataRequired, Length, NumberRange, EqualTo
import app.models
from datetime import datetime




class register(FlaskForm):

    email = EmailField('Email', [validators.Email(message='please enter a valid email')])
    password = PasswordField('Password', validators=[
    DataRequired(message='Password is required.'),
    EqualTo('confirm', message='Passwords must match.'),
    Length(message='Password must be between 6 and ten characters long.', min=6, max=10),
    ])
    confirm = PasswordField('Confirm password', validators=[EqualTo(fieldname=password, message='password does not match')])
    name = StringField('name', validators=[DataRequired(message='Name is required'), 
    Length(message='name must be between 6 and 12 characters long', min=6, max=12)])
    year = IntegerField('Age', validators=[NumberRange(min=5, max=18, message='please enter a digit between 5 and 18'),
    DataRequired(message='name is required')])
    submit = SubmitField('Register')



class login(FlaskForm):
    email = EmailField('Email', [validators.Email(message='please enter a valid email')])
    password = PasswordField('Password', [
    validators.DataRequired(message='Password is required.'),
    validators.Length(message='Password must be between 6 and ten characters long.', min=6, max=10)])
    submit = SubmitField('login')
    

class joining_code(FlaskForm):
    joining_code=IntegerField('Enter four digit joining code', [
    validators.DataRequired(message='data is required'),
    validators.NumberRange(min=1000, max=9999, message='please enter four digit number')])
    submit =SubmitField('join')