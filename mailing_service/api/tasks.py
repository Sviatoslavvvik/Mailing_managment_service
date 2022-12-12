import datetime
import os
import smtplib

import pytz
import requests
from celery.utils.log import get_task_logger
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from dotenv import load_dotenv

from mailing_service.celery import app

from .models import Client, Mailing, Message

load_dotenv()
logger = get_task_logger(__name__)


@app.task(bind=True, retry_backoff=True)
def send_message(
                self, data, client_id, mailing_id,
                url=os.getenv('URL'), token=os.getenv('TOKEN')
                ):
    mail = get_object_or_404(Mailing, id=mailing_id)
    client = get_object_or_404(Client, id=client_id)
    timezone = pytz.timezone(client.time_zone)
    now = datetime.datetime.now(timezone)
    now = datetime.datetime.strptime(
        now.strftime('%Y-%m-%d %H:%M:%S.%f'), '%Y-%m-%d %H:%M:%S.%f')

    if mail.start_time <= now <= mail.end_time:
        header = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'}
        try:
            requests.post(
                url=url + str(data.get('id')), headers=header, json=data)
        except requests.exceptions.RequestException as exc:
            logger.error(f"Сообщение с {data.get('id')} не отправлено")
            raise self.retry(exc=exc)
        else:
            logger.info(f"Сообщение {data.get('id')} отправлено")
            Message.objects.filter(pk=data.get('id')).update(
                send_status='sent')
    else:
        time = (mail.start_time - now).seconds
        logger.info(f"сообщение {data.get('id')} пока не отправлено, "
                    f"время отправки не подошло"
                    f"отправка через {time} секунд")
        return self.retry(countdown=time)


@app.task(bind=True, retry_backoff=True)
def send_statistics():
    now = datetime.datetime.now()
    period = datetime.timedelta(hours=24)
    start_period = now - period
    mailing_last_24h = Mailing.objects.filter(
        start_time__gte=start_period,
        end_time__lte=now)
    message = 'За последние 24 ч были сделаны рассылки: \n'
    for mailing in mailing_last_24h:
        message += mailing + '\n'
    try:
        send_mail(message, ['some_mail@123.com', ])
    except smtplib.SMTPException:
        logger.error(f'email за {now.date()} не отправлен')
    else:
        logger.info(f'сообщение за  {now.date()} успешно отправлено')
