"""Session-scoped fixtures for LakeFS integration tests.

Reads connection details from the standard ``LAKECTL_*`` environment
variables and seeds a shared repository (``langchain-lakefs-it``) with a
fixed layout the tests assert against. The seed is idempotent, so the
suite can be re-run repeatedly against a long-lived lakeFS instance.
"""

import os
from concurrent.futures import ThreadPoolExecutor
from typing import Iterator

import lakefs
import pytest
from lakefs.client import Client

REPO_NAME = "langchain-lakefs-it"
FEATURE_BRANCH = "feature"
BULK_PREFIX = "bulk/"
BULK_COUNT = 1500


@pytest.fixture(scope="session")
def lakefs_endpoint() -> str:
    return os.environ["LAKECTL_SERVER_ENDPOINT_URL"]


@pytest.fixture(scope="session")
def lakefs_access_key() -> str:
    return os.environ["LAKECTL_CREDENTIALS_ACCESS_KEY_ID"]


@pytest.fixture(scope="session")
def lakefs_secret_key() -> str:
    return os.environ["LAKECTL_CREDENTIALS_SECRET_ACCESS_KEY"]


@pytest.fixture(scope="session")
def lakefs_client(
    lakefs_endpoint: str, lakefs_access_key: str, lakefs_secret_key: str
) -> Client:
    return Client(
        host=lakefs_endpoint,
        username=lakefs_access_key,
        password=lakefs_secret_key,
    )


@pytest.fixture(scope="session")
def lakefs_storage_namespace() -> str:
    """Storage namespace for the seeded repo (e.g. ``s3://bucket/path``).

    Set via ``LAKEFS_STORAGE_NAMESPACE``; the bucket must already exist on
    the configured object store (created by CI before the suite runs).
    """
    return os.environ["LAKEFS_STORAGE_NAMESPACE"]


@pytest.fixture(scope="session")
def seeded_repo(lakefs_client: Client, lakefs_storage_namespace: str) -> Iterator[str]:
    """Create the seed repository and populate it on first use.

    Layout (created idempotently):

        main:
            data/hello.txt        ("hello",  user_metadata: {"lang": "en"})
            data/world.txt        ("world")
            other/note.txt        ("side note")

        feature (branched from main):
            data/feature-only.txt ("feature")
    """
    repo = lakefs.Repository(REPO_NAME, client=lakefs_client).create(
        storage_namespace=lakefs_storage_namespace,
        default_branch="main",
        exist_ok=True,
    )

    main = repo.branch("main")
    if not main.object("data/hello.txt").exists():
        main.object("data/hello.txt").upload(data=b"hello", metadata={"lang": "en"})
        main.object("data/world.txt").upload(data=b"world")
        main.object("other/note.txt").upload(data=b"side note")
        main.commit(message="seed main branch")

    feature = repo.branch(FEATURE_BRANCH).create(source_reference="main", exist_ok=True)
    if not feature.object("data/feature-only.txt").exists():
        feature.object("data/feature-only.txt").upload(data=b"feature")
        feature.commit(message="seed feature branch")

    yield REPO_NAME


@pytest.fixture(scope="session")
def bulk_prefix(seeded_repo: str, lakefs_client: Client) -> str:
    """Seed ``BULK_COUNT`` tiny files under ``BULK_PREFIX`` on ``main``.

    Used to exercise paginated listings: ``BULK_COUNT`` exceeds the lakeFS
    list-objects page size (default 1000), so a correct loader must
    iterate across pages to return every object.

    The fixture is idempotent: if the last expected file already exists,
    the seed is skipped. Uploads run concurrently to keep first-run time
    reasonable.
    """
    repo = lakefs.Repository(seeded_repo, client=lakefs_client)
    main = repo.branch("main")
    last_path = f"{BULK_PREFIX}{BULK_COUNT - 1:08d}.txt"
    if not main.object(last_path).exists():

        def _upload(i: int) -> None:
            main.object(f"{BULK_PREFIX}{i:08d}.txt").upload(data=b"x")

        with ThreadPoolExecutor(max_workers=16) as pool:
            list(pool.map(_upload, range(BULK_COUNT)))
        main.commit(message=f"seed {BULK_COUNT} files under {BULK_PREFIX}")
    return BULK_PREFIX
