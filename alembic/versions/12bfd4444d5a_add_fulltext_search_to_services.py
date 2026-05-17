"""add fulltext search to services

Revision ID: 12bfd4444d5a
Revises: eed593ad7d27
Create Date: 2026-05-17 20:16:52.791325

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '12bfd4444d5a'
down_revision: Union[str, Sequence[str], None] = 'eed593ad7d27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Ajout de la colonne search_vector
    op.add_column('services', sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True))

    # 2. Index GIN pour la recherche full-text
    op.create_index(
        'ix_services_search_vector',
        'services',
        ['search_vector'],
        unique=False,
        postgresql_using='gin',
    )

    # 3. Fonction qui calcule le search_vector avec pondération
    op.execute("""
        CREATE OR REPLACE FUNCTION services_search_vector_update()
        RETURNS trigger AS $$
        BEGIN
            NEW.search_vector :=
                setweight(to_tsvector('french', coalesce(NEW.title, '')), 'A') ||
                setweight(to_tsvector('french', coalesce(NEW.description, '')), 'B');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # 4. Trigger qui recalcule le vecteur à chaque INSERT ou UPDATE de title/description
    op.execute("""
        CREATE TRIGGER services_search_vector_trigger
        BEFORE INSERT OR UPDATE OF title, description
        ON services
        FOR EACH ROW
        EXECUTE FUNCTION services_search_vector_update();
    """)

    # 5. Backfill des lignes existantes
    op.execute("""
        UPDATE services
        SET search_vector =
            setweight(to_tsvector('french', coalesce(title, '')), 'A') ||
            setweight(to_tsvector('french', coalesce(description, '')), 'B');
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Ordre inverse : trigger -> fonction -> index -> colonne
    op.execute("DROP TRIGGER IF EXISTS services_search_vector_trigger ON services;")
    op.execute("DROP FUNCTION IF EXISTS services_search_vector_update();")
    op.drop_index('ix_services_search_vector', table_name='services', postgresql_using='gin')
    op.drop_column('services', 'search_vector')