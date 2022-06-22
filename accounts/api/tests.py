from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User


LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'


class AccountAPITests(TestCase):

    @staticmethod
    def createUser(username, email, password):
        return User.objects.create_user(username, email, password)

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = self.createUser(
            username='mytest',
            email='test@tweeter.com',
            password='mytest',
        )
        self.signup_data = {
            'username': 'someone',
            'email': 'someone@tweeter.com',
            'password': 'someone',
        }

    def test_login_method(self):
        response = self.client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': 'mytest'
        })
        self.assertEqual(response.status_code, 405)

    def test_login_password(self):
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'wrongpw'
        })
        self.assertEqual(response.status_code, 400)

    def test_login_happy_path(self):
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'mytest'
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['user'], None)
        self.assertEqual(response.data['user']['email'], 'test@tweeter.com')

        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_login_status(self):
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

    def test_logout(self):
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'mytest'
        })
        # check if logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

        # log out: wrong method
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        # log out happy path
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

    def test_signup_happy_path(self):
        response = self.client.post(SIGNUP_URL, self.signup_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['username'], 'someone')
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_signup_method(self):
        response = self.client.get(SIGNUP_URL, self.signup_data)
        self.assertEqual(response.status_code, 405)

    def test_signup_email(self):
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'messy email address',
            'password': 'someone'
        })
        self.assertEqual(response.status_code, 400)

    def test_signup_password(self):
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'someone@tweeter.com',
            'password': '1'
        })
        self.assertEqual(response.status_code, 400)

    def test_signup_username(self):
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone has tooooooooo long username',
            'email': 'someone@tweeter.com',
            'password': 'someone'
        })
        self.assertEqual(response.status_code, 400)
