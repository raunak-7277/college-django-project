from django.test import TestCase, Client
from django.utils import timezone
from call.models import User, Meeting, Staff


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


class StaffDashboardTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.staff = Staff.objects.create(
            name='Staff User',
            username='staff',
            password='staff123',
            is_active=True
        )

        session = self.client.session
        session['staff_id'] = self.staff.id
        session.save()

    def test_staff_dashboard_shows_ten_users_per_page_ordered_by_latest_call(self):
        older_user = User.objects.create(
            name='Older User',
            username='older',
            password='test123'
        )
        latest_user = User.objects.create(
            name='Latest User',
            username='latest',
            password='test123'
        )

        for index in range(10):
            User.objects.create(
                name=f'Extra User {index}',
                username=f'extra{index}',
                password='test123'
            )

        older_meeting_time = timezone.now() - timezone.timedelta(days=2)
        latest_meeting_time = timezone.now() - timezone.timedelta(hours=1)
        latest_end_time = timezone.now()

        Meeting.objects.create(
            creator=older_user,
            meeting_code='older123',
            created_at=older_meeting_time,
            ended_at=older_meeting_time + timezone.timedelta(minutes=10)
        )
        Meeting.objects.create(
            creator=latest_user,
            meeting_code='latest12',
            created_at=latest_meeting_time,
            ended_at=latest_end_time
        )

        response = self.client.get('/staff-dashboard/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['app_users']), 10)
        self.assertEqual(response.context['app_users'][0], latest_user)
        self.assertContains(response, latest_end_time.strftime('%d %b %Y'))
        self.assertNotContains(response, latest_end_time.strftime('%I:%M %p'))
        self.assertContains(response, 'Print PDF')
        self.assertTrue(response.context['page_obj'].has_next())
