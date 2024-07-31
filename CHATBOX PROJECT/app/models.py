from app.routes import db

Enrolement = db.Table('Enrolement', 
    db.Column('person_id', db.Integer, db.ForeignKey('Person.person_id')),
    db.Column('course_id', db.Integer, db.ForeignKey('Course.course_id'))
) 


class Person(db.Model):
    __tablename__ = "Person"
    person_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    email = db.Column(db.Text())
    password = db.Column(db.Text())
    subject = db.Column(db.Text())
    role = db.Column(db.Text())
    year_level = db.Column(db.Text())

    course_chats = db.relationship("Chat", back_populates="person", cascade="all, delete-orphan")
    courses = db.relationship("Course", secondary="Enrolement", back_populates='people')


class Course(db.Model):
    __tablename__ = "Course"
    course_id = db.Column(db.Integer, primary_key=True)
    joining_code = db.Column(db.Integer())
    subject = db.Column(db.Text())
    year_level = db.Column(db.Text())

    people_chats = db.relationship("Chat", back_populates="course", cascade="all, delete-orphan")
    people = db.relationship("Person", secondary="Enrolement", back_populates="courses")


class Chat(db.Model):
    __tablename__ = "Chat"
    chats_id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey("Person.person_id"))
    course_id = db.Column(db.Integer, db.ForeignKey("Course.course_id"))
    chat_content = db.Column(db.Text())
    chat_status = db.Column(db.Text())
    timestamp = db.Column(db.DateTime())

    person = db.relationship('Person', back_populates='course_chats')
    course = db.relationship('Course', back_populates='people_chats')






    


