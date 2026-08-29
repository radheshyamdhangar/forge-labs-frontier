"""
Simple Baseline RAG without verification.

This is a basic RAG system that:
- Reads PDFs from /idea folder
- Uses keyword matching to retrieve relevant documents
- Directly answers from retrieved content without verification
- No citations, no retry logic
- Expected to fail on contradictory questions (~40% accuracy)
"""

import os
from pathlib import Path
from typing import List, Tuple
from pypdf import PdfReader


class SimpleBaselineRAG:
    """Basic RAG without verification or retry logic."""
    
    def __init__(self, pdf_folder: str = None):
        """Initialize RAG with PDF folder."""
        if pdf_folder is None:
            pdf_folder = str(Path(__file__).parent.parent / "idea")
        
        self.pdf_folder = Path(pdf_folder)
        self.documents = {}  # {filename: content}
        self._load_pdfs()
    
    def _load_pdfs(self) -> None:
        """Load all PDFs from folder."""
        if not self.pdf_folder.exists():
            print(f"Warning: PDF folder not found: {self.pdf_folder}")
            return
        
        pdf_files = list(self.pdf_folder.glob("*.pdf"))
        print(f"Found {len(pdf_files)} PDFs")
        
        for pdf_path in pdf_files:
            try:
                reader = PdfReader(str(pdf_path))
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                self.documents[pdf_path.name] = text
                print(f"[OK] Loaded: {pdf_path.name}")
            except Exception as e:
                print(f"[ERROR] Failed to load {pdf_path.name}: {e}")
    
    def retrieve(self, query: str, top_k: int = 1) -> List[Tuple[str, str]]:
        """
        Retrieve relevant documents using simple keyword matching.
        Returns list of (filename, content_snippet).
        """
        query_words = set(query.lower().split())
        scored_docs = []
        
        for filename, content in self.documents.items():
            content_lower = content.lower()
            # Simple keyword matching score
            score = sum(1 for word in query_words if word in content_lower)
            if score > 0:
                scored_docs.append((filename, content, score))
        
        # Sort by score descending
        scored_docs.sort(key=lambda x: x[2], reverse=True)
        
        # Return top-k
        results = []
        for filename, content, _ in scored_docs[:top_k]:
            # Return first 500 chars of content
            snippet = content[:500]
            results.append((filename, snippet))
        
        return results if results else [("No documents found", "")]
    
    def answer(self, query: str) -> str:
        """
        Answer query directly from retrieved documents.
        No verification, no retry, no citations.
        """
        # Retrieve relevant documents
        retrieved = self.retrieve(query, top_k=1)
        
        if not retrieved or retrieved[0][0] == "No documents found":
            return "I don't have information about this topic in the SOPs."
        
        filename, content = retrieved[0]
        
        # Direct answer from SOP: just return the content
        prompt = f"Answer from SOPs: {query}\n\nRelevant SOP content:\n{content}"
        
        # Simple heuristic response (no LLM - just return the retrieved content)
        # In production, this would call an LLM, but we're keeping it baseline
        return f"From {filename}: {content[:300]}...\n\n[No verification, direct answer from SOP]"


def main():
    """Test the baseline RAG."""
    print("=" * 60)
    print("SIMPLE BASELINE RAG - No Verification")
    print("=" * 60)
    
    rag = SimpleBaselineRAG()
    
    # Test queries
    test_queries = [
        "What are the requirements for KYC verification?",
        "What is the minimum credit score for a loan?",
        "How long does it take to process an insurance claim?",
        "What is the claim limit for insurance policies?",
        "What documents are needed for a loan application?",
    ]
    
    print("\nRunning baseline RAG queries:\n")
    for query in test_queries:
        print(f"Q: {query}")
        answer = rag.answer(query)
        print(f"A: {answer}\n")
        print("-" * 60)


if __name__ == "__main__":
    main()
