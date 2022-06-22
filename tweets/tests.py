from django.contrib.auth.models import User
from django.test import TestCase
from tweets.models import Tweet
from datetime import timedelta
from utils.time_helpers import utc_now


class TweetTests(TestCase):

    @staticmethod
    def createUser(username, email, password):
        return User.objects.create_user(username, email, password)

    def setUp(self) -> None:
        self.user = self.createUser(
            username='mytest',
            email='test@tweeter.com',
            password='mytest',
        )

    def test_hours_to_now(self):
        tweet = Tweet.objects.create(user=self.user)
        tweet.created_at = utc_now() - timedelta(hours=10)
        tweet.save()
        self.assertEqual(tweet.hours_to_now, 10)
