{
    'name': 'Dynamic Approval Workflow',
    'version': '16.0.0.0.2',
    'summary': 'Module for Dynamic Approval Workflow with Sync to Target Models',
    'description': """
        This module allows users to create dynamic approval workflows and sync them to target models.
        It adds a tab with a tree view to the target model displaying the approval sequence and approvers.
    """,
    'author': 'Ahmad Mustafidul Ibad',
    'category': 'Tools',
    'depends': ['base', 'mail'],
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Views
        'views/approval_workflow_engine_view.xml',
        'views/menuitem.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
