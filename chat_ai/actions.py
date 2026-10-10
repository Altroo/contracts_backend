"""Only explicit, owned, unexpired confirmation can call native mutation views."""
from datetime import timedelta
import hashlib,json
from contextlib import contextmanager
from django.conf import settings
from django.db import transaction,connection,OperationalError
from django.db.models.deletion import ProtectedError,RestrictedError
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework.test import APIRequestFactory,force_authenticate
from simple_history.models import HistoricalRecords
from chat_ai_assistant.contracts import ChatAIError
from .models import PendingAction,AuditEvent
from account.models import CustomUser
from .resources import RESOURCES
from .security import authorize,capabilities,validate_text,company_code
from .labels import FIELD_LABELS


def fingerprint(obj):
    values={f.attname:getattr(obj,f.attname) for f in obj._meta.concrete_fields}
    # Project deletion detaches contracts; include that effect in the reviewed snapshot.
    if obj._meta.model_name == 'project':
        values['related_contracts'] = list(obj.contracts.order_by('pk').values('pk', 'date_updated'))
    return hashlib.sha256(json.dumps(values,sort_keys=True,cls=DjangoJSONEncoder).encode()).hexdigest()


@transaction.atomic
def validated_update(resource,obj,changes):
    spec=RESOURCES[resource]
    if not changes or set(changes)-set(spec.editable):raise ChatAIError('INVALID_ARGUMENTS')
    for value in changes.values():
        if value is not None:
            if not isinstance(value,str) or len(value)>1000:raise ChatAIError('INVALID_ARGUMENTS')
            validate_text(value)
    # Native field and cross-field validation, with trusted unchanged values.
    current=spec.serializer(obj).data
    data={name:current[name] for name,field in spec.serializer().fields.items() if not field.read_only and name in current}
    data.update(changes)
    serializer=spec.serializer(obj,data=data)
    if not serializer.is_valid():raise ChatAIError('INVALID_ARGUMENTS')
    return data


def prepare(executor,resource,identifier,operation,changes):
    caps=executor.capabilities()
    if ('delete' if operation=='delete' else 'update') not in caps:raise ChatAIError('PERMISSION_DENIED')
    if resource not in RESOURCES or not RESOURCES[resource].editable:raise ChatAIError('INVALID_ARGUMENTS')
    from .targets import trusted_target
    if not trusted_target(resource,identifier,instruction=executor.instruction or '',context=executor.context,state=executor.state,now=timezone.now()):raise ChatAIError('CONTEXT_EXPIRED')
    obj=executor.record(resource,identifier)
    if resource=='project' and operation=='delete' and obj.is_predefined:raise ChatAIError('PERMISSION_DENIED')
    if operation=='delete':
        ensure_delete_scope(obj)
        if changes:raise ChatAIError('INVALID_ARGUMENTS')
    elif operation=='update':validated_update(resource,obj,changes)
    else:raise ChatAIError('INVALID_ARGUMENTS')
    if PendingAction.objects.filter(user_id=executor.user_id,consumed_at__isnull=True,expires_at__gt=timezone.now()).count()>=20:raise ChatAIError('CONTEXT_LIMIT')
    action=PendingAction.objects.create(user_id=executor.user_id,company_id=executor.company_id,resource=resource,record_id=obj.pk,operation=operation,changes=changes,fingerprint=fingerprint(obj),expires_at=timezone.now()+timedelta(minutes=5),instruction_id=executor.request_id)
    return confirmation_card(action,obj,executor.context.get("interface_language","fr"))

def ensure_delete_scope(obj):
    if obj._meta.model_name == 'project' and obj.contracts.exclude(company=obj.company).exists():
        raise ChatAIError('ACTION_REJECTED')


def confirmation_card(action,obj,language="fr"):
    en=language=="en"
    before={key:str(getattr(obj,key)) if getattr(obj,key) is not None else None for key in action.changes}
    warnings=['This action will be recorded under your identity.' if en else 'Cette action sera enregistrée sous votre identité.']
    if action.resource=='project' and action.operation=='delete':
        ensure_delete_scope(obj)
        count=obj.contracts.count()
        if count:warnings.append(f'{count} contracts will be unlinked from this project, without being deleted.' if en else f'{count} contrats seront détachés de ce projet, sans être supprimés.')
    return {'type':'confirmation','action_id':str(action.pk),'company_id':action.company_id,'resource':action.resource,'record_id':action.record_id,'operation':action.operation,'label':str(obj)[:300],'changes':action.changes,'before':before,'warning':' '.join(warnings)}



def replay_confirmation(executor,action):
    # Reopened previews and delivery checks also run native serializers, which
    # may lock related records. Bound their validation just like tool execution.
    try:
        with transaction.atomic():
            if connection.vendor == 'postgresql':
                with connection.cursor() as cursor:
                    cursor.execute('SET LOCAL lock_timeout = %s',[5000])
                    cursor.execute('SET LOCAL statement_timeout = %s',[5000])
            return _replay_confirmation(executor,action)
    except OperationalError as exc:
        if getattr(exc.__cause__,'pgcode',None) in ('57014','55P03'):raise ChatAIError('TOOL_TIMEOUT') from None
        raise


def _replay_confirmation(executor,action):
    en=action.get('language')=='en'
    done='Action already performed under your identity.' if en else 'Action déjà effectuée sous votre identité.'
    unavailable='Action unavailable.' if en else 'Action indisponible.'
    expired='This confirmation has expired.' if en else 'Cette confirmation a expiré.'
    pending=PendingAction.objects.filter(pk=action['confirmation_id'],user_id=executor.user_id,company_id=executor.company_id).first()
    if pending is None:
        prior=AuditEvent.objects.filter(correlation_id=action['confirmation_id'],actor_id=executor.user_id,company_id=executor.company_id,application='contrat',tool__startswith='confirmed_',outcome='allowed').exists()
        return {'type':'confirmation_status','message':done if prior else unavailable}
    if pending.consumed_at:return {'type':'confirmation_status','message':done}
    if pending.expires_at<=timezone.now():return {'type':'confirmation_status','message':expired}
    needed='delete' if pending.operation=='delete' else 'update'
    if needed not in executor.capabilities():raise ChatAIError('PERMISSION_DENIED')
    obj=executor.record(pending.resource,pending.record_id)
    if fingerprint(obj)!=pending.fingerprint:raise ChatAIError('CONTEXT_EXPIRED')
    if pending.operation=='update':
        try:validated_update(pending.resource,obj,pending.changes)
        except ChatAIError:raise ChatAIError('CONTEXT_EXPIRED') from None
    return confirmation_card(pending,obj,"en" if en else "fr")


@contextmanager
def native_history_request(request):
    missing=object();previous=getattr(HistoricalRecords.context,'request',missing)
    HistoricalRecords.context.request=request
    try:yield
    finally:
        if previous is missing:del HistoricalRecords.context.request
        else:HistoricalRecords.context.request=previous


def confirm(request,id):
    with transaction.atomic():
        if connection.vendor == 'postgresql':
            with connection.cursor() as cursor:
                cursor.execute('SET LOCAL lock_timeout = %s',[5000])
                cursor.execute('SET LOCAL statement_timeout = %s',[5000])
        action=PendingAction.objects.select_for_update().filter(pk=id,user=request.user).first()
        if action is None:raise ChatAIError('NOT_FOUND')
        user=authorize(request.user.pk,action.company_id)
        if action.consumed_at or action.expires_at<=timezone.now():raise ChatAIError('CONTEXT_EXPIRED')
        if ('delete' if action.operation=='delete' else 'update') not in capabilities(user):raise ChatAIError('PERMISSION_DENIED')
        spec=RESOURCES[action.resource]
        obj=spec.model.objects.select_for_update().filter(pk=action.record_id,company=company_code(action.company_id)).first()
        if obj is None:raise ChatAIError('CONTEXT_EXPIRED')
        if action.resource=='project':
            if action.operation=='delete' and obj.is_predefined:raise ChatAIError('PERMISSION_DENIED')
            list(obj.contracts.select_for_update().values_list('pk',flat=True))
            if action.operation=='delete':ensure_delete_scope(obj)
        if fingerprint(obj)!=action.fingerprint:raise ChatAIError('CONTEXT_EXPIRED')
        data=validated_update(action.resource,obj,action.changes) if action.operation=='update' else None
        # Target/serializer locks may have blocked. Lock the native identity now,
        # then revalidate permissions and expiry at the execution boundary.
        # Concurrent revocation linearizes before this lock or after our commit.
        if not CustomUser.objects.select_for_update().filter(pk=request.user.pk).exists():raise ChatAIError('NOT_AUTHENTICATED')
        user=authorize(request.user.pk,action.company_id)
        if ('delete' if action.operation=='delete' else 'update') not in capabilities(user):raise ChatAIError('PERMISSION_DENIED')
        if action.expires_at<=timezone.now():raise ChatAIError('CONTEXT_EXPIRED')
        factory=APIRequestFactory()
        native_request=factory.put('/',data,format='json') if data is not None else factory.delete('/')
        force_authenticate(native_request,user=user)
        # Native views perform their own can_edit/can_delete checks, notifications,
        # serializers, financial rules and cascade/protection behavior.
        with native_history_request(request):
            try:response=spec.view.as_view()(native_request,pk=obj.pk)
            except (ProtectedError,RestrictedError):raise ChatAIError('ACTION_REJECTED') from None
        if response.status_code>=400:raise ChatAIError('ACTION_REJECTED')
        action.consumed_at=timezone.now();action.save(update_fields=['consumed_at'])
        AuditEvent.objects.create(user=user,actor_id=user.pk,actor_label=str(user)[:254],application='contrat',company_id=action.company_id,resource=action.resource,record_id=action.record_id,changed_fields=sorted(action.changes),tool='confirmed_'+action.operation,outcome='allowed',instruction_id=action.instruction_id,correlation_id=action.pk,model_version=settings.CHAT_AI_MODEL_ID)
    return {'success':True,'operation':action.operation,'resource':action.resource,'record_id':action.record_id}
