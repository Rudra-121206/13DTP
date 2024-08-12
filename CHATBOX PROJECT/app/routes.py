from app import app
from flask import render_template, abort, redirect, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy # no more boring old SQL for us!
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, LoginManager, UserMixin



basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, "chatbox.db")
db.init_app(app)
app.secret_key = 'correcthorsebatterystaple'
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'sup3r_secr3t_passw3rd'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'create_acc'


@login_manager.user_loader
def load_user(User_id):
    return models.User.query.get(int(User_id))


import app.models as models
from app import forms

@app.route('/all_courses/<int:ref>', methods=['GET', 'POST'])
def all_courses(ref):
    if current_user.is_authenticated is True:
        all_courses = models.Course.query.all()

        form = forms.joining_code()
        if request.method == 'GET':
            return render_template('all_courses.html', form=form, all_courses=all_courses)
        elif request.method == 'POST':
            form.validate_on_sumbit()
            
            if form.joining_code.data == models.Course.joining_code.filter_by(id=form.id.data):
                new_enrolment = models.enrolment()
                new_enrolment.person_id = ref
                new_enrolment.course_id = form.id.data
                return redirect(url_for('my_classes', ref=ref))
            else:
                return render_template('all_courses.html', form=form, all_courses=all_courses)
        else:
            404()
    else:
        return redirect(url_for('login'))

@app.route("/create_acc", methods=['GET', 'POST'])
def create_acc():
    form = forms.register()
    if request.method == 'GET':
        return render_template('create_acc.html', form=form, title='Create an account(student)')
    else:
        form.validate_on_submit()
        new_user = models.User()
        new_user.role = "student"
        new_user.name = form.name.data
        new_user.email = form.email.data
        new_user.password = generate_password_hash(form.password.data)
        new_user.year_level = form.year.data
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('my_classes', ref=new_user.id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.login()

    if current_user.is_authenticated is True:
        flash('user is logged in')
        return redirect(url_for('all_courses', ref=current_user.id))
    elif request.method == 'GET':
        print('half')
        return render_template('login.html', form=form)
    elif request.method == 'POST':
        form.validate_on_submit()
        print('1')
        email = form.email.data
        password = form.password.data
        print(email, password)
        user = models.User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('my_classes', ref=current_user.id))
        else:
            flash('Invalid credentials. Please try again.')

    return render_template('login.html', form=form)


@app.route("/my_classes/<int:ref>")
def my_classes(ref):
    
    if current_user.is_authenticated is True:
        courses = models.User.query.filter_by(id=ref).first_or_404()
        course_user = courses.courses
    else:
        flash('Invalid credentials. Please try again.')
        return redirect(url_for('login'))
    return render_template('my_classes.html', course_user=course_user)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404





 