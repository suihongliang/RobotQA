from rest_framework import serializers
from jianbox.boxinfo.models import (
    DeployTask,
    AwxJobTemplate,
    AwxInventory,
    AwxPlaybook,
    InventoryGroup,
    )
from jianbox.boxinfo.tasks import RunTask
# import time
import json


class DeployTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeployTask
        fields = (
            'id',
            'task_name',
            'template',
            'playbook',
            'group',
            'status',
        )


class DownloadTaskSerializer(serializers.ModelSerializer):

    store_list = serializers.JSONField(
        required=True, write_only=True,
        help_text='冷柜, 如: ["F0001", "F0002", ....]')
    dynamic_path = serializers.CharField(
        required=True, write_only=True, help_text='动态模型地址')
    static_path = serializers.CharField(
        required=True, write_only=True, help_text='静态模型地址')
    dynamic_update_version = serializers.CharField(
        required=True, write_only=True,
        help_text='动态下载更新版本号, 如: 1.10.2')
    static_update_version = serializers.CharField(
        required=True, write_only=True,
        help_text='静态下载更新版本号, 如: 1.10.2')
    callback_url = serializers.CharField(
        help_text='回调地址, 任务执行完成后调用')

    class Meta:
        model = DeployTask
        fields = (
            'id',
            'task_name',
            'store_list',
            'dynamic_path',
            'static_path',
            'dynamic_update_version',
            'static_update_version',
            'callback_url',
        )

    def create(self, validated_data):
        # update_time = datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')
        store_list = validated_data.pop('store_list')
        dynamic_path = validated_data.pop('dynamic_path')
        static_path = validated_data.pop('static_path')
        d_update_version = validated_data.pop('dynamic_update_version')
        s_update_version = validated_data.pop('static_update_version')
        # playbook
        try:
            playbook = AwxPlaybook.objects.get(name='download-model.yml')
            validated_data['playbook'] = playbook
        except AwxPlaybook.DoesNotExist:
            raise serializers.ValidationError("playbook 不存在")
        # template
        try:
            template = AwxJobTemplate.objects.get(name='download-model')
            validated_data['template'] = template
        except AwxJobTemplate.DoesNotExist:
            raise serializers.ValidationError("template 不存在")
        # stores
        inventories = AwxInventory.objects.filter(name__in=store_list)
        if not inventories.exists():
            raise serializers.ValidationError("冷柜编号 不存在")
        group = InventoryGroup(
            name=validated_data['task_name'],
            is_autocreated=True)
        group.save()
        group.inventories.add(*list(inventories))
        validated_data['group'] = group
        validated_data['descrption'] = 'download_model'
        extra_vars = {
            'dynamic_path': dynamic_path,
            'static_path': static_path,
            'dynamic_update_version': d_update_version,
            'static_update_version': s_update_version,
        }
        validated_data['extra_vars'] = json.dumps(extra_vars)
        instance = DeployTask.objects.create(**validated_data)

        RunTask.apply_async(args=[instance.id, json.dumps(extra_vars)])
        # RunTask().run(instance.id, json.dumps(extra_vars))
        return instance


class PublishTaskSerializer(serializers.ModelSerializer):

    store_list = serializers.JSONField(
        required=True, write_only=True,
        help_text='冷柜, 如: ["F0001", "F0002", ....]')
    dynamic_update_version = serializers.CharField(
        required=True, write_only=True,
        help_text='动态更新版本号, 如: 1.10.2')
    dynamic_current_version = serializers.CharField(
        required=True, write_only=True,
        help_text='动态当前版本号, 如: 1.10.2')
    static_update_version = serializers.CharField(
        required=True, write_only=True,
        help_text='静态更新版本号, 如: 1.10.2')
    static_current_version = serializers.CharField(
        required=True, write_only=True,
        help_text='静态当前版本号, 如: 1.10.2')
    product_info = serializers.JSONField(
        required=True, write_only=True,
        help_text='商品信息, 如: {}')
    callback_url = serializers.CharField(
        help_text='回调地址, 任务执行完成后调用')

    class Meta:
        model = DeployTask
        fields = (
            'id',
            'task_name',
            'store_list',
            'dynamic_update_version',
            'dynamic_current_version',
            'static_update_version',
            'static_current_version',
            'callback_url',
            'product_info',
        )

    def create(self, validated_data):
        store_list = validated_data.pop('store_list')
        d_update_version = validated_data.pop('dynamic_update_version')
        d_current_version = validated_data.pop('dynamic_current_version')
        s_update_version = validated_data.pop('static_update_version')
        s_current_version = validated_data.pop('static_current_version')
        product_info = validated_data.pop('product_info')
        # playbook
        try:
            playbook = AwxPlaybook.objects.get(name='publish-model.yml')
            validated_data['playbook'] = playbook
        except AwxPlaybook.DoesNotExist:
            raise serializers.ValidationError("playbook 不存在")
        # template
        try:
            template = AwxJobTemplate.objects.get(name='publish-model')
            validated_data['template'] = template
        except AwxJobTemplate.DoesNotExist:
            raise serializers.ValidationError("template 不存在")
        # stores
        inventories = AwxInventory.objects.filter(name__in=store_list)
        if not inventories.exists():
            raise serializers.ValidationError("冷柜编号 不存在")
        group = InventoryGroup(
            name=validated_data['task_name'],
            is_autocreated=True)
        group.save()
        group.inventories.add(*list(inventories))
        validated_data['group'] = group
        validated_data['descrption'] = 'publish_model'
        extra_vars = {
            'dynamic_update_version': d_update_version,
            'dynamic_current_version': d_current_version,
            'static_update_version': s_update_version,
            'static_current_version': s_current_version,
            'product_info': json.dumps(product_info),
        }
        validated_data['extra_vars'] = json.dumps(extra_vars)
        instance = DeployTask.objects.create(**validated_data)

        RunTask.apply_async(args=[instance.id, json.dumps(extra_vars)])
        # RunTask().run(instance.id, json.dumps(extra_vars))
        return instance


class AwxJobTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = AwxJobTemplate
        fields = (
            'id',
            'name',
        )


class AwxInventorySerializer(serializers.ModelSerializer):

    class Meta:
        model = AwxInventory
        fields = (
            'id',
            'name',
        )


class AwxPlaybookSerializer(serializers.ModelSerializer):

    class Meta:
        model = AwxPlaybook
        fields = (
            'id',
            'name',
        )


class InventoryGroupSerializer(serializers.ModelSerializer):

    inventories = serializers.SerializerMethodField('get_inventorie_list')

    def get_inventorie_list(self, instance):
        return instance.inventories.values_list('name', flat=True)

    class Meta:
        model = InventoryGroup
        fields = (
            'id',
            'name',
            'inventories',
        )
