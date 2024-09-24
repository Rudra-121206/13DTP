from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, SubmitField, \
    EmailField, HiddenField
from wtforms.validators import DataRequired, Length, NumberRange, \
    EqualTo, Email


min_passsword_length = 6
max_password_length = 12
min_length = 2
max_length = 60
min_age = 5
max_age = 18


# Student registration form with required fields and validation
class register_student(FlaskForm):
    email = EmailField('Email', [Email(message='Please enter a valid email.')])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.'),
        EqualTo('confirm', message='Passwords must match.'),
        Length(min=min_passsword_length, max=max_password_length,
               message='Password must be between 6 and 10 characters long.')])
    confirm = PasswordField('Confirm Password', validators=[
        EqualTo('password', message='Passwords do not match.')])
    name = StringField('Name', validators=[
        DataRequired(message='Name is required.'),
        Length(min=min_length, max=max_length,
               message='Name must be between 2 and 12 characters long.')])
    year = IntegerField('Age', validators=[
        NumberRange(min=min_age, max=max_age,
                    message='Please enter an age between 5 and 18.'),
        DataRequired(message='Age is required.')])
    submit = SubmitField('Register')


# User login form
class login(FlaskForm):
    email = EmailField('Email', [Email(message='Please enter a valid email.')])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.'),
        Length(min=min_passsword_length, max=max_password_length,
               message='Password must be between 6 and 12 characters long.')])
    submit = SubmitField('Login')


# Form for enrolling into a course using a course ID and a joining code
class EnrollForm(FlaskForm):
    course_id = HiddenField('Course ID')
    joining_code = IntegerField('Enter four-digit joining code', validators=[
        DataRequired(message='Please enter a valid four-digit number.'),
        NumberRange(min=1000, max=9999,
                    message='Please enter a valid four-digit number.')])
    submit_enroll = SubmitField('Join')


# Form for entering a chat message
class enter_chat(FlaskForm):
    chat = StringField('Enter text', validators=[
        DataRequired(), Length(min=min_length, max=max_length)],
        render_kw={"placeholder": "Type a message..."})
    submit = SubmitField('Send')


# Form for course creation
class CreateCourseForm(FlaskForm):
    subject = StringField('Subject', validators=[
        DataRequired(message='Subject is required.'),
        Length(min=min_length, max=max_length,
               message='Subject must be between 2 and 60 characters long.')])
    year_level = IntegerField('Age', validators=[
        NumberRange(min=min_age, max=max_age,
                    message='Please enter an age between 5 and 18.'),
        DataRequired(message='Year level is required.')])
    submit = SubmitField('Create Course')


# Teacher registration - student form but without the 'year' field
class register_teacher(FlaskForm):
    email = EmailField('Email', [Email(message='Please enter a valid email.')])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.'),
        EqualTo('confirm', message='Passwords must match.'),
        Length(min=min_passsword_length, max=max_password_length,
               message='Password must be between 6 and 12 characters long.')])
    confirm = PasswordField('Confirm Password', validators=[
        EqualTo('password', message='Passwords do not match.')])
    name = StringField('Name', validators=[
        DataRequired(message='Name is required.'),
        Length(min=min_length, max=max_length,
               message='Name must be between 2 and 60 characters long.')])
    submit = SubmitField('Register')


# Search form for searching classes
class SearchForm(FlaskForm):
    search = StringField('Enter Text', validators=[
        DataRequired(message='Search term is required.'),
        Length(min=min_length, max=max_length,
               message='Search term must be between 2 and 60 characters long.')
    ], render_kw={"placeholder": "🔎 Search for a class..."})
    submit_search = SubmitField('Submit')
