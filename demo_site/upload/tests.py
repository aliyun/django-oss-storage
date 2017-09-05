# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

# Create your tests here.

class SampleTest(TestCase):
    def test_basic_operation(self):
        """
        Test a simple math addition
        """
        self.assertEqual(100 + 200, 300)
