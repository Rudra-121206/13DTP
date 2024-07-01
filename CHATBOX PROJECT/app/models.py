from app.routes import db

Classes_Person=db.Table('Classes_Person', 
    db.Column('', db.Integer, db.ForeignKey('')),
    db.Column('', db.Integer, db.ForeignKey(''))
) 

class Person(db.Model):
    __tablename__="Person"
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.Text())
    email=db.Column(db.text())
    password=db.Column(db.text())
    subject=db.Column(db.text())
    role=db.Column(db.text())
    year_level=db.Column(db.text())



class Classes(db.Model):
    __tablename__="Classes"
    class_id=db.Column(db.integer, primary_key=True)
    joining_code=db.column(db.integer())
    subject=db.column(db.Text())
    year_level=db.Column(db.text())


class Chats(db.Model):
    __tablename__="Chats"
    chats_id=db.Column(db.integer, primary_key=True)
    person_id=db.Column(db.integer, db.ForeignKey("Person.id"))
    classes_id=db.Column(db.integer, db.ForeignKey("Classes.class_id"))
    = db.relationship('Actor', back_populates='movies')
    movie = db.relationship('Movie', back_populates='actors')








    


