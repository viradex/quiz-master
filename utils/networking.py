import ipaddress
import socket


def is_valid_ipv4(address):
    try:
        ipaddress.IPv4Address(address)
        return True
    except ipaddress.AddressValueError:
        return False


def get_ip_address():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return ip
