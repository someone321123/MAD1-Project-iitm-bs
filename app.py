# login flask jwt, flask api
from flask import Flask, render_template, request, redirect,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource,Api
from flask_jwt_extended import create_access_token, JWTManager , get_jwt_identity ,jwt_required
from datetime import datetime

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=  'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION']=False
app.config['SECRET_KEY'] = 'hush-secret'
db = SQLAlchemy(app)
api = Api(app)
jwt = JWTManager(app)
app.app_context().push()
class SponserRegistration(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        password = data['password']
        if not username or not password:
            return {'message':'Missing information'}, 400
        if User.query.filter_by(username = username).first():
            return{'message':'choose other one'}, 400
        new = User(username = username, password = password)
        db.session.add(new)
        db.session.commit()
        return {'message':'Done'} ,200
class SponserLogin(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        password = data['password']
        user = User.query.filter_by(username= username).first()
        if user and user.password == password:
            access_token = create_access_token(identity = user.id)
            return {'access_token': access_token}, 400
        return {'message': 'invalid'}, 401
api.add_resource(SponserRegistration,'/register')
api.add_resource(SponserLogin,'/register')

class ProtectedResource(Resource):
    @jwt_required() #validates the token availability
    def get(self):
        current_user =id.get_jwt_identity()
        return {'message':"SUCCESS"} , 200

#HERE


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


users(Name='Admin',Password= 'admin@123',Role= 'Admin')
@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        name = request.form['name']
        password = request.form['password']
        role = request.form['role']
        user=users(Name=name,Role='user', Password=password)

        if users.query.filter_by(Name=name).first() is None:
            user=users(Name=name,Password=password, Role=role)
            db.session.add(user)
            db.session.commit()
            return render_template('login.html')
        else:
            return render_template('error.html')

    else:
        return render_template('register.html')


@app.route('/home')
#@jwt_required()
def html2():
    return render_template('2hom.html')

@app.route('/book')
#@jwt_required()
def main():
    return render_template('1buk.html')


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        name = request.form['name']
        password = request.form['password']
        try:
            if name == users.query.filter_by(Name=name,Password=password).first().Name and password == users.query.filter_by(Name=name,Password=password).first().Password:
                access_token = create_access_token(identity=users.query.filter_by(Name=name,Password=password).first().ID)
                return redirect('/infh')
        except:
            return render_template('error.html')
    return render_template('login.html')

@app.route('/infh')
@jwt_required
def infh():
    return render_template('infh.html')

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
