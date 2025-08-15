import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.utils.log.log_utils import LogUtils
from src.model.process_object import ProcessObject
from src.services.ocr.ocr_adapters.abstract_ocr_adapter import AbstractOCRAdapter


class OCRTextFormaterService:
    def __init__(
        self,
        ocr_adapter: AbstractOCRAdapter,
        ocr_pool_executor: ThreadPoolExecutor,
        log_utils: LogUtils
    ):
        self._ocr_adapter = ocr_adapter
        self._ocr_pool_executor = ocr_pool_executor
        self._logger = log_utils.get_logger(__name__)
    
    def create_dataset(self, dataset):
        tbl = pd.DataFrame(dataset).astype({'text': 'string'})
        max_y = max(tbl['y'])

        tbl['y'] = tbl['y'].apply(lambda y: max_y - y)
        
        return tbl

    def calculate_axis_frequency(
        self,
        dataset: pd.DataFrame, 
        axis_source_name: str, 
        axis_target_name: str, 
        axis_source_name_range: str,
        bins: int = 15
    ) -> pd.DataFrame:
        dataset[axis_source_name_range] = pd.cut(dataset[axis_source_name], bins=bins)
        faixas = pd.DataFrame(
            dataset[axis_source_name_range].sort_values().drop_duplicates()
        )

        faixas[axis_target_name] = range(0, len(faixas))
        
        return faixas

    def map_text_positions(
        self, 
        dataset: pd.DataFrame, 
        num_rows: int=80,
        num_columns: int=40
    ) -> pd.DataFrame:
        row_source_name = 'y'
        row_target_name = 'row'
        column_source_name = 'x'
        column_target_name = 'column'
        row_source_name_range = f'range_{row_source_name}'
        column_source_name_range = f'range_{column_source_name}'
        
        rows = self.calculate_axis_frequency(
            dataset=dataset, 
            axis_source_name=row_source_name, 
            axis_target_name=row_target_name, 
            axis_source_name_range=row_source_name_range,
            bins=num_rows
        )
        
        columns = self.calculate_axis_frequency(
            dataset=dataset, 
            axis_source_name=column_source_name, 
            axis_target_name=column_target_name,
            axis_source_name_range=column_source_name_range,
            bins=num_columns
        )

        merge = pd.merge(
            left=dataset, 
            right=rows, 
            on=[row_source_name_range], 
            how='left'
        )
        merge = pd.merge(
            left=merge, 
            right=columns, 
            on=[column_source_name_range], 
            how='left'
        )
        
        return merge

    def extract_formated_text_from_image(
        self,
        ocr_output: object, 
        num_rows: int = 35, 
        num_columns: int = 20
    ) -> str:
        dataset = self._ocr_adapter.calculate_text_position(ocr_output)
        dataset = self.create_dataset(dataset)
        dataset = self.map_text_positions(dataset, num_rows, num_columns)
        text = self.format_output(dataset)
        
        return text

    def format_line(self, dataset: pd.DataFrame):
        line_text = []
        prev_end = 0
        
        for _, row in dataset.iterrows():
            start_pos = row['x']
            
            if start_pos > prev_end:
                spaces = ' ' * int((start_pos - prev_end) / 6) 
                line_text.append(spaces)
            
            line_text.append(row['text'])
            prev_end = start_pos + row['text_size'] * 6
        
        return ''.join(line_text)

    def format_output(self, dataset: pd.DataFrame):
        dataset = dataset.sort_values(by=['row', 'column'],  ascending=[False, True])
        grouped = dataset.groupby('row')
        reconstructed_doc = []
        for _, group in grouped:
            reconstructed_doc.append(self.format_line(group))

        reconstructed_doc.reverse()

        final_text = '\n'.join(reconstructed_doc)
        
        return final_text
    
    def process_document_text(
        self, 
        image_name: str, 
        page_id: int, 
        image: object, 
        num_rows: int = 35, 
        num_columns: int = 20
    ):
        self._logger.info(f'Extracting text from {image_name}')
        
        ocr_output = self._ocr_adapter.extract_image_text(image)
        
        formated_text = self.extract_formated_text_from_image(
            ocr_output=ocr_output,
            num_rows=num_rows,
            num_columns=num_columns
        )
        
        return {'page_id': page_id, 'formated_text': formated_text}

    def handle_request(
        self, 
        process_object: ProcessObject, 
        num_rows: int = 35, 
        num_columns: int = 20
    ):
        document_futures = [
            self._ocr_pool_executor.submit(
                self.process_document_text, 
                image_name,
                meta_data['id'],
                meta_data['image'],
                num_rows,
                num_columns
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
