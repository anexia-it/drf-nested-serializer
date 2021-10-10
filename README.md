# DRF Nested Serializer

> :warning: This package is work in progress

## Quick start

1. Download and install:

```bash
pip install git+https://github.com/anexia-it/drf-nested-serializer@master
```

2. Create the NestedSerializer in your Serializer where nested serialization is required:

```python
from drf_nested_serializer import NestedSerializer


class CategorySerializer(NestedSerializer, BaseModelSerializer):
    ...
```

3. Provide metaclass in serializer for related fields 

```python
    ...
    class Meta:
        model = Category
        fields = ['pk', 'url', 'name', 'children', 'books']
        one_to_many_fields = ['children']
```

Metaclass relation types:

* one_to_one_fields
* one_to_many_fields
* many_to_many_direct_fields
* many_to_many_fields
* many_to_one_fields
