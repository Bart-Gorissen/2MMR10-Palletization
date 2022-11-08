import functools

class Item:
    x, y, z = 0, 0, 0
    w, l, h = 0, 0, 0
    m, c = 1, (0, 0, 0)
    name = ""

    def __init__(self, name, w, l, h):
        self.name = name
        self.set((0, 0, 0), (w, l, h))

    def set(self, blc, wlh):
        self.x = blc[0]
        self.y = blc[1]
        self.z = blc[2]
        self.w = wlh[0]
        self.l = wlh[1]
        self.h = wlh[2]
        self.c = (self.x + (self.w / 2), self.y + (self.l / 2), self.z + (self.h / 2))

    def is_in_bounds(self, W, L, H):
        if self.x < 0: return False
        if self.y < 0: return False
        if self.z < 0: return False
        if self.x + self.w > W: return False
        if self.y + self.l > L: return False
        if self.z + self.h > H: return False
        return True

    def has_intersect(self, q):
        if self.x + self.w <= q.x: return False
        if q.x + q.w <= self.x: return False
        if self.y + self.l <= q.y: return False
        if q.y + q.l <= self.y: return False
        if self.z + self.h <= q.z: return False
        if q.z + q.h <= self.z: return False
        return True

    def has_intersect_set(self, Q):
        for q in Q:
            if self.has_intersect(q): return True
        return False

    def to_string(self):
        return "{n} x: {x} y: {y} z: {z} w: {w} l: {l} h: {h} V: {v}".format(n=self.name,
                                                                             x=self.x,y=self.y,z=self.z,
                                                                             w=self.w,l=self.l,h=self.h,
                                                                             v=self.w*self.l*self.h)

    def __repr__(self):
        return self.to_string()

@functools.total_ordering
class ItemQueueTask:
    def __init__(self, item, key, cnt):
        self.item = item
        self.key = key
        self.cnt = cnt

    def __repr__(self):
        return "Item {p}, key {k}, entry {c}".format(p=self.item,k=self.key,c=self.cnt)

    def __lt__(self, other):
        return (self.key, self.cnt) < (other.key, other.cnt)

    def __eq__(self, other):
        return (self.key, self.cnt) == (other.key, other.cnt)