import filetype


class FiletypeAdapter:
    """
    Adapter for detecting file types using the filetype library.
    
    This adapter provides a standardized interface for file type detection
    based on file content analysis rather than file extensions.
    """
    def get_filetype(self, document_bits: bytes):
        """
        Detect the file type from binary document data.
        
        Uses the filetype library to analyze file headers and content
        to determine the actual file type, regardless of file extension.
        
        Args:
            document_bits (bytes): Binary content of the file to analyze
            
        Returns:
            str: Detected file type (e.g., 'pdf', 'png', 'jpg', 'jpeg')
                Returns lowercase file extension for supported formats
                
        Raises:
            Exception: If file type detection fails or encounters an error
        """
        try:
            file_type = filetype.guess(document_bits)
            if file_type:
                return file_type.extension
            else:
                raise Exception('Unknown file format.')
        except Exception as e:
            raise Exception(f'Fail to check file format: {e}')
    