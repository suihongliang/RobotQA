from jianbox.boxinfo.models import (
    DeployTask,
    AwxJobTemplate,
    AwxInventory,
    AwxPlaybook,
    InventoryGroup,
    )
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import Http404
from .serializers import (
    DeployTaskSerializer,
    DownloadTaskSerializer,
    AwxJobTemplateSerializer,
    AwxInventorySerializer,
    AwxPlaybookSerializer,
    InventoryGroupSerializer,
    PublishTaskSerializer,
    )
from django.db import transaction

# Create your views here.


# def test(request):
#     from django.http import JsonResponse
#     print(request.GET.get('a'), request.GET.get('is_success'))
#     return JsonResponse({})


class DeployTaskViewSet(viewsets.GenericViewSet,
                        mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,):
    '''
    retrieve:
        获取自动部署任务
        ---

    list:
        获取自动部署任务列表
        ---

    download_model_task:
        下载模型任务
        ---
            callback_url: 回调地址, 返回后有一个is_success参数, 0(成功)|1(失败)

    stop_task:
        停止任务执行
        ---

    publish_model_task:
        更新模型任务
        ---

    bulk_download_model_task:
        批量下载模型任务
        ---

    bulk_publish_model_task:
        批量更新模型任务
        ---
    '''

    permission_classes = (
        IsAuthenticated,
    )

    queryset = DeployTask.objects.order_by('id')
    # serializer_class = DeployTaskSerializer

    def get_serializer_class(self):
        if self.action == 'download_model_task':
            return DownloadTaskSerializer
        elif self.action == 'publish_model_task':
            return PublishTaskSerializer
        elif self.action == 'bulk_download_model_task':
            return DownloadTaskSerializer
        elif self.action == 'bulk_publish_model_task':
            return PublishTaskSerializer
        return DeployTaskSerializer

    @action(methods=['get'], url_path='stop', detail=True)
    def stop_task(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_finish = True
        instance.status = 3
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(methods=['post'], url_path='download/model', detail=False)
    def download_model_task(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(methods=['post'], url_path='publish/model', detail=False)
    def publish_model_task(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(methods=['post'], url_path='download/model/bulk', detail=False)
    def bulk_download_model_task(self, request, *args, **kwargs):
        data_list = self.bulk_run(request.data)
        return Response(data_list)

    @action(methods=['post'], url_path='publish/model/bulk', detail=False)
    def bulk_publish_model_task(self, request, *args, **kwargs):
        data_list = self.bulk_run(request.data)
        return Response(data_list)

    def bulk_run(self, request_data):
        data_list = []
        for line in request_data:
            serializer = self.get_serializer(data=line)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            data_list.append(serializer.data)
        return data_list


class AwxJobTemplateViewSet(viewsets.GenericViewSet,
                            mixins.RetrieveModelMixin,
                            mixins.ListModelMixin,):
    '''
    任务模版
    ---
    '''

    permission_classes = (
        IsAuthenticated,
    )

    queryset = AwxJobTemplate.objects.order_by('id')
    serializer_class = AwxJobTemplateSerializer


class AwxInventoryViewSet(viewsets.GenericViewSet,
                          mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,):
    '''
    冷柜
    ---
    '''

    permission_classes = (
        IsAuthenticated,
    )

    queryset = AwxInventory.objects.order_by('id')
    serializer_class = AwxInventorySerializer


class AwxPlaybookViewSet(viewsets.GenericViewSet,
                         mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,):
    '''
    任务文件
    ---
    '''

    permission_classes = (
        IsAuthenticated,
    )

    queryset = AwxPlaybook.objects.order_by('id')
    serializer_class = AwxPlaybookSerializer


class InventoryGroupViewSet(viewsets.GenericViewSet,
                            mixins.RetrieveModelMixin,
                            mixins.ListModelMixin,):
    '''
    冷柜组
    ---
    '''

    permission_classes = (
        IsAuthenticated,
    )

    queryset = InventoryGroup.objects.order_by('id')
    serializer_class = InventoryGroupSerializer
