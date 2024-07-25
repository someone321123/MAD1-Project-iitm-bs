from flask import Flask, render_template, request, redirect,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=  'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION']=False
app.config['SECRET_KEY'] = 'hush-secret'
db = SQLAlchemy(app)

app.app_context().push()


class users(db.Model):
    __tablename__ = 'users'
    ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), unique=True, index=True)
    Password = db.Column(db.String(255), nullable=False)
    D_join = db.Column(db.DateTime, default=datetime.utcnow)
    Role = db.Column(db.String(200), default="inf")
    
    # Relationships
    influ = db.relationship('influs', backref='user', uselist=False)
    spon = db.relationship('spons', backref='user', uselist=False)
    requests_made = db.relationship('req', backref='requester', foreign_keys='req.reqer')
    requests_received = db.relationship('req', backref='target_user', foreign_keys='req.target')

    def __repr__(self):
        return f'<users {self.Name}>'

class influs(db.Model):
    __tablename__ = 'influs'
    ID = db.Column(db.Integer, db.ForeignKey('users.ID'), primary_key=True)
    Name = db.Column(db.String(200), nullable=False, unique=True, index=True)
    niche = db.Column(db.String(200), default="no niche assigned")
    folls = db.Column(db.Integer, default=0)
    plats = db.Column(db.String(10000), default="no platforms mentioned")
    bio = db.Column(db.String(1000), default='nothing here')

    def __repr__(self):
        return f'<influs {self.Name}>'

class spons(db.Model):
    __tablename__ = 'spons'
    ID = db.Column(db.Integer, db.ForeignKey('users.ID'), primary_key=True)
    Name = db.Column(db.String(200), unique=True, index=True)
    niche = db.Column(db.String(200))
    bio = db.Column(db.String(2000), default="No Bio")
    
    # Relationship
    campaigns = db.relationship('camps', backref='sponsor', lazy='dynamic')

    def __repr__(self):
        return f'<spons {self.Name}>'

class camps(db.Model):
    __tablename__ = 'camps'
    ID = db.Column(db.Integer, primary_key=True)
    goal = db.Column(db.String(2000),unique=True ,default="no goal assigned")
    D_start = db.Column(db.DateTime, default=datetime.utcnow)
    D_end = db.Column(db.DateTime, default=datetime.utcnow)
    budget = db.Column(db.Integer, default=100)
    visibs = db.Column(db.String(20), default='public')
    desc = db.Column(db.String(2000), default='no description given')
    spn = db.Column(db.Integer, db.ForeignKey('spons.ID'))
    
    # Relationship
    ads = db.relationship('ads', backref='campaign', lazy='dynamic')

    def __repr__(self):
        return f'<camps {self.ID}>'

class ads(db.Model):
    __tablename__ = 'ads'
    ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(200), unique=True, index=True)
    reqs = db.Column(db.String(2000), default="no requirements assigned")
    budget = db.Column(db.Integer, default=100)
    dura = db.Column(db.String(100), default='Not given')
    camps = db.Column(db.Integer, db.ForeignKey('camps.ID'))
    
    # Relationship
    ad_requests = db.relationship('req', backref='advertisement', lazy='dynamic')

    def __repr__(self):
        return f'<ads {self.Name}>'

class req(db.Model):
    __tablename__ = 'req'
    ID = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.Integer, db.ForeignKey('ads.ID'))
    target = db.Column(db.Integer, db.ForeignKey('users.ID'))
    reqer = db.Column(db.Integer, db.ForeignKey('users.ID'))
    status = db.Column(db.String(50), default="PENDING")
    D_iss = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<req {self.ID}>'


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
            if role=='inf':
                inf= influs( Name=name,ID=users.query.filter_by(Name=name).first().ID)
                db.session.add(inf)
                db.session.commit()
            elif role=='spn':
                spn= spons(Name=name, ID=users.query.filter_by(Name=name).first().ID)
                db.session.add(spn)
                db.session.commit()
# add admin role
            else:
                return render_template('error.html',message='Under Maintainance')

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
            return render_template('infh.html', current_user= current_user,users=users,req=req,ads=ads)
        else:
            return render_template('error.html',message='this is not the page you are looking for')
    except Exception as e:
        return render_template('error.html',message=str(e))

@app.route('/infs/<int:current_user>', methods=['GET','POST'])
def infs(current_user):
    results = ads.query.all()
    if request.method=='POST':
        value = request.form['value']
        
        # Query for Ads
        results_ads = ads.query.filter(ads.Name.ilike(f'%{value}%')).all()
       
        # Query for Camps
        results_camps = (ads.query
                         .join(camps, ads.camps == camps.ID)
                         .filter(camps.goal.ilike(f'%{value}%'))
                         .all())
       
        # Query for Spons
        results_spons = (ads.query
                         .join(camps, ads.camps == camps.ID)
                         .join(spons, camps.spn == spons.ID)
                         .filter(spons.Name.ilike(f'%{value}%'))
                         .all())
        
        # Combine results (removing duplicates)
        results = list(set(results_ads + results_camps +results_spons))
        return render_template('infs.html',current_user=current_user, users=users, camps=camps, spons=spons,ads=ads, results=results)
    try:
        if users.query.filter_by(ID=current_user).first().Role=='inf':
            return render_template('infs.html',current_user=current_user, users=users, camps=camps, spons=spons,ads=ads, results=results)
        else:
            return render_template('error.html',message='this is not the page you are looking for')
    except Exception as e:
        return render_template('error.html',message=str(e))
@app.route('/infd/<int:current_user>')
def infd(current_user):
    try:
        if users.query.filter_by(ID=current_user).first().Role=='inf':
            return render_template('infd.html',current_user=current_user, users=users, influs=influs, ads=ads)
        else:
            return render_template('error.html',message='this is not the page you are looking for')
    except:
        return render_template('error.html',message='this is not the page you are looking for')
@app.route('/spnh/<int:current_user>')
def spnh(current_user):
    try:
        if users.query.filter_by(ID=current_user).first().Role=='spn':
            return render_template('spnh.html', current_user= current_user,users=users,req=req,ads=ads)
        else:
            return render_template('error.html',message='this is not the page you are looking for')
    except:
        return render_template('error.html',message='this is not the page you are looking for')    
@app.route('/spns/<int:current_user>' , methods=['GET','POST'])
def spns(current_user):
    results = influs.query.all()
    if request.method=='POST':
        value = request.form['value']
        
        # Query for influs
        results_inf = influs.query.filter(influs.Name.ilike(f'%{value}%')).all()
       
        # Query for plat
        results_plts = influs.query.filter(influs.plats.ilike(f'%{value}%')).all()
       
        # Query for Niche
        results_niche = influs.query.filter(influs.niche.ilike(f'%{value}%')).all()
        
        # Combine results (removing duplicates)
        results = list(set(results_inf + results_plts +results_niche))
        return render_template('spns.html',current_user=current_user, users=users, camps=camps, spons=spons,ads=ads, results=results)
    try:
        if users.query.filter_by(ID=current_user).first().Role=='spn':
            return render_template('spns.html',current_user=current_user, users=users,camps=camps, spons=spons,ads=ads,results=results)
        else:
            return render_template('error.html',message='this is not the page you are looking for')
    except Exception as e:
        return render_template('error.html',message=str(e))
    
@app.route('/spnd/<int:current_user>' , methods=['GET','POST'])
def spnd(current_user):
    try:
        if request.method=='POST':
            try:
                niche = request.form['niche']
                bio = request.form['bio']

                spons.query.filter_by(ID=current_user).update({'niche' : niche,
                    'bio':bio})
                    
                db.session.commit()
                return redirect(f'/spnd/{current_user}')
            except Exception as e:
                return render_template('error.html', message=str(e))  # Handle other exceptions
        if users.query.filter_by(ID=current_user).first().Role=='spn':
            return render_template('spnd.html',current_user=current_user,camps=camps, users=users,ads=ads, spons=spons)
        else:
            return render_template('error.html',message='this is not the page you are looking for')
    except:
        return render_template('error.html',message='this is not the page you are looking for')
@app.route('/delete/<int:current_user>')
def delete(current_user):
    for camp in camps.query.filter_by(spn=current_user).all():
        for ad in ads.query.filter_by(camps=camp.ID).all():
            req.query.filter_by(ad=ad.ID).delete()
            db.session.delete(ad)
        db.session.delete(camp)
    if users.query.filter_by(ID=current_user).first().Role=='inf':
        influs.query.filter_by(ID=current_user).delete()
    elif users.query.filter_by(ID=current_user).first().Role=='spn':
        spons.query.filter_by(ID=current_user).delete()
    else:
        return render_template('error.html',message='Under Maintainance')
    db.session.delete(users.query.filter_by(ID=current_user).first())
    db.session.commit()
    return redirect("/login")

@app.route('/delete_ad/<int:ad>')
def delete_ad(ad):
    req.query.filter_by(ad=ad).delete()
    db.session.delete(ads.query.filter_by(ID=ad).first())
    db.session.commit()
    return redirect(f'/spnd/{current_user}')

@app.route('/delete_camp/<int:camp>')
def delete_camp(camp):
    for i in ads.query.filter_by(camps=camp).all():
        req.query.filter_by(ad=i.ID).delete()
    ads.query.filter_by(camps=camp).delete()
    camps.query.filter_by(ID=camp).delete()
    db.session.commit()
    return redirect(f'/spnd/{current_user}')

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
    return render_template('new.html',users=users,req=req,ads=ads,current_user=current_user, new='camp')

@app.route('/new_ad/<int:camp>', methods=['GET','POST'])
def new_ad(camp):
    if request.method=='POST':
        try:
            Name = request.form['Name']
            reqs = request.form['reqs']
            budget = request.form['budget']
            dura = request.form['dura']
            new_ad = ads(
                Name=Name,
                reqs=reqs,
                dura=dura,
                budget=budget,
                camps=camp,            )
            db.session.add(new_ad)
            db.session.commit()

            return redirect(f'/spnd/{current_user}')
        except Exception as e:
            return render_template('error.html', message=str(e))  # Handle other exceptions
    return render_template('new.html',users=users,req=req,ads=ads,current_user=current_user, new='ad', camp=camp)

@app.route('/new_request/<int:ad>', methods=['GET','POST'])
def new_request(ad):
    if request.method=='POST':
        try:
            target = request.form['target']
            reqer=current_user
            ad=request.form['ad']
            if int(target)==reqer:
                return render_template('error.html', message="You cant request yourself")
            elif ads.query.filter_by(ID=ad).first() is None:
                return render_template('error.html', message="This ad doesnt exist")
            elif camps.query.filter_by(ID=ads.query.filter_by(ID=ad).first().camps).first().spn!=current_user:
                return render_template('error.html', message="This ad is not yours")
    
            elif users.query.filter_by(ID=target).first() is None:
                return render_template('error.html', message="This user doesnt exist")
            else:
                new_req = req(
                    target=target,
                    reqer=reqer,
                    ad=ad,            )
                db.session.add(new_req)
                db.session.commit()

                return redirect(f'/spnd/{current_user}')
        except Exception as e:
            return render_template('error.html', message=str(e))  # Handle other exceptions
    return render_template('new.html',users=users,req=req,ads=ads,current_user=current_user, new='req', ad=ad)

@app.route('/update/<int:current_user>', methods=['GET','POST'])
def update(current_user):
    if request.method=='POST' and users.query.filter_by(ID=current_user).first().Role=='inf':
        try:
            niche = request.form['niche']
            folls = request.form['folls']
            plats = request.form['plats']
            bio = request.form['bio']

            influs.query.filter_by(ID=current_user).update({'niche' : niche,
                'folls':folls,
                'plats':plats,
                'bio':bio})
                
            db.session.commit()
            return redirect(f'/infd/{current_user}')
# add admin role
        except Exception as e:
            return render_template('error.html', message=str(e))  # Handle other exceptions
        
    return render_template('new.html',users=users,req=req,ads=ads,current_user=current_user, new='update_user', influs=influs)

@app.route('/update_camp/<int:camp>', methods=['GET','POST'])
def update_camp(camp):
    if request.method=='POST':
        try:
            goal = request.form['goal']
            deadline = request.form['deadline']
            budget = request.form['budget']
            visibility = request.form['visibs']
            description = request.form['desc']

            camps.query.filter_by(ID=camp).update({'goal' : goal,
                'D_end':datetime.strptime(deadline, '%Y-%m-%dT%H:%M'),
                'budget':budget,
                'visibs':visibility,
                'desc':description})
                
            db.session.commit()

            return redirect(f'/spnd/{current_user}')
        except Exception as e:
            return render_template('error.html', message=str(e))  # Handle other exceptions
    return render_template('new.html',users=users, camps=camps, req=req,ads=ads,current_user=current_user, new='update_camp', camp=camp)

@app.route('/update_ad/<int:ad>', methods=['GET','POST'])
def update_ad(ad):
    if request.method=='POST':
        try:
            Name = request.form['Name']
            budget = request.form['budget']
            dura = request.form['dura']
            request.form['reqs']
            ads.query.filter_by(ID=ad).update({'Name' : Name,                              
                'dura':dura,
                'reqs':request.form['reqs'],
                'budget':budget})
            db.session.commit()

            return redirect(f'/spnd/{current_user}')
        except Exception as e:
            return render_template('error.html', message=str(e))  # Handle other exceptions
    return render_template('new.html',users=users,req=req,ads=ads,current_user=current_user, new='update_ad',ad=ad)

@app.route('/update_req/<int:request_id>', methods=['GET','POST'])
def update_req(request_id):
    if request.method=='POST':
        try:
            if request.form['action']=='ACCEPT':
                req.query.filter_by(ID=request_id).update({'status':'ACCEPTED'})
                db.session.commit()
                if users.query.filter_by(ID=current_user).first().Role=='inf':
                    return redirect(f'/infh/{current_user}')
                elif users.query.filter_by(ID=current_user).first().Role=='spn':
                    return redirect(f'/spnh/{current_user}')
            elif request.form['action']=='REJECT':
                req.query.filter_by(ID=request_id).delete()
                db.session.commit()
                if users.query.filter_by(ID=current_user).first().Role=='inf':
                    return redirect(f'/infh/{current_user}')
                elif users.query.filter_by(ID=current_user).first().Role=='spn':
                    return redirect(f'/spnh/{current_user}')    
            else:
                return render_template('error.html', message="Under Maintainance")
        except Exception as e:
            return render_template('error.html', message=str(e))  # Handle other exceptions

#*****development settings*******
current_user=1

if __name__ == '__main__':
    app.run(debug=True)