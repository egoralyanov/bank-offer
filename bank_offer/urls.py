from django.contrib import admin
from django.urls import path
from bank_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('bank_offer/<int:bank_offer_id>', views.bank_offer, name='bank_offer'),
    path('bank_application/<int:bank_application_id>', views.bank_application, name='bank_application')
]
