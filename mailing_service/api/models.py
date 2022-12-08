from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


class Mailing(models.Model):
    """Модель рассылки"""
    start_time = models.DateTimeField(
        'Дата и время начала рассылки',
        db_index=True
    )
    end_time = models.DateTimeField(
        'Дата и время конца рассылки',
        db_index=True
    )
    text = models.CharField(
        'Текст сообщения',
        max_length=200
    )
    mailing_filters = models.JSONField(
        'Фильтр свойств клиента'
    )

    def __str__(self):
        return (f'{self.id},'
                'время начала - {self.start_time}, '
                'время окончания {self.end_time}')

    class Meta:
        verbose_name = 'Mailing'
        verbose_name_plural = 'Mailings'


class Client(models.Model):
    """Модель клиента для рассылки"""
    cell = models.CharField(
        'Номер телефона',
        unique=True,
        validators=[
            RegexValidator(r'^7\d{10}$',
                           message='Телефонный номер не в формате 7XXXXXXXXXX')
        ],
        max_length=11,
    )
    code = models.CharField(
        'Код телефона',
        validators=[
            RegexValidator(r'^\d{3}$',
                           message='Код не из трёх цифр')
        ],
        max_length=3,
    )
    tag = models.CharField(
        'Тэг',
        db_index=True,
        max_length=200,
    )
    time_zone = models.CharField(
        'Часовой пояс',
        default='UTC',
        max_length=200,
    )

    def save(self, *args, **kwargs):
        self.code = str(self.cell)[1:4]
        return super(Client, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'


class Message(models.Model):
    """Модель сообщения"""
    date_created = models.DateTimeField(
        'Время создания',
        auto_now_add=True,
        db_index=True
    )
    send_status = models.CharField(
        'Статус отправки',
        choices=settings.SEND_CHOICES,
        max_length=7,
    )
    mailing = models.ForeignKey(
        Mailing,
        verbose_name='Рассылка',
        related_name='message',
        on_delete=models.CASCADE,
    )
    client = models.ForeignKey(
        Client,
        verbose_name='Клиент',
        related_name='client',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{id} - {self.send_status} - {self.mailing}'

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
