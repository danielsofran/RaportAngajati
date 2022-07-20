import datetime

from django.test import TestCase

import main.models
from . import utils
from main.geometry import *

# Create your tests here.

class GeometryTestCase(TestCase):
    def setUp(self) -> None:
        self.t = Triunghi([0, 0], [0, 5], [1, 0])
        self.p = Patrulater([0, 0], [0, 5], [1, 0], [1, 5])
        self.c = Cerc([0, 0], [1, 0])

    def test_closest_point(self):
        self.t = Triunghi([0, 0], [0, 5], [1.5, 0])
        pt = self.t.closestPoint([2, 0])
        self.assertEqual(pt, [1.5, 0])
        cerc = self.c
        self.assertEqual(cerc.closestPoint([-2, 0]), [-1, 0])
        self.assertEqual(cerc.closestPoint([2, 0]), [1, 0])
        cerc = Cerc([1, 1], [1, 2])

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

class OwnSettingsTestCase(TestCase):
    def setUp(self) -> None:
        self.forma = main.models.Forma()

    def test_forma(self):
        forma = self.forma
        forma.tip = "Triunghi"
        forma.puncte = "0 0\n1 0\n0 1"
        self.assertEqual(forma.getShape().distance([-1, 0]), 1)
        forma.puncte = "0 0\n1 0\n0 1\n"
        self.assertEqual(forma.getShape().distance([-1, 0]), 1)
        forma.tip = "Patrulater"
        forma.puncte = "0 0\n1 0\n0 1\n1 1"
        self.assertEqual(forma.getShape().distance([-1, 0]), 1)
        forma.tip = "Cerc"
        forma.puncte = "0 0\n1 1\n\n"
        self.assertEqual(forma.getShape().distance([-1, 0]), 0)

class UtilsTestCase(TestCase):
    def setUp(self):
        main.models.OwnSettings.objects.create(program="L Ma Mi J V")

    def test_getnext(self):
        now = datetime.date(year=2022, month=7, day=20)
        self.assertEqual(utils.getNextDay(now).day, 21)
        self.assertEqual(utils.getPrevDay(now).day, 19)
        self.assertEqual(now.day, 20)
        now = datetime.date(year=2022, month=7, day=22)
        self.assertEqual(utils.getNextDay(now).day, 25)
