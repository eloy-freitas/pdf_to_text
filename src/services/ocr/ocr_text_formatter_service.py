import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.utils.log.log_utils import LogUtils
from src.model.process_object import ProcessObject
from src.services.ocr.ocr_adapters.abstract_ocr_adapter import AbstractOCRAdapter


class OCRTextFormatterService:
    """
    Service for performing OCR text extraction and formatting from images.
    
    This service coordinates OCR processing across multiple images and formats
    the extracted text into a structured, readable format with proper spacing
    and positioning.
    """
    def __init__(
        self,
        ocr_adapter: AbstractOCRAdapter,
        ocr_pool_executor: ThreadPoolExecutor,
        log_utils: LogUtils
    ):
        self._ocr_adapter = ocr_adapter
        self._ocr_pool_executor = ocr_pool_executor
        self._logger = log_utils.get_logger(__name__)
    
    def _create_pandas_dataset(self, dataset: list[dict]) -> pd.DataFrame:
        """
        Extract text from multiple images using the configured OCR adapter.
        
        Args:
            images (dict[str, dict]): Dictionary mapping image names to image data
                                    Each value contains: {'id': int, 'image': bytes}
                                    
        Returns:
            dict[str, list[dict]]: Dictionary mapping image names to extracted text data
                                 Each text entry contains: {'text': str, 'x': float, 'y': float, 'text_length': int}
                                 
        Raises:
            Exception: If OCR text extraction fails for any image
        """
        df_dataset = pd.DataFrame(dataset)
        if df_dataset.empty:
            return df_dataset
        df_dataset.astype({'text': 'string'})
        max_y = max(df_dataset['y'])

        df_dataset['y'] = df_dataset['y'].apply(lambda y: max_y - y)
        
        return df_dataset

    def _create_axis_classes(
        self,
        dataset: pd.DataFrame, 
        axis_source_name: str, 
        axis_target_name: str, 
        axis_classes_name: str,
        num_classes: int = 15
    ) -> pd.DataFrame:
        """
        Format extracted text with proper positioning and spacing.
        
        This method organizes text elements into a grid-based layout using
        calculated positioning to maintain the original document structure.
        
        Args:
            images_with_text (dict[str, list[dict]]): Text data extracted from images
            num_rows (int): Number of rows in the positioning grid
            num_columns (int): Number of columns in the positioning grid  
            space_redutor (int): Factor for reducing spacing between text elements
            font_size_regulator (int): Factor for regulating font size calculations
            num_classes (int): Number of classes to create for axis normalization
        Returns:
            str: Formatted text with proper spacing and positioning
            
        Raises:
            Exception: If text formatting process fails
        """
        dataset[axis_classes_name] = pd.cut(
            dataset[axis_source_name], 
            bins=num_classes
        )

        classes = pd.DataFrame(
            dataset[axis_classes_name]
            .sort_values()
            .drop_duplicates()
        )

        classes[axis_target_name] = range(0, len(classes))
        
        return classes
    
    def _calculate_axis(
        self,
        dataset: pd.DataFrame,
        source_name: str,
        target_name: str,
        class_name: str,
        num_classes: int = 15
    ) -> pd.DataFrame:
        """
        Calculate axis positioning for text elements in the dataset.
        
        Creates axis classes and merges them with the dataset to establish
        normalized positioning coordinates for text elements.
        
        Args:
            dataset (pd.DataFrame): Input dataset with text positioning data
            source_name (str): Name of the source coordinate column
            target_name (str): Name of the target normalized coordinate column
            class_name (str): Name of the class categorization column
            num_classes (int, optional): Number of classes for axis normalization. Defaults to 15.
            
        Returns:
            pd.DataFrame: Dataset with calculated axis positions merged
        """
        classes = self._create_axis_classes(
            dataset=dataset, 
            axis_source_name=source_name, 
            axis_target_name=target_name, 
            axis_classes_name=class_name,
            num_classes=num_classes
        )

        merge = pd.merge(
            left=dataset, 
            right=classes, 
            on=[class_name], 
            how='left'
        )

        return merge

    def _map_text_positions(
        self, 
        dataset: pd.DataFrame, 
        num_rows: int=80,
        num_columns: int=40
    ) -> pd.DataFrame:
        """
        Map text elements to a grid-based coordinate system.
        
        Converts continuous x,y coordinates to discrete row and column positions
        to facilitate proper text layout reconstruction.
        
        Args:
            dataset (pd.DataFrame): Dataset with text and coordinate information
            num_rows (int, optional): Number of rows in the grid system. Defaults to 80.
            num_columns (int, optional): Number of columns in the grid system. Defaults to 40.
            
        Returns:
            pd.DataFrame: Dataset with added 'row' and 'column' positioning information
        """
        row_source_name = 'y'
        row_target_name = 'row'
        row_source_name_range = f'classes_{row_source_name}'

        rows = self._calculate_axis(
            dataset=dataset, 
            source_name=row_source_name, 
            target_name=row_target_name, 
            class_name=row_source_name_range,
            num_classes=num_rows
        )

        column_source_name = 'x'
        column_target_name = 'column'
        column_source_name_range = f'classes_{column_source_name}'
        
        columns = self._calculate_axis(
            dataset=rows, 
            source_name=column_source_name, 
            target_name=column_target_name,
            class_name=column_source_name_range,
            num_classes=num_columns
        )

        return columns

    def _extract_formated_text_from_image(
        self,
        ocr_output: object, 
        num_rows: int = 35, 
        num_columns: int = 20,
        space_redutor: int = 8,
        font_size_regulator: int = 6
    ) -> str:
        """
        Extract and format text from OCR output with proper positioning.
        
        Processes raw OCR output through the complete text formatting pipeline
        to produce structured, readable text with preserved layout.
        
        Args:
            ocr_output (object): Raw OCR output from the OCR adapter
            num_rows (int, optional): Number of rows for grid positioning. Defaults to 35.
            num_columns (int, optional): Number of columns for grid positioning. Defaults to 20.
            space_redutor (int, optional): Factor for reducing spacing between elements. Defaults to 8.
            font_size_regulator (int, optional): Factor for font size calculations. Defaults to 6.
            
        Returns:
            str: Formatted text with preserved layout and proper spacing
            
        Raises:
            Exception: If text formatting process fails
        """
        if not ocr_output:
            return ''
        try:
            dataset = self._ocr_adapter.create_ocr_metadata(ocr_output)
            
            dataset = self._create_pandas_dataset(dataset)
            dataset = self._map_text_positions(dataset, num_rows, num_columns)
            text = self._format_output(dataset, space_redutor, font_size_regulator)
            return text
        except Exception as e:
            raise Exception(f'Fail on format ocr output: \n {e}')

    def _format_line(
        self, 
        dataset: pd.DataFrame, 
        space_redutor: int = 8, 
        font_size_regulator: int = 6
    ) -> str:
        """
        Format a single line of text with appropriate spacing.
        
        Reconstructs text line spacing based on calculated positions and text lengths
        to maintain the original document layout.
        
        Args:
            dataset (pd.DataFrame): Dataset containing text elements for a single line
            space_redutor (int, optional): Factor for calculating spaces between text elements. Defaults to 8.
            font_size_regulator (int, optional): Factor for calculating text element widths. Defaults to 6.
            
        Returns:
            str: Formatted line with appropriate spacing between text elements
        """
        line_text = []
        pivot = 0
        spaces_len = 1
        
        for _, row in dataset.iterrows():
            start_text = row['x']
            
            if start_text >= pivot:
                spaces_len = int((start_text - pivot) / (2 * (space_redutor + 1)))
            else:
                spaces_len = 1
            spaces = ' ' * spaces_len                
            line_text.append(spaces)
            line_text.append(row['text'])
            pivot = start_text + row['text_length']
        
        return ''.join(line_text)

    def _format_output(
        self, 
        dataset: pd.DataFrame, 
        space_redutor: int = 8, 
        font_size_regulator: int = 6
    ) -> str:
        """
        Format the complete document output from processed text data.
        
        Assembles all text elements into a complete document with proper line ordering
        and formatting to recreate the original document structure.
        
        Args:
            dataset (pd.DataFrame): Complete dataset with positioned text elements
            space_redutor (int, optional): Factor for calculating horizontal spacing. Defaults to 8.
            font_size_regulator (int, optional): Factor for text width calculations. Defaults to 6.
            
        Returns:
            str: Complete formatted document text with preserved layout
        """
        dataset = dataset.sort_values(by=['row', 'column'],  ascending=[False, True])
        grouped = dataset.groupby('row')
        reconstructed_doc = []
        for _, group in grouped:
            reconstructed_doc.append(self._format_line(group, space_redutor, font_size_regulator))

        reconstructed_doc.reverse()

        final_text = '\n'.join(reconstructed_doc)
        
        return final_text
    
    def _process_document_text(
        self, 
        image_name: str, 
        page_id: int, 
        image: bytes, 
        num_rows: int = 35, 
        num_columns: int = 20,
        space_redutor: int = 8, 
        font_size_regulator: int = 6
    ) -> dict:
        """
        Process a single document page/image for text extraction.

        Handles the complete OCR and formatting pipeline for a single image,
        including logging and error handling.

        Args:
            image_name (str): Name identifier for the image being processed
            page_id (int): Sequential page number for ordering
            image (bytes): Binary image data to process
            num_rows (int, optional): Grid rows for positioning. Defaults to 35.
            num_columns (int, optional): Grid columns for positioning. Defaults to 20.
            space_redutor (int, optional): Spacing calculation factor. Defaults to 8.
            font_size_regulator (int, optional): Font size calculation factor. Defaults to 6.
            
        Returns:
            dict: Dictionary containing 'page_id' and 'formated_text' keys
        """
        self._logger.info(f'Extracting text from {image_name}')
        
        ocr_output = self._ocr_adapter.read_text_from_image(image)
        
        formated_text = self._extract_formated_text_from_image(
            ocr_output=ocr_output,
            num_rows=num_rows,
            num_columns=num_columns,
            space_redutor=space_redutor,
            font_size_regulator=font_size_regulator
        )
        
        return {'page_id': page_id, 'formated_text': formated_text}

    def handle_request(
        self, 
        process_object: ProcessObject, 
        num_rows: int = 35, 
        num_columns: int = 20,
        space_redutor: int = 8, 
        font_size_regulator: int = 6
    ) -> ProcessObject:
        """
        Handle the complete OCR text formatting request for multiple images.
        
        Processes all images in the ProcessObject concurrently using the thread pool,
        formats the extracted text, and assembles the final document.
        
        Args:
            process_object (ProcessObject): Container with images and metadata
            num_rows (int, optional): Grid rows for text positioning. Defaults to 35.
            num_columns (int, optional): Grid columns for text positioning. Defaults to 20.
            space_redutor (int, optional): Factor for horizontal spacing calculations. Defaults to 8.
            font_size_regulator (int, optional): Factor for font size calculations. Defaults to 6.
            
        Returns:
            ProcessObject: Updated ProcessObject with extracted text and cleaned up data
        """
        document_futures = [
            self._ocr_pool_executor.submit(
                self._process_document_text, 
                image_name,
                meta_data['id'],
                meta_data['image'],
                num_rows,
                num_columns,
                space_redutor,
                font_size_regulator
            ) 
            for image_name, meta_data in process_object['images'].items()
        ]
        
        document_results = [
            future.result() 
            for future in as_completed(document_futures)
        ]

        sorted_data = sorted(document_results, key=lambda x: x['page_id'])
        
        content = []
        for data in sorted_data:
            content.append(data['formated_text'])
            content.append(f"End of page {data['page_id']}") 
        full_document_text = '\n'.join(content) 
        process_object['text'] = full_document_text.lower()
        del process_object['images']
        del process_object['document_bits']

        return process_object
