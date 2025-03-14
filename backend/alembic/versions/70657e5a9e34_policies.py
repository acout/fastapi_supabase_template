"""policies

Revision ID: 70657e5a9e34
Revises: 
Create Date: 2025-03-07 22:08:46.832833

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '70657e5a9e34'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('item',
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('owner_id', sa.Uuid(), server_default=sa.text('auth.uid()'), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['auth.users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('profiles',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('owner_id', sa.Uuid(), server_default=sa.text('auth.uid()'), nullable=False),
    sa.Column('email', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('picture_path', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['auth.users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    schema='public'
    )
    op.execute('ALTER TABLE item ENABLE ROW LEVEL SECURITY;')
    op.execute('\n                    CREATE POLICY "item_select" ON item\n                    FOR SELECT\n                \n    USING (\n                auth.uid() = owner_id OR\n                auth.role() = \'service_role\'\n            );')
    op.execute('\n                    CREATE POLICY "item_insert" ON item\n                    FOR INSERT\n                \n    WITH CHECK (\n                auth.uid() = owner_id OR\n                auth.role() = \'service_role\'\n            );')
    op.execute('\n                    CREATE POLICY "item_update" ON item\n                    FOR UPDATE\n                \n    USING (\n                auth.uid() = owner_id OR\n                auth.role() = \'service_role\'\n            )\n    WITH CHECK (\n                auth.uid() = owner_id OR\n                auth.role() = \'service_role\'\n            );')
    op.execute('\n                    CREATE POLICY "item_delete" ON item\n                    FOR DELETE\n                \n    USING (\n                auth.uid() = owner_id OR\n                auth.role() = \'service_role\'\n            );')
    op.execute('ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;')
    op.execute('\n                    CREATE POLICY "profiles_select" ON profiles\n                    FOR SELECT\n                \n    USING (\n                auth.uid() = owner_id OR\n                auth.role() = \'service_role\'\n            );')
    op.execute('\n                    CREATE POLICY "profiles_insert" ON profiles\n                    FOR INSERT\n                \n    WITH CHECK (\n                auth.uid() = owner_id OR\n                auth.role() = \'service_role\'\n            );')
    op.execute('\n                    CREATE POLICY "profiles_update" ON profiles\n                    FOR UPDATE\n                \n    USING (\n                auth.uid() = owner_id OR\n                auth.role() = \'service_role\'\n            )\n    WITH CHECK (\n                auth.uid() = owner_id OR\n                auth.role() = \'service_role\'\n            );')
    op.execute('\n                    CREATE POLICY "profiles_delete" ON profiles\n                    FOR DELETE\n                \n    USING (\n                auth.uid() = owner_id OR\n                auth.role() = \'service_role\'\n            );')
    op.execute("\n                INSERT INTO storage.buckets (id, name, public)\n                VALUES (\n                    'profile-pictures',\n                    'profile-pictures',\n                    true\n                )\n                ON CONFLICT (id) DO UPDATE\n                SET public = EXCLUDED.public;\n            ")
    op.execute('ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;')
    op.execute('\n                CREATE POLICY "Users can manage their own files in profile-pictures"\n                ON storage.objects\n                FOR ALL\n                USING ((\n            auth.role() = \'authenticated\' AND\n            (storage.foldername(name))[1] = (select auth.uid()::text)\n        ))\n                WITH CHECK ((\n            auth.role() = \'authenticated\' AND\n            (storage.foldername(name))[1] = (select auth.uid()::text)\n        ));\n            ')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('DROP POLICY IF EXISTS "Users can manage their own files in profile-pictures" ON storage.objects;')
    op.execute('ALTER TABLE profiles DISABLE ROW LEVEL SECURITY;')
    op.execute('DROP POLICY IF EXISTS "profiles_delete" ON profiles;')
    op.execute('DROP POLICY IF EXISTS "profiles_update" ON profiles;')
    op.execute('DROP POLICY IF EXISTS "profiles_insert" ON profiles;')
    op.execute('DROP POLICY IF EXISTS "profiles_select" ON profiles;')
    op.execute('ALTER TABLE item DISABLE ROW LEVEL SECURITY;')
    op.execute('DROP POLICY IF EXISTS "item_delete" ON item;')
    op.execute('DROP POLICY IF EXISTS "item_update" ON item;')
    op.execute('DROP POLICY IF EXISTS "item_insert" ON item;')
    op.execute('DROP POLICY IF EXISTS "item_select" ON item;')
    op.drop_table('profiles', schema='public')
    op.drop_table('item')
    op.execute("DELETE FROM storage.buckets WHERE id = 'profile-pictures';")
    # ### end Alembic commands ###