"""
DID resolver for aicache decentralized identity system
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
import json
import requests

from ..utils.logger import get_logger

logger = get_logger(__name__)

class DIDResolver:
    """Resolves decentralized identifiers (DIDs) to DID documents"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.did_documents = {}
        self.resolution_cache = {}
        self.supported_methods = []
        
    async def initialize(self):
        """Initialize the DID resolver"""
        logger.info("Initializing DID resolver")
        
        # Load resolver configuration
        self.resolver_config = self.config.get('resolver', {})
        self.default_resolution_timeout = self.resolver_config.get('resolution_timeout', 30)  # seconds
        self.cache_ttl = self.resolver_config.get('cache_ttl', 3600)  # 1 hour
        self.supported_methods = self.resolver_config.get('supported_methods', ['did:key', 'did:web'])
        
        # Initialize HTTP client for resolution
        self.http_client = requests.Session()
        self.http_client.timeout = self.default_resolution_timeout
        
        logger.info("DID resolver initialized")
        
    async def resolve_did(self, did: str) -> Optional[Dict[str, Any]]:
        """Resolve a DID to its DID document"""
        try:
            logger.info(f"Resolving DID: {did}")
            
            # Check cache first
            cached_document = await self._get_cached_document(did)
            if cached_document:
                logger.debug(f"Retrieved DID document from cache: {did}")
                return cached_document
                
            # Parse DID
            did_parts = did.split(':')
            if len(did_parts) < 3:
                logger.warning(f"Invalid DID format: {did}")
                return None
                
            did_method = f"{did_parts[0]}:{did_parts[1]}"
            method_specific_id = ':'.join(did_parts[2:])
            
            # Check if method is supported
            if did_method not in self.supported_methods:
                logger.warning(f"DID method {did_method} not supported")
                return None
                
            # Resolve based on method
            if did_method == 'did:key':
                document = await self._resolve_did_key(method_specific_id)
            elif did_method == 'did:web':
                document = await self._resolve_did_web(method_specific_id)
            else:
                # Try universal resolver
                document = await self._resolve_with_universal_resolver(did)
                
            # Cache document if resolved successfully
            if document:
                await self._cache_document(did, document)
                logger.info(f"Resolved DID document: {did}")
            else:
                logger.warning(f"Failed to resolve DID: {did}")
                
            return document
            
        except Exception as e:
            logger.error(f"Error resolving DID {did}: {e}")
            raise
            
    async def _get_cached_document(self, did: str) -> Optional[Dict[str, Any]]:
        """Get cached DID document"""
        try:
            # Check if document is cached
            if did in self.resolution_cache:
                cached_entry = self.resolution_cache[did]
                cached_document = cached_entry['document']
                cached_at = cached_entry['cached_at']
                
                # Check if cache is still valid
                current_time = datetime.now().timestamp()
                if current_time - cached_at < self.cache_ttl:
                    logger.debug(f"Using cached DID document for {did}")
                    return cached_document
                else:
                    # Remove expired cache entry
                    del self.resolution_cache[did]
                    logger.debug(f"Expired cached DID document removed for {did}")
                    
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached document: {e}")
            return None
            
    async def _cache_document(self, did: str, document: Dict[str, Any]):
        """Cache DID document"""
        try:
            # Store document in cache
            self.resolution_cache[did] = {
                'document': document,
                'cached_at': datetime.now().timestamp()
            }
            
            logger.debug(f"Cached DID document for {did}")
            
        except Exception as e:
            logger.error(f"Error caching document: {e}")
            
    async def _resolve_did_key(self, method_specific_id: str) -> Optional[Dict[str, Any]]:
        """Resolve did:key method"""
        try:
            logger.debug(f"Resolving did:key: {method_specific_id}")
            
            # For did:key, the method-specific ID is typically a multibase-encoded public key
            # In a real implementation, this would decode the key and create a DID document
            # For now, we'll create a mock DID document
            
            # Create mock DID document
            document = {
                '@context': [
                    'https://www.w3.org/ns/did/v1',
                    'https://w3id.org/security/suites/ed25519-2018/v1'
                ],
                'id': f'did:key:{method_specific_id}',
                'verificationMethod': [
                    {
                        'id': f'did:key:{method_specific_id}#{method_specific_id}',
                        'type': 'Ed25519VerificationKey2018',
                        'controller': f'did:key:{method_specific_id}',
                        'publicKeyBase58': method_specific_id
                    }
                ],
                'authentication': [
                    f'did:key:{method_specific_id}#{method_specific_id}'
                ],
                'assertionMethod': [
                    f'did:key:{method_specific_id}#{method_specific_id}'
                ],
                'capabilityDelegation': [
                    f'did:key:{method_specific_id}#{method_specific_id}'
                ],
                'capabilityInvocation': [
                    f'did:key:{method_specific_id}#{method_specific_id}'
                ],
                'keyAgreement': [
                    f'did:key:{method_specific_id}#{method_specific_id}'
                ]
            }
            
            logger.debug(f"Resolved did:key document for {method_specific_id}")
            return document
            
        except Exception as e:
            logger.error(f"Error resolving did:key {method_specific_id}: {e}")
            return None
            
    async def _resolve_did_web(self, method_specific_id: str) -> Optional[Dict[str, Any]]:
        """Resolve did:web method"""
        try:
            logger.debug(f"Resolving did:web: {method_specific_id}")
            
            # For did:web, the method-specific ID is a domain name
            # The DID document should be available at https://{domain}/.well-known/did.json
            domain = method_specific_id.replace(':', '/')
            url = f"https://{domain}/.well-known/did.json"
            
            try:
                # Fetch DID document
                response = self.http_client.get(url)
                response.raise_for_status()
                
                # Parse DID document
                document = response.json()
                
                logger.debug(f"Resolved did:web document for {method_specific_id}")
                return document
                
            except requests.RequestException as e:
                logger.warning(f"Failed to fetch did:web document from {url}: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error resolving did:web {method_specific_id}: {e}")
            return None
            
    async def _resolve_with_universal_resolver(self, did: str) -> Optional[Dict[str, Any]]:
        """Resolve DID using universal resolver"""
        try:
            logger.debug(f"Resolving {did} with universal resolver")
            
            # Use universal resolver service
            universal_resolver_url = self.resolver_config.get(
                'universal_resolver_url',
                'https://dev.uniresolver.io/1.0/identifiers/'
            )
            
            # Construct full URL
            url = f"{universal_resolver_url}{did}"
            
            try:
                # Fetch DID document
                response = self.http_client.get(url)
                response.raise_for_status()
                
                # Parse response
                resolver_response = response.json()
                document = resolver_response.get('didDocument')
                
                if document:
                    logger.debug(f"Resolved {did} with universal resolver")
                    return document
                else:
                    logger.warning(f"Universal resolver returned no DID document for {did}")
                    return None
                    
            except requests.RequestException as e:
                logger.warning(f"Failed to resolve {did} with universal resolver: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error using universal resolver for {did}: {e}")
            return None
            
    async def resolve_did_document(self, did: str) -> Optional[Dict[str, Any]]:
        """Resolve DID document (alias for resolve_did)"""
        return await self.resolve_did(did)
        
    async def get_supported_methods(self) -> List[str]:
        """Get list of supported DID methods"""
        return self.supported_methods.copy()
        
    async def add_supported_method(self, method: str) -> bool:
        """Add a supported DID method"""
        try:
            if method not in self.supported_methods:
                self.supported_methods.append(method)
                logger.info(f"Added supported DID method: {method}")
                return True
            else:
                logger.debug(f"DID method {method} already supported")
                return False
                
        except Exception as e:
            logger.error(f"Error adding supported method: {e}")
            raise
            
    async def remove_supported_method(self, method: str) -> bool:
        """Remove a supported DID method"""
        try:
            if method in self.supported_methods:
                self.supported_methods.remove(method)
                logger.info(f"Removed supported DID method: {method}")
                return True
            else:
                logger.debug(f"DID method {method} not supported")
                return False
                
        except Exception as e:
            logger.error(f"Error removing supported method: {e}")
            raise
            
    async def get_resolution_cache_info(self) -> Dict[str, Any]:
        """Get information about the resolution cache"""
        try:
            cache_info = {
                'cache_size': len(self.resolution_cache),
                'supported_methods': self.supported_methods.copy(),
                'cache_ttl': self.cache_ttl,
                'resolution_timeout': self.default_resolution_timeout
            }
            
            logger.debug("Retrieved resolution cache information")
            return cache_info
            
        except Exception as e:
            logger.error(f"Error getting cache info: {e}")
            raise
            
    async def clear_resolution_cache(self) -> bool:
        """Clear the resolution cache"""
        try:
            cache_size = len(self.resolution_cache)
            self.resolution_cache.clear()
            
            logger.info(f"Cleared resolution cache ({cache_size} entries)")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            raise
            
    async def get_did_verification_methods(self, did: str) -> List[Dict[str, Any]]:
        """Get verification methods for a DID"""
        try:
            # Resolve DID document
            document = await self.resolve_did(did)
            if not document:
                logger.warning(f"Could not resolve DID {did}")
                return []
                
            # Extract verification methods
            verification_methods = document.get('verificationMethod', [])
            
            logger.debug(f"Retrieved {len(verification_methods)} verification methods for {did}")
            return verification_methods
            
        except Exception as e:
            logger.error(f"Error getting verification methods for {did}: {e}")
            raise
            
    async def get_did_authentication_methods(self, did: str) -> List[str]:
        """Get authentication methods for a DID"""
        try:
            # Resolve DID document
            document = await self.resolve_did(did)
            if not document:
                logger.warning(f"Could not resolve DID {did}")
                return []
                
            # Extract authentication methods
            authentication_methods = document.get('authentication', [])
            
            logger.debug(f"Retrieved {len(authentication_methods)} authentication methods for {did}")
            return authentication_methods
            
        except Exception as e:
            logger.error(f"Error getting authentication methods for {did}: {e}")
            raise
            
    async def validate_did_document(self, document: Dict[str, Any]) -> bool:
        """Validate a DID document"""
        try:
            # Check required fields
            required_fields = ['@context', 'id']
            for field in required_fields:
                if field not in document:
                    logger.warning(f"Missing required field {field} in DID document")
                    return False
                    
            # Check context
            context = document['@context']
            if not isinstance(context, list):
                logger.warning("DID document @context must be a list")
                return False
                
            # Check ID format
            did = document['id']
            if not isinstance(did, str) or not did.startswith('did:'):
                logger.warning("DID document ID must be a valid DID")
                return False
                
            # Additional validation could include:
            # - Verification method validation
            # - Authentication method validation
            # - Service endpoint validation
            # - Signature validation
            
            logger.debug("DID document validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Error validating DID document: {e}")
            return False