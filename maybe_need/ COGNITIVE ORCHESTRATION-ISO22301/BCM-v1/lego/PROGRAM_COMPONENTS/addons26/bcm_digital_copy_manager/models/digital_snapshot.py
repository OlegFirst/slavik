from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging

_logger = logging.getLogger(__name__)


class BCMDigitalSnapshot(models.Model):
    _name = 'bcm.digital.snapshot'
    _description = 'BCM Digital Snapshot - детальный снимок компонентов'
    _order = 'create_date desc'

    name = fields.Char(string='Название', required=True)

    digital_copy_id = fields.Many2one(
        'bcm.digital.copy',
        string='Digital Copy',
        required=True,
        ondelete='cascade'
    )

    component_type = fields.Selection([
        ('organization', 'Организация'),
        ('processes', 'Процессы'),
        ('risks', 'Риски'),
        ('resources', 'Ресурсы'),
        ('contacts', 'Контакты'),
        ('locations', 'Локации'),
        ('dependencies', 'Зависимости'),
        ('plans', 'Планы'),
        ('incidents', 'Инциденты'),
        ('metrics', 'Метрики'),
    ], string='Тип компонента', required=True)

    snapshot_data = fields.Text(
        string='Данные компонента',
        help='JSON с детальным состоянием компонента'
    )

    checksum = fields.Char(
        string='Контрольная сумма',
        help='Хэш данных для проверки целостности'
    )

    size_bytes = fields.Integer(
        string='Размер (байт)',
        compute='_compute_size',
        store=True
    )

    @api.depends('snapshot_data')
    def _compute_size(self):
        for record in self:
            if record.snapshot_data:
                record.size_bytes = len(record.snapshot_data.encode('utf-8'))
            else:
                record.size_bytes = 0

    def get_component_data(self):
        """Получение данных компонента в виде словаря"""
        if self.snapshot_data:
            try:
                return json.loads(self.snapshot_data)
            except json.JSONDecodeError:
                _logger.error(f"Ошибка декодирования JSON в snapshot {self.id}")
                return {}
        return {}

    def set_component_data(self, data):
        """Установка данных компонента"""
        self.snapshot_data = json.dumps(data, ensure_ascii=False, indent=2)
        # Можно добавить вычисление checksum
        import hashlib
        self.checksum = hashlib.md5(self.snapshot_data.encode()).hexdigest()


class BCMSnapshotComparison(models.TransientModel):
    _name = 'bcm.digital.copy.comparison.wizard'
    _description = 'Мастер сравнения снапшотов'

    copy_id = fields.Many2one('bcm.digital.copy', string='Первый снапшот', required=True)
    compare_copy_id = fields.Many2one('bcm.digital.copy', string='Второй снапшот', required=True)

    comparison_result = fields.Html(string='Результат сравнения', readonly=True)

    def action_compare(self):
        """Выполнение сравнения снапшотов"""
        self.ensure_one()

        if self.copy_id.id == self.compare_copy_id.id:
            raise UserError(_('Нельзя сравнивать снапшот с самим собой'))

        # Получаем данные снапшотов
        data1 = json.loads(self.copy_id.snapshot_data or '{}')
        data2 = json.loads(self.compare_copy_id.snapshot_data or '{}')

        # Выполняем сравнение
        differences = self._compare_data(data1, data2)

        # Формируем HTML отчет
        html_result = self._generate_comparison_html(differences)
        self.comparison_result = html_result

        # Сохраняем результат сравнения
        self.env['bcm.digital.copy.comparison'].create({
            'copy_id': self.copy_id.id,
            'compare_copy_id': self.compare_copy_id.id,
            'comparison_result': str(differences),
            'differences_count': len(differences),
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _compare_data(self, data1, data2):
        """Сравнение двух наборов данных"""
        differences = []

        # Простое сравнение ключей и значений
        all_keys = set(data1.keys()) | set(data2.keys())

        for key in all_keys:
            if key not in data1:
                differences.append({
                    'type': 'added',
                    'key': key,
                    'value': data2[key],
                    'description': f'Добавлено поле "{key}"'
                })
            elif key not in data2:
                differences.append({
                    'type': 'removed',
                    'key': key,
                    'value': data1[key],
                    'description': f'Удалено поле "{key}"'
                })
            elif data1[key] != data2[key]:
                differences.append({
                    'type': 'changed',
                    'key': key,
                    'old_value': data1[key],
                    'new_value': data2[key],
                    'description': f'Изменено поле "{key}"'
                })

        return differences

    def _generate_comparison_html(self, differences):
        """Генерация HTML отчета сравнения"""
        if not differences:
            return '<p><strong>Снапшоты идентичны</strong></p>'

        html = f'<h3>Найдено различий: {len(differences)}</h3><ul>'

        for diff in differences:
            if diff['type'] == 'added':
                html += f'<li style="color: green;">➕ {diff["description"]}: {diff["value"]}</li>'
            elif diff['type'] == 'removed':
                html += f'<li style="color: red;">➖ {diff["description"]}: {diff["value"]}</li>'
            elif diff['type'] == 'changed':
                html += f'<li style="color: orange;">🔄 {diff["description"]}: {diff["old_value"]} → {diff["new_value"]}</li>'

        html += '</ul>'
        return html