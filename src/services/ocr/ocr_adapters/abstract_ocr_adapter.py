from abc import ABC, abstractmethod


class AbstractOCRAdapter(ABC):
    def __init__(self):
        self._ocr_reader = None
        
    @abstractmethod
    def extract_image_text(self, image: bytes) -> object: ...
    
    @abstractmethod
    def calculate_text_position(self, ocr_output: object) -> list[dict]:...