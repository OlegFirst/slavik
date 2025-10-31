from odoo import models, fields

class BcmForumPost(models.Model):
    _name = 'bcm.forum.post'
    _description = 'BCM Forum Post'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    content = fields.Html('Post Content', required=True)
    topic_id = fields.Many2one('bcm.forum.topic', 'Topic', required=True, ondelete='cascade')
    author_id = fields.Many2one('res.users', 'Author', required=True, default=lambda self: self.env.user)

    # Metadata
    created_date = fields.Datetime('Created', default=fields.Datetime.now)
    edited_date = fields.Datetime('Last Edited')
    is_edited = fields.Boolean('Edited', default=False)

    # Engagement
    like_count = fields.Integer('Likes', default=0)
    reply_count = fields.Integer('Replies', default=0)

    # Status
    active = fields.Boolean('Active', default=True)
    is_solution = fields.Boolean('Marked as Solution', default=False)

    # Multi-tenancy
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)