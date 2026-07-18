"""
SQLite 데이터를 PostgreSQL로 이전하는 일회성 마이그레이션 스크립트.

실행 위치:
    backend/

기본 실행:
    python scripts/migrate_sqlite_to_postgres.py

PostgreSQL에 기존 테스트 데이터가 있을 때 모두 삭제하고 실행:
    python scripts/migrate_sqlite_to_postgres.py --clear-target
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import MetaData, Table, create_engine, func, inspect, select, text
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import SQLAlchemyError


# scripts/의 부모 디렉터리인 backend/
BACKEND_DIR = Path(__file__).resolve().parent.parent

# 기존 SQLite 백업 파일
SQLITE_DB_PATH = BACKEND_DIR / "enterprise_ai_backup.db"

# app 모듈 import를 위해 backend 경로 추가
sys.path.insert(0, str(BACKEND_DIR))

from app.clients.config import settings  # noqa: E402


SOURCE_TABLE_ORDER = [
    "users",
    "conversations",
    "documents",
    "messages",
    "document_chunks",
]

DELETE_TABLE_ORDER = list(reversed(SOURCE_TABLE_ORDER))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="SQLite 데이터를 PostgreSQL로 이전합니다."
    )
    parser.add_argument(
        "--clear-target",
        action="store_true",
        help="PostgreSQL의 기존 애플리케이션 데이터를 삭제한 뒤 이전합니다.",
    )
    return parser.parse_args()


def create_engines() -> tuple[Engine, Engine]:
    if not SQLITE_DB_PATH.exists():
        raise FileNotFoundError(
            f"SQLite 백업 파일을 찾을 수 없습니다: {SQLITE_DB_PATH}"
        )

    postgres_url = settings.DATABASE_URL

    if not postgres_url.startswith("postgresql"):
        raise ValueError(
            "현재 DATABASE_URL이 PostgreSQL 주소가 아닙니다. "
            f"현재 값의 시작 부분: {postgres_url.split(':', 1)[0]}"
        )

    sqlite_url = f"sqlite:///{SQLITE_DB_PATH}"

    sqlite_engine = create_engine(
        sqlite_url,
        connect_args={"check_same_thread": False},
    )

    postgres_engine = create_engine(
        postgres_url,
        pool_pre_ping=True,
    )

    return sqlite_engine, postgres_engine


def validate_tables(engine: Engine, database_name: str) -> None:
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    missing_tables = [
        table_name
        for table_name in SOURCE_TABLE_ORDER
        if table_name not in existing_tables
    ]

    if missing_tables:
        raise RuntimeError(
            f"{database_name}에 필요한 테이블이 없습니다: "
            f"{', '.join(missing_tables)}"
        )


def reflect_tables(
    sqlite_engine: Engine,
    postgres_engine: Engine,
) -> tuple[dict[str, Table], dict[str, Table]]:
    sqlite_metadata = MetaData()
    postgres_metadata = MetaData()

    sqlite_tables = {
        table_name: Table(
            table_name,
            sqlite_metadata,
            autoload_with=sqlite_engine,
        )
        for table_name in SOURCE_TABLE_ORDER
    }

    postgres_tables = {
        table_name: Table(
            table_name,
            postgres_metadata,
            autoload_with=postgres_engine,
        )
        for table_name in SOURCE_TABLE_ORDER
    }

    return sqlite_tables, postgres_tables


def get_table_count(connection: Connection, table: Table) -> int:
    result = connection.execute(
        select(func.count()).select_from(table)
    )
    return int(result.scalar_one())


def print_source_counts(
    sqlite_engine: Engine,
    sqlite_tables: dict[str, Table],
) -> dict[str, int]:
    counts: dict[str, int] = {}

    print("\n[SQLite 원본 데이터]")

    with sqlite_engine.connect() as connection:
        for table_name in SOURCE_TABLE_ORDER:
            count = get_table_count(
                connection,
                sqlite_tables[table_name],
            )
            counts[table_name] = count
            print(f"  {table_name:<18} {count:>8}")

    return counts


def get_target_counts(
    connection: Connection,
    postgres_tables: dict[str, Table],
) -> dict[str, int]:
    return {
        table_name: get_table_count(
            connection,
            postgres_tables[table_name],
        )
        for table_name in SOURCE_TABLE_ORDER
    }


def ensure_target_is_empty(
    connection: Connection,
    postgres_tables: dict[str, Table],
    clear_target: bool,
) -> None:
    counts = get_target_counts(connection, postgres_tables)
    non_empty_tables = {
        table_name: count
        for table_name, count in counts.items()
        if count > 0
    }

    if not non_empty_tables:
        return

    print("\n[PostgreSQL 기존 데이터]")
    for table_name, count in non_empty_tables.items():
        print(f"  {table_name:<18} {count:>8}")

    if not clear_target:
        raise RuntimeError(
            "\nPostgreSQL에 기존 데이터가 있습니다.\n"
            "기존 테스트 데이터를 삭제하고 이전하려면 다음과 같이 실행하세요.\n\n"
            "python scripts/migrate_sqlite_to_postgres.py --clear-target"
        )

    print("\nPostgreSQL 기존 데이터를 삭제합니다.")

    for table_name in DELETE_TABLE_ORDER:
        connection.execute(
            postgres_tables[table_name].delete()
        )


def normalize_row(
    source_row: dict[str, Any],
    target_table: Table,
) -> dict[str, Any]:
    """
    원본과 대상 DB에 모두 존재하는 컬럼만 복사한다.

    마이그레이션 과정에서 PostgreSQL에만 추가된 nullable/default 컬럼이
    존재해도 안전하게 처리할 수 있다.
    """
    target_column_names = {
        column.name
        for column in target_table.columns
    }

    normalized_row : dict[str, Any] = {}

    for column_name, value in source_row.items():
        if column_name not in target_column_names:
            continue

        if isinstance(value, str):
            value = value.replace("\x00", "")

        normalized_row[column_name] = value

    return normalized_row


def copy_table(
    source_connection: Connection,
    target_connection: Connection,
    source_table: Table,
    target_table: Table,
) -> int:
    source_rows = source_connection.execute(
        select(source_table)
    ).mappings()

    copied_count = 0
    batch: list[dict[str, Any]] = []
    batch_size = 500

    for source_row in source_rows:
        normalized_row = normalize_row(
            dict(source_row),
            target_table,
        )

        batch.append(normalized_row)

        if len(batch) >= batch_size:
            target_connection.execute(
                target_table.insert(),
                batch,
            )
            copied_count += len(batch)
            batch.clear()

    if batch:
        target_connection.execute(
            target_table.insert(),
            batch,
        )
        copied_count += len(batch)

    return copied_count


def reset_postgres_sequences(
    connection: Connection,
    postgres_tables: dict[str, Table],
) -> None:
    print("\n[PostgreSQL 시퀀스 재설정]")

    for table_name in SOURCE_TABLE_ORDER:
        table = postgres_tables[table_name]

        if "id" not in table.c:
            continue

        sequence_name = connection.execute(
            text(
                """
                SELECT pg_get_serial_sequence(
                    :table_name,
                    :column_name
                )
                """
            ),
            {
                "table_name": table_name,
                "column_name": "id",
            },
        ).scalar_one_or_none()

        if not sequence_name:
            print(f"  {table_name:<18} 시퀀스 없음")
            continue

        max_id = connection.execute(
            select(func.max(table.c.id))
        ).scalar_one()

        if max_id is None:
            connection.execute(
                text(
                    """
                    SELECT setval(
                        CAST(:sequence_name AS regclass),
                        1,
                        false
                    )
                    """
                ),
                {"sequence_name": sequence_name},
            )
            print(f"  {table_name:<18} 다음 ID: 1")
        else:
            connection.execute(
                text(
                    """
                    SELECT setval(
                        CAST(:sequence_name AS regclass),
                        :max_id,
                        true
                    )
                    """
                ),
                {
                    "sequence_name": sequence_name,
                    "max_id": int(max_id),
                },
            )
            print(
                f"  {table_name:<18} "
                f"현재 최대 ID: {max_id}"
            )


def validate_migration(
    connection: Connection,
    postgres_tables: dict[str, Table],
    source_counts: dict[str, int],
) -> None:
    print("\n[마이그레이션 검증]")

    errors: list[str] = []

    for table_name in SOURCE_TABLE_ORDER:
        source_count = source_counts[table_name]
        target_count = get_table_count(
            connection,
            postgres_tables[table_name],
        )

        status = "정상" if source_count == target_count else "불일치"

        print(
            f"  {table_name:<18} "
            f"SQLite={source_count:<8} "
            f"PostgreSQL={target_count:<8} "
            f"{status}"
        )

        if source_count != target_count:
            errors.append(
                f"{table_name}: "
                f"SQLite={source_count}, "
                f"PostgreSQL={target_count}"
            )

    if errors:
        raise RuntimeError(
            "복사 건수가 일치하지 않습니다.\n"
            + "\n".join(errors)
        )


def migrate(clear_target: bool) -> None:
    sqlite_engine, postgres_engine = create_engines()

    try:
        validate_tables(
            sqlite_engine,
            "SQLite",
        )
        validate_tables(
            postgres_engine,
            "PostgreSQL",
        )

        sqlite_tables, postgres_tables = reflect_tables(
            sqlite_engine,
            postgres_engine,
        )

        source_counts = print_source_counts(
            sqlite_engine,
            sqlite_tables,
        )

        print("\nSQLite → PostgreSQL 마이그레이션을 시작합니다.")

        with sqlite_engine.connect() as source_connection:
            # begin() 내부에서 오류가 발생하면 PostgreSQL 전체 작업 롤백
            with postgres_engine.begin() as target_connection:
                ensure_target_is_empty(
                    target_connection,
                    postgres_tables,
                    clear_target,
                )

                print("\n[데이터 복사]")

                for table_name in SOURCE_TABLE_ORDER:
                    copied_count = copy_table(
                        source_connection,
                        target_connection,
                        sqlite_tables[table_name],
                        postgres_tables[table_name],
                    )

                    print(
                        f"  {table_name:<18} "
                        f"{copied_count:>8}건 복사"
                    )

                reset_postgres_sequences(
                    target_connection,
                    postgres_tables,
                )

                # validate_migration(
                #     target_connection,
                #     postgres_tables,
                #     source_counts,
                # )

        print("\n마이그레이션이 정상적으로 완료됐습니다.")

    finally:
        sqlite_engine.dispose()
        postgres_engine.dispose()


def main() -> None:
    args = parse_args()

    try:
        migrate(clear_target=args.clear_target)
    except (
        FileNotFoundError,
        ValueError,
        RuntimeError,
        SQLAlchemyError,
    ) as error:
        print(f"\n마이그레이션 실패: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()