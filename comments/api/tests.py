from testing.testcases import TestCase
from rest_framework import status
from comments.models import Comment
from django.utils import timezone

COMMENT_URL = '/api/comments/'
COMMENT_DETAIL_URL = '/api/comments/{}'


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
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_no_id(self):
        response = self.user1_cli.post(COMMENT_URL, {'content': 'Hello'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_too_long_content(self):
        response = self.user1_cli.post(COMMENT_URL, {'tweet_id': self.tweet.id, 'content': '1'*999})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('content' in response.data['errors'], True)

    def test_create_happy_path(self):
        response = self.user1_cli.post(COMMENT_URL, {'tweet_id': self.tweet.id, 'content': '1'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], '1')

    def test_destroy(self):
        comment = self.create_comment(self.user1, self.tweet)
        url = COMMENT_DETAIL_URL.format(comment.id)

        # have to log in
        response = self.anonymous_cli.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # only owner can delete
        response = self.user2_cli.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # owner can delete
        count = Comment.objects.count()
        response = self.user1_cli.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Comment.objects.count(), count - 1)

    def test_update(self):
        comment = self.create_comment(self.user1, self.tweet)
        url = COMMENT_DETAIL_URL.format(comment.id)
        another_tweet = self.create_tweet(self.user2)

        # have to log in
        response = self.anonymous_cli.put(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # only owner can update
        response = self.user2_cli.put(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # only able to update content
        before_updated_at = comment.updated_at
        before_created_at = comment.created_at
        now = timezone.now()
        response = self.user1_cli.put(url, {
            'content': 'new',
            'user_id': self.user2.id,
            'tweet_id': another_tweet.id,
            'created_at': now
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()  # update computer memory
        self.assertEqual(comment.content, 'new')
        self.assertEqual(comment.user, self.user1)
        self.assertEqual(comment.tweet, self.tweet)
        self.assertEqual(comment.created_at, before_created_at)
        self.assertNotEqual(comment.created_at, now)
        self.assertNotEqual(comment.updated_at, before_updated_at)
