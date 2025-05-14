from django_tables2 import tables
from django.utils.html import format_html
from project.documents.models import Document


class DocumentTable(tables.Table):
    button = tables.Column(verbose_name='Действие', empty_values=(), orderable=False)

    class Meta:
        model = Document
        fields = ('name', 'created_by', 'created_at', 'updated_at')
        attrs = {
            'class': 'table table-hover align-middle',
            'thead_class': 'text-uppercase',
            'th': {'style': 'font-size: 0.9rem'}
        }
        template_name = 'pages/django_tables2.html'

    def render_button(self, record):
        return format_html(record.get_button())

