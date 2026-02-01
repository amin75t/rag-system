"""
Document Processor for extracting text from various file formats.

This module provides functionality to extract text from PDF, DOCX, TXT,
and other document formats for RAG indexing.
"""
import os
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Document Processor for extracting text from various file formats.
    
    Supports: PDF, DOCX, TXT, MD, and plain text files.
    """
    
    def __init__(self):
        """Initialize the Document Processor."""
        self.supported_extensions = {
            '.pdf': self._extract_pdf,
            '.docx': self._extract_docx,
            '.txt': self._extract_text,
            '.md': self._extract_text,
            '.text': self._extract_text,
        }
        logger.info("DocumentProcessor initialized")
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a document file.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted text content
            
        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file doesn't exist
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extension = path.suffix.lower()
        
        if extension not in self.supported_extensions:
            raise ValueError(
                f"Unsupported file format: {extension}. "
                f"Supported formats: {', '.join(self.supported_extensions.keys())}"
            )
        
        extractor = self.supported_extensions[extension]
        text = extractor(file_path)
        
        logger.info(f"Extracted text from {file_path} ({len(text)} characters)")
        return text
    
    def _extract_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        try:
            import PyPDF2
            
            text = []
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text.append(page.extract_text())
            
            return '\n\n'.join(text)
            
        except ImportError:
            raise ImportError(
                "PyPDF2 is not installed. "
                "Install it with: pip install PyPDF2"
            )
        except Exception as e:
            logger.error(f"Error extracting PDF: {e}")
            raise
    
    def _extract_docx(self, file_path: str) -> str:
        """
        Extract text from DOCX file.
        
        Args:
            file_path: Path to DOCX file
            
        Returns:
            Extracted text
        """
        try:
            from docx import Document
            
            doc = Document(file_path)
            text = []
            
            for paragraph in doc.paragraphs:
                text.append(paragraph.text)
            
            # Also extract from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text.append(cell.text)
            
            return '\n\n'.join(text)
            
        except ImportError:
            raise ImportError(
                "python-docx is not installed. "
                "Install it with: pip install python-docx"
            )
        except Exception as e:
            logger.error(f"Error extracting DOCX: {e}")
            raise
    
    def _extract_text(self, file_path: str) -> str:
        """
        Extract text from plain text file.
        
        Args:
            file_path: Path to text file
            
        Returns:
            File content
        """
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try other encodings
            encodings = ['latin-1', 'cp1252', 'iso-8859-1']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        return file.read()
                except UnicodeDecodeError:
                    continue
            
            raise ValueError(f"Could not decode file {file_path} with any common encoding")
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            raise
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> List[str]:
        """
        Split text into overlapping chunks for embedding.
        
        Args:
            text: Input text to chunk
            chunk_size: Maximum size of each chunk (characters)
            chunk_overlap: Overlap between chunks (characters)
            
        Returns:
            List of text chunks
        """
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            
            # Try to end at a sentence boundary
            if end < text_length:
                # Look for sentence terminators
                terminators = ['.', '!', '?', '\n\n']
                for terminator in terminators:
                    last_pos = text.rfind(terminator, start, end)
                    if last_pos != -1:
                        end = last_pos + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - chunk_overlap
        
        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks
    
    def process_file(
        self,
        file_path: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Process a document file and return chunks with metadata.
        
        Args:
            file_path: Path to document file
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between chunks
            metadata: Additional metadata to include
            
        Returns:
            List of document chunks with metadata
        """
        # Extract text
        text = self.extract_text(file_path)
        
        # Chunk text
        chunks = self.chunk_text(text, chunk_size, chunk_overlap)
        
        # Prepare metadata
        path = Path(file_path)
        base_metadata = {
            'filename': path.name,
            'file_path': str(path),
            'file_size': path.stat().st_size,
            'file_type': path.suffix.lower(),
        }
        
        if metadata:
            base_metadata.update(metadata)
        
        # Create chunk documents
        documents = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = base_metadata.copy()
            chunk_metadata['chunk_id'] = i
            chunk_metadata['chunk_index'] = i
            chunk_metadata['total_chunks'] = len(chunks)
            
            documents.append({
                'content': chunk,
                'metadata': chunk_metadata,
                'id': f"{path.stem}_chunk_{i}"
            })
        
        logger.info(f"Processed {file_path} into {len(documents)} chunks")
        return documents


# Singleton instance
_document_processor: Optional[DocumentProcessor] = None


def get_document_processor() -> DocumentProcessor:
    """
    Get or create a singleton instance of DocumentProcessor.
    
    Returns:
        DocumentProcessor instance
    """
    global _document_processor
    if _document_processor is None:
        _document_processor = DocumentProcessor()
    return _document_processor
