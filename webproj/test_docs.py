from documents.doc_gen import *

path_sec = security_docs(entity_list=['Lista','de','autoridades'],event="Nome do evento",dates=('2018-02-21','2018-02-22'),place='Local do evento',admin_name='A equipa de gestão')
print('sec done!!!')
path_health = health_docs(entity_list=['Lista','de','autoridades'],event="Nome do evento",dates=('2018-02-21','2018-02-22'),place='Local do evento',admin_name='A equipa de gestão')
print('health done!!!')
path_invitations = invitations_docs(entity='Convidado 1',event="Nome do evento",dates=('2018-02-21','2018-02-22'),place='Local do evento',admin_name='A equipa de gestão')
print('invites done!!!')
path_sponsors = sponsors_docs(entity_list=['Lista','de','autoridades'],event="Nome do evento",dates=('2018-02-21','2018-02-22'),place='Local do evento',admin_name='A equipa de gestão')
print('sponsors done!!!')

print('sec: ',path_sec,'\nhealth: ',path_health,'\ninvites: ',path_invitations, '\nsponsors: ',path_sponsors)
