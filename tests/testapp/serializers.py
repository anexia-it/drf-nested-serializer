from rest_framework import serializers

from django_rest_nested_serializer import NestedSerializer
from .models import Book, Author, Chapter, Page, AuthorBook, Category


class ChapterPageSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(read_only=False, required=False, allow_null=True)

    class Meta:
        model = Page
        fields = ['pk', 'url', 'content', 'order']


class BookChapterSerializer(NestedSerializer):
    pk = serializers.IntegerField(read_only=False, required=False, allow_null=True)
    pages = ChapterPageSerializer(many=True, required=False)

    class Meta:
        model = Chapter
        fields = ['pk', 'url', 'title', 'order', 'pages']
        one_to_many_fields = ['pages']


class BookPageSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(read_only=False, required=False, allow_null=True)

    class Meta:
        model = Page
        fields = ['pk', 'url', 'content', 'chapter', 'order']


class BookCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['pk', 'url', 'parent']


class BookSerializer(NestedSerializer):
    chapters = BookChapterSerializer(many=True, required=False)
    pages = BookPageSerializer(many=True, required=False)
    categories = BookCategorySerializer(many=True, required=False)

    class Meta:
        model = Book
        fields = ['pk', 'url', 'title', 'chapters', 'categories', 'pages']
        one_to_many_fields = ['chapters', 'pages']
        many_to_many_direct_fields = ['categories']


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['pk', 'url', 'name', 'books']


class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['pk', 'url', 'title', 'book', 'order']


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['pk', 'url', 'content', 'book', 'chapter', 'order']


class AuthorBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorBook
        fields = ['pk', 'url', 'author', 'book']


class CategorySerializer(NestedSerializer):
    pk = serializers.IntegerField(read_only=False, required=False, allow_null=True)

    class Meta:
        model = Category
        fields = ['pk', 'url', 'name', 'child_categories', 'books']
        one_to_many_fields = ['child_categories']

CategorySerializer._declared_fields['child_categories'] = CategorySerializer(many=True)
