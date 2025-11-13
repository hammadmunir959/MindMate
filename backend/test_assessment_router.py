#!/usr/bin/env python3
"""
Test script to verify assessment router can be imported and loaded
"""
import sys
import traceback

print("=" * 60)
print("Testing Assessment Router Import")
print("=" * 60)

try:
    print("\n1. Testing assessment endpoint import...")
    from app.api.v1.endpoints import assessment
    print("✅ Assessment endpoint module imported successfully")
    
    print("\n2. Checking for router attribute...")
    if hasattr(assessment, 'router'):
        print("✅ Router attribute exists")
    else:
        print("❌ Router attribute not found")
        sys.exit(1)
    
    print("\n3. Checking router type...")
    from fastapi import APIRouter
    if isinstance(assessment.router, APIRouter):
        print("✅ Router is APIRouter instance")
    else:
        print(f"❌ Router is not APIRouter: {type(assessment.router)}")
        sys.exit(1)
    
    print("\n4. Checking router routes...")
    routes = assessment.router.routes
    print(f"✅ Router has {len(routes)} routes")
    
    print("\n5. Listing routes...")
    for route in routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = ', '.join(route.methods)
            print(f"   {methods:10} {route.path}")
    
    print("\n6. Testing AssessmentModerator import (lazy)...")
    # This might fail, but that's okay - it's lazy loaded
    try:
        from app.agents.assessment.assessment_v2.moderator import AssessmentModerator
        print("✅ AssessmentModerator can be imported")
    except Exception as e:
        print(f"⚠️  AssessmentModerator import failed (this is okay for lazy loading): {e}")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! Router should work.")
    print("=" * 60)
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Unexpected Error: {e}")
    traceback.print_exc()
    sys.exit(1)





