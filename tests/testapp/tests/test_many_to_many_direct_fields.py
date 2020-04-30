import json
import unittest

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from testapp.models import Book, Chapter, Page, Category, Author, AuthorBook


class ManyToManyDirectFieldsTests(APITestCase):

    def test_adding_books_with_categories_with_multiple_children(self):
        """
        Tests that a nested serializer can add objects referred by a foreign key. One level nesting.
        """
        url = reverse('book-list')
        data = {
            'title': 'Book 1',
            'categories': [
                {
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
            ]
        }
        response = self.client.post(url, data, format='json')

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Book 1')
        self.assertEqual(response.data['categories'][0]['name'], 'Category 1')
        self.assertEqual(response.data['categories'][0]['children'][0]['name'], 'Category 11')
        self.assertEqual(response.data['categories'][0]['children'][1]['name'], 'Category 12')
        self.assertEqual(response.data['categories'][0]['children'][2]['name'], 'Category 13')
        self.assertEqual(
            response.data['categories'][0]['children'][0]['children'][0]['name'], 'Category 111'
        )
        self.assertEqual(
            response.data['categories'][0]['children'][1]['children'][0]['name'], 'Category 121'
        )
        self.assertEqual(
            response.data['categories'][0]['children'][1]['children'][0]['children'][0]['name'],
            'Category 1211'
        )
        self.assertEqual(
            response.data['categories'][0]['children'][1]['children'][0]['children'][1]['name'],
            'Category 1212'
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

    def test_update_books_with_categories_with_multiple_children(self):
        """
        Tests that a nested serializer can add objects referred by a foreign key. One level nesting.
        """
        url = reverse('book-list')
        data = {
            'title': 'Book 1',
            'categories': [
                {
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
            ]
        }
        response = self.client.post(url, data, format='json')

        data = json.loads(response.content.decode('utf-8'))

        # Send update request
        url = reverse('book-detail', kwargs={'pk': data['pk']})
        response = self.client.put(url, data, format='json')

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Book 1')
        self.assertEqual(response.data['categories'][0]['name'], 'Category 1')
        self.assertEqual(response.data['categories'][0]['children'][0]['name'], 'Category 11')
        self.assertEqual(response.data['categories'][0]['children'][1]['name'], 'Category 12')
        self.assertEqual(response.data['categories'][0]['children'][2]['name'], 'Category 13')
        self.assertEqual(
            response.data['categories'][0]['children'][0]['children'][0]['name'], 'Category 111'
        )
        self.assertEqual(
            response.data['categories'][0]['children'][1]['children'][0]['name'], 'Category 121'
        )
        self.assertEqual(
            response.data['categories'][0]['children'][1]['children'][0]['children'][0]['name'],
            'Category 1211'
        )
        self.assertEqual(
            response.data['categories'][0]['children'][1]['children'][0]['children'][1]['name'],
            'Category 1212'
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

        # Assert book count
        self.assertEqual(Category.objects.get(name='Category 1').books.count(), 1)
        self.assertEqual(Category.objects.get(name='Category 11').books.count(), 0)
        self.assertEqual(Category.objects.get(name='Category 12').books.count(), 0)
        self.assertEqual(Category.objects.get(name='Category 13').books.count(), 0)
        self.assertEqual(Category.objects.get(name='Category 111').books.count(), 0)
        self.assertEqual(Category.objects.get(name='Category 121').books.count(), 0)
        self.assertEqual(Category.objects.get(name='Category 1211').books.count(), 0)
        self.assertEqual(Category.objects.get(name='Category 1212').books.count(), 0)

        # Modify data
        data = json.loads(response.content.decode('utf-8'))
        data['categories'][0]['children'][1]['children'][0]['children'][0]['name'] = 'Category 1211 update'
        old_pk_category_1212 = data['categories'][0]['children'][1]['children'][0]['children'][1]['pk']
        del data['categories'][0]['children'][1]['children'][0]['children'][1]['pk']
        del data['categories'][0]['children'][2]
        del data['categories'][0]['children'][0]

        # Send update request
        url = reverse('book-detail', kwargs={'pk': data['pk']})
        response = self.client.put(url, data, format='json')

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Book 1')
        self.assertEqual(response.data['categories'][0]['name'], 'Category 1')
        self.assertEqual(response.data['categories'][0]['children'][0]['name'], 'Category 12')
        self.assertEqual(
            response.data['categories'][0]['children'][0]['children'][0]['name'], 'Category 121'
        )
        self.assertEqual(
            response.data['categories'][0]['children'][0]['children'][0]['children'][0]['name'],
            'Category 1211 update'
        )
        self.assertEqual(
            response.data['categories'][0]['children'][0]['children'][0]['children'][1]['name'],
            'Category 1212'
        )

        # Assert data
        self.assertEqual(Category.objects.count(), 9)

        self.assertTrue(Category.objects.filter(name='Category 1', parent=None).exists())
        self.assertFalse(
            Category.objects.filter(name='Category 11', parent=Category.objects.get(name='Category 1')).exists()
        )
        self.assertTrue(
            Category.objects.filter(name='Category 12', parent=Category.objects.get(name='Category 1')).exists()
        )
        self.assertFalse(
            Category.objects.filter(name='Category 13', parent=Category.objects.get(name='Category 1')).exists()
        )
        self.assertTrue(
            Category.objects.filter(name='Category 13').exists()
        )
        self.assertTrue(
            Category.objects.filter(name='Category 111', parent=Category.objects.get(name='Category 11')).exists()
        )
        self.assertTrue(
            Category.objects.filter(name='Category 121', parent=Category.objects.get(name='Category 12')).exists()
        )
        self.assertTrue(
            Category.objects.filter(
                name='Category 1211 update',
                parent=Category.objects.get(name='Category 121'),
                pk=data['categories'][0]['children'][0]['children'][0]['children'][0]['pk']
            ).exists()
        )
        self.assertFalse(
            Category.objects.filter(name='Category 1211').exists()
        )
        self.assertTrue(
            Category.objects.filter(name='Category 1212', parent=Category.objects.get(name='Category 121')).exists()
        )
        self.assertTrue(
            Category.objects.filter(name='Category 1212', parent=None, pk=old_pk_category_1212).exists()
        )

        # Assert book count
        self.assertEqual(Category.objects.get(name='Category 1').books.count(), 1)
        self.assertEqual(Category.objects.get(name='Category 11').books.count(), 0)
        self.assertEqual(Category.objects.get(name='Category 12').books.count(), 0)
        self.assertEqual(Category.objects.get(name='Category 13').books.count(), 0)
        self.assertEqual(Category.objects.get(name='Category 111').books.count(), 0)
        self.assertEqual(Category.objects.get(name='Category 121').books.count(), 0)
        self.assertEqual(Category.objects.get(name='Category 1211 update').books.count(), 0)
        self.assertEqual(Category.objects.filter(parent=None).get(name='Category 1212').books.count(), 0)
        self.assertEqual(Category.objects.exclude(parent=None).get(name='Category 1212').books.count(), 0)

        # Modify data
        new_data = json.loads(response.content.decode('utf-8'))
        new_data['categories'] = []

        # Send update request
        url = reverse('book-detail', kwargs={'pk': new_data['pk']})
        response = self.client.put(url, new_data, format='json')

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Book 1')
        self.assertListEqual(response.data['categories'], [])

        # Assert data
        self.assertEqual(Category.objects.count(), 9)

        self.assertTrue(Category.objects.filter(name='Category 1', parent=None).exists())
        self.assertFalse(
            Category.objects.filter(name='Category 11', parent=Category.objects.get(name='Category 1')).exists()
        )
        self.assertTrue(
            Category.objects.filter(name='Category 12', parent=Category.objects.get(name='Category 1')).exists()
        )
        self.assertFalse(
            Category.objects.filter(name='Category 13', parent=Category.objects.get(name='Category 1')).exists()
        )
        self.assertTrue(
            Category.objects.filter(name='Category 13').exists()
        )
        self.assertTrue(
            Category.objects.filter(name='Category 111', parent=Category.objects.get(name='Category 11')).exists()
        )
        self.assertTrue(
            Category.objects.filter(name='Category 121', parent=Category.objects.get(name='Category 12')).exists()
        )
        self.assertTrue(
            Category.objects.filter(
                name='Category 1211 update',
                parent=Category.objects.get(name='Category 121'),
                pk=data['categories'][0]['children'][0]['children'][0]['children'][0]['pk']
            ).exists()
        )
        self.assertFalse(
            Category.objects.filter(name='Category 1211').exists()
        )
        self.assertTrue(
            Category.objects.filter(name='Category 1212', parent=Category.objects.get(name='Category 121')).exists()
        )
        self.assertTrue(
            Category.objects.filter(name='Category 1212', parent=None, pk=old_pk_category_1212).exists()
        )

        # Assert book count
        self.assertEqual(Category.objects.get(name='Category 1').books.count(), 0)
        self.assertEqual(Category.objects.get(name='Category 11').books.count(), 0)
        self.assertEqual(Category.objects.get(name='Category 12').books.count(), 0)
        self.assertEqual(Category.objects.get(name='Category 13').books.count(), 0)
        self.assertEqual(Category.objects.get(name='Category 111').books.count(), 0)
        self.assertEqual(Category.objects.get(name='Category 121').books.count(), 0)
        self.assertEqual(Category.objects.get(name='Category 1211 update').books.count(), 0)
        self.assertEqual(Category.objects.filter(parent=None).get(name='Category 1212').books.count(), 0)
        self.assertEqual(Category.objects.exclude(parent=None).get(name='Category 1212').books.count(), 0)
