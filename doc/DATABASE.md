## Docker commands

### Dump & Restore

**Dump (Docker)**

From Docker

```sh
docker-compose exec -T db pg_dump --username=postgres --host=localhost --port=5432 --dbname=rowing --verbose --format=tar > db-backup.tar
```

From Railway.app

```sh
docker-compose exec -T --env PGPASSWORD=123secret123 db pg_dump --username=postgres --host=example.railway.app --port=6863 --dbname=railway --verbose --format=tar > db-backup.tar
```

**Restore**

*Mind the `--clean` option: https://stackoverflow.com/questions/43603192/will-pg-restore-overwrite-the-existing-tables*

To Railway.app

```sh
docker-compose exec -T --env PGPASSWORD=123secret123 db pg_restore --username=postgres --host=example.railway.app --port=6863 --dbname=railway --verbose --clean < db-backup.tar
```

To Docker

```sh
docker-compose exec -T db pg_restore --username=postgres --host=localhost --port=5432 --dbname=rowing --verbose --clean < db-backup.tar
```

### Start and create tables

Compose up

    docker-compose up

Create tables

    python -m model.dbutils --create

### Purge container instance and volume

Drop tables (optional)

    python -m model.dbutils --drop

Compose down

    docker-compose down -v

## Other

**Reset Database SQL Statement**

```SQL
DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO postgres; GRANT ALL ON SCHEMA public TO public;
```
Ref: https://stackoverflow.com/a/13823560

## Notes

- Foreign Key / Integrity checking: https://docs.sqlalchemy.org/en/14/core/constraints.html
- JSON typed columns with SQLAlchemy: https://amercader.net/blog/beware-of-json-fields-in-sqlalchemy/
    - Use: `Column(MutableDict.as_mutable(JSONB))`
