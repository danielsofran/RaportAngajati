from django.test import TestCase
from main.geometry import *

# Create your tests here.

class GeometryTestCase(TestCase):
    def setUp(self) -> None:
        self.t = Triunghi([0, 0], [0, 5], [1, 0])
        self.p = Patrulater([0, 0], [0, 5], [1, 0], [1, 5])
        self.c = Cerc([0, 0], [1, 0])

    def test_triunghi(self):
        self.assertEqual(self.t.distance([-1, 0]), 1)
        self.assertEqual(self.t.distance([2, 0]), 1)
        self.assertEqual(self.t.distance([3, 0]), 2)
        self.assertAlmostEqual(self.t.distance([2.34523412, 0]), 1.34523412)
        self.assertAlmostEqual(self.t.distance([2, -1]), sqrt(2))
        self.assertEqual(self.t.distance([0.5, 0]), 0)
        self.assertEqual(self.t.distance([0.5, 0.5]), 0)

    def test_patrulater(self):
        self.assertEqual(self.p.distance([-1, 0]), 1)
        self.assertEqual(self.p.distance([2, 0]), 1)
        self.assertEqual(self.p.distance([3, 0]), 2)

    def test_cerc(self):
        self.assertEqual(self.c.distance([2, 0]), 1)
        self.assertEqual(self.c.distance([0.5, -0.5]), 0)
        self.assertEqual(self.c.distance([-1, 0]), 0)
        self.assertEqual(self.c.distance([-1, 0]), 0)
