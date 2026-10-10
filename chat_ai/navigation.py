"""Only routes present in the native frontend may leave the backend."""
from chat_ai_assistant.contracts import ChatAIError
from .security import company_code
ROUTES = {"contracts": "contracts", "users": "users", "dashboard": ""}
DETAILS = {"contract": "contracts", "user": "users"}


class ChatAINavigationResolver:
    @staticmethod
    def resolve(resource, company_id, identifier=None):
        company_code(company_id)
        base = resource
        suffix = ""
        if resource.endswith("_edit"):
            base, suffix = resource[:-5], "/edit"
        if resource.endswith("_new"):
            base = resource[:-4]
            if base not in DETAILS or identifier is not None:
                raise ChatAIError("INVALID_ARGUMENTS")
            path = "/dashboard/" + DETAILS[base] + "/new"
            if base == "contract":
                path += "?company=" + company_code(company_id)
        elif base in DETAILS and type(identifier) is int and 0 < identifier <= 2147483647:
            path = "/dashboard/" + DETAILS[base] + "/" + str(identifier) + suffix
        elif resource in ROUTES and identifier is None:
            path = "/dashboard/" + ROUTES[resource]
        else:
            raise ChatAIError("INVALID_ARGUMENTS")
        return {"application": "contrat", "resource": resource, "identifier": identifier, "company_id": company_id, "path": path}
