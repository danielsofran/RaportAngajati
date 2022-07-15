from django.test import TestCase
from main.geometry import *

# Create your tests here.

class GeometryTestCase(TestCase):
    def setUp(self) -> None:
        self.t = Triunghi([0, 0], [0, 5], [1, 0])

    def test_geometry(self):
        self.assertEqual(self.t.distance([-1, 0]), 1)
        self.assertEqual(self.t.distance([2, 0]), 1)
        self.assertEqual(self.t.distance([3, 0]), 2)
        self.assertAlmostEqual(self.t.distance([2.34523412, 0]), 1.34523412)