from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase as DjangoTestCase
from rest_framework.test import APIClient

from comments.models import Comment
from likes.models import Like
from newsfeeds.models import NewsFeed
from tweets.models import Tweet


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

    def create_newsfeed(self, user, tweet):
        return NewsFeed.objects.create(user=user, tweet=tweet)

    def create_like(self, user, target):
        instance, _ = Like.objects.get_or_create(
            object_id=target.id,
            content_type=ContentType.objects.get_for_model(target.__class__),
            user=user
        )
        return instance
