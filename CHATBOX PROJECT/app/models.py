from app.routes import db

Classes_Person = db.Table('Classes_Person', 
    db.Column('person_id', db.Integer, db.ForeignKey('Person.person_id')),
    db.Column('classes_id', db.Integer, db.ForeignKey('Classes.class_id'))
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
    classes = db.relationship("Chats", back_populates="Class", cascade="all, delete-orphan")
    Classes = db.relationship("Classes",
        secondary="Classes_Person",
        back_populates='person')


class Classes(db.Model):
    __tablename__ = "Classes"
    class_id = db.Column(db.Integer, primary_key=True)
    joining_code = db.Column(db.Integer())
    subject = db.Column(db.Text())
    year_level = db.Column(db.Text())
    persons = db.relationship("Chats", back_populates="person", cascade="all, delete-orphan")
    person = db.relationship("Person",
        secondary="Classes_Person",
        back_populates="Classes")


class Chats(db.Model):
    __tablename__ = "Chats"
    chats_id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey("Person.person_id"))
    classes_id = db.Column(db.Integer, db.ForeignKey("Classes.class_id"))
    person = db.relationship('Person', back_populates='classes')
    Class = db.relationship('Classes', back_populates='persons')








    


