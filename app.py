from flask import Flask,render_template,request,flash,redirect,url_for,session,current_app
from static.forms.contact import send_email,is_valid
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user,LoginManager,logout_user,user_logged_in,user_login_confirmed,user_logged_out
from datetime import datetime,timedelta
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
from functools import wraps
from bson import objectid

class User(UserMixin):
    def __init__(self,user_document):
        self.id = self
        self.name = user_document['name']
        self.username = user_document['username']
        self.email = user_document['email']

load_dotenv()
uri = os.environ.get("MONGODB_URI")
client = MongoClient(uri, server_api=ServerApi('1'))
auth_db = client.get_database('Auth').get_collection('users')
contact_db = client.get_database("Contact").get_collection("users")

login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"
bcrypt = Bcrypt()
current_user = None

@login_manager.user_loader
def load_user(user_id):
    global current_user
    user_id = current_user
    return user_id

def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        EXEMPT_METHODS = {"OPTIONS"}
        if request.method in EXEMPT_METHODS or current_app.config.get("LOGIN_DISABLED"):
            pass
        elif not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        
        if callable(getattr(current_app, "ensure_sync", None)):
            return current_app.ensure_sync(func)(*args, **kwargs)
        return func(*args, **kwargs)

    return decorated_view


App = Flask(__name__)
App.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
login_manager.init_app(App)
bcrypt.init_app(App)

@App.before_request
def session_handler():
    session.permanent = True
    App.permanent_session_lifetime = timedelta(minutes=1)


def connection_result(client):
    try:
        client.admin.command('ping')
        return True
    except  Exception as e :
        return e
    
def check_password(user,given,remember,source):
    if bcrypt.check_password_hash(user['password'],given):
        global current_user
        user_object = User(user)
        current_user = user_object
        login_user(user_object,remember=remember)
        session['logged_in'],session['name'],session['username'],session['email'] = True,user_object.name,user_object.username,user_object.email
        flash("Login Successfull" , 'success')
        return redirect('/')
    else:
        flash("Invalid Password !",'danger')
        return render_template('extra/login.html',value=user[f'{source}'])

@App.route("/")
def home():
    return render_template("main/index.html")

@App.route("/Login",methods=["GET","POST"])
def login():
    if request.method=="GET":
        return render_template("/extra/login.html",value=None)
    elif request.method=="POST":
        username = request.form['username']
        password = request.form['password']
        try:
            remember = request.form['remember']
        except:
            remember = False
        user_with_name , user_with_email = auth_db.find_one(filter={'username' : f'{username}'}) , auth_db.find_one(filter={'email' : f'{username}'})    
        if user_with_name!=None and user_with_email==None:
            return check_password(user_with_name,password,remember=remember,source='username')
        elif user_with_name==None and user_with_email!=None:
            return check_password(user_with_email,password,remember=remember,source='email')
        else:
            flash("Invalid Username or Email !",'danger')
            return render_template('extra/login.html',value=username)
    else: return None

@App.route("/Register",methods=["GET","POST"])
def register():
    if request.method=="GET":
        return render_template("/extra/register.html",value=None)
    elif request.method=="POST":
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        if auth_db.find_one(filter={'email' : f'{email}'}) == None:
            if auth_db.find_one(filter={'username' : f'{username}'}) == None:
                auth_db.insert_one({'name' : f'{name}' , 'email' : f'{email}' , 'username' : f'{username}' , 'password' : f'{password}'})
                flash("Registered Successfully !",'success')
                return render_template('extra/login.html',value=username)
            else:
                flash("Username Already Exists !",'warning')
                return render_template('extra/register.html',value={'name' : f'{name}' , 'email' : f'{email}' , 'username' : f'{username}'})
        else:
            flash("Email Already Exists !",'warning')
            return render_template('extra/register.html',value={'name' : f'{name}' , 'email' : f'{email}' , 'username' : f'{username}'})
    else: return None


@App.route("/DA-1")
@App.route("/DA-2")
@App.route("/DA-3")
@App.route("/ML-1")
@App.route("/ML-2")
@App.route("/ML-3")
@App.route("/DL-1")
@App.route("/DL-2")
@App.route("/DL-3")
def project_dis():
    re = str(request.url_rule)
    if re in ["/DA-1","/DA-2","/DA-3"]:
        return render_template("portfolio/portfolio-DA.html",value = re)
    elif re in ["/ML-1","/ML-2","/ML-3"]:
        return render_template("portfolio/portfolio-ML.html",value = re)
    elif re in ["/DL-1","/DL-2","/DL-3"]:
        return render_template("portfolio/portfolio-DL.html",value = re)
    else:
        return None

@App.route("/Contact",methods=["GET","POST"])
def contact():
    if request.method=="POST":
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        sent = True
        if contact_db.find_one(filter={'email' : f'{email}'}) == None:          
            if is_valid(email):
                contact_db.insert_one( {'date_time' : f'{datetime.now()}' , 'name' : f'{name}' , 'email' : f'{email}' , 'subject' : f'{subject}' , 'message' : f'{message}' } )
                sent = send_email(name,email,subject,message,other=True)
            else:
                sent = False
            return render_template("contact/contact_result.html",value=sent)
        else:
            sent = 'old'
            return render_template("contact/contact_result.html",value=sent)
    else:
        return False




@App.route("/dashboard")
@login_required
def user_about(userid):
    user = auth_db.find_one(filter={'_id' : f'{userid}'})
    return f"Name = {user['name']}<br>Email = {user['email']}<br>Username = {user['username']}"

@App.route("/Logout")
@login_required
def logout():
    print(current_user,type(current_user))
    if session['logged_in']==True:
        session['logged_in']=False
        logout_user()
        flash("Logged Out Successfully !","success")
        return redirect('Login')

if __name__ == "__main__":
    if connection_result(client) == True :
        App.run(debug=True)
    else :
        print(connection_result(client))