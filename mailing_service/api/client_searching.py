
from .models import Client


def client_searching(mailing_filters):
    """Функция поиска клиентов фильтрам"""
    codes = mailing_filters.get('code')
    tags = mailing_filters.get('tag')
    if codes:
        code_list = codes.split(', ')
        clients = Client.objects.filter(code__in=code_list, tag=tags)
    else:
        clients = Client.objects.filter(tag=tags)
    return clients
