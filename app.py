from flask import Flask,render_template,request
from static.forms.contact import send_email,is_valid
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

load_dotenv()
uri = os.environ.get("MONGODB_URI")
client = MongoClient(uri, server_api=ServerApi('1'))

App = Flask(__name__)
App.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")


def connection_result(client):
    try:
        client.admin.command('ping')
        return True
    except  Exception as e :
        return e

@App.route("/")
def home():
    return render_template("main/index.html")

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
        database = client.get_database("Contact")
        collection = database.get_collection("users")
        if collection.find_one(filter={'email' : f'{email}'}) == None:          
            if is_valid(email):
                collection.insert_one( {'date_time' : f'{datetime.now()}' , 'name' : f'{name}' , 'email' : f'{email}' , 'subject' : f'{subject}' , 'message' : f'{message}' } )
                sent = send_email(name,email,subject,message,other=True)
            else:
                sent = False
            return render_template("contact/contact_result.html",value=sent)
        else:
            sent = 'old'
            return render_template("contact/contact_result.html",value=sent)
    else:
        return False

@App.route("/Login")
def login():
    return render_template("/extra/login.html")

@App.route("/Login-Validation",methods=["GET","POST"])
def login_validation():
    if request.method=="POST":
        username = request.form['username']
        password = request.form['password']
        try:
            remember = request.form['remember']
        except:
            remember = False
            
        return f"User Name : {username}<br>Password : {password}<br>Remember Me : {remember}<br>"

if __name__ == "__main__":
    if connection_result(client) == True :
        App.run(debug=os.environ.get("DEBUG"))
    else :
        print(connection_result(client))