from testing.testcases import TestCase
from tweets.models import Tweet
from rest_framework import status

TWEET_LIST_API = '/api/tweets/'
TWEET_CREATE_API = '/api/tweets/'


class TweetApiTests(TestCase):

    def setUp(self) -> None:

        self.user1 = self.create_user('user1')
        self.tweet1 = [
            self.create_tweet(self.user1)
            for _ in range(3)
        ]
        self.user1_client = self.create_user_cli(user=self.user1)

        self.user2 = self.create_user('user2')
        self.tweet2 = [
            self.create_tweet(self.user2)
            for _ in range(2)
        ]

    def test_list_api_anonymous(self):
        response = self.anonymous_cli.get(TWEET_LIST_API)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_query_api_happy_path(self):
        response = self.anonymous_cli.get(TWEET_LIST_API, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['tweets']), 3)
        response = self.anonymous_cli.get(TWEET_LIST_API, {'user_id': self.user2.id})
        self.assertEqual(len(response.data['tweets']), 2)
        # check ordering
        self.assertEqual(response.data['tweets'][0]['id'], self.tweet2[1].id)
        self.assertEqual(response.data['tweets'][1]['id'], self.tweet2[0].id)

    def test_create_api_anonymous(self):
        response = self.anonymous_cli.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_api_no_content(self):
        response = self.user1_client.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_api_empty_content(self):
        response = self.user1_client.post(TWEET_CREATE_API, {'content': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_api_long_content(self):
        response = self.user1_client.post(TWEET_CREATE_API, {'content': '1' * 300})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_api_happy_path(self):
        num_tweets = Tweet.objects.count()
        response = self.user1_client.post(
            TWEET_CREATE_API,
            {'content': 'Testing create api'},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(Tweet.objects.count(), num_tweets + 1)
