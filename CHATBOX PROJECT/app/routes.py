from app import app
from flask import render_template, abort
from flask_sqlalchemy import SQLAlchemy # no more boring old SQL for us!
import os


basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, "chatbox.db")
db.init_app(app)


import app.models as models

@app.route('/all_classes')
def all_classes():
    all_classes = models.Classes.query.all()
    return render_template('all_classes.html', all_classes=all_classes)

 

 