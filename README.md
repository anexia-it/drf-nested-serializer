# Django Rest Nested Serializer

> :warning: This package is work in progress

## Quick start

1. Download and install using pip install from PyPi:

```bash
pip install django-cleanhtmlfield
```

2. Create the NestedSerializer in your Serializer where nested serialization is required:

```python
class TechnologySerializer(NestedSerializer, BaseModelSerializer):
    ...
```
