from flask import Flask, render_template, request, redirect,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=  'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION']=False
app.config['SECRET_KEY'] = 'hush-secret'
db = SQLAlchemy(app)

app.app_context().push()

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

class users(db.Model):
    __tablename__='users'
    ID=db.Column(db.Integer,primary_key=True)
    Name=db.Column(db.String(100),default="user")
    Password=db.Column(db.String(15),default="0000")
    D_join=db.Column(db.DateTime,default=datetime.utcnow)
    Role=db.Column(db.String(200),default="inf") 

db.create_all()

@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        name = request.form['name']
        password = request.form['password']
        role = request.form.get('role')

        if users.query.filter_by(Name=name).first() is None:
            user=users(Name=name,Password=password, Role=role)
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
        else:
            return render_template('error.html',message='Username already exists')

    else:
        return render_template('register.html')


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')

        if not name or not password:
            return render_template('error.html', message="Name and Password are required")

        user = users.query.filter_by(Name=name, Password=password).first()
        if user and users.query.filter_by(Name=name).first().Password == password:
            global current_user
            current_user = users.query.filter_by(Name=name, Password=password).first().ID
            if users.query.filter_by(ID=current_user).first().Role=="spn":
                return redirect(f'/spnh/{current_user}')
            elif users.query.filter_by(ID=current_user).first().Role=="inf":
                return redirect(f'/infh/{current_user}')
            else:
                return render_template('error.html', message= 'Under Maintainance')
            
        else:
            return render_template('error.html', message="Looks like user doesnt exist")
    return render_template('login.html')

@app.route('/infh/<int:current_user>')
def infh(current_user):
    return render_template('infh.html', current_user= current_user,users=users)

@app.route('/infs/<int:current_user>')
def infs(current_user):
    return render_template('infs.html',current_user=current_user, users=users)

@app.route('/infd/<int:current_user>')
def infd(current_user):
    return render_template('infd.html',current_user=current_user, users=users)


@app.route('/spnh/<int:current_user>')
def spnh(current_user):
    return render_template('spnh.html', current_user= current_user,users=users)

@app.route('/spns/<int:current_user>')
def spns(current_user):
    return render_template('spns.html',current_user=current_user, users=users)

@app.route('/spnd/<int:current_user>')
def spnd(current_user):
    return render_template('spnd.html',current_user=current_user, users=users)

@app.route('/delete/<int:current_user>')
def delete(current_user):
    db.session.delete(users.query.filter_by(ID=current_user).first())
    db.session.commit()
    return redirect("/login")



if __name__ == '__main__':
    app.run(debug=True)