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
        
    def read_text_from_image(self, image: bytes) -> list:
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

    def create_ocr_metadata(self, ocr_output: list) -> list[dict]:
        """
        Calculate normalized text positions from EasyOCR output.
        
        Processes the EasyOCR bounding box format and converts it to a standardized
        format with text content and position coordinates.
        
        Args:
            ocr_output (list): Raw EasyOCR output containing detection results
            
        Returns:
            list[dict]: List of dictionaries with normalized text position data
                       Each dict contains: {'text': str, 'x': float, 'y': float, 'text_length': int}
        """
        dataset = []
        for row in ocr_output:
            text = row[1]
            bounding_box = row[0]
            x = self.get_x_axis(bounding_box)
            y = self.get_y_axis(bounding_box)
            dataset.append({
                'text': text,
                'x': x, 
                'y': y, 
                'text_length': len(text)
            })

        return dataset
    

    def get_x_axis(self, bounding_box: object) -> float:
        """
        Extract the y-axis coordinates from the bounding box of OCR output.
        
        Args:
            bounding_box (object): Bounding box data from OCR output
            
        Returns:
            float: Value of x-axis coordinates
        """
        x = bounding_box[0][0]

        return x

    def get_y_axis(self, bounding_box: object) -> float:
        """
        Extract the y-axis coordinates from the bounding box of OCR output.
        
        Args:
            bounding_box (object): Bounding box data from OCR output
            
        Returns:
            float: Value of y-axis coordinates
        """
        y_start = bounding_box[0][1]
        y_end = bounding_box[1][1]
        y = ((y_end - y_start) / 2) + y_end
        return y
