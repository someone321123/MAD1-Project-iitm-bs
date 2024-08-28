from flask import Flask, render_template, request, redirect,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import time

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
    flag=db.Column(db.Integer, default=0)
    ph_no = db.Column(db.String(20),default="none")
    
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
    flag=db.Column(db.Integer, default=0)
    
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
    ad = db.Column(db.Integer, db.ForeignKey('ads.ID'), nullable=False)
    target = db.Column(db.Integer, db.ForeignKey('users.ID'))
    reqer = db.Column(db.Integer, db.ForeignKey('users.ID'))
    status = db.Column(db.String(50), default="PENDING")
    D_iss = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<req {self.ID}>'

class neg(db.Model):
    __tablename__ = 'neg'
    ID = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.Integer)
    Name = db.Column(db.String(200))
    reqs = db.Column(db.String(2000), default="no requirements assigned")
    budget = db.Column(db.Integer, default=100)
    dura = db.Column(db.String(100), default='Not given')


    def __repr__(self):
        return f'<neg {self.ID}>'


db.create_all()
if users.query.filter_by(Role='adm').first() is None:
    user=users(Name='admin',Password='admin', Role='adm')
    db.session.add(user)
    db.session.commit()

@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        name = request.form['name']
        password = request.form['password']
        role = request.form.get('role')
        ph = request.form.get('phone')

        if users.query.filter_by(Name=name).first() is None:
            user=users(Name=name,Password=password, Role=role, ph_no=ph)
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
        if name =='admin' and password=='admin':
            global adm
            adm=users.query.filter_by(Name=name, Password=password).first().ID
            return redirect('/admh')

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

@app.route('/admh')
def admh():
    return render_template('admh.html', users=users,camps=camps, req=req,ads=ads, current_user=adm)

@app.route('/adms', methods=['GET','POST'])
def adms():
    results=users.query.filter_by(ID=adm).first()
    if request.method=='POST':
        value = request.form['value']
        results=users.query.filter_by(ID=value).first()
        return render_template('adms.html', users=users, req=req,ads=ads,camps=camps, spons=spons,influs=influs, current_user=adm, results=results)
    return render_template('adms.html', users=users,camps=camps, req=req,ads=ads, current_user=adm, results=results)

@app.route('/flag/<string:type>/<int:id>/<int:flag>')
def flag(id,type,flag):
    if type=='u':
        if flag==1:
            users.query.filter_by(ID=id).update({'flag':1})
        else:
            users.query.filter_by(ID=id).update({'flag':0})
            db.session.commit()
            return redirect('/admh')
    if type=='c':
        if flag==1:
            camps.query.filter_by(ID=id).update({'flag':1})
        else:
            camps.query.filter_by(ID=id).update({'flag':0})
            db.session.commit()
            return redirect('/admh')
    db.session.commit()
    return redirect('/adms')

@app.route('/admd', methods=['GET', 'POST'])
def admd():
    return render_template('admd.html', users=users, req=req,ads=ads, current_user=adm, camps=camps, spons=spons, influs=influs, neg=neg)


@app.route('/infh/<int:current_user>', methods=['GET', 'POST'])
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
    result = ads.query.all()
    results_priv=ads.query.join(camps, ads.camps==camps.ID).filter(camps.visibs=='private').all()
  
    results=[i for i in result if i not in results_priv]
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
        results_priv=ads.query.join(camps, ads.camps==camps.ID).filter(camps.visibs=='private').all()
        
        # Combine results (removing duplicates)
        result = list(set(results_ads + results_camps +results_spons ))
        results=[i for i in result if i not in results_priv]
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
        view = request.form.get('view')
        inf= request.form.get('influ')
        inf= influs.query.filter_by(ID=inf).first()
        if view=='view':
            return render_template('view.html',current_user=current_user, users=users, camps=camps, spons=spons,ads=ads, results=results, influ=inf,view='influ')
        value = request.form['value']        
        # Query for influs
        results_inf = influs.query.filter(influs.Name.ilike(f'%{value}%')).all()       
        # Query for plat
        results_plts = influs.query.filter(influs.plats.ilike(f'%{value}%')).all()       
        # Query for Niche
        results_niche = influs.query.filter(influs.niche.ilike(f'%{value}%')).all()
    #    results_folls = influs.query.filter(influs.folls.ilike(f'%{value}%')).all()
        results_id=influs.query.filter(influs.ID.ilike(f'%{value}%')).all()
        # Combine results (removing duplicates)
        results = list(set( results_plts +results_niche  + results_id+results_inf))
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
        req.query.filter_by(reqer=current_user).delete()
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
                camps=camp           )
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

@app.route('/new_neg', methods=['GET','POST'])
def new_neg():
    if request.method=='POST':
        try:
            reqs = request.form['reqs']
            budget = request.form['budget']
            dura = request.form['dura']
            ad=request.form['ad']
            new_neg = neg(
                reqs=reqs,
                dura=dura,
                budget=budget,
                ad=req.query.filter_by(ID=ad).first().ad,
                Name=ads.query.filter_by(ID=req.query.filter_by(ID=ad).first().ad).first().Name
                )
            new_req=req(
                target=spons.query.filter_by(ID=camps.query.filter_by(ID=ads.query.filter_by(ID=req.query.filter_by(ID=ad).first().ad).first().camps).first().spn).first().ID,
                reqer=current_user,
                ad=req.query.filter_by(ID=ad).first().ad,
                status='NEGOTIATION',
                D_iss=datetime.utcnow()
                )
            db.session.add(new_req)
            db.session.add(new_neg)

            ####
            req.query.filter_by(ID=ad).delete()
            db.session.commit()
            return redirect(f'/infh/{current_user}')
        except Exception as e:
            return render_template('error.html', message=str(e))
    return render_template('error.html', message="Method not allowed")

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
#may have errors
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
            elif request.form['action']=='REJECT NEGOTIATION':
                if req.query.filter_by(ID=request_id).first().status=='NEGOTIATION':
                    neg.query.filter_by(ad=req.query.filter_by(ID=request_id).first().ad).delete()
                    db.session.commit()
                    req.query.filter_by(ID=request_id).delete()
                db.session.commit()
                if users.query.filter_by(ID=current_user).first().Role=='inf':
                    return redirect(f'/infh/{current_user}')
                elif users.query.filter_by(ID=current_user).first().Role=='spn':
                    return redirect(f'/spnh/{current_user}') 
            elif request.form['action']=='ACCEPT NEGOTIATION':
                if req.query.filter_by(ID=request_id).first().status=='NEGOTIATION':
                    ads.query.filter_by(ID=req.query.filter_by(ID=request_id).first().ad).update({
                        'reqs':neg.query.filter_by(ad=req.query.filter_by(ID=request_id).first().ad).first().reqs,
                        'dura':neg.query.filter_by(ad=req.query.filter_by(ID=request_id).first().ad).first().dura,
                        'budget':neg.query.filter_by(ad=req.query.filter_by(ID=request_id).first().ad).first().budget,
                        })
            
                    neg.query.filter_by(ad=req.query.filter_by(ID=request_id).first().ad).delete()
                    req.query.filter_by(ID=request_id).update({'status':'ACCEPTED'})
                    db.session.commit()
                    if users.query.filter_by(ID=current_user).first().Role=='spn':
                        return redirect(f'/spnh/{current_user}')
                    
            elif request.form['action']=='Make Request':
                reqe = req(
                    target=spons.query.filter_by(ID=camps.query.filter_by(ID=ads.query.filter_by(ID=request_id).first().camps).first().spn).first().ID,
                    reqer=current_user,
                    ad=request_id,
                    status='PENDING',
                    D_iss=datetime.utcnow()
                )
                db.session.add(reqe)
                db.session.commit()
                if users.query.filter_by(ID=current_user).first().Role=='inf':
                    return redirect(f'/infs/{current_user}')
                elif users.query.filter_by(ID=current_user).first().Role=='spn':
                    return redirect(f'/spns/{current_user}')
                else:
                    return render_template('error.html', message="User doesnt exist")
                
            elif request.form['action']=='Make Negotiation':
                
                ad = request_id
                return render_template('view.html', view='neg', ad=ad, ads=ads, users=users, req=req, camps=camps, spons=spons, influs=influs)
            elif request.form['action']=='VIEW NEGOTIATION':
                ad = request_id
                return render_template('view.html', view='view_neg', ad=ad, ads=ads,neg=neg,current_user=current_user, users=users, req=req, camps=camps, spons=spons, influs=influs)   

            else:
                return render_template('error.html', message="Under Maintainance")
        except Exception as e:
            return render_template('error.html', message=str(e))  # Handle other exceptions


#*****development settings*******
#current_user=1
adm=1
#****remove this line when you are done with development*******


if __name__ == '__main__':
    app.run(debug=True)