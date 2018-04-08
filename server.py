from flask import Flask, render_template, request, redirect, flash, session
from mysqlconnection import MySQLConnector
import re 
import md5

app = Flask(__name__)
app.secret_key = 'key'
mysql = MySQLConnector(app,'thewalldb')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'^[a-zA-Z]+$')

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/logout')
def logout():
    session["log"] = 0
    
    return redirect("/")


@app.route('/registration', methods=['POST'])
def create():
    count = 0
    if len(request.form['email']) < 1:
        flash("Email cannot be empty!")
        
    elif not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email!")
        
    else:
        email = request.form['email']
        count+=1

    if len(request.form['first_name']) < 2 and len(request.form['last_name']) < 2 :
        flash("has to be greater than 2") 
    else:
        if not NAME_REGEX.match(request.form['first_name']) or not NAME_REGEX.match(request.form['last_name']):
            flash("Invalid name!")
        
        else:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            count+=1
        
    if len(request.form['password']) < 1 or len(request.form['password']) < 8:
        flash("Password cannot be empty or needs to be at least 8 characters long!")
        
    else:
        if request.form['password'] != request.form['password2']:
            flash("Passwords need to match!")
            
        elif request.form['password'] == request.form['password2']:  
            count+=1
            password = request.form['password']
            password2 = request.form['password2']

    
    if count == 3:
        query = "INSERT INTO users (first_name, last_name, email, password, created_at) VALUES (:first_name, :last_name, :email, :password, NOW())"
        password = md5.new(request.form['password']).hexdigest()
        data = {
                'email': request.form['email'],
                'first_name': request.form['first_name'],
                'last_name': request.form['last_name'],
                'password': password
           }
        mysql.query_db(query, data)
        return redirect("/success")
    
    return redirect('/')

@app.route('/login', methods=['POST'])
def log():
    query = "SELECT * FROM users WHERE users.email = :email AND users.password = :password"
    password = md5.new(request.form['password']).hexdigest()
    data = {
             'email': request.form['email'],
             'password': password
           }
    log = mysql.query_db(query, data)
    session['log'] = log

    
    if len(log) > 0:   
        return redirect("/success")
    else:
        flash("Email or Password is not valid!")
    return redirect("/",)


@app.route('/wall', methods=["POST"])
def write_message():
    mquery = "INSERT INTO messages (message, user_id) VALUES (:message, :sessionid)"
    mdata = {
                "message": request.form['message'],
                "sessionid": session['log'][0]['id']
        }
    m_id = mysql.query_db(mquery, mdata)


    session['m_id'] = m_id

    return redirect("/success")


@app.route('/comment', methods=["POST"])
def write_comment():
    cquery = "INSERT INTO comments (comment,  message_id, user_id) VALUES (:comment, :mess_id, :us_id)"
    cdata = {
                "comment": request.form['comment'],
                "mess_id": request.form['hcomment'],
                "us_id": session['log'][0]['id']
        }
    mysql.query_db(cquery, cdata)

    
    
   
    return redirect("/success")



@app.route('/success')
def success():
    mquery = "SELECT message, messages.created_at, messages.id AS msid, CONCAT(first_name, ' ', last_name) AS name FROM messages JOIN users ON messages.user_id = users.id"
    msgsql = mysql.query_db(mquery)
    session['message'] = msgsql
    
    showquery = "SELECT messages.id AS msid, message, comment, comments.created_at AS created, comments.message_id AS mscmid, comments.user_id AS usercmnt, CONCAT(first_name, ' ', last_name) AS username FROM messages JOIN comments ON messages.id = comments.message_id JOIN users ON messages.user_id = users.id"
    showsql = mysql.query_db(showquery)
   
    
    return render_template("success.html", name=session['log'][0]['first_name'], msg = session['message'], showsql=showsql)




    


app.run(debug=True) # run our server