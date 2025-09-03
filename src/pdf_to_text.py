import argparse
from concurrent.futures import ThreadPoolExecutor

from .utils.log.log_utils import LogUtils


from .utils.log.log_utils import LogUtils
from .utils.file.adapters.pdf2image_adapter import PDF2ImageAdapter
from .utils.file.adapters.filetype_adapter import FIletypeAdapter

from .controller.pdf_to_text_controller import PDFToTextController

from .services.file.pdf_to_image_service import PdfToImageService
from .services.ocr.ocr_text_formatter_service import OCRTextFormatterService
from .services.ocr.ocr_adapters.easyocr_adapter import EasyOCRAdapter


def create_pdf_to_text_controller(
    languages: list[str] | None = None,
    max_workers: int = 2,
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
        log_utils=log_utils
    )
    
    return pdf_to_text_controller

def main():
    logger = LogUtils().get_logger(__name__)

    parser = argparse.ArgumentParser(description="OCR Formatter options.")

    parser.add_argument("-f", "--file_name", type=str, required=True, help="Input file name")
    parser.add_argument("-c", "--num_columns", type=int, required=False, default = 20, help="Number of columns of per page of the document (regulate the text position on x axis). default = 20")
    parser.add_argument("-r", "--num_rows", type=int, required=False, default = 35, help="Number of rows per page of the document (regulate the text position on y axis). default = 35")
    parser.add_argument("-s", "--space_redutor", type=int, required=False, default = 8, help="Used to smooth out the addition of tabs before each word on a line. (the higher the value, the fewer tabs will be added). default = 8")
    parser.add_argument("-w", "--max_workers", type=int, required=False, default = 2, help="Max of parallel page processing. This will increse the GPU usage. default = 2")
    parser.add_argument("-p", "--poppler_path", type=str, required=False, default = None, help="Path of installation of poppler binaries. Pass the path of the /bin folder in the folder of installation of the poppler. (Windows users https://github.com/oschwartz10612/poppler-windows/releases). default = None")
    parser.add_argument("-l", "--languages", type=str, required=False, default='en,pt', help="List of language of document. default = en,pt")
    parser.add_argument("-n", "--pages_to_include", type=str, required=False, default=None, help="List of pages to extract from PDF. default = None")
    parser.add_argument("-g", "--gpu", type=int, required=False, default=1, help="Flag to use GPU (1) or CPU (0) in OCR")
    parser.add_argument("-o", "--file_name_output", type=str, required=True, help="File name output")

    args = parser.parse_args()

    logger.info(f'file_name = {args.file_name}')
    logger.info(f'num_columns = {args.num_columns}')
    logger.info(f'num_rows = {args.num_rows}')
    logger.info(f'space_redutor = {args.space_redutor}')
    logger.info(f'max_workers = {args.max_workers}')
    logger.info(f'poppler_path = {args.poppler_path}')
    logger.info(f'languages = {args.languages}')
    logger.info(f'pages_to_include = {args.pages_to_include}')
    logger.info(f'gpu = {args.gpu}')
    logger.info(f'file_name_output = {args.file_name_output}')

    try:
        with open(f'{args.file_name}', "rb") as file:
            document_bits = file.read()
    except FileNotFoundError:
        logger.error(f"File {args.file_name} not found.")
        return

    gpu = True if args.gpu == 1 else False
    languages = args.languages.split(',') if args.languages else ['en', 'pt']
    pages_to_include = args.pages_to_include.split(',') if args.pages_to_include else None
    pages_to_include = [int(page) for page in pages_to_include] if pages_to_include else None

    if pages_to_include:
        pages_to_include.sort()

    pdf_to_text_controller = create_pdf_to_text_controller(
        languages=languages,
        poppler_path=args.poppler_path,
        max_workers=args.max_workers,
        gpu=gpu
    )    

    result = pdf_to_text_controller.extract_text_from_bytes(
        file_name=args.file_name, 
        document_bits=document_bits,
        pages_to_include=pages_to_include,
        num_rows=args.num_rows, 
        num_columns=args.num_columns,
        space_redutor=args.space_redutor
    )
    
    try:
        with open(f"{args.file_name_output}", "w") as file:
            file.write(result)
    except Exception as e:
        logger.error(f"Error writing to file {args.file_name_output}: {e}")
        return

if __name__ == "__main__":
    main()
    