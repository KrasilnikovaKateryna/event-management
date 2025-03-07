from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from events.models import Event

User = get_user_model()


class EventViewSetTestCase(TestCase):
    def setUp(self):
        self.client_organizer = APIClient()
        self.client_user = APIClient()
        self.organizer = User.objects.create_user(email='organizer@gmail.com', password='testpass')
        self.user = User.objects.create_user(email='user@gmail.com', password='testpass')
        self.event = Event.objects.create(title='Test Event', description='Test Description', location='Test Location',
                                          date='2025-12-31', organizer=self.organizer)
        self.client_organizer.force_authenticate(user=self.organizer)
        self.client_user.force_authenticate(user=self.user)

    def test_list_events(self):
        response = self.client_organizer.get('/events/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_event(self):
        response = self.client_organizer.post('/events/', {
            'title': 'New Event',
            'description': 'New Description',
            'location': 'New Location',
            'date': '2025-12-31',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_event(self):
        response = self.client_organizer.get(f'/events/{self.event.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_event(self):
        response = self.client_organizer.put(f'/events/{self.event.pk}/',
                                   {'title': 'Updated Event', 'description': 'Updated Description',
                                    'location': 'Updated Location', 'date': '2025-12-31'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_event(self):
        response = self.client_organizer.delete(f'/events/{self.event.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_register_user_to_event(self):
        response = self.client_organizer.post(f'/events/{self.event.pk}/register/', {'email': 'user@gmail.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.event.attendees.count(), 1)

    def test_unregister_user_from_event(self):
        self.event.attendees.add(self.user)
        response = self.client_organizer.post(f'/events/{self.event.pk}/unregister/', {'email': 'user@gmail.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.event.attendees.count(), 0)

    def test_search_event(self):
        response = self.client_organizer.get('/events/', {'search': 'New Event'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # negative test cases

    def test_create_event_no_auth(self):
        self.client_organizer.force_authenticate(user=None)
        response = self.client_organizer.post('/events/', {
            'title': 'New Event',
            'description': 'New Description',
            'location': 'New Location',
            'date': '2025-12-31',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_event_past_date(self):
        response = self.client_organizer.post('/events/', {
            'title': 'New Event',
            'description': 'New Description',
            'location': 'New Location',
            'date': '2022-12-31',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_nonexistent_event(self):
        response = self.client_organizer.get('/events/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_event_no_auth(self):
        self.client_organizer.force_authenticate(user=None)
        response = self.client_organizer.put(f'/events/{self.event.pk}/',
                                   {'title': 'Updated Event', 'description': 'Updated Description',
                                    'location': 'Updated Location', 'date': '2022-12-31'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_event_no_auth(self):
        self.client_organizer.force_authenticate(user=None)
        response = self.client_organizer.delete(f'/events/{self.event.pk}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_search_event_no_results(self):
        response = self.client_organizer.get('/events/', {'search': 'Nonexistent'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_register_user_to_event_no_auth(self):
        self.client_organizer.force_authenticate(user=None)
        response = self.client_organizer.post(f'/events/{self.event.pk}/register/', {'email': 'user@gmail.com'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_user_to_event_no_email(self):
        response = self.client_organizer.post(f'/events/{self.event.pk}/register/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_to_event_nonexistent_user(self):
        response = self.client_organizer.post(f'/events/{self.event.pk}/register/', {'email': 'nonexistent_user@gmail.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_to_event_registered_user(self):
        self.event.attendees.add(self.user)
        response = self.client_organizer.post(f'/events/{self.event.pk}/register/', {'email': 'user@gmail.com'})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_unregister_user_to_event_no_email(self):
        response = self.client_organizer.post(f'/events/{self.event.pk}/unregister/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unregister_user_to_event_nonexistent_user(self):
        response = self.client_organizer.post(f'/events/{self.event.pk}/unregister/', {'email': 'nonexistent_user@gmail.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unregister_user_from_event_not_registered(self):
        response = self.client_organizer.post(f'/events/{self.event.pk}/unregister/', {'email': 'user@gmail.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unregister_user_from_event_no_auth(self):
        self.client_organizer.force_authenticate(user=None)
        response = self.client_organizer.post(f'/events/{self.event.pk}/unregister/', {'email': 'user@gmail.com'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenTestCase(TestCase):
    def setUp(self):
        self.client_organizer = APIClient()
        self.client_user = APIClient()
        self.user = User.objects.create_user(email='testuser@gmail.com', password='testpass')

    def test_token_obtain_pair(self):
        response = self.client_organizer.post('/api/token/', {'email': 'testuser@gmail.com', 'password': 'testpass'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)

    def test_token_refresh(self):
        response = self.client_organizer.post('/api/token/', {'email': 'testuser@gmail.com', 'password': 'testpass'})
        refresh_token = response.data['refresh']
        response = self.client_organizer.post('/api/token/refresh/', {'refresh': refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)

    def test_token_obtain_pair_invalid_credentials(self):
        response = self.client_organizer.post('/api/token/', {'email': 'testuser@gmail.com', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_invalid_token(self):
        response = self.client_organizer.post('/api/token/refresh/', {'refresh': 'invalidtoken'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)