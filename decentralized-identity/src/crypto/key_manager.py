"""
Key manager for aicache decentralized identity system
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
import base64
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

from ..utils.logger import get_logger

logger = get_logger(__name__)

class KeyManager:
    """Manages cryptographic keys for decentralized identities"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.keys = {}
        self.key_pairs = {}
        
    async def initialize(self):
        """Initialize the key manager"""
        logger.info("Initializing key manager")
        
        # Load key configuration
        self.key_config = self.config.get('crypto', {})
        self.default_key_algorithm = self.key_config.get('default_algorithm', 'ed25519')
        self.key_size = self.key_config.get('key_size', 2048)
        self.key_storage_path = self.key_config.get('storage_path', './keys')
        
        logger.info("Key manager initialized")
        
    async def generate_key_pair(
        self,
        algorithm: Optional[str] = None,
        key_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate a new key pair"""
        try:
            # Use default values if not specified
            if algorithm is None:
                algorithm = self.default_key_algorithm
            if key_size is None:
                key_size = self.key_size
                
            logger.info(f"Generating {algorithm} key pair with size {key_size}")
            
            # Generate key pair based on algorithm
            if algorithm.lower() == 'rsa':
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=key_size,
                    backend=default_backend()
                )
                public_key = private_key.public_key()
            elif algorithm.lower() == 'ed25519':
                private_key = ed25519.Ed25519PrivateKey.generate()
                public_key = private_key.public_key()
            else:
                # Default to Ed25519
                logger.warning(f"Unknown algorithm {algorithm}, defaulting to Ed25519")
                private_key = ed25519.Ed25519PrivateKey.generate()
                public_key = private_key.public_key()
                
            # Serialize keys
            if algorithm.lower() == 'rsa':
                private_pem = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                public_pem = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            else:  # Ed25519
                private_pem = private_key.private_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PrivateFormat.Raw
                )
                public_pem = public_key.public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw
                )
                
            # Create key pair record
            import uuid
            key_pair_id = str(uuid.uuid4())
            
            key_pair = {
                'id': key_pair_id,
                'algorithm': algorithm,
                'key_size': key_size,
                'private_key': base64.b64encode(private_pem).decode(),
                'public_key': base64.b64encode(public_pem).decode(),
                'created_at': datetime.now().isoformat(),
                'status': 'active'
            }
            
            # Store key pair
            self.key_pairs[key_pair_id] = key_pair
            
            logger.info(f"Generated {algorithm} key pair with ID {key_pair_id}")
            return key_pair
            
        except Exception as e:
            logger.error(f"Error generating key pair: {e}")
            raise
            
    async def get_key_pair(self, key_pair_id: str) -> Optional[Dict[str, Any]]:
        """Get a key pair by ID"""
        try:
            key_pair = self.key_pairs.get(key_pair_id)
            if key_pair:
                logger.debug(f"Retrieved key pair {key_pair_id}")
            else:
                logger.debug(f"Key pair {key_pair_id} not found")
            return key_pair
            
        except Exception as e:
            logger.error(f"Error getting key pair: {e}")
            raise
            
    async def get_public_key(self, key_pair_id: str) -> Optional[str]:
        """Get public key from key pair"""
        try:
            key_pair = self.key_pairs.get(key_pair_id)
            if key_pair:
                public_key = key_pair.get('public_key')
                logger.debug(f"Retrieved public key from key pair {key_pair_id}")
                return public_key
            else:
                logger.debug(f"Key pair {key_pair_id} not found")
                return None
                
        except Exception as e:
            logger.error(f"Error getting public key: {e}")
            raise
            
    async def sign_data(
        self,
        key_pair_id: str,
        data: bytes,
        algorithm: Optional[str] = None
    ) -> str:
        """Sign data with private key"""
        try:
            # Get key pair
            key_pair = self.key_pairs.get(key_pair_id)
            if not key_pair:
                logger.warning(f"Key pair {key_pair_id} not found")
                raise ValueError(f"Key pair {key_pair_id} not found")
                
            # Deserialize private key
            private_pem = base64.b64decode(key_pair['private_key'])
            
            if key_pair['algorithm'].lower() == 'rsa':
                private_key = serialization.load_pem_private_key(
                    private_pem,
                    password=None,
                    backend=default_backend()
                )
                signature = private_key.sign(
                    data,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
            else:  # Ed25519
                private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_pem)
                signature = private_key.sign(data)
                
            # Encode signature as base64
            signature_b64 = base64.b64encode(signature).decode()
            
            logger.debug(f"Signed data with key pair {key_pair_id}")
            return signature_b64
            
        except Exception as e:
            logger.error(f"Error signing data: {e}")
            raise
            
    async def verify_signature(
        self,
        public_key: str,
        data: bytes,
        signature_b64: str,
        algorithm: str = 'ed25519'
    ) -> bool:
        """Verify signature with public key"""
        try:
            # Decode signature
            signature = base64.b64decode(signature_b64)
            
            # Deserialize public key
            public_pem = base64.b64decode(public_key)
            
            if algorithm.lower() == 'rsa':
                public_key_obj = serialization.load_pem_public_key(
                    public_pem,
                    backend=default_backend()
                )
                try:
                    public_key_obj.verify(
                        signature,
                        data,
                        padding.PSS(
                            mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=padding.PSS.MAX_LENGTH
                        ),
                        hashes.SHA256()
                    )
                    return True
                except Exception:
                    return False
            else:  # Ed25519
                public_key_obj = ed25519.Ed25519PublicKey.from_public_bytes(public_pem)
                try:
                    public_key_obj.verify(signature, data)
                    return True
                except Exception:
                    return False
                    
        except Exception as e:
            logger.error(f"Error verifying signature: {e}")
            return False
            
    async def encrypt_data(
        self,
        public_key: str,
        data: bytes,
        algorithm: str = 'rsa'
    ) -> str:
        """Encrypt data with public key"""
        try:
            # Deserialize public key
            public_pem = base64.b64decode(public_key)
            
            if algorithm.lower() == 'rsa':
                public_key_obj = serialization.load_pem_public_key(
                    public_pem,
                    backend=default_backend()
                )
                encrypted_data = public_key_obj.encrypt(
                    data,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
            else:
                # For Ed25519, we can't encrypt directly, so we'll use a hybrid approach
                # In a real implementation, this would use a proper hybrid encryption scheme
                logger.warning(f"Direct encryption not supported for {algorithm}, using mock encryption")
                encrypted_data = data  # Mock encryption for demonstration
                
            # Encode encrypted data as base64
            encrypted_b64 = base64.b64encode(encrypted_data).decode()
            
            logger.debug(f"Encrypted data with {algorithm} public key")
            return encrypted_b64
            
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise
            
    async def decrypt_data(
        self,
        key_pair_id: str,
        encrypted_data_b64: str,
        algorithm: Optional[str] = None
    ) -> bytes:
        """Decrypt data with private key"""
        try:
            # Get key pair
            key_pair = self.key_pairs.get(key_pair_id)
            if not key_pair:
                logger.warning(f"Key pair {key_pair_id} not found")
                raise ValueError(f"Key pair {key_pair_id} not found")
                
            # Decode encrypted data
            encrypted_data = base64.b64decode(encrypted_data_b64)
            
            # Deserialize private key
            private_pem = base64.b64decode(key_pair['private_key'])
            
            if key_pair['algorithm'].lower() == 'rsa':
                private_key = serialization.load_pem_private_key(
                    private_pem,
                    password=None,
                    backend=default_backend()
                )
                decrypted_data = private_key.decrypt(
                    encrypted_data,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
            else:
                # For Ed25519, we can't decrypt directly, so we'll use a hybrid approach
                # In a real implementation, this would use a proper hybrid decryption scheme
                logger.warning(f"Direct decryption not supported for {key_pair['algorithm']}, using mock decryption")
                decrypted_data = encrypted_data  # Mock decryption for demonstration
                
            logger.debug(f"Decrypted data with {key_pair['algorithm']} private key")
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise
            
    async def rotate_key_pair(
        self,
        old_key_pair_id: str,
        new_algorithm: Optional[str] = None,
        new_key_size: Optional[int] = None
    ) -> str:
        """Rotate a key pair (generate new key pair to replace old one)"""
        try:
            # Check if old key pair exists
            if old_key_pair_id not in self.key_pairs:
                logger.warning(f"Old key pair {old_key_pair_id} not found")
                raise ValueError(f"Old key pair {old_key_pair_id} not found")
                
            # Generate new key pair
            new_key_pair = await self.generate_key_pair(new_algorithm, new_key_size)
            new_key_pair_id = new_key_pair['id']
            
            # Mark old key pair as rotated
            old_key_pair = self.key_pairs[old_key_pair_id]
            old_key_pair['status'] = 'rotated'
            old_key_pair['rotated_at'] = datetime.now().isoformat()
            old_key_pair['replaced_by'] = new_key_pair_id
            
            logger.info(f"Rotated key pair {old_key_pair_id} to {new_key_pair_id}")
            return new_key_pair_id
            
        except Exception as e:
            logger.error(f"Error rotating key pair: {e}")
            raise
            
    async def revoke_key_pair(self, key_pair_id: str) -> bool:
        """Revoke a key pair"""
        try:
            # Check if key pair exists
            if key_pair_id not in self.key_pairs:
                logger.warning(f"Key pair {key_pair_id} not found")
                return False
                
            # Mark key pair as revoked
            key_pair = self.key_pairs[key_pair_id]
            key_pair['status'] = 'revoked'
            key_pair['revoked_at'] = datetime.now().isoformat()
            
            logger.info(f"Revoked key pair {key_pair_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error revoking key pair: {e}")
            raise
            
    async def list_active_key_pairs(self) -> List[Dict[str, Any]]:
        """List all active key pairs"""
        try:
            active_key_pairs = [
                kp for kp in self.key_pairs.values()
                if kp['status'] == 'active'
            ]
            
            logger.info(f"Retrieved {len(active_key_pairs)} active key pairs")
            return active_key_pairs
            
        except Exception as e:
            logger.error(f"Error listing active key pairs: {e}")
            raise
            
    async def get_key_pair_info(self, key_pair_id: str) -> Dict[str, Any]:
        """Get detailed information about a key pair"""
        try:
            key_pair = self.key_pairs.get(key_pair_id)
            if not key_pair:
                logger.warning(f"Key pair {key_pair_id} not found")
                return {}
                
            # Create info dict without sensitive data
            info = {
                'id': key_pair['id'],
                'algorithm': key_pair['algorithm'],
                'key_size': key_pair['key_size'],
                'created_at': key_pair['created_at'],
                'status': key_pair['status'],
                'rotated_at': key_pair.get('rotated_at'),
                'revoked_at': key_pair.get('revoked_at')
            }
            
            logger.debug(f"Retrieved info for key pair {key_pair_id}")
            return info
            
        except Exception as e:
            logger.error(f"Error getting key pair info: {e}")
            raise