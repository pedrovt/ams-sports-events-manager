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
                loader=PackageLoader('webapp', 'templates'),
                autoescape=select_autoescape(['html', 'xml'])
                )


########################################################################################################################
#   Utilities

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
        print(sql)
        cur = db_con.execute(sql)
        row = cur.fetchone()
        if row != None:
            if row[0] == pwd:
                self.set_user(usr)
        db_con.close()

    def do_authenticationJSON(self, usr, pwd):
        user = self.get_user()
        print(user)
        db_json = json.load(open(WebApp.dbjson))
        users = db_json['users']
        for u in users:
            if u['username'] == usr and u['password'] == pwd:
                self.set_user(usr)
                break
    
    def create_usrDB(self, usr, pwd, email):
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        sql = "insert into users (username,password,is_superuser,email) values ('{}','{}','0','{}')".format(usr,pwd,email)
        print(sql)
        try:
            cur = db_con.execute(sql)
            cur = db_con.execute("select * from users")
            print(cur.fetchall())
            db_con.commit()
            db_con.close()
        except sqlite3.Error as e:
            return e
        return None

########################################################################################################################
#   Controllers

    @cherrypy.expose
    def index(self):
        tparams = {
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


    @cherrypy.expose
    def contact(self):
        tparams = {
            'title': 'Contact',
            'message': 'Your contact page.',
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('contact.html', tparams)


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
                raise cherrypy.HTTPRedirect("/")

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

    @cherrypy.expose
    def create_event(self):
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
                'title': 'Create Event',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year
            }
            return self.render('eventgen.html', tparams)


    @cherrypy.expose
    def shut(self):
        cherrypy.engine.exit()


if __name__ == '__main__':
    baseDir = os.path.dirname(os.path.abspath(__file__))
	
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': baseDir
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './static'
        }
    }
    cherrypy.config.update({'server.socket_host' : '0.0.0.0'})  # THIS LINE CAN'T BE DELETED
    cherrypy.quickstart(WebApp(), '/', conf)
