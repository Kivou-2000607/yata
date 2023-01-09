from collections import defaultdict

from django.apps import apps


class BulkdManager:
    def __init__(self, chunk_size=100):
        self._create_queues = defaultdict(list)
        self.chunk_size = chunk_size

    def add(self, obj):
        model_class = type(obj)
        model_key = model_class._meta.label
        self._create_queues[model_key].append(obj)
        if len(self._create_queues[model_key]) >= self.chunk_size:
            self._commit(model_class)

    def done(self):
        for model_name, objs in self._create_queues.items():
            if len(objs) > 0:
                self._commit(apps.get_model(model_name))


class BulkCreateManager(BulkdManager):
    def __init__(self, chunk_size=100):
        self._create_queues = defaultdict(list)
        self.chunk_size = chunk_size

    def _commit(self, model_class):
        model_key = model_class._meta.label
        model_class.objects.bulk_create(self._create_queues[model_key])
        self._create_queues[model_key] = []


class BulkUpdateManager(BulkdManager):
    def __init__(self, fields, chunk_size=100):
        self._create_queues = defaultdict(list)
        self.chunk_size = chunk_size
        self.fields = fields

    def _commit(self, model_class):
        model_key = model_class._meta.label
        model_class.objects.bulk_update(self._create_queues[model_key], self.fields)
        self._create_queues[model_key] = []
