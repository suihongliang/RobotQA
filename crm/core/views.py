from rest_framework import permissions
from rest_framework import viewsets


class CompanyFilterViewSet(viewsets.GenericViewSet):
    '''
    通过用户过滤门店编号
    '''

    companyfilter_field = 'company_id'

    def get_param_company_id(self):
        if self.request.user.is_authenticated:
            company_id = self.request.user.company_id
        else:
            company_id = self.request.query_params.get('company_id')
        return company_id

    def get_queryset(self):
        queryset = super().get_queryset()
        company_id = self.get_param_company_id()
        queryset = queryset.filter(
            **{self.companyfilter_field: company_id})
        return queryset


class SellerFilterViewSet(CompanyFilterViewSet):
    '''
    销售员权限只能查看自己资源过滤
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
