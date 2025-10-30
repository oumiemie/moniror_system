"""Remove status field from Server table

Revision ID: 006
Revises: 005
Create Date: 2025-09-28 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    """删除Server表中的status字段"""
    # 删除status字段
    op.drop_column('server', 'status')


def downgrade():
    """恢复Server表中的status字段"""
    # 重新添加status字段
    op.add_column('server', sa.Column('status', sa.Enum('online', 'offline'), nullable=True, default='offline'))
