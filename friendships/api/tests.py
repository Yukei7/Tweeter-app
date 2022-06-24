from django.contrib.auth.models import User
from friendships.models import Friendship
from testing.testcases import TestCase
from rest_framework.test import APIClient

FOLLOWING_URL = "/api/friendships/followings/"
FOLLOWER_URL = "/api/friendships/followers/"


class FriendshipApiTests(TestCase):
    def setUp(self) -> None:
        self.anonymous_cli = self.create_user_cli(user=None)
        self.user1 = self.create_user(
            username="user1"
        )
        self.user1_cli = self.create_user_cli(user=self.user1)

        self.user2 = self.create_user(
            username="user2"
        )

