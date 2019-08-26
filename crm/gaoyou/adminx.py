import xadmin
from xadmin import views
from .models import EveryStatistics, FaceMatch


class EveryStatisticsAdmin(object):
    # 显示的列
    list_display = ['UserType', 'storeId', 'dateTime', 'male_value', 'female_value', 'early_value', 'young_value',
                    'middle_value', 'old_value']

    # 搜索的字段
    search_fields = ['UserType', 'storeId', 'dateTime', 'male_value', 'female_value', 'early_value', 'young_value',
                     'middle_value', 'old_value']
    # 过滤
    list_filter = ['UserType', 'storeId', 'dateTime', 'male_value', 'female_value', 'early_value', 'young_value',
                   'middle_value', 'old_value']


class FaceMatchAdmin(object):
    # 显示的列
    list_display = ['username', 'phone', 'time', 'library_picture', 'result']

    # 搜索的字段
    search_fields = ['username', 'phone', 'time', 'library_picture', 'result']
    # 过滤
    list_filter = ['username', 'phone', 'time', 'library_picture', 'result']


xadmin.site.register(EveryStatistics, EveryStatisticsAdmin)
xadmin.site.register(FaceMatch, FaceMatchAdmin)

