"""Ed25519 signing utilities."""

from pathlib import Path
from typing import Tuple

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


def generate_keypair() -> Tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    """Generate a new Ed25519 keypair."""
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key


def save_keypair(
    private_key: Ed25519PrivateKey,
    public_key: Ed25519PublicKey,
    key_path: Path,
    key_name: str,
) -> None:
    """Save keypair to disk."""
    private_key_path = key_path / f"{key_name}.pem"
    public_key_path = key_path / f"{key_name}.pub.pem"

    # Save private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    private_key_path.write_bytes(private_pem)

    # Save public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    public_key_path.write_bytes(public_pem)


def load_keypair(
    key_path: Path, key_name: str
) -> Tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    """Load keypair from disk."""
    private_key_path = key_path / f"{key_name}.pem"
    public_key_path = key_path / f"{key_name}.pub.pem"

    if not private_key_path.exists() or not public_key_path.exists():
        raise FileNotFoundError(f"Keypair not found at {key_path}")

    # Load private key
    private_pem = private_key_path.read_bytes()
    private_key = serialization.load_pem_private_key(
        private_pem, password=None
    )

    # Load public key
    public_pem = public_key_path.read_bytes()
    public_key = serialization.load_pem_public_key(public_pem)

    if not isinstance(private_key, Ed25519PrivateKey):
        raise ValueError("Private key is not Ed25519")
    if not isinstance(public_key, Ed25519PublicKey):
        raise ValueError("Public key is not Ed25519")

    return private_key, public_key


def sign_data(private_key: Ed25519PrivateKey, data: bytes) -> bytes:
    """Sign data with private key."""
    return private_key.sign(data)


def verify_signature(
    public_key: Ed25519PublicKey, signature: bytes, data: bytes
) -> bool:
    """Verify signature with public key."""
    try:
        public_key.verify(signature, data)
        return True
    except Exception:
        return False


def get_or_create_keypair(key_path: Path, key_name: str) -> Tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    """Get existing keypair or create a new one."""
    try:
        return load_keypair(key_path, key_name)
    except FileNotFoundError:
        private_key, public_key = generate_keypair()
        save_keypair(private_key, public_key, key_path, key_name)
        return private_key, public_key

