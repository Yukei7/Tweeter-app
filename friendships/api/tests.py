from friendships.models import Friendship
from testing.testcases import TestCase
from rest_framework import status

FOLLOWINGS_URL = "/api/friendships/{}/followings/"
FOLLOWERS_URL = "/api/friendships/{}/followers/"
FOLLOW_URL = "/api/friendships/{}/follow/"
UNFOLLOW_URL = "/api/friendships/{}/unfollow/"


class FriendshipApiTests(TestCase):
    def setUp(self) -> None:
        self.user1 = self.create_user(
            username="user1"
        )
        self.user1_cli = self.create_user_cli(user=self.user1)
        self.user2 = self.create_user(
            username="user2"
        )
        self.user2_cli = self.create_user_cli(user=self.user2)
        # create follower
        for i in range(2):
            following = self.create_user(username=f"user1_following_{i}")
            Friendship.objects.create(from_user=self.user1, to_user=following)

        for i in range(3):
            follower = self.create_user(username=f"user1_follower_{i}")
            Friendship.objects.create(from_user=follower, to_user=self.user1)

    def test_follow_happy_path(self):
        n_friendships = Friendship.objects.count()
        # follow user1
        url = FOLLOW_URL.format(self.user1.id)
        response = self.user2_cli.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('user' in response.data)
        self.assertTrue('created_at' in response.data)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(response.data['user']['username'], self.user1.username)
        self.assertEqual(Friendship.objects.count(), n_friendships + 1)

        # multiple times
        response = self.user2_cli.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Friendship.objects.count(), n_friendships + 1)

    def test_follow_anonymous(self):
        url = FOLLOW_URL.format(self.user1.id)
        response = self.anonymous_cli.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_follow_by_get(self):
        url = FOLLOW_URL.format(self.user1.id)
        response = self.user2_cli.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_follow_yourself(self):
        url = FOLLOW_URL.format(self.user1.id)
        response = self.user1_cli.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unfollow_anonymous(self):
        url = UNFOLLOW_URL.format(self.user1.id)
        response = self.anonymous_cli.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unfollow_by_get(self):
        url = UNFOLLOW_URL.format(self.user1.id)
        response = self.user2_cli.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_unfollow_yourself(self):
        url = UNFOLLOW_URL.format(self.user1.id)
        response = self.user1_cli.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unfollow_happy_path(self):
        # create friendship for test
        Friendship.objects.create(from_user=self.user2, to_user=self.user1)

        n_friendships = Friendship.objects.count()
        url = UNFOLLOW_URL.format(self.user1.id)
        response = self.user2_cli.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Friendship.objects.count(), n_friendships - 1)

        # duplicate
        response = self.user2_cli.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(Friendship.objects.count(), n_friendships - 1)

    def test_followings_by_post(self):
        url = FOLLOWINGS_URL.format(self.user1.id)
        response = self.anonymous_cli.post(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_followings_happy_path(self):
        url = FOLLOWINGS_URL.format(self.user1.id)
        response = self.anonymous_cli.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['followings']), 2)
        # ordering
        ts0 = response.data['followings'][0]['created_at']
        ts1 = response.data['followings'][1]['created_at']
        self.assertTrue(ts0 > ts1)
        self.assertEqual(
            response.data['followings'][0]['user']['username'],
            'user1_following_1'
        )
        self.assertEqual(
            response.data['followings'][1]['user']['username'],
            'user1_following_0'
        )

    def test_follower_by_post(self):
        url = FOLLOWERS_URL.format(self.user1.id)
        response = self.anonymous_cli.post(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_follower_happy_path(self):
        url = FOLLOWERS_URL.format(self.user1.id)
        response = self.anonymous_cli.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['followers']), 3)
        # ordering
        ts0 = response.data['followers'][0]['created_at']
        ts1 = response.data['followers'][1]['created_at']
        ts2 = response.data['followers'][2]['created_at']
        self.assertTrue(ts0 > ts1)
        self.assertTrue(ts1 > ts2)
        self.assertEqual(
            response.data['followers'][0]['user']['username'],
            'user1_follower_2'
        )
        self.assertEqual(
            response.data['followers'][1]['user']['username'],
            'user1_follower_1'
        )
        self.assertEqual(
            response.data['followers'][2]['user']['username'],
            'user1_follower_0'
        )
