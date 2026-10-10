"""Native flags remain authoritative; company selection narrows, never grants access."""
import hashlib
import re
from django.conf import settings
from account.models import CustomUser
from core.permissions import can_view, can_print, can_create, can_update, can_delete
from chat_ai_assistant.contracts import ChatAIError

# Stable adapter IDs for the native enum, not user roles or memberships.
COMPANIES = {1: ("casa_di_lusso", "Casa di Lusso"), 2: ("blueline_works", "Blueline Works")}
SECRET = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----|(?:Bearer\s+)[A-Za-z0-9._-]{16,}|(?:password|api[_-]?key|secret|access[_-]?token)\s*[:=]\s*\S+", re.I)


def validate_text(text):
    if not isinstance(text, str) or not text.strip() or len(text) > 4000 or "\x00" in text:
        raise ChatAIError("INVALID_ARGUMENTS")
    if SECRET.search(text):
        raise ChatAIError("SENSITIVE_INPUT")
    return text.strip()


def company_code(company_id):
    if type(company_id) is not int or company_id not in COMPANIES:
        raise ChatAIError("PERMISSION_DENIED")
    return COMPANIES[company_id][0]


def authorize(user_id, company_id):
    if not settings.CHAT_AI_ASSISTANT_ENABLED:
        raise ChatAIError("APPLICATION_UNAVAILABLE")
    company_code(company_id)
    user = CustomUser.objects.filter(pk=user_id, is_active=True).first()
    if user is None:
        raise ChatAIError("NOT_AUTHENTICATED")
    if not can_view(user):
        raise ChatAIError("PERMISSION_DENIED")
    return user


def capabilities(user):
    result = {name for name, check in [("read", can_view), ("print", can_print), ("create", can_create), ("update", can_update), ("delete", can_delete)] if check(user)}
    if user.is_staff:
        result.add("users_read")
    return result


def authorization_stamp(user_id, company_id):
    user = authorize(user_id, company_id)
    return hashlib.sha256(repr(("contrat", user.pk, company_code(company_id), user.is_staff, user.is_superuser, sorted(capabilities(user)))).encode()).hexdigest()
