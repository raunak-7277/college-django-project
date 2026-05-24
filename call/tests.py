from django.test import TestCase, Client
from django.urls import reverse
from call.models import User, Meeting


class HomePageTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class RegisterTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_user(self):
        response = self.client.post('/register/', {
            'name': 'Raunak Kumar',
            'username': 'raunak',
            'password': 'test123',
            'confirm_password': 'test123'
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='raunak').exists())

class LoginTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create(
            name='Raunak Kumar',
            username='raunak',
            password='test123'
        )

    def test_login_success(self):
        response = self.client.post('/login/', {
            'username': 'raunak',
            'password': 'test123',
            'role': 'user'
        })

        self.assertEqual(response.status_code, 302)


class CreateRoomTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create(
            name='Raunak Kumar',
            username='raunak',
            password='test123',
            is_paid=True
        )

    def test_create_room(self):
        response = self.client.get(f'/create-room/?user={self.user.username}')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Meeting.objects.count(), 1)


class JoinRoomTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create(
            name='Raunak Kumar',
            username='raunak',
            password='test123'
        )

        self.meeting = Meeting.objects.create(
            creator=self.user,
            meeting_code='abcd1234',
            is_premium=False
        )

    def test_join_room(self):
        response = self.client.post(f'/join-room/?user={self.user.username}', {
            'room_id': 'abcd1234'
        })

        self.assertEqual(response.status_code, 302)


class RoomPageTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create(
            name='Raunak Kumar',
            username='raunak',
            password='test123'
        )

        self.meeting = Meeting.objects.create(
            creator=self.user,
            meeting_code='room123',
            is_premium=False
        )

    def test_room_page_loads(self):
        response = self.client.get(f'/room/room123/?user={self.user.username}')

        self.assertEqual(response.status_code, 200)