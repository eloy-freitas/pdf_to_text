
from src.utils.file.file_utils import FileUtils
from src.model.process_object import ProcessObject


class PdfToImageService():
    def __init__(
        self,
        file_utils: FileUtils
    ) -> None:
        self._accetable_image_formats = ["png", "jpg", "jpeg", "bmp", "jiff"]
        self._file_utils = file_utils
         
    def _convert_pdf_to_images(self, file_name: str, file_type: str, document_bits: bytes):
        try:
            input_file_path = file_name.split('/')[-1].replace('.pdf', '')
            if file_type == 'pdf':
                data = self._file_utils.convert_pdf_from_bytes(
                    document_bits=document_bits, format='jpg'
                )
                
                images = {
                    f'{input_file_path}_____{i}.jpg': {'id': i, 'image': image} 
                    for i, image in enumerate(map(self._file_utils.pil_to_binary, data), start=1)
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
        
    def handle_hequest(self, process_object: ProcessObject):
        try:
            file_name = process_object.get('file_name')
            document_bits = process_object.get('document_bits')
            
            file_type = self._file_utils.get_file_type(document_bits)
            
            images = self._convert_pdf_to_images(
                file_name=file_name,
                file_type=file_type,
                document_bits=document_bits
            )
            
            process_object['images'] = images
            
            return process_object
        except Exception as e:
            raise Exception(f'Fail to convert PDF to Images \n{e}')
        
