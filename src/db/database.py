from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base

from src.config import config

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{config.pg_user}:{config.pg_pass}@{config.pg_host}:{config.pg_port}/{config.pg_db}"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=config.pg_pool_size,
    max_overflow=config.pg_max_overflow,
    pool_pre_ping=True,
)

if config.enable_database_telemetry:
    try:
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    except ImportError:
        raise ImportError(
            "OpenTelemetry is not installed. Please install it with `pip install opentelemetry-instrumentation-sqlalchemy`"
        )
    SQLAlchemyInstrumentor().instrument(
        engine=engine.sync_engine,
        enable_commenter=True,
        commenter_options={
            "db_driver" : True,
            "db_framework": True,
            "opentelemetry_values" : True,
        }
    )
SessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine
)

Base = declarative_base()
