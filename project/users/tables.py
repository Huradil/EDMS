import django_tables2 as tables

from.models import Department


class DepartmentTable(tables.Table):
    class Meta:
        model = Department
        fields = ('name', 'parent', 'branch', 'description')
        attrs = {
            'class': 'table table-hover align-middle',
            'thead_class': 'text-uppercase',
            'th': {'style': 'font-size: 0.9rem'}
        }
