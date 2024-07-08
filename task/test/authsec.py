from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from task.users.models import Organisation

User = get_user_model()

class GetUserRecordTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com', password='testpassword123', firstName='Test', lastName='User')
        self.other_user = User.objects.create_user(
            email='otheruser@example.com', password='testpassword123', firstName='Other', lastName='User')
        self.third_user = User.objects.create_user(
            email='thirduser@example.com', password='testpassword123', firstName='Third', lastName='User')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.organisation = Organisation.objects.create(name='Test Organisation', description='Test description')
        self.user.organisations.add(self.organisation)
        self.other_user.organisations.add(self.organisation)

    def test_get_own_record(self):
        url = reverse('get_user_record', kwargs={'id': self.user.userId})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['email'], self.user.email)

    def test_get_other_user_in_same_organisation(self):
        url = reverse('get_user_record', kwargs={'id': self.other_user.userId})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['email'], self.other_user.email)

    def test_get_user_in_different_organisation(self):
        url = reverse('get_user_record', kwargs={'id': self.third_user.userId})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'You do not have permission to view this user.')

class AddUserToOrganisationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com', password='testpassword123', firstName='Test', lastName='User')
        self.other_user = User.objects.create_user(
            email='otheruser@example.com', password='testpassword123', firstName='Other', lastName='User')
        self.third_user = User.objects.create_user(
            email='thirduser@example.com', password='testpassword123', firstName='Third', lastName='User')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.organisation = Organisation.objects.create(name='Test Organisation', description='Test description')
        self.user.organisations.add(self.organisation)

    def test_add_user_to_organisation(self):
        url = reverse('add_user', kwargs={'orgId': self.organisation.orgId})
        data = {'userId': str(self.other_user.userId)}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.other_user.organisations.filter(pk=self.organisation.orgId).exists())

    def test_add_user_to_nonexistent_organisation(self):
        url = reverse('add_user', kwargs={'orgId': 'nonexistent-org-id'})
        data = {'userId': str(self.other_user.userId)}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_nonexistent_user_to_organisation(self):
        url = reverse('add_user', kwargs={'orgId': self.organisation.orgId})
        data = {'userId': 'nonexistent-user-id'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserRegistrationTests(APITestCase):
    def test_register_user(self):
        url = reverse('register')
        data = {
            'email': 'test@example.com',
            'password': 'testpassword123',
            'firstName': 'Test',
            'lastName': 'User',
            'phone': '1234567890'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('accessToken', response.data['data'])

    def test_token_expiration(self):
        url = reverse('register')
        data = {
            'email': 'test@example.com',
            'password': 'testpassword123',
            'firstName': 'Test',
            'lastName': 'User',
            'phone': '1234567890'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        access_token = response.data['data']['accessToken']
        refresh = RefreshToken(access_token)
        self.assertFalse(refresh.access_token.is_expired)

class OrganisationAccessTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com', password='testpassword123', firstName='Test', lastName='User')
        self.other_user = User.objects.create_user(
            email='otheruser@example.com', password='testpassword123', firstName='Other', lastName='User')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.organisation = Organisation.objects.create(name='Test Organisation', description='Test description')
        self.user.organisations.add(self.organisation)

    def test_user_organisation_access(self):
        url = reverse('get_or_create_organisations')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['organisations']), 1)
        self.assertEqual(response.data['data']['organisations'][0]['name'], 'Test Organisation')

    def test_organisation_access_restriction(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse('get_or_create_organisations')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['organisations']), 0)