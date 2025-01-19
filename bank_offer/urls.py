from bank_app import views
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers, permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet, basename='user')

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),

    # Rest framework
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Auth
    path('api/', include(router.urls)),
    path('login/',  views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # Домен услуги
    path(r'offers/', views.OfferList.as_view(), name='offers-list'),
    path(r'offers/<int:offer_id>/', views.OfferDetail.as_view(), name='offer-details'),

    # Домен заявки
    path(r'applications/', views.ApplicationList.as_view(), name='applications-list'),
    path(r'applications/<int:application_id>/', views.ApplicationDetail.as_view(), name='application-details'),
    path(r'applications/<int:application_id>/submit/', views.ApplicationSubmit.as_view(), name='application-submit'),
    path(r'applications/<int:application_id>/approve-reject/', views.ApplicationApproveReject.as_view(), name='application-approve-reject'),

    # Домен м-м
    path(r'applications/<int:application_id>/offer/<int:offer_id>', views.ApplicationComment.as_view(), name='application-comment'),
]