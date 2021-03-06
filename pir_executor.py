from random import SystemRandom, uniform
from epspvt_utils import SecurityParameters
from binary_encoderdecoder import BinaryEncoderDecoder
import array

class PIRExecutor():
    def __init__(self):
        self.encoder = BinaryEncoderDecoder()
        pass

    def _getRandomBernouille(self, random_gen):
        r = SystemRandom().random()
        if r < random_gen:
            return 1
        return 0

    ### Generate a vector with sumEven. First generate a vector of length `size`
    ### And then if it doesn't match the requirements, reduce the SPARSITY_FACTOR
    ### by randomly removing one element to turn the sum from even to odd
    def _genRandomVector(self, size, sumEven):
        vector_sum = 0
        v = []
        random_gen = SecurityParameters.SPARSITY_FACTOR
        while vector_sum == 0:
            vector_sum = 0
            set_indexes = []
            v = []
            for i in range(size):
                value = self._getRandomBernouille(random_gen)
                if value == 1:
                    set_indexes.append(i)
                v.append(value)
            vector_sum = sum(v)

        if sumEven:
            if vector_sum % 2 != 0:
                index = int(uniform(0, len(set_indexes)))
                v[set_indexes[index]] = 0
        elif not sumEven:
            if vector_sum % 2 == 0:
                index = int(uniform(0, len(set_indexes)))
                v[set_indexes[index]] = 0
        return v

    def stringXorer(self, a, b):
        if type(a) is str:
            a = a.encode('utf-8')
        if type(b) is str:
            b = b.encode('utf-8')
        array_a = array.array('B', a)
        array_b = array.array('B', b)
        while(len(array_a) < len(array_b)):
            array_a.append(0)
        while(len(array_b) < len(array_a)):
            array_b.append(0)
        xored_array = array.array('B',[])
        for i in range(len(array_a)):
            xored_array.append(array_a[i] ^ array_b[i])
        stringify = xored_array.tostring()
        return stringify

    def _getMessagePack(self, index, size, dbnum):
        m = []
        for i in range(size):
            v = self._genRandomVector(dbnum, not i == index)
            m.append(v)
        return m

    def getMessagePack(self, index, size, dbnum):
        ## return a transposed list of messages, ready to be sent
        return [self.encoder.encode_binary(list(i)) for i in zip(*self._getMessagePack(index,size, dbnum))]
