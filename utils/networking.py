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


def get_hostname(ip=None):
    if ip is None:
        return socket.gethostname()

    try:
        client_host = socket.gethostbyaddr(ip)
        hostname = client_host[0]
    except socket.herror:
        hostname = "N/A"

    return hostname
