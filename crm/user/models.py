from datetime import datetime, timedelta

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
import json


class UserEvent:
    def __init__(self, user_id, in_type, in_time, out_time):
        self.user_id = user_id
        self.in_type = in_type
        self.in_time = in_time
        self.out_time = out_time
        self.diff_time = (out_time - in_time).seconds

    def __repr__(self):
        return "<{}: {}>".format(self.user_id, self.diff_time)


class BehaviorStack:
    def __init__(self, user_id):
        self._stack = []
        self.user_id = user_id
        self.value_in = "in"
        self.value_out = "out"
        self.result = []

    def clean(self):
        self._stack = []

    def push(self, bh_type, value):
        if bh_type == self.value_in:
            self.clean()
            self._stack.append(value)
        elif (bh_type == self.value_out) and self._stack:
            if self._stack[0].location != self.value_in:
                return
            v_in = self._stack.pop()
            v_out = value
            # compare value and save to record
            if reach_timeout(v_out.created, v_in.created):
                self.clean()
            else:
                self.clean()
                self.result.append(UserEvent(v_in.user_id, v_in.category, v_in.created, v_out.created))

def reach_timeout(d1, d2):
    df = d2 - d1
    return df > timedelta(minutes=10, seconds=0)

#
# class Store(models.Model):
#
#     store_code = models.CharField(
#         verbose_name='门店编码', max_length=255, unique=True)
#     company_id = models.CharField(
#         max_length=20, verbose_name="公司id")
#
#     def __str__(self):
#         return '.'.join([self.company_id, self.store_code])
#
#     class Meta:
#         verbose_name = '门店关系'


class BackendUserManager(BaseUserManager):

    def _create_user(self, username, mobile, password,
                     is_staff, is_superuser, **extra_fields):
        """
        根据用户名和密码创建一个用户
        """
        if not mobile:
            raise ValueError('mobile必须填写')
        user = self.model(mobile=mobile,
                          username=username,
                          is_active=True,
                          is_staff=is_staff,
                          is_superuser=is_superuser, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, mobile, password=None, **extra_fields):
        return self._create_user(mobile, mobile, password, False, False,
                                 **extra_fields)

    def create_superuser(self, username, mobile, password, **extra_fields):
        return self._create_user(username, mobile, password, True, True,
                                 **extra_fields)


class BaseUserManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

    def origin_all(self):
        return super().get_queryset()


class UserMobileMixin():

    @property
    def mobile(self):
        return self.user.mobile


class BackendPermission(models.Model):

    name = models.CharField(
        max_length=20, unique=True,
        verbose_name="权限名称")
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now)
    code = models.CharField(
        max_length=20, verbose_name='编码')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '后台权限'


class BackendRole(models.Model):

    name = models.CharField(
        max_length=20, verbose_name="组名称")
    permissions = models.ManyToManyField(
        BackendPermission)
    only_myself = models.BooleanField(
        verbose_name='查看自己数据', default=False)
    is_seller = models.BooleanField(
        verbose_name='是否销售', default=False)
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now)
    # store_code = models.CharField(
    #     verbose_name='门店编码', max_length=255)
    company_id = models.CharField(
        max_length=20, verbose_name="公司id")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '后台群组'
        unique_together = (("name", "company_id"),)


class BackendGroup(models.Model):

    name = models.CharField(
        max_length=20, verbose_name="备注名称")
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now)
    manager = models.ForeignKey(
        "user.BackendUser", null=True, blank=True, unique=True,
        on_delete=models.SET_NULL, verbose_name="管理员")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '用户组'
        unique_together = (("name", "manager"),)


class BackendUser(AbstractBaseUser, PermissionsMixin):

    mobile = models.CharField(
        max_length=20, verbose_name="手机号")
    username = models.CharField(
        verbose_name="用户名", max_length=30)
    is_active = models.BooleanField(
        verbose_name="激活", default=True)
    is_staff = models.BooleanField(
        verbose_name="Is Staff", default=False)
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now)
    role = models.ForeignKey(
        BackendRole, null=True, blank=True, on_delete=models.SET_NULL)
    # store_code = models.CharField(
    #     verbose_name='门店编码', max_length=255)
    company_id = models.CharField(
        max_length=20, verbose_name="公司id")
    name = models.CharField(
        max_length=25, verbose_name='昵称', default='')
    group = models.ForeignKey(
        BackendGroup, null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name="用户组")
    avatar = models.URLField(verbose_name="头像链接", max_length=500, blank=True, null=True)

    objects = BackendUserManager()

    USERNAME_FIELD = 'id'
    REQUIRED_FIELDS = ['mobile', ]

    def has_backend_perms(self):
        pass

    def __str__(self):
        return "{}:{}".format(self.company_id, self.mobile)

    class Meta:
        verbose_name = '后台用户'
        swappable = 'AUTH_USER_MODEL'

        unique_together = (("mobile", "company_id"), ("username", "company_id"))


class BaseUser(models.Model):

    mobile = models.CharField(
        max_length=25, db_index=True, verbose_name='用户手机号')
    # store_code = models.CharField(
    #     verbose_name='门店编码', max_length=255)
    company_id = models.CharField(
        max_length=20, verbose_name="公司id")
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now)
    is_active = models.BooleanField(
        verbose_name="是否激活", default=True)

    objects = BaseUserManager()

    def __str__(self):
        company_id = self.company_id or ""
        return "{}:{}".format(company_id, self.mobile)

    class Meta:
        verbose_name = '用户'
        unique_together = (("mobile", "company_id"),)


def before_day():
    return timezone.now() - timedelta(days=1)


class UserInfo(models.Model, UserMobileMixin):
    '''
    用户基本信息
    '''
    INDUSTRY = [
        (0, '其他'),
        (1, '政府机关'),
        (2, '事业单位'),
        (3, '建筑建材'),
        (4, '金融投资'),
        (5, '外贸'),
        (6, '消费零售'),
        (7, '制造行业'),
        (8, '广告传媒'),
        (9, '医药行业'),
        (10, '交通运输'),
        (11, 'IT及互联网'),
        (12, '教育行业'),
        (13, '退休'),
        (14, '商业服务'),
    ]

    user = models.OneToOneField(
        BaseUser, on_delete=models.CASCADE, primary_key=True,
        verbose_name="用户")
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now)
    name = models.CharField(
        max_length=25, verbose_name='用户昵称', default='')
    age = models.IntegerField(
        verbose_name='年龄', default=0)
    gender = models.IntegerField(
        choices=[
            (1, '男'),
            (2, '女'),
            (0, '未知'),
        ], default=0, verbose_name='性别')
    status = models.IntegerField(
        choices=[
            (0, '未接触'),
            (1, '观望中'),
            (2, '购房成功'),
            (3, '接触中'),
        ], default=0, verbose_name='购房状态')
    note = models.TextField(
        verbose_name='备注', default='', null=True, blank=True)
    willingness = models.CharField(
        choices=[
            ('1', '低'),
            ('2', '中'),
            ('3', '高'),
            ('4', '极高'),
        ], max_length=5, verbose_name='客观意愿度', default='1')
    self_willingness = models.CharField(
        choices=[
            ('1', '低'),
            ('2', '中'),
            ('3', '高'),
            ('4', '极高'),
        ], max_length=5, verbose_name='主观意愿度', default='1')
    net_worth = models.CharField(
        max_length=5, verbose_name='净值度', default='')
    is_seller = models.BooleanField(
        verbose_name='是否销售', default=False)
    last_active_time = models.DateTimeField(
        verbose_name='活跃时间', blank=True, null=True)
    access_times = models.IntegerField(
        verbose_name='到访次数', default=0)
    microstore_times = models.IntegerField(
        verbose_name='小店次数', default=0)
    microstore_seconds = models.IntegerField(
        verbose_name="小店总停留秒数", default=0)
    sampleroom_times = models.IntegerField(
        verbose_name='看样板房次数', default=0)
    sampleroom_seconds = models.IntegerField(
        verbose_name="看样板房总停留秒数", default=0)
    sdver_times = models.IntegerField(
        verbose_name='3DVR看房次数', default=0)
    coin = models.IntegerField(
        verbose_name='积分', default=0)
    spend_coin = models.IntegerField(
        verbose_name='花费积分', default=0)
    extra_data = models.TextField(
        verbose_name='额外参数', default=json.dumps({}))
    msg_last_at = models.DateTimeField(
        verbose_name="上次读取消息时间",
        default=before_day)
    industry = models.IntegerField(
        verbose_name='工作行业', choices=INDUSTRY, default=0)
    product_intention = models.CharField(
        max_length=50, verbose_name='意向产品', default='')
    purchase_purpose = models.CharField(
        max_length=50, verbose_name='购买用途', default='')
    big_room_seconds = models.IntegerField(
        verbose_name="大厅总停留时间", default=0)
    is_staff = models.BooleanField(
        verbose_name="是否为员工", default=False)
    buy_done = models.BooleanField(
        verbose_name="是否成交", default=False)
    introducer_name = models.CharField(
        max_length=50, verbose_name="介绍人姓名",
        blank=True, null=True)
    introducer_mobile = models.CharField(
        max_length=50, verbose_name="介绍人手机号码",
        blank=True, null=True)
    tags = models.TextField(
        verbose_name="标签", null=True,
        blank=True, max_length=500)

    work_space = models.CharField(verbose_name="工作区域", max_length=100, blank=True, null=True)
    live_space = models.CharField(verbose_name="工作区域", max_length=100, blank=True, null=True)
    avatar = models.URLField(verbose_name="头像链接", max_length=500, blank=True, null=True)

    target_of_buy_house = models.CharField(max_length=500, verbose_name='购房目的', null=True, blank=True)

    community = models.CharField(
        choices=[
            ('1', '龙蟠里'),
            ('2', '虎踞湾'),
        ], max_length=5, verbose_name='选择小区', null=True, blank=True)

    area_of_house = models.CharField(
        choices=[
            ('1', '100-110m2'),
            ('2', '110-120m2'),
            ('3', '120-130m2'),
            ('4', '130-140m2'),
            ('5', '140m2以上'),
        ], max_length=5, verbose_name='面积需求', null=True, blank=True)

    budget_of_house = models.CharField(
        choices=[
            ('1', '80万以下'),
            ('2', '80-90万'),
            ('3', '91-100万'),
            ('4', '101-110万'),
            ('5', '111-120万'),
            ('6', '120万以上'),
        ], max_length=5, verbose_name='预算', null=True, blank=True)

    have_discretion = models.BooleanField(verbose_name="是否为买房决策人?", default=False)
    times_of_buy = models.CharField(
        choices=[
            ('1', '首次置业'),
            ('2', '二次置业'),
            ('3', '三次置业'),
            ('4', '四次置业及以上'),
        ], max_length=5, verbose_name='置业次数', null=True, blank=True)
    remark = models.CharField(verbose_name="备注", null=True, blank=True, max_length=500)
    buy_count = models.PositiveIntegerField(verbose_name="成交套数", default=0)
    referrer = models.CharField(verbose_name="介绍人", max_length=100, null=True, blank=True)
    called_times = models.PositiveIntegerField(verbose_name="被访问次数", default=0)

    @property
    def tag_list(self):
        if not self.tags:
            return []
        return self.tags.split("|")

    def get_extra_data_json(self):
        try:
            return json.loads(self.extra_data)
        except json.JSONDecodeError:
            return {}

    def __str__(self):
        company_id = self.user.company_id or ""
        return "{}:{}".format(company_id, self.mobile)

    class Meta:
        verbose_name = '用户基本信息'


class UserOnlineOrder(models.Model, UserMobileMixin):
    '''
    用户在线点餐记录
    '''

    user = models.ForeignKey(
        BaseUser, on_delete=models.CASCADE, verbose_name="用户")
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now)
    location = models.CharField(
        max_length=50, verbose_name='点餐位置')
    detail = models.TextField(
        verbose_name='点餐详情', default='')

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = '用户在线点餐'


class UserBehavior(models.Model, UserMobileMixin):

    user = models.ForeignKey(
        BaseUser, on_delete=models.CASCADE, verbose_name="用户(外键)")
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now)
    """
    access: 到访(摄像头)
    signup: 注册
    sampleroom: 样板房
    sellerbind: 绑定销售
    3dvr: 3d看房
    microstore: 门店到访
    seller_call: 销售电话访问

    """
    category = models.CharField(
        verbose_name='类别', max_length=20)
    location = models.CharField(
        max_length=50, verbose_name='位置')
    visited_mobile = models.CharField(verbose_name="被访人手机号", max_length=100, null=True, blank=True)

    result = models.IntegerField(
        choices=[
            (0, '未勾选'),
            (1, '正确'),
            (2, '错误'),
        ], default=0, verbose_name='复查结果')
    lib_image_url = models.URLField(verbose_name="脸库图像", max_length=255, null=True, blank=True)
    face_image_url = models.URLField(verbose_name="捕捉图像", max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = '用户行为'


class StayTime(models.Model):
    user = models.ForeignKey(
        BaseUser, on_delete=models.CASCADE, verbose_name="用户")
    sample_seconds = models.IntegerField(verbose_name="样板房逗留时间", default=0)
    micro_seconds = models.IntegerField(verbose_name="微店逗留时间", default=0)
    big_room_seconds = models.IntegerField(verbose_name="大厅逗留时间", default=0)
    created_at = models.DateField(verbose_name="创建于")

    class Meta:
        verbose_name = verbose_name_plural = "大厅逗留时间"

    def __str__(self):
        return self.user.mobile


class UserVisit(models.Model):
    # 不去重
    all_access_total = models.IntegerField(verbose_name="来访人次", default=0)
    all_sample_room_total = models.IntegerField(verbose_name="样板房参观人次", default=0)
    all_micro_store_total = models.IntegerField(verbose_name="小店参数人次", default=0)

    # 去重
    access_total = models.IntegerField(verbose_name="来访人数", default=0)
    register_total = models.IntegerField(verbose_name="注册人数", default=0)
    sample_room_total = models.IntegerField(verbose_name="样板房参观人数", default=0)
    micro_store_total = models.IntegerField(verbose_name="小店参数人数", default=0)
    created_at = models.DateField(verbose_name="创建于", unique_for_date=True)
    company_id = models.CharField(max_length=20, verbose_name="公司id", blank=True, null=True)

    class Meta:
        verbose_name = verbose_name_plural = "参观数据"

    def __str__(self):
        return str(self.created_at) if self.created_at else ""


class UserDailyData(models.Model):
    user = models.ForeignKey(
        BaseUser, on_delete=models.CASCADE, verbose_name="用户")
    created_at = models.DateField(verbose_name="创建于")

    store_times = models.IntegerField(verbose_name="参观小店次数", default=0)
    sample_times = models.IntegerField(verbose_name="参观样板房次数", default=0)
    access_times = models.IntegerField(verbose_name="到访次数", default=0)

    total_time = models.IntegerField(verbose_name="总秒数", default=0)
    store_time = models.IntegerField(verbose_name="参观小店秒数", default=0)
    sample_time = models.IntegerField(verbose_name="参观样板房秒数", default=0)
    big_room_time = models.IntegerField(verbose_name="大厅停留秒数", default=0)

    class Meta:
        verbose_name = verbose_name_plural = "没人每天统计数据"

    def __str__(self):
        return self.user.mobile

    @classmethod
    def daily_times_compute(cls, start, end, company_id):
        cate_set = ['access', 'sampleroom', 'microstore']
        user_id_list = UserBehavior.objects.filter(
            user__seller__isnull=True, category__in=cate_set,
            user__userinfo__is_staff=False,
            created__gte=start,
            created__lte=end,
            user__company_id=company_id,
        ).values_list('user_id', flat=True).distinct()
        for user_id in user_id_list:
            all_access_total = 0
            last_at = UserBehavior.objects.filter(
                user_id=user_id,
                user__seller__isnull=True,
                created__gte=start,
                created__lte=end,
                category__in=cate_set, user__userinfo__is_staff=False).latest('created').created
            first_at = UserBehavior.objects.filter(
                user_id=user_id,
                created__gte=start,
                created__lte=end,
                user__seller__isnull=True,
                category__in=cate_set, user__userinfo__is_staff=False).latest('-created').created
            total_time = (last_at - first_at).seconds
            if last_at - first_at <= timedelta(hours=4):
                all_access_total += 1
            elif timedelta(hours=4) < last_at - first_at <= timedelta(hours=8):
                all_access_total += 2
            else:
                if UserBehavior.objects.filter(
                        created__gte=start,
                        created__lte=end,
                ).filter(
                    user_id=user_id,
                    user__seller__isnull=True, category__in=cate_set,
                    user__userinfo__is_staff=False,
                    created__gt=first_at + timedelta(hours=4),
                    created__lte=first_at + timedelta(hours=8)).exists():
                    all_access_total += 3
                else:
                    all_access_total += 2

            all_sample_room_total = UserBehavior.objects.filter(
                user_id=user_id,
                user__userinfo__is_staff=False,
                user__seller__isnull=True,
                category='sampleroom',
                location='in',
                created__gte=start,
                created__lte=end).count()
            all_micro_store_total = UserBehavior.objects.filter(
                user_id=user_id,
                user__userinfo__is_staff=False,
                user__seller__isnull=True,
                category='microstore',
                location='in',
                created__gte=start,
                created__lte=end).count()
            UserDailyData.objects.update_or_create(
                user_id=user_id, created_at=start.date(),
                defaults={
                    'total_time': total_time,
                    'store_times': all_micro_store_total,
                    'sample_times': all_sample_room_total,
                    'access_times': all_access_total
                }
            )

    @classmethod
    def daily_time_compute(cls, start, end, company_id):
        microstore_records = UserBehavior.objects.filter(
            user__seller__isnull=True, category='microstore',
            user__userinfo__is_staff=False,
            created__gte=start,
            created__lte=end,
            user__company_id=company_id,
        )
        events = {}
        for index, r in enumerate(microstore_records):
            if r.user_id not in events:
                events[r.user_id] = BehaviorStack(r.user_id)
            bh_stack = events[r.user_id]
            bh_stack.push(r.location, r)
        for uid, event in events.items():
            store_time = sum([r.diff_time for r in event.result])
            UserDailyData.objects.update_or_create(
                user_id=uid, created_at=start.date(),
                defaults={
                    'store_time': store_time
                }
            )

        sampleroom_records = UserBehavior.objects.filter(
            user__seller__isnull=True, category='sampleroom',
            user__userinfo__is_staff=False,
            created__gte=start,
            created__lte=end,
            user__company_id=company_id,
        )
        events = {}
        for index, r in enumerate(sampleroom_records):
            if r.user_id not in events:
                events[r.user_id] = BehaviorStack(r.user_id)
            bh_stack = events[r.user_id]
            bh_stack.push(r.location, r)
        for uid, event in events.items():
            sample_time = sum([r.diff_time for r in event.result])
            UserDailyData.objects.update_or_create(
                user_id=uid, created_at=start.date(),
                defaults={
                    'sample_time': sample_time
                }
            )
        data_list = UserDailyData.objects.filter(created_at=start.date()).all()
        for data in data_list:
            data.big_room_time = data.total_time - data.store_time - data.sample_time
            data.save()


class WebsiteConfig(models.Model):
    http_host = models.CharField(
        verbose_name="域名", max_length=100,
        unique=True)
    company_id = models.CharField(
        verbose_name="公司id", max_length=20,
        null=True)
    config = models.TextField(
        verbose_name="配置json")

    class Meta:
        verbose_name = verbose_name_plural = "后台配置"

    def __str__(self):
        return self.http_host


class SubTitle(models.Model):
    no = models.IntegerField(verbose_name="序号", default=0)
    name = models.CharField(verbose_name="标题名", max_length=200, blank=True, null=True)
    is_single = models.BooleanField(verbose_name="是否单选", default=True)
    company_id = models.CharField(
        verbose_name="公司id", max_length=20,
        null=True)

    class Meta:
        verbose_name = verbose_name_plural = "意向购买问题"

    def __str__(self):
        return self.name


class SubTitleChoice(models.Model):
    sub_title = models.ForeignKey(SubTitle, verbose_name="意向购买问题", on_delete=models.CASCADE, blank=True, null=True)
    content = models.CharField(verbose_name="选项内容", max_length=200,  blank=True, null=True)

    class Meta:
        verbose_name = verbose_name_plural = "意向购买选项"

    def __str__(self):
        return self.content

class SubTitleRecord(models.Model):
    user = models.ForeignKey(
        BaseUser, on_delete=models.CASCADE, verbose_name="用户")
    sub_title = models.ForeignKey(SubTitle, verbose_name="意向购买问题", on_delete=models.CASCADE, blank=True, null=True)
    choice_choose = models.ManyToManyField(SubTitleChoice, verbose_name="意向购买问题答案")

    class Meta:
        verbose_name = verbose_name_plural = "意向记录"


class VR(models.Model):
    company_id = models.CharField(verbose_name="公司id", max_length=20, null=True)
    left = models.URLField(verbose_name="左")
    right = models.URLField(verbose_name="右")

    class Meta:
        verbose_name = verbose_name_plural = "VR链接"

    def __str__(self):
        return self.company_id or ""
