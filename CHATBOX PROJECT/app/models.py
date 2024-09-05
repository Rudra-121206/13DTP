from app.routes import db
from flask_login import UserMixin

Enrolement = db.Table('Enrolement', 
    db.Column('person_id', db.Integer, db.ForeignKey('User.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('Course.id'))
) 


class User(UserMixin, db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    email = db.Column(db.Text())
    password = db.Column(db.Text())
    role = db.Column(db.Text())
    year_level = db.Column(db.Text())

    course_chats = db.relationship("Chat", back_populates="user", cascade="all, delete-orphan")
    courses = db.relationship("Course", secondary="Enrolement", back_populates='people')

    def get_id(self):
        return str(self.id)

    def has_role(self, role_name):
        return self.role == role_name


class Course(db.Model):
    __tablename__ = "Course"
    id = db.Column(db.Integer, primary_key=True)
    joining_code = db.Column(db.Integer())
    subject = db.Column(db.Text())
    year_level = db.Column(db.Text())

    people_chats = db.relationship("Chat", back_populates="course", cascade="all, delete-orphan")
    people = db.relationship("User", secondary="Enrolement", back_populates="courses")


class Chat(db.Model):
    __tablename__ = "Chat"
    chat_id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey("User.id"))
    course_id = db.Column(db.Integer, db.ForeignKey("Course.id"))
    chat_content = db.Column(db.Text())
    chat_status = db.Column(db.Text())
    timestamp = db.Column(db.DateTime())

    user = db.relationship('User', back_populates='course_chats')
    course = db.relationship('Course', back_populates='people_chats')





    


