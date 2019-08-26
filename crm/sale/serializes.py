from crm.user.models import UserBehavior
from rest_framework import serializers


class MatchFaceSerialize(serializers.ModelSerializer):
    created = serializers.CharField(allow_blank=False, read_only=True)
    result = serializers.CharField(allow_blank=False, read_only=True)
    lib_image_url = serializers.CharField(allow_blank=False, read_only=True)
    face_image_url = serializers.CharField(allow_blank=False, read_only=True)
    user = serializers.CharField(allow_blank=False, read_only=True)

    class Meta:
        model = UserBehavior
        fields = ['created', 'result', 'lib_image_url', 'face_image_url']
