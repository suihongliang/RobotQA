from django.db.models import Q
from rest_framework import serializers
from ..user.models import (
    BaseUser,
    UserInfo,
    UserOnlineOrder,
    BackendPermission,
    BackendRole,
    BackendUser,
    UserBehavior,
    BackendGroup,
    )
from ..sale.models import (
    Seller,
    CustomerRelation,
    QRCode,
    )
from ..discount.models import (
    CoinRule,
    Coupon,
    SendCoupon,
    CoinQRCode,
    PointRecord)
from ..user.utils import get_or_create_user

from rest_framework.utils import model_meta
import traceback
import django
import json


class AssignUserCompanySerializer(serializers.ModelSerializer):

    def get_fields(self):
        fields = super().get_fields()

        if 'request' in self.context.keys():
            if self.context['request'].user.is_authenticated:
                company_id = self.context['request'].user.company_id
                self.context['request'].data['company_id'] = company_id
        return fields


class BaseUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = BaseUser
        fields = (
            'mobile',
            'company_id',
        )


class BackendPermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = BackendPermission
        fields = (
            'id',
            'name',
            'code',
        )


class BackendRoleSerializer(AssignUserCompanySerializer):

    permissions = BackendPermissionSerializer(
        many=True, read_only=True)
    company_id = serializers.CharField(
        help_text='公司编号', max_length=50, write_only=True)
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
            'company_id',
            'w_permissions',
            'is_seller',
        )
        read_only_fields = ('created',)


class BackendGroupSerializer(serializers.ModelSerializer):

    manager_name = serializers.CharField(
        source='manager.name', allow_null=True, read_only=True)
    add_num = serializers.ListField(
        help_text='添加', write_only=True, required=False)
    remove_num = serializers.ListField(
        help_text='移除', write_only=True, required=False)

    def create(self, validated_data):
        add_num = validated_data.pop('add_num', [])

        ModelClass = self.Meta.model

        info = model_meta.get_field_info(ModelClass)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)

        try:
            instance = ModelClass.objects.create(**validated_data)
        except TypeError:
            tb = traceback.format_exc()
            msg = (
                    'Got a `TypeError` when calling `%s.objects.create()`. '
                    'This may be because you have a writable field on the '
                    'serializer class that is not a valid argument to '
                    '`%s.objects.create()`. You may need to make the field '
                    'read-only, or override the %s.create() method to handle '
                    'this correctly.\nOriginal exception was:\n %s' %
                    (
                        ModelClass.__name__,
                        ModelClass.__name__,
                        self.__class__.__name__,
                        tb
                    )
            )
            raise TypeError(msg)

        # Save many-to-many relationships after the instance is created.
        if many_to_many:
            for field_name, value in many_to_many.items():
                field = getattr(instance, field_name)
                field.set(value)
        if add_num:
            BackendUser.objects.filter(id__in=add_num).update(group=instance)
        return instance

    def update(self, instance, validated_data):
        add_num = validated_data.pop('add_num', [])
        remove_num = validated_data.pop('remove_num', [])
        if add_num:
            BackendUser.objects.filter(id__in=add_num).update(group=instance)
        if remove_num:
            BackendUser.objects.filter(id__in=remove_num).update(group=None)

        info = model_meta.get_field_info(instance)

        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                field = getattr(instance, attr)
                field.set(value)
            else:
                setattr(instance, attr, value)
        instance.save()

        return instance

    class Meta:
        model = BackendGroup
        fields = (
            'id',
            'name',
            'created',
            'manager',
            'manager_name',
            'add_num',
            'remove_num',
        )


class BackendGroupDetailSerializer(BackendGroupSerializer):
    member = serializers.SerializerMethodField()

    def get_member(self, instance):
        member = BackendUser.objects.filter(
            group=instance).values('id', 'name', 'mobile')
        return list(member)

    class Meta:
        model = BackendGroup
        fields = BackendGroupSerializer.Meta.fields + ('member',)


class BackendUserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        help_text='密码', write_only=True, max_length=50)
    role = BackendRoleSerializer(
        read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        write_only=True, allow_null=True,
        queryset=BackendRole.objects.all(), source='role')
    is_active = serializers.BooleanField(
        required=False, default=True)
    group = BackendGroupSerializer(
        read_only=True)
    group_id = serializers.PrimaryKeyRelatedField(
        write_only=True, allow_null=True, required=False,
        queryset=BackendGroup.objects.all(), source='group')

    def validate_mobile(self, mobile):
        company_id = self.context['request'].user.company_id
        user = BaseUser.objects.filter(mobile=mobile, company_id=company_id)
        if not user.exists():
            raise serializers.ValidationError('未注册手机号')
        return mobile

    def get_fields(self):
        fields = super().get_fields()

        if self.context['request'].user.is_authenticated:
            company_id = self.context['request'].user.company_id
            self.context['request'].data['company_id'] = company_id

            fields['role_id'].queryset = fields['role_id'].queryset.filter(
                company_id=company_id)
        return fields

    def create(self, validated_data):
        ModelClass = self.Meta.model
        info = model_meta.get_field_info(ModelClass)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)

        try:
            instance = ModelClass._default_manager.create(**validated_data)
        except TypeError:
            # tb = traceback.format_exc()
            raise TypeError('create backenduser type error')

        # Save many-to-many relationships after the instance is created.
        if many_to_many:
            for field_name, value in many_to_many.items():
                field = getattr(instance, field_name)
                field.set(value)

        instance.set_password(instance.password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        # raise_errors_on_nested_writes('update', self, validated_data)
        info = model_meta.get_field_info(instance)

        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                field = getattr(instance, attr)
                field.set(value)
            else:
                setattr(instance, attr, value)
        if 'password' in validated_data.keys():
            instance.set_password(validated_data['password'])
        instance.save()

        return instance

    class Meta:
        model = BackendUser
        fields = (
            'id',
            'mobile',
            'created',
            'password',
            'company_id',
            'role',
            'role_id',
            'is_active',
            'name',
            'group',
            'group_id',
        )
        read_only_fields = ('created',)


class UserInfoSerializer(serializers.ModelSerializer):

    gender_display = serializers.CharField(
        source='get_gender_display', read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)
    industry_display = serializers.CharField(
        source='get_industry_display', read_only=True)
    extra_info = serializers.JSONField(
        help_text='额外参数', required=False, write_only=True)
    customer_remark = serializers.CharField(
        help_text='客户备注名', required=False, write_only=True)
    seller = serializers.SerializerMethodField()
    extra_data = serializers.SerializerMethodField()
    mark_name = serializers.SerializerMethodField()
    bind_relation_time = serializers.SerializerMethodField()
    is_sampleroom = serializers.SerializerMethodField()
    is_3dvr = serializers.SerializerMethodField()
    new_message = serializers.SerializerMethodField()


    def get_is_3dvr(self, instance):
        behavior = UserBehavior.objects.filter(user=instance.user, category='3dvr')
        if behavior.exists():
            return True
        else:
            return False

    def get_is_sampleroom(self, instance):
        behavior = UserBehavior.objects.filter(user=instance.user, category='sampleroom')
        if behavior.exists():
            return True
        else:
            return False

    def get_new_message(self, instance):
        try:
            latest_record = PointRecord.objects.latest('created_at')
        except Exception:
            latest_record = None
        if not latest_record:
            return False
        if latest_record.created_at <= instance.msg_last_at:
            return False
        return True

    def get_mark_name(self, instance):
        try:
            return instance.customerrelation.mark_name
        except CustomerRelation.DoesNotExist:
            CustomerRelation.objects.create(user=instance)
            return None

    def get_extra_data(self, instance):
        return instance.get_extra_data_json()

    def get_seller(self, instance):
        try:
            seller = instance.customerrelation.seller
            if not seller:
                return None
            mobile = seller.user.mobile
            b_user = BackendUser.objects.filter(mobile=mobile).first()
            if b_user:
                return {
                    'seller_name': b_user.name,
                    'seller_mobile': mobile,
                }
        except CustomerRelation.DoesNotExist:
            CustomerRelation.objects.create(user=instance)
        except Seller.DoesNotExist:
            pass
        # if seller:
        #     return SellerSerializer(seller).data
        return None

    def get_bind_relation_time(self, instance):
        return instance.customerrelation.created.strftime("%Y-%m-%d %H:%M:%S")

    def update(self, instance, validated_data):
        extra_info = validated_data.pop('extra_info', '')
        customer_remark = validated_data.pop('customer_remark', '')
        if extra_info:
            try:
                extra_data = json.loads(instance.extra_data)
            except Exception:
                extra_data = {}
            extra_data.update(extra_info)
            validated_data['extra_data'] = json.dumps(extra_data)
            # 完善个人信息送积分
            rule = CoinRule.objects.filter(category=2).first()
            PointRecord.objects.get_or_create(
                user=instance, rule=rule,
                defaults={'coin': rule.coin, 'change_type': 'rule_reward'})
        if customer_remark:
            CustomerRelation.objects.filter(user=instance).update(mark_name=customer_remark)

        info = model_meta.get_field_info(instance)
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                field = getattr(instance, attr)
                field.set(value)
            else:
                setattr(instance, attr, value)
        instance.save()

        return instance

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
            'industry_display',
            'seller',
            'last_active_time',
            'access_times',
            'coin',
            'spend_coin',
            'extra_data',
            'mark_name',
            'new_message',
            'bind_relation_time',
            'extra_info',
            'customer_remark',
            'is_sampleroom',
            'is_3dvr',
            'product_intention',
            'purchase_purpose',
            'industry',
        )
        read_only_fields = (
            'user', 'created', 'mobile', 'is_seller',
            'last_active_time', 'access_times',
            'spend_coin', 'coin',)


class UserInfoReportSerializer(serializers.ModelSerializer):

    gender_display = serializers.CharField(
        source='get_gender_display', read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)
    extra_info = serializers.JSONField(
        help_text='额外参数', required=False, write_only=True)
    customer_remark = serializers.CharField(
        help_text='客户备注名', required=False, write_only=True)
    seller = serializers.SerializerMethodField()
    extra_data = serializers.SerializerMethodField()
    mark_name = serializers.SerializerMethodField()
    bind_relation_time = serializers.SerializerMethodField()
    is_sampleroom = serializers.SerializerMethodField()
    is_3dvr = serializers.SerializerMethodField()
    new_message = serializers.SerializerMethodField()
    coupon_count = serializers.SerializerMethodField()
    avg_sampleroom_seconds = serializers.SerializerMethodField()

    def get_avg_sampleroom_seconds(self, instance):
        return instance.sampleroom_seconds / instance.sampleroom_times if instance.sampleroom_times > 0 else 0

    def get_coupon_count(self, instance):
        coupon_num = SendCoupon.objects.filter(user=instance).count()
        return coupon_num

    def get_is_3dvr(self, instance):
        behavior = UserBehavior.objects.filter(user=instance.user, category='3dvr')
        if behavior.exists():
            return True
        else:
            return False

    def get_is_sampleroom(self, instance):
        behavior = UserBehavior.objects.filter(user=instance.user, category='sampleroom')
        if behavior.exists():
            return True
        else:
            return False

    def get_new_message(self, instance):
        try:
            latest_record = PointRecord.objects.latest('created_at')
        except Exception:
            latest_record = None
        if not latest_record:
            return False
        if latest_record.created_at <= instance.msg_last_at:
            return False
        return True

    def get_mark_name(self, instance):
        try:
            return instance.customerrelation.mark_name
        except CustomerRelation.DoesNotExist:
            CustomerRelation.objects.create(user=instance)
            return None

    def get_extra_data(self, instance):
        return instance.get_extra_data_json()

    def get_seller(self, instance):
        try:
            seller = instance.customerrelation.seller
            if not seller:
                return None
            mobile = seller.user.mobile
            b_user = BackendUser.objects.filter(mobile=mobile).first()
            if b_user:
                return {
                    'seller_name': b_user.name,
                    'seller_mobile': mobile,
                }
        except CustomerRelation.DoesNotExist:
            CustomerRelation.objects.create(user=instance)
        except Seller.DoesNotExist:
            pass
        # if seller:
        #     return SellerSerializer(seller).data
        return None

    def get_bind_relation_time(self, instance):
        return instance.customerrelation.created.strftime("%Y-%m-%d %H:%M:%S")

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
            'mark_name',
            'new_message',
            'bind_relation_time',
            'extra_info',
            'customer_remark',
            'is_sampleroom',
            'is_3dvr',
            'sampleroom_times',
            'sampleroom_seconds',
            'sdver_times',
            'coupon_count',
            'avg_sampleroom_seconds'
        )
        read_only_fields = (
            'user', 'created', 'mobile', 'is_seller',
            'last_active_time', 'access_times', 'sampleroom_times',
            'sampleroom_seconds', 'sdver_times', 'coupon_count',
            'spend_coin', 'coin',)


class UserInfoDetailSerializer(UserInfoSerializer):

    seller_info = serializers.SerializerMethodField()

    def get_seller_info(self, instance):
        if hasattr(instance.user, 'seller'):
            return SellerSerializer(instance.user.seller).data
        return {}

    class Meta:
        model = UserInfo
        fields = UserInfoSerializer.Meta.fields + (
            'seller_info',)


class UserInfoDetailReportSerializer(UserInfoReportSerializer):

    seller_info = serializers.SerializerMethodField()

    def get_seller_info(self, instance):
        if hasattr(instance.user, 'seller'):
            return SellerSerializer(instance.user.seller).data
        return {}

    class Meta:
        model = UserInfo
        fields = UserInfoSerializer.Meta.fields + (
            'seller_info',)


class BackendUserInfoSerializer(UserInfoSerializer):

    coupon_count = serializers.SerializerMethodField()

    def get_coupon_count(self, instance):
        return instance.sendcoupon_set.count()

    class Meta:
        model = UserInfo
        fields = UserInfoSerializer.Meta.fields + (
            'coupon_count',)
        read_only_fields = UserInfoSerializer.Meta.read_only_fields


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


class SellerSerializer(AssignUserCompanySerializer):

    qrcode = serializers.SerializerMethodField()

    def get_qrcode(self, instance):
        qrcode_info = instance.qrcode
        return QRCodeSerializer(qrcode_info).data if qrcode_info else None

    class Meta:
        model = Seller
        fields = (
            'user',
            'created',
            'mobile',
            'qrcode',
            # 'name',
            'is_active',
        )
        read_only_fields = (
            'user', 'created', 'mobile', 'qrcode',
            'is_active')


class CustomerRelationSerializer(AssignUserCompanySerializer):

    mobile_seller = serializers.CharField(
        help_text='销售手机号', max_length=20, write_only=True)
    company_id = serializers.CharField(
        help_text='公司编号', max_length=50, write_only=True)
    mobile_customer = serializers.SerializerMethodField(
        help_text='客户手机')

    def get_mobile_customer(self, instance):
        mobile_customer = instance.user.mobile
        return mobile_customer

    def update(self, instance, validated_data):
        if instance.seller:
            raise serializers.ValidationError(
                    {'detail': "客户已绑定销售"})
        company_id = validated_data.pop('company_id')

        try:
            mobile_seller = validated_data.pop('mobile_seller')
            seller = Seller.objects.filter(
                user__mobile=mobile_seller,
                user__company_id=company_id).first()
            if not seller:
                raise serializers.ValidationError(
                    {'detail': "销售不存在"})
        except KeyError:
            seller = None

        info = model_meta.get_field_info(instance)

        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                field = getattr(instance, attr)
                field.set(value)
            else:
                setattr(instance, attr, value)
        if seller is not None:
            instance.seller = seller
            UserBehavior.objects.create(
                user_id=instance.user_id, category='sellerbind', location='')
        instance.save()

        return instance

    class Meta:
        model = CustomerRelation
        fields = (
            'user',
            'mobile_seller',
            'mark_name',
            'company_id',
            'created',
            'mobile_customer',
        )
        read_only_fields = ('user', 'created')


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


class CreateSellerSerializer(AssignUserCompanySerializer):

    mobile = serializers.CharField(
        help_text='手机号', max_length=20, write_only=True)
    company_id = serializers.CharField(
        help_text='门店编号', max_length=10, write_only=True)

    def create(self, validated_data):
        mobile = validated_data.pop('mobile')
        company_id = validated_data.pop('company_id')
        user = get_or_create_user(mobile, company_id)
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
            'company_id',
            'name',
        )


class CoinRuleSerializer(serializers.ModelSerializer):

    category_display = serializers.CharField(
        source='get_category_display', read_only=True)

    qrcode = serializers.SerializerMethodField()

    def get_qrcode(self, instance):
        qrcode_info = instance.qrcode
        return CoinQRCodeSerializer(qrcode_info).data if qrcode_info else None

    class Meta:
        model = CoinRule
        fields = (
            'id',
            'category',
            'category_display',
            'qrcode',
            'coin',
        )
        read_only_fields = ('category', 'qrcode',
                            'company_id',)


class PointRecordSerializer(AssignUserCompanySerializer):
    change_type_name = serializers.SerializerMethodField()
    change_by = serializers.SerializerMethodField()
    user_mobile = serializers.SerializerMethodField()

    def get_change_by(self, instance):
        return instance.change_by

    def get_change_type_name(self, instance):
        return instance.get_change_type_display()

    def get_user_mobile(self, instance):
        return instance.user.mobile

    class Meta:
        model = PointRecord
        fields = (
            'id',
            'change_type_name',
            'change_type',
            'change_by',
            'user_mobile',
            'coin',
            'created_at')


class CreatePointRecordSerializer(AssignUserCompanySerializer):
    user_mobile = serializers.CharField(
        max_length=50, write_only=True)
    company_id = serializers.CharField(
        max_length=50, write_only=True)
    change_type = serializers.CharField(max_length=20,
                                        help_text='变更类型', write_only=True, required=True)
    coin = serializers.IntegerField(
        help_text='积分', required=False)
    change_by = serializers.CharField(
        help_text='订单号|退单号|后台管理用户手机号|积分规则二维码编码之一', required=True, write_only=True,
        max_length=100)

    def create(self, validated_data):
        mobile = validated_data.get('user_mobile')
        company_id = validated_data.get('company_id')
        change_type = validated_data.get('change_type')
        change_by = validated_data.get('change_by')
        coin = validated_data.get('coin', 0)

        if not coin and change_by != 'rule_reward':
            raise serializers.ValidationError({
                'detail': "参数错误"})
        user = UserInfo.objects.filter(
            user__mobile=mobile, user__company_id=company_id).first()
        if not user:
            raise serializers.ValidationError({
                'detail': "用户不存在"})
        ModelClass = self.Meta.model
        kw = {'user': user, 'change_type': change_type}
        if change_type == 'rule_reward':
            rule = CoinRule.objects.filter(Q(qrcode__code=change_by),
                                           company_id=company_id).first()
            if not rule:
                raise serializers.ValidationError({'detail': "规则不存在"})
            kw.update({'coin': rule.coin, 'rule': rule})
        elif change_type == 'seller_send':
            seller = BackendUser.objects.filter(mobile=change_by).first()
            if not seller:
                raise serializers.ValidationError({'detail': "后台管理用户不存在"})
            kw.update({'coin': coin, 'seller': seller})
        elif change_type == 'order':
            kw.update({'coin': coin, 'order_no': change_by})
        else:
            kw.update({'coin': coin, 'return_order_no': change_by})

        instance = ModelClass._default_manager.create(**kw)
        return instance

    class Meta:
        model = PointRecord
        fields = (
            'user_mobile',
            'company_id',
            'change_type',
            'change_by',
            'coin')


class CouponSerializer(AssignUserCompanySerializer):

    class Meta:
        model = Coupon
        fields = (
            'id',
            'description',
            'discount',
            'created',
            'company_id',
            'is_active',
        )
        read_only_fields = ('created',)


class SendCouponSerializer(AssignUserCompanySerializer):

    mobile_user = serializers.CharField(
        help_text='用户手机号', max_length=20, write_only=True)
    company_id = serializers.CharField(
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
        company_id = validated_data.pop('company_id')

        if not self.context['request'].user.is_authenticated:
            raise serializers.ValidationError(
                {'detail': "请登录"})
        b_user = self.context['request'].user

        user = get_or_create_user(mobile_user, company_id)

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
            'company_id',
            'coupon',
            'coupon_id',
        )


class UserBehaviorSerializer(AssignUserCompanySerializer):

    mobile = serializers.CharField(
        help_text='用户手机号', max_length=20)
    company_id = serializers.CharField(
        help_text='公司编号', max_length=50, write_only=True)
    name = serializers.SerializerMethodField(
        help_text='用户姓名'
    )

    def get_name(self, instance):
        name = instance.user.userinfo.name
        return name

    def create(self, validated_data):
        mobile = validated_data.pop('mobile')
        company_id = validated_data.pop('company_id')

        user = BaseUser.objects.origin_all().filter(
            mobile=mobile, company_id=company_id).first()
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
            'company_id',
            'category',
            'location',
            'created',
            'name',
        )
        read_only_fields = ('created',)


class QRCodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = QRCode
        fields = (
            'id',
            'code',
            'qr_code_url',
            'company_id'
        )


class CoinQRCodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = CoinQRCode
        fields = (
            'id',
            'code',
            'qr_code_url',
            'company_id'
        )
