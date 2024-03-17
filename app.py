from flask import Flask, render_template, request, redirect, url_for
from mongodb_helper import MongoDBHelper
import hashlib 

app = Flask(__name__)

connection_string = "mongodb+srv://admin:kFCu0SxsdUEjxntU@cluster0.g17f64c.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
db_name = "sapienta"
helper = MongoDBHelper(connection_string, db_name)

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

@app.route("/user/")
def user_index():
    return render_template("user/index.html")




@app.errorhandler(404)
def not_found(error):
    return render_template('user/404.html'), 404

if __name__ == "__main__":
    app.run(debug=True)
