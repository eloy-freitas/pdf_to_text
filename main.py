from concurrent.futures import ThreadPoolExecutor

from src.utils.log.log_utils import LogUtils
from src.utils.file.file_utils import FileUtils

from src.controller.pdf_to_text_controller import PDFToTextController

from src.services.file.pdf_to_image_service import PdfToImageService
from src.services.ocr.ocr_text_formater_service import OCRTextFormaterService
from src.services.ocr.ocr_adapters.easyocr_adapter import EasyOCRAdapter

def main(
    file_name: str,
    document_bits: str,
    lenguages: list[str] = ['en', 'pt'],
    max_workers: int = 3,
    num_rows: int = 35,
    num_colums: int = 20
):
    log_utils = LogUtils()
    file_utils = FileUtils()
    
    ocr_pool_executor = ThreadPoolExecutor(max_workers=max_workers)
    
    easyocr_adapter = EasyOCRAdapter(
        lenguages=lenguages
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
        num_columns=num_colums
    )
    
    return pdf_to_text_controller.run(file_name=file_name, document_bits=document_bits)

if __name__ == '__main__':
    
    file_name = 'AP - PAMELA MADEIRA MARQUES - ARGO.pdf'

    with open(file_name, "rb") as file:
        encoded_string = file.read()
    
    #print(encoded_string)
    result = main(file_name, encoded_string, num_colums=30, num_rows=50)    
    
    with open(f'{file_name}.txt', "w") as file:
        file.write(result)