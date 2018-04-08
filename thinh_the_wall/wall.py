from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
import md5
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
name_check = re.compile(r'^[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = "wall"
mysql = MySQLConnector(app,'the_wall')
@app.route('/')
def index():
    
    return render_template('index_wall.html')


@app.route('/logout')
def logout():
    session['logged_in_id'] = 0

    return redirect('/')

@app.route('/check', methods=['POST'])
def create():
    count = 0
    if len(request.form['fname']) < 0:
        flash("first name cannot be empty")
    else:
        if not name_check.match(request.form['fname']):
            flash("first name can only contain letters")
        else:
            count += 1
    if len(request.form['lname']) < 1:
        flash("last name cannot be empty")
    else:
        if not name_check.match(request.form['lname']):
            flash("last name can only contain letters")
        else:
            count += 1
    if len(request.form['email']) < 1:
        flash("email cannot be empty")
    else:
        if not EMAIL_REGEX.match(request.form['email']):
            flash("invalid email")
        else:
            count += 1
    if len(request.form['pass']) < 1 or len(request.form['repass']) < 1:
        flash("password cannot be empty")
    else:
        if request.form['pass'] != request.form['repass']:
            flash("passwords do not match")
        else:
            count += 1

    if count == 4:
        hashpass = md5.new(request.form['pass']).hexdigest()
        query = "INSERT INTO users (fname, lname, email, password) VALUES (:fname, :lname, :email, :password)"
        data = {
             'fname': request.form['fname'],
             'lname':  request.form['lname'],
             'email': request.form['email'],
             'password': hashpass
            
           }
        mysql.query_db(query, data)
        return redirect('/wall')
    return redirect('/')

@app.route('/logcheck', methods=['POST'])
def check():
    query = "SELECT * FROM users WHERE users.email = :email AND users.password = :password"
    data = {
        'email': request.form['useremail'],
        'password': md5.new(request.form['passcheck']).hexdigest()
    }
    email = mysql.query_db(query, data)

    
    # print msgsql[0]['message']
    
    session['loggedName'] = email
    
    if len(email) > 0:
        return redirect('/wall')
    else: 
        flash("incorrect log in")

    return redirect('/')




@app.route('/process', methods=['POST'])
def process():
    

    query = "INSERT INTO messages (message, user_id) VALUES (:newmesg, :loginid)"
    data ={
        "newmesg": request.form['message'],
        "loginid": session['loggedName'][0]['id']
    }
    dismesg = mysql.query_db(query, data)

    querymsg = "SELECT * FROM messages"
    msgsql = mysql.query_db(querymsg)
    session['message'] = msgsql

   
    
    return redirect('/wall')


@app.route('/comment', methods=['POST'])
def comment():
    query ="INSERT INTO comments (comment, user_id, message_id) VALUES (:vcomment, :vuserid, :vmsgid)"
    data ={
        "vcomment": request.form['comment'],
        "vuserid": session['loggedName'][0]['id'],
        "vmsgid" : request.form['hcomment']
    }
    mysql.query_db(query, data)
    

    queryone = "SELECT messages.id AS msid, message, comment, comments.created_at AS created, comments.message_id AS mscmid, comments.user_id AS usercmnt, CONCAT(fname, ' ', lname) AS username FROM messages JOIN comments ON messages.id = comments.message_id JOIN users ON messages.user_id = users.id"
    sql = mysql.query_db(queryone)
    session['cmnt'] = sql
    #print mysql.query_db(queryone)

    return redirect('/wall')


@app.route('/wall')
def show():
    queryjoin = "SELECT message, messages.created_at, messages.id AS msid, CONCAT(fname, ' ', lname) AS name FROM messages JOIN users ON messages.user_id = users.id"
    msfnjoin = mysql.query_db(queryjoin)
    session['msfnjoin'] = msfnjoin


    return render_template("/wall.html", disname=session['loggedName'], pdismesg=session['message'], hmsfnjoin=session['msfnjoin'], cmnt = session['cmnt'])

app.run(debug=True)
