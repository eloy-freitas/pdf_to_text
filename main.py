import argparse
from concurrent.futures import ThreadPoolExecutor

from src.utils.log.log_utils import LogUtils
from src.utils.file.adapters.pdf2image_adapter import PDF2ImageAdapter
from src.utils.file.adapters.filetype_adapter import FIletypeAdapter

from src.controller.pdf_to_text_controller import PDFToTextController

from src.services.file.pdf_to_image_service import PdfToImageService
from src.services.ocr.ocr_text_formatter_service import OCRTextFormatterService
from src.services.ocr.ocr_adapters.easyocr_adapter import EasyOCRAdapter


def create_controller(
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

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="OCR Formatter options.")

    parser.add_argument("-f", "--file_name", type=str, required=True, help="Input file name")
    parser.add_argument("-c", "--num_columns", type=int, required=False, default = 20, help="Number of columns of per page of the document (regulate the text position on x axis). default = 20")
    parser.add_argument("-r", "--num_rows", type=int, required=False, default = 35, help="Number of rows per page of the document (regulate the text position on y axis). default = 35")
    parser.add_argument("-s", "--space_redutor", type=int, required=False, default = 8, help="Used to smooth out the addition of tabs before each word on a line. (the higher the value, the fewer tabs will be added). default = 8")
    parser.add_argument("-z", "--font_size_regulator", type=int, required=False, default = 6, help="Used to compensate for spacing based on the font of the text in the document. If your document contains text in a large font size, consider increasing this value so the text doesn't appear too sparse. default = 6")
    parser.add_argument("-w", "--max_workers", type=int, required=False, default = 2, help="Max of parallel page processing. This will increse the GPU usage. default = 2")
    parser.add_argument("-p", "--poppler_path", type=str, required=False, default = None, help="Path of installation of poppler binaries. Pass the path of the /bin folder in the folder of installation of the poppler. (Window users https://github.com/oschwartz10612/poppler-windows/releases). default = None")
    parser.add_argument("-o", "--file_name_output", type=str, required=True, help="File name output")
    parser.add_argument("-l", "--languages", type=list, required=False, default=['en', 'pt'], help="Language of document. default = ['en', 'pt']")

    args = parser.parse_args()

    with open(f'{args.file_name}', "rb") as file:
        document_bits = file.read()
    
    pdf_to_text_controller = create_controller(
        languages=args.languages,
        num_rows=args.num_rows, 
        num_columns=args.num_columns,
        space_redutor=args.space_redutor,
        font_size_regulator=args.font_size_regulator,
        poppler_path=args.poppler_path,
        max_workers=args.max_workers
    )    

    result = pdf_to_text_controller.run(file_name=args.file_name, document_bits=document_bits)
    
    with open(fr"{args.file_name}.txt", "w") as file:
        file.write(result)