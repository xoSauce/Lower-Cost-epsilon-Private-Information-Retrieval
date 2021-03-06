from random import SystemRandom
from pir_executor import PIRExecutor
from epspvt_utils import SecurityParameters


class MessageCreator:
    def __init__(self, client):
        self.client = client
        self.dbnum = len(client.db_list)

    def _generate_random_indexes(self, requested_index, index_limit):
        assert(SecurityParameters.NUMBER_OF_REQUESTS < index_limit)
        gen = SystemRandom()
        random_set = set()
        while len(random_set) < SecurityParameters.NUMBER_OF_REQUESTS - 1:
            num = gen.randrange(index_limit)
            if num == requested_index:
                continue
            random_set.add(num)
        return random_set

    def generate_messages(self, requested_index,
                          requested_db,
                          record_size,
                          portEnum,
                          pir_xor=False):
        if not pir_xor:
            assert SecurityParameters.NUMBER_OF_REQUESTS % self.dbnum == 0
            indexes = self._generate_random_indexes(
                requested_index, record_size)
            real_message = self.client.package_message(
                requested_index, requested_db, pir_xor, portEnum)
            db_index = {}
            for i in range(self.dbnum):
                db_index[i] = []
            db_index[requested_db].append(real_message)
            current_db = 0
            first_round = True
            for i in indexes:
                if first_round and current_db == requested_db:
                    current_db += 1
                    current_db %= self.dbnum
                    if current_db == 0:
                        first_round = False
                db_index[current_db].append(
                    self.client.package_message(i, current_db, pir_xor, portEnum))
                current_db += 1
                current_db %= self.dbnum
                if current_db == 0:
                    first_round = False
            return db_index
        else:
            pirExecutor = PIRExecutor()
            messagePack = pirExecutor.getMessagePack(
                requested_index, record_size, self.dbnum)
            db_index = {}
            assert(len(messagePack) == self.dbnum)
            for i in range(self.dbnum):
                db_index[i] = []
            current_db = 0
            for i in messagePack:
                db_index[current_db].append(
                    self.client.package_message(i, current_db, pir_xor, portEnum))
                current_db += 1
            return db_index
