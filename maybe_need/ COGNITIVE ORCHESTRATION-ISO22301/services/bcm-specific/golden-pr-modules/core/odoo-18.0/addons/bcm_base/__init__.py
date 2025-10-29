# -*- coding: utf-8 -*-

from . import models

def post_init_hook(env):
    """
    Инициализация BCM модуля после установки
    """
    # Создаем начальные данные
    if env['bcm.service.config'].search_count([]) == 0:
        env['bcm.service.config'].create_default_configs()
