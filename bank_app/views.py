from django.shortcuts import render

bank_offers = [
  {
    "id": 1,
    "name": "РКО",
    "description": "РКО необходимо, чтобы проводить операции по получению и переводу денежных средств контрагентам, в бюджет, сотрудникам",
    "fact": 'Бухгалтерия для бизнеса',
    "cost": 100,
    "bonus": "Бонусы за открытие расчетного счета: скидки на бухгалтерские услуги и бесплатные переводы между счетами",
    'imageUrl': 'http://127.0.0.1:9000/bank-offer/1.png'
  },
  {
    "id": 2,
    "name": "Эквайринг",
    "description": "Подключение эквайринга для малого и среднего бизнеса – это возможность принимать безналичную оплату в торговых точках, при доставке, в интернете",
    "fact": 'Бесплатное подключение',
    "cost": 100,
    "bonus": "Услуги карт платежных систем МИР, Visa, Mastercard и UnionPay, выпущенные российскими эмитентами",
    'imageUrl': 'http://127.0.0.1:9000/bank-offer/2.png'
  },
  {
    "id": 3,
    "name": "Зарплатный проект",
    "description": "Надежный инструмент для экономии времени и ресурсов, а также повышения лояльности сотрудников вашей компании",
    "fact": 'Моментальный выпуск карт',
    "cost": 100,
    "bonus": "Интеграция с любой учетной системой клиента",
    'imageUrl': 'http://127.0.0.1:9000/bank-offer/3.png'
  }
]

mock_bank_application = {
  'id': 1,
  'psrn_and_company_name': '',
  'bank_offers': [
    {
      'id': 1,
      'id_bank_application': 1,
      'id_bank_offer': 1,
      'comment': 'Валюта: рубль'
    },
    {
      'id': 2,
      'id_bank_application': 1,
      'id_bank_offer': 2,
      'comment': 'Нет комментария'
    },
    {
      'id': 3,
      'id_bank_application': 1,
      'id_bank_offer': 3,
      'comment': '5 сотрудников'
    }
  ]
}

def index(request):
    search_query = request.GET.get('bank_offer_name', '')
    filtered_offers = [offer for offer in bank_offers if search_query.lower() in offer['name'].lower()]
    bank_application_offers_counter = len(mock_bank_application['bank_offers'])
    
    context = {
        'bank_offers': filtered_offers,
        'bank_application': mock_bank_application,
        'bank_application_offers_counter': bank_application_offers_counter
    }
    return render(request, 'index.html', context)

def bank_offer(request, bank_offer_id):
    searched_bank_offer = None
    for bank_offer in bank_offers:
      if bank_offer['id'] == bank_offer_id:
        searched_bank_offer = bank_offer
        break
    
    if searched_bank_offer == None:
      return
    
    context = {
        'bank_offer': searched_bank_offer
    }
    return render(request, 'bank_offer.html', context)

def bank_application(request, bank_application_id):
    result_bank_offers = []

    for bank_offer in mock_bank_application['bank_offers']:
      for offer in bank_offers:
        if bank_offer['id'] == offer['id']:
            result_bank_offers.append({ 'bank_offer': offer, 'comment': bank_offer['comment'] })
            break

    context = {
      'id': mock_bank_application['id'],
      'psrn_and_company_name': mock_bank_application['psrn_and_company_name'],
      'bank_offers': result_bank_offers,
    }

    return render(request, 'bank_application.html', context)

