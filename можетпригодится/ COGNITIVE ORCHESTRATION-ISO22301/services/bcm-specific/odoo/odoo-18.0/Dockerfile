# Dockerfile for Odoo 18.0 with Complete BCM Platform
FROM odoo:18.0

# Установка дополнительных системных зависимостей
USER root

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    curl \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Python зависимости для полной BCM платформы
# Создаем директорию для кеша pip
RUN mkdir -p /var/cache/pip && chown -R odoo:odoo /var/cache/pip

# Копируем requirements и устанавливаем с кешированием
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --cache-dir=/var/cache/pip --break-system-packages --ignore-installed typing-extensions -r /tmp/requirements.txt && \
    pip3 freeze > /tmp/installed_packages.txt

# Создаем директории для логов и данных
RUN mkdir -p /var/log/odoo /var/lib/odoo/filestore /var/lib/odoo/sessions
RUN chown -R odoo:odoo /var/log/odoo /var/lib/odoo

# Копируем конфигурацию Odoo
COPY ./config/odoo.conf /etc/odoo/odoo.conf
RUN chown odoo:odoo /etc/odoo/odoo.conf

# Копируем все BCM модули
COPY ./addons/ /mnt/extra-addons/
RUN chown -R odoo:odoo /mnt/extra-addons/

# Создаем entry point script и скрипт проверки зависимостей
COPY docker-entrypoint.sh /docker-entrypoint.sh
COPY check_dependencies.sh /check_dependencies.sh
RUN chmod +x /docker-entrypoint.sh /check_dependencies.sh && \
    chown odoo:odoo /docker-entrypoint.sh /check_dependencies.sh

USER odoo

# Health check для полной BCM платформы
HEALTHCHECK --interval=30s --timeout=15s --start-period=120s --retries=5 \
  CMD curl -f http://localhost:8069/web/health || exit 1

EXPOSE 8069

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["odoo", "--config=/etc/odoo/odoo.conf", "--logfile=/var/log/odoo/odoo.log"]
