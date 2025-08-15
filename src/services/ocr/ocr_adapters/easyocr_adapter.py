import easyocr
from .abstract_ocr_adapter import AbstractOCRAdapter


class EasyOCRAdapter(AbstractOCRAdapter):
    def __init__(self, lenguages):
        super().__init__()
        self._ocr_reader = easyocr.Reader(lenguages)
        
    def extract_image_text(self, image):
        try:
            return self._ocr_reader.readtext(image)
        except Exception as e:
            raise Exception(f'Fail to extract text from OCR: \n{e}')

    def calculate_text_position(self, ocr_output: object) -> list[dict]:
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