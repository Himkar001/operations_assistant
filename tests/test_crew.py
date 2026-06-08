"""
End-to-end tests for CrewAI crew.

Tests the full crew workflow on sample questions.

Run with: python tests/test_crew.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from crew_main import run_crew


class TestQuestions:
    """End-to-end crew tests with sample questions."""
    
    # Sample questions the crew should be able to answer
    SAMPLE_QUESTIONS = [
        {
            "id": 1,
            "question": "What is our product return policy?",
            "expected_keywords": ["30 days", "prepaid", "return", "shipping"],
            "description": "Returns and refunds"
        },
        {
            "id": 2,
            "question": "What features are included in the Premium package?",
            "expected_keywords": ["Premium", "analytics", "API", "support"],
            "description": "Product features"
        },
        {
            "id": 3,
            "question": "How many support tickets were resolved this month?",
            "expected_keywords": ["ticket", "support", "resolution"],
            "description": "Support metrics"
        }
    ]
    
    def test_question(self, question_data):
        """Test crew on a single question."""
        question = question_data["question"]
        q_id = question_data["id"]
        description = question_data["description"]
        expected_keywords = question_data["expected_keywords"]
        
        print(f"\n{'='*70}")
        print(f"Test Question #{q_id}: {description}")
        print(f"{'='*70}")
        print(f"Question: {question}\n")
        
        try:
            # Run crew
            result = run_crew(question)
            result_str = str(result).lower()
            
            # Check if answer contains expected content
            found_keywords = []
            missing_keywords = []
            
            for keyword in expected_keywords:
                if keyword.lower() in result_str:
                    found_keywords.append(keyword)
                else:
                    missing_keywords.append(keyword)
            
            # Verify result contains sources
            has_sources = "source" in result_str or "document" in result_str or "from" in result_str
            
            print(f"\n{'─'*70}")
            print("Analysis:")
            print(f"{'─'*70}")
            print(f"Found keywords: {len(found_keywords)}/{len(expected_keywords)}")
            for kw in found_keywords:
                print(f"  ✓ {kw}")
            
            if missing_keywords:
                print(f"Missing keywords: {missing_keywords}")
            
            print(f"Has sources: {'✓ Yes' if has_sources else '✗ No'}")
            
            # Result
            success = len(found_keywords) >= len(expected_keywords) * 0.5  # At least 50% match
            status = "✓ PASS" if success else "⚠ PARTIAL"
            
            print(f"\nResult: {status}")
            
            # Save example output
            self._save_example(q_id, question, result)
            
            return success
            
        except Exception as e:
            print(f"✗ ERROR: {e}")
            print(f"Result: FAILED")
            import traceback
            traceback.print_exc()
            return False
    
    def _save_example(self, q_id, question, result):
        """Save example Q&A to file."""
        output_dir = Path(__file__).parent.parent / "outputs" / "examples"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = output_dir / f"example_{q_id:02d}_q_and_a.md"
        
        content = f"""# Example Question #{q_id}

## Question
{question}

## Answer
{result}

---
Generated: {datetime.now().isoformat()}
"""
        
        try:
            filename.write_text(content, encoding='utf-8')
            print(f"Saved example to: {filename.name}")
        except Exception as e:
            print(f"Could not save example: {e}")
    
    def run_all_tests(self):
        """Run all sample questions."""
        print("\n" + "="*70)
        print("End-to-End Crew Tests")
        print("="*70)
        print(f"Testing {len(self.SAMPLE_QUESTIONS)} sample questions\n")
        
        passed = 0
        failed = 0
        
        for question_data in self.SAMPLE_QUESTIONS:
            try:
                if self.test_question(question_data):
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"\n✗ Unexpected error: {e}")
                failed += 1
        
        print(f"\n{'='*70}")
        print("Test Summary")
        print(f"{'='*70}")
        print(f"Total: {len(self.SAMPLE_QUESTIONS)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success rate: {100*passed//len(self.SAMPLE_QUESTIONS)}%")
        print(f"{'='*70}\n")
        
        return failed == 0


if __name__ == "__main__":
    tester = TestQuestions()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
