import json
try:
    import uhashlib as hashlib
except:
    import hashlib


def ljust(string, count, symbol):
    while len(string) < count:
        string += symbol
    return string


def translate(string, trans_type):
    trans = {
        'trans_36': bytes((x ^ 0x36) for x in range(256)),
        'trans_5C': bytes((x ^ 0x5C) for x in range(256))
    }
    s = [chr(trans[trans_type][i]) for i in string]
    return bytes(''.join(s), 'utf8')


def generate_signature(secret, expires, metod, path, data=None):
    """Generate a request signature compatible with BitMEX."""
    data = json.dumps(data) if data else ''
    message = metod + path + str(expires) + data
    key = ljust(bytes(secret, 'utf8'), 64, b'\0')

    inner = hashlib.sha256()
    inner.update(translate(key, 'trans_36'))
    inner.update(bytes(message, 'utf8'))

    outer = hashlib.sha256()
    outer.update(translate(key, 'trans_5C'))
    outer.update(inner.digest())

    return ''.join(['%.2x' % i for i in outer.digest()])
