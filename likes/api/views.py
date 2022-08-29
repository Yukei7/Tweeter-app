from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from likes.models import Like
from utils.decorators import required_param
from accounts.api.serializers import UserSerializerForLike
from likes.api.serializers import (
    LikeSerializerForCreate,
    LikeSerializerForCancel,
    LikeSerializer
)


class LikeViewSet(viewsets.GenericViewSet):
    queryset = Like.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializerForLike

    @required_param(request_attr='data', params=['content_type', 'object_id'])
    def create(self, request, *args, **kwargs):
        serializer = LikeSerializerForCreate(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                'errors': serializer.errors,
                'message': 'Please check your input',
            }, status=status.HTTP_400_BAD_REQUEST)

        like = serializer.save()
        return Response(
            LikeSerializer(like).data,
            status=status.HTTP_201_CREATED
        )

    @action(methods=['POST'], detail=False)
    @required_param(request_attr='data', params=['content_type', 'object_id'])
    def cancel(self, request):
        serializer = LikeSerializerForCancel(
            data=request.data,
            context={'request': request}
        )
        if not serializer.is_valid():
            return Response({
                'message': 'Please check your input.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        is_deleted = serializer.cancel()

        return Response({
            'success': True,
            'deleted': is_deleted
        }, status=status.HTTP_200_OK)
