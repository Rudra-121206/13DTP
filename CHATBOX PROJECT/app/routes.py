from app import app
from flask import render_template, redirect, request, url_for, \
    flash, jsonify
from flask_sqlalchemy import SQLAlchemy  # Using SQLAlchemy for ORM functionality
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, LoginManager, \
    UserMixin, logout_user
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


@app.route('/all_courses/<int:ref>', methods=['GET', 'POST'])
def all_courses(ref):
    if not current_user.is_authenticated:
        flash('User is not authenticated', 'error')
        return redirect(url_for('login'))

    if current_user.id != ref:
        flash('Unauthorized access', 'error')
        return redirect(url_for('home'))

    if current_user.has_role('teacher'):
        flash('User access invalid', 'error')
        return redirect(url_for('create_course'))

    # Create forms for enrollment and search
    search_form = forms.SearchForm()
    search_query = request.args.get('search')

    # Filter courses based on search query
    all_courses = models.Course.query.filter(models.Course.subject.like(f'%{search_query}%')).all() if search_query else models.Course.query.all()
    enroll_forms = [forms.EnrollForm() for _ in all_courses]

    if request.method == 'POST':
        # Get the course_id from the form that was submitted
        submitted_course_id = request.form.get('course_id')

        # Ensure the form's course_id was submitted
        if not submitted_course_id:
            flash('Invalid course submission', 'error')
            return redirect(url_for('all_courses', ref=ref))

        # Get the course that matches the submitted course_id
        course = models.Course.query.get(submitted_course_id)
        if not course:
            flash('Course not found.', 'error')
            return redirect(url_for('all_courses', ref=ref))

        # Loop through enroll_forms to find the submitted form
        for i, enroll_form in enumerate(enroll_forms):
            # Only validate the form that was submitted (matches submitted_course_id)
            if enroll_form.submit_enroll.data and str(all_courses[i].id) == submitted_course_id:
                if enroll_form.validate_on_submit():
                    # Get the joining code from the form
                    joining_code_input = enroll_form.joining_code.data

                    # Check if the joining code matches the course's joining code
                    if joining_code_input == course.joining_code:
                        user = models.User.query.get(ref)

                        # Check if the user is already enrolled in the course
                        if course in user.courses:
                            flash('You are already enrolled in this course', 'warning')
                        else:
                            # Enroll the user in the course
                            user.courses.append(course)
                            db.session.add(user)
                            db.session.commit()
                            flash(f"Successfully enrolled in {course.subject}", 'success')
                        return redirect(url_for('my_courses', ref=ref))
                    else:
                        flash(f"Invalid joining code for {course.subject}", 'error')
                else:
                    flash(f"There was a problem with your enrollment for {course.subject}.", 'error')

        # Handle search form submission
        if 'submit_search' in request.form and search_form.validate_on_submit():
            search_query = search_form.search.data
            all_courses = models.Course.query.filter(models.Course.subject.like(f'%{search_query}%')).all()
            if not all_courses:
                flash("No courses found matching your search", 'error')

    return render_template('all_courses.html', 
                           all_courses=all_courses, 
                           enroll_forms=enroll_forms, 
                           search_form=search_form,
                           zip=zip)

# Route to create a teacher account
@app.route("/create_acc_teacher", methods=['GET', 'POST'])
def create_acc_teacher():
    form = forms.register_teacher()

    if current_user.is_authenticated:
        flash('User is already logged in')
        return redirect(url_for('my_courses', ref=current_user.id))

    if request.method == 'POST':
        if form.validate_on_submit():  # Check if form is valid
            existing_user = models.User.query.filter_by(email=form.email.data).first()
            if existing_user:
                flash('Email already in use. Please choose a different one.', 'error')
                return redirect(url_for('create_acc'))
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

#create a student account different from teacher as year field is present
@app.route("/create_acc_student", methods=['GET', 'POST'])
def create_acc_student():
    form = forms.register_student()

    if current_user.is_authenticated:
        flash('User is already logged in')
        return redirect(url_for('my_courses', ref=current_user.id))

    if request.method == 'POST':
        if form.validate_on_submit():  # Check if form is valid
            existing_user = models.User.query.filter_by(email=form.email.data).first()
            if existing_user:
                flash('Email already in use. Please choose a different one.', 'error')
                return redirect(url_for('create_acc_student'))
            new_user = models.User()
            new_user.role = "student"
            new_user.year_level = form.year.data
            new_user.name = form.name.data
            new_user.email = form.email.data
            new_user.password = generate_password_hash(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! Please login with your new details.', 'success')
            return redirect(url_for('login'))  # Redirect to login page for new user to login
        else:
            flash('Errors have occurred in form submission.', 'error')

    return render_template('create_acc_student.html', form=form, title='Create an account (teacher)')
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
    if request.method == 'POST':
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
        else:
            flash('please enter text between 2 and 60 char', 'error')
    return render_template('chats.html', form=form, chats=chats, name=name,
                           course_id=course_id)


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

        if request.method == 'POST':
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
        else:
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


# leave course
@app.route('/leave_course/<int:ref>/<int:course_id>')
def leave_course(ref, course_id):

    if not current_user.is_authenticated:
        flash('You must be logged in to leave a course', 'error')
        return redirect(url_for('login'))
    elif current_user.id != ref:
        flash('Unauthorized access', 'error')
        return redirect(url_for('home'))
    elif current_user.has_role('teacher'):
        return redirect(url_for('my_courses', ref=ref))
    # Find the course the user wants to leave
    course = models.Course.query.get(course_id)

    if not course:
        flash('Course not found', 'error')
        return redirect(url_for('all_courses', ref=current_user.id))

    # Check if the user is enrolled in the course
    if course not in current_user.courses:
        flash('You are not enrolled in this course', 'error')
        return redirect(url_for('all_courses', ref=current_user.id))

    # Remove the course from the user's courses
    current_user.courses.remove(course)

    try:
        db.session.commit()
        flash(f'You have successfully left the course: {course.subject}', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while leaving the course', 'error')

    return redirect(url_for('my_courses', ref=current_user.id))