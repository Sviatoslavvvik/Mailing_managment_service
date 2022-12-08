from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Client, Mailing, Message
from .serializers import ClientSerializer, MailingSerializer


class ClientViewset(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']


class MailingViewset(viewsets.ModelViewSet):
    queryset = Mailing.objects.all()
    serializer_class = MailingSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        detail=False,
        methods=('GET',),
    )
    def general_info(self, request):
        mailing_count = Mailing.objects.count()
        mailing_message_queryset = Message.objects.select_related(
            'mailing').all()
        sent_message_count = mailing_message_queryset.filter(
            send_status='sent').count()
        no_sent_message_count = mailing_message_queryset.filter(
            send_status='no sent').count()
        result = {
            'Общее количество рассылок:': mailing_count,
            'Отправлено сообщений:': sent_message_count,
            'Не отправлено сообщений:': no_sent_message_count,
        }
        return Response(result)

    @action(
        detail=True,
        methods=('GET',),
    )
    def precise_info(self, request, pk):
        precise_mailing = get_object_or_404(Mailing, id=pk)
        messages = precise_mailing.message.all()
        sent_message_count = messages.filter(send_status='sent').count()
        no_sent_message_count = messages.filter(
            send_status='no sent').count()
        result = {
            'Рассылка:': (f'{pk} - время начала {precise_mailing.start_time}'
                          f' - конец {precise_mailing.end_time}'),
            'Отправлено сообщений:': sent_message_count,
            'Не отправлено сообщений:': no_sent_message_count,
        }
        return Response(result)