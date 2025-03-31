import importlib
import logging
import re
from tokenize import group

from django.conf import settings
from django.core.exceptions import ViewDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.urls import URLPattern, URLResolver, reverse_lazy  # type: ignore
from project.core.models import AvailableUrls, SidebarGroup, SidebarItem, SidebarItemChild

# group_icon_dict = {
#     'Задания': 'fas fa-tasks',
#     'Заявки': 'fas fa-file-signature',
#     'Залоги': 'fas fa-hand-holding-usd',
#     'Кадровый модуль': 'far fa-id-card',
#     'Клиенты': 'fas fa-users',
#     'Кредиты': 'fas fa-money-check',
#     'Онлайн заявки': 'fas fa-globe',
#     'Основные средства': 'fas fa-laptop-house',
#     'Отчеты': 'far fa-file-alt',
#     'Пользователи': 'fas fa-users-cog',
#     'Счета': 'fas fa-money-check',
#     'Транзакции': 'fas fa-file-import',
#     'Управление': 'far fa-compass',
#     'Интеграции': 'fas fa-network-wired',
# }
group_icon_dict = {}

for app in set(settings.PROJECT_APPS) - set(settings.EXCLUDED_APPS):
    views = importlib.import_module(app + '.views')
    names = [x for x in views.__dict__ if not x.startswith('_')]
    globals().update({k: getattr(views, k) for k in names})


def describe_pattern(p):
    return str(p.pattern)


class Command(BaseCommand):
    help = 'Populates sidebar items'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--noinput', action='store_true', help='Не запрашивать подтверждение')

    def handle(self, *args, **options):
        self.sidebar_urls_to_db()
        if SidebarItem.objects.all().count() != 0 and not options['noinput']:
            result = input('Sidebar items already exist. Do you want to delete them? (y/n): ')
            if result == 'y':
                self.refresh_urls()
            else:
                CommandError('Sidebar items already exist. Aborting...')
                return
        try:
            self.stdout.write('Populating sidebar items...')
            self.populate_sidebar_items()
            self.stdout.write('Sidebar items populated successfully!')
        except Exception as e:
            raise CommandError(e)

    def sidebar_urls(self):
        urlconf = 'ROOT_URLCONF'

        views = []
        if not hasattr(settings, urlconf):
            raise CommandError('Settings module {} does not have the attribute {}.'.format(settings, urlconf))

        try:
            urlconf = __import__(getattr(settings, urlconf), {}, {}, [''])
        except Exception as e:
            raise CommandError('Error occurred while trying to load %s: %s' % (getattr(settings, urlconf), str(e)))

        view_functions = self.extract_views_from_urlpatterns(urlconf.urlpatterns)
        for (func, _, url_name) in view_functions:

            if hasattr(func, 'view_class'):
                func = func.view_class
            if hasattr(func, '__name__'):
                func_name = func.__name__
            elif hasattr(func, '__class__'):
                func_name = '%s()' % func.__class__.__name__
            else:
                func_name = re.sub(r' at 0x[0-9a-f]+', '', repr(func))

            url_name = url_name or ''

            views.append((
                url_name,
                func_name,
            ))

        return views

    def extract_views_from_urlpatterns(self, urlpatterns, base='', namespace=None):
        """
        Return a list of views from a list of urlpatterns.
        Each object in the returned list is a three-tuple: (view_func, regex, name)
        """
        views = []
        for p in urlpatterns:
            if isinstance(p, URLPattern):
                try:
                    if not p.name:
                        name = p.name
                    elif namespace:
                        name = '{0}:{1}'.format(namespace, p.name)
                    else:
                        name = p.name
                    pattern = describe_pattern(p)
                    views.append((p.callback, base + pattern, name))
                except ViewDoesNotExist:
                    continue
            elif isinstance(p, URLResolver):
                try:
                    patterns = p.url_patterns
                except ImportError:
                    continue
                if namespace and p.namespace:
                    _namespace = '{0}:{1}'.format(namespace, p.namespace)
                else:
                    _namespace = (p.namespace or namespace)
                pattern = describe_pattern(p)
                views.extend(self.extract_views_from_urlpatterns(patterns, base + pattern, namespace=_namespace))
            elif hasattr(p, '_get_callback'):
                try:
                    views.append((p._get_callback(), base + describe_pattern(p), p.name))
                except ViewDoesNotExist:
                    continue
            elif hasattr(p, 'url_patterns') or hasattr(p, '_get_url_patterns'):
                try:
                    patterns = p.url_patterns
                except ImportError:
                    continue
                views.extend(
                    self.extract_views_from_urlpatterns(patterns, base + describe_pattern(p), namespace=namespace))
            else:
                raise TypeError('%s does not appear to be a urlpattern object' % p)
        return views

    def sidebar_urls_to_db(self):
        for i in self.sidebar_urls():
            try:
                reverse_lazy(i[0])
            except Exception:
                logging.error(f'URL {i[0]} is not available')
            else:
                AvailableUrls.objects.get_or_create(function_name=i[1], url_name=i[0])

    def refresh_urls(self):
        AvailableUrls.objects.all().delete()
        SidebarGroup.objects.all().delete()
        SidebarItem.objects.all().delete()
        SidebarItemChild.objects.all().delete()
        self.sidebar_urls_to_db()

    @staticmethod
    def populate_sidebar_items():
        for url in AvailableUrls.objects.all():
            try:
                _class = globals()[url.function_name]
            except KeyError:
                continue
            else:
                if hasattr(_class, 'sidebar_item_child') and hasattr(_class, 'sidebar_group') \
                        and hasattr(_class, 'sidebar_name'):
                    group, _ = SidebarGroup.objects.get_or_create(
                        name=_class.sidebar_group,
                        icon=group_icon_dict[_class.sidebar_group] if group_icon_dict[_class.sidebar_group] else
                        'far fa-circle')
                    item, _ = SidebarItem.objects.get_or_create(
                        group=group, display_name=_class.sidebar_name,
                        icon=_class.sidebar_icon if hasattr(_class, 'sidebar_icon') else 'far fa-circle')
                    SidebarItemChild.objects.get_or_create(
                        parent_item=item, display_name=_class.sidebar_item_child,
                        url=url,
                        icon=_class.sidebar_icon_child if hasattr(
                            _class, 'sidebar_icon_child') else 'far fa-circle')
                elif hasattr(_class, 'sidebar_group') and hasattr(_class, 'sidebar_name'):
                    group, _ = SidebarGroup.objects.get_or_create(
                        name=_class.sidebar_group,
                        icon=group_icon_dict[_class.sidebar_group] if group_icon_dict[_class.sidebar_group] else
                        'far fa-circle')
                    item, _ = SidebarItem.objects.get_or_create(
                        group=group, display_name=_class.sidebar_name,
                        url=url, icon=_class.sidebar_icon if hasattr(_class, 'sidebar_icon') else 'far fa-circle')
