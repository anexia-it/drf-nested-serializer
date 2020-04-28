from django.db import models


class Book(models.Model):

    title = models.CharField(
        max_length=50,
        blank=False,
        null=False,
    )


class Chapter(models.Model):

    book = models.ForeignKey(
        "Book",
        on_delete=models.CASCADE,
        related_name="chapters",
        null=False,
    )

    title = models.CharField(
        max_length=100,
        blank=False,
        null=False,
    )

    order = models.IntegerField(
        blank=True,
        null=True,
    )


class Pages(models.Model):
    
    book = models.ForeignKey(
        "Book",
        on_delete=models.CASCADE,
        related_name="pages",
        null=True,
    )

    chapter = models.ForeignKey(
        "Chapter",
        on_delete=models.CASCADE,
        related_name="pages",
        null=True,
    )

    content = models.TextField(
        blank=True,
        null=True,
    )

    order = models.IntegerField(
        blank=True,
        null=True,
    )


class Category(models.Model):

    parent = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        related_name="child_categories",
        null=True,
    )

    books = models.ManyToManyField(
        "Book",
        related_name="categories",
    )


class Author(models.Model):
    
    name = models.CharField(
        max_length=100,
        blank=False,
        null=False,
    )

    books = models.ManyToManyField(
        "Book",
        related_name="authors",
        through="AuthorBook"
    )


class AuthorBook(models.Model):

    author = models.ForeignKey(
        "Author",
        on_delete=models.CASCADE,
        related_name="author_books",
        null=False,
    )

    book = models.ForeignKey(
        "Book",
        on_delete=models.CASCADE,
        related_name="author_books",
        null=False,
    )
