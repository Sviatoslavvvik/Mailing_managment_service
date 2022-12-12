from rest_framework import serializers

from .models import Client, Mailing, Message


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('id', 'cell', 'code', 'tag', 'time_zone')
        read_only_fields = ('code',)


class MailingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mailing
        fields = '__all__'

    def validate_mailing_filters(self, value):
        if 'tag' not in value.keys() and 'code' not in value.keys():
            raise serializers.ValidationError(
                'mailing_filters должно содержать поля tag, code'
                )
        return value


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
