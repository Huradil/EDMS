from django.utils.timezone import datetime

from project.core.models import SidebarGroup

def get_template_data(request):
    sidebar_urls = SidebarGroup.objects.all().order_by("name").\
        prefetch_related("items", "items__available_url")
    version = "0.1"
    operation_date = datetime.now().date()

    context = {
        "sidebar_urls": sidebar_urls,
        "version": version,
        "operation_date": operation_date,
    }
    return context
