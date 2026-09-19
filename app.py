from flask import Flask, render_template, request, redirect, url_for, session
from flask_caching import Cache
from mongodb_helper import MongoDBHelper
import hashlib
import google.generativeai as genai
import re
import pickle

app = Flask(__name__)

connection_string = "mongodb+srv://admin:kFCu0SxsdUEjxntU@cluster0.g17f64c.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
db_name = "sapienta"
helper = MongoDBHelper(connection_string, db_name)

app.config['SECRET_KEY'] = 'hari123'
cache = Cache(app, config={'CACHE_TYPE': 'redis',
              'CACHE_REDIS_URL': 'redis://localhost:6379/0'})

api_key = "AIzaSyDXWRRh5XQy9O0_PloCn2Y8PYdvTs_XW7A"
model_name = "gemini-pro"
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name)
model2 = pickle.load(open('model/xgboost.sav', 'rb'))

start = -1

Name = None
Location = None
Mark = None
Subject = None
Interest = None
Hobbies = None
Goal = None
Salary = None
job_study = None
Ambition = None


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




@app.route('/user/logout')
def logout():
    if 'user_id' in session.keys():
        session.pop('user_id', None)
        return render_template('/index.html')
    else:
        return render_template('/index.html')


@app.route("/user-login", methods=["POST", "GET"])
def user_login():
    if request.method == "POST":
        data = request.form
        collection_name_login = "login"

        user = helper.find_document(collection_name_login, {
                                    "email": data.get("username")})

        if not user or user["password"] != hashlib.sha256(data.get("password").encode()).hexdigest():
            return '''
                <script>
                alert('Incorrect login credentials!');
                window.location.href = '/';
                </script>
                '''

        session['user_id'] = data.get("username")
        if session['user_id'] == "admin@gmail.com":
            return '''
                <script>
                alert('Welcome Back!');
                window.location.href = '/admin/';
                </script>
                '''
        else:
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

        existing_user = helper.find_document(
            collection_name_login, {"email": data.get("username")})
        if existing_user:
            return '''
                <script>
                alert('Account already registered!');
                window.location.href = '/';
                </script>
                '''

        password_hash = hashlib.sha256(
            data.get("password").encode()).hexdigest()

        login_document = {
            "email": data.get("username"),
            "password": password_hash,
            "user_type": 2
        }

        login_id = helper.insert_document(
            collection_name_login, login_document)
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

        register_id = helper.insert_document(
            collection_name_register, register_document)
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

# admin


@app.route("/admin/")
def admin_index():
    if 'user_id' in session.keys():

        return render_template("admin/index.html", name="Admin")
    else:
        return render_template("index.html")


@app.route("/admin/users")
def admin_users():
    if 'user_id' in session.keys():
        pipeline_users = [
            {"$project": {"_id": 0}}  # Exclude _id field
        ]
        user_details = list(helper.aggregate("users", pipeline_users))
        return render_template("admin/users.html", name="Admin", res=user_details)
    else:
        return render_template("index.html")


@app.route("/admin/history")
def admin_history():
    if 'user_id' in session.keys():

        collection_name_login = "login"
        collection_name_users = "users"
        collection_name_predict = "predict"

        # Fetch prediction data with user's name
        pipeline_predict = [
            {"$lookup": {
                "from": "login",
                "localField": "user_id",
                "foreignField": "email",
                "as": "login_data"
            }},
            {"$unwind": {"path": "$login_data", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {
                "from": "users",
                "localField": "login_data._id",
                "foreignField": "user_id",
                "as": "user_data"
            }},
            {"$unwind": {"path": "$user_data", "preserveNullAndEmptyArrays": True}},
            {"$project": {
                "_id": 0,
                "user_name": "$user_data.name",
                # Include all fields from the predict table
                "label": 1,
                "os_percentage": 1,
                "algorithms_percentage": 1,
                "program_concept": 1,
                "software_engineering": 1,
                "cn_percentage": 1,
                "electronics_percentage": 1,
                "computerarch_percentage": 1,
                "maths_percentage": 1,
                "computer_skills": 1,
                "logical_rating": 1,
                "hackathons": 1,
                "coding_rating": 1,
                "public_speaking": 1,
                "timebeforesystem": 1,
                "selflearning": 1,
                "certificate": 1,
                "workshop": 1,
                "talenttests": 1,
                "memory-capability": 1,
                "interested_subject": 1,
                "type_of_company": 1,
                "m_or_t": 1,
                "h_or_s": 1,
                "in_teams": 1
                # Add more fields as needed
            }},
        ]

        predict_data = list(helper.aggregate("predict", pipeline_predict))

        print(predict_data)

        return render_template("admin/history.html", name="Admin", res=predict_data)

    else:
        return render_template("index.html")

# user


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
            user_login = helper.find_document(
                collection_name_login, {"email": email})
            if user_login:
                user_id = user_login.get("_id")
                result = helper.update_document(collection_name_register, {"user_id": user_id}, {
                                                "$set": {"phonenumber": new_phone}})

        pipeline = [
            {"$match": {"email": email}},
            {"$lookup": {
                "from": collection_name_register,
                "localField": "_id",
                "foreignField": "user_id",
                "as": "user_details"
            }},
            {"$unwind": "$user_details"},
            {"$project": {"_id": 0, "name": "$user_details.name",
                          "phonenumber": "$user_details.phonenumber"}},
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
    return render_template("user/predict.html", name=name)


@app.route("/user/predict_IT", methods=["POST", "GET"])
def predict_IT():
    if 'user_id' in session.keys():
        if request.method == "POST":
            data = request.form
            print(data)
            form_data_list = [[int(value) for key, value in data.items()]]

            print(form_data_list)
            res = model2.predict(form_data_list)

            user_id = session['user_id']
            document = {"user_id": user_id, "label": int(res[0])}
            for key, value in data.items():
                document[key] = int(value)

            print(document)
            collection_name_predict = "predict"
            helper.insert_document(collection_name_predict, document)

            return render_template("user/result.html", pred="it", response=res[0])
        else:
            return render_template("user/predict_IT.html")
    else:
        return render_template("index.html")


@app.route("/user/predict_NONIT", methods=["POST", "GET"])
def predict_NONIT():
    if 'user_id' in session.keys():
        if request.method == "POST":
            data = request.form

            Foreign = data.get("language")
            Art = data.get("art")
            English = data.get("english_percent")
            Financial = data.get("financial")
            Legal = data.get("legal")
            Client = data.get("client_roles")
            Team = data.get("independent")
            Dead = data.get("deadline")

            prompt = f"""
            Let's explore your skills, interests, and work preferences to find the perfect career fit for you.

            Do I have proficiency in foreign languages...yes in {Foreign} languages
            Do I have proficiency in creative skills such as design, art, or music...yes I have in {Art}
            My percentage in English language is {English}
            I have level {Financial} of understanding of financial concepts and accounting principles
            Am I familiar with legal regulations and compliance in relevant industries? {Legal }
            {Client} have communication and interpersonal skills for client-facing roles? 
            I am comfortable working {Team}
            I can handle working with {Dead}
            """

            chat = model.start_chat()
            response = chat.send_message(prompt)
            txt = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', response.text)
            txt = txt.replace("* ", "<br>")

            return render_template("user/result.html", pred="non", response=txt)
        else:
            return render_template("user/predict_NONIT.html")
    else:
        return render_template("index.html")


@app.route("/user/chatbot")
def chatbot():
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
    return render_template("user/chatbot.html", name=name)


@app.route("/user/history")
def history():
    email = session['user_id']
    collection_name_predict = "predict"
    collection_name_login = "login"
    collection_name_users = "users"

    pipeline = [
        {"$match": {"email": email}},
        {"$lookup": {
            "from": collection_name_users,
            "localField": "_id",
            "foreignField": "user_id",
            "as": "user_data"
        }},
        {"$unwind": "$user_data"},
        {"$project": {"_id": 0, "user_name": "$user_data.name"}}
    ]

    result_cursor = helper.aggregate(collection_name_login, pipeline)
    result_list = list(result_cursor)

    # Extracting name from the result
    name = result_list[0]["user_name"] if result_list else None

    # Fetching prediction data
    pipeline_predict = [
        {"$match": {"user_id": email}}
    ]
    result_predict_cursor = helper.aggregate(
        collection_name_predict, pipeline_predict)
    predict_data = list(result_predict_cursor)

    return render_template("user/history.html", name=name, res=predict_data)


@app.route("/chat", methods=["POST", "GET"])
def chat():
    global start, Name, Location, Mark, Subject, Interest, Hobbies, Goal, Salary, job_study, Ambition
    if request.method == "POST":
        input = request.form['input']
        if input.lower() == "hi" and start == -1:
            start += 2
            return "Welcome to the Career Assistant Bot!\nwhat is your name?"
        elif start == 1:
            start += 1
            Name = input
            return "In which city are you located?"
        elif start == 2:
            start += 1
            Location = input
            return "What was your percentage in 12th standard?"
        elif start == 3:
            start += 1
            Mark = input
            return "What subjects did you excel in during 12th standard?"
        elif start == 4:
            start += 1
            Subject = input
            return "What topics or activities do you find interesting?"
        elif start == 5:
            start += 1
            Interest = input
            return "What do you like to do in your free time?"
        elif start == 6:
            start += 1
            Hobbies = input
            return "What do you want to achieve in your career?"
        elif start == 7:
            start += 1
            Goal = input
            return "Do you want a job that pays well? (y/n)"
        elif start == 8:
            start += 1
            Salary = input
            return "Do you plan to pursue higher studies or enter the job market?"
        elif start == 9:
            start += 1
            job_study = input
            return "What do you think you'd like to work in the future (Ambition)?"
        elif start == 10:
            start += 1
            Ambition = input

            career_start = f"""
                Let's explore your academic achievements, interests, and career aspirations to find the perfect higher studies course and college for you. Your Name is {Name}

                You are located in {Location} and achieved {Mark}% in your 12th standard exams. It's great to know that you excelled in {Subject} compared to other subjects.

                You are interested in {Interest} and enjoy {Hobbies} in your free time. Your career goal is to {Goal}, with a preference for a high-paying job. Currently, you are considering {job_study} and aspire to work as a {Ambition} in the future. A good salary is important to you, and you're willing to relocate if necessary.

                Considering your academic performance and interests, as well as your career aspirations, let's explore suitable higher studies courses that align with your profile and recommend reputable colleges in your {Location}.
                """
            chat = model.start_chat()
            response = chat.send_message(career_start)

            txt = response.text.replace(" * ", "<br>")
            txt = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', txt)
            return txt
    else:
        return "error"


# @app.errorhandler(404)
# def not_found(error):
#     return render_template('user/404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)
