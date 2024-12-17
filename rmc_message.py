from nmea_message import NMEAMessage

class RMCMessage(NMEAMessage):
    def __init__(self, raw_message):
        super().__init__(raw_message)
        if self.valid:
            self.parse()

    def parse(self):
        parts = self.raw.split(',')
        self.time = parts[1]
        self.status = parts[2]
        self.latitude = self.parse_coordinate(parts[3], parts[4])
        self.longitude = self.parse_coordinate(parts[5], parts[6])
        self.speed_over_ground = float(parts[7]) if parts[7] else None
        self.track_made_good = float(parts[8]) if parts[8] else None
        self.date = parts[9]

    def parse_coordinate(self, value, direction):
        if not value:
            return None
        degrees = float(value[:2])
        minutes = float(value[2:])
        result = degrees + (minutes / 60)
        if direction in ['S', 'W']:
            result = -result
        return result
