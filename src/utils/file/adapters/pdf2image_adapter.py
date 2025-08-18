import pdf2image as pdf


class PDF2ImageAdapter:
    def __init__(
        self,
        poppler_path: str = None
    ):
        self._poppler_path = poppler_path

    def convert_pdf_from_bytes(self, document_bits: bytes, format: str = 'jpg'):
        try:
            return pdf.convert_from_bytes(
                document_bits, 
                fmt=format, 
                poppler_path=self._poppler_path
            )
        except Exception as e:
            raise Exception(f'Fail to convert PDF to Images: {e}')