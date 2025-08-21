from src.model.process_object import ProcessObject
from src.utils.log.log_utils import LogUtils
from src.services.file.pdf_to_image_service import PdfToImageService
from src.services.ocr.ocr_text_formatter_service import OCRTextFormatterService


class PDFToTextController:
    """
    Controller class for handling PDF to text conversion processes.
    
    This controller orchestrates the conversion of PDF documents to text by coordinating
    between PDF-to-image conversion and OCR text formatting services.
    """
    
    def __init__(
        self,
        pdf_to_image_service: PdfToImageService,
        ocr_text_formatter_service: OCRTextFormatterService,
        log_utils: LogUtils,
        num_rows: int = 35,
        num_columns: int = 20,
        space_redutor: int = 8, 
        font_size_regulator: int = 6
    ):
        """
        Initialize the PDFToTextController with required services and configuration.
        
        Args:
            pdf_to_image_service (PdfToImageService): Service for converting PDF to images
            ocr_text_formatter_service (OCRTextFormatterService): Service for OCR processing and text formatting
            log_utils (LogUtils): Logging utility instance
            num_rows (int, optional): Number of rows for text positioning. Defaults to 35.
            num_columns (int, optional): Number of columns for text positioning. Defaults to 20.
            space_redutor (int, optional): Factor for reducing spacing between text elements. Defaults to 8.
            font_size_regulator (int, optional): Factor for regulating font size calculations. Defaults to 6.
        """
        self._pdf_to_image_service = pdf_to_image_service
        self._ocr_text_formatter_service = ocr_text_formatter_service
        self._num_rows = num_rows
        self._num_columns = num_columns
        self._space_redutor = space_redutor
        self._font_size_regulator = font_size_regulator
        self._logger = log_utils.get_logger(__name__)
        
    def run(self, file_name: str, document_bits: bytes, pages_to_include: list[int] = None) -> str:
        """
        Execute the complete PDF to text conversion process.
        
        Args:
            file_name (str): Name of the PDF file being processed
            document_bits (bytes): Binary content of the PDF document
            pages_to_include (list[int], optional): List of page numbers to convert.
                                                   If None, all pages are converted.
            
        Returns:
            str: Formatted text extracted from the PDF document
            
        Raises:
            RuntimeError: If the document contains no extractable text
            Exception: If the OCR process fails for any reason
        """
        try:
            process_object = ProcessObject()
            
            process_object['file_name'] = file_name
            process_object['document_bits'] = document_bits
            process_object['pages_to_include'] = pages_to_include
            
            process_object = self._pdf_to_image_service.handle_request(
                process_object=process_object
            )
            
            process_object = self._ocr_text_formatter_service.handle_request(
                process_object=process_object,
                num_rows=self._num_rows,
                num_columns=self._num_columns,
                space_redutor=self._space_redutor,
                font_size_regulator=self._font_size_regulator
            )
            
            formated_text = process_object.get('text')
            
            if formated_text:
                return formated_text
            else:
                raise RuntimeError(f'Document {file_name}, do not contain text!')
        except Exception as e:
            raise Exception(f'Fail in OCR process: {e}')