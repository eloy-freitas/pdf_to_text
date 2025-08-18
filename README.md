# PDF to Text Converter

A Python application that converts PDF documents and images to formatted text using OCR (Optical Character Recognition) technology.

## Overview

This application provides a complete pipeline for extracting and formatting text from PDF documents and various image formats. It uses advanced OCR capabilities with spatial text positioning to maintain the original document layout as much as possible.


## Features

- **Multi-format Support**: Handles PDF files and common image formats (PNG, JPG, JPEG, BMP, JIFF)
- **OCR Processing**: Uses EasyOCR for text extraction with multi-language support
- **Spatial Text Formatting**: Preserves document layout through intelligent text positioning
- **Concurrent Processing**: Multi-threaded OCR processing for improved performance
- **Configurable Parameters**: Adjustable formatting parameters for different document types
- **Comprehensive Logging**: Built-in logging system for monitoring and debugging

## Architecture

### Core Components

#### Controller Layer
- **PDFToTextController**: Main orchestrator that coordinates the entire conversion process

#### Service Layer
- **PdfToImageService**: Handles PDF to image conversion and file type detection
- **OCRTextFormatterService**: Manages OCR processing and text formatting with spatial awareness

#### Model Layer
- **ProcessObject**: Data transfer object that carries information through the processing pipeline

#### Adapter Layer
- **AbstractOCRAdapter**: Abstract base class for OCR implementations
- **EasyOCRAdapter**: Concrete implementation using the EasyOCR library
- **FIletypeAdapter**: File type detection using the filetype library
- **PDF2ImageAdapter**: PDF to image conversion using pdf2image library

#### Utility Layer
- **LogUtils**: Centralized logging functionality

### Design Patterns

- **Adapter Pattern**: Used for integrating external libraries (EasyOCR, pdf2image, filetype)
- **Dependency Injection**: Services receive their dependencies through constructor injection
- **Template Method**: Abstract OCR adapter defines the interface for different OCR implementations

## Class diagram
```
classDiagram
    class PDFToTextController {
        -PdfToImageService _pdf_to_image_service
        -OCRTextFormatterService _ocr_text_formatter_service
        -int _num_rows
        -int _num_columns
        -int _space_redutor
        -int _font_size_regulator
        -Logger _logger
        +__init__(pdf_to_image_service, ocr_text_formatter_service, log_utils, num_rows, num_columns, space_redutor, font_size_regulator)
        +run(file_name: str, document_bits: bytes) str
    }

    class ProcessObject {
        +__init__()
    }

    class PdfToImageService {
        -list _acceptable_image_formats
        -FIletypeAdapter _filetype_adapter
        -PDF2ImageAdapter _pdf2image_adapter
        +__init__(filetype_adapter, pdf2image_adapter)
        -_convert_pdf_to_images(file_name: str, file_type: str, document_bits: bytes) dict
        -_pil_to_binary(image: Image) bytes
        +handle_request(process_object: ProcessObject) dict
    }

    class OCRTextFormatterService {
        -AbstractOCRAdapter _ocr_adapter
        -ThreadPoolExecutor _ocr_pool_executor
        -Logger _logger
        +__init__(ocr_adapter, ocr_pool_executor, log_utils)
        -_create_dataset(dataset) DataFrame
        -_calculate_axis_frequency(dataset, axis_source_name, axis_target_name, axis_source_name_range, bins) DataFrame
        -_map_text_positions(dataset, num_rows, num_columns) DataFrame
        -_extract_formated_text_from_image(ocr_output, num_rows, num_columns, space_redutor, font_size_regulator) str
        -_format_line(dataset, space_redutor, font_size_regulator) str
        -_format_output(dataset, space_redutor, font_size_regulator) str
        -_process_document_text(image_name, page_id, image, num_rows, num_columns, space_redutor, font_size_regulator) dict
        +handle_request(process_object, num_rows, num_columns, space_redutor, font_size_regulator) ProcessObject
    }

    class AbstractOCRAdapter {
        <<abstract>>
        #_ocr_reader
        +__init__()
        +extract_image_text(image: bytes)* object
        +calculate_text_position(ocr_output: object)* list[dict]
    }

    class EasyOCRAdapter {
        +__init__(languages: list[str], gpu: bool)
        +extract_image_text(image) object
        +calculate_text_position(ocr_output: object) list[dict]
    }

    class LogUtils {
        +__init__()
        +get_logger(name) Logger
    }

    class FIletypeAdapter {
        +get_filetype(document_bits: bytes) str
    }

    class PDF2ImageAdapter {
        -str _poppler_path
        +__init__(poppler_path: str)
        +convert_pdf_from_bytes(document_bits: bytes, format: str) list
    }

    %% Inheritance
    ProcessObject --|> dict
    EasyOCRAdapter --|> AbstractOCRAdapter

    %% Dependencies
    PDFToTextController --> PdfToImageService
    PDFToTextController --> OCRTextFormatterService
    PDFToTextController --> LogUtils
    PDFToTextController --> ProcessObject

    PdfToImageService --> FIletypeAdapter
    PdfToImageService --> PDF2ImageAdapter
    PdfToImageService --> ProcessObject

    OCRTextFormatterService --> AbstractOCRAdapter
    OCRTextFormatterService --> LogUtils
    OCRTextFormatterService --> ProcessObject

```

## Installation

### Prerequisites

```bash
# Install required system dependencies (Ubuntu/Debian)
sudo apt-get install poppler-utils

# For other systems, ensure poppler-utils is available