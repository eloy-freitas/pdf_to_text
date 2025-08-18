from concurrent.futures import ThreadPoolExecutor

from src.utils.log.log_utils import LogUtils
from src.utils.file.adapters.pdf2image_adapter import PDF2ImageAdapter
from src.utils.file.adapters.filetype_adapter import FIletypeAdapter

from src.controller.pdf_to_text_controller import PDFToTextController

from src.services.file.pdf_to_image_service import PdfToImageService
from src.services.ocr.ocr_text_formatter_service import OCRTextFormatterService
from src.services.ocr.ocr_adapters.easyocr_adapter import EasyOCRAdapter


def create_pdf_to_text_controller(
    languages: list[str] | None = None,
    max_workers: int = 2,
    num_rows: int = 35,
    num_columns: int = 20,
    space_redutor: int = 8, 
    font_size_regulator: int = 6,
    gpu: bool = True,
    poppler_path: str = None
):
    """
    Create and return a fully wired PDFToTextController.
    
    This factory configures and composes the necessary adapters, services, and utilities
    to convert PDF pages to text using OCR. It instantiates logging utilities, a
    PDF-to-image adapter (optionally using a poppler binary path), a file-type adapter,
    an EasyOCR adapter (with optional GPU), a ThreadPoolExecutor for concurrent OCR tasks,
    and wiring services for PDF-to-image conversion and OCR text formatting, then returns
    the assembled PDFToTextController.
    
    Parameters:
        languages (list[str] | None): OCR languages to load (defaults to ["en", "pt"]).
        max_workers (int): Maximum worker threads for OCR concurrency (passed to ThreadPoolExecutor).
        num_rows (int): Number of text rows used by the controller's formatter.
        num_columns (int): Number of text columns used by the controller's formatter.
        space_redutor (int): Space reduction parameter for the formatter.
        font_size_regulator (int): Font-size regulation parameter for the formatter.
        gpu (bool): Whether to enable GPU in the EasyOCR adapter.
        poppler_path (str | None): Optional path to poppler binaries for PDF rendering.
    
    Returns:
        PDFToTextController: A controller instance ready to convert PDFs to text.
    
    Notes:
        - The function creates a ThreadPoolExecutor; the executor's lifecycle is managed
          by the components that receive it. Exceptions raised during component creation
          will propagate to the caller.
    """
    languages = languages or ["en", "pt"]
    log_utils = LogUtils()
    pdf2image_adapter = PDF2ImageAdapter(poppler_path=poppler_path)
    filetype_adapter = FIletypeAdapter()
    
    ocr_pool_executor = ThreadPoolExecutor(max_workers=max_workers)
    
    easyocr_adapter = EasyOCRAdapter(
        languages=languages,
        gpu=gpu
    )
    
    pdf_to_image_service = PdfToImageService(
        filetype_adapter=filetype_adapter,
        pdf2image_adapter=pdf2image_adapter
    )
    
    ocr_text_formatter_service = OCRTextFormatterService(
        log_utils=log_utils,
        ocr_adapter=easyocr_adapter,
        ocr_pool_executor=ocr_pool_executor
        
    )
    
    pdf_to_text_controller = PDFToTextController(
        pdf_to_image_service=pdf_to_image_service,
        ocr_text_formatter_service=ocr_text_formatter_service,
        log_utils=log_utils,
        num_rows=num_rows,
        num_columns=num_columns,
        space_redutor=space_redutor,
        font_size_regulator=font_size_regulator
    )
    
    return pdf_to_text_controller