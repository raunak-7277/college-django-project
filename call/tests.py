from django.test import TestCase
from django.urls import reverse


class RouteRenderTests(TestCase):
    def test_home_page_renders(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_create_room_page_renders(self):
        response = self.client.get(reverse('create_room'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_room.html')

    def test_room_page_renders(self):
        response = self.client.get(reverse('room'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'room.html')
        self.assertContains(response, 'localVideo')

    def test_room_detail_page_renders(self):
        response = self.client.get(reverse('room_detail', kwargs={'room_id': 'team-sync'}))

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
