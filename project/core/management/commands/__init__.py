import abc
from django.core.management.base import BaseCommand, CommandError

class CommandProxy(BaseCommand):
    """
    Базовый класс для команд, заполняющих базу данных начальными данными

    Переопределите метод populate_all для заполнения базы данных
    """
    help = 'Заполнить базу данных начальными данными'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--noinput', action='store_true', help='Не запрашивать подтверждение')

    def handle(self, *args, **options):
        no_input = options.get('noinput')
        if no_input:
            self.stdout.write('Заполнение началось')
            self.populate_all()
            self.stdout.write('Заполнение завершено')
        else:
            answer = input('Вы уверены, что хотите удалить все данные и заполнить их заново? (y/n) ')
            if answer == 'y':
                self.stdout.write('Заполнение началось')
                self.populate_all()
                self.stdout.write('Заполнение завершено')
            else:
                self.stdout.write('Заполнение отменено')

    @abc.abstractmethod
    def populate_all(self):
        pass

    def command_error(self, e):
        raise CommandError(e)
