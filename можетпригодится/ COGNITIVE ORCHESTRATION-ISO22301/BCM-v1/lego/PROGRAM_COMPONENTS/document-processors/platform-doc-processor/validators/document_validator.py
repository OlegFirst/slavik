# Восстановленная реализация валидации загрузки документов

from typing import List, Dict, Union, Optional
import os
import magic
import hashlib

# Настройки ограничений для загружаемых документов
ALLOWED_MIME_TYPES = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'application/vnd.oasis.opendocument.text'
]

MAX_FILE_SIZE_MB = 10  # Максимальный размер файла в МБ
MAX_FILES_PER_REQUEST = 5  # Максимальное количество файлов в одном запросе

class DocumentValidationError(Exception):
    """Исключение для ошибок валидации документа."""
    pass

def validate_document(file_data: bytes, filename: str) -> Dict[str, Union[str, int]]:
    """
    Валидирует загружаемый документ.
    
    Args:
        file_data: Содержимое файла в виде байтов
        filename: Имя файла
        
    Returns:
        Dict с метаданными валидного документа
        
    Raises:
        DocumentValidationError: Если документ не проходит валидацию
    """
    # Проверка размера файла
    file_size_mb = len(file_data) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise DocumentValidationError(
            f"Размер файла ({file_size_mb:.2f} МБ) превышает максимально допустимый ({MAX_FILE_SIZE_MB} МБ)"
        )
    
    # Проверка типа файла
    mime_type = magic.from_buffer(file_data, mime=True)
    if mime_type not in ALLOWED_MIME_TYPES:
        raise DocumentValidationError(
            f"Недопустимый тип файла: {mime_type}. Разрешены только: {', '.join(ALLOWED_MIME_TYPES)}"
        )
    
    # Проверка на вредоносное содержимое (пример)
    # В реальном сценарии здесь может быть более сложная проверка
    
    # Генерация хеша файла
    file_hash = hashlib.sha256(file_data).hexdigest()
    
    return {
        "filename": filename,
        "size_bytes": len(file_data),
        "mime_type": mime_type,
        "hash": file_hash
    }

def validate_documents_batch(files: List[Dict[str, Union[bytes, str]]]) -> List[Dict[str, Union[str, int]]]:
    """
    Валидирует пакет документов.
    
    Args:
        files: Список словарей с данными файлов и их именами
        
    Returns:
        Список метаданных валидных документов
        
    Raises:
        DocumentValidationError: Если превышено максимальное количество файлов или какой-то файл не прошел валидацию
    """
    if len(files) > MAX_FILES_PER_REQUEST:
        raise DocumentValidationError(
            f"Превышено максимальное количество файлов в запросе: {len(files)}. Максимум: {MAX_FILES_PER_REQUEST}"
        )
    
    results = []
    for file_info in files:
        file_data = file_info.get("data")
        filename = file_info.get("filename")
        
        if not file_data or not filename:
            raise DocumentValidationError("Отсутствуют данные файла или имя файла")
        
        metadata = validate_document(file_data, filename)
        results.append(metadata)
    
    return results
