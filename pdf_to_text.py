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