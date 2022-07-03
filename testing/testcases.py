from django.test import TestCase as DjangoTestCase
from django.contrib.auth.models import User
from tweets.models import Tweet
from comments.models import Comment
from rest_framework.test import APIClient


class TestCase(DjangoTestCase):
    @property
    def anonymous_cli(self):
        if hasattr(self, '_anonymous_cli'):
            return self._anonymous_cli
        self._anonymous_cli = APIClient()
        return self._anonymous_cli

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
        assert user is not None
        api_cli = APIClient()
        api_cli.force_authenticate(user)
        return api_cli

    def create_comment(self, user, tweet, content=None):
        if content is None:
            content = 'default comment content'

        return Comment.objects.create(user=user, tweet=tweet, content=content)

