from abc import ABC, abstractmethod
from math import sqrt

import numpy
from numpy import dot, array


class Shape(ABC):
    @abstractmethod
    def distance(self, point: list) -> float:
        pass

    @abstractmethod
    def closestPoint(self, point: list) -> list:
        pass

class Triunghi(Shape):
    def __init__(self, point1: list, point2: list, point3: list):
        self.__point1 = point1
        self.__point2 = point2
        self.__point3 = point3

    @staticmethod
    def __list_without(l1: list, l2: list) -> list:
        rez = []
        for item in l1:
            if item != l2:
                rez.append(item)
        return rez

    @staticmethod
    def __pointTriangleDistance(TRI:numpy.array, P:list):
        # function [dist,PP0] = pointTriangleDistance(TRI,P)
        # calculate distance between a point and a triangle in 3D
        # SYNTAX
        #   dist = pointTriangleDistance(TRI,P)
        #   [dist,PP0] = pointTriangleDistance(TRI,P)
        #
        # DESCRIPTION
        #   Calculate the distance of a given point P from a triangle TRI.
        #   Point P is a row vector of the form 1x3. The triangle is a matrix
        #   formed by three rows of points TRI = [P1;P2;P3] each of size 1x3.
        #   dist = pointTriangleDistance(TRI,P) returns the distance of the point P
        #   to the triangle TRI.
        #   [dist,PP0] = pointTriangleDistance(TRI,P) additionally returns the
        #   closest point PP0 to P on the triangle TRI.
        #
        # Author: Gwolyn Fischer
        # Release: 1.0
        # Release date: 09/02/02
        # Release: 1.1 Fixed Bug because of normalization
        # Release: 1.2 Fixed Bug because of typo in region 5 20101013
        # Release: 1.3 Fixed Bug because of typo in region 2 20101014

        # Possible extention could be a version tailored not to return the distance
        # and additionally the closest point, but instead return only the closest
        # point. Could lead to a small speed gain.

        # Example:
        # %% The Problem
        # P0 = [0.5 -0.3 0.5]
        #
        # P1 = [0 -1 0]
        # P2 = [1  0 0]
        # P3 = [0  0 0]
        #
        # vertices = [P1; P2; P3]
        # faces = [1 2 3]
        #
        # %% The Engine
        # [dist,PP0] = pointTriangleDistance([P1;P2;P3],P0)
        #
        # %% Visualization
        # [x,y,z] = sphere(20)
        # x = dist*x+P0(1)
        # y = dist*y+P0(2)
        # z = dist*z+P0(3)
        #
        # figure
        # hold all
        # patch('Vertices',vertices,'Faces',faces,'FaceColor','r','FaceAlpha',0.8)
        # plot3(P0(1),P0(2),P0(3),'b*')
        # plot3(PP0(1),PP0(2),PP0(3),'*g')
        # surf(x,y,z,'FaceColor','b','FaceAlpha',0.3)
        # view(3)

        # The algorithm is based on
        # "David Eberly, 'Distance Between Point and Triangle in 3D',
        # Geometric Tools, LLC, (1999)"
        # http:\\www.geometrictools.com/Documentation/DistancePoint3Triangle3.pdf
        #
        #        ^t
        #  \     |
        #   \reg2|
        #    \   |
        #     \  |
        #      \ |
        #       \|
        #        *P2
        #        |\
        #        | \
        #  reg3  |  \ reg1
        #        |   \
        #        |reg0\
        #        |     \
        #        |      \ P1
        # -------*-------*------->s
        #        |P0      \
        #  reg4  | reg5    \ reg6
        # rewrite triangle in normal form
        B = TRI[0, :]
        E0 = TRI[1, :] - B
        # E0 = E0/sqrt(sum(E0.^2)); %normalize vector
        E1 = TRI[2, :] - B
        # E1 = E1/sqrt(sum(E1.^2)); %normalize vector
        D = B - P
        a = dot(E0, E0)
        b = dot(E0, E1)
        c = dot(E1, E1)
        d = dot(E0, D)
        e = dot(E1, D)
        f = dot(D, D)

        # print "{0} {1} {2} ".format(B,E1,E0)
        det = a * c - b * b
        s = b * e - c * d
        t = b * d - a * e

        # Terible tree of conditionals to determine in which region of the diagram
        # shown above the projection of the point into the triangle-plane lies.
        if (s + t) <= det:
            if s < 0.0:
                if t < 0.0:
                    # region4
                    if d < 0:
                        t = 0.0
                        if -d >= a:
                            s = 1.0
                            sqrdistance = a + 2.0 * d + f
                        else:
                            s = -d / a
                            sqrdistance = d * s + f
                    else:
                        s = 0.0
                        if e >= 0.0:
                            t = 0.0
                            sqrdistance = f
                        else:
                            if -e >= c:
                                t = 1.0
                                sqrdistance = c + 2.0 * e + f
                            else:
                                t = -e / c
                                sqrdistance = e * t + f

                                # of region 4
                else:
                    # region 3
                    s = 0
                    if e >= 0:
                        t = 0
                        sqrdistance = f
                    else:
                        if -e >= c:
                            t = 1
                            sqrdistance = c + 2.0 * e + f
                        else:
                            t = -e / c
                            sqrdistance = e * t + f
                            # of region 3
            else:
                if t < 0:
                    # region 5
                    t = 0
                    if d >= 0:
                        s = 0
                        sqrdistance = f
                    else:
                        if -d >= a:
                            s = 1
                            sqrdistance = a + 2.0 * d + f  # GF 20101013 fixed typo d*s ->2*d
                        else:
                            s = -d / a
                            sqrdistance = d * s + f
                else:
                    # region 0
                    invDet = 1.0 / det
                    s = s * invDet
                    t = t * invDet
                    sqrdistance = s * (a * s + b * t + 2.0 * d) + t * (b * s + c * t + 2.0 * e) + f
        else:
            if s < 0.0:
                # region 2
                tmp0 = b + d
                tmp1 = c + e
                if tmp1 > tmp0:  # minimum on edge s+t=1
                    numer = tmp1 - tmp0
                    denom = a - 2.0 * b + c
                    if numer >= denom:
                        s = 1.0
                        t = 0.0
                        sqrdistance = a + 2.0 * d + f  # GF 20101014 fixed typo 2*b -> 2*d
                    else:
                        s = numer / denom
                        t = 1 - s
                        sqrdistance = s * (a * s + b * t + 2 * d) + t * (b * s + c * t + 2 * e) + f

                else:  # minimum on edge s=0
                    s = 0.0
                    if tmp1 <= 0.0:
                        t = 1
                        sqrdistance = c + 2.0 * e + f
                    else:
                        if e >= 0.0:
                            t = 0.0
                            sqrdistance = f
                        else:
                            t = -e / c
                            sqrdistance = e * t + f
                            # of region 2
            else:
                if t < 0.0:
                    # region6
                    tmp0 = b + e
                    tmp1 = a + d
                    if tmp1 > tmp0:
                        numer = tmp1 - tmp0
                        denom = a - 2.0 * b + c
                        if numer >= denom:
                            t = 1.0
                            s = 0
                            sqrdistance = c + 2.0 * e + f
                        else:
                            t = numer / denom
                            s = 1 - t
                            sqrdistance = s * (a * s + b * t + 2.0 * d) + t * (b * s + c * t + 2.0 * e) + f

                    else:
                        t = 0.0
                        if tmp1 <= 0.0:
                            s = 1
                            sqrdistance = a + 2.0 * d + f
                        else:
                            if d >= 0.0:
                                s = 0.0
                                sqrdistance = f
                            else:
                                s = -d / a
                                sqrdistance = d * s + f
                else:
                    # region 1
                    numer = c + e - b - d
                    if numer <= 0:
                        s = 0.0
                        t = 1.0
                        sqrdistance = c + 2.0 * e + f
                    else:
                        denom = a - 2.0 * b + c
                        if numer >= denom:
                            s = 1.0
                            t = 0.0
                            sqrdistance = a + 2.0 * d + f
                        else:
                            s = numer / denom
                            t = 1 - s
                            sqrdistance = s * (a * s + b * t + 2.0 * d) + t * (b * s + c * t + 2.0 * e) + f

        # account for numerical round-off error
        if sqrdistance < 0:
            sqrdistance = 0

        dist = sqrt(sqrdistance)

        PP0 = B + s * E0 + t * E1
        return dist, PP0

    def __factor(self, point=None):
        lst = [*self.__point1, *self.__point2, *self.__point3]
        if point is not None:
            lst += [point[0], point[1]]
        mx = 0
        for nr in lst:
            d = str(nr).split('.')
            if len(d) < 2: continue
            exp = len(d[1])
            mx = max(mx, exp)
        return 10**mx

    def closestPoint(self, point: list) -> list:
        factor = self.__factor(point)
        TRI = [[self.__point1[0]*factor] + [self.__point1[1]*factor] + [1],
               [self.__point2[0]*factor] + [self.__point2[1]*factor] + [1],
               [self.__point3[0]*factor] + [self.__point3[1]*factor] + [1]]
        P = [point[0]*factor] + [point[1]*factor] + [1]
        P0 = self.__pointTriangleDistance(array(TRI), P)[1]
        return [P0[0]/factor, P0[1]/factor]

    def distance(self, point: list) -> float:
        #TRI = [self.__point1 + [1], self.__point2 + [1], self.__point3 + [1]]
        factor = self.__factor(point)
        TRI = [[self.__point1[0] * factor] + [self.__point1[1] * factor] + [1],
               [self.__point2[0] * factor] + [self.__point2[1] * factor] + [1],
               [self.__point3[0] * factor] + [self.__point3[1] * factor] + [1]]
        P = [point[0] * factor] + [point[1] * factor] + [1]
        return self.__pointTriangleDistance(array(TRI), P)[0]/factor

class Patrulater(Shape):
    def __init__(self, point1: list, point2: list, point3: list, point4: list):
        self.__point1 = point1
        self.__point2 = point2
        self.__point3 = point3
        self.__point4 = point4

    @staticmethod
    def __ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

    # Return true if line segments AB and CD intersect
    @staticmethod
    def __intersect(A, B, C, D):
        return Patrulater.__ccw(A, C, D) != Patrulater.__ccw(B, C, D) and Patrulater.__ccw(A, B, C) != Patrulater.__ccw(A, B, D)

    def points(self, order = (1, 2, 3, 4)):
        pcts = [self.__point1, self.__point2, self.__point3, self.__point4]
        rez = []
        for i in range(4):
            rez.append(pcts[order[i]-1])
        return rez

    @property
    def __getDiag(self):
        # returneaza tuple din lista diagonala si punctele care au ramas
        if Patrulater.__intersect(*self.points()):  # 12 - 34
            return self.points()[0:2], self.points()[2:4]
        elif Patrulater.__intersect(*self.points((1, 3, 2, 4))):  # 13 - 24
            return self.points((1, 3, 2, 4))[0:2], self.points((1, 3, 2, 4))[2:4]
        elif Patrulater.__intersect(*self.points((1, 4, 2, 3))):  # 14 - 23
            return self.points((1, 3, 2, 4))[0:2], self.points((1, 3, 2, 4))[2:4]
        raise ValueError("la patrulaterul curent, nu e nici diagonala 12, nici 13, nici 14")

    def distance(self, point: list) -> float:
        diag, rest = self.__getDiag
        t1 = Triunghi(*diag, rest[0])
        t2 = Triunghi(*diag, rest[1])
        return min(t1.distance(point), t2.distance(point))

    def closestPoint(self, point: list) -> list:
        diag, rest = self.__getDiag
        t1 = Triunghi(*diag, rest[0])
        t2 = Triunghi(*diag, rest[1])
        if t1.distance(point) <= t2.distance(point):
            return t1.closestPoint(point)
        return t2.closestPoint(point)

class Cerc(Shape):
    @staticmethod
    def __dist(point1: list, point2: list):
        return sqrt((point1[1]-point2[1])**2 + (point1[0]-point2[0])**2)

    @staticmethod
    def __circle_line_segment_intersection(circle_center, circle_radius, pt1, pt2, full_line=False, tangent_tol=1e-8):
        """ Find the points at which a circle intersects a line-segment.  This can happen at 0, 1, or 2 points.

        :param circle_center: The (x, y) location of the circle center
        :param circle_radius: The radius of the circle
        :param pt1: The (x, y) location of the first point of the segment
        :param pt2: The (x, y) location of the second point of the segment
        :param full_line: True to find intersections along full line - not just in the segment.  False will just return intersections within the segment.
        :param tangent_tol: Numerical tolerance at which we decide the intersections are close enough to consider it a tangent
        :return Sequence[Tuple[float, float]]: A list of length 0, 1, or 2, where each element is a point at which the circle intercepts a line segment.

        Note: We follow: http://mathworld.wolfram.com/Circle-LineIntersection.html
        """

        (p1x, p1y), (p2x, p2y), (cx, cy) = pt1, pt2, circle_center
        (x1, y1), (x2, y2) = (p1x - cx, p1y - cy), (p2x - cx, p2y - cy)
        dx, dy = (x2 - x1), (y2 - y1)
        dr = (dx ** 2 + dy ** 2) ** .5
        big_d = x1 * y2 - x2 * y1
        discriminant = circle_radius ** 2 * dr ** 2 - big_d ** 2

        if discriminant < 0:  # No intersection between circle and line
            return []
        else:  # There may be 0, 1, or 2 intersections with the segment
            intersections = [
                (cx + (big_d * dy + sign * (-1 if dy < 0 else 1) * dx * discriminant ** .5) / dr ** 2,
                 cy + (-big_d * dx + sign * abs(dy) * discriminant ** .5) / dr ** 2)
                for sign in ((1, -1) if dy < 0 else (-1, 1))]  # This makes sure the order along the segment is correct
            if not full_line:  # If only considering the segment, filter out intersections that do not fall within the segment
                fraction_along_segment = [(xi - p1x) / dx if abs(dx) > abs(dy) else (yi - p1y) / dy for xi, yi in
                                          intersections]
                intersections = [pt for pt, frac in zip(intersections, fraction_along_segment) if 0 <= frac <= 1]
            if len(intersections) == 2 and abs(
                    discriminant) <= tangent_tol:  # If line is tangent to circle, return just one point (as both intersections have same location)
                return [intersections[0]]
            else:
                return intersections

    def __init__(self, center: list, point: list):
        self.__center = center
        self.__point = point
        self.__raza = Cerc.__dist(center, point)

    @property
    def center(self):
        return (self.__center[0], self.__center[1])

    @property
    def centerStr(self):
        return f"{self.__center[0]}, {self.__center[1]}"

    @property
    def point(self):
        return (self.__point[0], self.__point[1])

    @property
    def pointStr(self):
        return f"{self.__point[0]}, {self.__point[1]}"

    @property
    def raza(self):
        return self.__raza

    def distance(self, point: list) -> float:
        dst = Cerc.__dist(self.__center, point) - self.__raza
        if dst < 0: return 0
        return dst

    def closestPoint(self, point: list) -> list:
        centru = (self.__center[0], self.__center[1])
        point2 = (point[0], point[1])
        intersections = Cerc.__circle_line_segment_intersection\
            (centru, self.__raza, centru, point2)
        if len(intersections) == 0:
            raise ValueError("interior")
        # dmin = 2**32
        # pmin = None
        # for k in range(len(intersections)):
        #     p = [intersections[k][0], intersections[k][1]]
        #     d = abs(self.distance(p) - self.distance(point))
        #     if d < dmin:
        #         dmin = d
        #         pmin = p
        k=0
        return [intersections[k][0], intersections[k][1]]
