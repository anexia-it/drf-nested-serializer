from django.contrib import admin

from .models import Book, Author, Chapter, Pages, AuthorBook, Category

admin.site.register(Book)
admin.site.register(Author)
admin.site.register(Chapter)
admin.site.register(Pages)
admin.site.register(AuthorBook)
admin.site.register(Category)
