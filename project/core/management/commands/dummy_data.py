import os
import json

from django.core.management.base import BaseCommand, CommandError

from project.core.models import Branch
from project.users.models import Department, Position

DATA_FILES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data_files')

def get_data_from_file(file_name: str) -> dict:
    with open(os.path.join(DATA_FILES, file_name), 'r') as f:
        return json.load(f)

def populate_branches() -> None:
    branches = get_data_from_file('department_position.json')['branches']
    for branch in branches:
        id = branch.pop("id")
        Branch.objects.get_or_create(
            id=id,
            defaults=branch
        )


def populate_departments() -> None:
    departments = get_data_from_file('department_position.json')['departments']
    for depart in departments:
        department, _ = Department.objects.get_or_create(
            name=depart['name'],
            branch_id=int(depart['branch_id'])
        )
        positions = depart.get('positions', None)
        if positions:
            for position in positions:
                Position.objects.get_or_create(
                    department=department,
                    name=position['name']
                )


class Command(BaseCommand):
    def handle(self, *args, **options):
        for func in [populate_branches, populate_departments]:
            func()

    def command_error(self, e):
        raise CommandError(e)

