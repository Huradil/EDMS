import django_tables2 as tables

from.models import Department, Position


class DepartmentTable(tables.Table):
    class Meta:
        model = Department
        fields = ('name', 'parent', 'branch', 'description')
        attrs = {
            'class': 'table table-hover align-middle',
            'thead_class': 'text-uppercase',
            'th': {'style': 'font-size: 0.9rem'}
        }
        template_name = 'pages/django_tables2.html'


class PositionTable(tables.Table):
    class Meta:
        model = Position
        fields = ('name', 'department', 'description')
        attrs = {
            'class': 'table table-hover align-middle',
            'thead_class': 'text-uppercase',
            'th': {'style': 'font-size: 0.9rem'}
        }
        template_name = 'pages/django_tables2.html'
