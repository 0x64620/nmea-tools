from gga_message import GGAMessage
from rmc_message import RMCMessage
from gsv_message import GSVMessage
from nmea_message import NMEAMessage

def message_factory(raw_message):
    if raw_message.startswith('$GPGGA'):
        return GGAMessage(raw_message)
    elif raw_message.startswith('$GPRMC'):
        return RMCMessage(raw_message)
    elif raw_message.startswith('$GPGSV'):
        return GSVMessage(raw_message)
    else:
        return NMEAMessage(raw_message)
