"""
networking.py

Provides networking utility functions for values relating to networking such as IP addresses, rather
than actual client/server processes.
"""

import ipaddress
import socket


def is_valid_ipv4(address: str, allow_localhost: bool = True) -> bool:
    """
    Determines if the IP address provided is in valid IPv4 format. If allow_localhost, also accepts the
    string 'localhost' (this does not allow/prevent the usage of '127.0.0.1'). This function does not test
    if the IP address can be successfully connected to, however.

    Arguments:
        address: The IP address to test. A string is used as it can easily store an IPv4 address due to
            the periods.

        allow_localhost: Whether to allow the text 'localhost' or not. Defaults to True.

    Returns:
        A boolean specifying whether or not checks passed (True if IP is valid, otherwise False). A boolean
        is used as it easily represents if the checks were successful or not.
    """
    if address == "localhost" and allow_localhost:
        return True

    try:
        # Test by trying to initialize an IPv4 address. If it throws an error, assume IP is invalid.
        ipaddress.IPv4Address(address)
        return True
    except ipaddress.AddressValueError:
        return False


def get_ip_address() -> str | None:
    """
    Gets the IPv4 address of the current device, by retrieving the hostname of the current device
    and finding the IP address from it.

    Returns:
        The IPv4 address of the current device as a string, or None if it could not be found. A string
            is used as it can easily store an IPv4 address due to the periods.
    """
    try:
        # Get the hostname as provided by the device
        hostname = socket.gethostname()

        # Get the IP from the hostname
        ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        # If address resolution fails (can occur on macOS)
        ip = None

    return ip
