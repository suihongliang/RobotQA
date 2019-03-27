from rest_framework import serializers
from ..user.models import (
    BaseUser,
    UserInfo,
    UserOnlineOrder,
    BackendPermission,
    BackendRole,
    BackendUser,
    UserBehavior,
    )
from ..sale.models import (
    Seller,
    CustomerRelation,
    )
from ..discount.models import (
    CoinRule,
    UserCoinRecord,
    Coupon,
    SendCoupon,
    )
# from ..discount.tasks import (
#     SyncCoinTask,
#     )
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


class AssignUserStoreSerializer(serializers.ModelSerializer):

    def get_fields(self):
        fields = super().get_fields()

        if 'request' in self.context.keys():
            if self.context['request'].user.is_authenticated:
                store_code = self.context['request'].user.store_code
                self.context['request'].data['store_code'] = store_code
        return fields


class BaseUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = BaseUser
        fields = (
            'mobile',
            'store_code',
        )


class BackendPermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = BackendPermission
        fields = (
            'id',
            'name',
            'code',
        )


class BackendRoleSerializer(AssignUserStoreSerializer):

    permissions = BackendPermissionSerializer(
        many=True, read_only=True)
    store_code = serializers.CharField(
        help_text='门店编号', max_length=50, write_only=True)
    w_permissions = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True,
        queryset=BackendPermission.objects.all(), source='permissions')

    class Meta:
        model = BackendRole
        fields = (
            'id',
            'name',
            'created',
            'permissions',
            'store_code',
            'w_permissions',
        )
        read_only_fields = ('created',)


class BackendUserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        help_text='密码', write_only=True, max_length=50)
    role = BackendRoleSerializer(
        read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=BackendRole.objects.all(), source='role')
    is_active = serializers.BooleanField(
        required=False, default=True)

    def get_fields(self):
        fields = super().get_fields()

        if self.context['request'].user.is_authenticated:
            store_code = self.context['request'].user.store_code
            self.context['request'].data['store_code'] = store_code

            fields['role_id'].queryset = fields['role_id'].queryset.filter(
                store_code=store_code)
        return fields

    class Meta:
        model = BackendUser
        fields = (
            'id',
            'mobile',
            'created',
            'password',
            'store_code',
            'role',
            'role_id',
            'is_active',
        )
        read_only_fields = ('created',)


class UserInfoSerializer(serializers.ModelSerializer):

    gender_display = serializers.CharField(source='get_gender_display')
    status_display = serializers.CharField(source='get_status_display')
    seller = serializers.SerializerMethodField()
    extra_data = serializers.SerializerMethodField()

    def get_extra_data(self, instance):
        return instance.get_extra_data_json()

    def get_seller(self, instance):
        seller = instance.customerrelation.seller
        if seller:
            return SellerSerializer(seller).data
        return None

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
            'seller',
            'last_active_time',
            'access_times',
            'coin',
            'spend_coin',
            'extra_data',
        )
        read_only_fields = (
            'user', 'created', 'mobile', 'is_seller', 'gender_display',
            'status_display', 'last_active_time', 'access_times',
            'spend_coin', 'coin',)


class UserOnlineOrderSerializer(serializers.ModelSerializer):

    order = serializers.SerializerMethodField('get_custom_order')

    def get_custom_order(self, instance):
        return {}

    class Meta:
        model = UserOnlineOrder
        fields = (
            'id',
            'user',
            'mobile',
            'created',
            'location',
            'order',
        )


class SellerSerializer(AssignUserStoreSerializer):

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


class CustomerRelationSerializer(AssignUserStoreSerializer):

    mobile_seller = serializers.CharField(
        help_text='销售手机号', max_length=20, write_only=True)
    store_code = serializers.CharField(
        help_text='门店编号', max_length=50, write_only=True)

    def update(self, instance, validated_data):
        mobile_seller = validated_data.pop('mobile_seller')
        store_code = validated_data.pop('store_code')
        seller = Seller.objects.filter(
            user__mobile=mobile_seller, user__store_code=store_code).first()
        if not seller:
            raise serializers.ValidationError(
                {'detail': "销售不存在"})

        info = model_meta.get_field_info(instance)

        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                field = getattr(instance, attr)
                field.set(value)
            else:
                setattr(instance, attr, value)
        instance.seller = seller
        instance.save()

        return instance

    class Meta:
        model = CustomerRelation
        fields = (
            'user',
            'mobile_seller',
            'store_code',
        )


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


class CreateSellerSerializer(AssignUserStoreSerializer):

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
            raise serializers.ValidationError(
                {'detail': "用户已创建"})

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

    category_display = serializers.CharField(
        source='get_category_display', read_only=True)

    class Meta:
        model = CoinRule
        fields = (
            'id',
            'category',
            'category_display',
            'coin',
            'qr_code_url',
        )
        read_only_fields = ('category', 'qr_code_url',
                            'store_code',)


class UserCoinRecordSerializer(AssignUserStoreSerializer):

    user_mobile = serializers.CharField(
        max_length=50, write_only=True)
    store_code = serializers.CharField(
        max_length=50, write_only=True)
    category = serializers.IntegerField(
        help_text='积分规则', write_only=True, required=False)
    coin = serializers.IntegerField(
        help_text='积分', required=False)
    extra_data = serializers.CharField(
        help_text='其他参数, 默认不传', required=False, write_only=True,
        max_length=500)

    def create(self, validated_data):
        mobile = validated_data.pop('user_mobile')
        store_code = validated_data.pop('store_code')
        # user = get_or_create_user(mobile, store_code)
        try:
            category = validated_data.pop('category')
        except KeyError:
            category = None
        if not validated_data.get('coin') and category is None:
            raise serializers.ValidationError({
                'detail': "参数错误"})
        user = UserInfo.objects.filter(
            user__mobile=mobile, user__store_code=store_code).first()
        if not user:
            raise serializers.ValidationError({
                'detail': "用户不存在"})
        if category is None:
            rule = None
        else:
            rule = CoinRule.objects.filter(
                category=category, store_code=store_code).first()
            if not rule:
                raise serializers.ValidationError({
                    'detail': "规则不存在"})
            validated_data['coin'] = rule.coin

        ModelClass = self.Meta.model
        instance = ModelClass._default_manager.create(
            user=user, rule=rule, **validated_data)
        return instance

    class Meta:
        model = UserCoinRecord
        fields = (
            'id',
            'mobile',
            'created',
            'coin',
            'rule',
            'store_code',
            'category',
            'user_mobile',
            'extra_data',
        )
        read_only_fields = ('created', 'rule')


class CouponSerializer(AssignUserStoreSerializer):

    class Meta:
        model = Coupon
        fields = (
            'id',
            'description',
            'discount',
            'created',
            'store_code',
            'is_active',
        )
        read_only_fields = ('created',)


class SendCouponSerializer(AssignUserStoreSerializer):

    mobile_user = serializers.CharField(
        help_text='用户手机号', max_length=20, write_only=True)
    store_code = serializers.CharField(
        help_text='门店编号', max_length=50, write_only=True)
    coupon = CouponSerializer(
        read_only=True)
    coupon_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Coupon.objects.all(), source='coupon')
    user = UserInfoSerializer(
        read_only=True)
    backenduser = BackendUserSerializer(
        read_only=True)

    def create(self, validated_data):
        mobile_user = validated_data.pop('mobile_user')
        store_code = validated_data.pop('store_code')

        if not self.context['request'].user.is_authenticated:
            raise serializers.ValidationError(
                {'detail': "请登录"})
        b_user = self.context['request'].user

        user = get_or_create_user(mobile_user, store_code)

        ModelClass = self.Meta.model
        try:
            instance = ModelClass._default_manager.create(
                user=user.userinfo, backenduser=b_user, **validated_data)
        except django.db.utils.IntegrityError:
            raise serializers.ValidationError(
                {'detail': "参数错误"})
        return instance

    class Meta:
        model = SendCoupon
        fields = (
            'id',
            'mobile_user',
            'user',
            'backenduser',
            'store_code',
            'coupon',
            'coupon_id',
        )


class UserBehaviorSerializer(AssignUserStoreSerializer):

    mobile = serializers.CharField(
        help_text='用户手机号', max_length=20)
    store_code = serializers.CharField(
        help_text='门店编号', max_length=50, write_only=True)

    def create(self, validated_data):
        mobile = validated_data.pop('mobile')
        store_code = validated_data.pop('store_code')

        user = BaseUser.objects.origin_all().filter(
            mobile=mobile, store_code=store_code).first()
        if not user:
            raise serializers.ValidationError(
                {'detail': "用户不存在"})

        ModelClass = self.Meta.model
        try:
            instance = ModelClass._default_manager.create(
                user=user, **validated_data)
        except django.db.utils.IntegrityError:
            raise serializers.ValidationError(
                {'detail': "参数错误"})
        return instance

    class Meta:
        model = UserBehavior
        fields = (
            'id',
            'mobile',
            'store_code',
            'category',
            'location',
            'created',
        )
        read_only_fields = ('created',)
