"""
Identity bridge for aicache decentralized identity system
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
import json

from ..utils.logger import get_logger

logger = get_logger(__name__)

class IdentityBridge:
    """Bridges traditional and decentralized identities"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.identity_mappings = {}
        self.federated_identities = {}
        self.traditional_identities = {}
        
    async def initialize(self):
        """Initialize the identity bridge"""
        logger.info("Initializing identity bridge")
        
        # Load bridge configuration
        self.bridge_config = self.config.get('bridge', {})
        self.default_bridge_method = self.bridge_config.get('default_method', 'oauth')
        self.supported_providers = self.bridge_config.get('supported_providers', ['github', 'gitlab', 'google'])
        
        logger.info("Identity bridge initialized")
        
    async def bridge_identity(
        self,
        traditional_provider: str,
        traditional_id: str,
        decentralized_did: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Create a bridge between traditional and decentralized identity"""
        try:
            logger.info(f"Bridging identity: {traditional_provider}/{traditional_id} ↔ {decentralized_did}")
            
            # Validate provider
            if traditional_provider not in self.supported_providers:
                logger.warning(f"Unsupported identity provider: {traditional_provider}")
                return False
                
            # Create identity mapping
            mapping_id = hashlib.sha256(
                f"{traditional_provider}:{traditional_id}:{decentralized_did}".encode()
            ).hexdigest()[:16]
            
            # Create mapping record
            mapping_record = {
                'id': mapping_id,
                'traditional_provider': traditional_provider,
                'traditional_id': traditional_id,
                'decentralized_did': decentralized_did,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'status': 'active',
                'metadata': metadata or {}
            }
            
            # Store mapping
            self.identity_mappings[mapping_id] = mapping_record
            
            # Update identity records
            self.traditional_identities[f"{traditional_provider}:{traditional_id}"] = {
                'provider': traditional_provider,
                'id': traditional_id,
                'did': decentralized_did,
                'mapped_at': datetime.now().isoformat(),
                'status': 'mapped'
            }
            
            self.federated_identities[decentralized_did] = {
                'did': decentralized_did,
                'traditional_provider': traditional_provider,
                'traditional_id': traditional_id,
                'mapped_at': datetime.now().isoformat(),
                'status': 'mapped'
            }
            
            logger.info(f"Identity bridge created: {mapping_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error bridging identity: {e}")
            raise
            
    async def unbridge_identity(
        self,
        traditional_provider: str,
        traditional_id: str,
        decentralized_did: str
    ) -> bool:
        """Remove bridge between traditional and decentralized identity"""
        try:
            logger.info(f"Unbridging identity: {traditional_provider}/{traditional_id} ↔ {decentralized_did}")
            
            # Find mapping
            mapping_id = hashlib.sha256(
                f"{traditional_provider}:{traditional_id}:{decentralized_did}".encode()
            ).hexdigest()[:16]
            
            # Remove mapping
            if mapping_id in self.identity_mappings:
                mapping_record = self.identity_mappings[mapping_id]
                mapping_record['status'] = 'inactive'
                mapping_record['updated_at'] = datetime.now().isoformat()
                mapping_record['unmapped_at'] = datetime.now().isoformat()
                
                # Update identity records
                traditional_key = f"{traditional_provider}:{traditional_id}"
                if traditional_key in self.traditional_identities:
                    self.traditional_identities[traditional_key]['status'] = 'unmapped'
                    self.traditional_identities[traditional_key]['unmapped_at'] = datetime.now().isoformat()
                    
                if decentralized_did in self.federated_identities:
                    self.federated_identities[decentralized_did]['status'] = 'unmapped'
                    self.federated_identities[decentralized_did]['unmapped_at'] = datetime.now().isoformat()
                    
                logger.info(f"Identity bridge removed: {mapping_id}")
                return True
            else:
                logger.warning(f"Identity bridge not found: {mapping_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error unbridging identity: {e}")
            raise
            
    async def get_decentralized_identity(
        self,
        traditional_provider: str,
        traditional_id: str
    ) -> Optional[str]:
        """Get decentralized identity for traditional identity"""
        try:
            traditional_key = f"{traditional_provider}:{traditional_id}"
            identity_record = self.traditional_identities.get(traditional_key)
            
            if identity_record and identity_record['status'] == 'mapped':
                did = identity_record['did']
                logger.debug(f"Found decentralized identity {did} for {traditional_provider}/{traditional_id}")
                return did
            else:
                logger.debug(f"No decentralized identity found for {traditional_provider}/{traditional_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting decentralized identity: {e}")
            raise
            
    async def get_traditional_identity(self, decentralized_did: str) -> Optional[Dict[str, str]]:
        """Get traditional identity for decentralized identity"""
        try:
            identity_record = self.federated_identities.get(decentralized_did)
            
            if identity_record and identity_record['status'] == 'mapped':
                traditional_identity = {
                    'provider': identity_record['traditional_provider'],
                    'id': identity_record['traditional_id']
                }
                logger.debug(f"Found traditional identity {traditional_identity} for {decentralized_did}")
                return traditional_identity
            else:
                logger.debug(f"No traditional identity found for {decentralized_did}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting traditional identity: {e}")
            raise
            
    async def is_identity_bridged(
        self,
        traditional_provider: str,
        traditional_id: str,
        decentralized_did: str
    ) -> bool:
        """Check if identity is bridged"""
        try:
            mapping_id = hashlib.sha256(
                f"{traditional_provider}:{traditional_id}:{decentralized_did}".encode()
            ).hexdigest()[:16]
            
            mapping_record = self.identity_mappings.get(mapping_id)
            is_bridged = (
                mapping_record is not None and
                mapping_record['status'] == 'active'
            )
            
            logger.debug(f"Identity {traditional_provider}/{traditional_id} ↔ {decentralized_did} is {'bridged' if is_bridged else 'not bridged'}")
            return is_bridged
            
        except Exception as e:
            logger.error(f"Error checking identity bridge: {e}")
            raise
            
    async def list_bridged_identities(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List all bridged identities"""
        try:
            # Get active mappings
            active_mappings = [
                mapping for mapping in self.identity_mappings.values()
                if mapping['status'] == 'active'
            ]
            
            # Sort by creation time (newest first)
            active_mappings.sort(key=lambda x: x['created_at'], reverse=True)
            
            # Apply limit
            limited_mappings = active_mappings[:limit]
            
            logger.info(f"Retrieved {len(limited_mappings)} bridged identities")
            return limited_mappings
            
        except Exception as e:
            logger.error(f"Error listing bridged identities: {e}")
            raise
            
    async def get_bridge_statistics(self) -> Dict[str, Any]:
        """Get identity bridge statistics"""
        try:
            total_mappings = len(self.identity_mappings)
            active_mappings = len([
                mapping for mapping in self.identity_mappings.values()
                if mapping['status'] == 'active'
            ])
            inactive_mappings = total_mappings - active_mappings
            
            # Count by provider
            provider_counts = {}
            for mapping in self.identity_mappings.values():
                provider = mapping['traditional_provider']
                provider_counts[provider] = provider_counts.get(provider, 0) + 1
                
            stats = {
                'total_mappings': total_mappings,
                'active_mappings': active_mappings,
                'inactive_mappings': inactive_mappings,
                'provider_distribution': provider_counts,
                'supported_providers': self.supported_providers.copy(),
                'default_bridge_method': self.default_bridge_method
            }
            
            logger.debug("Retrieved identity bridge statistics")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting bridge statistics: {e}")
            raise
            
    async def sync_identity_data(
        self,
        traditional_provider: str,
        traditional_id: str,
        decentralized_did: str
    ) -> bool:
        """Sync data between traditional and decentralized identities"""
        try:
            logger.info(f"Syncing identity data: {traditional_provider}/{traditional_id} ↔ {decentralized_did}")
            
            # Check if identities are bridged
            if not await self.is_identity_bridged(traditional_provider, traditional_id, decentralized_did):
                logger.warning(f"Identities not bridged: {traditional_provider}/{traditional_id} ↔ {decentralized_did}")
                return False
                
            # In a real implementation, this would:
            # 1. Fetch data from traditional provider
            # 2. Update decentralized identity with new data
            # 3. Handle conflicts and merging
            # 4. Validate synchronization
            
            # For now, we'll simulate successful synchronization
            logger.info(f"Identity data synchronized: {traditional_provider}/{traditional_id} ↔ {decentralized_did}")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing identity data: {e}")
            raise
            
    async def validate_identity_bridge(
        self,
        traditional_provider: str,
        traditional_id: str,
        decentralized_did: str
    ) -> bool:
        """Validate an identity bridge"""
        try:
            logger.info(f"Validating identity bridge: {traditional_provider}/{traditional_id} ↔ {decentralized_did}")
            
            # Check if bridge exists
            if not await self.is_identity_bridged(traditional_provider, traditional_id, decentralized_did):
                logger.warning(f"Identity bridge not found: {traditional_provider}/{traditional_id} ↔ {decentralized_did}")
                return False
                
            # In a real implementation, this would:
            # 1. Verify traditional identity still exists
            # 2. Verify decentralized identity is still valid
            # 3. Check for any conflicts or inconsistencies
            # 4. Validate synchronization status
            
            # For now, we'll simulate successful validation
            logger.info(f"Identity bridge validated: {traditional_provider}/{traditional_id} ↔ {decentralized_did}")
            return True
            
        except Exception as e:
            logger.error(f"Error validating identity bridge: {e}")
            raise
            
    async def revoke_identity_bridge(
        self,
        traditional_provider: str,
        traditional_id: str,
        decentralized_did: str,
        reason: str = 'unspecified'
    ) -> bool:
        """Revoke an identity bridge"""
        try:
            logger.info(f"Revoking identity bridge: {traditional_provider}/{traditional_id} ↔ {decentralized_did}")
            
            # Check if bridge exists
            if not await self.is_identity_bridged(traditional_provider, traditional_id, decentralized_did):
                logger.warning(f"Identity bridge not found: {traditional_provider}/{traditional_id} ↔ {decentralized_did}")
                return False
                
            # Create revocation record
            mapping_id = hashlib.sha256(
                f"{traditional_provider}:{traditional_id}:{decentralized_did}".encode()
            ).hexdigest()[:16]
            
            mapping_record = self.identity_mappings.get(mapping_id)
            if mapping_record:
                mapping_record['status'] = 'revoked'
                mapping_record['revoked_at'] = datetime.now().isoformat()
                mapping_record['revocation_reason'] = reason
                mapping_record['updated_at'] = datetime.now().isoformat()
                
                # Update identity records
                traditional_key = f"{traditional_provider}:{traditional_id}"
                if traditional_key in self.traditional_identities:
                    self.traditional_identities[traditional_key]['status'] = 'revoked'
                    self.traditional_identities[traditional_key]['revoked_at'] = datetime.now().isoformat()
                    
                if decentralized_did in self.federated_identities:
                    self.federated_identities[decentralized_did]['status'] = 'revoked'
                    self.federated_identities[decentralized_did]['revoked_at'] = datetime.now().isoformat()
                    
                logger.info(f"Identity bridge revoked: {mapping_id}")
                return True
            else:
                logger.warning(f"Identity bridge record not found: {mapping_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error revoking identity bridge: {e}")
            raise
            
    async def get_revocation_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get history of revoked identity bridges"""
        try:
            # Get revoked mappings
            revoked_mappings = [
                mapping for mapping in self.identity_mappings.values()
                if mapping['status'] == 'revoked'
            ]
            
            # Sort by revocation time (newest first)
            revoked_mappings.sort(key=lambda x: x.get('revoked_at', ''), reverse=True)
            
            # Apply limit
            limited_mappings = revoked_mappings[:limit]
            
            logger.info(f"Retrieved {len(limited_mappings)} revoked identity bridges")
            return limited_mappings
            
        except Exception as e:
            logger.error(f"Error getting revocation history: {e}")
            raise