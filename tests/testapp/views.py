from rest_framework import viewsets, permissions

from .models import Book, Author, Chapter, Page, AuthorBook, Category
from .serializers import BookSerializer, AuthorSerializer, ChapterSerializer, PageSerializer, AuthorBookSerializer, \
    CategorySerializer


class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]


class BookViewSet(BaseViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class AuthorViewSet(BaseViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class ChapterViewSet(BaseViewSet):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer


class PageViewSet(BaseViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer


class AuthorBookViewSet(BaseViewSet):
    queryset = AuthorBook.objects.all()
    serializer_class = AuthorBookSerializer


class CategoryViewSet(BaseViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
