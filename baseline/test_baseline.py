"""
Tests for Simple Baseline RAG.

Tests include:
- Basic correctness tests (should pass ~60%)
- Contradictory question tests (should fail ~40%)

This demonstrates the baseline's inability to handle conflicting information
and verify answers.
"""

import sys
from pathlib import Path
from simple_baseline import SimpleBaselineRAG


class TestResults:
    """Track test results."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def record(self, test_name: str, passed: bool, expected: str, actual: str):
        """Record a test result."""
        status = "✓ PASS" if passed else "✗ FAIL"
        self.tests.append({
            'name': test_name,
            'passed': passed,
            'expected': expected,
            'actual': actual
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_summary(self):
        """Print test summary."""
        total = self.passed + self.failed
        accuracy = (self.passed / total * 100) if total > 0 else 0
        
        print("\n" + "=" * 70)
        print("TEST RESULTS SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Accuracy: {accuracy:.1f}%")
        print("=" * 70)
        
        print("\nDetailed Results:")
        for i, test in enumerate(self.tests, 1):
            status = "✓" if test['passed'] else "✗"
            print(f"\n{status} Test {i}: {test['name']}")
            print(f"  Expected: {test['expected']}")
            print(f"  Actual: {test['actual'][:100]}...")


def test_kyc_verification():
    """Test 1: KYC verification requirements (SHOULD PASS)."""
    rag = SimpleBaselineRAG()
    query = "What documents are needed for KYC verification?"
    answer = rag.answer(query)
    
    # Check if answer mentions required documents
    passed = "document" in answer.lower() or "kyc" in answer.lower() or "identification" in answer.lower()
    return passed, "Mentions documents or identification", answer


def test_loan_credit_score():
    """Test 2: Loan credit score minimum (SHOULD PASS)."""
    rag = SimpleBaselineRAG()
    query = "What is the minimum credit score for a secured loan?"
    answer = rag.answer(query)
    
    # Check if answer mentions credit score requirement
    passed = "credit" in answer.lower() and ("loan" in answer.lower() or "score" in answer.lower())
    return passed, "Should mention credit score", answer


def test_insurance_claim_time():
    """Test 3: Insurance claim processing time (SHOULD PASS)."""
    rag = SimpleBaselineRAG()
    query = "How long does it take to process an insurance claim?"
    answer = rag.answer(query)
    
    # Check if answer mentions timeframe
    passed = "day" in answer.lower() or "business" in answer.lower()
    return passed, "Should mention processing time in days", answer


def test_loan_amount_limit():
    """Test 4: Loan amount limits (SHOULD PASS)."""
    rag = SimpleBaselineRAG()
    query = "What is the maximum loan amount?"
    answer = rag.answer(query)
    
    # Check if answer mentions loan or amount
    passed = ("loan" in answer.lower() and ("amount" in answer.lower() or "maximum" in answer.lower()))
    return passed, "Should mention loan amount", answer


def test_insurance_payment_speed():
    """Test 5: Insurance emergency payment (SHOULD PASS)."""
    rag = SimpleBaselineRAG()
    query = "How quickly are emergency insurance claims paid?"
    answer = rag.answer(query)
    
    # Check if answer mentions insurance claim
    passed = "claim" in answer.lower() or "insurance" in answer.lower()
    return passed, "Should mention insurance claims", answer


def test_contradictory_kyc_income():
    """Test 6: Contradictory question - Income requirements (WILL FAIL)."""
    rag = SimpleBaselineRAG()
    # This question tests if RAG can handle nuanced answers
    query = "Is income verification always required for KYC?"
    answer = rag.answer(query)
    
    # The answer should clarify that income verification is only for high transactions
    # But baseline won't distinguish this nuance
    passed = "$50,000" in answer or "exceeding" in answer.lower()
    return passed, "Should clarify income verification is conditional on transaction amount", answer


def test_contradictory_claim_disputes():
    """Test 7: Contradictory question - Claim disputes (WILL FAIL)."""
    rag = SimpleBaselineRAG()
    # Test if RAG can answer about claim disputes (likely not in SOP detail)
    query = "What is the process for disputing a rejected insurance claim?"
    answer = rag.answer(query)
    
    # This likely isn't detailed in SOPs, so RAG will fail
    passed = "appeal" in answer.lower() or "dispute" in answer.lower() or "review" in answer.lower()
    return passed, "Should explain claim dispute/appeal process", answer


def test_contradictory_loan_rejection():
    """Test 8: Contradictory question - Loan rejection reasons (WILL FAIL)."""
    rag = SimpleBaselineRAG()
    # Test if RAG can explain implicit rejection reasons
    query = "Why would a loan application be automatically rejected?"
    answer = rag.answer(query)
    
    # The answer should mention credit score < 500, but baseline might not infer this
    passed = "rejected" in answer.lower() and ("500" in answer or "credit" in answer.lower())
    return passed, "Should explain automatic rejection criteria", answer


def test_contradictory_payment_methods():
    """Test 9: Contradictory question - Payment methods (WILL FAIL)."""
    rag = SimpleBaselineRAG()
    query = "What payment methods are accepted for insurance claims?"
    answer = rag.answer(query)
    
    # This requires understanding implicit details
    passed = "transfer" in answer.lower() and ("check" in answer.lower() or "bank" in answer.lower())
    return passed, "Should mention both bank transfer and check payment options", answer


def test_contradictory_approval_levels():
    """Test 10: Contradictory question - Approval levels (WILL FAIL)."""
    rag = SimpleBaselineRAG()
    query = "Who approves a $100,000 loan?"
    answer = rag.answer(query)
    
    # Should mention manager approval for loans between $50k-$250k
    passed = "manager" in answer.lower()
    return passed, "Should mention manager approval for loans in $50k-$250k range", answer


def main():
    """Run all tests."""
    print("=" * 70)
    print("SIMPLE BASELINE RAG - TEST SUITE")
    print("Expected Accuracy: ~40-50% (showing limitations)")
    print("=" * 70)
    
    results = TestResults()
    
    # Run tests
    tests = [
        ("KYC Verification Requirements", test_kyc_verification),
        ("Loan Credit Score Minimum", test_loan_credit_score),
        ("Insurance Claim Processing Time", test_insurance_claim_time),
        ("Loan Amount Limits", test_loan_amount_limit),
        ("Insurance Emergency Payment Speed", test_insurance_payment_speed),
        ("Contradictory: KYC Income Requirements", test_contradictory_kyc_income),
        ("Contradictory: Claim Dispute Process", test_contradictory_claim_disputes),
        ("Contradictory: Loan Rejection Reasons", test_contradictory_loan_rejection),
        ("Contradictory: Payment Methods", test_contradictory_payment_methods),
        ("Contradictory: Approval Levels for Loans", test_contradictory_approval_levels),
    ]
    
    for test_name, test_func in tests:
        try:
            passed, expected, actual = test_func()
            results.record(test_name, passed, expected, actual)
            status = "✓" if passed else "✗"
            print(f"{status} {test_name}")
        except Exception as e:
            results.record(test_name, False, "No exception", str(e))
            print(f"✗ {test_name} (Exception: {e})")
    
    results.print_summary()
    return results


if __name__ == "__main__":
    results = main()
    sys.exit(0 if results.failed == 0 else 1)
