import socket

IP_ADDRESS = None


def get_ip_address():
    global IP_ADDRESS

    if IP_ADDRESS is None:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            IP_ADDRESS = s.getsockname()[0]
        except:
            IP_ADDRESS = "unavailable"
    return IP_ADDRESS
