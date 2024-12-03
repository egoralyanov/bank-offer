from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView

from django.contrib.auth.models import User
from bank_app.models import Comment, BankApplication, BankOffer
from bank_app.serializers import UserSerializer, BankOfferSerializer, BankApplicationSerializer

from django.contrib.auth import authenticate, login, logout
from bank_app.minio import add_pic, delete_pic

from django.utils import timezone

import random


def user():
    try:
        user1 = User.objects.get(id=2) # id = 1 is superuser
    except:
        print("No such user")
    return user1


class OfferList(APIView):
    offer_class = BankOffer
    offer_serializer = BankOfferSerializer
    application_class = BankApplication
    application_serializer = BankApplicationSerializer

    def get(self, request, format=None):
        offers = self.offer_class.objects.filter(is_deleted=False)  
        offer_name = request.query_params.get('offer_name')
        if offer_name:
            offers = offers.filter(name__icontains=offer_name)      
        serializer = self.offer_serializer(offers, many=True)

        draft_application = self.application_class.objects.filter(user=user(), status='draft').first()
        draft_application_id = None
        number_of_offers = None
        if draft_application is not None:
            draft_application_id = draft_application.id
            number_of_offers = len(Comment.objects.filter(application=draft_application))

        return Response({'offers': serializer.data, 'draft_application_id': draft_application_id, 'application_offers_counter': number_of_offers})

    def post(self, request, format=None):
        serializer = self.offer_serializer(data=request.data)
        if serializer.is_valid():
            offer = serializer.save()
            # image = request.FILES.get("image")
            # pic_result = add_pic(offer, image)
            # if 'error' in pic_result.data:
            #     return pic_result
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OfferDetail(APIView):
    model_class = BankOffer
    serializer_class = BankOfferSerializer

    def get(self, request, offer_id, format=None):
        offer = get_object_or_404(self.model_class, pk=offer_id)
        serializer = self.serializer_class(offer)
        return Response(serializer.data)

    def put(self, request, offer_id, format=None):
        offer = get_object_or_404(self.model_class, pk=offer_id)
        serializer = self.serializer_class(offer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, offer_id, format=None):
        offer = get_object_or_404(self.model_class, pk=offer_id)
        offer.is_deleted = True
        offer.save()
        pic_result = delete_pic(offer_id)
        if 'error' in pic_result.data:
            return pic_result
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def post(self, request, offer_id, format=None):
        offer = get_object_or_404(self.model_class, pk=offer_id)

        new_image = request.FILES.get('image')
        if not new_image:
            return Response({"error": "Изображение не предоставлено."}, status=status.HTTP_400_BAD_REQUEST)

        if offer.imageUrl is not None:
            delete_result = delete_pic(offer_id)
            if 'error' in delete_result.data:
                return delete_result

        add_result = add_pic(offer, new_image)
        if 'error' in add_result.data:
            return add_result

        return Response({"message": "Изображение успешно обновлено."}, status=status.HTTP_200_OK)


class ApplicationList(APIView):
    model_class = BankApplication
    serializer_class = BankApplicationSerializer

    def get(self, request, format=None):
        user_instance = user()        
        applications = self.model_class.objects.filter(user=user_instance).exclude(status__in=['deleted', 'draft'])

        status = request.query_params.get('status')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if status:
            applications = applications.filter(status=status)
        if start_date:
            start_date_datetime = timezone.datetime.fromisoformat(start_date)
            applications = applications.filter(apply_date__gt=start_date_datetime)
        if end_date:
            end_date_datetime = timezone.datetime.fromisoformat(end_date)
            applications = applications.filter(apply_date__lt=end_date_datetime)

        serializer = self.serializer_class(applications, many=True)
        return Response({'applications': serializer.data, 'creator': user_instance.username})


    def post(self, request, format=None):
        user_instance = user()
        draft_application, created = BankApplication.objects.get_or_create(user=user_instance, status='draft', defaults={'creation_date': timezone.now})
        
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

    def put(self, request, application_id, format=None):
        application = get_object_or_404(self.application_class, pk=application_id)
        serializer = self.application_serializer(application, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, application_id, format=None):
        application = get_object_or_404(self.application_class, pk=application_id)
        application.status = 'deleted'
        application.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ApplicationSubmit(APIView):
    model_class = BankApplication
    serializer_class = BankApplicationSerializer

    def put(self, request, application_id, format=None):
        application = get_object_or_404(self.model_class, pk=application_id)
        if application.status != 'draft':
            return Response({'error': 'Заявка не может быть сформирована только из статуса "Черновик"'}, status=status.HTTP_403_FORBIDDEN)
        application.status = 'created'
        application.apply_date = timezone.now().isoformat()
        application.save()
        return Response({"message": "Заявка сформирована"}, status=status.HTTP_204_NO_CONTENT)
    

class ApplicationApproveReject(APIView):
    model_class = BankApplication
    serializer_class = BankApplicationSerializer

    def put(self, request, application_id, format=None):
        user_instance = user()
        # if user_instance.is_staff == False:
        #     return Response({'error': 'Текущий пользователь не является модератором'}, status=status.HTTP_403_FORBIDDEN)
        application = get_object_or_404(self.model_class, pk=application_id)
        if application.status != 'created':
            return Response({'error': 'Заявка не может быть завершена до того, как перейдет в статус "Сформирована"'}, status=status.HTTP_403_FORBIDDEN)
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

    def delete(self, request, application_id, offer_id, format=None):
        application = get_object_or_404(self.model_class, pk=application_id)
        offer = get_object_or_404(BankOffer, pk=offer_id)
        priority_to_delete = get_object_or_404(Comment, application=application, offer=offer)
        priority_to_delete.delete()

        return Response({"message": "Услуга удалена из заявки"}, status=status.HTTP_204_NO_CONTENT)
    
    def put(self, request, application_id, offer_id, format=None):
        application = get_object_or_404(self.model_class, pk=application_id, status='draft')
        offer = get_object_or_404(BankOffer, pk=offer_id)
        comment_value = request.data.get('comment')

        comment_to_change = get_object_or_404(Comment, application=application, offer=offer)
        comment_to_change.comment = comment_value
        comment_to_change.save()

        return Response({"message": "Комментарий изменен"}, status=status.HTTP_204_NO_CONTENT)
    

class UserProfile(APIView):
    model_class = User
    serializer_class = UserSerializer

    def put(self, request, format=None):
        user_instance = user()
        serializer = self.serializer_class(user_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserLogin(APIView):    
    def post(self, request, format=None):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"message": "Вход успешен."}, status=status.HTTP_200_OK)
        return Response({"error": "Неверные данные."}, status=status.HTTP_401_UNAUTHORIZED)


class UserRegistration(APIView):
    serializer_class = UserSerializer
    
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Регистрация успешна."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserLogout(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        logout(request)
        return Response({"message": "Выход успешен."}, status=status.HTTP_200_OK)