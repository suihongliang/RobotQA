from rest_framework import serializers
from ..user.models import (
    BaseUser,
    UserInfo,
    UserOnlineOrder,
    )
from ..sale.models import (
    Seller,
    )
from ..discount.models import (
    CoinRule,
    UserCoinRecord,
    )
from ..discount.tasks import (
    SyncCoinTask,
    )
# import time
from rest_framework.utils import model_meta
import traceback
import django
# import json


def get_or_create_user(mobile, store_code):
    user = BaseUser.objects.origin_all().filter(
        mobile=mobile, store_code=store_code).first()
    if not user:
        user = BaseUser.objects.create(
            mobile=mobile, store_code=store_code)
    return user


class BaseUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = BaseUser
        fields = (
            'mobile',
            'store_code',
        )


class UserInfoSerializer(serializers.ModelSerializer):

    gender_display = serializers.CharField(source='get_gender_display')
    status_display = serializers.CharField(source='get_status_display')

    class Meta:
        model = UserInfo
        fields = (
            'user',
            'mobile',
            'name',
            'age',
            'gender',
            'status',
            'note',
            'willingness',
            'net_worth',
            'created',
            'is_seller',
            'gender_display',
            'status_display',
        )
        read_only_fields = (
            'user', 'created', 'mobile', 'is_seller', 'gender_display',
            'status_display')


class UserOnlineOrderSerializer(serializers.ModelSerializer):

    order = serializers.SerializerMethodField('get_custom_order')

    def get_custom_order(self, instance):
        return {}

    class Meta:
        model = UserOnlineOrder
        fields = (
            'user',
            'mobile',
            'created',
            'location',
            'order',
        )


class SellerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Seller
        fields = (
            'user',
            'created',
            'mobile',
            'code',
            'qr_code_url',
            'name',
            'is_active',
        )
        read_only_fields = (
            'user', 'created', 'mobile', 'qr_code_url', 'code',
            'is_active')


class UpdateSellerSerializer(serializers.ModelSerializer):

    is_seller = serializers.BooleanField(
        help_text='是否是销售', write_only=True)

    class Meta:
        model = Seller
        fields = (
            'user',
            'is_seller',
        )
        read_only_fields = ('user',)


class CreateSellerSerializer(serializers.ModelSerializer):

    mobile = serializers.CharField(
        help_text='手机号', max_length=20, write_only=True)
    store_code = serializers.CharField(
        help_text='门店编号', max_length=10, write_only=True)

    def create(self, validated_data):
        mobile = validated_data.pop('mobile')
        store_code = validated_data.pop('store_code')
        user = get_or_create_user(mobile, store_code)
        user.userinfo.is_seller = True
        user.userinfo.save()

        ModelClass = self.Meta.model

        info = model_meta.get_field_info(ModelClass)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)

        try:
            instance = ModelClass._default_manager.create(
                user=user, **validated_data)
        except TypeError:
            tb = traceback.format_exc()
            msg = (
                'Got a `TypeError` when calling `%s.%s.create()`. '
                'This may be because you have a writable field on the '
                'serializer class that is not a valid argument to '
                '`%s.%s.create()`. You may need to make the field '
                'read-only, or override the %s.create() method to handle '
                'this correctly.\nOriginal exception was:\n %s' %
                (
                    ModelClass.__name__,
                    ModelClass._default_manager.name,
                    ModelClass.__name__,
                    ModelClass._default_manager.name,
                    self.__class__.__name__,
                    tb
                )
            )
            raise TypeError(msg)
        except django.db.utils.IntegrityError:
            raise serializers.ValidationError("用户已创建")

        if many_to_many:
            for field_name, value in many_to_many.items():
                field = getattr(instance, field_name)
                field.set(value)

        return instance

    class Meta:
        model = Seller
        fields = (
            'mobile',
            'store_code',
            'name',
        )


class CoinRuleSerializer(serializers.ModelSerializer):

    category_display = serializers.CharField(source='get_category_display')

    class Meta:
        model = CoinRule
        fields = (
            'category',
            'category_display',
            'coin',
            'qr_code_url',
        )
        read_only_fields = ('category', 'category_display', 'qr_code_url',
                            'store_code',)


class UserCoinRecordSerializer(serializers.ModelSerializer):

    user_mobile = serializers.CharField(
        max_length=50, write_only=True)
    store_code = serializers.CharField(
        max_length=50, write_only=True)
    category = serializers.IntegerField(
        help_text='积分规则', write_only=True)

    def create(self, validated_data):
        mobile = validated_data.pop('user_mobile')
        store_code = validated_data.pop('store_code')
        user = get_or_create_user(mobile, store_code)
        category = validated_data.pop('category')
        rule = CoinRule.objects.filter(
            category=category, store_code=store_code).first()
        if not rule:
            raise serializers.ValidationError("规则不存在")

        ModelClass = self.Meta.model
        instance = ModelClass._default_manager.create(
            user=user.userinfo, rule=rule, coin=rule.coin, **validated_data)
        SyncCoinTask.apply_async(args=[instance.id])
        return instance

    class Meta:
        model = UserCoinRecord
        fields = (
            'mobile',
            'created',
            'coin',
            'rule',
            'store_code',
            'category',
            'user_mobile',
        )
        read_only_fields = ('created', 'coin', 'rule')
