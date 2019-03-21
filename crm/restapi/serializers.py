from rest_framework import serializers
from ..user.models import (
    BaseUser,
    UserInfo,
    UserOnlineOrder,
    )
from ..sale.models import (
    Seller,
    )
# import time
from rest_framework.utils import model_meta
import traceback
import django
import json


class BaseUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = BaseUser
        fields = (
            'mobile',
            'store_code',
        )


class UserInfoSerializer(serializers.ModelSerializer):

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
        )
        read_only_fields = ('user', 'created', 'mobile')


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

    is_active = serializers.SerializerMethodField('get_custom_is_active')

    def get_custom_is_active(self, instance):
        return instance.user.userinfo.is_seller

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
            'user', 'created', 'mobile', 'qr_code_url', 'code', 'name',
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
        user = BaseUser.objects.origin_all().filter(
            mobile=mobile, store_code=store_code).first()
        if not user:
            user = BaseUser.objects.create(
                mobile=mobile, store_code=store_code)
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


# class DownloadTaskSerializer(serializers.ModelSerializer):
#
#     store_list = serializers.JSONField(
#         required=True, write_only=True,
#         help_text='冷柜, 如: ["F0001", "F0002", ....]')
#     dynamic_path = serializers.CharField(
#         required=True, write_only=True, help_text='动态模型地址')
#     static_path = serializers.CharField(
#         required=True, write_only=True, help_text='静态模型地址')
#     dynamic_update_version = serializers.CharField(
#         required=True, write_only=True,
#         help_text='动态下载更新版本号, 如: 1.10.2')
#     static_update_version = serializers.CharField(
#         required=True, write_only=True,
#         help_text='静态下载更新版本号, 如: 1.10.2')
#     callback_url = serializers.CharField(
#         help_text='回调地址, 任务执行完成后调用')
#
#     class Meta:
#         model = DeployTask
#         fields = (
#             'id',
#             'task_name',
#             'store_list',
#             'dynamic_path',
#             'static_path',
#             'dynamic_update_version',
#             'static_update_version',
#             'callback_url',
#         )
#
#     def create(self, validated_data):
#         # update_time = datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')
#         store_list = validated_data.pop('store_list')
#         dynamic_path = validated_data.pop('dynamic_path')
#         static_path = validated_data.pop('static_path')
#         d_update_version = validated_data.pop('dynamic_update_version')
#         s_update_version = validated_data.pop('static_update_version')
#         # playbook
#         try:
#             playbook = AwxPlaybook.objects.get(name='download-model.yml')
#             validated_data['playbook'] = playbook
#         except AwxPlaybook.DoesNotExist:
#             raise serializers.ValidationError("playbook 不存在")
#         # template
#         try:
#             template = AwxJobTemplate.objects.get(name='download-model')
#             validated_data['template'] = template
#         except AwxJobTemplate.DoesNotExist:
#             raise serializers.ValidationError("template 不存在")
#         # stores
#         inventories = AwxInventory.objects.filter(name__in=store_list)
#         if not inventories.exists():
#             raise serializers.ValidationError("冷柜编号 不存在")
#         group = InventoryGroup(
#             name=validated_data['task_name'],
#             is_autocreated=True)
#         group.save()
#         group.inventories.add(*list(inventories))
#         validated_data['group'] = group
#         validated_data['descrption'] = 'download_model'
#         extra_vars = {
#             'dynamic_path': dynamic_path,
#             'static_path': static_path,
#             'dynamic_update_version': d_update_version,
#             'static_update_version': s_update_version,
#         }
#         validated_data['extra_vars'] = json.dumps(extra_vars)
#         instance = DeployTask.objects.create(**validated_data)
#
#         RunTask.apply_async(args=[instance.id, json.dumps(extra_vars)])
#         # RunTask().run(instance.id, json.dumps(extra_vars))
#         return instance
#
#
# class PublishTaskSerializer(serializers.ModelSerializer):
#
#     store_list = serializers.JSONField(
#         required=True, write_only=True,
#         help_text='冷柜, 如: ["F0001", "F0002", ....]')
#     dynamic_update_version = serializers.CharField(
#         required=True, write_only=True,
#         help_text='动态更新版本号, 如: 1.10.2')
#     dynamic_current_version = serializers.CharField(
#         required=True, write_only=True,
#         help_text='动态当前版本号, 如: 1.10.2')
#     static_update_version = serializers.CharField(
#         required=True, write_only=True,
#         help_text='静态更新版本号, 如: 1.10.2')
#     static_current_version = serializers.CharField(
#         required=True, write_only=True,
#         help_text='静态当前版本号, 如: 1.10.2')
#     product_info = serializers.JSONField(
#         required=True, write_only=True,
#         help_text='商品信息, 如: {}')
#     callback_url = serializers.CharField(
#         help_text='回调地址, 任务执行完成后调用')
#
#     class Meta:
#         model = DeployTask
#         fields = (
#             'id',
#             'task_name',
#             'store_list',
#             'dynamic_update_version',
#             'dynamic_current_version',
#             'static_update_version',
#             'static_current_version',
#             'callback_url',
#             'product_info',
#         )
#
#     def create(self, validated_data):
#         store_list = validated_data.pop('store_list')
#         d_update_version = validated_data.pop('dynamic_update_version')
#         d_current_version = validated_data.pop('dynamic_current_version')
#         s_update_version = validated_data.pop('static_update_version')
#         s_current_version = validated_data.pop('static_current_version')
#         product_info = validated_data.pop('product_info')
#         # playbook
#         try:
#             playbook = AwxPlaybook.objects.get(name='publish-model.yml')
#             validated_data['playbook'] = playbook
#         except AwxPlaybook.DoesNotExist:
#             raise serializers.ValidationError("playbook 不存在")
#         # template
#         try:
#             template = AwxJobTemplate.objects.get(name='publish-model')
#             validated_data['template'] = template
#         except AwxJobTemplate.DoesNotExist:
#             raise serializers.ValidationError("template 不存在")
#         # stores
#         inventories = AwxInventory.objects.filter(name__in=store_list)
#         if not inventories.exists():
#             raise serializers.ValidationError("冷柜编号 不存在")
#         group = InventoryGroup(
#             name=validated_data['task_name'],
#             is_autocreated=True)
#         group.save()
#         group.inventories.add(*list(inventories))
#         validated_data['group'] = group
#         validated_data['descrption'] = 'publish_model'
#         extra_vars = {
#             'dynamic_update_version': d_update_version,
#             'dynamic_current_version': d_current_version,
#             'static_update_version': s_update_version,
#             'static_current_version': s_current_version,
#             'product_info': json.dumps(product_info),
#         }
#         validated_data['extra_vars'] = json.dumps(extra_vars)
#         instance = DeployTask.objects.create(**validated_data)
#
#         RunTask.apply_async(args=[instance.id, json.dumps(extra_vars)])
#         # RunTask().run(instance.id, json.dumps(extra_vars))
#         return instance
#
#
# class AwxJobTemplateSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = AwxJobTemplate
#         fields = (
#             'id',
#             'name',
#         )
#
#
# class AwxInventorySerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = AwxInventory
#         fields = (
#             'id',
#             'name',
#         )
#
#
# class AwxPlaybookSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = AwxPlaybook
#         fields = (
#             'id',
#             'name',
#         )
#
#
# class InventoryGroupSerializer(serializers.ModelSerializer):
#
#     inventories = serializers.SerializerMethodField('get_inventorie_list')
#
#     def get_inventorie_list(self, instance):
#         return instance.inventories.values_list('name', flat=True)
#
#     class Meta:
#         model = InventoryGroup
#         fields = (
#             'id',
#             'name',
#             'inventories',
#         )
