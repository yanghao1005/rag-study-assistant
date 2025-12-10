"""
PDF parsing service using PyMuPDF (fitz)
Handles PDF text extraction with fallback to OCR for scanned documents
"""
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Optional
import mimetypes

from app.core.logging import logger


class PDFParsingError(Exception):
    """Custom exception for PDF parsing errors"""
    pass


def validate_pdf(file_path: str, max_size_mb: int = 10) -> bool:
    """
    Validate PDF file before processing
    
    Args:
        file_path: Path to PDF file
        max_size_mb: Maximum allowed file size in MB
        
    Returns:
        True if valid
        
    Raises:
        PDFParsingError: If validation fails
    """
    path = Path(file_path)
    
    # Check file exists
    if not path.exists():
        raise PDFParsingError(f"File not found: {file_path}")
    
    # Check file size
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > max_size_mb:
        raise PDFParsingError(
            f"File too large: {size_mb:.2f}MB (max: {max_size_mb}MB)"
        )
    
    # Check MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type != "application/pdf":
        raise PDFParsingError(f"Invalid file type: {mime_type}, expected PDF")
    
    # Try to open with PyMuPDF
    try:
        doc = fitz.open(file_path)
        if doc.is_encrypted:
            doc.close()
            raise PDFParsingError("PDF is password-protected")
        doc.close()
    except Exception as e:
        raise PDFParsingError(f"Cannot open PDF: {str(e)}")
    
    logger.info(f"PDF validation passed: {file_path} ({size_mb:.2f}MB)")
    return True


def extract_pdf_metadata(file_path: str) -> Dict:
    """
    Extract metadata from PDF
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Dictionary with metadata: total_pages, author, creation_date, etc.
    """
    try:
        doc = fitz.open(file_path)
        
        metadata = {
            "total_pages": len(doc),
            "author": doc.metadata.get("author", ""),
            "title": doc.metadata.get("title", ""),
            "subject": doc.metadata.get("subject", ""),
            "creator": doc.metadata.get("creator", ""),
            "producer": doc.metadata.get("producer", ""),
            "creation_date": doc.metadata.get("creationDate", ""),
            "modification_date": doc.metadata.get("modDate", ""),
            "format": doc.metadata.get("format", ""),
        }
        
        doc.close()
        logger.info(f"Extracted metadata from {file_path}: {metadata['total_pages']} pages")
        return metadata
        
    except Exception as e:
        logger.error(f"Failed to extract metadata: {e}")
        raise PDFParsingError(f"Metadata extraction failed: {str(e)}")


def extract_text_by_page(file_path: str) -> List[Dict]:
    """
    Extract text from PDF page by page
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        List of dicts: [{"page_num": 1, "text": "...", "char_count": 1500}]
    """
    try:
        doc = fitz.open(file_path)
        pages_data = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Extract text (preserves layout)
            text = page.get_text("text")
            
            # Get page dimensions for context
            rect = page.rect
            
            page_data = {
                "page_num": page_num + 1,  # 1-indexed for users
                "text": text,
                "char_count": len(text),
                "width": rect.width,
                "height": rect.height,
            }
            
            pages_data.append(page_data)
        
        doc.close()
        
        # Calculate average chars per page for quality check
        total_chars = sum(p["char_count"] for p in pages_data)
        avg_chars = total_chars / len(pages_data) if pages_data else 0
        
        logger.info(
            f"Extracted text from {len(pages_data)} pages, "
            f"avg {avg_chars:.0f} chars/page"
        )
        
        return pages_data
        
    except Exception as e:
        logger.error(f"Failed to extract text: {e}")
        raise PDFParsingError(f"Text extraction failed: {str(e)}")


def check_text_quality(pages_text: List[Dict]) -> bool:
    """
    Check if extracted text quality is sufficient
    
    Args:
        pages_text: List of page data from extract_text_by_page
        
    Returns:
        True if quality is good, False if likely scanned/image PDF
    """
    if not pages_text:
        return False
    
    total_chars = sum(p["char_count"] for p in pages_text)
    avg_chars = total_chars / len(pages_text)
    
    # Heuristic: < 100 chars per page indicates scanned/image PDF
    is_good_quality = avg_chars >= 100
    
    if not is_good_quality:
        logger.warning(
            f"Low text density detected: {avg_chars:.0f} chars/page "
            f"(threshold: 100). Likely scanned PDF."
        )
    
    return is_good_quality


def handle_scanned_pdf(file_path: str) -> List[Dict]:
    """
    Fallback handler for scanned PDFs using Unstructured with OCR
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        List of page data similar to extract_text_by_page
        
    Note:
        Requires: pip install unstructured[pdf] pytesseract
        And Tesseract OCR installed on system
    """
    logger.info(f"Attempting OCR extraction for scanned PDF: {file_path}")
    
    try:
        from unstructured.partition.pdf import partition_pdf
        
        # Use Unstructured's OCR capabilities
        elements = partition_pdf(
            filename=file_path,
            strategy="hi_res",  # Use high-res OCR
            infer_table_structure=True,
        )
        
        # Group elements by page
        pages_data = {}
        for element in elements:
            page_num = getattr(element.metadata, "page_number", 1)
            
            if page_num not in pages_data:
                pages_data[page_num] = {
                    "page_num": page_num,
                    "text": "",
                    "char_count": 0,
                }
            
            # Concatenate text from all elements on the page
            pages_data[page_num]["text"] += str(element) + "\n"
        
        # Convert to list and update char counts
        result = []
        for page_num in sorted(pages_data.keys()):
            page_data = pages_data[page_num]
            page_data["char_count"] = len(page_data["text"])
            result.append(page_data)
        
        logger.info(f"OCR extraction completed: {len(result)} pages")
        return result
        
    except ImportError:
        logger.error(
            "Unstructured library not installed. "
            "Install with: pip install unstructured[pdf] pytesseract"
        )
        raise PDFParsingError(
            "OCR not available. Cannot process scanned PDF. "
            "Install 'unstructured[pdf]' and Tesseract OCR."
        )
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        raise PDFParsingError(f"OCR extraction failed: {str(e)}")


def parse_pdf(file_path: str, max_size_mb: int = 10) -> tuple[Dict, List[Dict]]:
    """
    Main PDF parsing function with automatic fallback to OCR
    
    Args:
        file_path: Path to PDF file
        max_size_mb: Maximum allowed file size in MB
        
    Returns:
        Tuple of (metadata, pages_text)
        - metadata: dict with PDF metadata
        - pages_text: list of page data with extracted text
        
    Raises:
        PDFParsingError: If parsing fails
    """
    # Step 1: Validate
    validate_pdf(file_path, max_size_mb)
    
    # Step 2: Extract metadata
    metadata = extract_pdf_metadata(file_path)
    
    # Step 3: Extract text
    pages_text = extract_text_by_page(file_path)
    
    # Step 4: Quality check and fallback to OCR if needed
    if not check_text_quality(pages_text):
        logger.warning("Falling back to OCR for scanned PDF")
        try:
            pages_text = handle_scanned_pdf(file_path)
        except PDFParsingError as e:
            logger.warning(
                f"OCR fallback failed: {e}. "
                f"Proceeding with low-quality text extraction."
            )
            # Continue with original extraction even if poor quality
    
    return metadata, pages_text


# Convenience function for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pdf_parser.py <path_to_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    try:
        metadata, pages = parse_pdf(pdf_path)
        print(f"\n=== PDF Metadata ===")
        print(f"Pages: {metadata['total_pages']}")
        print(f"Author: {metadata['author']}")
        print(f"Title: {metadata['title']}")
        
        print(f"\n=== First Page Preview ===")
        if pages:
            print(f"Page 1 ({pages[0]['char_count']} chars):")
            print(pages[0]['text'][:500] + "...")
        
    except PDFParsingError as e:
        print(f"Error: {e}")
        sys.exit(1)
