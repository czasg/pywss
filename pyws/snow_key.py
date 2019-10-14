import time


def get_current_timestamp(): return int(time.time() * 1000)


class SnowKey:
    def __init__(self, workerId, datacenterId):
        self.workerId = workerId
        self.datacenterId = datacenterId
        self.sequence = 0
        self.twepoch = 1288834974657
        self.workerIdBits = 5
        self.datacenterIdBits = 5
        self.maxWorkerId = -1 ^ (-1 << self.workerIdBits)
        self.maxDatacenterId = -1 ^ (-1 << self.datacenterIdBits)
        self.sequenceBits = 12
        self.workerIdShift = self.sequenceBits
        self.datacenterIdShift = self.sequenceBits + self.workerIdBits
        self.timestampLeftShift = self.sequenceBits + self.workerIdBits + self.datacenterIdBits
        self.sequenceMask = -1 ^ (-1 << self.sequenceBits)
        self.lastTimestamp = -1

    @classmethod
    def from_node(cls, workerId=0, datacenterId=0):
        return cls(workerId, datacenterId)

    def next_id(self):
        timestamp = get_current_timestamp()
        if self.lastTimestamp > timestamp:
            raise Exception()
        if self.lastTimestamp == timestamp:
            self.sequence = (self.sequence + 1) & self.sequenceMask
            if self.sequence == 0:
                timestamp = self.next_timestamp(timestamp)
        else:
            self.sequence = 0
        self.lastTimestamp = timestamp
        return ((timestamp - self.twepoch) << self.timestampLeftShift) | \
               (self.datacenterId << self.datacenterIdShift) | \
               (self.workerId << self.workerIdShift) | \
               self.sequence

    def next_timestamp(self, timestamp, next_timestamp=0):
        while timestamp >= next_timestamp: next_timestamp = get_current_timestamp()
        return next_timestamp


id_pool = SnowKey.from_node()
