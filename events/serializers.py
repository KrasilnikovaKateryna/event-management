from rest_framework import serializers
from events.models import Event
from django.utils.timezone import now



class EventSerializer(serializers.ModelSerializer):
    organizer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'location', 'organizer']

    def validate_date(self, value):
        """Проверяем, что дата события не в прошлом"""
        if value < now():
            raise serializers.ValidationError("Event date cannot be in the past.")
        return value