import datetime

import pytz
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404

from .client_searching import client_searching
from .models import Mailing, Message
from .tasks import send_message

utc = pytz.UTC

@receiver(post_save, sender=Mailing, dispatch_uid='create_message')
def create_message(sender, instance, created, **kwargs):
    now = datetime.datetime.now(pytz.timezone('UTC'))
    now = datetime.datetime.strptime(now.strftime('%Y-%m-%d %H:%M:%S.%f'), '%Y-%m-%d %H:%M:%S.%f')
    if created:
        clients = client_searching(instance.mailing_filters)
        mailing = get_object_or_404(Mailing, id=instance.id)
        for client in clients:
            Message.objects.create(
                send_status="no sent",
                client=client,
                mailing=mailing
            )
            message = Message.objects.filter(
                mailing=instance.id, client=client.id
                ).first()
            data = {
                    'id': message.id,
                    "phone": client.cell,
                    "text": instance.text
                }
            if instance.start_time <= now <= instance.end_time:
                send_message.apply_async((data, client.id, instance.id),
                                         expires=instance.end_time)
            else:
                send_message.apply_async((data, client.id, instance.id),
                                         eta=instance.start_time,
                                         expires=instance.end_time)
