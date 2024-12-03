from drf_yasg import openapi

bank_offer_with_extra_data_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'pk': openapi.Schema(type=openapi.TYPE_INTEGER),
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        'description': openapi.Schema(type=openapi.TYPE_STRING),
        'bonus': openapi.Schema(type=openapi.TYPE_STRING),
        'fact': openapi.Schema(type=openapi.TYPE_STRING),
        'cost': openapi.Schema(type=openapi.TYPE_INTEGER),
        'imageUrl': openapi.Schema(type=openapi.TYPE_STRING),
        'account_number': openapi.Schema(type=openapi.TYPE_STRING),
        'comment': openapi.Schema(type=openapi.TYPE_STRING)
    }
)

bank_offer_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'pk': openapi.Schema(type=openapi.TYPE_INTEGER),
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        'description': openapi.Schema(type=openapi.TYPE_STRING),
        'bonus': openapi.Schema(type=openapi.TYPE_STRING),
        'fact': openapi.Schema(type=openapi.TYPE_STRING),
        'cost': openapi.Schema(type=openapi.TYPE_INTEGER),
        'imageUrl': openapi.Schema(type=openapi.TYPE_STRING)
    }
)

bank_application_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'pk': openapi.Schema(type=openapi.TYPE_INTEGER),
        'status': openapi.Schema(type=openapi.TYPE_STRING),
        'creation_date': openapi.Schema(type=openapi.TYPE_STRING),
        'apply_date': openapi.Schema(type=openapi.TYPE_STRING),
        'end_date': openapi.Schema(type=openapi.TYPE_STRING),
        'psrn_and_company_name': openapi.Schema(type=openapi.TYPE_STRING)
    }
)