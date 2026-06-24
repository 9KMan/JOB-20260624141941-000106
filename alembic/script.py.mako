// alembic/script.py.mako
// alembic/script.py.mako
"""${message}

Revision ID: ${rev}
Revises: ${down_rev}
Create Date: ${create_date}
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
${imports if imports else ''}

revision: str = ${repr(rev)}
down_revision: Union[str, None] = ${repr(down_rev)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}

