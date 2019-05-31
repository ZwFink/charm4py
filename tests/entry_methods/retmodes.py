from charm4py import charm, Chare, Group, Array, Reducer, threaded
import random


class Test(Chare):

    def __init__(self, callback, callback_test_done):
        self.myval = random.randint(1, 100)
        self.rcvd_bcasts = 0
        self.callback_test_done = callback_test_done
        self.contribute(self.myval, Reducer.gather, callback)

    def getVal(self, bcast):
        if bcast:
            self.rcvd_bcasts += 1
            if self.rcvd_bcasts == 6:
                self.contribute(None, None, self.callback_test_done)
        return self.myval

    @threaded
    def getVal_th(self, bcast):
        return self.getVal(bcast)


def main(args):
    f1 = charm.createFuture()
    f2 = charm.createFuture()
    done1 = charm.createFuture()
    done2 = charm.createFuture()
    a = Array(Test, charm.numPes() * 10, args=[f1, done1])
    g = Group(Test, args=[f2, done2])

    collections = []
    collections.append((a, f1.get(), charm.numPes() * 10))
    collections.append((g, f2.get(), charm.numPes()))
    for collection, vals, num_elems in collections:
        indexes = list(range(num_elems))
        random_idxs = random.sample(indexes, int(max(len(indexes) * 0.8, 1)))
        for random_idx in random_idxs:
            retval = collection[random_idx].getVal(False, ret=0)
            assert retval is None

            retval = collection[random_idx].getVal(False, ret=1).get()
            assert retval == vals[random_idx]

            retval = collection[random_idx].getVal(False, ret=2).get()
            assert retval == vals[random_idx]

            retval = collection[random_idx].getVal_th(False, ret=0)
            assert retval is None

            retval = collection[random_idx].getVal_th(False, ret=1).get()
            assert retval == vals[random_idx]

            retval = collection[random_idx].getVal_th(False, ret=2).get()
            assert retval == vals[random_idx]

        retval = collection.getVal(True, ret=0)
        assert retval is None

        retval = collection.getVal(True, ret=1).get()
        assert retval is None

        retval = collection.getVal(True, ret=2).get()
        assert retval == [vals[i] for i in range(num_elems)]

        retval = collection.getVal_th(True, ret=0)
        assert retval is None

        retval = collection.getVal_th(True, ret=1).get()
        assert retval is None

        retval = collection.getVal_th(True, ret=2).get()
        assert retval == [vals[i] for i in range(num_elems)]

    done1.get()
    done2.get()
    exit()


charm.start(main)