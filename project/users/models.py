from enum import unique

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from cython_generate_keys import generate_keys, decrypt_private_key, sign_document, verify_signature

# class UserRole(Enum):
#     ADMIN = 'ADMIN'
#     SUPPORT = 'SUPPORT'
#     EMPLOYEE = 'EMPLOYEE'

class UserPermission(models.Model):
    codename = models.CharField(max_length=255, verbose_name='Кодовое имя доступа', unique=True)
    description = models.TextField(verbose_name='Описание доступа', null=True, blank=True)

    class Meta:
        verbose_name = _('Permission')
        verbose_name_plural = _('Permissions')

    def __str__(self):
        return self.codename


class UserRole(models.Model):
    name = models.CharField(verbose_name='Имя роли', max_length=255)
    description = models.TextField(verbose_name='Описание роли', null=True, blank=True)
    permissions = models.ManyToManyField(UserPermission, verbose_name='Доступы роли')

    class Meta:
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')

    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    Default custom user model for Electronic Documents Management.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    fullname = models.CharField(max_length=255, verbose_name="ФИО пользователя", help_text="Введите фио пользователя",
                                null=True, blank=True)
    patronymic = models.CharField(max_length=255, verbose_name="Отчество", help_text="Введите отчество",
                                  null=True, blank=True)
    private_key = models.TextField(blank=True, null=True)
    public_key = models.TextField(blank=True, null=True)
    role = models.ForeignKey(UserRole, verbose_name='Роль пользователя', null=True, blank=True,
                             on_delete=models.PROTECT)
    extra_permissions = models.ManyToManyField(UserPermission, verbose_name='Права доступа пользователя', blank=True)

    def __str__(self):
        return self.fullname

    def generate_keys(self, password: str):
        self.private_key, self.public_key = generate_keys(password)
        self.save()

    def save(self, *args, **kwargs):
        if not self.fullname:
            self.fullname = f"{self.first_name} {self.last_name}"
        super().save(*args, **kwargs)

    def sign_document(self, document: bytes, password: str) -> bytes:
        if self.private_key is None or self.private_key == "":
            raise Exception("Не был найден приватный ключ для подписи")
        signature: bytes = sign_document(self.private_key, password, document)
        return signature

    def verify_signature(self, document: bytes, signature: bytes) -> bool:
        if self.public_key is None or self.private_key == "":
            raise Exception("Не был найден публичный ключ")
        result: bool = verify_signature(self.public_key, document, signature)
        return result

    @property
    def employee(self):
        employee = UserEmployee.objects.filter(user=self, end_date__isnull=True)
        if employee.exists():
            return employee.first()
        return None


    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})

    def has_permission_user(self, perm: str, obj=None) -> bool:
        if self.is_superuser:
            return True
        if self.role is not None:
            if self.role.permissions.filter(codename=perm).exists():
                return True
        if self.extra_permissions.filter(codename=perm).exists():
            return True
        return False


class Department(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название структурного подразделения',
                            help_text='Введите название структурного подразделения')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name='Родительский подразделение',
                               help_text='Выберите родительский подразделение', null=True, blank=True,
                               related_name='children')
    branch = models.ForeignKey('core.Branch', on_delete=models.CASCADE, verbose_name='Филиал', related_name='departments',
                               help_text='Выберите филиал')
    description = models.TextField(verbose_name='Описание структурного подразделения',
                                   help_text='Введите описание структурного подразделения', null=True, blank=True)

    class Meta:
        verbose_name = _('Department')
        verbose_name_plural = _('Departments')

    def __str__(self):
        return f"{self.name} ({self.branch.name})"


class Position(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название должности',
                            help_text='Введите название должности')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='Структурное подразделение',
                                   help_text='Выберите структурное подразделение', related_name='positions')
    description = models.TextField(verbose_name='Описание должности',
                                   help_text='Введите описание должности', null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.department.name})"


class UserEmployee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    position = models.ForeignKey(Position, on_delete=models.CASCADE, verbose_name='Должность', related_name='employees')
    start_date = models.DateField(verbose_name='Дата начала работы')
    end_date = models.DateField(verbose_name='Дата окончания работы', null=True, blank=True)

    def __str__(self):
        return f"{self.user.fullname} ({self.position.name})"

    def save(self, *args, **kwargs):
        if self.__class__.objects.filter(user=self.user, end_date__isnull=True).exists():
            last_position = (self.__class__.objects.filter(user=self.user, end_date__isnull=True).
                             order_by('-start_date').first())
            if last_position.start_date > self.start_date:
                raise Exception("Невозможно назначить должность, которая начинается раньше, чем уже имеющаяся должность")
            self.__class__.objects.filter(user=self.user, end_date__isnull=True).update(end_date=self.start_date)
        super().save(*args, **kwargs)
