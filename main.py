from ntp_client import NTPClient
from ntp_stats import NTPStats
import socket
import datetime
import struct
import threading
import time

NTD_IP = ["172.16.26.3", "172.16.26.4", "172.16.26.7", "172.16.26.9", "172.17.26.10", "172.16.26.11", "172.16.26.12", "172.16.26.13", "172.16.26.14", "172.16.26.15", "172.17.26.16", "172.17.26.17"]

log_file = "other_log.csv"


global timestamp



'''NTP Class Declaration'''

class NTPException(Exception):
    """Exception raised by this module."""
    pass


def _to_int(timestamp):
    """Return the integral part of a timestamp.

    Parameters:
    timestamp -- NTP timestamp

    Retuns:
    integral part
    """
    return int(timestamp)


# def _to_frac(timestamp, n=32):
#     """Return the fractional part of a timestamp.

#     Parameters:
#     timestamp -- NTP timestamp
#     n         -- number of bits of the fractional part

#     Retuns:
#     fractional part
#     """
#     return int(abs(timestamp - _to_int(timestamp)) * 2**n)


# def _to_time(integ, frac, n=32):
#     """Return a timestamp from an integral and fractional part.

#     Parameters:
#     integ -- integral part
#     frac  -- fractional part
#     n     -- number of bits of the fractional part

#     Retuns:
#     timestamp
#     """
#     return integ + float(frac)/2**n


# def ntp_to_system_time(timestamp):
#     """Convert a NTP time to system time.

#     Parameters:
#     timestamp -- timestamp in NTP time

#     Returns:
#     corresponding system time
#     """
#     return timestamp - NTP.NTP_DELTA


# def system_to_ntp_time(timestamp):
#     """Convert a system time to a NTP time.

#     Parameters:
#     timestamp -- timestamp in system time

#     Returns:
#     corresponding NTP time
#     """
#     return timestamp + NTP.NTP_DELTA


def leap_to_text(leap):
    """Convert a leap indicator to text.

    Parameters:
    leap -- leap indicator value

    Returns:
    corresponding message

    Raises:
    NTPException -- in case of invalid leap indicator
    """
    if leap in NTP.LEAP_TABLE:
        return NTP.LEAP_TABLE[leap]
    else:
        raise NTPException("Invalid leap indicator.")


def mode_to_text(mode):
    """Convert a NTP mode value to text.

    Parameters:
    mode -- NTP mode

    Returns:
    corresponding message

    Raises:
    NTPException -- in case of invalid mode
    """
    if mode in NTP.MODE_TABLE:
        return NTP.MODE_TABLE[mode]
    else:
        raise NTPException("Invalid mode.")


def stratum_to_text(stratum):
    """Convert a stratum value to text.

    Parameters:
    stratum -- NTP stratum

    Returns:
    corresponding message

    Raises:
    NTPException -- in case of invalid stratum
    """
    if stratum in NTP.STRATUM_TABLE:
        return NTP.STRATUM_TABLE[stratum] % (stratum)
    elif 1 < stratum < 16:
        return "secondary reference (%s)" % (stratum)
    elif stratum == 16:
        return "unsynchronized (%s)" % (stratum)
    else:
        raise NTPException("Invalid stratum or reserved.")


def ref_id_to_text(ref_id, stratum=2):
    """Convert a reference clock identifier to text according to its stratum.

    Parameters:
    ref_id  -- reference clock indentifier
    stratum -- NTP stratum

    Returns:
    corresponding message

    Raises:
    NTPException -- in case of invalid stratum
    """
    fields = (ref_id >> 24 & 0xff, ref_id >> 16 & 0xff,
              ref_id >> 8 & 0xff, ref_id & 0xff)

    # return the result as a string or dot-formatted IP address
    if 0 <= stratum <= 1:
        text = '%c%c%c%c' % fields
        if text in NTP.REF_ID_TABLE:
            return NTP.REF_ID_TABLE[text]
        else:
            return "Unidentified reference source '%s'" % (text)
    elif 2 <= stratum < 255:
        return '%d.%d.%d.%d' % fields
    else:
        raise NTPException("Invalid stratum.")

def get_ntp_time(host):
    port = 123; # Port.
    read_buffer = 1024; # The size of the buffer to read in the received UDP packet.
    address = ( host, port ); # Tuple needed by sendto.
    data = '\x1b' + 47 * '\0'; # Hex message to send to the server.

    epoch = 2208988800; # Time in seconds since Jan, 1970 for UNIX epoch.

    client = socket.socket( AF_INET, SOCK_DGRAM ); # Internet, UDP

    client.sendto( data, address ); # Aend the UDP packet to the server on the port.

    data, address = client.recvfrom( read_buffer ); # Get the response and put it in data and put the send socket address into address.

    t = struct.unpack( "!12I", data )[ 10 ]; # Unpack the binary data and get the seconds out.

    return t - epoch; # Calculate seconds since the epoch.

def send_time(host, data, server):
    global open_ntd_count, timestamp, var_log_file

    host_ip, server_port = host, 10000
    # Initialize a TCP client socket using SOCK_STREAM
    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     

    try:
        # Establish connection to TCP server and exchange data
        tcp_client.connect((host_ip, server_port))
        tcp_client.sendall(data)
     
        # Read data from the TCP server and close the connection
        received = tcp_client.recv(1024)

        var_log_file.write(str(datetime.datetime.now()) + "," + time.ctime(timestamp-bias) + "," + host + ",Synchronized" + "," + str(bias) + "\r\n")
    except Exception as e:
        var_log_file.write(str(datetime.datetime.now()) + "," + time.ctime(timestamp-bias) + ","  + host + ",Not Connected" + "," + str(bias) + "\r\n")
    finally:
        open_ntd_count-=1
        tcp_client.close()
    
def sync_ntd(server, hosts):

    global open_ntd_count, timestamp, var_log_file

    # print ("Please wait while getting time from ") + server + "\r\n"

    # ______________________________________________________________
    
    print("Please wait while getting time from", server, "\r\n")


    response = call.request(server, version=3)

    timestamp = round(response.tx_time + bias)

    # print ("NPLI NTP TIME: ") + time.ctime(timestamp) + "\r\n"

    # ______________________________________________________
    print("NPLI NTP TIME:", time.ctime(timestamp), "\r\n")


    ntp_date = datetime.datetime.fromtimestamp(timestamp)

    header = b'\x55\xaa\x00\x00\x01\x01\x00\xc1\x00\x00\x00\x00\x00\x00\x0f\x00\x00\x00\x0f\x00\x10\x00\x00\x00\x00\x00\x00\x00'
    footer = b'\x00\x00\x0d\x0a'

    year1 = bytes([ntp_date.year // 256])

    year2 = bytes([ntp_date.year % 256])
    
    data = header + year2 + year1 + bytes([ntp_date.month]) + bytes([ntp_date.day]) + bytes([ntp_date.hour]) + bytes([ntp_date.minute]) + bytes([ntp_date.second]) + footer


    
    for host in hosts:
        open_ntd_count += 1
        threading.Thread(target=send_time, args=(host, data, server)).start()


     
def loop():
    global open_ntd_count, var_log_file 
    while True:
        var_log_file = open(log_file, "a")
        open_ntd_count = 0

        sync_ntd(ntp_server_name, NTD_IP)
        while(open_ntd_count > 0):
            continue
        var_log_file.close()

        time.sleep(sync_time)

def start():
    global ntp_server_name, call, bias, sync_time
    ntp_server_name = input("Server: ")

    sync_time = 60 * int(input("Schedule Synchronization time (in minutes): "))

    bias = int(input("Bias (in Seconds): "))
    call = NTPClient()
    print("Synchronising NTD:-\n")
    for host in NTD_IP:
        print(host + "\n")

    try:
        loop()
    except Exception as e:
        print(e)
        print("Alert: unable to get NTP Time...")
        time.sleep(60)
        print("RESTARTING...")
        loop()

start()
