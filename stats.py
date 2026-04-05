import threading

class PacketStats:
    def __init__(self):
        self.total = 0
        self.processed = 0
        self.duplicates = 0
        self.invalid = 0
        self.lock = threading.Lock()

    def received(self):
        with self.lock:
            self.total += 1

    def processed_packet(self):
        with self.lock:
            self.processed += 1

    def duplicate(self):
        with self.lock:
            self.duplicates += 1

    def invalid_packet(self):
        with self.lock:
            self.invalid += 1

    def packet_loss(self):
        with self.lock:
          if self.total == 0:
             return 0
        lost = self.invalid + self.duplicates
        return (lost / self.total) * 100