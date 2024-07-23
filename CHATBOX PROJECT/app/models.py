from app.routes import db

Classes_Person = db.Table('Classes_Person', 
    db.Column('person_id', db.Integer, db.ForeignKey('Person.person_id')),
    db.Column('classes_id', db.Integer, db.ForeignKey('Classes.class_id'))
) 


class Person(db.Model):
    __tablename__ = "Person"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    email = db.Column(db.text())
    password = db.Column(db.text())
    subject = db.Column(db.text())
    role = db.Column(db.text())
    year_level = db.Column(db.text())
    classes = db.relationship("Chats", back_populates="Class", cascade="all, delete-orphan")
    Classes = db.relationship("Classes",
        secondary="Classes_Person",
        back_populates='person')


class Classes(db.Model):
    __tablename__ = "Classes"
    class_id = db.Column(db.integer, primary_key=True)
    joining_code = db.column(db.integer())
    subject = db.column(db.Text())
    year_level = db.Column(db.text())
    persons = db.relationship("Chats", back_populates="person", cascade="all, delete-orphan")
    person = db.relationship("Person",
        secondary="Classes_person",
        back_populates="Classes")


class Chats(db.Model):
    __tablename__ = "Chats"
    chats_id = db.Column(db.integer, primary_key=True)
    person_id = db.Column(db.integer, db.ForeignKey("Person.person_id"))
    classes_id = db.Column(db.integer, db.ForeignKey("Classes.class_id"))
    person = db.relationship('Person', back_populates='classes')
    Class = db.relationship('Classes', back_populates='persons')








    


