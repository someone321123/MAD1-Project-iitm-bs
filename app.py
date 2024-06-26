from flask import Flask, render_template, request, redirect,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=  'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION']=False
app.config['SECRET_KEY'] = 'hush-secret'
db = SQLAlchemy(app)

app.app_context().push()

class influs(db.Model):
    __tablename__= 'influs'
    ID=db.Column(db.Integer,db.ForeignKey('users.ID'),primary_key=True )
    Name=db.Column(db.String(200),nullable=False,default="no name assigned", unique=True) 
    niche=db.Column(db.String(200),default="no niche assigned" )
    folls=db.Column(db.Integer,default=0)
    #plats=db.Column(db.DateTime,default=datetime.utcnow)
    plats=db.Column(db.String(10000),default="no platforms mentioned")
    bio=db.Column(db.String(1000),default='nothing here')
    def __repr__(self):
        return '<influs %r>' %self.ID 

class camps(db.Model):
    __tablename__='camps'
    ID=db.Column(db.Integer,primary_key=True)
    goal=db.Column(db.String(2000),default="no goal assigned")
    D_start=db.Column(db.DateTime,default=datetime.utcnow)
    D_end=db.Column(db.DateTime,default=datetime.utcnow)
    budget=db.Column(db.Integer, default = '100')
    visibs=db.Column(db.String(20),default='public')
    desc=db.Column(db.String(2000),default='no description given')
    spn=db.Column(db.Integer,db.ForeignKey('spons.ID'))
    def __repr__(self):
        return '<camps %r>' %self.ID 

class ads(db.Model):
    __tablename__='ads'
    ID=db.Column(db.Integer,primary_key=True)
    Name=db.Column(db.String(200),unique=True)
    reqs=db.Column(db.String(2000),default="no requirements assigned")
    budget=db.Column(db.Integer, default = '100')
    dura=db.Column(db.String(100),default='Not given')
    camps=db.Column(db.Integer,db.ForeignKey('camps.ID'))
    def __repr__(self):
        return '<ads %r>' %self.ID 

class spons(db.Model):
    __tablename__='spons'
    ID=db.Column(db.Integer, db.ForeignKey('users.ID'),primary_key=True,)
    Name = db.Column(db.String(200),unique=True)
   # niche= db.relationship('book', backref=db.backref('register', lazy=True))
    niche = db.Column(db.String(200))
    #user_id= db.relationship('users', backref=db.backref('register', lazy=True))
    bio=db.Column(db.String(2000),default="No Bio")
    def __repr__(self):
        return '<spons %r>' %self.ID 
    
class req(db.Model):
    __tablename__='req'
    ID=db.Column(db.Integer,db.ForeignKey('ads.ID'), primary_key=True)
    target=db.Column(db.Integer,db.ForeignKey('users.ID'))
    reqer=db.Column(db.Integer,db.ForeignKey('users.ID'))
    status=db.Column(db.String(50),default="Pending")
    D_iss=db.Column(db.DateTime,default=datetime.utcnow)
    def __repr__(self):
        return '<req %r>' %self.ID 

class users(db.Model):
    __tablename__='users'
    ID=db.Column(db.Integer,primary_key=True)
    Name=db.Column(db.String(100),default="user")
    Password=db.Column(db.String(15),default="0000")
    D_join=db.Column(db.DateTime,default=datetime.utcnow)
    Role=db.Column(db.String(200),default="inf") 
    def __repr__(self):
        return '<users %r>' %self.ID 


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
    try:
        if users.query.filter_by(ID=current_user).first().Role=='inf':
            return render_template('infh.html', current_user= current_user,users=users)
        else:
            return render_template('error.html',message='this is not the page you are looking for')
    except:
        return render_template('error.html',message='this is not the page you are looking for')
@app.route('/infs/<int:current_user>')
def infs(current_user):
    try:
        if users.query.filter_by(ID=current_user).first().Role=='inf':
            return render_template('infs.html',current_user=current_user, users=users)
        else:
            return render_template('error.html',message='this is not the page you are looking for')
    except:
        return render_template('error.html',message='this is not the page you are looking for')
@app.route('/infd/<int:current_user>')
def infd(current_user):
    try:
        if users.query.filter_by(ID=current_user).first().Role=='inf':
            return render_template('infd.html',current_user=current_user, users=users)
        else:
            return render_template('error.html',message='this is not the page you are looking for')
    except:
        return render_template('error.html',message='this is not the page you are looking for')
@app.route('/spnh/<int:current_user>')
def spnh(current_user):
    try:
        if users.query.filter_by(ID=current_user).first().Role=='spn':
            return render_template('spnh.html', current_user= current_user,users=users)
        else:
            return render_template('error.html',message='this is not the page you are looking for')
    except:
        return render_template('error.html',message='this is not the page you are looking for')    
@app.route('/spns/<int:current_user>')
def spns(current_user):
    try:
        if users.query.filter_by(ID=current_user).first().Role=='spn':
            return render_template('spns.html',current_user=current_user, users=users)
        else:
            return render_template('error.html',message='this is not the page you are looking for')
    except:
        return render_template('error.html',message='this is not the page you are looking for')
@app.route('/spnd/<int:current_user>')
def spnd(current_user):
    try:
        if users.query.filter_by(ID=current_user).first().Role=='spn':
            return render_template('spnd.html',current_user=current_user,camps=camps, users=users)
        else:
            return render_template('error.html',message='this is not the page you are looking for')
    except:
        return render_template('error.html',message='this is not the page you are looking for')
@app.route('/delete/<int:current_user>')
def delete(current_user):
    db.session.delete(users.query.filter_by(ID=current_user).first())
    db.session.commit()
    return redirect("/login")

@app.route('/new_camp/<int:current_user>', methods=['GET','POST'])
def new_camp(current_user):
    if request.method=="POST":
        try:
            goal = request.form['goal']
            deadline = request.form['deadline']
            budget = request.form['budget']
            visibility = request.form['visibs']
            description = request.form['desc']

            # Create new campaign instance
            new_campaign = camps(
                spn=current_user,
                goal=goal,
                D_end=datetime.strptime(deadline, '%Y-%m-%dT%H:%M'),
                budget=budget,
                visibs=visibility,
                desc=description
            )
            # Add and commit to the database
            db.session.add(new_campaign)
            db.session.commit()

            return redirect(f'/spnh/{current_user}')
        except Exception as e:
            return render_template('error.html', message=str(e))  # Handle other exceptions
    return render_template('new.html',users=users,req=req,ads=ads,current_user=current_user)



if __name__ == '__main__':
    app.run(debug=True)