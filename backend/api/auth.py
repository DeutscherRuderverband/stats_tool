import os
from hashlib import sha256 as secure_hash_algorithm

def hashed(password: str, salt='drv_project_2023') -> str:
    payload = salt.encode() + password.encode('utf-8')
    return secure_hash_algorithm(payload).hexdigest()

MASTER_PASSWORD_HASHED = '17abb7a3b5198bd6fcdf88b2e37e459547efd55f154676cddb972c78a152f974'
if os.environ.get('BACKEND_MASTER_PASSWORD'):
    MASTER_PASSWORD_HASHED = hashed(os.environ.get('BACKEND_MASTER_PASSWORD'))

if __name__ == '__main__':
    pass_raw = input("Password to hash: ")
    pass_ = pass_raw.strip()
    hash_ = hashed(pass_)
    print(f'Hash for "{pass_}" is "{hash_}"')