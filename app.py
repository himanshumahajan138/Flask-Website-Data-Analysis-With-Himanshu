from flask import Flask,render_template,request,flash,redirect,session
from flask_bcrypt import Bcrypt
from flask_login import login_user,LoginManager,login_required,logout_user,current_user
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os,random,codecs
from datetime import datetime,timedelta
from dotenv import load_dotenv
from flask_toastr import Toastr
from users import User,User_info
from static.forms.contact import is_valid,send_email
from bson.objectid import ObjectId
from fileinput import filename

def connection_result(client):
    try:
        client.admin.command('ping')
        return True
    except  Exception as e :
        return e
    
def check_password(user,given,remember,source):
    if bcrypt.check_password_hash(user['password'],given):
        user_object = User_info(user)
        login_user(user_object,remember=remember)
        flash({'title': "Success", 'message': "Login Successfull"}, 'success')
        return redirect('/User-Profile')
    else:
        flash({'title': "Error", 'message': "Invalid Password !"}, 'error')
        return render_template('auth/login.html',value=user[f'{source}'])


load_dotenv()
uri = os.environ.get("DATABASE_URL")
client = MongoClient(uri, server_api=ServerApi('1'))
auth_db = client.get_database('Auth').get_collection('users')
contact_db = client.get_database("Contact").get_collection("users")
bcrypt = Bcrypt()

App = Flask(__name__)
App.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
login_manager = LoginManager(app=App)
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"
login_manager.init_app(App)
bcrypt.init_app(App)
toastr = Toastr(app=App)

# App.jinja_env.globals.update(send_otp=send_otp)

@login_manager.user_loader
def load_user(user_id):
        try:
            user_id=session["_user_id"]
        except:
            session.clear()
        finally:
            id = ObjectId(user_id)
            user_doc = auth_db.find_one(filter={'_id':id})
            user_obj = User_info(user_document=user_doc)
            return user_obj

@App.before_request
def session_handler():
    session.permanent = True
    # App.permanent_session_lifetime = timedelta(minutes=1)


@App.route("/")
def home():
    return render_template("main/index.html")


@App.route("/Login",methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    else:
        if request.method=="GET":
            return render_template("auth/login.html",value=None)
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
                flash({'title': "Error", 'message': "Invalid Username or Email !",'options':{'TOASTR_POSITION_CLASS':'toast-top-center'}}, 'error')
                return render_template('auth/login.html',value=username)
        else: return None

@App.route("/Register",methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        return redirect('/')
    else:
        if request.method=="GET":
            return render_template("auth/register.html",value=None,otp_req=False)
        elif request.method=="POST":
            global otp_list,user_name,user_email,user_username,user_password
            user_name = request.form['name']
            user_email = request.form['email']
            user_username = request.form['username']
            user_password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
            if auth_db.find_one(filter={'email' : f'{user_email}'}) == None:
                if auth_db.find_one(filter={'username' : f'{user_username}'}) == None:
                    x = round(random.random()*1000000)
                    otp_list=[]
                    otp_list.append(x)
                    send_email(name=user_name,email=user_email,other=True,count=1,otp=otp_list[0])
                    return render_template('auth/register.html',value={'name' : f'{user_name}' , 'email' : f'{user_email}' , 'username' : f'{user_username}'},otp_req=True)
                else:
                    flash({'title': "Warning", 'message': "Username Already Exists !",}, 'warning')
                    return render_template('auth/register.html',value={'name' : f'{user_name}' , 'email' : f'{user_email}' , 'username' : f'{user_username}'},otp_req=False)
            else:
                flash({'title': "Warning", 'message': "Email Already Exists !"}, 'warning')
                return render_template('auth/register.html',value={'name' : f'{user_name}' , 'email' : f'{user_email}' , 'username' : f'{user_username}'},otp_req=False)
        else: return None

@App.route("/OTP-Validation",methods=["GET","POST"])
def send_otp():
    if current_user.is_authenticated:
            return redirect("/")
    else:
        if request.method=="POST":
            global otp_list,user_name,user_email,user_username,user_password
            print(int(request.form['otp']),otp_list)
            if int(request.form['otp']) == otp_list[0]:
                auth_db.insert_one({'name' : f'{user_name}' , 'email' : f'{user_email}' , 'username' : f'{user_username}' , 'password' : f'{user_password}'})
                flash({'title': "Success", 'message': "Registered Successfully!"}, 'success')
                return render_template('auth/login.html',value=user_username)
            else:
                flash({'title': "Warning", 'message': "Please Provide Correct OTP !<br>Register Again Please !"}, 'warning')
                return redirect("/Register")
        else:
            flash({'title': "Info", 'message': "Please Register first !"}, 'info')
            return redirect("/Register")
    

@App.route("/DA-1")
@App.route("/DA-2")
@App.route("/DA-3")
@App.route("/ML-1")
@App.route("/ML-2")
@App.route("/ML-3")
@App.route("/DL-1")
@App.route("/DL-2")
@App.route("/DL-3")
@login_required
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
        if contact_db.find_one(filter={'email' : f'{email}'}) == None:  
            if is_valid(email):
                contact_db.insert_one( {'date_time' : f'{datetime.now()}' , 'name' : f'{name}' , 'email' : f'{email}' , 'subject' : f'{subject}' , 'message' : f'{message}' } )
                send_email(name,email,subject,message)
                flash({'title': "Success", 'message': "Message Sent Successfully !"}, 'success')
            else:                
                flash({'title': "Error", 'message': "Please Provide A Working Email !"}, 'error')
            return redirect('/')
        else:
            flash({'title': "Information", 'message': "Message Already Sent Please Wait For Support !"}, 'info')
            return redirect('/')
    else:
        return False

@App.route("/User-Profile")
@login_required
def profile():
    return render_template("profile/user-profile.html")

@App.route("/User-Profile/Edit-Profile",methods=["GET","POST"])
@login_required
def edit_profile():
    if request.method=="GET":
        return redirect("/User-Profile")
    elif request.method=="POST":
        id = ObjectId(session['_user_id'])
        
        image,name,about,company,job,country,address,phone,twitter,facebook,instagram,linkedin,github = \
            request.files['image'],request.form['fullName'],request.form['about'],request.form['company'],\
            request.form['job'],request.form['country'],request.form['address'],request.form['phone'],\
            request.form['twitter'],request.form['facebook'],request.form['instagram'],request.form['linkedin'],request.form['github']
        
        image.save(f"static/assets/upload/{image.filename}")
        
        with open(f"static/assets/upload/{image.filename}", "rb") as imageFile:
            encoded_image = codecs.encode(imageFile.read(),encoding="base64")
        decoded_image=encoded_image.decode()
        
        auth_db.find_one_and_update(filter={'_id':id},
                                    update={'$set':{'image':f'{decoded_image}','name':f'{name}','about':f'{about}','company':f'{company}',
                                            'job':f'{job}','country':f'{country}','address':f'{address}','phone':f'{phone}',
                                            'twitter':f'{twitter}','facebook':f'{facebook}','instagram':f'{instagram}',
                                            'linkedin':f'{linkedin}','github':f'{github}'}})
        
        flash({'title': "Success", 'message': "Profile Updated Successfully!"}, 'success')
        return redirect("/User-Profile")

@App.route("/User-Profile/Edit-Password",methods=["GET","POST"])
@login_required
def edit_password():
    if request.method=="GET":
        return redirect("/User-Profile")
    elif request.method=="POST":
        current_password = request.form['password']
        new_password = bcrypt.generate_password_hash(request.form['newpassword']).decode()
        id = ObjectId(session['_user_id'])
        user = auth_db.find_one(filter={"_id":id})
        if user!=None:
            if bcrypt.check_password_hash(user['password'],current_password):
                auth_db.find_one_and_update(filter={"_id":id},update={'$set':{'password':f'{new_password}'}})
                flash({'title': "Success", 'message': "Password Changed Successfully!"}, 'success')
                return redirect("/User-Profile")
            else:
                flash({'title': "Error", 'message': "Wrong Current Password Entered !<br>Please Provide Correct Current Password."}, 'error')
                return redirect("/User-Profile")
        else:
            flash({'title': "Error", 'message': "Something Went Wrong"}, 'error')
            return redirect("/User-Profile")

# @App.route("/User-Profile/Edit-Settings",methods=["GET","POST"])
# @login_required
# def edit_notifications():
#     if request.method=="GET":
#         return redirect("/User-Profile/#profile-settings")
#     elif request.method=="POST":
#         id = ObjectId(session['_user_id'])
#         auth_db.find_one_and_update(filter={'_id':id},update={"$set":{'changesmade':f'{request.form["changesmade"]}','newproducts'}})

@App.route("/Logout")
@login_required
def logout():
    logout_user()
    flash({'title': "Success", 'message': "Logged Out Successfully !"}, 'success')
    return redirect('Login')

@App.errorhandler(404)
def not_found(error):
    return render_template("extra/404.html")

if __name__ == "__main__":
    if connection_result(client) == True :
        App.run(debug=True)
    else :
        print(connection_result(client))