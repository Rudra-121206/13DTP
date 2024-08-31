from app import app
from flask import render_template, abort, redirect, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy # no more boring old SQL for us!
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, LoginManager, UserMixin, logout_user, login_required
from datetime import datetime



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
    all_courses = models.Course.query.all()
    form = forms.joining_code()
    if request.method == 'GET':
        print('half')
        return render_template('all_courses.html', form=form, all_courses=all_courses)

    elif request.method == 'POST':
        print("data") 
         
        print(form.joining_code.data) 
        print(form.course.data)
        course = models.Course.query.filter_by(id=form.course.data).first()
        if course is not None:

            if form.joining_code.data == course.joining_code:

                print('success')
                user = models.User.query.get(ref)
                course = models.Course.query.get(form.course.data)

                if user and course:
                        #check if user is already enrolled into the course
                    if course in user.courses:
                        print("can't add more")

                        flash('you are already enrolled into this course')
                        return redirect(url_for('my_courses', ref=ref))
                    else:
                        print("can add more")
                        # Add the course to the user's courses list
                        user.courses.append(course)
                        # Commit the changes to the database
                        db.session.add(user)
                        db.session.commit()
                        print(f"User {user.name} has been enrolled in the course ")

                        return redirect(url_for('my_courses', ref=ref))
                else:
                    flash("error in the system")
                    return render_template('all_courses.html', form=form, all_courses=all_courses)
            else:
                flash("invalid credentials, please try again")
                return render_template('all_courses.html', form=form, all_courses=all_courses)
        else:
            flash("invalid credentials, please try again")
            return render_template('all_courses.html', form=form, all_courses=all_courses)    
    else:
        flash("invalid credentials, please try again")
        return render_template('all_courses.html', form=form, all_courses=all_courses)

@app.route("/create_acc", methods=['GET', 'POST'])
def create_acc():
    form = forms.register()
    if current_user.is_authenticated is True:
        flash('user is logged in')
        return redirect(url_for('all_courses', ref=current_user.id))
    elif request.method == 'GET':
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
        flash('login with your details')
        return redirect(url_for('my_courses', ref=new_user.id))


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
        #form.validate_on_submit()
        print('1')
        email = form.email.data
        password = form.password.data
        print(email, password)
        user = models.User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)

            flash('Logged in successfully.')
            if user.role == "student":
                print(user.role)
                return redirect(url_for('my_courses', ref=current_user.id))
            else:
                return redirect(url_for('my_courses', ref=current_user.id))
        else:
            flash('Invalid credentials. Please try again.')

    return render_template('login.html', form=form)

 




@app.route("/my_courses/<int:ref>")
def my_courses(ref):
    
    if current_user.is_authenticated is True:
        courses = models.User.query.filter_by(id=ref).first_or_404()
        if courses is None:
            return redirect(url_for('all_courses', ref=current_user.id))
        else:
            course_user = courses.courses
    else:
        flash('Login required')
        return redirect(url_for('login'))
    return render_template('my_classes.html', course_user=course_user)
     


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.route("/chats/<int:ref>/<int:course_id>", methods=['GET', 'POST'])
def chats(ref, course_id):
    chats = models.Chat.query.filter_by(course_id=course_id).all()
    for chat in chats: 
        name = []
        print(chat)
        name_user = models.User.query.filter_by(id=chat.person_id).all()
        print(name_user)
        name_user.name(name)

    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        form = forms.enter_chat()
        if request.method == "GET":
            return render_template('chats.html', form=form, chats=chats, name=name)
        elif request.method == "POST":
            form.validate_on_submit()
            new_chat = models.Chat()
            new_chat.course_id = course_id
            new_chat.person_id = ref
            new_chat.chat_content = form.chat.data
            new_chat.chat_status = 0
            new_chat.timestamp = datetime.now()
            db.session.add(new_chat)
            db.session.commit()
            return redirect(url_for("chats", ref=ref, course_id=course_id))
        else:
            pass
         







 