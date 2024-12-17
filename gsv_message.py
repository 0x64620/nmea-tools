from nmea_message import NMEAMessage

class GSVMessage(NMEAMessage):
    def __init__(self, raw_message):
        super().__init__(raw_message)
        if self.valid:
            self.parse()

    def parse(self):
        parts = self.raw.split(',')
        self.total_messages = int(parts[1]) if parts[1].isdigit() else 0
        self.message_number = int(parts[2]) if parts[2].isdigit() else 0
        self.satellites_in_view = int(parts[3]) if parts[3].isdigit() else 0
        self.satellites = []
        for i in range(4, len(parts) - 1, 4):
            if len(parts) > i + 3 and parts[i].isdigit():
                satellite = {
                    'prn': int(parts[i]),
                    'elevation': int(parts[i + 1]) if parts[i + 1].isdigit() else None,
                    'azimuth': int(parts[i + 2]) if parts[i + 2].isdigit() else None,
                    'snr': int(parts[i + 3]) if parts[i + 3].isdigit() else None,
                }
                self.satellites.append(satellite)
