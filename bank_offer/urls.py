from bank_app import views
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Домен услуги
    path(r'offers/', views.OfferList.as_view(), name='offers-list'),
    path(r'offers/<int:offer_id>/', views.OfferDetail.as_view(), name='offer-details'),
    path(r'offers/<int:offer_id>/upload_image/', views.OfferDetail.as_view(), name='upload-offer-image'),
    path(r'applications/draft/', views.ApplicationList.as_view(), name='add-to-draft'),

    # Домен заявки
    path(r'applications/', views.ApplicationList.as_view(), name='applications-list'),
    path(r'applications/<int:application_id>/', views.ApplicationDetail.as_view(), name='application-details'),
    path(r'applications/<int:application_id>/submit/', views.ApplicationSubmit.as_view(), name='application-submit'),
    path(r'applications/<int:application_id>/approve-reject/', views.ApplicationApproveReject.as_view(), name='application-approve-reject'),

    # Домен м-м
    path(r'applications/<int:application_id>/offer/<int:offer_id>', views.ApplicationComment.as_view(), name='application-comment'),

    # Домен Пользователь
    path(r'register/', views.UserRegistration.as_view(), name='user-registration'),
    path(r'profile/', views.UserProfile.as_view(), name='user-profile'),
    path(r'login/', views.UserLogin.as_view(), name='user-login'),
    path(r'logout/', views.UserLogout.as_view(), name='user-logout'),
]