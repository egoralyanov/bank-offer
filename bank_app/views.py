from bank_app.minio import add_pic, delete_pic
from bank_app.models import Comment, BankApplication, BankOffer
from bank_app.serializers import UserSerializer, BankOfferSerializer, BankApplicationSerializer
from bank_app.schemas import bank_offer_response_schema, bank_offer_with_extra_data_response_schema, bank_application_response_schema

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

import random

import redis

from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

import uuid


session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


@swagger_auto_schema(
    operation_summary="Аутентификация",
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'login': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['login', 'password']
    ),
)
@api_view(['POST'])
def login_view(request):
    username = request.data["login"] 
    password = request.data["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
        random_key = str(uuid.uuid4())
        session_storage.set(random_key, user.pk)

        serializer = UserSerializer(user)

        response = Response(serializer.data, status=status.HTTP_200_OK)
        response.set_cookie("session_id", random_key)

        return response
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
@swagger_auto_schema(
    method='post',
    operation_summary="Деавторизация"
)
@api_view(['POST'])
def logout_view(request):
    session_id = request.COOKIES.get('session_id')
    if session_id:
        session_storage.delete(session_id)
        response = Response(status=status.HTTP_200_OK)
        response.delete_cookie("session_id")
        return response
    return Response(status=status.HTTP_401_UNAUTHORIZED)


class UserViewSet(viewsets.ModelViewSet):
    """Класс, описывающий методы работы с пользователями
    Осуществляет связь с таблицей пользователей в базе данных
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    model_class = User

    @swagger_auto_schema(
        operation_summary="Регистрация"
    )
    def create(self, request):
        """
        Функция регистрации новых пользователей
        Если пользователя c указанным в request username ещё нет, в БД будет добавлен новый пользователь.
        """
        if self.model_class.objects.filter(username=request.data['username']).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            self.model_class.objects.create_user(username=serializer.data['username'],
                                     password=serializer.data['password'],
                                     is_superuser=serializer.data['is_superuser'],
                                     is_staff=serializer.data['is_staff'])
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OfferList(APIView):
    offer_class = BankOffer
    offer_serializer = BankOfferSerializer
    application_class = BankApplication
    application_serializer = BankApplicationSerializer

    @swagger_auto_schema(
        operation_summary="Список банковских услуг",
        manual_parameters=[
            openapi.Parameter(
                'offer_name',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING
            ),
        ],
        responses={
            200: openapi.Response(
                description="",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'sections': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=bank_offer_response_schema,
                        ),
                        'draft_application_id': openapi.Schema(
                            type=openapi.TYPE_INTEGER
                        ),
                        'application_offers_counter': openapi.Schema(
                            type=openapi.TYPE_INTEGER
                        ),
                    }
                )
            )
        }
    )
    def get(self, request, format=None):
        offers = self.offer_class.objects.filter(is_deleted=False)  
        offer_name = request.query_params.get('offer_name')
        if offer_name:
            offers = offers.filter(name__icontains=offer_name)      
        serializer = self.offer_serializer(offers, many=True)

        draft_application = None
        ssid = request.COOKIES.get("session_id")
        if ssid is not None:
            user_id = session_storage.get(ssid)
            user_instance = User.objects.filter(pk=user_id).first()
            if user_instance is not None:
                draft_application = self.application_class.objects.filter(user=user_instance, status='draft').first()
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

        draft_application_id = None
        number_of_offers = None
        if draft_application is not None:
            draft_application_id = draft_application.id
            number_of_offers = len(Comment.objects.filter(application=draft_application))

        return Response({'offers': serializer.data, 'draft_application_id': draft_application_id, 'application_offers_counter': number_of_offers})

    @swagger_auto_schema(
        operation_summary="Добавление банковской услуги"
    )
    def post(self, request, format=None):
        serializer = self.offer_serializer(data=request.data)
        if serializer.is_valid():
            offer = serializer.save()
            image = request.FILES.get("image")
            pic_result = add_pic(offer, image)
            if 'error' in pic_result.data:
                return pic_result
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OfferDetail(APIView):
    model_class = BankOffer
    serializer_class = BankOfferSerializer

    @swagger_auto_schema(
        operation_summary="Одна банковская услуга"
    )
    def get(self, request, offer_id, format=None):
        offer = get_object_or_404(self.model_class, pk=offer_id)
        serializer = self.serializer_class(offer)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Изменение банковской услуги",
        request_body=BankOfferSerializer
    )
    def put(self, request, offer_id, format=None):
        offer = get_object_or_404(self.model_class, pk=offer_id)
        serializer = self.serializer_class(offer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Удаление банковской услуги"
    )
    def delete(self, request, offer_id, format=None):
        offer = get_object_or_404(self.model_class, pk=offer_id)
        offer.is_deleted = True
        offer.save()
        pic_result = delete_pic(offer_id)
        if 'error' in pic_result.data:
            return pic_result
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @swagger_auto_schema(
        operation_summary="Добавление изображения"
    )
    def post(self, request, offer_id, format=None):
        offer = get_object_or_404(self.model_class, pk=offer_id)

        new_image = request.FILES.get('image')
        if not new_image:
            return Response({"error": "Изображение не предоставлено."}, status=status.HTTP_400_BAD_REQUEST)

        delete_result = delete_pic(offer_id)
        if 'error' in delete_result.data:
            return add_result

        add_result = add_pic(offer, new_image)
        if 'error' in add_result.data:
            return add_result

        return Response({"message": "Изображение успешно обновлено."}, status=status.HTTP_200_OK)


class ApplicationList(APIView):
    model_class = BankApplication
    serializer_class = BankApplicationSerializer

    @swagger_auto_schema(
        operation_summary="Список банковских заявок",
        manual_parameters=[
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'apply_date',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: openapi.Response(
                examples={
                    'application/json': {
                        'applications': [
                            {
                                "pk": 2,
                                "status": "created",
                                "creation_date": "2024-10-22T22:27:30Z",
                                "apply_date": None,
                                "end_date": None,
                                "creator": "testuser",
                                "moderator": "adminuser",
                                "psrn_and_company_name": None
                            }
                        ]
                    }
                },
                description="",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'applications': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=bank_application_response_schema,
                        )
                    }
                )
            )
        }
    )
    def get(self, request, format=None):
        applications = None
        ssid = request.COOKIES.get("session_id")
        if ssid is not None:
            user_id = session_storage.get(ssid)
            user_instance = User.objects.filter(pk=user_id).first()
            if user_instance is not None:
                if user_instance.is_staff:
                    applications = self.model_class.objects.all().exclude(status__in=['deleted', 'draft'])
                else:
                    applications = self.model_class.objects.filter(user=user_instance).exclude(status__in=['deleted', 'draft'])
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

        query_status = request.query_params.get('status')
        apply_date = request.query_params.get('apply_date')

        if query_status:
            applications = applications.filter(status=query_status)
        if apply_date:
            apply_date_datetime = timezone.datetime.fromisoformat(apply_date)
            applications = applications.filter(apply_date__date=apply_date_datetime)

        serializer = self.serializer_class(applications, many=True)
        return Response({'applications': serializer.data})

    @swagger_auto_schema(
        operation_summary="Добавление в заявку-черновик",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'section_id': openapi.Schema(type=openapi.TYPE_INTEGER)
            },
            required=['section_id']
        ),
        responses={
            201: openapi.Response('Created'),
            400: openapi.Response('Bad Request')
        }
    )
    def post(self, request, format=None):
        draft_application = None
        ssid = request.COOKIES.get("session_id")
        if ssid is not None:
            user_id = session_storage.get(ssid)
            user_instance = User.objects.filter(pk=user_id).first()
            if user_instance is not None:
                draft_application, created = BankApplication.objects.get_or_create(user=user_instance, status='draft', defaults={'creation_date': timezone.now})
            else:
                return Response({"error": "No such user"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "ssid is nil or empty."}, status=status.HTTP_403_FORBIDDEN)
        
        offer_id = request.data.get('offer_id')
        offer = get_object_or_404(BankOffer, pk=offer_id, is_deleted=False)

        if Comment.objects.filter(application=draft_application, offer=offer):
            return Response({"error": "Секция уже добавлена в текущую заявку"}, status=status.HTTP_400_BAD_REQUEST)

        Comment.objects.create(application=draft_application, offer=offer)

        return Response({"message": "Секция добавлена в заявку"}, status=status.HTTP_201_CREATED)


class ApplicationDetail(APIView):
    offer_class = BankOffer
    offer_serializer = BankOfferSerializer
    application_class = BankApplication
    application_serializer = BankApplicationSerializer

    @swagger_auto_schema(
        operation_summary="Одна заявка",
        responses={
            200: openapi.Response(
                description="",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'application': bank_application_response_schema,
                        'offers': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=bank_offer_with_extra_data_response_schema,
                        )
                    }
                )
            )
        }
    )
    def get(self, request, application_id, format=None):
        application = get_object_or_404(self.application_class, pk=application_id)
        serializer = self.application_serializer(application)

        comments = Comment.objects.filter(application=application)

        offers_with_extra_data = []
        for comment in comments:
            if comment.offer.is_deleted == False:
                offer_data = self.offer_serializer(comment.offer).data
                offer_data['account_number'] = comment.account_number
                offer_data['comment'] = comment.comment
                offers_with_extra_data.append(offer_data)

        return Response({'application': serializer.data, 'offers': offers_with_extra_data})

    @swagger_auto_schema(
        request_body=BankApplicationSerializer,
        operation_summary="Изменение доп. полей заявки",
    )
    def put(self, request, application_id, format=None):
        application = get_object_or_404(self.application_class, pk=application_id)
        serializer = self.application_serializer(application, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Удаление заявки",
        responses={
            204: openapi.Response('No Content'),
        }
    )
    def delete(self, request, application_id, format=None):
        application = get_object_or_404(self.application_class, pk=application_id)
        application.status = 'deleted'
        application.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ApplicationSubmit(APIView):
    model_class = BankApplication
    serializer_class = BankApplicationSerializer

    @swagger_auto_schema(
        operation_summary="Сформировать создателем",
        responses={
            204: openapi.Response('No Content'),
            400: openapi.Response('Bad Request')
        }
    )
    def put(self, request, application_id, format=None):
        ssid = request.COOKIES.get("session_id")
        if ssid is not None:
            user_id = session_storage.get(ssid)
            user_instance = User.objects.filter(pk=user_id).first()
            if user_instance is None:
                return Response({'error': 'No such user'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                application = get_object_or_404(self.model_class, pk=application_id)
                if application.user != user_instance:
                    return Response({"error": "Заявка может быть сформирована только создателем"}, status=status.HTTP_400_BAD_REQUEST)
                if application.status != 'draft':
                    return Response({"error": "Заявка может быть сформирована только из статуса 'черновик'"}, status=status.HTTP_400_BAD_REQUEST)
                application.status = 'created'
                application.apply_date = timezone.now().isoformat()
                application.save()
                return Response({"message": "Заявка сформирована"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'No user'}, status=status.HTTP_400_BAD_REQUEST)
    

class ApplicationApproveReject(APIView):
    model_class = BankApplication
    serializer_class = BankApplicationSerializer

    @swagger_auto_schema(
        operation_summary="Завершить/отклонить модератором",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, description="'completed' or 'rejected'")
            },
            required=['status']
        ),
        responses={
            200: openapi.Response('Success', serializer_class),
            400: openapi.Response('Bad Request')
        }
    )
    def put(self, request, application_id, format=None):
        ssid = request.COOKIES.get("session_id")
        if ssid is not None:
            user_id = session_storage.get(ssid)
            user_instance = User.objects.filter(pk=user_id).first()
            if user_instance is None:
                return Response({'error': 'No such user'}, status=status.HTTP_400_BAD_REQUEST)
            if user_instance.is_staff is False:
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"error": "ssid is nil or empty."}, status=status.HTTP_403_FORBIDDEN)
        application = get_object_or_404(self.model_class, pk=application_id)
        if application.status != 'created':
            return Response({'error': 'Заявка не может быть завершена до того, как перейдет в статус "Сформирована"'}, status=status.HTTP_400_BAD_REQUEST)
        application.status = request.data['status']
        application.moderator = user_instance
        application.end_date = timezone.now().isoformat()

        Comment.objects.filter(application=application).update(account_number=''.join(random.choices('0123456789', k=20)))

        application.save()
        serializer = self.serializer_class(application)

        return Response(serializer.data)


class ApplicationComment(APIView):
    model_class = BankApplication
    serializer_class = BankApplicationSerializer

    @swagger_auto_schema(
        operation_summary="Удалить услугу из заявки"
    )
    def delete(self, request, application_id, offer_id, format=None):
        application = get_object_or_404(self.model_class, pk=application_id)
        offer = get_object_or_404(BankOffer, pk=offer_id)
        priority_to_delete = get_object_or_404(Comment, application=application, offer=offer)
        priority_to_delete.delete()

        return Response({"message": "Услуга удалена из заявки"}, status=status.HTTP_204_NO_CONTENT)
    
    @swagger_auto_schema(
        operation_summary="Изменить комментарий к услуге в заявке"
    )
    def put(self, request, application_id, offer_id, format=None):
        application = get_object_or_404(self.model_class, pk=application_id, status='draft')
        offer = get_object_or_404(BankOffer, pk=offer_id)
        comment_value = request.data.get('comment')

        comment_to_change = get_object_or_404(Comment, application=application, offer=offer)
        comment_to_change.comment = comment_value
        comment_to_change.save()

        return Response({"message": "Комментарий изменен"}, status=status.HTTP_204_NO_CONTENT)
