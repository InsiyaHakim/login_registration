from flask import Flask,request,redirect,render_template,session,flash
from mysqlconnection import MySQLConnector
import md5
import re
import datetime
import string
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app=Flask(__name__)
app.secret_key='jdldnhd'
mysql=MySQLConnector(app,'login_reg')
list=[]
list2=[]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/insert',methods=['POST'])
def insert():

    list=[]
    list2=[]

    first_name=str(request.form['first_name'])
    f_name=str.isalpha(first_name)

    last_name = str(request.form['last_name'])
    l_name = str.isalpha(last_name)

    email=request.form['email']
    password=request.form['password']
    c_password=request.form['c_password']

    if f_name == False or l_name == False:
        list.append("First and Last name shouldn't have any numeric value(s)")
    if len(first_name) <= 1 :
        list.append("First name must be ateast 2 characters")
    if len(last_name) <= 1 :
        list.append("Last name must be ateast 2 characters")
    if not EMAIL_REGEX.match(email):
        list.append("Your Email has to be written in proper email format")
    if len(password)<8:
        list.append("Your Password must be above eight characters")
    if password != c_password:
        list.append("Your Password must match")

    query='SELECT email FROM registration WHERE email = :selected_email'
    data={
        'selected_email':email
    }
    db=mysql.query_db(query,data)
    if len(db)>0:
        list.append("This email is already used by another user")

    if len(list)>0:
        return render_template('index.html',list=list)
    else:
        hashed_pw=md5.new(request.form['password']).hexdigest()
        query='INSERT INTO registration (first_name,last_name,email,password,created_at) VALUES (:first_name,:last_name,:email,:password,NOW())'
        data={
            'first_name': string.capwords(first_name),
            'last_name': string.capwords(last_name),
            'email': email,
            'password': hashed_pw
        }
        mysql.query_db(query,data)
        return render_template('login_page.html')


@app.route('/login_page')
def login_page():
    return render_template('login_page.html')


@app.route('/login',methods=['POST'])
def login():
    email=request.form['email']
    password=md5.new(request.form['password']).hexdigest()
    query='SELECT * FROM registration where email=:email and password=:password'
    data={
        'email':email,
        'password':password
    }
    db=mysql.query_db(query,data)
    if len(db)>0:
        for entry in db:
            id=entry['id']
        session['user_id']=id

        return render_template('success.html',user_data=message_query(),user_comments=comment_query(),db_name=name_display_on_everypage())
    else:
        list2.append('The Email is incorrect')
        return render_template('login_page.html',list=list2)


@app.route('/<id>/logout')
def logout(id):
    #session['user_id']=''
    session.clear()
    return redirect('/')



@app.route('/<u_id>/message',methods=['POST'])
def message(u_id):
    message=str(request.form['message'])
    if len(message)!=0:
        query='INSERT INTO messages(user_id,messages,created_at)VALUES(:u_id,:messages,NOW())'
        data={
            'u_id':u_id,
            'messages':message
        }
        mysql.query_db(query,data)

        return render_template('success.html', user_data=message_query(),db_name=name_display_on_everypage())
    else:
        return render_template('success.html', user_data=message_query(), user_comments=comment_query(),empty_message="Empty Message cannot be send!!!!",db_name=name_display_on_everypage())


@app.route('/<user_id>/<message_id>/comment',methods=['POST'])
def comment(user_id,message_id):
    comment=request.form['comments']
    if len(comment)!=0:
        query='INSERT INTO comments (message_id,user_id,comment,created_at) VALUES (:message_id,:user_id,:comment,NOW())'
        data={
            'message_id':message_id,
            'user_id':user_id,
            'comment':comment
        }
        mysql.query_db(query,data)

        return render_template('success.html', user_data=message_query(), user_comments=comment_query(),db_name=name_display_on_everypage())
    else:
        return render_template('success.html', user_data=message_query(), user_comments=comment_query(),empty_comment="Empty Comment cannot be send!!!!",db_name=name_display_on_everypage())

@app.route('/<message_id>/<u_id>/delete')
def delete(message_id,u_id):
    query='DELETE FROM messages WHERE user_id=:u_id and id=:message_id'
    data={
        'u_id':u_id,
        'message_id':message_id
    }
    mysql.query_db(query,data)
    return render_template('success.html', user_data=message_query(), user_comments=comment_query(),db_name=name_display_on_everypage())



def message_query():
    query = 'SELECT registration.first_name,registration.last_name,messages.id as id,messages.messages,messages.user_id as user_id,messages.created_at FROM registration join messages on registration.id=messages.user_id  ORDER BY messages.id DESC '
    data = {
        'id': session['user_id']
    }
    db = mysql.query_db(query, data)
    for msg in db:
        if 4 <= int(msg['created_at'].strftime('%d')) <= 20 or 24 <= int(msg['created_at'].strftime('%d')) <= 30:
            suffix = "th"
            msg['created_at'] = msg['created_at'].strftime('%b')+" "+msg['created_at'].strftime('%d')+suffix+" "+msg['created_at'].strftime('%y')
        else:
            suffix = ["st", "nd", "rd"][int(msg['created_at'].strftime('%d')) % 10 - 1]
            msg['created_at'] = msg['created_at'].strftime('%b')+" "+msg['created_at'].strftime('%d')+suffix+" "+msg['created_at'].strftime('%y')
    return db

def comment_query():
    query = 'select registration.id as reg_id ,registration.first_name as First,registration.last_name as Last,comments.created_at as Created_at,comments.comment as Comments, comments.message_id as comment_Message_id, comments.user_id as User_id from registration join comments on comments.user_id=registration.id'
    db_comment = mysql.query_db(query)
    for msg in db_comment:
        if 4 <= int(msg['Created_at'].strftime('%d')) <= 20 or 24 <= int(msg['Created_at'].strftime('%d')) <= 30:
            suffix = "th"
            msg['Created_at'] = msg['Created_at'].strftime('%b')+" "+msg['Created_at'].strftime('%d')+suffix+" "+msg['Created_at'].strftime('%y')
        else:
            suffix = ["st", "nd", "rd"][int(msg['Created_at'].strftime('%d')) % 10 - 1]
            msg['Created_at'] = msg['Created_at'].strftime('%b')+" "+msg['Created_at'].strftime('%d')+suffix+" "+msg['Created_at'].strftime('%y')
    return db_comment

def name_display_on_everypage():
    query = 'select first_name,last_name from registration where id=:id'
    data = {
        'id': session['user_id']
    }
    db_name = mysql.query_db(query, data)
    return db_name




app.run(debug=True)