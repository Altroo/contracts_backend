"""Optional modules/actions: descriptions accepted; a bare slash action explains usage."""
import re
from chat_ai_assistant.clarifications import message_language
from chat_ai_assistant.routing import normalized
from chat_ai_assistant.contracts import ChatAIError
from .security import capabilities
MODULES=[('/contrats','contract','Contrats','Contracts'),('/projets','project','Projets de construction','Construction projects'),('/utilisateurs','user','Utilisateurs','Users')]
ALIASES={'/contracts':'/contrats','/projects':'/projets','/users':'/utilisateurs','/search':'/voir','/chercher':'/voir','/edit':'/modifier','/delete':'/supprimer','/help':'/aide','/docx':'/word'}

def shortcut_catalog(user,language='fr'):
    en=language=='en';caps=capabilities(user)
    items=[]
    for command,resource,fr,english in MODULES:
        if resource=='user' and 'users_read' not in caps:continue
        example={'contract':'/contrats '+('customer Demo Atlas' if en else 'client Démo Atlas'),'project':'/projets '+('Résidence Exemple'),'user':'/utilisateurs '+('Demo Louise')}[resource]
        items.append({'command':command,'title':english if en else fr,'help':'Search by name, reference or description.' if en else 'Recherchez par nom, référence ou description.','example':example})
    for command,fr,english,cap in [('/voir','Rechercher un document','Find a record','read'),('/modifier','Modifier après confirmation','Edit with confirmation','update'),('/supprimer','Supprimer après confirmation','Delete with confirmation','delete'),('/pdf','Contrat PDF','Contract PDF','print'),('/word','Contrat Word','Contract Word','print'),('/aide','Aide des raccourcis','Shortcut help','read')]:
        if cap in caps:items.append({'command':command,'title':english if en else fr,'help':'Describe the record; select the matching result before any change.' if en else 'Décrivez le document ; choisissez le bon résultat avant toute modification.','example':command+' '+('contract for Demo Atlas' if en else 'contrat de Démo Atlas')})
    return items if 'read' in caps else []


def suggestions(user,language='fr'):
    if 'read' not in capabilities(user):return []
    items=['Show the latest contracts.','Show signed contracts.','Find a contract by customer name.','What does the contract status mean?'] if language=='en' else ['Affiche les derniers contrats.','Montre les contrats signés.','Retrouver un contrat par nom de client.','Que signifie le statut d’un contrat ?']
    if 'create' in capabilities(user):items.append('How do I create a contract?' if language=='en' else 'Comment créer un contrat ?')
    return items


def shortcut_action(text,executor=None,interface_language='fr'):
    if not text.startswith('/'):return None
    parts=text.split(maxsplit=1);command=ALIASES.get(parts[0].casefold(),parts[0].casefold());arg=parts[1].strip() if len(parts)>1 else ''
    if command=='/' and not arg:command='/aide'
    language=message_language(text,interface_language);en=language=='en'
    catalog=shortcut_catalog(executor.authorize(),language);item=next((x for x in catalog if x['command']==command),None)
    if not item:
        if command in ('/modifier','/supprimer','/pdf','/word','/utilisateurs'):raise ChatAIError('PERMISSION_DENIED')
        return {'tool':'clarify','message':'Unknown command. Send /help.' if en else 'Commande inconnue. Envoyez /aide.'}
    if command=='/aide':return {'tool':'clarify','message':('\n'.join(x['command']+' : '+x['title'] for x in catalog))}
    module=next((x for x in MODULES if x[0]==command),None)
    if module and not arg:return {'tool':'search_records','arguments':{'resource':module[1]},'usage_message':item['help']+' '+item['example']}
    if not arg:return {'tool':'clarify','message':item['help']+' '+item['example']}
    return None

def reference_action(text,state):
    if not state.get('ids'):return None
    words=normalized(text).strip().rstrip('.!?')
    values={'first':1,'second':2,'third':3,'premier':1,'premiere':1,'deuxieme':2,'troisieme':3}
    match=re.fullmatch(r'(?:open (?:the )?|ouvre (?:le |la )?)(first|second|third|premier|premiere|deuxieme|troisieme)(?: one| result| resultat)?',words)
    if match:return {'tool':'previous_results','arguments':{'operation':'open','index':values[match[1]]}}
    return None

def knowledge_action(text):
    words=normalized(text).strip()
    if len(text)<300 and not re.search(r'\d|\b(?:then|puis|ensuite|ignore|et|and|current|this|ce|cette)\b',words) and re.match(r'^(?:how (?:do i|to)|comment (?:creer|retrouver|trouver|modifier|supprimer|utiliser)|que signifie|what does)\b',words):return {'tool':'knowledge','arguments':{'query':text}}
    return None


def greeting_action(text):
    """Greeting-only messages never invoke the model or retrieve business records."""
    words=normalized(text).strip().rstrip('.!?').strip()
    words=re.sub(r'\s+',' ',words)
    if words in {'hello','hi','hey','good morning','good afternoon','good evening','hello there'}:
        return {'tool':'clarify','message':'Hello! How can I help you with Contracts?'}
    if words in {'bonjour','salut','bonsoir','coucou','bonjour a tous'}:
        return {'tool':'clarify','message':'Bonjour ! Comment puis-je vous aider dans Contracts ?'}
    if words in {'thanks','thank you','thank you very much'}:
        return {'tool':'clarify','message':'You’re welcome!'}
    if words in {'merci','merci beaucoup'}:
        return {'tool':'clarify','message':'Avec plaisir !'}
    return None
