import hashlib


def get_hash_md5(file):
    m = hashlib.md5()
    while True:
        data = file.read(8192)
        if not data:
            break
        m.update(data)
    return m.hexdigest()

