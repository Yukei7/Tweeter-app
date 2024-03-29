from testing.testcases import TestCase
from rest_framework import status
from comments.models import Comment
from django.utils import timezone

COMMENT_URL = '/api/comments/'
COMMENT_DETAIL_URL = '/api/comments/{}/'
TWEET_LIST_API = '/api/tweets/'
TWEET_DETAIL_API = '/api/tweets/{}/'
NEWSFEED_LIST_API = '/api/newsfeeds/'


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

    def test_list(self):
        # must have tweet_id
        response = self.anonymous_cli.get(COMMENT_URL)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # with tweet_id
        response = self.anonymous_cli.get(COMMENT_URL, {
            'tweet_id': self.tweet.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['comments']), 0)

        # comments order by time
        self.create_comment(self.user1, self.tweet, '1')
        self.create_comment(self.user2, self.tweet, '2')
        self.another_tweet = self.create_tweet(self.user2)
        self.create_comment(self.user2, self.another_tweet, '3')
        response = self.anonymous_cli.get(COMMENT_URL, {
            'tweet_id': self.tweet.id
        })
        self.assertEqual(len(response.data['comments']), 2)
        self.assertEqual(response.data['comments'][0]['content'], '1')
        self.assertEqual(response.data['comments'][1]['content'], '2')

        # provide both of user_id and tweet_id, only tweet_id works
        response = self.anonymous_cli.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'user_id': self.user1.id
        })
        self.assertEqual(len(response.data['comments']), 2)

    def test_comments_count(self):
        # create tweet and comment
        tweet = self.create_tweet(self.user1)
        url = TWEET_DETAIL_API.format(tweet.id)
        response = self.user1_cli.get(url)
        # no comments
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments_count'], 0)

        # test tweet list api
        self.create_comment(self.user1, tweet)
        response = self.user1_cli.get(TWEET_LIST_API, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['tweets'][0]['comments_count'], 1)

        # test newsfeeds list api
        self.create_comment(self.user2, tweet)
        self.create_newsfeed(self.user1, tweet)
        response = self.user1_cli.get(NEWSFEED_LIST_API)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['newsfeeds'][0]['tweet']['comments_count'], 2)
