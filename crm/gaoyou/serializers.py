from rest_framework import serializers
from crm.gaoyou.models import EveryStatistics, FaceMatch


class CustomerTendencyViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = EveryStatistics
        fields = '__all__'


class FaceMatchViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceMatch
        fields = '__all__'
