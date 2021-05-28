import binascii
import hmac
import hashlib
import base58
from ecdsa import SECP256k1
from ecdsa.ecdsa import Public_key
from eth_utils import keccak
import sys

seed = sys.argv[1]

# the HMAC-SHA512 `key` and `data` must be bytes:
seed_bytes = binascii.unhexlify(seed)

I = hmac.new(b'Bitcoin seed', seed_bytes, hashlib.sha512).digest()
L, R = I[:32], I[32:]

master_private_key = int.from_bytes(L, 'big')
master_chain_code = R

VERSION_BYTES = {
    'mainnet_public': binascii.unhexlify('0488b21e'),
    'mainnet_private': binascii.unhexlify('0488ade4'),
    'testnet_public': binascii.unhexlify('043587cf'),
    'testnet_private': binascii.unhexlify('04358394'),
}

version_bytes = VERSION_BYTES['mainnet_private']
depth_byte = b'\x00'
parent_fingerprint = b'\x00' * 4
child_number_bytes = b'\x00' * 4
key_bytes = b'\x00' + L

all_parts = (
    version_bytes,      # 4 bytes  
    depth_byte,         # 1 byte
    parent_fingerprint, # 4 bytes
    child_number_bytes, # 4 bytes
    master_chain_code,  # 32 bytes
    key_bytes,          # 33 bytes
)

all_bytes = b''.join(all_parts)
root_key = base58.b58encode_check(all_bytes).decode('utf8')

SECP256k1_GEN = SECP256k1.generator

def serialize_curve_point(p):
   x, y = p.x(), p.y()
   if y & 1:
      return b'\x03' + x.to_bytes(32, 'big')
   else:
      return b'\x02' + x.to_bytes(32, 'big')

def curve_point_from_int(k):
   return Public_key(SECP256k1_GEN, SECP256k1_GEN * k).point

def fingerprint_from_priv_key(k):
    K = curve_point_from_int(k)
    K_compressed = serialize_curve_point(K)
    identifier = hashlib.new(
      'ripemd160',
      hashlib.sha256(K_compressed).digest(),
    ).digest()
    return identifier[:4]

SECP256k1_ORD = SECP256k1.order

def derive_ext_private_key(private_key, chain_code, child_number):
    if child_number >= 2 ** 31:
        # Generate a hardened key
        data = b'\x00' + private_key.to_bytes(32, 'big')
    else:
        # Generate a non-hardened key
        p = curve_point_from_int(private_key)
        data = serialize_curve_point(p)

    data += child_number.to_bytes(4, 'big')

    hmac_bytes = hmac.new(chain_code, data, hashlib.sha512).digest()
    L, R = hmac_bytes[:32], hmac_bytes[32:]

    L_as_int = int.from_bytes(L, 'big')
    child_private_key = (L_as_int + private_key) % SECP256k1_ORD
    child_chain_code = R

    return (child_private_key, child_chain_code)

path_numbers = (2147483692, 2147483708, 2147483648, 0, 0)

depth = 0
parent_fingerprint = None
child_number = None
private_key = master_private_key
chain_code = master_chain_code

for i in path_numbers:
    depth += 1
    
    child_number = i
    
    parent_fingerprint = fingerprint_from_priv_key(private_key)
    
    private_key, chain_code = derive_ext_private_key(private_key, chain_code, i)

version_bytes = VERSION_BYTES['mainnet_private']
depth_byte = depth.to_bytes(1, 'big')
child_number_bytes = child_number.to_bytes(4, 'big')
key_bytes = b'\x00' + private_key.to_bytes(32, 'big')

all_parts = (
    version_bytes,      # 4 bytes  
    depth_byte,         # 1 byte
    parent_fingerprint, # 4 bytes
    child_number_bytes, # 4 bytes
    chain_code,         # 32 bytes
    key_bytes,          # 33 bytes
)
all_bytes = b''.join(all_parts)
extended_private_key = base58.b58encode_check(all_bytes).decode('utf8')

# Derive the public key Point:
p = curve_point_from_int(private_key)

# Serialize the Point, p
public_key_bytes = serialize_curve_point(p)

# Hash the concatenated x and y public key point values:
digest = keccak(p.x().to_bytes(32, 'big') + p.y().to_bytes(32, 'big'))

# Take the last 20 bytes and add '0x' to the front:
address = '0x' + digest[-20:].hex()

print(hex(private_key))
print(address)
sys.stdout.flush()

# print(f'address: {address}')
# print(f'private key: {hex(private_key)}')
# print(f'xprv: {extended_private_key}')
# print(f'master private key (hex): {hex(master_private_key)}')
# print(f'master chain code (bytes): {master_chain_code}')
# print(f'root key: {root_key}')