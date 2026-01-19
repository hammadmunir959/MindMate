"""
Test Database Persistence
Tests that sessions are properly saved and retrieved from database
"""

import sys
import os
import uuid
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.agents.assessment.assessment_v2.moderator import AssessmentModerator
from app.agents.assessment.assessment_v2.types import SessionState

def test_database_persistence():
    """Test database persistence for sessions"""
    print("\n" + "="*80)
    print("DATABASE PERSISTENCE TEST")
    print("="*80)
    
    try:
        moderator = AssessmentModerator()
        
        if not hasattr(moderator, 'db') or not moderator.db:
            print("⚠️  Database not available - skipping persistence test")
            return
        
        # Create test session with valid UUID
        test_user_id = str(uuid.uuid4())  # Use valid UUID format
        test_session_id = f"test_persistence_{uuid.uuid4().hex[:8]}"
        
        print(f"\n1. Creating session: {test_session_id}")
        greeting = moderator.start_assessment(
            user_id=test_user_id,
            session_id=test_session_id
        )
        print(f"   ✅ Session created: {greeting[:50]}...")
        
        # Check if session exists in database
        print(f"\n2. Checking if session exists in database...")
        db_session = moderator.db.get_session(test_session_id)
        if db_session:
            print(f"   ✅ Session found in database!")
            print(f"   - Session ID: {db_session.session_id}")
            print(f"   - Current Module: {db_session.current_module}")
            print(f"   - User ID: {db_session.user_id}")
        else:
            print(f"   ❌ Session NOT found in database")
            return False
        
        # Process a message and check persistence
        print(f"\n3. Processing message and checking persistence...")
        response = moderator.process_message(
            user_id=test_user_id,
            session_id=test_session_id,
            message="34"
        )
        print(f"   ✅ Message processed: {response[:50]}...")
        
        # Check if session was updated in database
        db_session_updated = moderator.db.get_session(test_session_id)
        if db_session_updated:
            print(f"   ✅ Session updated in database!")
            print(f"   - Updated at: {db_session_updated.updated_at}")
        else:
            print(f"   ❌ Session update not found in database")
            return False
        
        # Test module transition persistence
        print(f"\n4. Testing module transition persistence...")
        # Process more messages to trigger module transition
        for msg in ["Male", "Bachelor's degree", "Software Engineer", "Single"]:
            moderator.process_message(
                user_id=test_user_id,
                session_id=test_session_id,
                message=msg
            )
        
        # Check if module transition was persisted
        db_session_transitioned = moderator.db.get_session(test_session_id)
        if db_session_transitioned:
            print(f"   ✅ Module transition persisted!")
            print(f"   - Current Module: {db_session_transitioned.current_module}")
            print(f"   - Module History: {db_session_transitioned.module_history}")
        else:
            print(f"   ❌ Module transition not persisted")
            return False
        
        print(f"\n✅ All database persistence tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during database persistence test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database_persistence()
    sys.exit(0 if success else 1)

