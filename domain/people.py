# The City Running Project
# Domain layer :: people (Person, Manager and Participant)
# Fields: name, contact, events

class Person() :
	# CTOR
	def __init__ (self, name, contact, events) :
		"""Person"""
		self.name = name
		self.contact = contact
		self.events = events


class Manager(Person):
	
	# CTOR
	def __init__ (self, name, contact, events):
		"""Manager"""
		Person.__init__(name, contact, events)
		
	
	def add_event(self, event):
		"""Adds an event to the manager, updating the event ifself"""
		self.events = [set(self.events + [event])]
		event.managers = [set(self.events + [event])]
	
class Participante(Person):
	# CTOR
	def __init__ (self, name, contact, events) :
		"""Manager"""
		Person.__init__(name, contact, events)
