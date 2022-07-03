from testing.testcases import TestCase
from rest_framework import status

COMMENT_URL = '/api/comments/'


class CommentApiTests(TestCase):
    def setUp(self) -> None:
        self.user1 = self.create_user('user1')
        self.user1_cli = self.create_user_cli(self.user1)
        self.tweet = self.create_tweet(self.user1)

        self.user2 = self.create_user('user2')
        self.user2_cli = self.create_user_cli(self.user2)

    def test_create_anonymous(self):
        response = self.anonymous_cli.post(COMMENT_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_null(self):
        response = self.user1_cli.post(COMMENT_URL)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_no_content(self):
        response = self.user1_cli.post(COMMENT_URL, {'tweet_id': self.tweet.id})
        self.assertEqual(response.status_code, 400)

    def test_create_no_id(self):
        response = self.user1_cli.post(COMMENT_URL, {'content': 'Hello'})
        self.assertEqual(response.status_code, 400)

    def test_create_too_long_content(self):
        response = self.user1_cli.post(COMMENT_URL, {'tweet_id': self.tweet.id, 'content': '1'*999})
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content' in response.data['errors'], True)

    def test_create_happy_path(self):
        response = self.user1_cli.post(COMMENT_URL, {'tweet_id': self.tweet.id, 'content': '1'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], '1')

