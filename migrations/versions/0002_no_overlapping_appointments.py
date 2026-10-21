from alembic import op
revision = "0002_no_overlap"
down_revision = "0001_initial"
branch_labels = None
depends_on = None
def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
    op.execute("ALTER TABLE appointments ADD CONSTRAINT appointments_no_overlap EXCLUDE USING gist (professional_id WITH =, tstzrange(starts_at, ends_at, '[)') WITH &&) WHERE (status IN ('confirmed', 'completed'))")
def downgrade():
    op.execute("ALTER TABLE appointments DROP CONSTRAINT appointments_no_overlap")
