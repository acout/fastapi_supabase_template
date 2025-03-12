"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}

# Initialize empty policy and function collections if not provided
policy_upgrades = getattr(context, 'policy_upgrades', {})
function_upgrades = getattr(context, 'function_upgrades', {})

def upgrade() -> None:
    # Table operations
    ${upgrades if upgrades else "pass"}

    # RLS Policies
    % if policy_upgrades:
    % for table_name, policies in policy_upgrades.items():
    % if policies:

    # Policies for ${table_name}
    op.execute("ALTER TABLE ${table_name} ENABLE ROW LEVEL SECURITY;")
    % for policy in policies:
    op.execute("""
        CREATE POLICY "${policy.name}"
        ON ${table_name}
        FOR ${policy.operation}
        USING (${policy.using})
        ${f"WITH CHECK ({policy.check})" if policy.check else ""};
    """)
    % endfor
    % endif
    % endfor
    % endif

    # PostgreSQL Functions
    % if function_upgrades:
    % for table_name, functions in function_upgrades.items():
    % if functions:

    # Functions for ${table_name}
    % for func in functions:
    op.execute("""
        CREATE OR REPLACE FUNCTION ${func.schema}.${func.name}()
        RETURNS ${func.returns} AS $$
        ${func.body}
        $$ LANGUAGE ${func.language} SECURITY ${func.security};
    """)
    % endfor
    % endif
    % endfor
    % endif


def downgrade() -> None:
    # Drop policies
    % if policy_upgrades:
    % for table_name, policies in policy_upgrades.items():
    % if policies:
    % for policy in policies:
    op.execute('DROP POLICY IF EXISTS "${policy.name}" ON ${table_name};')
    % endfor
    op.execute("ALTER TABLE ${table_name} DISABLE ROW LEVEL SECURITY;")
    % endif
    % endfor
    % endif

    # Drop functions
    % if function_upgrades:
    % for table_name, functions in function_upgrades.items():
    % if functions:
    % for func in functions:
    op.execute('DROP FUNCTION IF EXISTS ${func.schema}.${func.name}();')
    % endfor
    % endif
    % endfor
    % endif

    # Table operations
    ${downgrades if downgrades else "pass"}
