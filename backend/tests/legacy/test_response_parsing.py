"""
Test Response Parsing and Analysis
Tests the parsing and analysis of assessment responses
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.assessment.assessment_v2.core.llm_response_parser import LLMResponseParser
from app.agents.assessment.assessment_v2.core.response_processor import GlobalResponseProcessor
from app.agents.assessment.assessment_v2.base_types import SCIDQuestion, ResponseType, ProcessedResponse

def test_json_parsing_edge_cases():
    """Test JSON parsing with various edge cases"""
    parser = LLMResponseParser()
    
    test_cases = [
        # Valid JSON
        ('{"selected_option": "Yes", "confidence": 0.9}', True),
        # JSON with markdown code blocks
        ('```json\n{"selected_option": "Yes"}\n```', True),
        # JSON with extra text
        ('Here is the response: {"selected_option": "Yes"}', True),
        # Malformed JSON (missing value)
        ('{"selected_option": "Yes", "confidence":}', False),
        # Empty string
        ('', False),
        # Just text
        ('This is not JSON', False),
        # JSON with trailing comma (should be fixed and parsed)
        ('{"selected_option": "Yes",}', True),  # Our parser fixes this
        # Multiple JSON objects (should extract the one with selected_option)
        ('{"first": "obj"} {"selected_option": "Yes"}', True),
    ]
    
    print("Testing JSON Parsing Edge Cases:")
    print("=" * 60)
    
    for i, (test_input, should_succeed) in enumerate(test_cases, 1):
        try:
            result = parser._parse_json_response(test_input)
            # Check if parsing actually succeeded (not just fallback)
            parsing_failed = result.get("free_text_analysis", {}).get("parsing_failed", False)
            has_data = result.get("selected_option") is not None or result.get("confidence", 0) > 0.5
            success = has_data and not parsing_failed
            status = "✓" if (success == should_succeed) else "✗"
            test_preview = str(test_input)[:50] if test_input else ""
            print(f"{status} Test {i}: {test_preview}...")
            if not success == should_succeed:
                print(f"   Expected: {should_succeed}, Got: {success} (parsing_failed: {parsing_failed})")
        except Exception as e:
            status = "✗" if should_succeed else "✓"
            print(f"{status} Test {i}: Exception - {str(e)[:100]}")
    
    print()

def test_response_analysis():
    """Test response analysis with various user inputs"""
    processor = GlobalResponseProcessor()
    
    # Create a test question
    question = SCIDQuestion(
        id="TEST_01",
        sequence_number=1,
        simple_text="Have you been feeling sad or depressed?",
        response_type=ResponseType.YES_NO,
        options=["Yes", "No", "Sometimes", "Not sure"]
    )
    
    test_responses = [
        # Simple yes/no
        ("yes", "Yes"),
        ("no", "No"),
        ("1", "Yes"),
        ("2", "No"),
        # Complex responses
        ("Yes, I've been feeling very sad lately", None),  # Should use LLM
        ("I'm not sure, maybe sometimes", None),  # Should use LLM
        ("Definitely yes", None),  # Should use LLM
        # Edge cases
        ("", None),
        ("y", "Yes"),
        ("n", "No"),
    ]
    
    print("Testing Response Analysis:")
    print("=" * 60)
    
    for user_response, expected_option in test_responses:
        try:
            processed = processor.process_response(
                user_response=user_response,
                question=question,
                conversation_history=[],
                session_id="test_session"
            )
            
            if expected_option:
                match = processed.selected_option == expected_option
                status = "✓" if match else "✗"
                print(f"{status} '{user_response}' -> {processed.selected_option} (expected: {expected_option})")
            else:
                # Complex response - should have some analysis (and not be a parsing failure)
                parsing_failed = processed.free_text_analysis.get("parsing_failed", False) or processed.free_text_analysis.get("processing_failed", False)
                has_analysis = (
                    (processed.selected_option is not None or
                     bool(processed.extracted_fields) or
                     bool(processed.free_text_analysis)) and
                    not parsing_failed and
                    processed.confidence > 0.0
                )
                status = "✓" if has_analysis else "✗"
                print(f"{status} '{user_response}' -> Selected: {processed.selected_option}, Confidence: {processed.confidence}, Parsing OK: {not parsing_failed}")
        except Exception as e:
            print(f"✗ '{user_response}' -> Error: {e}")
    
    print()

def test_llm_parsing_robustness():
    """Test LLM parsing with various response formats"""
    parser = LLMResponseParser()
    
    # Mock LLM responses (simulating what LLM might return)
    mock_llm_responses = [
        # Clean JSON
        '{"selected_option": "Yes", "confidence": 0.95, "extracted_fields": {}}',
        # JSON with markdown
        '```json\n{"selected_option": "Yes"}\n```',
        # JSON with explanation
        'Based on the response, I believe: {"selected_option": "Yes", "confidence": 0.8}',
        # Malformed but recoverable
        '{"selected_option": "Yes", "confidence": 0.9,}',  # Trailing comma
        # Multiple objects
        '{"first": "obj"} {"selected_option": "Yes"}',
        # Nested JSON
        '{"selected_option": "Yes", "extracted_fields": {"duration": "2 weeks"}}',
    ]
    
    print("Testing LLM Parsing Robustness:")
    print("=" * 60)
    
    for i, mock_response in enumerate(mock_llm_responses, 1):
        try:
            result = parser._parse_json_response(mock_response)
            has_data = result.get("selected_option") is not None or result.get("confidence", 0) > 0
            status = "✓" if has_data else "✗"
            print(f"{status} Mock Response {i}: Extracted data: {has_data}")
            if has_data:
                print(f"   Selected: {result.get('selected_option')}, Confidence: {result.get('confidence')}")
        except Exception as e:
            print(f"✗ Mock Response {i}: Error - {e}")
    
    print()

def test_error_handling():
    """Test error handling in parsing"""
    processor = GlobalResponseProcessor()
    parser = LLMResponseParser()
    
    print("Testing Error Handling:")
    print("=" * 60)
    
    # Test with None values
    try:
        question = SCIDQuestion(
            id="TEST_01",
            sequence_number=1,
            simple_text="Test question",
            response_type=ResponseType.TEXT
        )
        result = processor.process_response(
            user_response="",
            question=question,
            conversation_history=[],
            session_id="test"
        )
        print(f"✓ Empty response handled: {result.selected_option is None}")
    except Exception as e:
        print(f"✗ Empty response error: {e}")
    
    # Test with invalid JSON
    try:
        result = parser._parse_json_response("not json at all")
        print(f"✓ Invalid JSON handled: {result.get('free_text_analysis', {}).get('error') is not None}")
    except Exception as e:
        print(f"✗ Invalid JSON error: {e}")
    
    print()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("RESPONSE PARSING AND ANALYSIS TESTS")
    print("=" * 60 + "\n")
    
    test_json_parsing_edge_cases()
    test_response_analysis()
    test_llm_parsing_robustness()
    test_error_handling()
    
    print("=" * 60)
    print("TESTS COMPLETE")
    print("=" * 60)

