class ProcessObject(dict):
    """
    A dictionary-based data container for managing processing state across services.
    
    This class extends the built-in dict to provide a structured way to pass data
    between different services in the PDF-to-text conversion pipeline.
    """
    
    def __init__(self):
        """
        Initialize an empty ProcessObject dictionary.
        
        The ProcessObject is used to store and pass data such as file names,
        document bytes, images, and extracted text between different processing stages.
        """
        super().__init__()