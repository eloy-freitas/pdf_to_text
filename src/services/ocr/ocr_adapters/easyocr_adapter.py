import easyocr
from .abstract_ocr_adapter import AbstractOCRAdapter


class EasyOCRAdapter(AbstractOCRAdapter):
    """
    Concrete implementation of AbstractOCRAdapter using the EasyOCR library.
    
    This adapter provides OCR functionality using the EasyOCR engine,
    with support for multiple languages and GPU acceleration.
    """
    
    def __init__(self, languages: list[str], gpu: bool = False):
        """
        Initialize the EasyOCR adapter with specified languages and GPU settings.
        
        Args:
            languages (list[str]): List of language codes for OCR recognition
            gpu (bool, optional): Whether to use GPU acceleration. Defaults to False.
                                If GPU initialization fails, automatically falls back to CPU.
        """
        super().__init__()
        try:
            self._ocr_reader = easyocr.Reader(languages, gpu=gpu)
        except Exception:
            self._ocr_reader = easyocr.Reader(languages, gpu=False)
        
    def extract_image_text(self, image: bytes) -> list:
        """
        Extract text from an image using EasyOCR.
        
        Args:
            image (bytes): Binary image data to process
            
        Returns:
            list: EasyOCR output containing text detection results
                 Each element contains: [bounding_box, text, confidence]
                 
        Raises:
            Exception: If text extraction fails
        """
        try:
            return self._ocr_reader.readtext(image)
        except Exception as e:
            raise Exception(f'Fail to extract text from OCR: \n{e}')

    def calculate_text_position(self, ocr_output: list) -> list[dict]:
        """
        Calculate normalized text positions from EasyOCR output.
        
        Processes the EasyOCR bounding box format and converts it to a standardized
        format with text content and position coordinates.
        
        Args:
            ocr_output (list): Raw EasyOCR output containing detection results
            
        Returns:
            list[dict]: List of dictionaries with normalized text position data
                       Each dict contains: {'text': str, 'x': float, 'y': float, 'text_size': int}
        """
        dataset = []
        for row in ocr_output:
            text = row[1]
            box = row[0]
            x_start = box[0][0]
            y_start = box[0][1]
            y_end = box[1][1]
            x = x_start
            text_size = len(text)
            y = ((y_end - y_start) / 2) + y_end
            dataset.append({
                'text': text,
                'x': x, 
                'y': y, 
                'text_size': text_size
            })

        return dataset