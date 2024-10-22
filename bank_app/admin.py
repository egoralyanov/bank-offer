from django.contrib import admin
from .models import BankOffer, BankApplication, Comment

admin.site.register(BankOffer)
admin.site.register(BankApplication)
admin.site.register(Comment)