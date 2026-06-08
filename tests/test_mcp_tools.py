"""
Unit tests for MCP server tools.

Tests search_documents, read_record, and save_report tools directly.

Run with: python -m pytest tests/test_mcp_tools.py -v
Or: python tests/test_mcp_tools.py
"""

import json
import sys
from pathlib import Path
import tempfile

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_server import search_documents, read_record, save_report


class TestMCPTools:
    """Test MCP server tools."""
    
    def test_search_documents_valid_query(self):
        """Test searching for documents with valid query."""
        print("\n✓ Test: Search documents with valid query")
        
        result_json = search_documents(query="return policy")
        result = json.loads(result_json)
        
        assert "query" in result
        assert "results" in result
        assert result["query"] == "return policy"
        assert len(result["results"]) > 0
        
        # Check result structure
        first_result = result["results"][0]
        assert "id" in first_result
        assert "title" in first_result
        assert "snippet" in first_result
        
        print(f"  Found {len(result['results'])} documents")
        print(f"  First match: {first_result['title']}")
    
    def test_search_documents_no_results(self):
        """Test searching with query that matches nothing."""
        print("\n✓ Test: Search with no matches")
        
        result_json = search_documents(query="xyzabc123notfound")
        result = json.loads(result_json)
        
        assert "results" in result
        assert len(result["results"]) == 0
        assert result["total"] == 0
        
        print("  Correctly returned empty results")
    
    def test_read_record_valid_document(self):
        """Test reading a valid document."""
        print("\n✓ Test: Read valid document")
        
        result_json = read_record(document_id="return_policy")
        result = json.loads(result_json)
        
        assert "content" in result
        assert result["found"] == True
        assert len(result["content"]) > 0
        assert "Return" in result["content"] or "return" in result["content"]
        
        print(f"  Successfully read {len(result['content'])} characters")
        print(f"  Content preview: {result['content'][:100]}...")
    
    def test_read_record_invalid_document(self):
        """Test reading a non-existent document."""
        print("\n✓ Test: Read invalid document")
        
        result_json = read_record(document_id="nonexistent_document")
        result = json.loads(result_json)
        
        assert "error" in result
        assert "not found" in result["error"].lower()
        assert "available_documents" in result
        
        print(f"  Correctly returned error")
        print(f"  Available documents: {result['available_documents']}")
    
    def test_save_report(self):
        """Test saving a report."""
        print("\n✓ Test: Save report")
        
        test_title = "Test Report"
        test_content = "This is a test report about return policies.\n\nKey findings:\n- 30 day window\n- Free returns"
        
        result_json = save_report(title=test_title, content=test_content)
        result = json.loads(result_json)
        
        assert "success" in result
        assert result["success"] == True
        assert "file_path" in result
        assert "filename" in result
        
        # Check file was created
        file_path = Path(result["file_path"])
        assert file_path.exists()
        
        # Check content
        saved_content = file_path.read_text()
        assert test_title in saved_content
        assert test_content in saved_content
        
        print(f"  Report saved to: {result['filename']}")
        print(f"  File exists and contains correct content")
    
    def test_search_and_read_workflow(self):
        """Test realistic workflow: search then read."""
        print("\n✓ Test: Search then read workflow")
        
        # Step 1: Search
        search_result = json.loads(search_documents(query="product features"))
        assert len(search_result["results"]) > 0
        
        doc_id = search_result["results"][0]["id"]
        print(f"  Step 1: Found document '{doc_id}'")
        
        # Step 2: Read
        read_result = json.loads(read_record(document_id=doc_id))
        assert read_result["found"] == True
        assert len(read_result["content"]) > 0
        
        print(f"  Step 2: Read {len(read_result['content'])} characters")
        
        # Step 3: Save report
        report_content = f"# Query Result\n\nFound in: {doc_id}\n\n{read_result['content'][:500]}"
        save_result = json.loads(save_report(
            title="Search and Read Test",
            content=report_content
        ))
        
        assert save_result["success"] == True
        print(f"  Step 3: Saved report to {save_result['filename']}")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*70)
    print("MCP Tools Unit Tests")
    print("="*70)
    
    tests = TestMCPTools()
    test_methods = [
        ("Search with valid query", tests.test_search_documents_valid_query),
        ("Search with no matches", tests.test_search_documents_no_results),
        ("Read valid document", tests.test_read_record_valid_document),
        ("Read invalid document", tests.test_read_record_invalid_document),
        ("Save report", tests.test_save_report),
        ("Search and read workflow", tests.test_search_and_read_workflow),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in test_methods:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*70 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
