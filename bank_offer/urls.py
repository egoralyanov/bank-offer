from django.contrib import admin
from django.urls import path
from bank_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('offer/<int:offer_id>', views.offer, name='offer'),
    path('application/<int:application_id>', views.application, name='application'),

    path('add_offer/<int:offer_id>', views.add_offer, name='add_offer'),
    path('set_application_deleted/<int:application_id>', views.set_application_deleted, name='set_application_deleted'),
]