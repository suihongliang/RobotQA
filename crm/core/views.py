from rest_framework import permissions
from rest_framework import viewsets
from crm.user.models import BackendUser
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class CompanyFilterViewSet(viewsets.GenericViewSet):
    '''
    通过用户公司过滤
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
                    mobiles = BackendUser.objects.filter(
                        group__manager=self.request.user)\
                        .values_list('mobile', flat=True)
                    mobiles_list = list(mobiles)
                    mobiles_list.append(mobile)
                    queryset = queryset.filter(
                        **{self.userfilter_field+'__in': mobiles_list})
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


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            if request.user.role:
                if request.user.role.only_myself:
                    try:
                        return obj.customerrelation.seller.mobile == request.user.mobile
                    except Exception:
                        return True
                else:
                    return True
            else:
                return False
        else:
            return True


class CustomBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, company_id=None, **kwargs):
        UserModel = get_user_model()
        try:
            if company_id:
                user = UserModel.objects.get(username=username,
                                             company_id=company_id,
                                             is_active=True)
            else:
                user = UserModel.objects.filter(username=username,
                                                is_active=True).first()
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except Exception:
            return None
