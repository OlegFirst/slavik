
def validate_jwt_secret():
    """Валидация наличия JWT-секретного ключа в переменных окружения."""
    import os
    
    jwt_secret = os.getenv("JWT_SECRET_KEY")
    if not jwt_secret:
        raise ValueError("JWT_SECRET_KEY не установлен в переменных окружения. Установите его перед запуском приложения.")
    
    if len(jwt_secret) < 32:
        raise ValueError("JWT_SECRET_KEY слишком короткий. Минимальная длина должна быть 32 символа.")
    
    return jwt_secret
