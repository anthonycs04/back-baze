from collections.abc import Generator
from urllib.parse import parse_qsl, unquote

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, URL
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.base import Base


_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def _build_database_url(raw_url: str) -> URL | str:
    if "://" not in raw_url:
        return raw_url

    scheme, rest = raw_url.split("://", 1)
    if scheme not in {"postgres", "postgresql", "postgresql+psycopg"}:
        return raw_url

    userinfo, hostpart = rest.rsplit("@", 1)
    if ":" in userinfo:
        username, password = userinfo.split(":", 1)
    else:
        username, password = userinfo, None

    hostport, path_query = hostpart.split("/", 1) if "/" in hostpart else (hostpart, "")
    database, query_string = path_query.split("?", 1) if "?" in path_query else (path_query, "")

    if hostport.startswith("["):
        host_end = hostport.find("]")
        host = hostport[1:host_end]
        port_text = hostport[host_end + 2 :] if hostport[host_end + 1 :].startswith(":") else None
    elif ":" in hostport:
        host, port_text = hostport.rsplit(":", 1)
    else:
        host, port_text = hostport, None

    return URL.create(
        "postgresql+psycopg",
        username=unquote(username),
        password=unquote(password) if password is not None else None,
        host=host,
        port=int(port_text) if port_text else None,
        database=unquote(database) if database else None,
        query=dict(parse_qsl(query_string, keep_blank_values=True)),
    )


def get_engine() -> Engine:
    global _engine

    if settings.database_url is None:
        raise RuntimeError("DATABASE_URL is not configured")

    if _engine is None:
        _engine = create_engine(
            _build_database_url(settings.database_url),
            echo=settings.sql_echo,
            pool_pre_ping=True,
        )

    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _session_factory

    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(),
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

    return _session_factory


def get_db() -> Generator[Session, None, None]:
    session_factory = get_session_factory()

    with session_factory() as session:
        yield session


def check_database_connection() -> bool:
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
