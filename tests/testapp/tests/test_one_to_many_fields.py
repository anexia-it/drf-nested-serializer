import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from testapp.models import Book, Chapter, Page, Category, Author, AuthorBook


class OneToManyFieldsTests(APITestCase):

    def test_adding_book_with_chapters(self):
        """
        Tests that a nested serializer can add objects referred by a foreign key. One level nesting.
        """
        url = reverse('book-list')
        data = {
            'title': 'Book 1',
            'chapters': [
                {'title': 'Chapter 3', 'order': 3},
                {'title': 'Chapter 1', 'order': 1},
                {'title': 'Chapter 2', 'order': 2},
            ],
            'pages': [],
        }
        response = self.client.post(url, data, format='json')

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['chapters']), len(data['chapters']))
        self.assertEqual(len(response.data['pages']), len(data['pages']))
        self.assertEqual(len(response.data['categories']), 0)

        # Check that all chapters where added
        for request_chapter in data['chapters']:
            chapter_exists = False
            for response_chapter in response.data['chapters']:
                if request_chapter['title'] == response_chapter['title'] \
                        and request_chapter['order'] == response_chapter['order']:
                    chapter_exists = True
            self.assertTrue(chapter_exists)

        # Assert data
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(Chapter.objects.count(), 3)
        self.assertEqual(Page.objects.count(), 0)
        self.assertEqual(Category.objects.count(), 0)
        self.assertEqual(Author.objects.count(), 0)
        self.assertEqual(AuthorBook.objects.count(), 0)

        # Check that all chapters where added
        book_object = Book.objects.get(title=data['title'])
        for chapter in data['chapters']:
            self.assertEqual(
                Chapter.objects.filter(title=chapter['title'], order=chapter['order'], book=book_object).count(), 1
            )

    def test_update_book_with_chapters(self):
        """
        Tests that a nested serializer can update objects referred by a foreign key. One level nesting.

        Object without a primary key will be added, object with primary key will be updated and object that exists in
        the database where the primary key was not sent will be removed.
        """
        url = reverse('book-list')
        data = {
            'title': 'Book 1',
            'chapters': [
                {'title': 'Chapter 3', 'order': 3},
                {'title': 'Chapter 1', 'order': 1},
                {'title': 'Chapter 2', 'order': 2},
            ],
            'pages': [],
        }
        response = self.client.post(url, data, format='json')

        # Prepare object for update
        data = json.loads(response.content.decode('utf-8'))
        data['title'] = 'Book 1 update'
        chapter_1_pk = None
        chapter_3_pk = None
        chapter_3_index = None
        for index, chapter in enumerate(data['chapters']):
            # Remove pk of `Chapter 1` to delete the initial object and create a new one
            if chapter['title'] == 'Chapter 1':
                chapter_1_pk = chapter['pk']
                chapter['title'] = 'Chapter 1 new'
                del chapter['pk']

            # Update title only
            if chapter['title'] == 'Chapter 2':
                chapter['title'] = 'Chapter 2 update'

            # Store the index for removal
            if chapter['title'] == 'Chapter 3':
                chapter_3_pk = chapter['pk']
                chapter_3_index = index

        self.assertIsNotNone(chapter_1_pk)
        self.assertIsNotNone(chapter_3_pk)
        self.assertIsNotNone(chapter_3_index)

        # Remove chapter 3, will case deletion form database
        del data['chapters'][chapter_3_index]

        # Send update request
        url = reverse('book-detail', kwargs={'pk': data['pk']})
        response = self.client.put(url, data, format='json')

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['chapters']), len(data['chapters']))
        self.assertEqual(len(response.data['pages']), len(data['pages']))
        self.assertEqual(len(response.data['categories']), 0)

        # Check that all chapters where added
        for request_chapter in data['chapters']:
            chapter_exists = False
            for response_chapter in response.data['chapters']:
                if request_chapter['title'] == response_chapter['title'] \
                        and request_chapter['order'] == response_chapter['order']:
                    chapter_exists = True
                    if 'pk' in request_chapter:
                        self.assertEqual(request_chapter['pk'], response_chapter['pk'])
            self.assertTrue(chapter_exists)

        # Assert data
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(Chapter.objects.count(), 2)
        self.assertEqual(Page.objects.count(), 0)
        self.assertEqual(Category.objects.count(), 0)
        self.assertEqual(Author.objects.count(), 0)
        self.assertEqual(AuthorBook.objects.count(), 0)

        # Check that all chapters where added
        book_object = Book.objects.get(title=data['title'])
        for chapter in data['chapters']:
            self.assertEqual(
                Chapter.objects.filter(title=chapter['title'], order=chapter['order'], book=book_object).count(), 1
            )

        # Assert chapter 1 and chapter 3 where deleted
        self.assertFalse(Chapter.objects.filter(pk=chapter_1_pk).exists())
        self.assertFalse(Chapter.objects.filter(pk=chapter_3_pk).exists())

    def test_adding_book_with_chapters_with_pages(self):
        """
        Tests that a nested serializer can add objects referred by a foreign key. Two level nesting.
        """
        url = reverse('book-list')
        data = {
            'title': 'Book 1',
            'chapters': [
                {
                    'title': 'Chapter 3',
                    'order': 3,
                    'pages': [
                        {'content': 'Chapter 3, page 1', 'order': 1},
                        {'content': 'Chapter 3, page 2', 'order': 2},
                    ],
                },
                {
                    'title': 'Chapter 1',
                    'order': 1,
                    'pages': [],
                },
                {
                    'title': 'Chapter 2',
                    'order': 2,
                    'pages': [
                        {'content': 'Chapter 2, page 1', 'order': 1},
                        {'content': 'Chapter 2, page 3', 'order': 3},
                        {'content': 'Chapter 2, page 2', 'order': 2},
                    ],
                },
            ],
            'pages': [],
        }
        response = self.client.post(url, data, format='json')

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['chapters']), len(data['chapters']))
        self.assertEqual(len(response.data['pages']), len(data['pages']))
        self.assertEqual(len(response.data['categories']), 0)

        # Check that all chapters where added
        for request_chapter in data['chapters']:
            chapter_exists = False
            for response_chapter in response.data['chapters']:
                if request_chapter['title'] == response_chapter['title'] \
                        and request_chapter['order'] == response_chapter['order']:
                    chapter_exists = True
                    self.assertEqual(len(request_chapter['pages']), len(response_chapter['pages']))

                    # Check that all chapter pages where added
                    for request_chapter_page in request_chapter['pages']:
                        chapter_page_exists = False
                        for response_chapter_page in response_chapter['pages']:
                            if request_chapter_page['content'] == response_chapter_page['content'] \
                                    and request_chapter_page['order'] == response_chapter_page['order']:
                                chapter_page_exists = True
                        self.assertTrue(chapter_page_exists)
            self.assertTrue(chapter_exists)

        # Assert data
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(Chapter.objects.count(), 3)
        self.assertEqual(Page.objects.count(), 5)
        self.assertEqual(Category.objects.count(), 0)
        self.assertEqual(Author.objects.count(), 0)
        self.assertEqual(AuthorBook.objects.count(), 0)

        # Check that all chapters where added
        book_object = Book.objects.get(title=data['title'])
        for chapter in data['chapters']:
            chapter_object = Chapter.objects.get(title=chapter['title'], order=chapter['order'], book=book_object)

            # Check that all chapter pages where added
            for chapter_page in chapter['pages']:
                self.assertEqual(
                    Page.objects.filter(
                        content=chapter_page['content'],
                        order=chapter_page['order'],
                        chapter=chapter_object,
                    ).count(),
                    1
                )

    def test_update_book_with_chapters_with_pages(self):
        """
        Tests that a nested serializer can add objects referred by a foreign key. Two level nesting.

        Object without a primary key will be added, object with primary key will be updated and object that exists in
        the database where the primary key was not sent will be removed.
        """
        url = reverse('book-list')
        data = {
            'title': 'Book 1',
            'chapters': [
                {
                    'title': 'Chapter 3',
                    'order': 3,
                    'pages': [
                        {'content': 'Chapter 3, page 1', 'order': 1},
                        {'content': 'Chapter 3, page 2', 'order': 2},
                    ],
                },
                {
                    'title': 'Chapter 1',
                    'order': 1,
                    'pages': [],
                },
                {
                    'title': 'Chapter 2',
                    'order': 2,
                    'pages': [
                        {'content': 'Chapter 2, page 1', 'order': 1},
                        {'content': 'Chapter 2, page 3', 'order': 3},
                        {'content': 'Chapter 2, page 2', 'order': 2},
                    ],
                },
            ],
            'pages': [],
        }
        response = self.client.post(url, data, format='json')

        # Prepare object for update
        data = json.loads(response.content.decode('utf-8'))
        data['title'] = 'Book 1 update'
        chapter_1_pk = None
        chapter_3_pk = None
        chapter_3_index = None
        chapter_2_page_1_pk = None
        chapter_2_page_3_pk = None
        chapter_2_page_3_index = None
        for index, chapter in enumerate(data['chapters']):
            # Remove pk of `Chapter 1` to delete the initial object and create a new one
            if chapter['title'] == 'Chapter 1':
                chapter_1_pk = chapter['pk']
                chapter['title'] = 'Chapter 1 new'
                chapter['pages'] = [
                    {'content': 'Chapter 1, page 1', 'order': 1},
                ]
                del chapter['pk']

            # Update title and pages
            if chapter['title'] == 'Chapter 2':
                chapter['title'] = 'Chapter 2 update'

                for page_index, page in enumerate(chapter['pages']):
                    # Remove pk of `Chapter 2, page 1` to delete the initial object and create a new one
                    if page['content'] == 'Chapter 2, page 1':
                        chapter_2_page_1_pk = page['pk']
                        page['content'] = 'Chapter 2, page 1 new'
                        del page['pk']

                    # Update content only
                    if page['content'] == 'Chapter 2, page 2 update':
                        pass

                    # Store the index for removal
                    if page['content'] == 'Chapter 2, page 3':
                        chapter_2_page_3_pk = page['pk']
                        chapter_2_page_3_index = page_index

                self.assertIsNotNone(chapter_2_page_1_pk)
                self.assertIsNotNone(chapter_2_page_3_pk)
                self.assertIsNotNone(chapter_2_page_3_index)

                # Remove chapter 2, page 3, will case deletion form database
                del chapter['pages'][chapter_2_page_3_index]

            # Store the index for removal
            if chapter['title'] == 'Chapter 3':
                chapter_3_pk = chapter['pk']
                chapter_3_index = index

        self.assertIsNotNone(chapter_1_pk)
        self.assertIsNotNone(chapter_3_pk)
        self.assertIsNotNone(chapter_3_index)

        # Remove chapter 3, will case deletion form database
        del data['chapters'][chapter_3_index]

        # Send update request
        url = reverse('book-detail', kwargs={'pk': data['pk']})
        response = self.client.put(url, data, format='json')

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['chapters']), len(data['chapters']))
        self.assertEqual(len(response.data['pages']), len(data['pages']))
        self.assertEqual(len(response.data['categories']), 0)

        # Check that all chapters where added
        for request_chapter in data['chapters']:
            chapter_exists = False
            for response_chapter in response.data['chapters']:
                if request_chapter['title'] == response_chapter['title'] \
                        and request_chapter['order'] == response_chapter['order']:
                    chapter_exists = True
                    self.assertEqual(len(request_chapter['pages']), len(response_chapter['pages']))

                    if 'pk' in request_chapter:
                        self.assertEqual(request_chapter['pk'], response_chapter['pk'])

                    # Check that all chapter pages where added
                    for request_chapter_page in request_chapter['pages']:
                        chapter_page_exists = False
                        for response_chapter_page in response_chapter['pages']:
                            if request_chapter_page['content'] == response_chapter_page['content'] \
                                    and request_chapter_page['order'] == response_chapter_page['order']:
                                chapter_page_exists = True

                                if 'pk' in request_chapter_page:
                                    self.assertEqual(request_chapter_page['pk'], response_chapter_page['pk'])

                        self.assertTrue(chapter_page_exists)
            self.assertTrue(chapter_exists)

        # Assert data
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(Chapter.objects.count(), 2)
        self.assertEqual(Page.objects.count(), 5)
        self.assertEqual(Page.objects.exclude(chapter=None, book=None).count(), 3)
        self.assertEqual(Category.objects.count(), 0)
        self.assertEqual(Author.objects.count(), 0)
        self.assertEqual(AuthorBook.objects.count(), 0)

        # Check that all chapters where added
        book_object = Book.objects.get(title=data['title'])
        for chapter in data['chapters']:
            chapter_object = Chapter.objects.get(title=chapter['title'], order=chapter['order'], book=book_object)

            # Check that all chapter pages where added
            for chapter_page in chapter['pages']:
                self.assertEqual(
                    Page.objects.filter(
                        content=chapter_page['content'],
                        order=chapter_page['order'],
                        chapter=chapter_object,
                    ).count(),
                    1
                )

        # Assert deletions
        self.assertFalse(Chapter.objects.filter(pk=chapter_1_pk).exists())
        self.assertFalse(Chapter.objects.filter(pk=chapter_3_pk).exists())

        # Second level objects where only unassigned from chapter
        # ToDo: check if this behavior can be controlled. This is caused because of multiple foreign keys
        self.assertFalse(Page.objects.filter(pk=chapter_2_page_1_pk).exclude(chapter=None).exists())
        self.assertFalse(Page.objects.filter(pk=chapter_2_page_3_pk).exclude(chapter=None).exists())
        self.assertTrue(Page.objects.filter(pk=chapter_2_page_1_pk).exists())
        self.assertTrue(Page.objects.filter(pk=chapter_2_page_3_pk).exists())

    def test_adding_book_with_pages_and_chapter_with_pages(self):
        """
        Tests that a nested serializer can add objects referred by a foreign key. Two level and one level nesting.
        """
        url = reverse('book-list')
        data = {
            'title': 'Book 1',
            'chapters': [
                {
                    'title': 'Chapter 3',
                    'order': 3,
                    'pages': [
                        {'content': 'Chapter 3, page 1', 'order': 1},
                        {'content': 'Chapter 3, page 2', 'order': 2},
                    ],
                },
                {
                    'title': 'Chapter 1',
                    'order': 1,
                    'pages': [],
                },
                {
                    'title': 'Chapter 2',
                    'order': 2,
                    'pages': [
                        {'content': 'Chapter 2, page 1', 'order': 1},
                        {'content': 'Chapter 2, page 3', 'order': 3},
                        {'content': 'Chapter 2, page 2', 'order': 2},
                    ],
                },
            ],
            'pages': [
                {'content': 'Book 1, page 1', 'order': 1},
                {'content': 'Book 1, page 3', 'order': 3},
                {'content': 'Book 1, page 2', 'order': 2},
            ]
        }
        response = self.client.post(url, data, format='json')

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['chapters']), len(data['chapters']))
        self.assertEqual(len(response.data['pages']), len(data['pages']))
        self.assertEqual(len(response.data['categories']), 0)

        # Check that all chapters where added
        for request_chapter in data['chapters']:
            chapter_exists = False
            for response_chapter in response.data['chapters']:
                if request_chapter['title'] == response_chapter['title'] \
                        and request_chapter['order'] == response_chapter['order']:
                    chapter_exists = True
                    self.assertEqual(len(request_chapter['pages']), len(response_chapter['pages']))

                    # Check that all chapter pages where added
                    for request_chapter_page in request_chapter['pages']:
                        chapter_page_exists = False
                        for response_chapter_page in response_chapter['pages']:
                            if request_chapter_page['content'] == response_chapter_page['content'] \
                                    and request_chapter_page['order'] == response_chapter_page['order']:
                                chapter_page_exists = True
                        self.assertTrue(chapter_page_exists)
            self.assertTrue(chapter_exists)

        # Assert data
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(Chapter.objects.count(), 3)
        self.assertEqual(Page.objects.count(), 8)
        self.assertEqual(Category.objects.count(), 0)
        self.assertEqual(Author.objects.count(), 0)
        self.assertEqual(AuthorBook.objects.count(), 0)

        # Check that all chapters where added
        book_object = Book.objects.get(title=data['title'])
        for chapter in data['chapters']:
            chapter_object = Chapter.objects.get(title=chapter['title'], order=chapter['order'], book=book_object)

            # Check that all chapter pages where added
            for chapter_page in chapter['pages']:
                self.assertEqual(
                    Page.objects.filter(
                        content=chapter_page['content'],
                        order=chapter_page['order'],
                        chapter=chapter_object,
                        book=None
                    ).count(),
                    1
                )

        # Check that pages where added
        for page in data['pages']:
            self.assertEqual(
                Page.objects.filter(
                    content=page['content'],
                    order=page['order'],
                    chapter=None,
                    book=book_object
                ).count(),
                1
            )

    def test_updating_book_with_pages_and_chapter_with_pages(self):
        """
        Tests that a nested serializer can update objects referred by a foreign key. Two level and one level nesting.

        Object without a primary key will be added, object with primary key will be updated and object that exists in
        the database where the primary key was not sent will be removed.
        """
        url = reverse('book-list')
        data = {
            'title': 'Book 1',
            'chapters': [
                {
                    'title': 'Chapter 3',
                    'order': 3,
                    'pages': [
                        {'content': 'Chapter 3, page 1', 'order': 1},
                        {'content': 'Chapter 3, page 2', 'order': 2},
                    ],
                },
                {
                    'title': 'Chapter 1',
                    'order': 1,
                    'pages': [],
                },
                {
                    'title': 'Chapter 2',
                    'order': 2,
                    'pages': [
                        {'content': 'Chapter 2, page 1', 'order': 1},
                        {'content': 'Chapter 2, page 3', 'order': 3},
                        {'content': 'Chapter 2, page 2', 'order': 2},
                    ],
                },
            ],
            'pages': [
                {'content': 'Book 1, page 1', 'order': 1},
                {'content': 'Book 1, page 3', 'order': 3},
                {'content': 'Book 1, page 2', 'order': 2},
            ]
        }
        response = self.client.post(url, data, format='json')

        # Prepare object for update
        data = json.loads(response.content.decode('utf-8'))
        data['title'] = 'Book 1 update'
        chapter_1_pk = None
        chapter_3_pk = None
        chapter_3_index = None
        chapter_2_page_1_pk = None
        chapter_2_page_3_pk = None
        chapter_2_page_3_index = None
        page_1_pk = None
        page_3_pk = None
        page_3_index = None
        for index, chapter in enumerate(data['chapters']):
            # Remove pk of `Chapter 1` to delete the initial object and create a new one
            if chapter['title'] == 'Chapter 1':
                chapter_1_pk = chapter['pk']
                chapter['title'] = 'Chapter 1 new'
                chapter['pages'] = [
                    {'content': 'Chapter 1, page 1', 'order': 1},
                ]
                del chapter['pk']

            # Update title and pages
            if chapter['title'] == 'Chapter 2':
                chapter['title'] = 'Chapter 2 update'

                for page_index, page in enumerate(chapter['pages']):
                    # Remove pk of `Chapter 2, page 1` to delete the initial object and create a new one
                    if page['content'] == 'Chapter 2, page 1':
                        chapter_2_page_1_pk = page['pk']
                        page['content'] = 'Chapter 2, page 1 new'
                        del page['pk']

                    # Update content only
                    if page['content'] == 'Chapter 2, page 2 update':
                        pass

                    # Store the index for removal
                    if page['content'] == 'Chapter 2, page 3':
                        chapter_2_page_3_pk = page['pk']
                        chapter_2_page_3_index = page_index

                self.assertIsNotNone(chapter_2_page_1_pk)
                self.assertIsNotNone(chapter_2_page_3_pk)
                self.assertIsNotNone(chapter_2_page_3_index)

                # Remove chapter 2, page 3, will case deletion form database
                del chapter['pages'][chapter_2_page_3_index]

            # Store the index for removal
            if chapter['title'] == 'Chapter 3':
                chapter_3_pk = chapter['pk']
                chapter_3_index = index

        for index, page in enumerate(data['pages']):
            # Remove pk of `Chapter 1` to delete the initial object and create a new one
            if page['content'] == 'Book 1, page 1':
                page_1_pk = page['pk']
                page['content'] = 'Book 1, page 1 new'
                del page['pk']

            # Update content only
            if page['content'] == 'Book 1, page 2':
                page['content'] = 'Book 1, page 2 update'

            # Store the index for removal
            if page['content'] == 'Book 1, page 3':
                page_3_pk = page['pk']
                page_3_index = index

        self.assertIsNotNone(chapter_1_pk)
        self.assertIsNotNone(chapter_3_pk)
        self.assertIsNotNone(chapter_3_index)
        self.assertIsNotNone(page_1_pk)
        self.assertIsNotNone(page_3_pk)
        self.assertIsNotNone(page_3_index)

        # Remove chapter 3, will case deletion form database
        del data['chapters'][chapter_3_index]
        del data['pages'][page_3_index]

        # Send update request
        url = reverse('book-detail', kwargs={'pk': data['pk']})
        response = self.client.put(url, data, format='json')

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['chapters']), len(data['chapters']))
        self.assertEqual(len(response.data['pages']), len(data['pages']))
        self.assertEqual(len(response.data['categories']), 0)

        # Check that all chapters where added
        for request_chapter in data['chapters']:
            chapter_exists = False
            for response_chapter in response.data['chapters']:
                if request_chapter['title'] == response_chapter['title'] \
                        and request_chapter['order'] == response_chapter['order']:
                    chapter_exists = True
                    self.assertEqual(len(request_chapter['pages']), len(response_chapter['pages']))

                    if 'pk' in request_chapter:
                        self.assertEqual(request_chapter['pk'], response_chapter['pk'])

                    # Check that all chapter pages where added
                    for request_chapter_page in request_chapter['pages']:
                        chapter_page_exists = False
                        for response_chapter_page in response_chapter['pages']:
                            if request_chapter_page['content'] == response_chapter_page['content'] \
                                    and request_chapter_page['order'] == response_chapter_page['order']:
                                chapter_page_exists = True

                                if 'pk' in request_chapter_page:
                                    self.assertEqual(request_chapter_page['pk'], response_chapter_page['pk'])

                        self.assertTrue(chapter_page_exists)
            self.assertTrue(chapter_exists)

        # Assert data
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(Chapter.objects.count(), 2)
        self.assertEqual(Page.objects.count(), 9)
        self.assertEqual(Page.objects.exclude(book=None, chapter=None).count(), 5)
        self.assertEqual(Category.objects.count(), 0)
        self.assertEqual(Author.objects.count(), 0)
        self.assertEqual(AuthorBook.objects.count(), 0)

        # Check that all chapters where added
        book_object = Book.objects.get(title=data['title'])
        for chapter in data['chapters']:
            chapter_object = Chapter.objects.get(title=chapter['title'], order=chapter['order'], book=book_object)

            # Check that all chapter pages where added
            for chapter_page in chapter['pages']:
                self.assertEqual(
                    Page.objects.filter(
                        content=chapter_page['content'],
                        order=chapter_page['order'],
                        chapter=chapter_object,
                        book=None
                    ).count(),
                    1
                )

        # Check that pages where added
        for page in data['pages']:
            self.assertEqual(
                Page.objects.filter(
                    content=page['content'],
                    order=page['order'],
                    chapter=None,
                    book=book_object
                ).count(),
                1
            )

        # Assert deletions
        self.assertFalse(Chapter.objects.filter(pk=chapter_1_pk).exists())
        self.assertFalse(Chapter.objects.filter(pk=chapter_3_pk).exists())

        # Second level objects where only unassigned from chapter
        # ToDo: check if this behavior can be controlled. This is caused because of multiple foreign keys
        self.assertFalse(Page.objects.filter(pk=chapter_2_page_1_pk).exclude(chapter=None).exists())
        self.assertFalse(Page.objects.filter(pk=chapter_2_page_3_pk).exclude(chapter=None).exists())
        self.assertFalse(Page.objects.filter(pk=page_1_pk).exclude(book=None).exists())
        self.assertFalse(Page.objects.filter(pk=page_3_pk).exclude(book=None).exists())
        self.assertTrue(Page.objects.filter(pk=chapter_2_page_1_pk).exists())
        self.assertTrue(Page.objects.filter(pk=chapter_2_page_3_pk).exists())
        self.assertTrue(Page.objects.filter(pk=page_1_pk).exists())
        self.assertTrue(Page.objects.filter(pk=page_3_pk).exists())

    def test_adding_categories_with_single_children(self):
        """
        Tests that a nested serializer can add objects referred by a foreign key with self reference.
        Multiple level nesting.
        """
        url = reverse('category-list')
        data = {
            "name": "Category 1",
            "children": [
                {
                    "name": "Category 2",
                    "children": [
                        {
                            "name": "Category 3",
                            "children": [],
                        }
                    ],
                }
            ]
        }
        response = self.client.post(url, data, format='json')

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Category 1')
        self.assertEqual(response.data['children'][0]['name'], 'Category 2')
        self.assertEqual(response.data['children'][0]['children'][0]['name'], 'Category 3')

        # Assert data
        self.assertEqual(Category.objects.count(), 3)
        self.assertTrue(Category.objects.filter(name='Category 1', parent=None).exists())
        self.assertTrue(
            Category.objects.filter(name='Category 2', parent=Category.objects.get(name='Category 1')).exists()
        )
        self.assertTrue(
            Category.objects.filter(name='Category 3', parent=Category.objects.get(name='Category 2')).exists()
        )

    def test_update_categories_with_single_children(self):
        """
        Tests that a nested serializer can update objects referred by a foreign key with self reference.
        Multiple level nesting. This tests tries only to send the same object again, so nothing should change.
        """
        url = reverse('category-list')
        data = {
            "name": "Category 1",
            "children": [
                {
                    "name": "Category 2",
                    "children": [
                        {
                            "name": "Category 3",
                            "children": [],
                        }
                    ],
                }
            ]
        }
        response = self.client.post(url, data, format='json')

        data = json.loads(response.content.decode('utf-8'))

        # Send update request
        url = reverse('category-detail', kwargs={'pk': data['pk']})
        response = self.client.put(url, data, format='json')

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Category 1')
        self.assertEqual(response.data['children'][0]['name'], 'Category 2')
        self.assertEqual(response.data['children'][0]['children'][0]['name'], 'Category 3')

        # Assert data
        self.assertEqual(Category.objects.count(), 3)
        self.assertTrue(Category.objects.filter(name='Category 1', parent=None).exists())
        self.assertTrue(
            Category.objects.filter(name='Category 2', parent=Category.objects.get(name='Category 1')).exists()
        )
        self.assertTrue(
            Category.objects.filter(name='Category 3', parent=Category.objects.get(name='Category 2')).exists()
        )

    def test_adding_categories_with_multiple_children(self):
        """
        Tests that a nested serializer can add objects referred by a foreign key with self reference.
        Multiple level nesting.
        """
        url = reverse('category-list')
        data = {
            "name": "Category 1",
            "children": [
                {
                    "name": "Category 11",
                    "children": [
                        {
                            "name": "Category 111",
                            "children": [],
                        }
                    ],
                },
                {
                    "name": "Category 12",
                    "children": [
                        {
                            "name": "Category 121",
                            "children": [
                                {
                                    "name": "Category 1211",
                                    "children": [],
                                },
                                {
                                    "name": "Category 1212",
                                    "children": [],
                                }
                            ],
                        }
                    ],
                },
                {
                    "name": "Category 13",
                    "children": [],
                }
            ]
        }
        response = self.client.post(url, data, format='json')

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Category 1')
        self.assertEqual(response.data['children'][0]['name'], 'Category 11')
        self.assertEqual(response.data['children'][1]['name'], 'Category 12')
        self.assertEqual(response.data['children'][2]['name'], 'Category 13')
        self.assertEqual(response.data['children'][0]['children'][0]['name'], 'Category 111')
        self.assertEqual(response.data['children'][1]['children'][0]['name'], 'Category 121')
        self.assertEqual(
            response.data['children'][1]['children'][0]['children'][0]['name'], 'Category 1211'
        )
        self.assertEqual(
            response.data['children'][1]['children'][0]['children'][1]['name'], 'Category 1212'
        )

        # Assert data
        self.assertEqual(Category.objects.count(), 8)
        self.assertTrue(Category.objects.filter(name='Category 1', parent=None).exists())
        self.assertTrue(
            Category.objects.filter(name='Category 11', parent=Category.objects.get(name='Category 1')).exists()
        )
        self.assertTrue(
            Category.objects.filter(name='Category 12', parent=Category.objects.get(name='Category 1')).exists()
        )
        self.assertTrue(
            Category.objects.filter(name='Category 13', parent=Category.objects.get(name='Category 1')).exists()
        )
        self.assertTrue(
            Category.objects.filter(name='Category 111', parent=Category.objects.get(name='Category 11')).exists()
        )
        self.assertTrue(
            Category.objects.filter(name='Category 121', parent=Category.objects.get(name='Category 12')).exists()
        )
        self.assertTrue(
            Category.objects.filter(name='Category 1211', parent=Category.objects.get(name='Category 121')).exists()
        )
        self.assertTrue(
            Category.objects.filter(name='Category 1212', parent=Category.objects.get(name='Category 121')).exists()
        )

    def test_update_categories_with_multiple_children(self):
        """
        Tests that a nested serializer can add objects referred by a foreign key with self reference.
        Multiple level nesting. This tests tries only to send the same object again, so nothing should change.
        """
        url = reverse('category-list')
        data = {
            "name": "Category 1",
            "children": [
                {
                    "name": "Category 11",
                    "children": [
                        {
                            "name": "Category 111",
                            "children": [],
                        }
                    ],
                },
                {
                    "name": "Category 12",
                    "children": [
                        {
                            "name": "Category 121",
                            "children": [
                                {
                                    "name": "Category 1211",
                                    "children": [],
                                },
                                {
                                    "name": "Category 1212",
                                    "children": [],
                                }
                            ],
                        }
                    ],
                },
                {
                    "name": "Category 13",
                    "children": [],
                }
            ]
        }
        response = self.client.post(url, data, format='json')

        data = json.loads(response.content.decode('utf-8'))

        # Send update request
        url = reverse('category-detail', kwargs={'pk': data['pk']})
        response = self.client.put(url, data, format='json')

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Category 1')
        self.assertEqual(response.data['children'][0]['name'], 'Category 11')
        self.assertEqual(response.data['children'][1]['name'], 'Category 12')
        self.assertEqual(response.data['children'][2]['name'], 'Category 13')
        self.assertEqual(response.data['children'][0]['children'][0]['name'], 'Category 111')
        self.assertEqual(response.data['children'][1]['children'][0]['name'], 'Category 121')
        self.assertEqual(
            response.data['children'][1]['children'][0]['children'][0]['name'], 'Category 1211'
        )
        self.assertEqual(
            response.data['children'][1]['children'][0]['children'][1]['name'], 'Category 1212'
        )

        # Assert data
        self.assertEqual(Category.objects.count(), 8)
        self.assertTrue(Category.objects.filter(name='Category 1', parent=None).exists())
        self.assertTrue(
            Category.objects.filter(name='Category 11', parent=Category.objects.get(name='Category 1')).exists()
        )
        self.assertTrue(
            Category.objects.filter(name='Category 12', parent=Category.objects.get(name='Category 1')).exists()
        )
        self.assertTrue(
            Category.objects.filter(name='Category 13', parent=Category.objects.get(name='Category 1')).exists()
        )
        self.assertTrue(
            Category.objects.filter(name='Category 111', parent=Category.objects.get(name='Category 11')).exists()
        )
        self.assertTrue(
            Category.objects.filter(name='Category 121', parent=Category.objects.get(name='Category 12')).exists()
        )
        self.assertTrue(
            Category.objects.filter(name='Category 1211', parent=Category.objects.get(name='Category 121')).exists()
        )
        self.assertTrue(
            Category.objects.filter(name='Category 1212', parent=Category.objects.get(name='Category 121')).exists()
        )