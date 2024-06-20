from django.db.models.query import QuerySet
from rest_framework import serializers


class QueryOptimizer:
    def __new__(cls, *args, **kwargs):

        if isinstance(kwargs.get('data', None), QuerySet) and hasattr(cls, 'Meta'):

            if hasattr(cls.Meta, 'select_related'):
                kwargs['data'] = kwargs['data'].select_related(*cls.Meta.select_related)

            if hasattr(cls.Meta, 'load_only'):
                kwargs['data'] = kwargs['data'].only(*cls.Meta.load_only)

        return super().__new__(cls, *args, **kwargs)


class Serializer(QueryOptimizer, serializers.Serializer):
    pass

class ModelSerializer(QueryOptimizer, serializers.ModelSerializer):
    pass

class HyperlinkedModelSerializer(QueryOptimizer, serializers.HyperlinkedModelSerializer):
    pass
