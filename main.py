from flask import Flask,render_template, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from flask import request,redirect,session,flash
from flask_login import UserMixin
from sklearn.feature_selection import f_classif
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
import json, os
import DT
from flask_cors import cross_origin
#import mail

# My Db Connection
local_server = True
app = Flask(__name__)
app.secret_key = 'vitalai'


#this is for getting unique user access 
login_manager=LoginManager(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/hms'
db = SQLAlchemy(app)


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    
class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50))
    Lname = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(1000))
    
class Patient(db.Model):
    pid = db.Column(db.Integer,primary_key=True)
    fname = db.Column(db.String(50))
    Lname = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    gender = db.Column(db.String(50))
    #age = db.Column(db.Integer(50))
    disease = db.Column(db.String(50))
    history = db.Column(db.String(50))
    
#try:
#        Test.query.all()
#        return 'My Database is connected'
#    except:
#       return 'My Database is not connected'
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/doctors")
def doctors():
    return render_template('doctors.html')

@app.route("/bot")
def bot():
    return render_template('bot.html')

@app.route("/disease",methods=["POST","GET"])
def disease():
    if request.method == "POST":
        global sym1,sym2,sym3,sym4,sym5,dis 
        sym1 = request.form.get('sym1')
        sym2 = request.form.get('sym2')
        sym3 = request.form.get('sym3')
        sym4 = request.form.get('sym4')
        sym5 = request.form.get('sym5')
        print(sym1,sym2,sym3,sym4,sym5)
        
        try:
            dis = DT.dt_pred(sym1,sym2,sym3,sym4,sym5)
            return redirect(url_for('bot'))
            
        except ValueError:
            print("Invalid Credentials")
            return render_template('disease.html')

    return render_template('disease.html')


@app.route('/webhook', methods=['GET','POST'])
@cross_origin()
def webhook():

    req = request.get_json(silent=True, force=True)

    print("req")
    

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    #print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


# processing the request from dialogflow
def processRequest(req):

    #sessionID=req.get('responseId')
    result = req.get("queryResult")
    #print(result)

    parameters = result.get("parameters")
    global diag1,diag2,diag3,dis
    diag1 = parameters.get("diag1")
    print(diag1)
    diag2 = int(parameters.get("diag2"))
    diag3 = parameters.get("diag3")
    print(dis)
    intent = result.get("intent").get('displayName')
    if (intent=='Default Welcome Intent - yes'):
        if(dis == '0'):
            status = 'Not Found'
        else:
            status = "You are Found with this"+dis+"Disease."

       
        fulfillmentText= status
        print(fulfillmentText)
        return {
            
            "fulfillmentText": fulfillmentText
        }
    
    email = current_user.email
    fname = current_user.fname
    Lname = current_user.Lname
    query = db.engine.execute(f"INSERT INTO `patient` (`f_name`, `Lname`, `email`, `gender`,`age`,`disease`,`history`) VALUES ('{fname}','{Lname}', '{email}', '{diag1}', '{diag2}', '{dis}', '{diag3}')")

# return render_template('bd.html', fname=current_user.fname, Lname=current_user.Lname)
#if not User.is_authenticated:

@app.route("/bd")
@login_required
def bd():
    em = current_user.email
    if em == 'doc123@gmail.com':
        query = db.engine.execute(f"SELECT * FROM `patient`")
        return render_template('bd.html',query=query)
    elif em == 'admin@gmail.com':
        query = db.engine.execute(f"SELECT * FROM `patient`")
        return render_template('bd.html',query=query)
    else:
        query = db.engine.execute(f"SELECT * FROM `patient` WHERE email='{em}'")
        return render_template('bd.html',query=query)


@app.route("/edit/<string:pid>",methods=["POST", "GET"])
@login_required
def edit(pid):
    posts = Patient.query.filter_by(pid=pid).first()
    if request.method == "POST":
        fname = request.form.get('fname')
        Lname = request.form.get('Lname')
        email = request.form.get('email')
        gender = request.form.get('gender')
        age = request.form.get('age')
        diss = request.form.get('diss')
        history = request.form.get('history')
        db.engine.execute(f"UPDATE `patient` SET `f_name` = '{fname}', `Lname` = '{Lname}', `email` = '{email}', `gender` = '{gender}', `age` = '{age}',`disease` = '{diss}',`history` = '{history}' WHERE `patient`.`pid`= '{pid}'")
        flash("Slot is Updated","success")
        return redirect('/bd')
    return render_template('edit.html',posts=posts)


@app.route("/login", methods=["POST","GET"])
def login():
    if request.method == "POST":
        

        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password,password):
            login_user(user)
            return redirect(url_for('index'))
        
        else:
            flash("Invalid Credentials","danger")
            return render_template('login.html')
        
    return render_template('login.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('login'))

@app.route("/patients")
@login_required
def patients():
    return render_template('patients.html',fname=current_user.fname, Lname=current_user.Lname)

@app.route("/signup", methods=["POST","GET"])
def signup():
    if request.method == "POST":
        fname = request.form.get('fname')
        Lname = request.form.get('Lname')
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Registered","warning")
            return render_template('signup.html')
        
        encpassword = generate_password_hash(password)
        new_user = db.engine.execute(f"INSERT INTO `user` (`fname`, `Lname`, `email`, `password`) VALUES ('{fname}','{Lname}', '{email}', '{encpassword}')")
        
        flash("Successfully Signup, Please Login","success")
        return render_template('login.html')
    
    
    return render_template('signup.html')


    




app.run(debug=True)