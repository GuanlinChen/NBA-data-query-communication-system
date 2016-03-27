#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following uses the sqlite3 database test.db -- you can use this for debugging purposes
# However for the project you will need to connect to your Part 2 database in order to use the
# data
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@w4111db.eastus.cloudapp.azure.com/username
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@w4111db.eastus.cloudapp.azure.com/ewu2493"
#
DATABASEURI = "postgresql://gc2666:PZVNPF@w4111db.eastus.cloudapp.azure.com/gc2666"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


#
# START SQLITE SETUP CODE
#
# after these statements run, you should see a file test.db in your webserver/ directory
# this is a sqlite database that you can query like psql typing in the shell command line:
# 
#     sqlite3 test.db
#
# The following sqlite3 commands may be useful:
# 
#     .tables               -- will list the tables in the database
#     .schema <tablename>   -- print CREATE TABLE statement for table
# 
# The setup code should be deleted once you switch to using the Part 2 postgresql database
#


#engine.execute("""DROP TABLE IF EXISTS test;""")
#engine.execute("""CREATE TABLE IF NOT EXISTS Account ( 
#userid int, 
#username text,
#password text,
#email text,
#blockflag int ,
#PRIMARY KEY(userid));""")
#gc2666 = "gc2666"
#id = 2
#query = """INSERT INTO Account(userid, username, password, email, blockflag) VALUES ('{0}', '{1}', 'gc2666', 'gc2666@columbia.edu', 0);""".format(id, gc2666)
#engine.execute(query)
#
# END SQLITE SETUP CODE
#



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  #print 'request args is:', request.args


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT username, password FROM Account")
  user_info = {}
  for result in cursor:
    user_info[result['username']] = result['password']
     
  #print user_info  # can also be accessed using result[0]
  cursor.close()
  

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = user_info.keys())
  #in_username = request.form['username']
  #print 'the username is ', username
  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#

#The data mainpage
@app.route('/data')
def data():
  cursor = g.conn.execute("select * from player")
  player_dict = {}
  for result in cursor:
    player_dict[result['pname']] = result['pdata']
  #print player_dict
  cursor.close()
  #player = request.form['player']
  #print 'the input is %s' % player
  #if player in player_dict.keys():
  #  weburl = "/player/%s" % player
  #  return redirect(weburl)
 
  return render_template("data.html")


@app.route('/get_player', methods=['POST'])
def get_player():
  player = request.form['player']
  weburl = "/player/%s" % player
  return redirect(weburl)

@app.route('/get_team', methods=['POST'])
def get_team():
  team = request.form['team']
  weburl = "/team/%s" % team
  return redirect(weburl)

@app.route('/player/<player>')
def player(player):
  cursor = g.conn.execute("select * from player")
  player_dict = {}
  for result in cursor:
    player_dict[result['pname']] = result['pdata']
  #print player_dict
  cursor.close()
  context = {}
  context['name'] = player
  context['score'] = player_dict[player][0]
  context['rebound'] = player_dict[player][1]
  context['assists'] = player_dict[player][2]
  return render_template("player.html", **context)

@app.route('/team/<team>')
def team(team):
  cursor = g.conn.execute("select * from team")
  team_dict = {}
  for result in cursor:
    team_dict[result['tname']] = result['location']
    #print result['tname'], result['location']
  cursor.close()
  context = {}
  context['name'] = team
  context['location'] = 'Houston'
  #print context
  return render_template("team.html", **context)

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test VALUES (NULL, ?)', name)
  return redirect('/')

@app.route('/login', methods=['POST'])
def login():
  cursor = g.conn.execute("SELECT username, password FROM Account")
  user_info = {}
  for result in cursor:
    user_info[result['username']] = result['password']
     
  #print user_info  # can also be accessed using result[0]
  cursor.close()


  username = request.form['username']
  #print username
  password = request.form['password']
  #print password
  #print user_info
  for i in user_info.keys():
    if i == str(username) and user_info[i] == str(password):
      print 'Welcome %s' % username
      
      weburl = '/mainpage/%s' % username
      return redirect(weburl)
      #return render_template("main_page.html", **context)
  return redirect('/')

@app.route('/mainpage/<username>')
def mainpage(username):
  print username, 'is in this page'
  context = dict(data = username)
  return render_template("main_page.html", **context)

"""@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()
"""

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
