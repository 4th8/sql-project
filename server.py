import os, datetime
import psycopg2
import uuid
from flask import Flask, session, request, redirect, url_for, render_template
import psycopg2.extras
from flask.ext.socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.secret_key= os.urandom(24).encode('hex')

socketio = SocketIO(app)

date = {'year' : "2016", "month" : "September", "dayOfWeek" : "Saturday", 'day' : '3'}
past = False
if datetime.datetime.today() > datetime.datetime(2016, 9 , 3):
    past = True
thenames = ['Nathan Woodhead','Heather Burgess']

regesteredGuests = [{'Name' : 'Nathan Woodhead', 'Phone' : 5408548888, 'Address' : "301 cracked street",'numGuests' : 10}]

@socketio.on('createNewRoom', namespace='/chat')
def createNewRoom(username, roomname):
  conn= connectToMessageDB()
  cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
  cur.execute("SELECT * FROM rooms WHERE roomname = %s", (roomname,))
  if cur.fetchone():
    emit('roomExists')
  else:
    cur.execute("INSERT INTO rooms (roomname, username) VALUES (%s, %s);" ,(roomname, username))
    conn.commit()
    emit('rooms', roomname, broadcast = all)

def autoLogin(username):
  session['username'] = username

@app.route('/createAccount', methods = ['POST', 'GET'])
def loadCreatePage():
  if 'username' in session:
    username = session['username']
    return render_template('createAccount.html', username = username, responseText = '')
  else:
    return render_template('createAccount.html', username = 'Not logged in', responseText = '')
    
@app.route('/newaccount', methods=['POST','GET'])
def createNewAccount():
  username = ''
  if 'username' in session:
    username = session['username']
  conn= connectToUserDB()
  cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
  username = request.form['user']
  pw = request.form['password']
  if username == '':
    return render_template('createAccount.html', username = username, responseText = 'Please enter a username')
  cur.execute("SELECT * FROM users WHERE username = %s;" , (username,))
  if cur.fetchone():
    return render_template('createAccount.html', username = username, responseText = 'That username is already taken')
  if pw == '':
    return render_template('createAccount.html', username = username, responseText = 'Please enter a password')
  cur.execute("INSERT INTO users (username, password) VALUES(%s, crypt(%s, gen_salt('bf')));" , (username, pw))
  conn.commit()
  autoLogin(username)
  return render_template('index.html', username = username, date=date, past = past)
  

@socketio.on('createChat', namespace='/chat')
def loginChat():
  print('Trying to pass username to socketio')
  if 'username' in session:
    emit('loginChat', session['username'])
  else:
    emit('login', '')

@socketio.on('join')
def on_join():
    username = data['username']
    room = data['room']
    join_room(room)
    send(username + ' has entered the room.', room=room)

@socketio.on('leave')
def on_leave():
    username = session['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', room=room)

@socketio.on('search', namespace='/chat')
def search(text):
  conn= connectToMessageDB()
  cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
  searchtext = '%' + text + '%'
  cur.execute("SELECT * FROM messages WHERE message LIKE %s OR username LIKE %s;" ,(searchtext, searchtext))
  results = cur.fetchall()
  for result in results:
    print(result)
    emit ('search', result)

@socketio.on('connect', namespace='/chat')
def makeConnection():
    conn = connectToMessageDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM messages;")
    messages = cur.fetchall()
    session['uuid'] = uuid.uuid1()
    for message in messages:
        emit('message', message)
      

@socketio.on('chat', namespace='/chat')
def chat(text, username):
  print(text)
  conn = connectToMessageDB()
  cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
  cur.execute("INSERT INTO messages (username, message) VALUES (%s, %s);" , (username, text))
  conn.commit()
  message = [username , text]
  emit('message', message, broadcast = all)

def connectToDB():
#  connectionString = 'dbname=music user=postgres password=kirbyk9 host=localhost'
  connectionString = 'dbname=wedding user=admin password=0328940 host=localhost'
  try:
    return psycopg2.connect(connectionString)
  except:
    print("Can't connect to database")

def connectToUserDB():
#  connectionString = 'dbname=music user=postgres password=kirbyk9 host=localhost'
  connectionString = 'dbname=wedding user=usercontrol password=0328940 host=localhost'
  try:
    return psycopg2.connect(connectionString)
  except:
    print("Can't connect to database")
    
def connectToMessageDB():
#  connectionString = 'dbname=music user=postgres password=kirbyk9 host=localhost'
  connectionString = 'dbname=wedding user=messagecontrol password=0328940 host=localhost'
  try:
    return psycopg2.connect(connectionString)
  except:
    print("Can't connect to database")
    
@app.route('/logintry', methods =['POST'])
def login():
    conn = connectToUserDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    pw = request.form['password']
    username = request.form['user']
    cur.execute("select * from users WHERE username = %s AND password = crypt(%s, password);" , (username, pw))
    if cur.fetchone():
      print('Login successful as ' + username)
      session['username'] = username
      return render_template('index.html', username=username, date=date, past=past)
    else:
      return render_template('login.html', username = 'Not logged in', feedback = 'Invalid username and password')
    
    
@app.route('/')
def mainIndex():
  if 'username' in session:
    username = session['username']
    print('Username: ' , session['username'])
  else:
    username = 'Not Logged in'
  return render_template('index.html',date=date, past=past, username=username)
	
@app.route('/bridal')
def apage():
  if session.has_key('username'):
      username = session['username']
  else:
    username = 'Not Logged in'
  return render_template('bridalParty.html', username=username)

@app.route('/login')
def loginPage():
  if 'username' in session:
      username = session['username']
  else:
    username = 'Not Logged in'
  return render_template('login.html', username=username, feedback = '')

@app.route('/countdown')
def count():
    if 'username' in session:
      username = session['username']
    else:
      username = 'Not Logged in'
    diff = datetime.datetime(2016, 9, 3) - datetime.datetime.today()
    days = diff.days
    return render_template('countdown.html', dayz=days, date=date, past=past, username=username)
    
@app.route('/chat')
def chatPage():
  if 'username' in session:
      username = session['username']
  else:
    username = 'Not Logged in'
  return render_template('chat.html', username=username)

@app.route('/registry')
def stuff():
  if 'username' in session:
      username = session['username']
  else:
    username = 'Not Logged in'
    want = ['http://store.ssgtactical.com/product.iwi-us-inc-tavor-semi-automatic-9mm-17-black-bullpup-1-mag-32rd-adjustable-sights-tsb17-9-34', 'http://store.ssgtactical.com/product.century-arms-international-922r-fury-12-gauge-semi-auto-1-10rd-us-24', 'http://store.ssgtactical.com/product.kimber-solo-carry-9mm-1039']
    return render_template('registry.html', iwant = want, username=username)
    
@app.route('/rsvp', methods=['POST', 'GET'])
def rsvp():
  if 'username' in session:
      username = session['username']
  else:
    username = 'Not Logged in'
  conn = connectToDB()
  cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
  if request.method == 'POST':
    try:
      cur.execute("""INSERT INTO list (name, phone, address, numberofguests) 
       VALUES (%s, %s, %s, %s);""",
       (request.form['name'], request.form['phone'], request.form['address'], request.form['num']) )
      
      
    except:
      print "Error inserting into list"
      conn.rollback()
        
    conn.commit()
  try:
    cur.execute("select name from list")
    
  except:
    print("Error executing select")
  results = cur.fetchall()
  print "FACTORY"
  print results
  return render_template('rsvp.html', guests=results, username=username)
  
  
  
  
      
# start the server
if __name__ == '__main__':
        socketio.run(app, host=os.getenv('IP', '0.0.0.0'), port =int(os.getenv('PORT', 8080)), debug=True)