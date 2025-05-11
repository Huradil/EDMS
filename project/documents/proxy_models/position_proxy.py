from project.users.models import UserEmployee, Position
from . import ProxyModelReportMixin, ReportManager


class UserEmployeeProxy(ProxyModelReportMixin, UserEmployee):
    class Meta:
        proxy = True

    proxy_objects = ReportManager()

    def report_fullname(self):
        return self.user.fullname

    report_fullname.verbose_name = 'Фио'

    def report_first_name(self):
        return self.user.first_name

    report_first_name.verbose_name = 'Имя'

    def report_last_name(self):
        return self.user.last_name

    report_last_name.verbose_name = 'Фамилия'

    def report_patronymic(self):
        patronymic = self.user.patronymic
        if patronymic is None:
            return ''
        return patronymic

    report_patronymic.verbose_name = 'Отчество'

    def report_chief_accountant(self):
        position = Position.objects.filter(name='Главный бухгалтер').first()
        if position is None:
            return ''
        employee_position = UserEmployee.objects.select_related('user').filter(position=position).first()
        if employee_position is None:
            return ''
        return employee_position.user.fullname

    report_chief_accountant.verbose_name = 'ГлавныйБухгалтер'

    def report_deputy_chief_accountant(self):
        position = Position.objects.filter(name='Зам. главного бухгалтера').first()
        if position is None:
            return ''
        employee_position = UserEmployee.objects.select_related('user').filter(position=position).first()
        if employee_position is None:
            return ''
        return employee_position.user.fullname

    report_deputy_chief_accountant.verbose_name = 'ЗамГлавныйБухгалтер'

    def report_head_edu_department(self):
        position = Position.objects.filter(name='Начальник учебного управления').first()
        if position is None:
            return ''
        employee_position = UserEmployee.objects.select_related('user').filter(position=position).first()
        if employee_position is None:
            return None
        return employee_position.user.fullname

    report_head_edu_department.verbose_name = 'НачУчебногоУправления'





