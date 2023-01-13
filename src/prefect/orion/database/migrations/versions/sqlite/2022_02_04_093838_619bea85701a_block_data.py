"""Add the block data table.

Revision ID: 619bea85701a
Revises: 9725c1cbee35
Create Date: 2022-02-04 09:38:38.324086

"""
import sqlalchemy as sa
from alembic import op

import prefect

# revision identifiers, used by Alembic.
revision = "619bea85701a"
down_revision = "9725c1cbee35"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "block_data",
        sa.Column(
            "id",
            prefect.orion.utilities.database.UUID(),
            server_default=sa.text(
                "(\n    (\n        lower(hex(randomblob(4))) \n        || '-' \n       "
                " || lower(hex(randomblob(2))) \n        || '-4' \n        ||"
                " substr(lower(hex(randomblob(2))),2) \n        || '-' \n        ||"
                " substr('89ab',abs(random()) % 4 + 1, 1) \n        ||"
                " substr(lower(hex(randomblob(2))),2) \n        || '-' \n        ||"
                " lower(hex(randomblob(6)))\n    )\n    )"
            ),
            nullable=False,
        ),
        sa.Column(
            "created",
            prefect.orion.utilities.database.Timestamp(timezone=True),
            server_default=sa.text("(strftime('%Y-%m-%d %H:%M:%f000', 'now'))"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            prefect.orion.utilities.database.Timestamp(timezone=True),
            server_default=sa.text("(strftime('%Y-%m-%d %H:%M:%f000', 'now'))"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("blockref", sa.String(), nullable=False),
        sa.Column(
            "data",
            prefect.orion.utilities.database.JSON(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_block_data")),
    )
    op.create_index(op.f("ix_block_data__name"), "block_data", ["name"], unique=True)
    op.create_index(
        op.f("ix_block_data__updated"), "block_data", ["updated"], unique=False
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_block_data__updated"), table_name="block_data")
    op.drop_index(op.f("ix_block_data__name"), table_name="block_data")
    op.drop_table("block_data")
    # ### end Alembic commands ###
