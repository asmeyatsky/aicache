"""
Trust registry for aicache decentralized identity system
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
import json

from ..utils.logger import get_logger

logger = get_logger(__name__)

class TrustRegistry:
    """Manages trust relationships and verification for decentralized identities"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.trusted_issuers = {}
        self.revoked_credentials = {}
        self.trust_relationships = {}
        self.verification_policies = {}
        
    async def initialize(self):
        """Initialize the trust registry"""
        logger.info("Initializing trust registry")
        
        # Load trust configuration
        self.trust_config = self.config.get('trust', {})
        self.default_trust_level = self.trust_config.get('default_trust_level', 'medium')
        self.trust_storage_path = self.trust_config.get('storage_path', './trust')
        
        logger.info("Trust registry initialized")
        
    async def register_trusted_issuer(
        self,
        issuer_did: str,
        issuer_name: str,
        trust_level: str = 'medium',
        verification_method: str = 'manual',
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Register a trusted credential issuer"""
        try:
            logger.info(f"Registering trusted issuer: {issuer_name} ({issuer_did})")
            
            # Create issuer record
            issuer_record = {
                'did': issuer_did,
                'name': issuer_name,
                'trust_level': trust_level,
                'verification_method': verification_method,
                'registered_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'status': 'active',
                'metadata': metadata or {},
                'issued_credentials': 0,
                'revoked_credentials': 0
            }
            
            # Store issuer record
            self.trusted_issuers[issuer_did] = issuer_record
            
            logger.info(f"Registered trusted issuer: {issuer_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering trusted issuer: {e}")
            raise
            
    async def unregister_trusted_issuer(self, issuer_did: str) -> bool:
        """Unregister a trusted credential issuer"""
        try:
            # Check if issuer exists
            if issuer_did not in self.trusted_issuers:
                logger.warning(f"Trusted issuer {issuer_did} not found")
                return False
                
            # Mark issuer as inactive
            issuer_record = self.trusted_issuers[issuer_did]
            issuer_record['status'] = 'inactive'
            issuer_record['updated_at'] = datetime.now().isoformat()
            
            logger.info(f"Unregistered trusted issuer: {issuer_record['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Error unregistering trusted issuer: {e}")
            raise
            
    async def is_trusted_issuer(self, issuer_did: str) -> bool:
        """Check if an issuer is trusted"""
        try:
            issuer_record = self.trusted_issuers.get(issuer_did)
            if not issuer_record:
                logger.debug(f"Issuer {issuer_did} not found in trust registry")
                return False
                
            is_trusted = (
                issuer_record['status'] == 'active' and
                issuer_record['trust_level'] in ['high', 'medium']
            )
            
            logger.debug(f"Issuer {issuer_did} is {'trusted' if is_trusted else 'not trusted'}")
            return is_trusted
            
        except Exception as e:
            logger.error(f"Error checking trusted issuer: {e}")
            raise
            
    async def get_trusted_issuer(self, issuer_did: str) -> Optional[Dict[str, Any]]:
        """Get trusted issuer information"""
        try:
            issuer_record = self.trusted_issuers.get(issuer_did)
            if issuer_record:
                logger.debug(f"Retrieved trusted issuer: {issuer_record['name']}")
            else:
                logger.debug(f"Trusted issuer {issuer_did} not found")
            return issuer_record
            
        except Exception as e:
            logger.error(f"Error getting trusted issuer: {e}")
            raise
            
    async def list_trusted_issuers(self, trust_level: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all trusted issuers"""
        try:
            # Filter by trust level if specified
            if trust_level:
                issuers = [
                    issuer for issuer in self.trusted_issuers.values()
                    if issuer['trust_level'] == trust_level and issuer['status'] == 'active'
                ]
            else:
                issuers = [
                    issuer for issuer in self.trusted_issuers.values()
                    if issuer['status'] == 'active'
                ]
                
            logger.info(f"Retrieved {len(issuers)} trusted issuers")
            return issuers
            
        except Exception as e:
            logger.error(f"Error listing trusted issuers: {e}")
            raise
            
    async def revoke_credential(
        self,
        credential_id: str,
        issuer_did: str,
        reason: str = 'unspecified'
    ) -> bool:
        """Revoke a credential"""
        try:
            logger.info(f"Revoking credential {credential_id} issued by {issuer_did}")
            
            # Check if issuer is trusted
            if not await self.is_trusted_issuer(issuer_did):
                logger.warning(f"Issuer {issuer_did} is not trusted")
                return False
                
            # Create revocation record
            revocation_record = {
                'credential_id': credential_id,
                'issuer_did': issuer_did,
                'revoked_at': datetime.now().isoformat(),
                'reason': reason,
                'status': 'revoked'
            }
            
            # Store revocation record
            self.revoked_credentials[credential_id] = revocation_record
            
            # Update issuer statistics
            if issuer_did in self.trusted_issuers:
                issuer_record = self.trusted_issuers[issuer_did]
                issuer_record['revoked_credentials'] += 1
                issuer_record['updated_at'] = datetime.now().isoformat()
                
            logger.info(f"Revoked credential {credential_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error revoking credential: {e}")
            raise
            
    async def is_credential_revoked(self, credential_id: str) -> bool:
        """Check if a credential is revoked"""
        try:
            revocation_record = self.revoked_credentials.get(credential_id)
            if revocation_record:
                is_revoked = revocation_record['status'] == 'revoked'
                logger.debug(f"Credential {credential_id} is {'revoked' if is_revoked else 'not revoked'}")
                return is_revoked
            else:
                logger.debug(f"Credential {credential_id} not found in revocation registry")
                return False
                
        except Exception as e:
            logger.error(f"Error checking credential revocation: {e}")
            raise
            
    async def establish_trust_relationship(
        self,
        subject_did: str,
        trustee_did: str,
        trust_level: str = 'medium',
        relationship_type: str = 'peer',
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Establish a trust relationship between two identities"""
        try:
            logger.info(f"Establishing trust relationship between {subject_did} and {trustee_did}")
            
            # Create relationship ID
            relationship_id = hashlib.sha256(
                f"{subject_did}:{trustee_did}:{relationship_type}".encode()
            ).hexdigest()[:16]
            
            # Create trust relationship record
            relationship_record = {
                'id': relationship_id,
                'subject_did': subject_did,
                'trustee_did': trustee_did,
                'trust_level': trust_level,
                'relationship_type': relationship_type,
                'established_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'status': 'active',
                'metadata': metadata or {}
            }
            
            # Store relationship
            self.trust_relationships[relationship_id] = relationship_record
            
            logger.info(f"Established trust relationship {relationship_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error establishing trust relationship: {e}")
            raise
            
    async def verify_trust_relationship(
        self,
        subject_did: str,
        trustee_did: str,
        relationship_type: str = 'peer'
    ) -> Optional[Dict[str, Any]]:
        """Verify a trust relationship between two identities"""
        try:
            # Create relationship ID
            relationship_id = hashlib.sha256(
                f"{subject_did}:{trustee_did}:{relationship_type}".encode()
            ).hexdigest()[:16]
            
            # Get relationship record
            relationship_record = self.trust_relationships.get(relationship_id)
            if relationship_record and relationship_record['status'] == 'active':
                logger.debug(f"Verified trust relationship {relationship_id}")
                return relationship_record
            else:
                logger.debug(f"Trust relationship {relationship_id} not found or inactive")
                return None
                
        except Exception as e:
            logger.error(f"Error verifying trust relationship: {e}")
            raise
            
    async def configure_verification_policy(
        self,
        policy_name: str,
        policy_rules: Dict[str, Any],
        default_action: str = 'deny'
    ) -> bool:
        """Configure a verification policy"""
        try:
            logger.info(f"Configuring verification policy: {policy_name}")
            
            # Create policy record
            policy_record = {
                'name': policy_name,
                'rules': policy_rules,
                'default_action': default_action,
                'configured_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'status': 'active'
            }
            
            # Store policy
            self.verification_policies[policy_name] = policy_record
            
            logger.info(f"Configured verification policy: {policy_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error configuring verification policy: {e}")
            raise
            
    async def evaluate_verification_policy(
        self,
        policy_name: str,
        subject_did: str,
        credential: Dict[str, Any]
    ) -> bool:
        """Evaluate a verification policy against a subject and credential"""
        try:
            # Get policy
            policy_record = self.verification_policies.get(policy_name)
            if not policy_record:
                logger.warning(f"Verification policy {policy_name} not found")
                return False
                
            # Evaluate policy rules
            # In a real implementation, this would evaluate complex policy rules
            # For now, we'll simulate a simple evaluation
            
            import random
            
            # Simulate policy evaluation
            evaluation_result = random.random() > 0.3  # 70% chance of approval
            
            logger.debug(f"Evaluated verification policy {policy_name}: {'approved' if evaluation_result else 'denied'}")
            return evaluation_result
            
        except Exception as e:
            logger.error(f"Error evaluating verification policy: {e}")
            raise
            
    async def get_verification_statistics(self) -> Dict[str, Any]:
        """Get verification statistics"""
        try:
            # Calculate statistics
            total_issuers = len(self.trusted_issuers)
            active_issuers = len([
                issuer for issuer in self.trusted_issuers.values()
                if issuer['status'] == 'active'
            ])
            
            total_credentials = len(self.revoked_credentials)
            revoked_credentials = len([
                cred for cred in self.revoked_credentials.values()
                if cred['status'] == 'revoked'
            ])
            
            total_relationships = len(self.trust_relationships)
            active_relationships = len([
                rel for rel in self.trust_relationships.values()
                if rel['status'] == 'active'
            ])
            
            total_policies = len(self.verification_policies)
            active_policies = len([
                policy for policy in self.verification_policies.values()
                if policy['status'] == 'active'
            ])
            
            stats = {
                'trusted_issuers': {
                    'total': total_issuers,
                    'active': active_issuers,
                    'revoked_credentials': revoked_credentials,
                    'total_credentials': total_credentials
                },
                'trust_relationships': {
                    'total': total_relationships,
                    'active': active_relationships
                },
                'verification_policies': {
                    'total': total_policies,
                    'active': active_policies
                },
                'last_updated': datetime.now().isoformat()
            }
            
            logger.debug(f"Retrieved verification statistics")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting verification statistics: {e}")
            raise
            
    async def get_trust_report(self) -> Dict[str, Any]:
        """Get comprehensive trust report"""
        try:
            # Get verification statistics
            stats = await self.get_verification_statistics()
            
            # Get trust level distribution
            trust_levels = {}
            for issuer in self.trusted_issuers.values():
                level = issuer['trust_level']
                trust_levels[level] = trust_levels.get(level, 0) + 1
                
            # Get relationship types distribution
            relationship_types = {}
            for relationship in self.trust_relationships.values():
                rel_type = relationship['relationship_type']
                relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1
                
            # Get policy types distribution
            policy_types = {}
            for policy in self.verification_policies.values():
                # For now, we'll categorize by name patterns
                if 'high' in policy['name'].lower():
                    policy_type = 'high_security'
                elif 'medium' in policy['name'].lower():
                    policy_type = 'medium_security'
                elif 'low' in policy['name'].lower():
                    policy_type = 'low_security'
                else:
                    policy_type = 'general'
                    
                policy_types[policy_type] = policy_types.get(policy_type, 0) + 1
                
            report = {
                'statistics': stats,
                'trust_level_distribution': trust_levels,
                'relationship_types_distribution': relationship_types,
                'policy_types_distribution': policy_types,
                'generated_at': datetime.now().isoformat()
            }
            
            logger.debug(f"Generated trust report")
            return report
            
        except Exception as e:
            logger.error(f"Error generating trust report: {e}")
            raise