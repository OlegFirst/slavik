from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import json
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class BCMDigitalCopy(models.Model):
    _name = 'bcm.digital.copy'
    _description = 'BCM Digital Copy - снапшот состояния Digital Twin'
    _order = 'create_date desc'
    _rec_name = 'name'

    # Основные поля
    name = fields.Char(
        string='Название копии',
        required=True,
        help='Название снапшота для идентификации'
    )

    digital_twin_id = fields.Many2one(
        'bcm.digital.twin.organization',
        string='Digital Twin',
        required=True,
        ondelete='cascade',
        help='Цифровой двойник, снапшот которого создается'
    )

    bcm_client_id = fields.Many2one(
        'bcm.client',
        string='BCM Client',
        related='digital_twin_id.bcm_client_id',
        store=True,
        help='Клиент BCM'
    )

    # Тип и статус
    copy_type = fields.Selection([
        ('manual', 'Ручной снапшот'),
        ('automatic', 'Автоматический'),
        ('backup', 'Резервная копия'),
        ('milestone', 'Контрольная точка'),
    ], string='Тип копии', default='manual', required=True)

    state = fields.Selection([
        ('draft', 'Черновик'),
        ('creating', 'Создается'),
        ('active', 'Активна'),
        ('restored', 'Восстановлена'),
        ('archived', 'Архивирована'),
        ('error', 'Ошибка'),
    ], string='Статус', default='draft', tracking=True)

    # Данные снапшота
    snapshot_data = fields.Text(
        string='Данные снапшота',
        help='JSON с состоянием Digital Twin на момент создания копии'
    )

    metadata = fields.Text(
        string='Метаданные',
        help='Дополнительная информация о снапшоте в формате JSON'
    )

    # Временные метки
    snapshot_date = fields.Datetime(
        string='Дата снапшота',
        default=fields.Datetime.now,
        required=True,
        help='Время создания снапшота'
    )

    valid_until = fields.Datetime(
        string='Действует до',
        help='Дата истечения действия снапшота'
    )

    # Связи и ссылки
    parent_copy_id = fields.Many2one(
        'bcm.digital.copy',
        string='Родительская копия',
        help='Снапшот, на основе которого создана эта копия'
    )

    child_copy_ids = fields.One2many(
        'bcm.digital.copy',
        'parent_copy_id',
        string='Дочерние копии',
        help='Снапшоты, созданные на основе этой копии'
    )

    # Сравнения
    comparison_ids = fields.One2many(
        'bcm.digital.copy.comparison',
        'copy_id',
        string='Сравнения',
        help='Сравнения этого снапшота с другими'
    )

    # Вычисляемые поля
    size_kb = fields.Float(
        string='Размер (KB)',
        compute='_compute_size',
        store=True,
        help='Размер снапшота в килобайтах'
    )

    is_expired = fields.Boolean(
        string='Истек',
        compute='_compute_is_expired',
        help='Истек ли срок действия снапшота'
    )

    changes_count = fields.Integer(
        string='Количество изменений',
        compute='_compute_changes_count',
        help='Количество изменений относительно родительского снапшота'
    )

    # Описание и теги
    description = fields.Text(
        string='Описание',
        help='Подробное описание снапшота и причины его создания'
    )

    tag_ids = fields.Many2many(
        'bcm.digital.copy.tag',
        string='Теги',
        help='Теги для категоризации снапшотов'
    )

    # Системные поля
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        string='Компания',
        default=lambda self: self.env.company,
        required=True
    )


    @api.depends('snapshot_data')
    def _compute_size(self):
        """Вычисление размера снапшота"""
        for record in self:
            if record.snapshot_data:
                record.size_kb = len(record.snapshot_data.encode('utf-8')) / 1024
            else:
                record.size_kb = 0.0

    @api.depends('valid_until')
    def _compute_is_expired(self):
        """Проверка истечения срока действия"""
        now = fields.Datetime.now()
        for record in self:
            record.is_expired = (
                record.valid_until and record.valid_until < now
            )

    @api.depends('parent_copy_id', 'snapshot_data')
    def _compute_changes_count(self):
        """Подсчет количества изменений"""
        for record in self:
            if record.parent_copy_id and record.snapshot_data:
                # Здесь должна быть логика сравнения JSON
                record.changes_count = 0  # Заглушка
            else:
                record.changes_count = 0

    @api.model
    def create_snapshot(self, digital_twin_id, name=None, description=None, copy_type='manual'):
        """Создание снапшота Digital Twin"""
        digital_twin = self.env['bcm.digital.twin.organization'].browse(digital_twin_id)
        if not digital_twin.exists():
            raise UserError(_('Digital Twin не найден'))

        if not name:
            name = f"Снапшот {digital_twin.organization_name} - {datetime.now().strftime('%d.%m.%Y %H:%M')}"

        # Получение текущего состояния Digital Twin
        snapshot_data = self._get_twin_state(digital_twin)

        # Создание снапшота
        copy = self.create({
            'name': name,
            'digital_twin_id': digital_twin_id,
            'copy_type': copy_type,
            'description': description,
            'snapshot_data': json.dumps(snapshot_data, ensure_ascii=False, indent=2),
            'state': 'active',
        })

        _logger.info(f"Создан снапшот {copy.name} для Digital Twin {digital_twin.organization_name}")
        return copy

    def _get_twin_state(self, digital_twin):
        """Получение полного состояния Digital Twin"""
        return {
            'organization_id': digital_twin.id,
            'organization_name': digital_twin.organization_name,
            'domain_type': digital_twin.domain_type,
            'current_state': digital_twin.current_state,
            'health_score': digital_twin.health_score,
            'risk_level': digital_twin.risk_level,
            'is_active': digital_twin.is_active,
            'last_updated': str(digital_twin.last_updated),
            'bcm_client_id': digital_twin.bcm_client_id.id if digital_twin.bcm_client_id else None,
            'bcm_context_id': digital_twin.bcm_context_id.id if digital_twin.bcm_context_id else None,
            'metadata': json.loads(digital_twin.metadata or '{}'),
            'snapshot_timestamp': str(fields.Datetime.now()),
        }

    def action_restore_snapshot(self):
        """Восстановление Digital Twin из снапшота"""
        self.ensure_one()
        if self.state != 'active':
            raise UserError(_('Можно восстанавливать только активные снапшоты'))

        try:
            snapshot_data = json.loads(self.snapshot_data)
            digital_twin = self.digital_twin_id

            # Восстановление состояния
            digital_twin.write({
                'current_state': snapshot_data.get('current_state'),
                'health_score': snapshot_data.get('health_score'),
                'risk_level': snapshot_data.get('risk_level'),
                'metadata': json.dumps(snapshot_data.get('metadata', {})),
                'last_updated': fields.Datetime.now(),
            })

            self.state = 'restored'

            _logger.info(f"Digital Twin {digital_twin.organization_name} восстановлен из снапшота {self.name}")

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': f'Digital Twin восстановлен из снапшота "{self.name}"',
                    'type': 'success',
                    'sticky': False,
                }
            }

        except Exception as e:
            self.state = 'error'
            _logger.error(f"Ошибка восстановления снапшота {self.name}: {str(e)}")
            raise UserError(_('Ошибка восстановления снапшота: %s') % str(e))

    def action_compare_snapshots(self):
        """Открытие мастера сравнения снапшотов"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Сравнение снапшотов',
            'res_model': 'bcm.digital.copy.comparison.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_copy_id': self.id}
        }

    def action_archive_snapshot(self):
        """Архивирование снапшота"""
        self.ensure_one()
        self.state = 'archived'
        self.active = False

    @api.model
    def cleanup_expired_snapshots(self):
        """Очистка истекших снапшотов (для cron)"""
        expired_snapshots = self.search([
            ('valid_until', '<', fields.Datetime.now()),
            ('state', '!=', 'archived'),
        ])

        for snapshot in expired_snapshots:
            if snapshot.copy_type == 'automatic':
                snapshot.unlink()  # Удаляем автоматические
            else:
                snapshot.action_archive_snapshot()  # Архивируем ручные

        _logger.info(f"Обработано {len(expired_snapshots)} истекших снапшотов")


class BCMDigitalCopyTag(models.Model):
    _name = 'bcm.digital.copy.tag'
    _description = 'Теги для цифровых копий'

    name = fields.Char(string='Название', required=True)
    color = fields.Integer(string='Цвет')
    description = fields.Text(string='Описание')


class BCMDigitalCopyComparison(models.Model):
    _name = 'bcm.digital.copy.comparison'
    _description = 'Сравнение цифровых копий'

    copy_id = fields.Many2one('bcm.digital.copy', string='Первая копия', required=True)
    compare_copy_id = fields.Many2one('bcm.digital.copy', string='Вторая копия', required=True)
    comparison_result = fields.Text(string='Результат сравнения')
    differences_count = fields.Integer(string='Количество различий')
    create_date = fields.Datetime(string='Дата сравнения', default=fields.Datetime.now)