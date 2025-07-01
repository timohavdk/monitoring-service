from alembic import op
import sqlalchemy as sa
import uuid

revision = '0001_create_monitoring_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'rooms',
        sa.Column('id', sa.UUID(as_uuid=True),
                  primary_key=True, default=uuid.uuid4),
        sa.Column('rtsp', sa.Text, nullable=True),
        sa.Column('title', sa.Text, nullable=True)
    )

    op.create_table(
        'statistics',
        sa.Column('id', sa.UUID(as_uuid=True),
                  primary_key=True, default=uuid.uuid4),
        sa.Column('work_stations', sa.Integer, nullable=True),
        sa.Column('persons', sa.Integer, nullable=True),
        sa.Column('sitting_persons', sa.Integer, nullable=True),
        sa.Column('not_sitting_persons', sa.Integer, nullable=True),
        sa.Column('free_work_station', sa.Integer, nullable=True),
        sa.Column('timestamp', sa.TIMESTAMP, nullable=True),
        sa.Column('room_id', sa.UUID(as_uuid=True),
                  sa.ForeignKey('rooms.id'), nullable=True)
    )

    op.create_table(
        'work_stations',
        sa.Column('id', sa.UUID(as_uuid=True),
                  primary_key=True, default=uuid.uuid4),
        sa.Column('x_center', sa.REAL, nullable=True),
        sa.Column('y_center', sa.REAL, nullable=True),
        sa.Column('width', sa.REAL, nullable=True),
        sa.Column('height', sa.REAL, nullable=True),
        sa.Column('room_id', sa.UUID(as_uuid=True),
                  sa.ForeignKey('rooms.id'), nullable=True)
    )

    op.create_table(
        'work_stations_statistics',
        sa.Column('id', sa.UUID(as_uuid=True),
                  primary_key=True, default=uuid.uuid4),
        sa.Column('work_station_id', sa.UUID(as_uuid=True),
                  sa.ForeignKey('work_stations.id'), nullable=True),
        sa.Column('free', sa.Boolean, nullable=True),
        sa.Column('timestamp', sa.TIMESTAMP, nullable=True)
    )


def downgrade():
    op.drop_table('work_stations_statistics')
    op.drop_table('work_stations')
    op.drop_table('statistics')
    op.drop_table('rooms')
