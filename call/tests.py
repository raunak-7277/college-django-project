from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User as AuthUser

from .models import User, Staff, Meeting


class RouteRenderTests(TestCase):
    def test_home_page_renders(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_create_room_page_renders(self):
        response = self.client.get(reverse('create_room'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))

    def test_room_page_renders(self):
        response = self.client.get(reverse('room_detail', kwargs={'room_id': 'team-sync'}))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))

    def test_room_detail_page_renders(self):
        user = User.objects.create(name='Test User', username='testuser', password='pass')
        Meeting.objects.create(creator=user, meeting_code='team-sync')
        response = self.client.get(
            reverse('room_detail', kwargs={'room_id': 'team-sync'}),
            {'user': user.username},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'room.html')
        self.assertEqual(response.context['room_id'], 'team-sync')

    def test_login_page_renders(self):
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_register_page_renders(self):
        response = self.client.get(reverse('register'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_member_login_uses_existing_app_user_flow(self):
        User.objects.create(name='Member User', username='member', password='pass')

        response = self.client.post(reverse('login'), {
            'role': 'user',
            'username': 'member',
            'password': 'pass',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/dashboard/?user=member')

    def test_staff_login_redirects_to_staff_dashboard(self):
        Staff.objects.create(
            name='Staff User',
            username='staff',
            password='pass',
        )

        response = self.client.post(reverse('login'), {
            'role': 'staff',
            'username': 'staff',
            'password': 'pass',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('staff_dashboard'))

    def test_admin_login_redirects_to_django_admin(self):
        AuthUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='pass',
        )

        response = self.client.post(reverse('login'), {
            'role': 'admin',
            'username': 'admin',
            'password': 'pass',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/admin/')

    def test_end_meeting_records_end_time(self):
        creator = User.objects.create(name='Creator', username='creator', password='pass')
        meeting = Meeting.objects.create(creator=creator, meeting_code='team-sync')

        response = self.client.post(
            reverse('end_meeting', kwargs={'room_id': meeting.meeting_code}),
            {'user': creator.username},
        )

        meeting.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(meeting.ended_at)
