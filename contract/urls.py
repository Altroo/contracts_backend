from django.urls import path

from .views import (
    ContractListCreateView,
    ContractDetailEditDeleteView,
    GenerateNumeroContratView,
    ContractStatusUpdateView,
    BulkDeleteContractView,
    ContractPDFView,
    ContractDOCView,
)

app_name = "contract"

urlpatterns = [
    # GET list (paginated/full) + POST create
    path("", ContractListCreateView.as_view(), name="contract-list-create"),
    # DELETE bulk
    path("bulk_delete/", BulkDeleteContractView.as_view(), name="contract-bulk-delete"),
    # GET detail + PUT update + DELETE single
    path("<int:pk>/", ContractDetailEditDeleteView.as_view(), name="contract-detail"),
    # GET generate next numero_contrat
    path("generate_num_contrat/", GenerateNumeroContratView.as_view(), name="generate-numero-contrat"),
    # PATCH switch statut
    path("switch_statut/<int:pk>/", ContractStatusUpdateView.as_view(), name="contract-statut-update"),
    # GET PDF (French)
    path("pdf/fr/<int:pk>/", ContractPDFView.as_view(), {"language": "fr"}, name="contract-pdf-fr"),
    # GET PDF (English)
    path("pdf/en/<int:pk>/", ContractPDFView.as_view(), {"language": "en"}, name="contract-pdf-en"),
    # GET DOCX (French)
    path("doc/fr/<int:pk>/", ContractDOCView.as_view(), {"language": "fr"}, name="contract-doc-fr"),
    # GET DOCX (English)
    path("doc/en/<int:pk>/", ContractDOCView.as_view(), {"language": "en"}, name="contract-doc-en"),
]
