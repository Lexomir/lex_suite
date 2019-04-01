from math import sin, cos, sqrt, acos


def normalize(v, tolerance=0.00001):
    mag2 = sum(n * n for n in v)
    if abs(mag2 - 1.0) > tolerance:
        mag = sqrt(mag2)
        v = tuple(n / mag for n in v)
    return v

def q_mult(q1, q2):
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
    z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
    return w, x, y, z


def q_conjugate(q):
    w, x, y, z = q
    return w, -x, -y, -z


def qv_mult(q1, v1):
    q2 = (0.0,) + v1
    return q_mult(q_mult(q1, q2), q_conjugate(q1))[1:]


def axisangle_to_q(v, theta):
    v = normalize(v)
    x, y, z = v
    theta /= 2
    w = cos(theta)
    x = x * sin(theta)
    y = y * sin(theta)
    z = z * sin(theta)
    return w, x, y, z


def q_to_axisangle(q):
    w, v = q[0], q[1:]
    theta = acos(w) * 2.0
    return normalize(v), theta

def cross(a, b):
    c = [a[1]*b[2] - a[2]*b[1],
         a[2]*b[0] - a[0]*b[2],
         a[0]*b[1] - a[1]*b[0]]

    return c

def dot(u, v):
    return sum([i*j for (i, j) in zip(u, v)])


def q_from_two_vectors(u, v):
    w = cross(u, v)
    q = [1.0 + dot(u, v), w[0], w[1], w[2]]
    return normalize(q)


# Utility classes
class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def copy(self):
        return Vec2(self.x, self.y)

    def round(self, decimals=3):
        return round(self.x, decimals), round(self.y, decimals)

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        x1, y1 = self.round(5)
        x2, y2 = other.round(5)
        return x1 == x2 and y1 == y2

    def __ne__(self, other):
        return not self.__eq__(other)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __mul__(self, other):
        if isinstance(other, Vec2):
            return Vec2(self.x * other.x, self.y * other.y)
        else:
            Vec2(self.x * other, self.y * other)

    def __truediv__(self, other):
        if isinstance(other, Vec2):
            return Vec2(self.x * other.x, self.y * other.y)
        else:
            return Vec2(self.x / other, self.y / other)

    def __str__(self):
        return "Vec2({}, {})".format(self.x, self.y)

    def __repr__(self):
        return "Vec2({}, {})".format(self.x, self.y)


class Vec3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def toList(self):
        return [self.x, self.y, self.z]

    def toTuple(self):
        return self.x, self.y, self.z

    @staticmethod
    def FromList(list):
        return Vec3(list[0], list[1], list[2])

    def copy(self):
        return Vec3(self.x, self.y, self.z)

    def round(self, decimals=3):
        return round(self.x, decimals), round(self.y, decimals), round(self.z, decimals)

    def normalized(self, tolerance=0.00001):
        return Vec3(*normalize(self.toTuple(), tolerance))

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __eq__(self, other):
        x1, y1, z1 = self.round(5)
        x2, y2, z2 = other.round(5)
        return x1 == x2 and y1 == y2 and z1 == z2

    def __ne__(self, other):
        return not self.__eq__(other)

    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __rsub__(self, other):
        return Vec3(other.x - self.x, other.y - self.y, other.z - self.z)

    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        if isinstance(other, Vec3):
            return Vec3(self.x * other.x, self.y * other.y, self.z * other.z)
        else:
            return Vec3(self.x * other, self.y * other, self.z * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, Vec3):
            return Vec3(self.x * other.x, self.y * other.y, self.z * other.z)
        else:
            return Vec3(self.x / other, self.y / other, self.z / other)

    def __str__(self):
        return "Vec3({}, {}, {})".format(self.x, self.y, self.z)

    def __repr__(self):
        return "Vec3({}, {}, {})".format(self.x, self.y, self.z)


class Quat:
    def __init__(self, w, x, y, z):
        self.w = w
        self.x = x
        self.y = y
        self.z = z

    def toList(self):
        return [self.w, self.x, self.y, self.z]

    def toTuple(self):
        return self.w, self.x, self.y, self.z

    @staticmethod
    def FromList(list):
        return Quat(list[0], list[1], list[2], list[3])

    @staticmethod
    def FromDirection(dir):
        if not isinstance(dir, Vec3):
            dir = Vec3(*dir)
        up = (0, 0, 1)
        return Quat(*q_from_two_vectors(up, dir.toTuple()))
    
    @staticmethod
    def RotationBetweenVectors(dir1, dir2):
        return Quat(*q_from_two_vectors(dir1.toTuple(), dir2.toTuple()))

    def conjugate(self):
        return q_conjugate(self.toTuple())

    def __mul__(self, other):
        if isinstance(other, Quat):
            return Quat(*q_mult(self.toTuple(), other.toTuple()))
        elif isinstance(other, Vec3):
            return Vec3(*qv_mult(self.toTuple(), other.toTuple()))

    def __str__(self):
        return "Quat({}, {}, {}, {})".format(self.w, self.x, self.y, self.z)

    def __repr__(self):
        return "Quat({}, {}, {}, {})".format(self.w, self.x, self.y, self.z)
