from abc import ABC, abstractmethod


class AbstractOCRAdapter(ABC):
    """
    Abstract base class for OCR (Optical Character Recognition) adapters.
    
    This class defines the interface that all OCR adapters must implement
    to ensure consistent behavior across different OCR engines.
    """
    
    def __init__(self):
        """
        Initialize the abstract OCR adapter.
        
        Sets up the base OCR reader attribute that concrete implementations
        will populate with their specific OCR engine instances.
        """
        self._ocr_reader = None
        
    @abstractmethod
    def read_text_from_image(self, image: bytes) -> object:
        """
        Extract text from an image using OCR technology.
        
        Args:
            image (bytes): Binary image data to process
            
        Returns:
            object: OCR output in the format specific to the OCR engine implementation
        """
        ...
    
    @abstractmethod
    def create_ocr_metadata(self, ocr_output: object) -> list[dict]:
        """
        Calculate and normalize text positions from OCR output.
        
        Args:
            ocr_output (object): Raw output from the OCR engine
            
        Returns:
            list[dict]: List of dictionaries containing text and position information
                       Each dict should contain: {'text': str, 'x': float, 'y': float, 'text_length': int}
        """
        ...
