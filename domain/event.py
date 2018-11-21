# The City Running Project
# Domain layer :: event
# Fields (defined at init=: name, date, place, num_participants, visibility, teams
# Fields participants, results, documents
from enum import Enum
class Visibility(Enum):
	PUBLIC = 1
	PRIVATE = 2
	
class Event():
	
	# CTOR
	def __init__(self, name, date, place, visibility, num_participants):
		self.name  = name
		self.date  = date
		self.place = place
		self.visibility 	  = visibility # TODO consider not using enums
		self.num_participants = num_participants
		self.participants = []
		self.results	  = []
		self.documents	  = []

	# TODO
	def add_participant(self, person, team):
		pass
	
	# TODO
	def add_team(self, team):
		pass
	
	# TODO
	def add_result(self, result):
		pass
	
	# TODO
	def add_document(self, document):
		pass
