# validateIPv4.py

def valid_ipv4(ip):
    """
    This validates an IPv4 address based on a certain criteria. 
    It will return True if valid, and False otherwise.
    """
    
    # This must be a non-empty string
    if not isinstance(ip, str) or not ip:
        return False

    # This must contain exactly 4 octets
    parts = ip.split(".")
    if len(parts) != 4:
        return False

    octets = []
    for part in parts:
        # There should be no empty octets
        if part == "":
            return False

        # This must be digits only
        if not part.isdigit():
            return False

        # Each octet must be between 0 and 255
        value = int(part)
        if value < 0 or value > 255:
            return False
        octets.append(value)

    first, second, third, fourth = octets

    # Broadcast address
    if octets == [255, 255, 255, 255]:
        return False

    # Loopback addresses: 127.0.0.0 – 127.255.255.255
    if first == 127:
        return False

    # Link-local addresses: 169.254.0.0 – 169.254.255.255
    if first == 169 and second == 254:
        return False

    # Multicast addresses: 224.0.0.0 – 239.255.255.255
    if 224 <= first <= 239:
        return False

    # Reserved / Experimental addresses: 240.0.0.0 – 255.255.255.254
    if 240 <= first <= 255:
        return False

    return True

if __name__ == "__main__":
    main()