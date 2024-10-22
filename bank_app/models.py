from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class BankOffer(models.Model):
    name = models.CharField(max_length=100, null=False)
    description = models.CharField(max_length=500, default="Без описания", null=False)
    bonus = models.CharField(max_length=200, default="Без бонусов", null=False)
    fact = models.CharField(max_length=100, default='Без факта', null=False)
    cost = models.IntegerField(default=5000, null=False)
    imageUrl = models.URLField(null=False)
    is_deleted = models.BooleanField(default=False, null=False)

    class Meta:
        db_table = 'offer'

    def __str__(self):
        return f"BankOffer '{self.id}':  '{self.name}'"


class BankApplication(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('deleted', 'Удалена'),
        ('created', 'Сформирована'),
        ('completed', 'Завершена'),
        ('rejected', 'Отклонена')
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft', null=False)

    creation_date = models.DateTimeField(default=timezone.now, null=False)
    apply_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name='user')
    moderator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderator')

    psrn_and_company_name = models.CharField(max_length=100, null=True, blank=True)
    number_of_services = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'application'

    def __str__(self):
        return f"Application '{self.id}' by '{self.user.username}' created at '{self.creation_date}'"


class Comment(models.Model):
    application = models.ForeignKey(BankApplication, on_delete=models.CASCADE)
    offer = models.ForeignKey(BankOffer, on_delete=models.CASCADE)

    comment = models.CharField(max_length=500, default="", null=False)

    class Meta:
        db_table = 'comment'
        unique_together = ('application', 'offer')

    def __str__(self):
        return f"Comment '{self.id}' in '{self.application}' of '{self.offer}' = '{self.comment}'"