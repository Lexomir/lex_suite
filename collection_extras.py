from collections import OrderedDict, MutableSet 


class OrderedSet(OrderedDict, MutableSet):
    def __init__(self, *args, **kwargs):
        super(OrderedSet, self).__init__()
        self.update(*args, **kwargs)
        self.index = 0

    def update(self, *args, **kwargs):
        if kwargs:
            raise TypeError("update() takes no keyword arguments")

        for s in args:
            for e in s:
                 self.add(e)

    def add(self, elem):
        if elem in self:
            return self[elem]
        else:
            self[elem] = self.index
            self.index += 1
            return self.index - 1

    def append(self, elem):
        return self.add(elem)

    def discard(self, elem):
        self.pop(elem, None)

    def __setitem__(self, key, value):
        # optional processing here
        super(OrderedSet, self).__setitem__(key, value)

    def __le__(self, other):
        return all(e in other for e in self)

    def __lt__(self, other):
        return self <= other and self != other

    def __ge__(self, other):
        return all(e in self for e in other)

    def __gt__(self, other):
        return self >= other and self != other

    def __repr__(self):
        return 'OrderedSet([%s])' % (', '.join(map(repr, self.keys())))

    def __str__(self):
        return '{%s}' % (', '.join(map(repr, self.keys())))

    difference = property(lambda self: self.__sub__)
    difference_update = property(lambda self: self.__isub__)
    intersection = property(lambda self: self.__and__)
    intersection_update = property(lambda self: self.__iand__)
    issubset = property(lambda self: self.__le__)
    issuperset = property(lambda self: self.__ge__)
    symmetric_difference = property(lambda self: self.__xor__)
    symmetric_difference_update = property(lambda self: self.__ixor__)
    union = property(lambda self: self.__or__)