# from rest_framework import viewsets


class StoreFilterMixin():
    '''
    通过用户过滤门店编号
    '''

    storefilter_field = 'store_code'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user:
            store_code = self.request.user.store_code
            queryset = queryset.filter(
                **{self.storefilter_field: store_code})
        else:
            store_code = self.request.query_params.get('store_code')
            if store_code:
                queryset = queryset.filter(
                    **{self.storefilter_field: store_code})
        return queryset


class SellerFilterMixin():
    '''
    销售元权限只能查看自己资源过滤
    '''

    userfilter_field = 'mobile'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user:
            if self.request.user.role:
                if self.request.user.role.only_myself:
                    mobile = self.request.user.mobile
                    queryset = queryset.filter(
                        **{self.userfilter_field: mobile})
            else:
                queryset = queryset.filter(**{self.userfilter_field: ''})
        return queryset
