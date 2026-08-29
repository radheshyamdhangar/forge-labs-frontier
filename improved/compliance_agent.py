"""
Compliance Agent - Orchestrates Retriever -> Verifier -> Final Output.

Orchestration flow:
1. Retrieve relevant chunks from retriever agent
2. Generate initial answer from chunks
3. Verify answer with verifier agent
4. If not verified, retry retrieval with different parameters
5. Return final JSON with evidence, confidence, compliance flag
"""

import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from retriever_agent import RetrieverAgent, RetrievedChunk
from verifier_agent import VerifierAgent, VerificationResult


@dataclass
class EvidenceItem:
    """Evidence supporting an answer."""
    source: str
    page: int
    section: str
    relevance: float


@dataclass
class ComplianceResponse:
    """Final compliance response with evidence."""
    compliant: bool  # Answer was grounded and verified
    answer: str
    confidence: float  # 0.0 to 1.0
    evidence: List[Dict[str, Any]]  # Source, page, relevance
    needs_human_review: bool
    attempted_retries: int
    explanation: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "compliant": self.compliant,
            "answer": self.answer,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "needs_human_review": self.needs_human_review,
            "attempted_retries": self.attempted_retries,
            "explanation": self.explanation
        }


class ComplianceAgent:
    """Compliance Agent - Orchestrates retrieval and verification."""
    
    MAX_RETRIES = 2
    
    def __init__(self, pdf_folder: str = None):
        """Initialize compliance agent with retriever and verifier."""
        self.retriever = RetrieverAgent(pdf_folder)
        self.verifier = VerifierAgent()
        self.trajectory: List[Dict[str, Any]] = []  # Track execution steps
    
    def _generate_answer_from_chunks(self, query: str, chunks: List[RetrievedChunk]) -> str:
        """Generate answer from retrieved chunks."""
        if not chunks:
            return "I don't have relevant information to answer this question."
        
        # Build answer from top chunks
        answer_parts = []
        seen_text = set()
        
        for chunk in chunks[:3]:  # Use top 3 chunks
            if chunk.text.strip() and chunk.text not in seen_text:
                answer_parts.append(f"{chunk.text.strip()}")
                seen_text.add(chunk.text)
        
        if answer_parts:
            # Join with space, limit to 500 chars for clarity
            answer = " ".join(answer_parts)
            return answer[:500] if len(answer) > 500 else answer
        else:
            return "Retrieved chunks but unable to formulate answer."
    
    def _log_step(self, step_name: str, details: Dict[str, Any]) -> None:
        """Log a step in the execution trajectory."""
        self.trajectory.append({
            "step": step_name,
            "details": details
        })
    
    def process(self, query: str, verbose: bool = False) -> ComplianceResponse:
        """
        Process a query through retriever -> verifier pipeline.
        
        Returns ComplianceResponse with full evidence and confidence.
        """
        self.trajectory = []  # Reset trajectory
        
        # Step 1: Initial Retrieval
        self._log_step("retrieval", {"query": query, "attempt": 1})
        
        chunks = self.retriever.retrieve(query, top_k=3)
        self._log_step("retrieval_result", {
            "chunks_found": len(chunks),
            "confidence_scores": [c.confidence for c in chunks]
        })
        
        if verbose:
            print(f"[Retriever] Found {len(chunks)} chunks, top confidence: {chunks[0].confidence if chunks else 0:.2%}")
        
        # Step 2: Answer Generation
        answer = self._generate_answer_from_chunks(query, chunks)
        self._log_step("answer_generation", {"answer": answer[:100]})
        
        if verbose:
            print(f"[Generator] Answer: {answer[:80]}...")
        
        # Step 3: Verification
        self._log_step("verification", {"attempt": 1})
        verification = self.verifier.verify(answer, chunks)
        self._log_step("verification_result", {
            "verified": verification.is_verified,
            "confidence": verification.confidence,
            "explanation": verification.explanation
        })
        
        if verbose:
            print(f"[Verifier] Verified={verification.is_verified}, Confidence={verification.confidence:.2%}")
        
        attempted_retries = 0
        
        # Step 4: Retry Logic
        if not verification.is_verified and verification.retry_suggested:
            for retry_idx in range(self.MAX_RETRIES):
                attempted_retries += 1
                
                if verbose:
                    print(f"[Retry] Attempt {retry_idx + 1}...")
                
                self._log_step("retry", {"attempt": retry_idx + 1})
                
                # Try retrieving more chunks or with different strategy
                top_k = 5 if retry_idx == 0 else 7
                chunks = self.retriever.retrieve(query, top_k=top_k)
                
                self._log_step("retry_retrieval", {
                    "chunks_found": len(chunks),
                    "top_k": top_k
                })
                
                # Re-generate answer
                answer = self._generate_answer_from_chunks(query, chunks)
                
                # Re-verify
                verification = self.verifier.verify(answer, chunks)
                
                self._log_step("retry_verification", {
                    "verified": verification.is_verified,
                    "confidence": verification.confidence
                })
                
                if verification.is_verified:
                    if verbose:
                        print(f"[Retry] Success on attempt {retry_idx + 1}!")
                    break
        
        # Step 5: Build Evidence List
        evidence_list = []
        for chunk in chunks[:3]:
            evidence_list.append({
                "source": chunk.source_file,
                "page": chunk.page_number,
                "section": chunk.section_title or "General",
                "relevance": chunk.confidence,
                "text_snippet": chunk.text[:100]
            })
        
        self._log_step("evidence_compilation", {"evidence_items": len(evidence_list)})
        
        # Step 6: Final Response
        compliance_response = ComplianceResponse(
            compliant=verification.is_verified,
            answer=answer,
            confidence=verification.confidence,
            evidence=evidence_list,
            needs_human_review=verification.needs_human_review,
            attempted_retries=attempted_retries,
            explanation=verification.explanation
        )
        
        self._log_step("final_response", {
            "compliant": compliance_response.compliant,
            "confidence": compliance_response.confidence
        })
        
        return compliance_response
    
    def get_trajectory(self) -> List[Dict[str, Any]]:
        """Get execution trajectory for logging/analysis."""
        return self.trajectory


def main():
    """Test compliance agent."""
    print("=" * 70)
    print("COMPLIANCE AGENT - Orchestrated RAG Pipeline")
    print("=" * 70)
    
    agent = ComplianceAgent()
    
    test_queries = [
        "What is the minimum credit score for a secured loan?",
        "How long does it take to process an insurance claim?",
        "What documents are needed for KYC verification?",
    ]
    
    print("\nProcessing queries with full compliance pipeline:\n")
    for query in test_queries:
        print(f"Q: {query}")
        response = agent.process(query, verbose=True)
        print(f"  Compliant: {response.compliant}")
        print(f"  Confidence: {response.confidence:.2%}")
        print(f"  Evidence: {len(response.evidence)} items")
        print(f"  Human Review: {response.needs_human_review}")
        print()


if __name__ == "__main__":
    main()
