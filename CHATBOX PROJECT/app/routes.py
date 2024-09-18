from app import app
from flask import render_template, abort, redirect, request, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy  # Using SQLAlchemy for ORM functionality
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, LoginManager, UserMixin, logout_user, login_required
from datetime import datetime
import random

# Define base directory and configure SQLAlchemy database
basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, "chatbox.db")
db.init_app(app)
app.secret_key = 'correcthorsebatterystaple'

# Enable CSRF protection
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'sup3r_secr3t_passw3rd'

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'create_acc'

# Load the current user from session
@login_manager.user_loader
def load_user(User_id):
    return models.User.query.get(int(User_id))

# Import models and forms from the app module
import app.models as models
from app import forms


# Home route
@app.route('/')
def home():
    return render_template('home.html')


# Route for displaying all courses for a specific user
@app.route('/all_courses/<int:ref>', methods=['GET', 'POST'])
def all_courses(ref):
    # Check if the user is authenticated
    if not current_user.is_authenticated:
        flash('User is not authenticated')
        return redirect(url_for('login'))

    # check if the user url is correct
    elif current_user.id != ref:
        flash('Unauthorised access', 'error')
        return redirect(url_for('home'))

    # Check if the user is a teacher
    elif current_user.has_role('teacher'):
        flash('User access invalid')
        return redirect(url_for('create_course'))

    else:
        form = forms.joining_code()  # Form for joining courses
        search_form = forms.search()  # Search form
        search_query = request.args.get('search')  # Get search query from the request

        # Filter courses based on search query
        if search_query:
            all_courses = models.Course.query.filter(models.Course.subject.like(f'%{search_query}%')).all()
        else:
            all_courses = models.Course.query.all()  # Fetch all courses if no search query

        # Handle POST request for course enrollment
        if request.method == 'POST':
            if 'submit_enroll' in request.form and form.validate_on_submit():
                course = models.Course.query.filter_by(id=form.course.data).first()

                # Check if the course and joining code are valid
                if course and form.joining_code.data == course.joining_code:
                    user = models.User.query.get(ref)
                    course = models.Course.query.get(form.course.data)

                    # Check if the user and course exist
                    if user and course:
                        if course in user.courses:
                            flash('You are already enrolled in this course', 'warning')
                        else:
                            user.courses.append(course)
                            db.session.add(user)
                            db.session.commit()
                            flash(f"User {user.name} has been enrolled in the course", 'success')
                        return redirect(url_for('my_courses', ref=ref))

                else:
                    flash("Invalid course ID or joining code, please try again.", 'error')

            # Handle search form submission
            elif 'submit_search' in request.form and search_form.validate_on_submit():
                search_query = search_form.search.data
                all_courses = models.Course.query.filter(models.Course.subject.like(f'%{search_query}%')).all()
                if all_courses is None:
                    flash("So sorry we can't find what you're looking for", 'error')

        # Render the page with the list of filtered courses
        return render_template('all_courses.html', form=form, search_form=search_form, all_courses=all_courses)


# Route to create a student account
@app.route("/create_acc_student", methods=['GET', 'POST'])
def create_acc():
    form = forms.register_student()

    # If the user is already authenticated, redirect them to their courses
    if current_user.is_authenticated:
        flash('User is logged in')
        return redirect(url_for('my_courses', ref=current_user.id))

    elif request.method == 'GET':
        return render_template('create_acc_student.html', form=form, title='Create an account (student)')

    else:
        if form.validate_on_submit():
            # Check if the email is already in use
            existing_user = models.User.query.filter_by(email=form.email.data).first()
            if existing_user:
                flash('Email already in use. Please choose a different one.', 'error')
                return redirect(url_for('create_acc'))

            # Create a new user
            else:
                new_user = models.User()
                new_user.role = "student"
                new_user.name = form.name.data
                new_user.email = form.email.data
                new_user.password = generate_password_hash(form.password.data)
                new_user.year_level = form.year.data
                db.session.add(new_user)
                db.session.commit()
                flash('Account created successfully! Please log in with your details.', 'success')
                return redirect(url_for('my_courses', ref=new_user.id))

        else:
            flash("Incorrect information in form", "error")
            return render_template('create_acc_student.html', form=form, title='Create an account (student)')


# Route to create a teacher account
@app.route("/create_acc_teacher", methods=['GET', 'POST'])
def create_acc_teacher():
    form = forms.register_teacher()

    if current_user.is_authenticated:
        flash('User is already logged in')
        return redirect(url_for('my_courses', ref=current_user.id))

    if request.method == 'POST':
        if form.validate_on_submit():  # This will check if the form submission is valid
            new_user = models.User()
            new_user.role = "teacher"
            new_user.name = form.name.data
            new_user.email = form.email.data
            new_user.password = generate_password_hash(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! Please login with your new details.', 'success')
            return redirect(url_for('login'))  # Redirect to login page for new user to login
        else:
            flash('Errors have occurred in form submission.', 'error')

    return render_template('create_acc_teacher.html', form=form, title='Create an account (teacher)')
# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.login()

    # If the user is already logged in, redirect to courses
    if current_user.is_authenticated:
        flash('User is already logged in')
        return redirect(url_for('all_courses', ref=current_user.id))

    if form.validate_on_submit():  # Validate the form when it's submitted
        email = form.email.data
        password = form.password.data
        user = models.User.query.filter_by(email=email).first()

        # Check if the user exists and the password matches
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('my_courses', ref=current_user.id))
        else:
            flash('Invalid credentials. Please try again.', 'error')

    # GET request or if validation fails, re-render the form
    return render_template('login.html', form=form)

# Route to display courses for the logged-in user
@app.route("/my_courses/<int:ref>")
def my_courses(ref):
    if current_user.id != ref:
        flash('Unauthorised access', 'error')
        return redirect(url_for('home'))

    elif current_user.is_authenticated:

        courses = models.User.query.filter_by(id=ref).first_or_404()
        if courses is None:
            return redirect(url_for('all_courses', ref=current_user.id))
        else:
            course_user = courses.courses
    else:
        flash('Login required', 'warning')
        return redirect(url_for('login'))
    return render_template('my_classes.html', course_user=course_user)


# Route for logging out the user
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


# Error handler for 404 errors
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


# Route for handling chat functionality
@app.route("/chats/<int:ref>/<int:course_id>", methods=['GET', 'POST'])
def chats(ref, course_id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
 
    # Ensure that the user is enrolled in the course
    course = models.Course.query.get(course_id)
    if not course or current_user not in course.people:
        flash('unauthorised access to class', 'error')
        return redirect(url_for('home'))

    # Redirect to homepage if not authorized

    chats = models.Chat.query.filter_by(course_id=course_id).all()
  
    # Fetch the names of users participating in the chat
    name = []
    for chat in chats:
        user = models.User.query.filter_by(id=chat.user_id).first()
        name.append(user.name) if user else name.append('Unknown User')

    form = forms.enter_chat()
 
    if form.validate_on_submit():  # Check if the form was submitted and valid
        new_chat = models.Chat(
            course_id=course_id,
            user_id=ref,
            chat_content=form.chat.data,
            chat_status="unread",
            timestamp=datetime.now()
        )
        db.session.add(new_chat)
        db.session.commit()

        return redirect(url_for("chats", ref=ref, course_id=course_id))

    return render_template('chats.html', form=form, chats=chats, name=name, course_id=course_id)


# Route to create a new course (teachers only)
@app.route('/create_course', methods=['GET', 'POST'])
def create_course():
    # Check if the user is authenticated
    if not current_user.is_authenticated:
        flash('User is not authenticated')
        return redirect(url_for('login'))

    # Check if the user has a teacher role
    elif current_user.has_role('teacher'):
        form = forms.CreateCourseForm()

        # Handle form submission
        if form.validate_on_submit():
            # Create a new course using data from the form
            new_course = models.Course(
                joining_code=random.randint(1111, 9999),  # Generate a random joining code
                subject=form.subject.data,
                year_level=form.year_level.data
            )

            # Add the new course to the database
            db.session.add(new_course)
            db.session.commit()

            # Retrieve the user and enroll in the latest created course
            user = models.User.query.get(current_user.id)
            last_course = models.Course.query.order_by(models.Course.id.desc()).first()

            # Ensure both the user and the course exist
            if user and last_course:
                if last_course in user.courses:
                    flash('You are already enrolled in this course', 'warning')
                else:
                    # Add the course to the user's courses list
                    user.courses.append(last_course)
                    db.session.add(user)
                    db.session.commit()
                    flash('Course created successfully!', 'success')
                return redirect(url_for('my_courses', ref=current_user.id))
        else:
            # If form validation fails, render the form with errors
            flash('Form validation failed. Please correct the errors.', 'error')
            return render_template('create_course.html', form=form)

    # If the user is a student, deny access to course creation
    else:
        flash('Student access unauthorized', 'error')
        return redirect(url_for('my_courses', ref=current_user.id))

# Route to check if there are new messages in a course chat
@app.route('/check_new_messages/<int:course_id>/<int:last_chat_id>', methods=['GET'])
def check_new_messages(course_id, last_chat_id):
    # Query to find if there are any new chat messages after the last known chat ID
    new_chats = models.Chat.query.filter(
        models.Chat.course_id == course_id,
        models.Chat.chat_id > last_chat_id
    ).count()
    
    # Return a JSON response indicating whether there are new messages
    return jsonify({"new_messages": new_chats > 0})


# Route to delete a course (teachers only)
@app.route('/delete_course/<int:ref>/<int:course_id>')
def delete_course(ref, course_id):
    # Check if the user is authenticated
    if not current_user.is_authenticated:
        flash('User is not authenticated', 'error')
        return redirect(url_for('login'))

    # Check if the URL is coherent with the current user's ID
    elif current_user.id != ref:
        flash('Unauthorized access', 'error')
        return redirect(url_for('home'))

    # Check if the user has a teacher role
    elif current_user.has_role('teacher'):
        # Retrieve the course to be deleted and the current user
        course_to_delete = models.Course.query.get(course_id)
        user = models.User.query.get(current_user.id)

        # Ensure both the user and the course exist
        if user and course_to_delete:
            # Check if the course belongs to the user (teacher)
            if course_to_delete in user.courses:
                # Additional check to ensure the teacher is enrolled in the course
                if course_to_delete in current_user.courses:
                    if course_to_delete:
                        try:
                            # Attempt to delete the course from the database
                            db.session.delete(course_to_delete)
                            db.session.commit()
                            flash("Course has been deleted", 'success')
                            return redirect(url_for('my_courses', ref=ref))
                        except Exception as e:
                            # Handle any errors during deletion
                            db.session.rollback()
                            flash(f"Error deleting course: {e}", "warning")
                            return redirect(url_for('my_courses', ref=ref))
                    else:
                        flash(f"No course found with ID {course_id}.", 'warning')
                        return redirect(url_for('my_courses', ref=ref))
                else:
                    flash("You are not enrolled in this course", 'error')
                    return redirect(url_for('my_courses', ref=ref))
            else:
                flash("Authorization invalid, this course is not yours", 'error')
                return redirect(url_for('my_courses', ref=ref))
        else:
            flash("User or course does not exist", 'error')
            return redirect(url_for('my_courses', ref=ref))

    # If the user is a student, deny access to course deletion
    else:
        flash('Student access unauthorized', 'error')
        return redirect(url_for('my_courses', ref=ref))
    
