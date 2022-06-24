from django.db import models
from django.contrib.auth.models import User


class Friendship(models.Model):
    # Related name: following_friendship_set
    # => User.objects.filter(following_friendship_set=user)
    from_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="following_friendship_set",
    )
    # Related name: follower_friendship_set
    # => User.objects.filter(follower_friendship_set=user)
    to_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="follower_friendship_set",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            ('from_user_id', 'created_at'),
            ('to_user_id', 'created_at'),
        )
        unique_together = (('from_user_id', 'to_user_id'), )
        ordering = ('-created_at', )

    def __str__(self):
        return f"{self.from_user.id} followed {self.to_user.id}"
