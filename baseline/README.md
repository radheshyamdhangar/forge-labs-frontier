# Simple Baseline RAG - Without Verification

## Overview

This is a **basic RAG (Retrieval-Augmented Generation) system** designed to demonstrate the limitations of simple keyword-matching approaches without verification or retry logic.

**Expected Accuracy: ~40-50%**

The baseline intentionally lacks:
- ❌ Answer verification
- ❌ Fact checking
- ❌ Retry mechanisms
- ❌ Citation tracking
- ❌ Conflict resolution
- ❌ Semantic understanding

## Components

### 1. `simple_baseline.py`
Basic RAG implementation with:
- **PDF Loading**: Uses `pypdf` to read documents from `/idea` folder
- **Simple Retrieval**: Keyword matching to find relevant documents
- **Direct Answering**: Returns retrieved content without verification
- **No Citations**: Doesn't track sources properly
- **No Retry**: Single attempt only

### 2. `create_dummy_pdfs.py`
Creates 3 dummy Standard Operating Procedures (SOPs):
1. **KYC_SOP.pdf** - Know Your Customer procedures
2. **Insurance_Claim_SOP.pdf** - Insurance claim processing
3. **Loan_SOP.pdf** - Loan application and processing

### 3. `test_baseline.py`
Comprehensive test suite with 10 test cases:
- **5 Basic Tests** (should pass): Direct SOP questions
- **5 Contradictory Tests** (should fail): Nuanced/complex questions

## Test Results

```
Total Tests: 10
Passed: 5
Failed: 5
Accuracy: 50.0%
```

### Passing Tests (Basic Questions)
✓ KYC Verification Requirements
✓ Loan Credit Score Minimum
✓ Insurance Claim Processing Time
✓ Insurance Emergency Payment Speed
✓ Approval Levels for Loans

### Failing Tests (Contradictory/Nuanced Questions)
✗ Loan Amount Limits
✗ KYC Income Requirements (conditional logic)
✗ Claim Dispute Process (not in SOP)
✗ Loan Rejection Reasons (implicit info)
✗ Payment Methods (needs inference)

## Why This Baseline Fails

1. **Simple Keyword Matching**: Retrieves wrong documents when multiple docs contain keywords
2. **No Verification**: Returns content as-is without checking accuracy
3. **No Semantic Understanding**: Can't handle conditional logic or nuanced questions
4. **No Retry Mechanism**: Single attempt only, no second-guessing
5. **No Citation Tracking**: Doesn't properly attribute sources
6. **Missing Context**: Doesn't understand relationships between pieces of information

## Example Failures

### Failed Test: Loan Amount Limits
**Query**: "What is the maximum loan amount?"
**Expected**: "5x annual verified income"
**Actual**: Returns content from Insurance Claim SOP instead of Loan SOP

**Why**: Simple keyword matching found "maximum" in Insurance SOP before finding better match in Loan SOP.

### Failed Test: Claim Dispute Process
**Query**: "What is the process for disputing a rejected insurance claim?"
**Expected**: Explanation of appeal/review process
**Actual**: Returns standard claim processing info, not dispute process

**Why**: Dispute process isn't detailed in the SOP, baseline has no way to handle this.

## File Structure

```
forge-labs-frontier/
├── baseline/
│   ├── simple_baseline.py       # Main RAG implementation
│   ├── create_dummy_pdfs.py     # PDF generator
│   ├── test_baseline.py         # Test suite
│   └── README.md                # This file
├── idea/
│   ├── KYC_SOP.pdf
│   ├── Insurance_Claim_SOP.pdf
│   └── Loan_SOP.pdf
└── requirements.txt             # Dependencies
```

## Dependencies

- `pypdf` - PDF reading
- `reportlab` - PDF generation (for creating dummy PDFs)

## Usage

### Create Dummy PDFs
```bash
python baseline/create_dummy_pdfs.py
```

### Run Baseline RAG
```bash
python baseline/simple_baseline.py
```

### Run Tests
```bash
python baseline/test_baseline.py
```

## Key Takeaways

This baseline demonstrates:
1. **Simple RAG systems achieve only ~50% accuracy** on mixed question types
2. **Keyword matching is insufficient** for document retrieval
3. **Verification is critical** - without it, wrong answers get returned
4. **Context understanding matters** - conditional logic, implicit info, and nuances are missed
5. **Next steps** (Improved version) should include:
   - Semantic search (embeddings)
   - Answer verification
   - Retry logic with clarification
   - Source citation
   - Fact checking
   - Confidence scoring

## Next Phase: Improved Version

The improved version will address these limitations with:
- 🔄 Semantic retrieval using embeddings
- ✓ Answer verification layer
- 🔁 Retry logic with constraint checks
- 📚 Proper citations
- 🎯 Confidence scoring
- 🔍 Fact verification

**Expected Improvement**: 50% → 80%+ accuracy
