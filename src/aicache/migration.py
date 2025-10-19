"""
Migration tools and backward compatibility for aicache.
"""

import os
import json
import sqlite3
import hashlib
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)

@dataclass
class MigrationResult:
    """Result of a migration operation."""
    success: bool
    migrated_count: int
    errors: List[str]
    warnings: List[str]
    duration: float
    source_version: str
    target_version: str

class LegacyCacheReader:
    """Reads cache entries from legacy formats."""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
    
    def detect_cache_format(self) -> str:
        """Detect the format of existing cache."""
        if not self.cache_dir.exists():
            return "none"
        
        # Check for SQLite database (enhanced format)
        if (self.cache_dir / "cache.db").exists():
            return "enhanced"
        
        # Check for JSON files (original format)
        json_files = list(self.cache_dir.glob("*.json"))
        if json_files:
            return "json"
        
        # Check for individual cache files (original format)
        cache_files = [f for f in self.cache_dir.iterdir() 
                      if f.is_file() and len(f.name) == 64]  # SHA256 length
        if cache_files:
            return "original"
        
        return "unknown"
    
    def read_original_format(self) -> List[Dict[str, Any]]:
        """Read cache entries from original JSON file format."""
        entries = []
        
        for cache_file in self.cache_dir.iterdir():
            if cache_file.is_file() and len(cache_file.name) == 64:  # SHA256 hash
                try:
                    with open(cache_file) as f:
                        data = json.load(f)
                        
                    # Convert to standard format
                    entry = {
                        'cache_key': cache_file.name,
                        'prompt': data.get('prompt', ''),
                        'response': data.get('response', ''),
                        'context': data.get('context', {}),
                        'timestamp': data.get('timestamp', os.path.getctime(cache_file)),
                        'access_count': 0,
                        'last_accessed': data.get('timestamp', os.path.getctime(cache_file)),
                        'legacy_format': 'original'
                    }
                    entries.append(entry)
                    
                except Exception as e:
                    logger.error(f"Failed to read legacy cache file {cache_file}: {e}")
        
        return entries
    
    def read_json_format(self) -> List[Dict[str, Any]]:
        """Read cache entries from consolidated JSON format."""
        entries = []
        
        for json_file in self.cache_dir.glob("*.json"):
            try:
                with open(json_file) as f:
                    data = json.load(f)
                
                # Handle different JSON formats
                if isinstance(data, list):
                    # Array of entries
                    entries.extend(data)
                elif isinstance(data, dict):
                    if 'entries' in data:
                        # Structured format with entries array
                        entries.extend(data['entries'])
                    else:
                        # Single entry
                        entries.append(data)
                        
            except Exception as e:
                logger.error(f"Failed to read JSON cache file {json_file}: {e}")
        
        # Normalize entries
        normalized_entries = []
        for entry in entries:
            normalized = {
                'cache_key': entry.get('cache_key', hashlib.sha256(
                    f"{entry.get('prompt', '')}:{json.dumps(entry.get('context', {}), sort_keys=True)}"
                    .encode()).hexdigest()),
                'prompt': entry.get('prompt', ''),
                'response': entry.get('response', ''),
                'context': entry.get('context', {}),
                'timestamp': entry.get('timestamp', time.time()),
                'access_count': entry.get('access_count', 0),
                'last_accessed': entry.get('last_accessed', entry.get('timestamp', time.time())),
                'legacy_format': 'json'
            }
            normalized_entries.append(normalized)
        
        return normalized_entries

class CacheMigrator:
    """Handles migration between different cache formats."""
    
    def __init__(self, source_cache_dir: Path, target_cache_dir: Path = None):
        self.source_cache_dir = source_cache_dir
        self.target_cache_dir = target_cache_dir or source_cache_dir
        self.reader = LegacyCacheReader(source_cache_dir)
    
    def migrate_to_enhanced(self) -> MigrationResult:
        """Migrate legacy cache to enhanced format."""
        start_time = time.time()
        result = MigrationResult(
            success=False,
            migrated_count=0,
            errors=[],
            warnings=[],
            duration=0.0,
            source_version="unknown",
            target_version="enhanced"
        )
        
        try:
            # Detect source format
            source_format = self.reader.detect_cache_format()
            result.source_version = source_format
            
            if source_format == "enhanced":
                result.warnings.append("Cache is already in enhanced format")
                result.success = True
                return result
            
            if source_format == "none":
                result.warnings.append("No cache found to migrate")
                result.success = True
                return result
            
            # Read legacy entries
            if source_format == "original":
                entries = self.reader.read_original_format()
            elif source_format == "json":
                entries = self.reader.read_json_format()
            else:
                result.errors.append(f"Unknown source format: {source_format}")
                return result
            
            if not entries:
                result.warnings.append("No cache entries found to migrate")
                result.success = True
                return result
            
            # Create backup
            backup_dir = self.source_cache_dir.parent / f"aicache_backup_{int(time.time())}"
            try:
                shutil.copytree(self.source_cache_dir, backup_dir)
                logger.info(f"Created backup at {backup_dir}")
            except Exception as e:
                result.warnings.append(f"Failed to create backup: {e}")
            
            # Initialize target database
            db_path = self.target_cache_dir / "cache.db"
            self.target_cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Create enhanced database schema
            self._create_enhanced_schema(db_path)
            
            # Migrate entries
            with sqlite3.connect(db_path) as conn:
                migrated = 0
                for entry in entries:
                    try:
                        # Compress response (simple approach)
                        import zlib
                        response_bytes = entry['response'].encode('utf-8')
                        compressed_response = zlib.compress(response_bytes)
                        compression_ratio = len(compressed_response) / len(response_bytes) if response_bytes else 1.0
                        
                        # Insert into database
                        conn.execute('''
                            INSERT OR REPLACE INTO cache_entries 
                            (cache_key, prompt, response, context, timestamp, access_count, 
                             last_accessed, response_size, compression_ratio, cost_estimate, priority_score)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            entry['cache_key'],
                            entry['prompt'],
                            compressed_response,
                            json.dumps(entry['context']),
                            entry['timestamp'],
                            entry['access_count'],
                            entry['last_accessed'],
                            len(response_bytes),
                            compression_ratio,
                            1.0,  # Default cost estimate
                            0.0   # Default priority score
                        ))
                        migrated += 1
                        
                    except Exception as e:
                        result.errors.append(f"Failed to migrate entry {entry.get('cache_key', 'unknown')}: {e}")
                
                conn.commit()
                result.migrated_count = migrated
            
            # Clean up old format files if migration successful
            if migrated > 0:
                try:
                    self._cleanup_legacy_files(source_format)
                except Exception as e:
                    result.warnings.append(f"Failed to clean up legacy files: {e}")
            
            result.success = True
            logger.info(f"Successfully migrated {migrated} cache entries")
            
        except Exception as e:
            result.errors.append(f"Migration failed: {str(e)}")
            logger.error(f"Migration error: {e}")
        
        result.duration = time.time() - start_time
        return result
    
    def _create_enhanced_schema(self, db_path: Path):
        """Create enhanced database schema."""
        with sqlite3.connect(db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache_entries (
                    cache_key TEXT PRIMARY KEY,
                    prompt TEXT NOT NULL,
                    response BLOB NOT NULL,
                    context TEXT,
                    timestamp REAL NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    last_accessed REAL,
                    response_size INTEGER,
                    compression_ratio REAL DEFAULT 1.0,
                    semantic_tags TEXT,
                    cost_estimate REAL DEFAULT 1.0,
                    priority_score REAL DEFAULT 0.0
                )
            ''')
            
            conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON cache_entries(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_entries(last_accessed)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_priority ON cache_entries(priority_score DESC)')
            conn.commit()
    
    def _cleanup_legacy_files(self, source_format: str):
        """Clean up legacy cache files after successful migration."""
        if source_format == "original":
            # Remove individual cache files
            for cache_file in self.source_cache_dir.iterdir():
                if cache_file.is_file() and len(cache_file.name) == 64:
                    cache_file.unlink()
        
        elif source_format == "json":
            # Remove JSON cache files
            for json_file in self.source_cache_dir.glob("*.json"):
                json_file.unlink()

class ConfigMigrator:
    """Handles migration of configuration files."""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
    
    def migrate_config(self) -> MigrationResult:
        """Migrate configuration to latest format."""
        start_time = time.time()
        result = MigrationResult(
            success=False,
            migrated_count=0,
            errors=[],
            warnings=[],
            duration=0.0,
            source_version="unknown",
            target_version="latest"
        )
        
        config_file = self.config_dir / "config.yaml"
        
        try:
            if not config_file.exists():
                result.warnings.append("No config file found to migrate")
                result.success = True
                return result
            
            # Read current config
            import yaml
            with open(config_file) as f:
                current_config = yaml.safe_load(f) or {}
            
            # Detect version (simple heuristic)
            if 'semantic_cache' in current_config:
                result.source_version = "enhanced"
                result.warnings.append("Config is already in enhanced format")
                result.success = True
                return result
            
            result.source_version = "legacy"
            
            # Create backup
            backup_file = config_file.with_suffix(f'.yaml.backup.{int(time.time())}')
            shutil.copy2(config_file, backup_file)
            
            # Migrate to new format
            from .config import DEFAULT_CONFIG
            
            # Map legacy settings to new structure
            migrated_config = DEFAULT_CONFIG.copy()
            
            # Basic settings
            if 'cache_dir' in current_config:
                migrated_config['cache_dir'] = current_config['cache_dir']
            if 'ttl' in current_config:
                migrated_config['ttl'] = current_config['ttl']
            if 'cache_size_limit' in current_config:
                migrated_config['cache_size_limit'] = current_config['cache_size_limit']
            
            # Enable new features by default for migrated configs (except analytics for privacy)
            migrated_config['semantic_cache']['enabled'] = True
            migrated_config['intelligent_management']['enabled'] = True
            migrated_config['analytics']['enabled'] = False  # Changed to False for privacy
            
            # Save migrated config
            with open(config_file, 'w') as f:
                yaml.dump(migrated_config, f, default_flow_style=False, indent=2)
            
            result.migrated_count = 1
            result.success = True
            logger.info("Successfully migrated configuration file")
            
        except Exception as e:
            result.errors.append(f"Config migration failed: {str(e)}")
            logger.error(f"Config migration error: {e}")
        
        result.duration = time.time() - start_time
        return result

class BackwardCompatibilityLayer:
    """Ensures backward compatibility with legacy interfaces."""
    
    def __init__(self, enhanced_cache):
        self.enhanced_cache = enhanced_cache
    
    def get_legacy_format(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cache entry in legacy format."""
        entry = self.enhanced_cache.inspect(cache_key)
        if not entry:
            return None
        
        # Convert to legacy format
        return {
            'prompt': entry['prompt'],
            'response': entry['response'],
            'context': entry['context'],
            'timestamp': entry['timestamp']
        }
    
    def set_legacy_format(self, prompt: str, response: str, context: Dict[str, Any] = None) -> str:
        """Set cache entry using legacy interface."""
        return self.enhanced_cache.set(prompt, response, context)
    
    def list_legacy_format(self) -> List[str]:
        """List cache keys in legacy format."""
        return self.enhanced_cache.list(verbose=False)
    
    def stats_legacy_format(self) -> Dict[str, Any]:
        """Get stats in legacy format."""
        enhanced_stats = self.enhanced_cache.get_stats()
        
        # Convert to legacy format
        storage = enhanced_stats.get('storage', {})
        return {
            'num_entries': storage.get('total_entries', 0),
            'total_size': storage.get('total_size', 0),
            'num_expired': storage.get('expired_entries', 0)
        }

class MigrationManager:
    """Manages all migration operations."""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_migrator = CacheMigrator(cache_dir)
        self.config_migrator = ConfigMigrator(cache_dir.parent / ".config" / "aicache")
    
    def run_full_migration(self) -> Dict[str, MigrationResult]:
        """Run complete migration process."""
        results = {}
        
        logger.info("Starting full migration process...")
        
        # Migrate cache data
        logger.info("Migrating cache data...")
        results['cache'] = self.cache_migrator.migrate_to_enhanced()
        
        # Migrate configuration
        logger.info("Migrating configuration...")
        results['config'] = self.config_migrator.migrate_config()
        
        # Summary
        total_success = all(result.success for result in results.values())
        total_migrated = sum(result.migrated_count for result in results.values())
        total_errors = sum(len(result.errors) for result in results.values())
        
        logger.info(f"Migration complete. Success: {total_success}, "
                   f"Migrated: {total_migrated}, Errors: {total_errors}")
        
        return results
    
    def check_migration_needed(self) -> Dict[str, bool]:
        """Check if migration is needed for different components."""
        cache_format = self.cache_migrator.reader.detect_cache_format()
        config_file = self.config_migrator.config_dir / "config.yaml"
        
        needs_cache_migration = cache_format not in ["enhanced", "none"]
        needs_config_migration = False
        
        if config_file.exists():
            try:
                import yaml
                with open(config_file) as f:
                    config = yaml.safe_load(f) or {}
                needs_config_migration = 'semantic_cache' not in config
            except Exception:
                needs_config_migration = True
        
        return {
            'cache': needs_cache_migration,
            'config': needs_config_migration,
            'any': needs_cache_migration or needs_config_migration
        }
    
    def generate_migration_report(self, results: Dict[str, MigrationResult]) -> str:
        """Generate a detailed migration report."""
        report = []
        report.append("# aicache Migration Report")
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        for component, result in results.items():
            report.append(f"## {component.title()} Migration")
            report.append(f"- Success: {'✅' if result.success else '❌'}")
            report.append(f"- Source Version: {result.source_version}")
            report.append(f"- Target Version: {result.target_version}")
            report.append(f"- Migrated Items: {result.migrated_count}")
            report.append(f"- Duration: {result.duration:.2f}s")
            
            if result.errors:
                report.append("### Errors:")
                for error in result.errors:
                    report.append(f"- ❌ {error}")
            
            if result.warnings:
                report.append("### Warnings:")
                for warning in result.warnings:
                    report.append(f"- ⚠️ {warning}")
            
            report.append("")
        
        return "\n".join(report)

# CLI command for migration
def run_migration_cli(cache_dir: str = None):
    """CLI entry point for migration."""
    cache_path = Path(cache_dir) if cache_dir else Path.home() / ".cache" / "aicache"
    
    manager = MigrationManager(cache_path)
    
    # Check if migration is needed
    migration_needed = manager.check_migration_needed()
    
    if not migration_needed['any']:
        print("✅ No migration needed. All components are up to date.")
        return
    
    print("🔄 Migration needed for:", 
          ', '.join(k for k, v in migration_needed.items() if v and k != 'any'))
    
    # Ask for confirmation
    try:
        confirm = input("Proceed with migration? [y/N]: ").lower().strip()
        if confirm not in ['y', 'yes']:
            print("Migration cancelled.")
            return
    except KeyboardInterrupt:
        print("\nMigration cancelled.")
        return
    
    # Run migration
    results = manager.run_full_migration()
    
    # Display results
    print("\n" + "="*50)
    print("MIGRATION RESULTS")
    print("="*50)
    
    for component, result in results.items():
        status = "✅ SUCCESS" if result.success else "❌ FAILED"
        print(f"{component.upper()}: {status} ({result.migrated_count} items, {result.duration:.2f}s)")
        
        if result.errors:
            for error in result.errors:
                print(f"  ❌ {error}")
        
        if result.warnings:
            for warning in result.warnings:
                print(f"  ⚠️ {warning}")
    
    # Save report
    report_file = cache_path / f"migration_report_{int(time.time())}.md"
    with open(report_file, 'w') as f:
        f.write(manager.generate_migration_report(results))
    
    print(f"\n📄 Detailed report saved to: {report_file}")

if __name__ == "__main__":
    import sys
    cache_dir = sys.argv[1] if len(sys.argv) > 1 else None
    run_migration_cli(cache_dir)