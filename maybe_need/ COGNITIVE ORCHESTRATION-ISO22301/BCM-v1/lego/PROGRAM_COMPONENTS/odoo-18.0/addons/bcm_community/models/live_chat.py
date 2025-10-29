from odoo import models, fields, api

class BcmLiveChat(models.Model):
    _name = 'bcm.live.chat'
    _description = 'BCM Live Chat'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Chat Room Name', required=True)
    description = fields.Text('Description')

    # Chat type
    chat_type = fields.Selection([
        ('public', 'Public Chat'),
        ('private', 'Private Group'),
        ('scenario', 'Scenario Discussion'),
        ('support', 'Technical Support')
    ], required=True, default='public')

    # Participants
    participant_ids = fields.Many2many('res.users', string='Participants')
    max_participants = fields.Integer('Max Participants', default=50)

    # Status
    is_active = fields.Boolean('Active', default=True)
    is_archived = fields.Boolean('Archived', default=False)

    # Metadata
    created_by = fields.Many2one('res.users', 'Created By', default=lambda self: self.env.user)
    message_count = fields.Integer('Messages', default=0)
    last_activity = fields.Datetime('Last Activity')

    # Multi-tenancy
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)


class BcmChatMessage(models.Model):
    _name = 'bcm.chat.message'
    _description = 'Chat Message'

    content = fields.Text('Message Content', required=True)
    chat_id = fields.Many2one('bcm.live.chat', 'Chat Room', required=True, ondelete='cascade')
    author_id = fields.Many2one('res.users', 'Author', required=True, default=lambda self: self.env.user)

    # Message metadata
    message_type = fields.Selection([
        ('text', 'Text Message'),
        ('file', 'File Upload'),
        ('system', 'System Message'),
        ('ai', 'AI Response')
    ], default='text')

    # Timestamps
    sent_at = fields.Datetime('Sent At', default=fields.Datetime.now)
    edited_at = fields.Datetime('Edited At')
    is_edited = fields.Boolean('Edited', default=False)

    # Reactions and engagement
    reaction_count = fields.Integer('Reactions', default=0)
    is_pinned = fields.Boolean('Pinned', default=False)

    # Multi-tenancy
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)