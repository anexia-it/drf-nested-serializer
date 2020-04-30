from django.core.exceptions import ValidationError as CoreValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


__all__ = [
    "NestedSerializer",
]


class BaseNestedSerializer(serializers.ModelSerializer):
    def _manage_one_to_many_assignment(
        self,
        instance,
        related_objects,
        related_model=None,
        related_serializer=None,
        relation_name=None,
        inverse_relation_name=None,
        errors=None,
    ):
        """
        Update previous relations (set null/blank or remove unwanted, depending on the related model.field definition),
        set the new relations (create if not already exist)
        :param instance:
        :param related_objects:
        :param related_model:
        :param related_serializer:
        :param relation_name:
        :param inverse_relation_name:
        :param errors:
        :return:
        """
        if errors is None:
            errors = []

        # Get common assignments (existing and still wanted related objects)
        related_object_pks = []
        for related_object in related_objects:
            if isinstance(related_object, related_model):
                if hasattr(related_object, "pk"):
                    related_object_pks.append(related_object.pk)
            elif "pk" in related_object:
                related_object_pks.append(related_object["pk"])

        # Update old related objects (set inverse_relation_name fields to null/blank or delete the objects)
        inverse_field = [
            field
            for field in related_model._meta.fields
            if field.name == inverse_relation_name
        ][0]

        if inverse_field.null:
            # unset (set blank) the inverse relation to all currently related_objects
            # not supposed to be kept (not specified in the request)
            related_model.objects.filter(**{inverse_relation_name: instance}).exclude(
                pk__in=related_object_pks
            ).update(**{inverse_relation_name: None})
        elif inverse_field.blank:
            # unset (set blank) the inverse relation to all currently related_objects
            # not supposed to be kept (not specified in the request)
            related_model.objects.filter(**{inverse_relation_name: instance}).exclude(
                pk__in=related_object_pks
            ).update(**{inverse_relation_name: ""})
        else:
            # delete all currently related_objects
            # not supposed to be kept (not specified in the request)
            queryset = related_model.objects.filter(
                **{inverse_relation_name: instance}
            ).exclude(pk__in=related_object_pks,)

            if hasattr(related_serializer.Meta, "one_to_many_fields_filters"):
                if relation_name in related_serializer.Meta.one_to_many_fields_filters:
                    queryset = queryset.filter(
                        **related_serializer.Meta.one_to_many_fields_filters[
                            relation_name
                        ]
                    )

            queryset.delete()

        # Set the new relations (create if not exist yet)
        # TODO: make unittest to prove and explain behaviour!
        # (if pk is given, but object is gone/belongs to another template, create a new one)
        related_errors = []
        related_error_found = False
        for related_object in related_objects:
            try:
                if isinstance(related_object, related_model):
                    setattr(related_object, inverse_relation_name, instance)
                    related_object.save()

                    # add the new related child to the parent instance
                    getattr(instance, relation_name).add(related_object)
                else:
                    related_object[inverse_relation_name] = instance

                    if related_serializer:
                        self._manage_one_to_many_child(
                            instance=instance,
                            child=related_object,
                            child_model=related_model,
                            child_serializer=related_serializer,
                            relation_name=relation_name,
                        )

                related_errors.append({})
            except CoreValidationError as e:
                if hasattr(e, "message_dict"):
                    related_errors.append(e.message_dict)
                    related_error_found = True
                else:
                    raise e
            except ValidationError as e:
                if hasattr(e, "detail"):
                    related_errors.append(e.detail)
                    related_error_found = True
                else:
                    raise e
            except Exception as e:
                if hasattr(e, "message_dict"):
                    related_errors.append(e.message_dict)
                    related_error_found = True
                elif hasattr(e, "detail"):
                    related_errors.append(e.detail)
                    related_error_found = True
                else:
                    raise e

        if related_error_found:
            last_err = next(s for s in reversed(related_errors) if s)
            for rel_err in related_errors:
                errors.append(rel_err)
                if rel_err == last_err:
                    break

    def _manage_one_to_many_child(self, instance, child, child_serializer, child_model, relation_name):
        """
        Outsourced update/creation of the child object to allow for custom behaviour in certain Serializers,
        e.g. SubTemplateGroupSerializer(special behaviour for nested bulk management of TemplateGroups within a
        Campaign)
        :param instance:
        :param child:
        :param child_serializer:
        :param child_model:
        :param relation_name:
        :param inverse_relation_name:
        :return:
        """
        if "pk" not in child:
            child_instance = child_serializer.create(validated_data=child)
            getattr(instance, relation_name).add(child_instance)
        else:
            try:
                child_instance = getattr(instance, relation_name).get(pk=child["pk"])
                child_serializer.update(instance=child_instance, validated_data=child)
            except child_model.DoesNotExist:
                child.pop("pk")
                child_instance = child_serializer.create(validated_data=child)
                getattr(instance, relation_name).add(child_instance)

    def _manage_many_to_one_assignment(
        self, related_object, related_model=None, related_serializer=None, errors=[],
    ):
        """
        Create the new relation if it doesn't already exist
        :param related_object:
        :param related_model:
        :param related_serializer:
        :param errors:
        :return:
        """
        # Set the new relation (create if not exists yet)
        # (if pk is given, but object is gone/belongs to another instance, create a new one)
        related_instance = None
        try:
            if related_serializer:
                if "pk" not in related_object:
                    related_instance = related_serializer.create(
                        validated_data=related_object
                    )
                else:
                    try:
                        related_object_instance = related_model.objects.get(
                            pk=related_object["pk"]
                        )
                        related_instance = related_serializer.update(
                            instance=related_object_instance,
                            validated_data=related_object,
                        )
                    except related_model.DoesNotExist:
                        related_object.pop("pk")
                        related_instance = related_serializer.create(
                            validated_data=related_object
                        )
        except CoreValidationError as e:
            if hasattr(e, "message_dict"):
                errors.append(e.message_dict)
            else:
                raise e
        except ValidationError as e:
            if hasattr(e, "detail"):
                errors.append(e.detail)
            else:
                raise e
        except Exception as e:
            if hasattr(e, "message_dict"):
                errors.append(e.message_dict)
            elif hasattr(e, "detail"):
                errors.append(e.detail)
            else:
                raise e

        return related_instance

    def _manage_many_to_many_assignment(
        self,
        instance,
        related_objects,
        related_model=None,
        related_serializer=None,
        intermediate_relation_name=None,
        intermediate_inverse_relation_name=None,
        errors=None,
    ):
        """
        Update previous relations (set null/blank or delete unwanted, depending on the related model.field definition),
        set the new relations (create if not already exist)
        :param instance:
        :param related_objects:
        :param related_model:
        :param related_serializer:
        :param intermediate_relation_name:
        :param intermediate_inverse_relation_name:
        :param errors:
        :return:
        """
        if errors is None:
            errors = []

        # Get common assignments (existing and still wanted related objects)
        related_object_pks = []
        for related_object in related_objects:
            if "pk" in related_object:
                related_object_pks.append(related_object["pk"])

        # Update old related objects (set inverse_relation_name fields to null/blank or delete the objects)
        inverse_field = [
            field
            for field in related_model._meta.fields
            if field.name == intermediate_inverse_relation_name
        ][0]

        if inverse_field.null:
            # unset (set null) the inverse relation to all currently related_objects
            # not supposed to be kept (not specified in the request)
            related_model.objects.filter(
                **{intermediate_inverse_relation_name: instance}
            ).exclude(pk__in=related_object_pks).update(
                **{intermediate_inverse_relation_name: None}
            )
        elif inverse_field.blank:
            # unset (set blank) the inverse relation to all currently related_objects
            # not supposed to be kept (not specified in the request)
            related_model.objects.filter(
                **{intermediate_inverse_relation_name: instance}
            ).exclude(pk__in=related_object_pks).update(
                **{intermediate_inverse_relation_name: ""}
            )
        else:
            # delete all currently related_objects
            # not supposed to be kept (not specified in the request)
            related_model.objects.filter(
                **{intermediate_inverse_relation_name: instance}
            ).exclude(pk__in=related_object_pks).delete()

        # Set the new relations (create if not exist yet)
        # TODO: make unittest to prove and explain behaviour!
        related_errors = []
        related_error_found = False
        for related_object in related_objects:
            try:
                related_object[intermediate_inverse_relation_name] = instance

                if "pk" in related_object:
                    existing = related_model.objects.filter(
                        pk=related_object["pk"]
                    ).exists()
                else:
                    existing = related_model.objects.filter(
                        **{
                            intermediate_relation_name: related_object[
                                intermediate_relation_name
                            ],
                            intermediate_inverse_relation_name: related_object[
                                intermediate_inverse_relation_name
                            ],
                        }
                    ).exists()

                if not existing:
                    related_object_instance = related_model.objects.create(
                        **related_object
                    )
                else:
                    try:
                        if "pk" in related_object:
                            related_object_instance = related_model.objects.get(
                                pk=related_object["pk"]
                            )
                        else:
                            related_object_instance = related_model.objects.filter(
                                **{
                                    intermediate_relation_name: related_object[
                                        intermediate_relation_name
                                    ],
                                    intermediate_inverse_relation_name: instance,
                                }
                            ).first()

                        related_serializer.update(
                            instance=related_object_instance,
                            validated_data=related_object,
                        )
                    except related_model.DoesNotExist:
                        related_object.pop("pk")
                        related_serializer.create(validated_data=related_object)

                related_errors.append({})
            except CoreValidationError as e:
                if hasattr(e, "message_dict"):
                    related_errors.append(e.message_dict)
                    related_error_found = True
                else:
                    raise e
            except ValidationError as e:
                if hasattr(e, "detail"):
                    related_errors.append(e.detail)
                    related_error_found = True
                else:
                    raise e
            except Exception as e:
                if hasattr(e, "message_dict"):
                    related_errors.append(e.message_dict)
                    related_error_found = True
                elif hasattr(e, "detail"):
                    related_errors.append(e.detail)
                    related_error_found = True
                else:
                    raise e

        if related_error_found:
            last_err = next(s for s in reversed(related_errors) if s)
            for rel_err in related_errors:
                errors.append(rel_err)
                if rel_err == last_err:
                    break

    def _manage_one_to_one_assignment(
        self,
        instance,
        related_object,
        related_model=None,
        related_serializer=None,
        inverse_relation_name=None,
        errors=None,
    ):
        """
        Update previous relation (set null/blank or delete unwanted, depending on the related model.field definition),
        set the new relation (create if not already exists)
        :param instance:
        :param related_object:
        :param related_model:
        :param related_serializer:
        :param inverse_relation_name:
        :param errors:
        :return:
        """
        if errors is None:
            errors = {}

        # Update old related object (set inverse_relation_name field to null/blank or delete the object)
        inverse_field = [
            field
            for field in related_model._meta.fields
            if field.name == inverse_relation_name
        ][0]

        if inverse_field.null:
            # unset (set null) the inverse relation to the currently related_object
            # not supposed to be kept (not specified in the request)
            if related_object and "pk" in related_object:
                related_model.objects.filter(
                    **{inverse_relation_name: instance}
                ).exclude(pk=related_object["pk"]).update(
                    **{inverse_relation_name: None}
                )
            else:
                related_model.objects.filter(
                    **{inverse_relation_name: instance}
                ).update(**{inverse_relation_name: None})
        elif inverse_field.blank:
            # unset (set blank) the inverse relation to the currently related_object
            # not supposed to be kept (not specified in the request)
            if related_object and "pk" in related_object:
                related_model.objects.filter(
                    **{inverse_relation_name: instance}
                ).exclude(pk=related_object["pk"]).update(**{inverse_relation_name: ""})
            else:
                related_model.objects.filter(
                    **{inverse_relation_name: instance}
                ).update(**{inverse_relation_name: ""})
        else:
            # delete the currently related_object
            # not supposed to be kept (not specified in the request)
            if not related_object or "pk" not in related_object:
                related_model.objects.filter(
                    **{inverse_relation_name: instance}
                ).delete()
            else:
                related_model.objects.filter(
                    **{inverse_relation_name: instance}
                ).exclude(pk=related_object["pk"]).delete()

        # Set the new relation (create if not exists yet)
        # TODO: make unittest to prove and explain behaviour!
        # (if pk is given, but object is gone/belongs to another parent, create a new one)
        if related_object:
            related_object[inverse_relation_name] = instance

            if related_serializer:
                try:
                    if "pk" not in related_object:
                        related_serializer.create(validated_data=related_object)
                    else:
                        try:
                            related_object_instance = related_model.objects.get(
                                pk=related_object["pk"],
                                **{inverse_relation_name: instance}
                            )
                            related_serializer.update(
                                instance=related_object_instance,
                                validated_data=related_object,
                            )
                        except related_model.DoesNotExist:
                            related_object.pop("pk")
                            related_serializer.create(validated_data=related_object)
                except CoreValidationError as e:
                    if hasattr(e, "message_dict"):
                        errors.update(e.message_dict)
                    else:
                        raise e
                except ValidationError as e:
                    if hasattr(e, "detail"):
                        errors.update(e.detail)
                    else:
                        raise e
                except Exception as e:
                    if hasattr(e, "message_dict"):
                        errors.update(e.message_dict)
                    elif hasattr(e, "detail"):
                        errors.update(e.detail)
                    else:
                        raise e

    @staticmethod
    def _get_m2m_fields(through_model, field):
        """
        Get through fields of m2m relation
        """
        m2m = dict()

        # Finding the models which participate in the through table and the direction
        m2m["left"] = {"model": field.related_model.__name__}
        # m2m['right'] = {'model': field.model.__name__}

        # Finding field names for the foreign keys of the through table
        for through_field in through_model._meta.get_fields():
            if through_field.related_model:
                if through_field.related_model != field.related_model:
                    m2m["right"] = {"model": through_field.related_model.__name__}

                if m2m["left"]["model"] == through_field.related_model.__name__:
                    m2m["left"]["field"] = through_field.name
                elif m2m["right"]["model"] == through_field.related_model.__name__:
                    m2m["right"]["field"] = through_field.name

        return m2m

    def process_many_to_one_fields(self, validated_data, many_to_one_fields, errors):
        relation_errors = []
        for relation_name, related_object in many_to_one_fields.items():
            related_model = self.fields[relation_name].Meta.model
            related_serializer = self.fields[relation_name]

            related_instance = self._manage_many_to_one_assignment(
                related_object,
                related_model=related_model,
                related_serializer=related_serializer,
                errors=relation_errors,
            )
            validated_data[relation_name] = related_instance

            if relation_errors:
                errors[relation_name] = relation_errors
                raise ValidationError(errors, code="invalid")

    def process__one_to_many_fields(self, instance, one_to_many_fields, errors):
        relation_errors = []
        for relation_name, related_objects in one_to_many_fields.items():
            related_model = getattr(self.Meta.model, relation_name).rel.related_model
            related_serializer = None
            if hasattr(self.fields[relation_name], "child"):
                related_serializer = self.fields[relation_name].child
            inverse_relation_name = getattr(
                self.Meta.model, relation_name
            ).rel.remote_field.name
            self._manage_one_to_many_assignment(
                instance,
                related_objects,
                related_model=related_model,
                related_serializer=related_serializer,
                relation_name=relation_name,
                inverse_relation_name=inverse_relation_name,
                errors=relation_errors,
            )

            if relation_errors:
                errors[relation_name] = relation_errors

    def process_many_to_many_through_fields(self, instance, many_to_many_through_fields, errors):
        relation_errors = []
        for relation_name, related_objects in many_to_many_through_fields.items():
            model_meta = getattr(self.Meta.model, relation_name)
            related_model = model_meta.rel.related_model
            related_field = model_meta.field
            related_serializer = None
            if hasattr(self.fields[relation_name], "child"):
                related_serializer = self.fields[relation_name].child

            m2m_fields = self._get_m2m_fields(related_model, related_field)
            intermediate_relation_name = m2m_fields["right"]["field"]
            intermediate_inverse_relation_name = m2m_fields["left"]["field"]

            self._manage_many_to_many_assignment(
                instance,
                related_objects,
                related_model=related_model,
                related_serializer=related_serializer,
                intermediate_relation_name=intermediate_relation_name,
                intermediate_inverse_relation_name=intermediate_inverse_relation_name,
                errors=relation_errors,
            )

            if relation_errors:
                errors[relation_name] = relation_errors

    def process_many_to_many_direct_fields(self, instance, many_to_many_direct_fields, errors):
        relation_errors = []

        for relation_name, related_objects in many_to_many_direct_fields.items():
            if hasattr(self.fields[relation_name], "child"):
                model_meta = getattr(self.Meta.model, relation_name)
                related_model = model_meta.rel.model
                related_serializer = self.fields[relation_name].child
                added_objects = []
                assigned_pks = []
                for related_object in related_objects:
                    if 'pk' in related_object:
                        # ToDo: Add meta parameter to select the behavior for non existing pk
                        # Option 1: Raise exception
                        # Option 2: Add as new object
                        related_serializer.update(
                            instance=related_model.objects.get(pk=related_object['pk']),
                            validated_data=related_object
                        )
                        assigned_pks.append(related_object['pk'])
                    else:
                        obj = related_serializer.__class__(data=related_object)
                        obj.is_valid()
                        new_object = obj.save()
                        added_objects.append(new_object)
                        assigned_pks.append(new_object.pk)

                # Add newly created objects to original instance
                getattr(instance, relation_name).add(*added_objects)

                # ToDo: Add meta parameter to select the behavior for removing items
                # Option 1: Remove m2m relation
                # Option 2: Remove m2m relation and related object
                getattr(instance, relation_name).remove(
                    *list(getattr(instance, relation_name).exclude(pk__in=assigned_pks))
                )

        if relation_errors:
            errors[relation_name] = relation_errors

    def process_one_to_one_fields(self, instance, one_to_one_fields, errors):
        for relation_name, related_object in one_to_one_fields.items():
            relation_errors = {}
            related_model = getattr(
                self.Meta.model, relation_name
            ).related.related_model
            related_serializer = self.fields[relation_name]
            inverse_relation_name = getattr(
                self.Meta.model, relation_name
            ).related.remote_field.name
            self._manage_one_to_one_assignment(
                instance,
                related_object,
                related_model=related_model,
                related_serializer=related_serializer,
                inverse_relation_name=inverse_relation_name,
                errors=relation_errors,
            )

            if relation_errors:
                errors[relation_name] = relation_errors

    def extract_relation_data(self, validated_data):
        """
        Extract relation information defined on serializer Meta class
        """
        ralations = {
            'one_to_one_fields': {},
            'one_to_many_fields': {},
            'many_to_one_fields': {},
            'many_to_many_through_fields': {},
            'many_to_many_direct_fields': {},
        }

        if hasattr(self.Meta, "one_to_many_fields"):
            for relation in self.Meta.one_to_many_fields:
                if relation in validated_data:
                    ralations['one_to_many_fields'][relation] = validated_data.pop(relation)

        if hasattr(self.Meta, "many_to_one_fields"):
            for relation in self.Meta.many_to_one_fields:
                if relation in validated_data:
                    ralations['many_to_one_fields'][relation] = validated_data.pop(relation)

        if hasattr(self.Meta, "many_to_many_through_fields"):
            for relation in self.Meta.many_to_many_through_fields:
                if relation in validated_data:
                    ralations['many_to_many_through_fields'][relation] = validated_data.pop(relation)

        if hasattr(self.Meta, "many_to_many_direct_fields"):
            for relation in self.Meta.many_to_many_direct_fields:
                if relation in validated_data:
                    ralations['many_to_many_direct_fields'][relation] = validated_data.pop(relation)

        if hasattr(self.Meta, "one_to_one_fields"):
            for relation in self.Meta.one_to_one_fields:
                if relation in validated_data:
                    ralations['one_to_one_fields'][relation] = validated_data.pop(relation)

        return ralations

    def manage_assignments(self, validated_data, instance=None):
        """
        Remove the related data from validated_data and handle it separately

        :param validated_data:
        :param instance:
        :return:
        """
        errors = {}
        relations = self.extract_relation_data(validated_data)

        # Fields to be processed before the instance
        self.process_many_to_one_fields(validated_data, relations['many_to_one_fields'], errors)

        # Store Instance
        if instance:
            instance = super().update(instance, validated_data)
        else:
            instance = super().create(validated_data)

        # Fields to be processed after the instance
        self.process__one_to_many_fields(instance, relations['one_to_many_fields'], errors)
        self.process_many_to_many_through_fields(instance, relations['many_to_many_through_fields'], errors)
        self.process_many_to_many_direct_fields(instance, relations['many_to_many_direct_fields'], errors)
        self.process_one_to_one_fields(instance, relations['one_to_one_fields'], errors)

        if errors:
            raise ValidationError(errors, code="invalid")
        return instance


class NestedCreateSerializer(BaseNestedSerializer):
    def create(self, validated_data):
        """
        Overwrite default create behaviour of serializers to handle nested relations
        :param validated_data:
        :return:
        """
        return self.manage_assignments(validated_data)


class NestedUpdateSerializer(BaseNestedSerializer):
    def update(self, instance, validated_data):
        """
        Overwrite default update behaviour of serializers to handle nested relations

        :param instance:
        :param validated_data:
        :return:
        """
        return self.manage_assignments(validated_data, instance)


class NestedSerializer(NestedCreateSerializer, NestedUpdateSerializer, serializers.ModelSerializer):
    pass
