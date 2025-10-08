"""
Стандартная конфигурация логирования для всех сервисов платформы
"""
import logging
import sys
from typing import Optional


def setup_logging(service_name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Стандартная конфигурация логирования для всех сервисов

    Args:
        service_name: Название сервиса
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        logging.Logger: Настроенный логгер для сервиса

    Example:
        >>> logger = setup_logging("bia-service", "DEBUG")
        >>> logger.info("Service started")
    """

    # Конвертируем строковый уровень в константу logging
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Настраиваем базовую конфигурацию
    logging.basicConfig(
        level=numeric_level,
        format=f'%(asctime)s - {service_name} - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )

    # Создаем и возвращаем логгер для сервиса
    logger = logging.getLogger(service_name)

    return logger


def setup_file_logging(
    service_name: str,
    log_level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Конфигурация логирования с записью в файл

    Args:
        service_name: Название сервиса
        log_level: Уровень логирования
        log_file: Путь к файлу логов (опционально)

    Returns:
        logging.Logger: Настроенный логгер с записью в файл
    """

    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter(
                f'%(asctime)s - {service_name} - %(name)s - %(levelname)s - %(message)s'
            )
        )
        handlers.append(file_handler)

    logging.basicConfig(
        level=numeric_level,
        format=f'%(asctime)s - {service_name} - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

    logger = logging.getLogger(service_name)

    return logger
