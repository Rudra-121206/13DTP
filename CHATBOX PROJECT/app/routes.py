from app import app
from flask import render_template, abort, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy # no more boring old SQL for us!
import os



basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, "chatbox.db")
db.init_app(app)
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'sup3r_secr3t_passw3rd'

import app.models as models
from app import forms

@app.route('/all_classes')
def all_classes():
    all_classes = models.Course.query.all()
    return render_template('all_courses.html', all_classes=all_classes)

@app.route("/create_acc", methods=['GET', 'POST'])
def create_acc():
    form = forms.login()
    if request.method == 'GET':
        return render_template('create_acc.html', form=form, title='Create an account(student)' )
    else:
        form.validate_on_submit()
        new_person = models.Person()
        new_person.role = "student"
        new_person.name = form.name.data
        new_person.email = form.email.data
        new_person.password = form.password.data
        new_person.year_level = form.year.data
        db.session.add(new_person)
        db.session.commit()
        return redirect(url_for('my_classes/{ref}', ref=new_person.person_id))


#@app.route("/my_classes/<:int:>")
#def all_classes(int):
    #my_classes=models.Classes_Person.classes.query.filter_by(person=int)
    #for classes in my_classes:
        #group = models.Classes.query.filter_by(class_id=classes)
    #return render_template()





 