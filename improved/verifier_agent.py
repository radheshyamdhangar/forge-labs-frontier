"""
Verifier Agent - Fact checking and answer verification.

Improvements over baseline:
- Checks if answer is grounded in retrieved chunks
- Retry logic if answer not properly grounded
- Confidence score based on evidence quality
- Tracks whether human review is needed
- Generates explanations for failures
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
from retriever_agent import RetrievedChunk


@dataclass
class VerificationResult:
    """Result of verification."""
    is_verified: bool
    confidence: float  # 0.0 to 1.0
    grounding_chunks: List[RetrievedChunk]
    explanation: str
    needs_human_review: bool
    retry_suggested: bool


class VerifierAgent:
    """Verifier Agent for fact checking and answer grounding."""
    
    def __init__(self):
        """Initialize verifier."""
        pass
    
    def _extract_key_claims(self, answer: str) -> List[str]:
        """Extract key factual claims from answer."""
        # Simple claim extraction - split by periods and sentences
        sentences = [s.strip() for s in answer.split(".") if s.strip()]
        
        # Filter for claim-bearing sentences (those with numbers, keywords, actions)
        claims = []
        for sent in sentences:
            sent_lower = sent.lower()
            # Look for specific patterns
            if any(keyword in sent_lower for keyword in 
                   ["must", "require", "should", "need", "limit", "maximum", 
                    "minimum", "days", "hours", "years", "percent", "amount"]):
                claims.append(sent)
        
        return claims if claims else sentences[:2]  # Fallback to first 2 sentences
    
    def _check_claim_grounding(self, claim: str, chunks: List[RetrievedChunk]) -> Tuple[bool, float]:
        """
        Check if a claim is grounded in retrieved chunks.
        Returns (is_grounded, confidence).
        """
        claim_lower = claim.lower()
        claim_words = set(word for word in claim_lower.split() if len(word) > 3)
        
        best_match_score = 0.0
        
        for chunk in chunks:
            chunk_text = chunk.text.lower()
            
            # Check keyword overlap
            chunk_words = set(word for word in chunk_text.split() if len(word) > 3)
            overlap = len(claim_words & chunk_words)
            
            if overlap > 0:
                match_score = overlap / len(claim_words)
                best_match_score = max(best_match_score, match_score)
        
        # Grounded if at least 25% of claim keywords found in chunks (lowered from 30%)
        is_grounded = best_match_score >= 0.25
        confidence = best_match_score
        
        return is_grounded, confidence
    
    def verify(self, answer: str, chunks: List[RetrievedChunk]) -> VerificationResult:
        """
        Verify if answer is grounded in chunks.
        
        Returns VerificationResult with:
        - is_verified: bool
        - confidence: 0.0-1.0
        - grounding_chunks: chunks that support answer
        - explanation: why verification passed/failed
        - needs_human_review: if answer is ambiguous
        - retry_suggested: if we should try different retrieval
        """
        if not chunks:
            return VerificationResult(
                is_verified=False,
                confidence=0.0,
                grounding_chunks=[],
                explanation="No chunks provided for verification",
                needs_human_review=True,
                retry_suggested=True
            )
        
        # Extract claims from answer
        claims = self._extract_key_claims(answer)
        
        if not claims:
            return VerificationResult(
                is_verified=True,  # No claims to verify
                confidence=0.5,
                grounding_chunks=chunks,
                explanation="Answer contains no specific claims to verify",
                needs_human_review=True,
                retry_suggested=False
            )
        
        # Check each claim
        grounded_claims = 0
        total_confidence = 0.0
        supporting_chunks = []
        
        for claim in claims:
            is_grounded, confidence = self._check_claim_grounding(claim, chunks)
            
            if is_grounded:
                grounded_claims += 1
                total_confidence += confidence
                # Add most confident chunk as supporting
                if chunks:
                    supporting_chunks.append(chunks[0])
        
        # Calculate verification result
        grounding_ratio = grounded_claims / len(claims) if claims else 0.0
        avg_confidence = total_confidence / len(claims) if claims else 0.0
        
        is_verified = grounding_ratio >= 0.7  # 70% of claims must be grounded
        
        # Build explanation
        if is_verified:
            explanation = f"Answer verified: {int(grounding_ratio*100)}% of claims grounded in chunks"
        else:
            explanation = f"Answer not sufficiently grounded: only {int(grounding_ratio*100)}% of claims found in chunks"
        
        # Determine if human review needed
        needs_human_review = (
            avg_confidence < 0.4 or  # Low confidence
            grounding_ratio < 1.0  # Some claims not grounded
        )
        
        # Suggest retry if confidence is very low
        retry_suggested = avg_confidence < 0.3
        
        return VerificationResult(
            is_verified=is_verified,
            confidence=avg_confidence,
            grounding_chunks=supporting_chunks[:3],  # Top 3 supporting chunks
            explanation=explanation,
            needs_human_review=needs_human_review,
            retry_suggested=retry_suggested
        )


def main():
    """Test verifier agent."""
    print("=" * 60)
    print("VERIFIER AGENT - Answer Verification & Fact Checking")
    print("=" * 60)
    
    verifier = VerifierAgent()
    
    # Create mock chunks for testing
    mock_chunks = [
        RetrievedChunk(
            text="Credit score minimum 650 for unsecured loans. Minimum credit score 500 for secured loans.",
            source_file="Loan_SOP.pdf",
            page_number=1,
            chunk_index=0,
            confidence=0.85,
            section_title="Credit Check"
        ),
        RetrievedChunk(
            text="Customers with credit score below 500 are automatically rejected.",
            source_file="Loan_SOP.pdf",
            page_number=1,
            chunk_index=1,
            confidence=0.90,
            section_title="Credit Check"
        ),
    ]
    
    test_answers = [
        "The minimum credit score for a secured loan is 500 and for unsecured is 650.",
        "You need a credit score of 1000 to get any loan.",
        "There is a credit score requirement for loans.",
    ]
    
    print("\nVerifying answers:\n")
    for i, answer in enumerate(test_answers, 1):
        print(f"Answer {i}: {answer}")
        result = verifier.verify(answer, mock_chunks)
        print(f"  Verified: {result.is_verified}")
        print(f"  Confidence: {result.confidence:.2%}")
        print(f"  Explanation: {result.explanation}")
        print(f"  Human Review Needed: {result.needs_human_review}")
        print(f"  Retry Suggested: {result.retry_suggested}")
        print()


if __name__ == "__main__":
    main()
