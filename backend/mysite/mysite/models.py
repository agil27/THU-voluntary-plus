from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, User
from datetime import datetime, timedelta

class WX_OPENID_TO_THUID(models.Model):
    OPENID = models.CharField(max_length=100, primary_key=True)
    THUID = models.IntegerField()

class VOLUNTEER(models.Model):
    THUID = models.IntegerField(primary_key=True)
    NAME = models.CharField(max_length=100)
    DEPARTMENT = models.TextField()
    NICKNAME = models.CharField(max_length=100)
    SIGNATURE = models.TextField()
    PHONE = models.TextField()
    VOLUNTEER_TIME = models.FloatField(default=0)
    EMAIL = models.TextField()


'''
class UserManager(BaseUserManager):
    def _create_user(self , Identity, username, password, **kwargs):
        if not Identity:
            raise  ValueError("必须要确认用户身份！")
        if not password:
            raise  ValueError("必须输入密码！")
        user = self.model( Identity = Tdentity, username= username , **kwargs)
        user.set_password( password )
        user.save()
        return user
    def create_user(self,  telephone, username, password, **kwargs):
        kwargs['is_superuser'] = False
        return self._create_user( telephone = telephone, username=username, password = password, **kwargs )
    def create_superuser(self, telephone, username, password, **kwargs):
        kwargs['is_superuser'] = True
        return  self._create_user( telephone = telephone, username=username, password = password, **kwargs )
class User(AbstractBaseUser):  # 老师或志愿团体
    username = models.CharField(max_length=50, unique=True)
    Identity = models.IntegerField(verbose_name='身份', blank=True, null=True)  # 0 表示老师， 1表示志愿团体
    USERNAME_FIELD = "username"
    objects = UserManager()
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True
    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
'''


class UserIdentity(models.Model):
    # isTeacher = models.BooleanField(verbose_name='身份', default=False)
    isTeacher = models.IntegerField(verbose_name = '身份',default=0)  # 0未分配身份,1老师,2志愿团体
    setuptime = models.CharField(max_length=255, verbose_name='创立时间')
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    # user = models.OneToOneField(to=User, on_delete=models.CASCADE)

    groupname = models.CharField(max_length=255, verbose_name='团队名称')
    email = models.CharField(max_length=255, verbose_name='邮箱')
    phone = models.CharField(max_length=255, verbose_name='电话')
    about = models.CharField(max_length=2000,verbose_name='团队简介')

    members = models.CharField(max_length=2000,verbose_name='团队成员')
    #membersname = models.CharField(max_length=255, verbose_name='团队成员名字')
    #subjects = models.CharField(max_length=255, verbose_name='团队成员院系')

    status = models.IntegerField(verbose_name='是否通过审核', default=0) # 0待审核，1通过,-1没通过

class VerificationCode(models.Model):
    VerificationCode = models.CharField(max_length=255,verbose_name='邀请码')
