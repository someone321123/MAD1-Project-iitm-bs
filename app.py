# this repo is updated in vs code
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=  'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION']=False
db = SQLAlchemy(app)

class books(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    Name=db.Column(db.String(100),nullable=False,default="Xbook") 
    time=db.Column(db.String(100),default=datetime.utcnow)

def __repr__(self):
    return '<Book %r>' %self.id 

@app.route('/')
def mainhtml():
    return render_template('mainhtml.html')
@app.route('/html2')
def html2():
    return render_template('html2.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
