# ntp_stats.py
from ntp import NTP
from ntp_packet import NTPPacket, _to_time, _to_int


class NTPStats(NTPPacket):
    """NTP statistics.

    Wrapper for NTPPacket, offering additional statistics like offset and
    delay, and timestamps converted to system time.
    """

    def __init__(self):
        """Constructor."""
        NTPPacket.__init__(self)
        self.dest_timestamp = 0
        """destination timestamp"""

    @property
    def offset(self):
        """offset"""
        return ((self.recv_timestamp - self.orig_timestamp) +
                (self.tx_timestamp - self.dest_timestamp))/2

    @property
    def delay(self):
        """round-trip delay"""
        return ((self.dest_timestamp - self.orig_timestamp) -
                (self.tx_timestamp - self.recv_timestamp))

    @property
    def tx_time(self):
        """Transmit timestamp in system time."""
        return ntp_to_system_time(self.tx_timestamp)

    @property
    def recv_time(self):
        """Receive timestamp in system time."""
        return ntp_to_system_time(self.recv_timestamp)

    @property
    def orig_time(self):
        """Originate timestamp in system time."""
        return ntp_to_system_time(self.orig_timestamp)

    @property
    def ref_time(self):
        """Reference timestamp in system time."""
        return ntp_to_system_time(self.ref_timestamp)

    @property
    def dest_time(self):
        """Destination timestamp in system time."""
        return ntp_to_system_time(self.dest_timestamp)
    
    
def ntp_to_system_time(timestamp):
    """Convert a NTP time to system time.

    Parameters:
    timestamp -- timestamp in NTP time

    Returns:
    corresponding system time
    """
    return timestamp - NTP.NTP_DELTA