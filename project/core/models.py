from django.db import models
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.utils.translation import gettext_lazy as _
from project.users.models import User


class Branch(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(verbose_name='Название филиала', max_length=255)
    address = models.CharField(verbose_name='Адрес филиала', max_length=255)
    open_date = models.DateField(verbose_name='Дата открытия')
    close_date = models.DateField(verbose_name='Дата закрытия', null=True, blank=True)
    is_active = models.BooleanField(verbose_name='Филиал активен', default=True)

    class Meta:
        verbose_name = _('Branch')
        verbose_name_plural = _('Branches')

    def __str__(self):
        return self.name


class SidebarGroup(models.Model):
    name = models.CharField(verbose_name='Группа бокового меню', max_length=255)
    icon = models.CharField(verbose_name='Иконка бокового меню', max_length=255)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for user in User.objects.all():
            key = make_template_fragment_key('sidebar', [user.username])
            cache.delete(key)

    class Meta:
        verbose_name = 'Группа бокового меню'
        verbose_name_plural = 'Группы бокового меню'


class AvailableUrls(models.Model):
    function_name = models.CharField(verbose_name='Название', max_length=255)
    url_name = models.CharField(verbose_name='URL', max_length=255)

    def __str__(self):
        return f'{self.function_name} - {self.url_name}'

    class Meta:
        verbose_name = 'Допступный url'
        verbose_name_plural = 'Доступные url'


class SidebarItem(models.Model):
    name = models.CharField(verbose_name='Название', max_length=255)
    icon = models.CharField(verbose_name='Иконка', max_length=255)
    available_url = models.ForeignKey(AvailableUrls, verbose_name='url', null=True, blank=True,
                                      on_delete=models.CASCADE)
    group = models.ForeignKey(SidebarGroup, verbose_name='Группа бокового меню', on_delete=models.CASCADE,
                              related_name='items')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for user in User.objects.all():
            key = make_template_fragment_key('sidebar', [user.username])
            cache.delete(key)

    class Meta:
        verbose_name = 'Элемент бокового меню'
        verbose_name_plural = 'Элементы бокового меню'


class SidebarItemChild(models.Model):
    name = models.CharField(verbose_name='Название', max_length=255)
    icon = models.CharField(verbose_name='Иконка', max_length=255)
    available_url = models.ForeignKey(AvailableUrls, verbose_name='url', on_delete=models.CASCADE)
    parent_item = models.ForeignKey(SidebarItem, verbose_name='Элемент бокового меню', on_delete=models.CASCADE,
                                    related_name='children')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for user in User.objects.all():
            key = make_template_fragment_key('sidebar', [user.username])
            cache.delete(key)

    class Meta:
        verbose_name = 'Элемент бокового подменю'
        verbose_name_plural = 'Элементы бокового подменю'
