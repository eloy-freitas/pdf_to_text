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
    gpu: bool = True
):
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
        num_rows=max(num_rows, 10),
        num_columns=max(num_columns, 35)
    )
    
    return pdf_to_text_controller.run(file_name=file_name, document_bits=document_bits)

if __name__ == '__main__':

    try:
        file_name = sys.argv[1]
    except ValueError as e:
        raise ValueError(f'Invalid file_name')
    try:
        num_rows_arg = sys.argv[2]
        num_columns_arg = sys.argv[3]
    except IndexError:
        num_rows_arg = None
        num_columns_arg = None
    
    if num_rows_arg:
        try:
            num_rows = int(num_rows_arg)
            print(num_rows)
        except ValueError as e:
            raise ValueError(f'num_rows must be int')
    else:
        num_rows = 35
        
    if num_columns_arg:
        try:
            num_columns = int(num_columns_arg)
            print(num_columns)
        except ValueError as e:
            raise ValueError(f'num_columns_arg must be int')
    else:
        num_columns = 20

    with open(file_name, "rb") as file:
        encoded_string = file.read()
    
    result = main(file_name, encoded_string, num_rows=num_rows, num_columns=num_columns)    
    
    with open(f'{file_name}.txt', "w") as file:
        file.write(result)