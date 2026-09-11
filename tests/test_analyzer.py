import os
import sys
import tempfile
from datetime import datetime, timedelta
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.analysis.analyzer import DocumentAnalyzer
from src.models.analysis_models import DocumentAnalysisResult
from src.utils.file_rotation import get_sorted_items

def test_analyzer_extraction():
    # Mock LLM to avoid real API calls in unit tests
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    
    # Setup mock return value
    expected_result = DocumentAnalysisResult(
        title="Test Document",
        author="John Doe",
        creation_date="2026-09-06",
        key_topics=["Testing", "Validation"],
        summary="This is a test document summary."
    )
    mock_structured.invoke.return_value = expected_result
    mock_llm.with_structured_output.return_value = mock_structured
    
    analyzer = DocumentAnalyzer(llm=mock_llm)
    result = analyzer.analyze("Dummy text for testing the analyzer.")
    
    assert result.title == "Test Document"
    assert len(result.key_topics) == 2
    mock_structured.invoke.assert_called_once()

def test_file_and_folder_rotation():
    with tempfile.TemporaryDirectory() as base_dir:
        analyzer = DocumentAnalyzer(llm=MagicMock(), base_save_dir=base_dir)
        
        # 1. Test File Rotation (creating 10 files in today's folder)
        dummy_result = DocumentAnalysisResult(
            key_topics=["A"],
            summary="B"
        )
        
        # Save 10 times to trigger rotation
        for i in range(10):
            analyzer.save_analysis(dummy_result, filename_prefix=f"test_{i}")
            
        today_folder = os.path.join(base_dir, datetime.now().strftime("%Y-%m-%d"))
        files = get_sorted_items(today_folder, is_dir=False)
        
        # Should only have 5 files left
        assert len(files) == 5
        
        # 2. Test Folder Rotation
        # Create 10 dummy date folders manually to simulate past days
        for i in range(10):
            past_date = (datetime.now() - timedelta(days=i+1)).strftime("%Y-%m-%d")
            os.makedirs(os.path.join(base_dir, past_date))
            
        # We now have 11 folders (10 past + 1 today). 
        # Triggering a save should run the folder rotation, keeping only the 5 most recent.
        analyzer.save_analysis(dummy_result, filename_prefix="trigger_folder_rotation")
        
        folders = get_sorted_items(base_dir, is_dir=True)
        assert len(folders) == 5
