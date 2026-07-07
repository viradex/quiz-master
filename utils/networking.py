import ipaddress
import socket


def is_valid_ipv4(address: str) -> bool:
    """Checks if the IP format is valid IPv4. Does not check if the IP can be connected to."""
    try:
        ipaddress.IPv4Address(address)
        return True
    except ipaddress.AddressValueError:
        return False


def get_ip_address() -> str | None:
    """Gets own device IP address. Returns None if the hostname cannot be resolved."""
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        ip = None

    return ip


def get_hostname(ip: str | None = None) -> str:
    """Gets hostname from external IP. If IP is None, retrieves own device hostname."""
    if ip is None:
        # Return own hostname
        return socket.gethostname()

    # Return IP's hostname
    try:
        # Perform reverse DNS lookup
        client_host = socket.gethostbyaddr(ip)
        hostname = client_host[0]
    except socket.herror:
        hostname = "N/A"

    return hostname
