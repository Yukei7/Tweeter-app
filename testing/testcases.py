from django.test import TestCase as DjangoTestCase
from django.contrib.auth.models import User
from tweets.models import Tweet
from rest_framework.test import APIClient


class TestCase(DjangoTestCase):
    def create_user(self, username, email=None, password=None):
        if password is None:
            password = 'test'
        if email is None:
            email = f'{username}@tweet.com'

        return User.objects.create_user(username, email, password)

    def create_tweet(self, user, content=None):
        if content is None:
            content = "Test content"
        return Tweet.objects.create(user=user, content=content)

    def create_user_cli(self, user=None):
        api_cli = APIClient()
        if user is not None:
            api_cli.force_authenticate(user)
        return api_cli
