import cherrypy
from jinja2 import Environment, PackageLoader, select_autoescape
import os
from datetime import datetime
import sqlite3
from sqlite3 import Error
import json

class WebApp(object):
    dbsqlite = 'data/db.sqlite3'
    dbjson = 'data/db.json'

    def __init__(self):
        self.env = Environment(
                loader=PackageLoader('webapp', 'html'),
                autoescape=select_autoescape(['html', 'xml'])
                )

    ########################################################################################################################
    # Utilities

    def set_user(self, username=None):
        if username == None:
            cherrypy.session['user'] = {'is_authenticated': False, 'username': ''}
        else:
            cherrypy.session['user'] = {'is_authenticated': True, 'username': username}

    def get_user(self):
        if not 'user' in cherrypy.session:
            self.set_user()
        return cherrypy.session['user']

    def render(self, tpg, tps):
        template = self.env.get_template(tpg)
        return template.render(tps)

    def db_connection(db_file):
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
        return None

    def do_authenticationDB(self, usr, pwd):
        user = self.get_user()
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        sql = "select password from users where username == '{}'".format(usr)
        cur = db_con.execute(sql)
        row = cur.fetchone()
        if row != None:
            if row[0] == pwd:
                self.set_user(usr)
        db_con.close()

    def do_authenticationJSON(self, usr, pwd):
        user = self.get_user()
        db_json = json.load(open(WebApp.dbjson))
        users = db_json['users']
        for u in users:
            if u['username'] == usr and u['password'] == pwd:
                self.set_user(usr)
                break
    
    def create_usrDB(self, usr, pwd, email):
        print(WebApp.dbsqlite)
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        sql = "insert into users (username,password,is_superuser,email) values ('{}','{}','0','{}')".format(usr,pwd,email)
        try:
            cur = db_con.execute(sql)
            db_con.commit()
            db_con.close()
        except sqlite3.Error as e:
            return e
        return None

<<<<<<< Updated upstream
    ########################################################################################################################
    # Documents Generation

    ########################################################################################################################
    # Controllers
=======
    def store_eventDB(self, usr, name, date, place, modality, participants, private, icon):
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        sql = "insert into event()"

########################################################################################################################
#   Controllers
>>>>>>> Stashed changes

    # -------------------------------------------------
    # Initial Pages
    @cherrypy.expose
    def index(self):
        tparams = {
            'title': 'Home',
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('index.html', tparams)

    @cherrypy.expose
    def about(self):
        tparams = {
            'title': 'About',
            'message': 'Your application description page.',
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('about.html', tparams)

    # -------------------------------------------------
    # Authentication
    @cherrypy.expose
    def login(self, username=None, password=None):
        if username == None:
            tparams = {
                'title': 'Login',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year,
            }
            return self.render('login.html', tparams)
        else:
            self.do_authenticationDB(username, password)
            if not self.get_user()['is_authenticated']:
                tparams = {
                    'title': 'Login',
                    'errors': True,
                    'user': self.get_user(),
                    'year': datetime.now().year,
                }
                return self.render('login.html', tparams)
            else:
                raise cherrypy.HTTPRedirect("/my_events")

    @cherrypy.expose
    def signup(self, username=None, password=None, mail=None):
        print(username, password, mail)
        if username == None:
            tparams = {
                'title': 'Sign up',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year,
            }
            return self.render('signup.html', tparams)
        else:
            e = self.create_usrDB(username, password,mail)
            if not e:
                raise cherrypy.HTTPRedirect("/")
            tparams = {
                'title': 'Sign up',
                'errors': True,
                'user': self.get_user(),
                'year': datetime.now().year,
            }
            return self.render('signup.html', tparams)

    @cherrypy.expose
    def logout(self):
        self.set_user()
        raise cherrypy.HTTPRedirect("/")
    
    # -------------------------------------------------
    # Event Management Pages
    @cherrypy.expose
<<<<<<< Updated upstream
    def create_event(self):
        # TODO this page needs:
        # -> Read info from form and add to DB

=======
    def create_event(self, name, date, place, mod, participants, visibility):
>>>>>>> Stashed changes
        print('usr on: ', self.get_user()['is_authenticated'])
        if not self.get_user()['is_authenticated']:
            tparams = {
                'title' : 'Login',
                'errors' : False,
                'user' : self.get_user(),
                'year' : datetime.now().year
            }
            return self.render('login.html', tparams)
        else:
            tparams = {
                'title': 'Create an Event',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year
            }
            return self.render('create_event.html', tparams)

    @cherrypy.expose
    def my_events(self):
        # TODO this page needs:
        # -> Receive list of events info. Each event is a card
        #   -> Each card needs event name, dates & type

        #print('usr on: ', self.get_user()['is_authenticated'])
        if not self.get_user()['is_authenticated']:
            tparams = {
                'title' : 'Login',
                'errors' : False,
                'user' : self.get_user(),
                'year' : datetime.now().year
            }
            return self.render('login.html', tparams)
        else:
            tparams = {
                'title': 'My Events',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year
            }
            return self.render('my_events.html', tparams)

    @cherrypy.expose
    def event_details(self):
        # TODO this page needs:
        # -> Receive all event info to put in card About your event

        #print('usr on: ', self.get_user()['is_authenticated'])
        if not self.get_user()['is_authenticated']:
            tparams = {
                'title': 'Login',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year
            }
            return self.render('login.html', tparams)
        else:
            tparams = {
                'title': 'Event Details',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year
            }
            return self.render('event_details.html', tparams)
    
    @cherrypy.expose
    def delete_event(self):
        # TODO 
        pass

    # -------------------------------------------------
    # Add Info Pages
    @cherrypy.expose
    def add_participants(self):
        # TODO this page needs:
        # -> If there's no user, return error
        # -> Else, add participant
        # -> If Add More, redirect to the same page
        # -> Else, redirect to event_details

        #print('usr on: ', self.get_user()['is_authenticated'])
        if not self.get_user()['is_authenticated']:
            tparams = {
                'title': 'Login',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year
            }
            return self.render('login.html', tparams)
        else:
            tparams = {
                'title': 'Add Participants',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year
            }
            return self.render('add_participants.html', tparams)

    @cherrypy.expose
    def add_results(self):
        # TODO this page needs:
        # -> If Add Result is pressed, add result and return to event_details
        # -> Else, fetch results from dummy sensor (JSON based?), return error 

        #print('usr on: ', self.get_user()['is_authenticated'])
        if not self.get_user()['is_authenticated']:
            tparams = {
                'title': 'Login',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year
            }
            return self.render('login.html', tparams)
        else:
            tparams = {
                'title': 'Add Results',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year
            }
            return self.render('add_results.html', tparams)

    @cherrypy.expose
    def create_documents(self):
        # TODO this page needs:
        # -> When Create Documents is pressed
        # -> For each card:
        #   -> If Create is selected, read info (if needed)
        #      apply it to the LaTeX document and save to the db

        #print('usr on: ', self.get_user()['is_authenticated'])
        if not self.get_user()['is_authenticated']:
            tparams = {
                'title': 'Login',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year
            }
            return self.render('login.html', tparams)
        else:
            tparams = {
                'title': 'Create Documents',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year
            }
            return self.render('create_documents.html', tparams)

    # -------------------------------------------------
    # See Info Pages
    @cherrypy.expose
    def see_participants(self):
        # TODO this page needs:
        # -> For each participant/list item: username and email

        #print('usr on: ', self.get_user()['is_authenticated'])
        if not self.get_user()['is_authenticated']:
            tparams = {
                'title': 'Login',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year
            }
            return self.render('login.html', tparams)
        else:
            tparams = {
                'title': 'Participants',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year
            }
            return self.render('see_participants.html', tparams)

    @cherrypy.expose
    def see_results(self):
        # TODO this page needs:
        # -> For each result/list item: participant name, result and date
        
        #print('usr on: ', self.get_user()['is_authenticated'])
        if not self.get_user()['is_authenticated']:
            tparams = {
                'title': 'Login',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year
            }
            return self.render('login.html', tparams)
        else:
            tparams = {
                'title': 'Results',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year
            }
            return self.render('see_results.html', tparams)

    @cherrypy.expose
    def see_documents(self):
        # TODO this page needs:
        # -> For each document/list item: name, type and link
        #print('usr on: ', self.get_user()['is_authenticated'])
        if not self.get_user()['is_authenticated']:
            tparams = {
                'title': 'Login',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year
            }
            return self.render('login.html', tparams)
        else:
            tparams = {
                'title': 'Documents',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year
            }
            return self.render('see_documents.html', tparams)

    @cherrypy.expose
    def shut(self):
        cherrypy.engine.exit()

    
if __name__ == '__main__':
    baseDir = os.path.dirname(os.path.abspath(__file__))
    print("Dir is " + str(baseDir))
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': baseDir
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './static'
        },
        '/favicon.ico':{
            'tools.staticfile.on': True,
            'tools.staticfile.filename': '/static/images/favicon.ico'
        }
    }
    cherrypy.config.update({'server.socket_host' : '0.0.0.0'})  # THIS LINE CAN'T BE DELETED
    cherrypy.quickstart(WebApp(), '/', conf)
