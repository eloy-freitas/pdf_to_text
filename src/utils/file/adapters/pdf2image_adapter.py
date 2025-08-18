import pdf2image as pdf
from PIL import Image


class PDF2ImageAdapter:
    """
    Adapter for converting PDF documents to images using the pdf2image library.
    
    This adapter provides a standardized interface for PDF to image conversion
    operations, handling various image formats and conversion parameters.
    """
    def __init__(
        self,
        poppler_path: str = None
    ):
        self._poppler_path = poppler_path

    def convert_pdf_from_bytes(self, document_bits: bytes, format: str = 'jpg') -> list[Image.Image]:
        """
        Convert PDF document from bytes to a list of PIL Image objects.
        
        Takes binary PDF data and converts each page to a separate image
        in the specified format using the pdf2image library.
        
        Args:
            document_bits (bytes): Binary content of the PDF document
            format (str, optional): Output image format. Defaults to 'jpg'.
                                  Supported formats: 'jpg', 'png', 'bmp', etc.
                                  
        Returns:
            list[Image.Image]: List of PIL Image objects, one for each PDF page
                              Images are ordered sequentially by page number
                              
        Raises:
            Exception: If PDF conversion fails due to invalid PDF data,
                      memory issues, or unsupported format
        """
        try:
            return pdf.convert_from_bytes(
                document_bits, 
                fmt=format, 
                poppler_path=self._poppler_path
            )
        except Exception as e:
            raise Exception(f'Fail to convert PDF to Images: {e}')