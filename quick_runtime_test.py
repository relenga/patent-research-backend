#!/usr/bin/env python3
"""
Quick runtime test for Phase 3.2A pipeline functionality.
Tests basic imports and service status without full instantiation.
"""

def test_pipeline_imports():
    """Test if pipeline modules can be imported."""
    try:
        import sys
        import os
        
        # Add src to path
        src_path = os.path.join(os.path.dirname(__file__), 'src')
        sys.path.insert(0, src_path)
        
        print("Testing pipeline imports...")
        
        # Test basic enum import
        from app.core.pipeline.state_machine import PipelineDocumentState, PipelineImageState
        print("✓ State enums import successfully")
        print(f"  Document states available: {len(list(PipelineDocumentState))}")
        print(f"  Image states available: {len(list(PipelineImageState))}")
        
        # Test common service imports (without instantiation)
        from common.time import TimeService
        from common.ids import IDService
        print("✓ Service classes import successfully")
        print(f"  TimeService class: {TimeService}")
        print(f"  IDService class: {IDService}")
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_abstract_vs_concrete():
    """Check if services are concrete or abstract."""
    try:
        from common.time import TimeService
        from common.ids import IDService
        from abc import ABC
        
        print("\nTesting service implementations...")
        
        # Check if abstract
        is_time_abstract = issubclass(TimeService, ABC)
        is_id_abstract = issubclass(IDService, ABC)
        
        print(f"TimeService is abstract: {is_time_abstract}")
        print(f"IDService is abstract: {is_id_abstract}")
        
        # Try to see if they have abstract methods
        time_abstract_methods = getattr(TimeService, '__abstractmethods__', set())
        id_abstract_methods = getattr(IDService, '__abstractmethods__', set())
        
        print(f"TimeService abstract methods: {len(time_abstract_methods)}")
        print(f"IDService abstract methods: {len(id_abstract_methods)}")
        
        if time_abstract_methods:
            print(f"  TimeService missing: {list(time_abstract_methods)[:5]}...")
        if id_abstract_methods:
            print(f"  IDService missing: {list(id_abstract_methods)[:5]}...")
            
        return not (is_time_abstract or is_id_abstract)
        
    except Exception as e:
        print(f"✗ Abstract check failed: {e}")
        return False

def main():
    """Run basic runtime tests."""
    print("=== Phase 3.2A Pipeline Runtime Test ===")
    
    imports_work = test_pipeline_imports()
    services_concrete = test_abstract_vs_concrete()
    
    print(f"\n=== RESULTS ===")
    print(f"Pipeline imports work: {imports_work}")
    print(f"Services are concrete: {services_concrete}")
    
    if imports_work and services_concrete:
        print("✓ Runtime fixes appear successful")
        return 0
    elif imports_work:
        print("⚠ Partial success - imports work but services still abstract")
        return 1
    else:
        print("✗ Runtime fixes failed - basic imports broken")
        return 2

if __name__ == "__main__":
    exit(main())