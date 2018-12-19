import cherrypy
import json
import os
import sqlite3
import requests
from datetime import datetime
from sqlite3 import Error
from jinja2 import Environment, PackageLoader, select_autoescape
from documents.doc_gen import *

PEOPLE_SEPARATOR = ";"

# Event Info
EVENT_MODALITIES = ['Football', 'Volleyball', 'Marathons', 'Others']

EVENT_SIZES      = {'Small' :'1-10 participants', 
                    'Medium':'10-100 participants', 
                    'Large' :'100+ participants'}

EVENT_SIZES_MAX  = {'Small (1-10 participants)'     : 10,
                    'Medium (10-100 participants)'  : 100,
                    'Large (100+ participants)'     : None}

# ##############################################################################
class WebApp(object):
    dbsqlite = 'data/db.sqlite3'
    dbjson = 'data/db.json'

    def __init__(self):
        self.env = Environment(
                loader=PackageLoader('webapp', 'html'),
                autoescape=select_autoescape(['html', 'xml'])
                )

    ############################################################################
    # Utilities
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

    # #########################################
    # User Authentication
    def set_user(self, username=None):
        if username == None:
            cherrypy.session['user'] = {'is_authenticated': False, 'username': ''}
        else:
            cherrypy.session['user'] = {'is_authenticated': True, 'username': username}

    def get_user(self):
        if not 'user' in cherrypy.session:
            self.set_user()
        return cherrypy.session['user']

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

    # #########################################
    # Create and Get Events
    def create_eventDB(self, name, s_date, e_date, place, modality, participants, visibility, icon=None):
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        username=self.get_user()['username']
        team = "" + username + PEOPLE_SEPARATOR
        sql = "insert into events (creator, team, e_name, s_date, e_date, place, modality, participants, visibility,icon,inscriptions) values ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','')".format(username,team,name,s_date,e_date,place,modality,participants,False if visibility=='Private' else True, icon if icon else None)
        try:
            cur = db_con.execute(sql)
            db_con.commit()
            db_con.close()
        except sqlite3.Error as e:
            return e
        return None

    def get_events(self):
        username = self.get_user()['username']
        
        # select events where user is admin
        sql = "select * from events where team like '%{}%'".format(username)
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        cur = db_con.execute(sql)
        table = cur.fetchall()
        
        lst = []
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
                'icon_path':event[11],
                'inscriptions':event[10]
                }
            lst.append(e)
        
        # select events where user is a participant
        # TODO simplty 
        # would be enough where team like '%{}%' or where inscriptions like '%{}%'
        sql = "select * from events where inscriptions like '%{}%'".format(username)    
        cur = db_con.execute(sql)
        table = cur.fetchall()

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
                'icon_path':event[11],
                'inscriptions':event[10]
                }
            lst.append(e)

        db_con.close()
        return lst

    # #########################################
    # Event Management
    def delete_eventDB(self, name):
        username = self.get_user()['username']
        sql = "delete from events where e_name='{}' and team like '%{}%'".format(name, username)
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        cur = db_con.execute(sql)
        db_con.commit()
        db_con.close()

    def alter_event(self, name, arg2alter, newarg):
        username = self.get_user()['username']
        sql = "update events set {}='{}' where e_name='{}' and team like '%{}%'".format(arg2alter,newarg,name,username)
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        cur = db_con.execute(sql)
        db_con.commit()
        db_con.close()

    # #########################################
    # Inscriptions/Participants
    def get_inscriptions(self, name):
        sql = "select inscriptions from events where e_name='{}'".format(name)
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        cur = db_con.execute(sql)
        insc_str = cur.fetchall()[0][0]
        db_con.close()
        
        try:
            insc_lst = insc_str.split(PEOPLE_SEPARATOR)
            insc_lst.remove('')
        except ValueError:
            print("Internal Error while removing '' name")
        
        return insc_lst

    def get_inscriptables(self, name):
        sql = "select username from users"
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        cur = db_con.execute(sql)
        users_lst = cur.fetchall()
        db_con.close()

        users_lst = [user[0] for user in users_lst] 
        inscriptions_lst = self.get_inscriptions(name)
        inscriptables = [user for user in users_lst if user not in inscriptions_lst]
        
        return inscriptables

    def get_inscriptions_details(self, name):
        insc_lst = self.get_inscriptions(name)
        insc_detail_lst = []

        db_con = WebApp.db_connection(WebApp.dbsqlite)

        for username in insc_lst:
            sql = "select email from users where username='{}'".format(username)
            cur = db_con.execute(sql)
            email = cur.fetchall()

            insc_detail_lst.append({'name': username, 
                                    'email': email[0][0]})

        db_con.close()

        return insc_detail_lst

    def add_inscription(self, e_name, insc_name):
        usr = self.get_user()['username']
        print("\n\n\n\n\n\n")
        print(e_name)
        get_sql = "select * from events where e_name='{}'".format(e_name)
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        cur = db_con.execute(get_sql)
        event = cur.fetchall()[0]
        print(event)
        management = event[2]
        insc_lst = event[-2]
        if usr not in management:
            return "Error: Not a manager, can't add participants"
        if not insc_lst:
            insc_lst = insc_name + PEOPLE_SEPARATOR
        else:
            insc_lst += insc_name + PEOPLE_SEPARATOR
        put_sql = "update events set inscriptions='{}' where e_name='{}'".format(insc_lst, e_name)
        db_con.execute(put_sql)
        db_con.commit()
        db_con.close()
        print("ADDED")

    # #########################################
    # Results
    def get_event_results(self, e_name):
        sql = "select * from results where e_name == '{}'".format(e_name)
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        cur = db_con.execute(sql)
        results_lst = cur.fetchall()
        db_con.close()

        event_results=[]
        for result in results_lst:
            r = {
                'username': result[2],
                'result': result[3],
                'date': result[4]
            }
            event_results.append(r)

        return event_results

    def add_result(self, e_name, participant_username, result, date):
        print("RESULT ADD")
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        
        sql = "insert into results (e_name, username, result, date) values ('{}','{}','{}','{}')".format(e_name, participant_username, result, date)

        try:
            cur = db_con.execute(sql)
            db_con.commit()
            db_con.close()
        except sqlite3.Error as e:
            return e
        
        print("FINISH")
        return None

    # #########################################
    # 
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
        
        # get counters
        inscriptions = self.get_inscriptions(name)
        results = self.get_event_results(name)
        documents = self.get_event_documents(name)

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
            'inscriptions': inscriptions,
            'inscriptions_count': len(inscriptions),
            'results': results,
            'results_count': len(results),
            'documents': documents,
            'documents_count': len(documents)
            }

        # verify if user is a manager or a participant
        username = self.get_user()['username']
        management_team = event[2]
        management_team_lst = management_team.split(PEOPLE_SEPARATOR)

        if (username in management_team_lst):
            return e, True
        
        return e, False
    
    # #########################################
    # Documents
    def gen_event_doc(self, name, entity_list, self_doc=False, doctype='Security'):
        details= self.get_event_details(name)[0]
        admin = self.get_user()['username'] if self_doc else 'A equipa de gestão do evento'
        print('event_details: ', details)
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
        self.store_doc(name, new_path, doctype)
        return new_path

    def gen_event_invitations(self, name, self_doc=False):
        details = self.get_event_details(name)[0]
        admin = self.get_user()['username'] if self_doc else 'A equipa de gestão do evento'
        icon = details['icon_path'] if details['icon_path'] != 'None' else '../static/images/logo.png'
        path_invites = invitations_docs(event=name,icon_path=icon,dates=(details['start'],details['end']),place=details['place'],admin_name=admin)
        path_invites = os.path.join(os.getcwd(),os.path.basename(path_invites))
        db_path = os.getcwd() + '/events_docs_db/' + name
        if not os.path.exists(db_path):
            os.mkdir(db_path)
        new_path=os.path.join(db_path,os.path.basename(path_invites))
        os.rename(path_invites, new_path)
        self.store_doc(name, new_path, 'invitations')
        return new_path

    def store_doc(self, name, path, doctype):
        usr = self.get_user()['username']
        sql = "insert into documents(e_name,name,type,path) values ('{}','{}','{}','{}') ".format(name,usr,doctype,path)
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        try:
            cur = db_con.execute(sql)
            db_con.commit()
            db_con.close()
            return True
        except:
            db_con.close()

    def get_event_documents(self, e_name):
        sql = "select * from documents where e_name == '{}'".format(e_name)
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        cur = db_con.execute(sql)
        documents_lst = cur.fetchall()
        db_con.close()
        event_documents = []
        for document in documents_lst:
            d = {
                'name': document[2],
                'type': document[3],
                'path': document[4]
            }
            event_documents.append(d)
        return event_documents
    
    # ##########################################################################
    # #########################################
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

    # #########################################
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
    
    # #########################################
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
                    'modalities': EVENT_MODALITIES,
                    'sizes': EVENT_SIZES
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
                    'error': e,
                    'modalities': EVENT_MODALITIES,
                    'sizes': EVENT_SIZES
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
            details, is_admin = self.get_event_details(e_name)
            tparams = {
                'title': 'Event Details',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year,
                'details': details,
                'is_admin': is_admin,
                'size_limits': EVENT_SIZES_MAX
            }
            return self.render('event_details.html', tparams)

    # TODO: To be done
    @cherrypy.expose
    def change_event(self, e_name=None, arg2alter=None, newarg=None):
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
            details, is_admin = self.get_event_details(e_name)
            tparams = {
                'title': 'Event Details',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year,
                'details': details,
                'is_admin': is_admin
            }
            return self.render('event_details.html', tparams)
    
    # TODO: To be done
    @cherrypy.expose
    def delete_event(self, e_name=None):
        if not self.get_user()['is_authenticated']:
            raise cherrypy.HTTPRedirect('/login')
        else:
            self.delete_eventDB(e_name)
            raise cherrypy.HTTPRedirect('/my_events')

    # #########################################
    # Add Info Pages
    @cherrypy.expose
    def add_participants(self, e_name=None, participant_username=None, more=None):
        # TODO December 18
        # when participant_username!= None:
        #   add inscription
        #   if more = True
        #     redirect to add_participants(e_name)
        #   else redirect to event details

        if not self.get_user()['is_authenticated']:
            raise cherrypy.HTTPRedirect('/login')
        elif participant_username:
            self.add_inscription(e_name, participant_username)
            if more == 'True':
                raise cherrypy.HTTPRedirect('/add_participants?e_name='+e_name)
            else:
                raise cherrypy.HTTPRedirect('/event_details?e_name='+e_name)

        elif e_name:
                tparams = {
                    'title': 'Add Participants',
                    'errors': False,
                    'user': self.get_user(),
                    'year': datetime.now().year,
                    'e_name': e_name,
                    'participants': self.get_inscriptables(e_name)
                }
                return self.render('add_participants.html', tparams)
            
    @cherrypy.expose
    def add_results(self, e_name=None, auto=None, participant_username=None, result=None, date=None):
        # this page needs:
        # -> If Add Result is pressed, add result and return to event_details
        # TODO -> Else, fetch results from dummy sensor (JSON based?), return error 

        if not self.get_user()['is_authenticated']:
            raise cherrypy.HTTPRedirect('/login')
        elif not auto or not participant_username or not result or not date:
            # Add Results Page
            tparams = {
                'title': 'Add Results',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year,
                'e_name': e_name,
                'participants': self.get_inscriptions_details(e_name)
            }
            return self.render('add_results.html', tparams)
        else:
            print("\n\n\n\n\n\n\n")
            print(auto)
            
            if auto == True:    # TODO auto fetch results from virtual sensors
                print("AUTO")
            else:       
                print("MANUAL")
                self.add_result(e_name, participant_username, result, date)
            
            # redirect to event_details
            # FIXME temp fix
            print("\n\n\n\n\n\n\n")
            raise cherrypy.HTTPRedirect('/event_details?e_name='+e_name)

    @cherrypy.expose
    def create_documents(self, e_name=None, security=None, security_create=None, health=None, health_create=None, invite_create=None):
        # SOMETHING_create : if True, create
        # SOMETHING: info (e.g authority name)

        # TODO this page needs:
        # -> When Create Documents is pressed
        # -> For each card:
        #   -> If Create is selected, read info (if needed)
        #      apply it to the LaTeX document and save to the db
        if not self.get_user()['is_authenticated']:
            raise cherrypy.HTTPRedirect('/login')
        else:
            if security_create or health_create or invite_create:
                if invite_create:
                    self.gen_event_invitations(e_name)
                if security_create:
                    security = security.split(',')
                    print(security)
                    self.gen_event_doc(e_name, security, doctype='Security')
                if health_create:
                    health = health.split(',')
                    self.gen_event_doc(e_name, health, doctype='Health')
                
                raise cherrypy.HTTPRedirect('/event_details?e_name='+e_name)
            tparams = {
                'title': 'Create Documents',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year,
                'e_name': e_name
            }
            return self.render('create_documents.html', tparams)

    # #########################################
    # See Info Pages
    @cherrypy.expose
    def see_participants(self, e_name=None):
        # this page needs:
        # -> For each participant/list item: username and email
        if not self.get_user()['is_authenticated']:
            raise cherrypy.HTTPRedirect('/login')
        else:
            tparams = {
                'title': 'Participants',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year,
                'e_name': e_name,
                'participants': self.get_inscriptions_details(e_name)
            }
            return self.render('see_participants.html', tparams)

    @cherrypy.expose
    def see_results(self, e_name=None):
        # this page needs:
        # -> For each result/list item: participant name, result and date
        if not self.get_user()['is_authenticated']:
            raise cherrypy.HTTPRedirect('/login')
        else:
            # we can discuss if the user could only see his/her results
            results = self.get_event_results(e_name)   
            
            # for debug purposes
            # results = [{'username': 'USER', 'result': '5-24562'},
            #            {'username': 'sfdf', 'result': 'adsd-24562'}]

            tparams = {
                'title': 'Results',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year,
                'e_name': e_name,
                'results': results
            }
            return self.render('see_results.html', tparams)
    
    @cherrypy.expose
    def see_documents(self, e_name=None):
        # this page needs:
        # -> For each document/list item: name, type and link

        if not self.get_user()['is_authenticated']:
            raise cherrypy.HTTPRedirect('/login')
        else:
            documents = self.get_event_documents(e_name)
            
            # for debug purposes 
            # documents = [{'name': 'NAME', 'type': 'HEALTH', 'path': 'URL'}, {
            #    'name': 'NAME1', 'type': 'HEALTH', 'path': 'URL'}]
            print(documents)
            tparams = {
                'title': 'Documents',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year,
                'e_name': e_name,
                'documents': documents
            }
            return self.render('see_documents.html', tparams)

    @cherrypy.expose
    def view_doc(self, e_name=None, doctype=None, path=None):
        if not self.get_user()['is_authenticated']:
            raise cherrypy.HTTPRedirect('/login')
        else:
            # for debug purposes 
            # documents = [{'name': 'NAME', 'type': 'HEALTH', 'path': 'URL'}, {
            #    'name': 'NAME1', 'type': 'HEALTH', 'path': 'URL'}]
            print(e_name, doctype, path)
            tparams = {
                'title': doctype + 'document of event ' + e_name,
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year,
                'e_name': e_name,
                'doctype':doctype,
                'path': path
            }
            return self.render('view_doc.html', tparams)


    
# ##############################################################################
# Error page
def error_page(status, message, traceback, version):
    tparams = {
        'status'    : status,
        'message'   : message,
        'traceback' : traceback,
        'version'   : version
    }
    return app.render('error.html', tparams)

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

    cherrypy.config.update({'error_page.404': error_page})      # COMMENT FOR DEBUG PURPOSES
    cherrypy.config.update({'error_page.500': error_page})      # COMMENT FOR DEBUG PURPOSES
    cherrypy.config.update({'server.socket_host' : '0.0.0.0'})  # THIS LINE CAN'T BE DELETED

    app = WebApp()
    cherrypy.quickstart(app, '/', conf)
