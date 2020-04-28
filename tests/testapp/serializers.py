from rest_framework import serializers

from .models import Book, Author, Chapter, Pages, AuthorBook, Category


class BookSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Book
        fields = ['url', 'title']


class AuthorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Author
        fields = ['url', 'name', 'books']


class ChapterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Chapter
        fields = ['url', 'title', 'book', 'order']


class PagesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Pages
        fields = ['url', 'content', 'book', 'chapter', 'order']


class AuthorBookSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AuthorBook
        fields = ['url', 'author', 'book']


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ['url', 'parent', 'books']
