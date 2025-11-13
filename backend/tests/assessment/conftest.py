"""
Pytest configuration and fixtures for assessment tests
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture(scope="session", autouse=True)
def mock_database():
    """Mock database connections to speed up tests"""
    # Patch all three modules
    patches = [
        patch('app.agents.assessment.sra.sra_module.ModeratorDatabase'),
        patch('app.agents.assessment.da.da_module.ModeratorDatabase'),
        patch('app.agents.assessment.tpa.tpa_module.ModeratorDatabase'),
    ]
    
    mock_instances = []
    for p in patches:
        mock_db = p.start()
        mock_instance = MagicMock()
        mock_instance.save_module_state.return_value = True
        mock_instance.get_module_state.return_value = None
        mock_db.return_value = mock_instance
        mock_instances.append(mock_instance)
    
    yield mock_instances
    
    for p in patches:
        p.stop()


@pytest.fixture(scope="session", autouse=True)
def mock_llm():
    """Mock LLM calls to speed up tests"""
    # Patch all three modules
    patches = [
        patch('app.agents.assessment.sra.sra_module.LLMWrapper'),
        patch('app.agents.assessment.da.da_module.LLMWrapper'),
        patch('app.agents.assessment.tpa.tpa_module.LLMWrapper'),
    ]
    
    mock_instances = []
    for p in patches:
        mock_llm_class = p.start()
        mock_llm_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.content = '{"symptoms": [{"symptom_name": "Test", "description": "Test symptom"}]}'
        mock_response.error = None
        mock_llm_instance.generate_response.return_value = mock_response
        mock_llm_class.return_value = mock_llm_instance
        mock_instances.append(mock_llm_instance)
    
    yield mock_instances
    
    for p in patches:
        p.stop()


@pytest.fixture
def mock_llm_for_da():
    """Mock LLM for DA module"""
    with patch('app.agents.assessment.da.da_module.LLMWrapper') as mock_llm_class:
        mock_llm_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.content = '{"primary_diagnosis": {"name": "Test Diagnosis"}, "confidence": 0.8}'
        mock_llm_instance.generate_response.return_value = mock_response
        mock_llm_class.return_value = mock_llm_instance
        yield mock_llm_instance


@pytest.fixture
def mock_llm_for_tpa():
    """Mock LLM for TPA module"""
    with patch('app.agents.assessment.tpa.tpa_module.LLMWrapper') as mock_llm_class:
        mock_llm_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.content = '{"primary_intervention": {"name": "CBT"}, "reasoning": "Test"}'
        mock_llm_instance.generate_response.return_value = mock_response
        mock_llm_class.return_value = mock_llm_instance
        yield mock_llm_instance

