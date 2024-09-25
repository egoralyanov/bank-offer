from django.shortcuts import render

offers = [
  {
    "id": 1,
    "name": "Дебетовая карта",
    "description": "Карта для повседневных покупок с выгодными условиями обслуживания",
    "cashback": 5,
    "duration": 3,
    "subscription": 100,
    "bonus": "Бонусы у партнеров: скидки в магазинах, кафе и на автозаправках",
    'imageUrl': 'http://127.0.0.1:9000/bank-offer/debit.png'
  },
  {
    "id": 2,
    "name": "Кредитная карта",
    "description": "Удобный инструмент для получения краткосрочных кредитов с гибкими условиями погашения",
    "cashback": 10,
    "duration": 2,
    "subscription": 250,
    "bonus": "Предоставляет льготный период на покупки до 50 дней",
    'imageUrl': 'http://127.0.0.1:9000/bank-offer/credit.png'
  },
  {
    "id": 3,
    "name": "Премиальная карта",
    "description": "Эксклюзивная карта с привилегиями для путешествий и бизнеса",
    "cashback": 20,
    "duration": 2,
    "subscription": 500,
    "bonus": "Доступ в бизнес-залы аэропортов и премиальные программы лояльности",
    'imageUrl': 'http://127.0.0.1:9000/bank-offer/premium.png'
  },
  {
    "id": 4,
    "name": "Социальная карта",
    "description": "Карта для жителей города с привилегиями и льготами",
    "cashback": 7,
    "duration": 3,
    "subscription": 0,
    "bonus": "Бесплатный проезд в общественном транспорте и скидки в муниципальных учреждениях",
    'imageUrl': 'http://127.0.0.1:9000/bank-offer/social.png'
  },
  {
    "id": 5,
    "name": "Детская карта",
    "description": "Карта для детей с возможностью родительского контроля расходов",
    "cashback": 15,
    "duration": 2,
    "subscription": 0,
    "bonus": "Позволяет родителям контролировать траты ребенка и устанавливать лимиты",
    'imageUrl': 'http://127.0.0.1:9000/bank-offer/kids.png'
  }
]

mock_application = {
  'id': 1,
  'fio': '',
  'offer_priority': [
    {
      'id': 1,
      'id_application': 1,
      'id_offer': 1,
      'priority_number': 1
    },
    {
      'id': 2,
      'id_application': 1,
      'id_offer': 2,
      'priority_number': 3
    },
    {
      'id': 3,
      'id_application': 1,
      'id_offer': 3,
      'priority_number': 2
    },
    {
      'id': 4,
      'id_application': 1,
      'id_offer': 5,
      'priority_number': 4
    }
  ]
}

def index(request):
    search_query = request.GET.get('offer_name', '')
    filtered_offers = [offer for offer in offers if search_query.lower() in offer['name'].lower()]
    application_offers_size = len(mock_application['offer_priority'])
    
    context = {
        'offers': filtered_offers,
        'application': mock_application,
        'application_offers_counter': application_offers_size
    }
    return render(request, 'index.html', context)

def offer(request, offer_id):
    searched_offer = None
    for offer in offers:
      if offer['id'] == offer_id:
        searched_offer = offer
        break
    
    if searched_offer == None:
      return
    
    context = {
        'offer': searched_offer
    }
    return render(request, 'offer.html', context)

def application(request, application_id):
    sorted_offers_order = sorted(mock_application['offer_priority'], key=lambda dict: dict['priority_number'])

    sorted_offers = []
    index = 0
    for sorted_offer_order in sorted_offers_order:
      index += 1
      for offer in offers:
        if sorted_offer_order['id'] == offer['id']:
            sorted_offers.append({ 'offer': offer, 'index': index })
            break

    context = {
      'id': mock_application['id'],
      'fio': mock_application['fio'],
      'offers': sorted_offers,
    }

    return render(request, 'application.html', context)

