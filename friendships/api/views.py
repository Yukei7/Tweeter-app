from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from friendships.models import Friendship
from friendships.api.serializers import (
    FollowerSerializer,
    FollowingSerializer,
    FriendshipSerializerForCreate,
)


class FriendshipViewSet(viewsets.GenericViewSet):
    serializer_class = FriendshipSerializerForCreate
    queryset = User.objects.all()

    # get followers
    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        # GET /api/friendships/1/followers
        friendships = Friendship.objects.filter(to_user_id=pk).order_by('-created_at')
        serializer = FollowerSerializer(friendships, many=True)
        return Response({'followers': serializer.data}, status=status.HTTP_200_OK)

    # get followings
    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        # GET /api/friendships/1/followings
        friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')
        serializer = FollowingSerializer(friendships, many=True)
        return Response({'followings': serializer.data}, status=status.HTTP_200_OK)

    def list(self, request):
        return Response({'message': "Friendship API"})

    # follow action
    # /api/friendships/<pk>/follow
    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        # check if pk exists, if not, raise 404 error
        self.get_object()

        serializer = FriendshipSerializerForCreate(data={
            'from_user_id': request.user.id,
            'to_user_id': pk,
        })

        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        friendship = serializer.save()
        return Response(FriendshipSerializerForCreate(friendship).data,
                        status=status.HTTP_201_CREATED)

    # unfollow action
    # /api/friendships/<pk>/follow
    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        # check if pk exists
        unfollow_user = self.get_object()

        # can't unfollow oneself
        if request.user.id == int(pk):
            return Response({
                'success': False,
                'message': 'You can\'t unfollow yourself',
            }, status=status.HTTP_400_BAD_REQUEST)

        # return number of rows that are deleted (delete on cascade)
        # and number of deleted rows for each type
        deleted, _ = Friendship.objects.filter(
            from_user=request.user,
            to_user=unfollow_user,
        ).delete()
        return Response({'success': True, 'deleted': deleted})
