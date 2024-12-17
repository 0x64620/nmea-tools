from nmea_message import NMEAMessage

class GGAMessage(NMEAMessage):
    def __init__(self, raw_message):
        super().__init__(raw_message)
        if self.valid:
            self.parse()

    def parse(self):
        parts = self.raw.split(',')
        self.time = parts[1]
        self.latitude = self.parse_coordinate(parts[2], parts[3])
        self.longitude = self.parse_coordinate(parts[4], parts[5])
        self.fix_quality = parts[6]
        self.num_satellites = int(parts[7]) if parts[7].isdigit() else 0
        self.hdop = float(parts[8]) if parts[8] else None
        self.altitude = float(parts[9]) if parts[9] else None

    def parse_coordinate(self, value, direction):
        if not value:
            return None
        degrees = float(value[:2])
        minutes = float(value[2:])
        result = degrees + (minutes / 60)
        if direction in ['S', 'W']:
            result = -result
        return result
