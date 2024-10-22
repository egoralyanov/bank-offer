from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST, require_GET

from django.http import Http404

from django.db import connection

from django.contrib.auth.models import User
from bank_app.models import BankOffer, BankApplication, Comment


@require_GET
def index(request):
    search_query = request.GET.get('offer_name', '')
    all_offers = BankOffer.objects.filter(is_deleted=False)
       
    if search_query:
       all_offers = all_offers.filter(name=search_query)

    default_user = User.objects.get(id=2) # id = 1 is superuser
    user_applications = BankApplication.objects.filter(user=default_user)
    draft_application = user_applications.filter(status='draft').first()

    priorities = Comment.objects.filter(application=draft_application)
    application_offers_size = 0
    for priority in priorities:
        if priority.offer.is_deleted is False:
           application_offers_size += 1
    
    context = {
        'offers': all_offers,
        'application': draft_application,
        'application_offers_counter': application_offers_size
    }
    return render(request, 'index.html', context)


@require_GET
def offer(request, offer_id):
    searched_offer = get_object_or_404(BankOffer, pk=offer_id)
    
    if searched_offer.is_deleted == True:
      return Http404("Услуга удалена")
    
    context = {
        'offer': searched_offer
    }
    return render(request, 'offer.html', context)


@require_GET
def application(request, application_id):
    application = get_object_or_404(BankApplication, pk=application_id)

    if application.status != 'draft':
       raise Http404("Заявка не доступна для редактирования")

    priorities = Comment.objects.filter(application=application)

    application_sections = []
    for priority in priorities:
      if priority.offer.is_deleted is False:
        application_sections.append({ 'offer': priority.offer, 'comment': priority.comment })

    psrn_and_company_name = ''
    if application.psrn_and_company_name is not None:
       psrn_and_company_name = application.psrn_and_company_name

    context = {
      'id': application.id,
      'psrn_and_company_name': psrn_and_company_name,
      'offers': application_sections,
    }

    return render(request, 'application.html', context)


@require_POST
def add_offer(request, offer_id):
    default_user = User.objects.get(id=2) # id = 1 is superuser
    user_applications = BankApplication.objects.filter(user=default_user)
    draft_application = user_applications.filter(status='draft').first()

    chosen_offer = BankOffer.objects.get(pk=offer_id)

    if not draft_application:
        draft_application = BankApplication.objects.create(user=default_user, status='draft')

    priorities = Comment.objects.filter(application=draft_application)

    if priorities.filter(offer=chosen_offer):
       print('Эта услуга уже добавлена в заявку')
       return redirect('index')
    
    Comment.objects.create(application=draft_application, offer=chosen_offer)

    return redirect('index')


@require_POST
def set_application_deleted(request, application_id):
    application = BankApplication.objects.get(id=application_id)
    priorities_counter = Comment.objects.filter(application=application).count()

    with connection.cursor() as cursor:
        cursor.execute("UPDATE application SET status = 'deleted', number_of_services = %s WHERE id = %s", [priorities_counter, application_id])
        print("Заявка удалена.")
        
    return redirect('index')