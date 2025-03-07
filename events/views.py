from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from events.models import Event
from events.permissions import IsOwnerPermission
from events.serializers import EventSerializer

from users.models import User


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerPermission]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'location']

    def perform_create(self, serializer):
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save(organizer=self.request.user)
        except ValidationError as e:
            raise ValidationError({"error": str(e.detail)}, code=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        attendee_email = request.data.get('email')
        if not attendee_email:
            return Response({'message': 'email is not defined'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            attendee = User.objects.get(email=attendee_email)
        except User.DoesNotExist:
            return Response({'message': 'user with such email does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        event = self.get_object()

        if attendee in event.attendees.all():
            return Response({'message': 'user with this email has been already registered'}, status=status.HTTP_409_CONFLICT)

        event.attendees.add(attendee)

        # Отправляем email
        subject = f"You were registered to event '{event.title}'"
        message = f"Organizer {event.organizer.email} registered you as a attendee to the event '{event.title}'."
        recipient_list = [attendee_email]

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            recipient_list,
            fail_silently=False
        )

        return Response({'status': 'registered'})

    @action(detail=True, methods=['post'])
    def unregister(self, request, pk=None):
        attendee_email = request.data.get('email')
        if not attendee_email:
            return Response({'message': 'email is not defined'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            attendee = User.objects.get(email=attendee_email)
        except User.DoesNotExist:
            return Response({'message': 'user with such email does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        event = self.get_object()
        if attendee in event.attendees.all():
            event.attendees.remove(attendee)
            return Response({'status': 'unregistered'})
        else:
            return Response({'status': 'not registered'}, status=status.HTTP_400_BAD_REQUEST)


def api_documentation(request):
    return render(request, 'doc.html')