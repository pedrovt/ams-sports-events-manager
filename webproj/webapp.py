import json
import os
import sqlite3
from datetime import datetime
from sqlite3 import Error

import requests
import cherrypy
from jinja2 import Environment, PackageLoader, select_autoescape

from documents.doc_gen import *

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
    
    def create_usrDB(self, usr, pwd, email):
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        sql = "insert into users (username,password,is_superuser,email) values ('{}','{}','0','{}')".format(usr,pwd,email)
        try:
            cur = db_con.execute(sql)
            db_con.commit()
            db_con.close()
        except sqlite3.Error as e:
            return e
        return None

    def create_eventDB(self, name, s_date, e_date, place, modality, participants, visibility, icon=None):
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        username=self.get_user()['username']
        team = "" + username + ";"
        sql = "insert into events (creator, team, e_name, s_date, e_date, place, modality, participants, visibility,icon,inscriptions) values ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','')".format(username,team,name,s_date,e_date,place,modality,participants,False if visibility=='Private' else True, icon if icon else None)
        try:
            cur = db_con.execute(sql)
            db_con.commit()
            db_con.close()
        except sqlite3.Error as e:
            return e
        return None

    def get_events(self):
        # todo select events where participnants are...
        username = self.get_user()['username']
        sql = "select * from events where team like '%{}%'".format(username)
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        cur = db_con.execute(sql)
        table = cur.fetchall()
        db_con.close()
        lst =[]
        for event in table:
            e = {
                'creator':event[1],
                'management':event[2],
                'name':event[3],
                'start':event[4],
                'end':event[5],
                'place':event[6],
                'modality':event[7],
                'participants':event[8],
                'visible':event[9],
                'icon_path':event[10],
                'inscriptions':event[11]
                }
            lst.append(e)
        return lst

    def delete_event(self, name):
        username = self.get_user()['username']
        sql = "delete from events where e_name='{}' and team like '%{}%'".format(name, username)
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        cur = db_con.execute(sql)
        db_con.close()

    def alter_event(self, name, arg2alter, newarg):
        username = self.get_user()['username']
        sql = "update events set {}='{}' where e_name='{}' and team like '%{}%'".format(arg2alter,newarg,name,username)
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        cur = db_con.execute(sql)
        db_con.commit()
        db_con.close()

    def get_inscriptions(self, name):
        sql = "select inscriptions from events where e_name='{}'".format(name)
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        cur = db_con.execute(sql)
        insc_lst = cur.fetchall()[0][0]
        db_con.close()
        return insc_lst

    def add_inscription(self, e_name, insc_name):
        usr = self.get_user()['username']
        get_sql = "select * from events where e_name='{}'".format(e_name)
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        cur = db_con.execute(get_sql)
        event = cur.fetchall()[0]
        management = event[2]
        insc_lst = event[-2]
        if usr not in management:
            return "Error: Not a manager, can't add participants"
        if not insc_lst:
            insc_lst = insc_name + ","
        else:
            insc_lst += insc_name + ","
        put_sql = "update events set inscriptions='{}' where e_name='{}'".format(insc_lst, e_name)
        db_con.execute(put_sql)
        db_con.commit()
        db_con.close()

    def usr_exists(self, name):
        sql = "select * from users where name='{}'".format(name)
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        cur = db_con.execute(sql)
        name = cur.fetchall()
        db_con.close()
        if not name:
            return False
        return True

    def event_exists(self, name):
        sql = "select * from events where e_name='{}'".format(name)
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        cur = db_con.execute(sql)
        name = cur.fetchall()
        db_con.close()
        if not name:
            return False
        return True
    
    def get_event_details(self, name):
        sql = "select * from events where e_name='{}'".format(name)
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        cur = db_con.execute(sql)
        event = cur.fetchall()[0]
        db_con.close()
        # TODO get docs, participants and results count
        e = {
            'creator':event[1],
            'management':event[2],
            'name':event[3],
            'start':event[4],
            'end':event[5],
            'place':event[6],
            'modality':event[7],
            'participants':event[8],
            'visible':event[9],
            'icon_path':event[11],
            'inscriptions':event[10]
            }
        return e
    
    def gen_event_doc(self, name, entity_list, self_doc=False, doctype='Security'):
        details = self.get_event_details(name)
        admin = self.get_user()['username'] if self_doc else 'A equipa de gestão do evento'
        icon = details['icon_path'] if details['icon_path'] != 'None' else '../static/images/logo.png'
        if doctype=='Security':
            path = security_docs(entity_list=entity_list,event=name,icon_path=icon,dates=(details['start'],details['end']),place=details['place'],admin_name=admin)
        elif doctype=='Health':
            path = health_docs(entity_list=entity_list,event=name,icon_path=icon,dates=(details['start'],details['end']),place=details['place'],admin_name=admin)
        elif doctype=='Sponsors':
            path = sponsors_docs(entity_list=entity_list,event=name,icon_path=icon,dates=(details['start'],details['end']),place=details['place'],admin_name=admin)
        path = os.path.join(os.getcwd(),os.path.basename(path))
        db_path = os.getcwd() + '/events_docs_db/' + name
        if not os.path.exists(db_path):
            os.mkdir(db_path)
        new_path=os.path.join(db_path,os.path.basename(path))
        os.rename(path, new_path)
        return new_path

    def gen_event_invitations(self, name, entity, self_doc=False):
        details = self.get_event_details(name)
        admin = self.get_user()['username'] if self_doc else 'A equipa de gestão do evento'
        icon = details['icon_path'] if details['icon_path'] != 'None' else '../static/images/logo.png'
        path_invites = invitations_docs(entity=entity,event=name,icon_path=icon,dates=(details['start'],details['end']),place=details['place'],admin_name=admin)
        path_invites = os.path.join(os.getcwd(),os.path.basename(path_invites))
        db_path = os.getcwd() + '/events_docs_db/' + name
        if not os.path.exists(db_path):
            os.mkdir(db_path)
        new_path=os.path.join(db_path,os.path.basename(path_invites))
        os.rename(path_invites, new_path)
        return new_path

    # ##########################################################################
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

    # ##########################################################################
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
    
    # ##########################################################################
    # Event Management Pages
    @cherrypy.expose
    def create_event(self, name=None, s_date=None, e_date=None, place=None, modality=None, participants=None, visibility=None, icon=None):
        #TODO:
        # -> throw exception when event has something missing
        if not self.get_user()['is_authenticated']:
            raise cherrypy.HTTPRedirect('/login')
        else:
            # it always has participants so it is the way to check if it's first time accessign page
            if not participants:
                tparams = {
                    'title': 'Event creation Page',
                    'errors': False,
                    'user': self.get_user(),
                    'year': datetime.now().year,
                }
                return self.render('create_event.html', tparams)
               
            e = self.create_eventDB(name, s_date, e_date, place, modality, participants, visibility, icon)
            # send error to print in web UI
            if e:
                tparams = {
                    'title': 'Failed Event creation',
                    'errors': True,
                    'user': self.get_user(),
                    'year': datetime.now().year,
                    'error': e
                }
                return self.render('create_event.html', tparams)
            raise cherrypy.HTTPRedirect('/my_events')

    @cherrypy.expose
    def my_events(self):
        # TODO this page needs:
        # -> Receive list of events info. Each event is a card
        #   -> Each card needs event name, dates & type
        if not self.get_user()['is_authenticated']:
            raise cherrypy.HTTPRedirect('/login')
        else:
            events_list = self.get_events()
            tparams = {
                'title': 'My Events',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year,
                'events': events_list
            }
            return self.render('my_events.html', tparams)

    @cherrypy.expose
    def event_details(self, e_name=None):
        if not self.get_user()['is_authenticated']:
            raise cherrypy.HTTPRedirect('/login')
        elif not e_name:
            tparams = {
                'title': 'Event Details',
                'errors': True,
                'user': self.get_user(),
                'year': datetime.now().year,
            }
            return self.render('event_details.html', tparams)
        else:
            details = self.get_event_details(e_name)
            tparams = {
                'title': 'Event Details',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year,
                'details': details
            }
            return self.render('event_details.html', tparams)

    # ##########################################################################
    # Add Info Pages
    @cherrypy.expose
    def add_participants(self, e_name=None, insc=None):
        # TODO this page needs:
        # -> If there's no user, return error
        # -> Else, add participant
        # -> If Add More, redirect to the same page
        # -> Else, redirect to event_details
        if not self.get_user()['is_authenticated']:
            raise cherrypy.HTTPRedirect('/login')
        else:
            if e_name:
                tparams = {
                    'title': 'Add Participants',
                    'errors': False,
                    'user': self.get_user(),
                    'year': datetime.now().year,
                    'participants': self.get_inscriptions(e_name)
                }
                return self.render('add_participants.html', tparams)
            

    @cherrypy.expose
    def add_results(self, e_name=None):
        # TODO this page needs:
        # -> If Add Result is pressed, add result and return to event_details
        # -> Else, fetch results from dummy sensor (JSON based?), return error 

        #print('usr on: ', self.get_user()['is_authenticated'])
        if not self.get_user()['is_authenticated']:
            raise cherrypy.HTTPRedirect('/login')
        else:
            tparams = {
                'title': 'Add Results',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year
            }
            return self.render('add_results.html', tparams)

    @cherrypy.expose
    def create_documents(self, e_name=None):
        # TODO this page needs:
        # -> When Create Documents is pressed
        # -> For each card:
        #   -> If Create is selected, read info (if needed)
        #      apply it to the LaTeX document and save to the db
        if not self.get_user()['is_authenticated']:
            raise cherrypy.HTTPRedirect('/login')
        else:
            tparams = {
                'title': 'Create Documents',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year
            }
            return self.render('create_documents.html', tparams)

    # ##########################################################################
    # See Info Pages
    @cherrypy.expose
    def see_participants(self, e_name=None):
        # TODO this page needs:
        # -> For each participant/list item: username and email
        if not self.get_user()['is_authenticated']:
            raise cherrypy.HTTPRedirect('/login')
        else:
            tparams = {
                'title': 'Participants',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year
            }
            return self.render('see_participants.html', tparams)

    @cherrypy.expose
    def see_results(self, e_name=None):
        # TODO this page needs:
        # -> For each result/list item: participant name, result and date
        if not self.get_user()['is_authenticated']:
            raise cherrypy.HTTPRedirect('/login')
        else:
            tparams = {
                'title': 'Results',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year
            }
            return self.render('see_results.html', tparams)

    @cherrypy.expose
    def see_documents(self, e_name=None):
        # TODO this page needs:
        # -> For each document/list item: name, type and link
        if not self.get_user()['is_authenticated']:
            raise cherrypy.HTTPRedirect('/login')
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

    # ##########################################################################
    # Error pages
    @cherrypy.expose
    def error_404(self):
        pass

    @cherrypy.expose
    def error_500(self):
        pass
    
if __name__ == '__main__':
    baseDir = os.path.dirname(os.path.abspath(__file__))
    cherrypy.log("The City Running Project")
    cherrypy.log("Dir is " + str(baseDir))
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
