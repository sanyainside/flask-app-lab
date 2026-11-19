"""Insert data into products table

Revision ID: 10e1203ba6e2
Revises: 5ceabaf67655
Create Date: 2026-11-19 12:49:14.354518

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '10e1203ba6e2'
down_revision = '5ceabaf67655'
branch_labels = None
depends_on = None


def upgrade():
    categories = sa.table(
        'categories',
        sa.column('id', sa.Integer),
        sa.column('name', sa.String),
    )
    products = sa.table(
        'products',
        sa.column('name', sa.String),
        sa.column('price', sa.Float),
        sa.column('active', sa.Boolean),
        sa.column('category_id', sa.Integer),
    )

    op.bulk_insert(categories, [
        {'name': 'Electronics'},
        {'name': 'Books'},
        {'name': 'Clothing'},
    ])

    connection = op.get_bind()
    category_ids = dict(
        connection.execute(
            sa.select(categories.c.name, categories.c.id)
        ).all()
    )

    op.bulk_insert(products, [
        {
            'name': 'Laptop',
            'price': 1200.0,
            'active': True,
            'category_id': category_ids['Electronics'],
        },
        {
            'name': 'Smartphone LG',
            'price': 800.0,
            'active': True,
            'category_id': category_ids['Electronics'],
        },
        {
            'name': 'Novel',
            'price': 20.0,
            'active': True,
            'category_id': category_ids['Books'],
        },
        {
            'name': 'T-Shirt',
            'price': 25.0,
            'active': False,
            'category_id': category_ids['Clothing'],
        },
    ])


def downgrade():
    categories = sa.table(
        'categories',
        sa.column('id', sa.Integer),
        sa.column('name', sa.String),
    )
    products = sa.table(
        'products',
        sa.column('name', sa.String),
        sa.column('category_id', sa.Integer),
    )

    category_names = ['Electronics', 'Books', 'Clothing']
    product_names = ['Laptop', 'Smartphone LG', 'Novel', 'T-Shirt']

    category_ids = sa.select(categories.c.id).where(
        categories.c.name.in_(category_names),
    )

    connection = op.get_bind()
    connection.execute(
        products.delete().where(
            products.c.name.in_(product_names),
            products.c.category_id.in_(category_ids),
        )
    )
    connection.execute(
        categories.delete().where(
            categories.c.name.in_(category_names),
        )
    )
