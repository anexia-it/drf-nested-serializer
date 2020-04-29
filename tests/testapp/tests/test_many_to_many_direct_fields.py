import json
import unittest

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from testapp.models import Book, Chapter, Page, Category, Author, AuthorBook


class ManyToManyDirectFieldsTests(APITestCase):

    @unittest.skip("ToDo: Fix for direct m2m relation required")
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
                    "child_categories": [
                        {
                            "name": "Category 11",
                            "child_categories": [
                                {
                                    "name": "Category 111",
                                    "child_categories": [],
                                }
                            ],
                        },
                        {
                            "name": "Category 12",
                            "child_categories": [
                                {
                                    "name": "Category 121",
                                    "child_categories": [
                                        {
                                            "name": "Category 1211",
                                            "child_categories": [],
                                        },
                                        {
                                            "name": "Category 1212",
                                            "child_categories": [],
                                        }
                                    ],
                                }
                            ],
                        },
                        {
                            "name": "Category 13",
                            "child_categories": [],
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
        self.assertEqual(response.data['categories'][0]['child_categories'][0]['name'], 'Category 11')
        self.assertEqual(response.data['categories'][0]['child_categories'][1]['name'], 'Category 12')
        self.assertEqual(response.data['categories'][0]['child_categories'][2]['name'], 'Category 13')
        self.assertEqual(
            response.data['categories'][0]['child_categories'][0]['child_categories'][0]['name'], 'Category 111'
        )
        self.assertEqual(
            response.data['categories'][0]['child_categories'][1]['child_categories'][0]['name'], 'Category 121'
        )
        self.assertEqual(
            response.data['categories'][0]['child_categories'][1]['child_categories'][0]['child_categories'][0]['name'],
            'Category 1211'
        )
        self.assertEqual(
            response.data['categories'][0]['child_categories'][1]['child_categories'][0]['child_categories'][1]['name'],
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
