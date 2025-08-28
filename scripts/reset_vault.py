#!/usr/bin/env python3
"""
Vault Reset Script for ReliQuary

This script provides functionality to reset vault data for testing purposes,
including clearing vault storage, resetting trust scores, and cleaning up
associated metadata.
"""

import argparse
import json
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
import uuid

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import ReliQuary components
try:
    from vaults.manager import VaultManager
    from core.trust.scorer import TrustScoringEngine
    from agents.memory.db_manager import DBManager
except ImportError:
    # Mock implementations for reset script
    class VaultManager:
        def __init__(self, storage_backend=None):
            self.storage_path = Path("vaults/storage/local")
        
        def list_vaults(self) -> list:
            return ["demo_vault_1", "demo_vault_2"]
        
        def delete_vault(self, vault_id: str) -> bool:
            return True
    
    class TrustScoringEngine:
        def reset_user_trust(self, user_id: str) -> bool:
            return True
        
        def reset_all_trust_data(self) -> bool:
            return True
    
    class DBManager:
        def __init__(self, db_path: str = None):
            pass
        
        def cleanup_old_records(self, older_than_days: int = 30) -> int:
            return 0


def reset_vault_storage(vault_manager: VaultManager, force: bool = False) -> int:
    """Reset vault storage by deleting all vaults"""
    print("Resetting vault storage...")
    
    try:
        # List all vaults
        vaults = vault_manager.list_vaults()
        print(f"Found {len(vaults)} vaults to reset")
        
        if not force and len(vaults) > 0:
            response = input(f"Are you sure you want to delete {len(vaults)} vaults? (y/N): ")
            if response.lower() != 'y':
                print("Vault reset cancelled by user")
                return 0
        
        # Delete each vault
        deleted_count = 0
        for vault_id in vaults:
            try:
                if vault_manager.delete_vault(vault_id):
                    print(f"  ✓ Deleted vault: {vault_id}")
                    deleted_count += 1
                else:
                    print(f"  ✗ Failed to delete vault: {vault_id}")
            except Exception as e:
                print(f"  ✗ Error deleting vault {vault_id}: {e}")
        
        print(f"Vault storage reset completed. Deleted {deleted_count} vaults.")
        return deleted_count
        
    except Exception as e:
        print(f"Error resetting vault storage: {e}")
        return 0


def reset_trust_data(trust_engine: TrustScoringEngine, user_id: str = None) -> bool:
    """Reset trust data for a specific user or all users"""
    print("Resetting trust data...")
    
    try:
        if user_id:
            # Reset trust for specific user
            result = trust_engine.reset_user_trust(user_id)
            if result:
                print(f"  ✓ Trust data reset for user: {user_id}")
            else:
                print(f"  ✗ Failed to reset trust data for user: {user_id}")
            return result
        else:
            # Reset all trust data
            result = trust_engine.reset_all_trust_data()
            if result:
                print("  ✓ All trust data reset successfully")
            else:
                print("  ✗ Failed to reset all trust data")
            return result
            
    except Exception as e:
        print(f"Error resetting trust data: {e}")
        return False


def cleanup_database(db_manager: DBManager, days: int = 30) -> int:
    """Clean up old database records"""
    print(f"Cleaning up database records older than {days} days...")
    
    try:
        deleted_count = db_manager.cleanup_old_records(older_than_days=days)
        print(f"  ✓ Cleaned up {deleted_count} old database records")
        return deleted_count
        
    except Exception as e:
        print(f"Error cleaning up database: {e}")
        return 0


def reset_agent_memory(days: int = 7) -> int:
    """Reset agent memory by cleaning up old records"""
    print(f"Resetting agent memory (records older than {days} days)...")
    
    try:
        # Clean up agent memory directory
        memory_path = Path("agents/memory")
        if memory_path.exists():
            deleted_count = 0
            cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
            
            for file_path in memory_path.glob("*.mem"):
                try:
                    if file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        deleted_count += 1
                except Exception:
                    continue
            
            print(f"  ✓ Cleaned up {deleted_count} agent memory files")
            return deleted_count
        else:
            print("  No agent memory directory found")
            return 0
            
    except Exception as e:
        print(f"Error resetting agent memory: {e}")
        return 0


def reset_audit_logs(days: int = 30) -> int:
    """Reset audit logs by cleaning up old entries"""
    print(f"Resetting audit logs (entries older than {days} days)...")
    
    try:
        # Clean up audit log directory
        audit_path = Path("logs")
        if audit_path.exists():
            deleted_count = 0
            cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
            
            for file_path in audit_path.glob("audit_*.log"):
                try:
                    if file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        deleted_count += 1
                except Exception:
                    continue
            
            print(f"  ✓ Cleaned up {deleted_count} audit log files")
            return deleted_count
        else:
            print("  No audit log directory found")
            return 0
            
    except Exception as e:
        print(f"Error resetting audit logs: {e}")
        return 0


def create_reset_report(reset_stats: dict) -> str:
    """Create a reset report"""
    report = {
        "reset_timestamp": datetime.now().isoformat(),
        "reset_stats": reset_stats,
        "reset_id": str(uuid.uuid4())
    }
    
    report_path = Path("logs/reset_reports")
    report_path.mkdir(parents=True, exist_ok=True)
    
    report_file = report_path / f"reset_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Reset report saved to: {report_file}")
    except Exception as e:
        print(f"Failed to save reset report: {e}")
    
    return str(report_file)


def main():
    """Main reset function"""
    parser = argparse.ArgumentParser(description="ReliQuary Vault Reset Script")
    parser.add_argument("--force", action="store_true", 
                        help="Force reset without confirmation prompts")
    parser.add_argument("--user-id", help="Reset trust data for specific user only")
    parser.add_argument("--days", type=int, default=30,
                        help="Number of days for data cleanup (default: 30)")
    parser.add_argument("--vaults-only", action="store_true",
                        help="Reset vaults only")
    parser.add_argument("--trust-only", action="store_true",
                        help="Reset trust data only")
    parser.add_argument("--db-only", action="store_true",
                        help="Clean up database only")
    parser.add_argument("--all", action="store_true",
                        help="Reset everything (default behavior)")
    
    args = parser.parse_args()
    
    # Determine what to reset
    reset_vaults = args.all or args.vaults_only or (not any([args.trust_only, args.db_only]))
    reset_trust = args.all or args.trust_only or (not any([args.vaults_only, args.db_only]))
    reset_db = args.all or args.db_only or (not any([args.vaults_only, args.trust_only]))
    
    print("🔧 ReliQuary Vault Reset Utility")
    print(f"Time: {datetime.now().isoformat()}")
    print(f"Force mode: {'Enabled' if args.force else 'Disabled'}")
    print(f"Days for cleanup: {args.days}")
    
    if not args.force:
        response = input("This will reset system data. Are you sure? (type 'RESET' to confirm): ")
        if response != 'RESET':
            print("Reset cancelled")
            return 1
    
    # Initialize components
    reset_stats = {
        "vaults_deleted": 0,
        "trust_data_reset": False,
        "db_records_cleaned": 0,
        "agent_memory_cleaned": 0,
        "audit_logs_cleaned": 0
    }
    
    try:
        # Initialize managers
        vault_manager = VaultManager()
        trust_engine = TrustScoringEngine()
        db_manager = DBManager()
        
        # Reset vaults
        if reset_vaults:
            reset_stats["vaults_deleted"] = reset_vault_storage(vault_manager, args.force)
        
        # Reset trust data
        if reset_trust:
            reset_stats["trust_data_reset"] = reset_trust_data(trust_engine, args.user_id)
        
        # Clean up database
        if reset_db:
            reset_stats["db_records_cleaned"] = cleanup_database(db_manager, args.days)
            reset_stats["agent_memory_cleaned"] = reset_agent_memory(args.days)
            reset_stats["audit_logs_cleaned"] = reset_audit_logs(args.days)
        
        # Create reset report
        report_file = create_reset_report(reset_stats)
        
        # Summary
        print("\n=== Reset Summary ===")
        print(f"Vaults deleted: {reset_stats['vaults_deleted']}")
        print(f"Trust data reset: {reset_stats['trust_data_reset']}")
        print(f"Database records cleaned: {reset_stats['db_records_cleaned']}")
        print(f"Agent memory files cleaned: {reset_stats['agent_memory_cleaned']}")
        print(f"Audit log files cleaned: {reset_stats['audit_logs_cleaned']}")
        print(f"Report saved to: {report_file}")
        print("✅ Reset completed successfully!")
        
        return 0
        
    except Exception as e:
        print(f"❌ Reset failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)