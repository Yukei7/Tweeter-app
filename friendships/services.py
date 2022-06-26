from friendships.models import Friendship
from django.contrib.auth.models import User


class FriendshipService:

    @classmethod
    def get_followers(cls, user):
        friendships = Friendship.objects.filter(to_user=user).prefetch_related('from_user')
        return [friendship for friendship in friendships]
