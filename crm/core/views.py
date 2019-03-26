from rest_framework import permissions
from rest_framework import viewsets


class StoreFilterViewSet(viewsets.GenericViewSet):
    '''
    通过用户过滤门店编号
    '''

    storefilter_field = 'store_code'

    def get_param_store_code(self):
        if self.request.user.is_authenticated:
            store_code = self.request.user.store_code
        else:
            store_code = self.request.query_params.get('store_code')
        return store_code

    def get_queryset(self):
        queryset = super().get_queryset()
        store_code = self.get_param_store_code()
        queryset = queryset.filter(
            **{self.storefilter_field: store_code})
        return queryset


class SellerFilterViewSet(StoreFilterViewSet):
    '''
    销售元权限只能查看自己资源过滤
    '''

    userfilter_field = 'mobile'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            if self.request.user.role:
                if self.request.user.role.only_myself:
                    mobile = self.request.user.mobile
                    queryset = queryset.filter(
                        **{self.userfilter_field: mobile})
            else:
                queryset = queryset.filter(**{self.userfilter_field: ''})
        return queryset


def custom_permission(backend_perms):

    class BackendPermission(permissions.BasePermission):
        '''
        后台权限控制
        '''

        def has_permission(self, request, view):
            perms = backend_perms.get(view.action)
            if not perms:
                return True
            user = request.user
            if user.is_authenticated:
                role = user.role
                if not role:
                    return False
                user_perms = list(user.role.permissions.all().values_list(
                    'code', flat=True))
                if set(user_perms) & set(perms):
                    return True
                else:
                    return False
            else:
                return True

    return BackendPermission
