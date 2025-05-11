import logging
from django.db import models


class ReportManager(models.Manager):
    def get_all_data(self):
        def get_select_related_fields(model):
            """
            Recursively get all related fields for a model.
            """
            select = []

            # get all field objects for the model
            model_fields = model._meta.get_fields()

            # filter the field objects to get only the relationships
            relationships = [f for f in model_fields if isinstance(f, models.ForeignKey)]

            # loop through the relationships
            for relationship in relationships:
                # get the related model
                related_model = relationship.related_model

                select.append(relationship.name)
                if model != related_model:
                    # recursively call this function to get the related fields for the related model
                    related_select = get_select_related_fields(related_model)

                    # add the related fields to the select list
                    for item in related_select:
                        select.append(f'{relationship.name}__{item}')

            one_to_one = [f.name for f in model_fields if f.one_to_one]
            select.extend(one_to_one)

            return select

        # get all related fields for the model
        select_related_fields = get_select_related_fields(self.model)

        # use prefetch_related or select_related with the related field names
        return self.all().select_related(*select_related_fields)


class ProxyModelReportMixin:
    args_data: dict = {}

    def get_report_data(self):
        report_data = {}
        for method in dir(self):
            if method.startswith('report_'):
                report_data[getattr(self, method).verbose_name] = str(getattr(self, method)())
            if method.startswith('foreign_report_'):
                try:
                    instance, available_methods = getattr(self, method)()
                except TypeError as e:
                    logging.error(f'{e} with {method}')
                else:
                    if instance:
                        for key, value in available_methods.items():
                            report_data[f'{getattr(self, method).verbose_name}.{key}'] = value
            if method.startswith('iterable_report_'):
                report_data.update(getattr(self, method)())
        return report_data

    def get_data(self, data: dict):
        """
        Может принимать любой аргумент, но изначально создавался чтобы получить возможность принять
        данные из формы в proxy модели для подстановки в отчет и вызывает get_report_data()
        :param data: словарь с данными
        :return: вызывает функцию get_report_data()
        """
        # Костыльное решение проблемы с несериализируемыми данными
        try:
            cdn_id = data['credit_document_number']
            data['credit_document_number'] = cdn_id.id
        except KeyError:
            pass

        try:
            credits_tranche_id = data['credits_tranche']
            data['credits_tranche'] = credits_tranche_id.id
        except KeyError:
            pass

        self.args_data['form_data'] = data

        return data

    @staticmethod
    def foreign_report_data(model=None, filter_field: str = '', filter_field_value=None):
        available_methods = {}
        try:
            instance = model.proxy_objects.get_all_data().filter(**{filter_field: filter_field_value}).first()
            if instance:
                available_methods = instance.get_report_data()
        except AttributeError:
            instance = {}
        return instance, available_methods
