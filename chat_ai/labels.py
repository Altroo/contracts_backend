from contract.models import Contract, Project
FIELD_LABELS = {field.name: str(field.verbose_name) for model in (Contract, Project) for field in model._meta.fields}
RESOURCE_LABELS = {"contract": "Contrat", "project": "Projet", "user": "Utilisateur"}

def selected_action_text(operation, resource, language="fr"):
    if language == "en":
        return ("Delete" if operation == "delete" else "Edit") + " · " + {"contract":"Contract","project":"Project","user":"User"}.get(resource,"Record")
    return ("Supprimer" if operation == "delete" else "Modifier") + " · " + RESOURCE_LABELS.get(resource, "Document")

# Captions verified against contract-form.tsx and translations/fr.ts + en.ts.
FIELD_LABELS.update({'numero_contrat':'Numéro de contrat','client_nom':'Nom du client','client_tel':'Téléphone','client_email':'Email','adresse_travaux':'Adresse des travaux','date_debut':'Date de début','duree_estimee':'Durée estimée','description_travaux':'Description des travaux','notes':'Notes','st_lot_description':'Description du lot','st_observations':'Observations','montant_ht':'Montant HT','date_contrat':'Date du contrat','tva':'TVA'})
FIELD_LABELS_EN = {**FIELD_LABELS,'numero_contrat':'Contract number','client_nom':'Client name','client_tel':'Phone','client_email':'Email','adresse_travaux':'Work address','date_debut':'Start date','duree_estimee':'Estimated duration','description_travaux':'Work description','notes':'Notes','st_lot_description':'Lot description','st_observations':'Observations','montant_ht':'Amount excl. tax','date_contrat':'Contract date','tva':'VAT','name':'Name','description':'Description','adresse':'Address','maitre_ouvrage':'Project owner','permis':'Building permit'}
