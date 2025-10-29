from odoo import models, fields, api

class BcmForumTopic(models.Model):
    _name = 'bcm.forum.topic'
    _description = 'BCM Forum Topic'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Topic Title', required=True, tracking=True)
    description = fields.Text('Description')
    content = fields.Html('Content')

    # Forum categorization
    category_id = fields.Many2one('bcm.forum.category', 'Category', required=True)

    # Topic metadata
    view_count = fields.Integer('Views', default=0)
    reply_count = fields.Integer('Replies', default=0)
    is_pinned = fields.Boolean('Pinned', default=False)
    is_locked = fields.Boolean('Locked', default=False)

    # Relations
    author_id = fields.Many2one('res.users', 'Author', required=True, default=lambda self: self.env.user)
    last_post_date = fields.Datetime('Last Post', default=fields.Datetime.now)

    # Live chat integration
    chat_room_id = fields.Many2one('bcm.live.chat', 'Associated Chat Room')

    # Status
    active = fields.Boolean('Active', default=True)

    # Multi-tenancy
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)


class BcmForumIntegration(models.Model):
    _name = 'bcm.forum.integration'
    _description = 'BCM Forum Integration'

    name = fields.Char('Integration Name', required=True)
    active = fields.Boolean('Active', default=True)

    # Integration settings
    forum_service_url = fields.Char('Forum Service URL')
    api_key = fields.Char('API Key')
    webhook_url = fields.Char('Webhook URL')

    # Status
    connection_status = fields.Selection([
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('error', 'Error')
    ], default='disconnected')

    last_sync = fields.Datetime('Last Sync')

    # Multi-tenancy
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)