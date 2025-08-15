import filetype
from PIL import Image
from io import BytesIO
import pdf2image as pdf


class FileUtils:
    
    def pil_to_binary(self, image: Image):
        try:
            img_buffer = BytesIO()
            image.save(img_buffer, format='JPEG')
            img_buffer.seek(0)
            body = img_buffer.getvalue()
        except Exception as e:
            raise Exception(f'Error converting PIL object to binary. ERROR: {e}')
        else:
            return body
    
    def get_file_type(self, document_bits: str):        
        try:
            file_type = filetype.guess(document_bits)
            if file_type:
                return file_type.extension
            else:
                raise Exception('Unknow file format.')
        except Exception as e:
            raise Exception(f'Fail to check file format: {e}')
    
    def convert_pdf_from_bits(self, document_bits: str, format: str = 'jpg'):
        try:
            return pdf.convert_from_bytes(document_bits, fmt=format)
        except Exception as e:
            raise Exception(f'Fail to convert PDF to Images: {e}')