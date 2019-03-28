from rest_framework.response import Response


class ResInfo(Response):

    def __init__(self, msg='', data='', code=200, *arg, **kwargs):
        data = dict(code=code, msg=msg, data=data)
        super(ResInfo, self).__init__(data, *arg, **kwargs)
