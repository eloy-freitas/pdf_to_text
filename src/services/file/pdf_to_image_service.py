from PIL import Image
from io import BytesIO
from src.model.process_object import ProcessObject
from src.utils.file.adapters.filetype_adapter import FIletypeAdapter
from src.utils.file.adapters.pdf2image_adapter import PDF2ImageAdapter


class PdfToImageService:
    """
    Service for converting PDF documents and images to a standardized image format.
    
    This service handles the conversion of PDF files to images and validates
    acceptable image formats for further OCR processing.
    """
    
    def __init__(
        self,
        filetype_adapter: FIletypeAdapter,
        pdf2image_adapter: PDF2ImageAdapter
    ) -> None:
        """
        Initialize the PdfToImageService with required adapters.
        
        Args:
            filetype_adapter (FIletypeAdapter): Adapter for detecting file types
            pdf2image_adapter (PDF2ImageAdapter): Adapter for PDF to image conversion
        """
        self._accetable_image_formats = ["png", "jpg", "jpeg", "bmp", "jiff"]
        self._filetype_adapter = filetype_adapter
        self._pdf2image_adapter = pdf2image_adapter
         
    def _convert_pdf_to_images(
        self, 
        file_name: str, 
        file_type: str, 
        document_bits: bytes,
        pages_to_include: list[int] = None
    ) -> dict[str, bytes]:
        """
        Convert PDF document or validate image format and prepare for OCR processing.
        
        Args:
            file_name (str): Name of the input file
            file_type (str): Detected file type extension
            document_bits (bytes): Binary content of the document
            pages_to_include (list[int], optional): List of page numbers to convert.
                                                   If None, all pages are converted.
            
        Returns:
            dict[str, bytes]: Dictionary mapping image names to their binary data and metadata
            
        Raises:
            Exception: If file type is not supported or conversion fails
        """
        try:
            input_file_path = file_name.split('/')[-1].replace('.pdf', '')
            if file_type == 'pdf':
                data = self._pdf2image_adapter.convert_pdf_from_bytes(
                    document_bits=document_bits, format='jpg', pages_to_include=pages_to_include
                )
                
                images = {
                    f'{input_file_path}_____{i}.jpg': {'id': i, 'image': image} 
                    for i, image in enumerate(map(self._pil_to_binary, data), start=1)
                }
            elif file_type in self._accetable_image_formats:
                images = {input_file_path: {'id': 1, 'image': document_bits} }
            else:
                raise Exception(
                    f'Invalid file type {file_type}.'
                    f'The application only support PDF and following images formats:'
                    f'{self._accetable_image_formats}'
                )
            return images
        except Exception as e:
            raise Exception(f'Fail on convert PDF to JPG. Error: \n{e}')
        
    def _pil_to_binary(self, image: Image) -> bytes:
        """
        Convert a PIL Image object to binary JPEG format.
        
        Args:
            image (Image): PIL Image object to convert
            
        Returns:
            bytes: Binary representation of the image in JPEG format
            
        Raises:
            Exception: If image conversion fails
        """
        try:
            img = image.convert('RGB') if image.mode not in ('RGB',) else image
            with BytesIO() as img_buffer:
                img.save(img_buffer, format='JPEG')
                img_buffer.seek(0)
                body = img_buffer.getvalue()
        except Exception as e:
            raise Exception(f'Error converting PIL object to binary. ERROR: {e}')
        else:
            return body
        
    def handle_request(self, process_object: ProcessObject) -> ProcessObject:
        """
        Process a document conversion request and add converted images to the process object.
        
        Args:
            process_object (ProcessObject): Container with file name and document data
            
        Returns:
            ProcessObject: Updated process object containing converted images
            
        Raises:
            Exception: If PDF to image conversion fails
        """
        try:
            file_name = process_object.get('file_name')
            document_bits = process_object.get('document_bits')
            pages_to_include = process_object.get('pages_to_include')
            
            file_type = self._filetype_adapter.get_filetype(document_bits)
            
            images = self._convert_pdf_to_images(
                file_name=file_name,
                file_type=file_type,
                document_bits=document_bits,
                pages_to_include=pages_to_include
            )
            
            process_object['images'] = images
            
            return process_object
        except Exception as e:
            raise Exception(f'Fail to convert PDF to Images \n{e}')