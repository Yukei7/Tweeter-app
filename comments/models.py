from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from tweets.models import Tweet
from likes.models import Like


class Comment(models.Model):
    # who leaves this comment
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # which tweet is commented
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    content = models.TextField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # order the tweet's comments by time
        index_together = (('tweet', 'created_at'), )
        ordering = ('-created_at',)

    def __str__(self):
        return "{} - {} says {} at tweet {}".format(
            self.created_at,
            self.user,
            self.content,
            self.tweet
        )

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Comment),
            object_id=self.id
        ).order_by('-created_at')
