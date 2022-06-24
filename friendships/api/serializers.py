from rest_framework.exceptions import ValidationError

from accounts.api.serializers import UserSerializerForFriendship
from rest_framework import serializers
from friendships.models import Friendship
from django.contrib.auth.models import User


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


class FriendshipSerializerForCreate(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id', )

    def validate(self, attrs):
        if attrs['from_user_id'] == attrs['to_user_id']:
            raise ValidationError({
                'message': 'You can\'t follow yourself'
            })

        if Friendship.objects.filter(
            from_user_id=attrs['from_user_id'],
            to_user=attrs['to_user_id'],
        ).exists():
            # already followed
            raise ValidationError({
                'message': 'You have already followed this user'
            })
        return attrs

    def create(self, validated_data):
        return Friendship.objects.create(
            from_user_id=validated_data['from_user_id'],
            to_user_id=validated_data['to_user_id'],
        )
