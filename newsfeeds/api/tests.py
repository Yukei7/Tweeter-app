from testing.testcases import TestCase
from rest_framework import status


NEWSFEEDS_URL = '/api/newsfeeds/'
POST_TWEETS_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendships/{}/follow/'


class NewsFeedApiTest(TestCase):

    def setUp(self):
        self.user1 = self.create_user(username='testuser1')
        self.user1_client = self.create_user_cli(self.user1)

        self.user2 = self.create_user(username='testuser2')
        self.user2_client = self.create_user_cli(self.user2)

    def test_newsfeeds_anonymous(self):
        response = self.anonymous_cli.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_newsfeeds_by_post(self):
        print(NEWSFEEDS_URL)
        response = self.user1_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_newsfeeds_happy_path(self):
        # use get, success
        response = self.user1_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['newsfeeds']), 0)
        # self post a tweet
        self.user1_client.post(POST_TWEETS_URL, {'content': "hello world."})
        response = self.user1_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['newsfeeds']), 1)
        self.assertEqual(response.data['newsfeeds'][0]['tweet']['user']['id'], self.user1.id)
        # follow user2, and user2 post a tweet
        self.user1_client.post(FOLLOW_URL.format(self.user2.id))
        response = self.user2_client.post(POST_TWEETS_URL, {'content': 'hello LA!'})
        posted_tweet_id = response.data['id'] # check id match
        response = self.user1_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['newsfeeds']), 2)
        self.assertEqual(response.data['newsfeeds'][0]['tweet']['id'], posted_tweet_id)
