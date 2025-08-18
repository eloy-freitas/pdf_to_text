import filetype


class FIletypeAdapter:
    def get_filetype(self, document_bits: bytes):        
        try:
            file_type = filetype.guess(document_bits)
            if file_type:
                return file_type.extension
            else:
                raise Exception('Unknown file format.')
        except Exception as e:
            raise Exception(f'Fail to check file format: {e}')
    