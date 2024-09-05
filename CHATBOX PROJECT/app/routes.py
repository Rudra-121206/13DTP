from app import app
from flask import render_template, abort, redirect, request, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy # no more boring old SQL for us!
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, LoginManager, UserMixin, logout_user, login_required
from datetime import datetime
import random


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
    if not current_user.is_authenticated:
        flash('User is not authenticated')
        return redirect(url_for('login'))
    elif current_user.has_role('teacher'):
        flash('User access invalid')
        return redirect(url_for('create_course'))
    else:
        form = forms.joining_code()  # Form for joining courses
        search_form = forms.search()  # Search form

        search_query = request.args.get('search')  # Get the search query from GET request
        print(search_query)

        # Filter courses based on search query
        if search_query:
            all_courses = models.Course.query.filter(models.Course.subject.like(f'%{search_query}%')).all()
        else:
            all_courses = models.Course.query.all()  # Get all courses if no search query

        # Handle POST request (course enrollment)
        if request.method == 'POST':
            if 'submit_enroll' in request.form and form.validate_on_submit():
                course = models.Course.query.filter_by(id=form.course.data).first()

                if course and form.joining_code.data == course.joining_code:
                    user = models.User.query.get(ref)
                    course = models.Course.query.get(form.course.data)

                    if user and course:
                        if course in user.courses:
                            flash('You are already enrolled in this course')
                        else:
                            user.courses.append(course)
                            db.session.add(user)
                            db.session.commit()
                            flash(f"User {user.name} has been enrolled in the course")
                        return redirect(url_for('my_courses', ref=ref))
                else:
                    flash("Invalid course ID or joining code, please try again.")
            elif 'submit_search' in request.form and search_form.validate_on_submit():
            
                search_query = search_form.search.data
                all_courses = models.Course.query.filter(models.Course.subject.like(f'%{search_query}%')).all()
                print(all_courses)
                if all_courses is None:
                    flash("So sorry we can't find what you're looking for")
        # Render the page with the list of filtered courses
        return render_template('all_courses.html', form=form, search_form=search_form, all_courses=all_courses)
    

@app.route("/create_acc_student", methods=['GET', 'POST'])
def create_acc():
    form = forms.register_student()
    if current_user.is_authenticated is True:
        flash('user is logged in')
        return redirect(url_for('my_courses', ref=current_user.id))
    elif request.method == 'GET':
        return render_template('create_acc_student.html', form=form, title='Create an account(student)')
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

@app.route("/create_acc_teacher", methods=['GET', 'POST'])
def create_acc_teacher():
    form = forms.register_teacher()
    if current_user.is_authenticated is True:
        flash('user is logged in')
        return redirect(url_for('my_courses', ref=current_user.id))
    elif request.method == 'GET':
        return render_template('create_acc_teacher.html', form=form, title='Create an account(student)')
    else:
        form.validate_on_submit()
        new_user = models.User()
        new_user.role = "teacher"
        new_user.name = form.name.data
        new_user.email = form.email.data
        new_user.password = generate_password_hash(form.password.data)
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
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        
        chats = models.Chat.query.filter_by(course_id=course_id).all()
        name = []
        for chat in chats:
            print(chat.person_id)
            user = models.User.query.filter_by(id=chat.person_id).all()
            for name_user in user:
                name.append(name_user.name)
                print(name)
        form = forms.enter_chat()
        if request.method == "GET":
            return render_template('chats.html', form=form, chats=chats, name=name, course_id=course_id)
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
         

@app.route('/create_course', methods=['GET', 'POST'])
@login_required
def create_course():
    if not current_user.is_authenticated:
        flash('User is not authenticated')
        return redirect(url_for('login'))
    elif current_user.has_role('teacher'):   
        form = forms.CreateCourseForm()
        if request.method == 'GET':
            return render_template('create_course.html', form=form)
        else:
            form.validate_on_submit()
            new_course = models.Course(
                joining_code=random.randint(1111, 9999),
                subject=form.subject.data,
                year_level=form.year_level.data
            )
            db.session.add(new_course)
            db.session.commit()
            user = models.User.query.get(current_user.id)
            last_course = models.Course.query.order_by(models.Course.id.desc()).first()
            course = models.Course.query.get(last_course.id)

            if user and course:
            #check if user is already enrolled into the course
                if course in user.courses:
                    print("can't add more")
                    flash('you are already enrolled into this course')
                    return redirect(url_for('my_courses', ref=current_user.id))
                else:
                    print("can add more")
                    # Add the course to the user's courses list
                    user.courses.append(course)
                    # Commit the changes to the database
                    db.session.add(user)
                    db.session.commit()
                    flash('Course created successfully!', 'success')
                    return redirect(url_for('my_courses', ref=current_user.id))  # Redirect to a relevant page
    else:
        flash('Student access unauthorized')
        return redirect(url_for('my_courses', ref=current_user.id))
    
@app.route('/check_new_messages/<int:course_id>/<int:last_chat_id>', methods=['GET'])
def check_new_messages(course_id, last_chat_id):
    # Query to find if there's any chat with an ID greater than the last known chat ID
    new_chats = models.Chat.query.filter(models.Chat.course_id == course_id, models.Chat.chat_id > last_chat_id).count()
    
    return jsonify({"new_messages": new_chats > 0})


@app.route('/delete_course/<int:ref>/<int:course_id>')
def delete_course(ref, course_id):
    if not current_user.is_authenticated:
        flash('User is not authenticated')
        return redirect(url_for('login'))
    elif current_user.has_role('teacher'):
        print("one")
        # Query to find the course by id
        course_to_delete = models.Course.query.get(course_id)
        user = models.User.query.get(current_user.id)
        if user and course_to_delete:
            if course_to_delete in user.courses:
                if course_to_delete:
                    try:
                        db.session.delete(course_to_delete)
                        db.session.commit()
                        flash("Course has been deleted")
                        return redirect(url_for('my_courses', ref=ref))
                    except Exception as e:
                        print('fail')
                        db.session.rollback()
                        flash(f"Error deleting course:{e}", "danger")
                        return redirect(url_for('my_courses', ref=ref))
                else:
                    flash(f"No course found with ID {course_id}.", "warning")
                    return redirect(url_for('my_courses', ref=ref))
            else:
                flash("autharization invalid, this course is not yours")
                return redirect(url_for('my_courses', ref=ref))
        else:
            flash("such user or course does not exist")
            return redirect(url_for('my_courses', ref=ref))
    else:
        flash('Student access unauthorized')
        return render_template('my_courses', ref=ref)
    

 
