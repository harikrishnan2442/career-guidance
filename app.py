from flask import Flask, render_template, request, redirect, url_for, session
from flask_caching import Cache
from mongodb_helper import MongoDBHelper
import hashlib 

app = Flask(__name__)

connection_string = "mongodb+srv://admin:kFCu0SxsdUEjxntU@cluster0.g17f64c.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
db_name = "sapienta"
helper = MongoDBHelper(connection_string, db_name)

app.config['SECRET_KEY'] = 'hari123'
cache = Cache(app, config={'CACHE_TYPE': 'redis','CACHE_REDIS_URL': 'redis://localhost:6379/0'})

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/send_message")
def send_message():
    return render_template("contact.html")

@app.route("/user-login", methods=["POST", "GET"])
def user_login():
     if request.method == "POST":
        data = request.form
        collection_name_login = "login" 

        user = helper.find_document(collection_name_login, {"email": data.get("username")})

        if not user or user["password"] != hashlib.sha256(data.get("password").encode()).hexdigest():
            return '''
                <script>
                alert('Incorrect login credentials!');
                window.location.href = '/';
                </script>
                '''
        
        session['user_id'] = data.get("username")
        return '''
                <script>
                alert('Welcome Back!');
                window.location.href = '/user/';
                </script>
                '''
     else:
        return render_template("user-login.html")

@app.route("/user-reg", methods=["POST", "GET"])
def user_reg():
    if request.method == "POST":
        data = request.form
        collection_name_login = "login"  
        collection_name_register = "users" 
        
        existing_user = helper.find_document(collection_name_login, {"email": data.get("username")})
        if existing_user:
            return '''
                <script>
                alert('Account already registered!');
                window.location.href = '/';
                </script>
                '''
        
        password_hash = hashlib.sha256(data.get("password").encode()).hexdigest()

        login_document = {
            "email": data.get("username"),
            "password": password_hash
        }
        
       
        login_id = helper.insert_document(collection_name_login, login_document)
        if not login_id:
            return '''
                <script>
                alert('Error registration!');
                window.location.href = '/';
                </script>
                '''

        
        register_document = {
            "name": data.get("name"),
            "phonenumber": data.get("number"),
            "user_id": login_id  
        }
        
        register_id = helper.insert_document(collection_name_register, register_document)
        if not register_id:
            
            helper.delete_document(collection_name_login, {"_id": login_id})
            return '''
                <script>
                alert('Error registration!');
                window.location.href = '/';
                </script>
                '''
        else:
            return '''
                <script>
                alert('Registered successfully!');
                window.location.href = '/';
                </script>
                '''
    else:
        return render_template("user-reg.html")

#user

@app.route("/user/")
def user_index():
    if 'user_id' in session.keys():
        email = session['user_id']
        collection_name_login = "login"
        collection_name_register = "users"
        pipeline = [
            {"$match": {"email": email}},
            {"$lookup": {
                "from": collection_name_register,
                "localField": "_id",
                "foreignField": "user_id",
                "as": "user_details"
            }},
            {"$unwind": "$user_details"},
            {"$project": {"_id": 0, "name": "$user_details.name"}},
            {"$limit": 1} 
        ]

        user_details_cursor = helper.aggregate(collection_name_login, pipeline)
        user_details = next(user_details_cursor, None)
        name = user_details.get("name")
        return render_template("user/index.html", name=name)
    else:
        return render_template("index.html")


@app.route("/user/profile", methods=["POST", "GET"])
def profile():
    if 'user_id' in session.keys():
        email = session['user_id']
        collection_name_login = "login"
        collection_name_register = "users"
        
        if request.method == "POST":
            new_phone = request.form.get("phone")
            user_login = helper.find_document(collection_name_login, {"email": email})
            if user_login:
                user_id = user_login.get("_id")
                result = helper.update_document(collection_name_register, {"user_id": user_id}, {"$set": {"phonenumber": new_phone}})
                
                
        pipeline = [
            {"$match": {"email": email}},
            {"$lookup": {
                "from": collection_name_register,
                "localField": "_id",
                "foreignField": "user_id",
                "as": "user_details"
            }},
            {"$unwind": "$user_details"},
            {"$project": {"_id": 0, "name": "$user_details.name", "phonenumber": "$user_details.phonenumber"}},
            {"$limit": 1} 
        ]

        user_details_cursor = helper.aggregate(collection_name_login, pipeline)
        user_details = next(user_details_cursor, None)
        name = user_details.get("name")
        phone = user_details.get("phonenumber")
        return render_template("user/profile.html", name=name, email=email, phone=phone)
    else:
        return render_template("index.html")

@app.route("/user/predict")
def predict():
    return render_template("user/predict.html")


@app.errorhandler(404)
def not_found(error):
    return render_template('user/404.html'), 404

if __name__ == "__main__":
    app.run(debug=True)
