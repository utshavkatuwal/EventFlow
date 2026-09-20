# EventFlow - Migration Guide

## Creating Migrations

```bash
cd backend
alembic revision --autogenerate -m "description of changes"
```

## Applying Migrations

```bash
alembic upgrade head
```

## Downgrading

```bash
alembic downgrade -1
alembic downgrade <revision_id>
```

## Migration History

```bash
alembic history
alembic current
```

## Migration Files

Located in `database/migrations/versions/`:
- `000000000000_initial.py` - Initial schema with all 18 tables

## Common Operations

### Add Column
```python
op.add_column('table_name', sa.Column('new_column', sa.String(100), nullable=True))
```

### Create Index
```python
op.create_index('idx_table_column', 'table_name', ['column'])
```

### Add Foreign Key
```python
op.create_foreign_key(
    'fk_table_other',
    'table_name',
    'other_table',
    ['other_id'],
    ['id'],
    ondelete='CASCADE'
)
```

## Production Migrations

1. Always backup database first
2. Test migration on staging
3. Run during maintenance window
4. Monitor for issues