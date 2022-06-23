from accounts.api.serializers import UserSerializerForFriendship
from rest_framework import serializers
from friendships.models import Friendship


class FollowerSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='from_user')
    created_at = serializers.DateTimeField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at', )


class FollowingSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='to_user')
    created_at = serializers.DateTimeField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at', )


class FriendshipSerializerForCreate(serializers.Serializer):
    pass