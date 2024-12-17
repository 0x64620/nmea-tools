class NMEAMessage:
    def __init__(self, raw_message):
        self.raw = raw_message.strip()
        self.valid = self.validate_checksum()

    def validate_checksum(self):
        try:
            data, checksum = self.raw.split('*')
            data = data[1:]  # Remove the '$'
            calc_checksum = 0
            for char in data:
                calc_checksum ^= ord(char)
            return hex(calc_checksum)[2:].upper() == checksum.upper()
        except ValueError:
            return False

    def parse(self):
        raise NotImplementedError("Subclasses should implement this method!")
