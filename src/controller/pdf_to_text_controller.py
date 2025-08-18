from src.model.process_object import ProcessObject
from src.utils.log.log_utils import LogUtils
from src.services.file.pdf_to_image_service import PdfToImageService
from src.services.ocr.ocr_text_formater_service import OCRTextFormaterService

class PDFToTextController:
    
    def __init__(
        self,
        pdf_to_image_service: PdfToImageService,
        ocr_text_formater_service: OCRTextFormaterService,
        log_utils: LogUtils,
        num_rows: int = 35,
        num_columns: int = 20
    ):
        self._pdf_to_image_service = pdf_to_image_service
        self._ocr_text_formater_service = ocr_text_formater_service
        self._num_rows = num_rows
        self._num_columns = num_columns
        self._logger = log_utils.get_logger(__name__)
        
    def run(self, file_name: str, document_bits: bytes):
        try:
            process_object = ProcessObject()
            
            process_object['file_name'] = file_name
            process_object['document_bits'] = document_bits
            
            process_object = self._pdf_to_image_service.handle_hequest(
                process_object=process_object
            )
            
            process_object = self._ocr_text_formater_service.handle_request(
                process_object=process_object,
                num_rows=self._num_rows,
                num_columns=self._num_columns
            )
            
            formated_text = process_object.get('text')
            
            if formated_text:
                return formated_text
            else:
                raise RuntimeError(f'Document {file_name}, do not contain text!')
        except Exception as e:
            raise Exception(f'Fail in OCR process: {e}')
        
        