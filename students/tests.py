from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from rest_framework.test import APIClient

from .models import Student
from .views import get_student_count


class StudentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='rahim',
            password='123456',
        )
        self.other_user = User.objects.create_user(
            username='karim',
            password='123456',
        )
        self.student = Student.objects.create(
            name='Rahim',
            roll=101,
            email='rahim@gmail.com',
            department='CSE',
            age=20,
            created_by=self.user,
        )

    def test_student_name(self):
        self.assertEqual(self.student.name, 'Rahim')

    @override_settings(
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            },
        }
    )
    def test_student_count_is_cached_per_user(self):
        cache.set(f'student_count_{self.user.id}', 5, 300)

        self.assertEqual(get_student_count(self.user), 5)
        self.assertEqual(get_student_count(self.other_user), 0)
        self.assertEqual(cache.get(f'student_count_{self.other_user.id}'), 0)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 302)

    def test_create_student(self):
        self.client.login(username='rahim', password='123456')
        response = self.client.post(
            reverse('student_create'),
            {
                'name': 'Sumon',
                'roll': 102,
                'email': 's@gmail.com',
                'department': 'EEE',
                'age': 22,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Student.objects.filter(created_by=self.user).count(),
            2,
        )

    def test_other_user_cannot_delete_student(self):
        self.client.login(username='karim', password='123456')
        response = self.client.post(
            reverse('student_delete', args=[self.student.id])
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            Student.objects.filter(id=self.student.id).exists()
        )

    def test_api_requires_authentication(self):
        response = APIClient().get('/api/students/')

        self.assertEqual(response.status_code, 401)

    def test_api_with_jwt_only_returns_current_users_students(self):
        Student.objects.create(
            name='Karim',
            roll=202,
            email='karim@gmail.com',
            department='EEE',
            age=21,
            created_by=self.other_user,
        )
        client = APIClient()
        token_response = client.post(
            '/api/token/',
            {'username': 'rahim', 'password': '123456'},
            format='json',
        )
        self.assertEqual(token_response.status_code, 200)

        client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token_response.data['access']
        )
        response = client.get('/api/students/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.student.id)
