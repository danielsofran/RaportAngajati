import math
from abc import ABC, abstractmethod
from numpy import dot, array
from math import sqrt

class Shape(ABC):
    @abstractmethod
    def distance(self, point: list) -> float:
        pass

class Triunghi(Shape):
    def __init__(self, point1: list, point2: list, point3: list):
        self.__point1 = point1[:]
        self.__point2 = point2[:]
        self.__point3 = point3[:]

    @staticmethod
    def __list_without(l1: list, l2: list) -> list:
        rez = []
        for item in l1:
            if item != l2:
                rez.append(item)
        return rez

    @staticmethod
    def __pointTriangleDistance(TRI:list, P:list):
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

    def distance(self, point: list) -> float:
        TRI = [self.__point1 + [1], self.__point2 + [1], self.__point3 + [1]]
        return self.__pointTriangleDistance(array(TRI), point + [1])[0]

class Patrulater(Shape):
    def __int__(self, point1: list, point2: list, point3: list, point4: list):
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
