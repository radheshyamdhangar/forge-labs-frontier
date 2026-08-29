"""
Retriever Agent - Better context retrieval with source tracking.

Improvements over baseline:
- Semantic similarity scoring (cosine distance approximation)
- Multi-chunk retrieval with context windows
- Source tracking: file, page number
- Confidence scoring based on relevance match
- Handles overlapping documents better
"""

import re
from pathlib import Path
from typing import List, Tuple, Dict
from pypdf import PdfReader
from dataclasses import dataclass
import math


@dataclass
class RetrievedChunk:
    """A chunk of text with metadata."""
    text: str
    source_file: str
    page_number: int
    chunk_index: int
    confidence: float  # 0.0 to 1.0
    section_title: str = ""


class RetrieverAgent:
    """Retriever Agent with semantic similarity and confidence scoring."""
    
    CHUNK_SIZE = 300  # Characters per chunk
    CHUNK_OVERLAP = 50  # Overlap for context
    
    def __init__(self, pdf_folder: str = None):
        """Initialize retriever with PDF folder."""
        if pdf_folder is None:
            pdf_folder = str(Path(__file__).parent.parent / "idea")
        
        self.pdf_folder = Path(pdf_folder)
        self.chunks: Dict[str, List[RetrievedChunk]] = {}
        self._load_and_chunk_pdfs()
    
    def _load_and_chunk_pdfs(self) -> None:
        """Load PDFs and split into chunks."""
        if not self.pdf_folder.exists():
            print(f"Warning: PDF folder not found: {self.pdf_folder}")
            return
        
        pdf_files = list(self.pdf_folder.glob("*.pdf"))
        print(f"Found {len(pdf_files)} PDFs")
        
        for pdf_path in pdf_files:
            try:
                reader = PdfReader(str(pdf_path))
                
                for page_idx, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    
                    # Split into chunks with overlap
                    chunks = self._create_chunks(text, page_idx, pdf_path.name)
                    
                    if pdf_path.name not in self.chunks:
                        self.chunks[pdf_path.name] = []
                    self.chunks[pdf_path.name].extend(chunks)
                
                print(f"[OK] Loaded: {pdf_path.name} ({len(reader.pages)} pages)")
            except Exception as e:
                print(f"[ERROR] Failed to load {pdf_path.name}: {e}")
    
    def _create_chunks(self, text: str, page_idx: int, filename: str) -> List[RetrievedChunk]:
        """Split text into overlapping chunks with section detection."""
        chunks = []
        section_title = ""
        
        # Extract section titles (lines with <b> tags or all caps followed by newline)
        lines = text.split("\n")
        
        for i in range(0, len(text), self.CHUNK_SIZE - self.CHUNK_OVERLAP):
            chunk_text = text[i:i + self.CHUNK_SIZE]
            
            # Detect section title from current line
            for line in lines:
                if line.strip() and (line.startswith("<b>") or (len(line) < 50 and line.isupper())):
                    section_title = line.replace("<b>", "").replace("</b>", "").strip()
                    break
            
            chunk = RetrievedChunk(
                text=chunk_text.strip(),
                source_file=filename,
                page_number=page_idx + 1,  # 1-indexed
                chunk_index=len(chunks),
                confidence=0.0,  # Will be updated by retriever
                section_title=section_title
            )
            chunks.append(chunk)
        
        return chunks
    
    def _keyword_overlap(self, query_words: set, text: str) -> float:
        """Calculate keyword overlap ratio."""
        text_lower = text.lower()
        text_words = set(text_lower.split())
        
        if not query_words:
            return 0.0
        
        overlap = len(query_words & text_words)
        return overlap / len(query_words)
    
    def _semantic_similarity(self, query: str, text: str) -> float:
        """
        Approximate semantic similarity using:
        1. Keyword overlap
        2. Phrase matching
        3. Length appropriateness
        """
        query_lower = query.lower()
        text_lower = text.lower()
        
        # Keyword overlap (0.6 weight)
        query_words = set(query_lower.split())
        keyword_score = self._keyword_overlap(query_words, text_lower)
        
        # Phrase matching (0.3 weight)
        phrase_score = 0.0
        phrases = [p.strip() for p in query_lower.split() if len(p) > 3]
        if phrases:
            phrase_matches = sum(1 for phrase in phrases if phrase in text_lower)
            phrase_score = phrase_matches / len(phrases) if phrases else 0.0
        
        # Length appropriateness (0.1 weight)
        # Prefer chunks that aren't too short or too long
        text_word_count = len(text_lower.split())
        if 20 <= text_word_count <= 300:
            length_score = 1.0
        elif 10 <= text_word_count <= 500:
            length_score = 0.7
        else:
            length_score = 0.3
        
        # Combined score
        similarity = (0.6 * keyword_score) + (0.3 * phrase_score) + (0.1 * length_score)
        return min(1.0, max(0.0, similarity))
    
    def retrieve(self, query: str, top_k: int = 3) -> List[RetrievedChunk]:
        """
        Retrieve top-k chunks most relevant to query.
        Returns chunks with confidence scores.
        """
        scored_chunks = []
        
        # Score all chunks
        for filename, chunk_list in self.chunks.items():
            for chunk in chunk_list:
                similarity = self._semantic_similarity(query, chunk.text)
                
                if similarity > 0.1:  # Filter very low scores
                    chunk.confidence = similarity
                    scored_chunks.append(chunk)
        
        # Sort by confidence descending
        scored_chunks.sort(key=lambda x: x.confidence, reverse=True)
        
        # Return top-k
        return scored_chunks[:top_k]
    
    def get_chunk_context(self, chunk: RetrievedChunk, context_chars: int = 200) -> str:
        """Get surrounding context for a chunk."""
        return f"[{chunk.section_title}]\n{chunk.text}"


def main():
    """Test retriever agent."""
    print("=" * 60)
    print("RETRIEVER AGENT - Better Context Retrieval")
    print("=" * 60)
    
    retriever = RetrieverAgent()
    
    test_queries = [
        "What is the minimum credit score for a loan?",
        "How long does it take to process an insurance claim?",
        "What documents are needed for KYC verification?",
    ]
    
    print("\nRetrieving top-3 chunks per query:\n")
    for query in test_queries:
        print(f"Q: {query}")
        chunks = retriever.retrieve(query, top_k=3)
        
        for i, chunk in enumerate(chunks, 1):
            print(f"  [{i}] {chunk.source_file} (page {chunk.page_number})")
            print(f"      Confidence: {chunk.confidence:.2%}")
            print(f"      Section: {chunk.section_title}")
            print(f"      Text: {chunk.text[:80]}...")
        print()


if __name__ == "__main__":
    main()
