# Generated by Django 5.0.12 on 2025-04-21 03:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_sidebaritemchild_parent_item'),
    ]

    operations = [
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.SmallIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, verbose_name='Название филиала')),
                ('address', models.CharField(max_length=255, verbose_name='Адрес филиала')),
                ('open_date', models.DateField(verbose_name='Дата открытия')),
                ('close_date', models.DateField(blank=True, null=True, verbose_name='Дата закрытия')),
                ('is_active', models.BooleanField(default=True, verbose_name='Филиал активен')),
            ],
        ),
    ]
