import sys
from concurrent.futures import ThreadPoolExecutor

from src.utils.log.log_utils import LogUtils
from src.utils.file.file_utils import FileUtils

from src.controller.pdf_to_text_controller import PDFToTextController

from src.services.file.pdf_to_image_service import PdfToImageService
from src.services.ocr.ocr_text_formater_service import OCRTextFormaterService
from src.services.ocr.ocr_adapters.easyocr_adapter import EasyOCRAdapter


def main(
    file_name: str,
    document_bits: bytes,
    languages: list[str] | None = None,
    max_workers: int = 2,
    num_rows: int = 35,
    num_columns: int = 20,
    space_redutor: int = 8, 
    font_size_regulator: int = 6,
    gpu: bool = True
):
    if num_rows:
        try:
            num_rows = int(num_rows)
        except ValueError as e:
            raise ValueError(f'num_rows must be int')
    else:
        num_rows = 35
        
    if num_columns:
        try:
            num_columns = int(num_columns)
        except ValueError as e:
            raise ValueError(f'num_columns must be int')
    else:
        num_columns = 20

    if space_redutor:
        try:
            space_redutor = abs(int(space_redutor))
        except ValueError as e:
            raise ValueError(f'space_redutor must be int and positive')
    else:
        space_redutor = 8
    
    if font_size_regulator:
        try:
            font_size_regulator = abs(int(font_size_regulator))
        except ValueError as e:
            raise ValueError(f'font_size_regulator must be int and positive')
    else:
        font_size_regulator = 6

    languages = languages or ['en', 'pt']
    log_utils = LogUtils()
    file_utils = FileUtils()
    
    ocr_pool_executor = ThreadPoolExecutor(max_workers=max_workers)
    
    easyocr_adapter = EasyOCRAdapter(
        languages=languages,
        gpu=gpu
    )
    
    pdf_to_image_service = PdfToImageService(
        file_utils=file_utils
    )
    
    ocr_text_formater_service = OCRTextFormaterService(
        log_utils=log_utils,
        ocr_adapter=easyocr_adapter,
        ocr_pool_executor=ocr_pool_executor
        
    )
    
    pdf_to_text_controller = PDFToTextController(
        pdf_to_image_service=pdf_to_image_service,
        ocr_text_formater_service=ocr_text_formater_service,
        log_utils=log_utils,
        num_rows=num_rows,
        num_columns=num_columns,
        space_redutor=space_redutor,
        font_size_regulator=font_size_regulator
    )
    
    return pdf_to_text_controller.run(file_name=file_name, document_bits=document_bits)

if __name__ == '__main__':

    try:
        file_name = sys.argv[1]
    except IndexError as e:
        raise IndexError(f'Invalid file_name')
    try:
        num_rows = sys.argv[2]
    except IndexError:
        num_rows = None
    try:
        num_columns = sys.argv[3]
    except IndexError:
        num_columns = None
    try:
        space_redutor = sys.argv[4]
    except IndexError:
        space_redutor = None
    try:
        font_size_regulator = sys.argv[5]
    except IndexError:
        font_size_regulator = None

    with open(file_name, "rb") as file:
        encoded_string = file.read()
    
    result = main(
        file_name, 
        encoded_string, 
        num_rows=num_rows, 
        num_columns=num_columns,
        space_redutor=space_redutor,
        font_size_regulator=font_size_regulator
    )    
    
    with open(f'{file_name}.txt', "w") as file:
        file.write(result)