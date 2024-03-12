# this repo is updated in vs code
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=  'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION']=False
db = SQLAlchemy(app)
app.app_context().push()

N=100000  #time for revoking access automatically

class book(db.Model):
    __tablename__= 'book'
    ID=db.Column(db.Integer,primary_key=True)
    Name=db.Column(db.String(200),nullable=False,default="no title assigned") 
    Category=db.Column(db.String(200),db.ForeignKey('section.Name'),default="no category assigned", )
    category = db.relationship('section', backref=db.backref('book', lazy=True))
    Author=db.Column(db.String(200),default="no author assigned")
    D_issue=db.Column(db.DateTime,default=datetime.utcnow)
    Content=db.Column(db.String(10000),default="no content assigned")
    Description=db.Column(db.String(1000),default='nothing here')
    Rating=db.Column(db.Integer,default="no rating assigned")
    def __repr__(self):
        return '<Book %r>' %self.id 

class section(db.Model):
    __tablename__='section'
    ID=db.Column(db.Integer,primary_key=True)
    Name=db.Column(db.String(200),default="no name assigned")
    D_issue=db.Column(db.DateTime,default=datetime.utcnow)
    Description=db.Column(db.String(1000),default="no description assigned")
    S_books=db.Column(db.Integer)

class users(db.Model):
    __tablename__='users'
    ID=db.Column(db.Integer,primary_key=True)
    Name=db.Column(db.String(100),default="user")
    Password=db.Column(db.String(15),default="0000")
    D_join=db.Column(db.DateTime,default=datetime.utcnow)
    Role=db.Column(db.String(200),default="no role assigned") 

class register(db.Model):
    __tablename__='register'
    ID=db.Column(db.Integer,primary_key=True)
    F_book_id = db.Column(db.Integer, db.ForeignKey('book.ID'))
    book_id= db.relationship('book', backref=db.backref('register', lazy=True))
    D_grant=db.Column(db.DateTime,default=datetime.utcnow)
    D_return=db.Column(db.DateTime,default=datetime.utcnow)
    F_user_id = db.Column(db.String(200), db.ForeignKey('users.ID'))
    user_id= db.relationship('users', backref=db.backref('register', lazy=True))
    Status=db.Column(db.String(2),default="N")
    Rating=db.Column(db.Integer,default=None)
    Comment=db.Column(db.String(1000),default=None)
db.create_all()
@app.route('/')
def mainhtml():
    return render_template('mainhtml.html')

@app.route('/home')
def html2():
    return render_template('2hom.html')

@app.route('/book')
def main():
    return render_template('1buk.html')
@app.route('/account')
def register():
    return render_template('5usp.html')

@app.route('/liblog.html')
def liblog():
    return render_template('liblog.html')

@app.route('/categories')
def cat():
    return render_template('3cat.html')

@app.route('/search')
def search():
    return render_template('4srh.html')

@app.route('/read')
def read():
    return render_template('6vew.html')

@app.route('/11das')
def dashboard():
    return render_template('11das.html')

@app.route('/12ind')
def index():
    return render_template('12ind.html')

@app.route('/13usr')
def user():
    return render_template('13usr.html')

@app.route('/14buk')
def libbuk():
    return render_template('14buk.html')

@app.route('/15cat')
def libccat():
    return render_template('15cat.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
