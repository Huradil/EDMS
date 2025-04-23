from django.urls import path

from .views import user_detail_view
from .views import user_redirect_view
from .views import user_update_view
from .views import UserCreateView
from .views import (UserGetKeys, DepartmentCreateView, DepartmentListView, PositionCreateView, PositionListView,
                    EmployeeCreateView)

app_name = "users"
urlpatterns = [
    # hr
    path('department_create/', view=DepartmentCreateView.as_view(), name='department_create'),
    path('department_list/', view=DepartmentListView.as_view(), name='department_list'),
    path('position_create/', view=PositionCreateView.as_view(), name='position_create'),
    path('position_list/', view=PositionListView.as_view(), name='position_list'),
    path('employee_create/', view=EmployeeCreateView.as_view(), name='employee_create'),

    # users
    path('user_create/', view=UserCreateView.as_view(), name='user_create'),
    path('generate_keys/', view=UserGetKeys.as_view(), name='generate_keys'),
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<str:username>/", view=user_detail_view, name="detail"),
]
