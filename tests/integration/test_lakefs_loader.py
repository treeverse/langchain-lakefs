"""Integration tests for ``LakeFSLoader`` against a real lakeFS server."""

import pytest

from langchain_lakefs.document_loaders import LakeFSLoader


def _make_loader(
    endpoint: str,
    access_key: str,
    secret_key: str,
    repo: str,
    ref: str = "main",
    path: str = "",
    user_metadata: bool = False,
) -> LakeFSLoader:
    return LakeFSLoader(
        lakefs_endpoint=endpoint,
        lakefs_access_key=access_key,
        lakefs_secret_key=secret_key,
        repo=repo,
        ref=ref,
        path=path,
        user_metadata=user_metadata,
    )


def _paths(documents: list) -> set[str]:
    return {doc.metadata["path"] for doc in documents}


def test_load_all_returns_documents(
    seeded_repo: str,
    lakefs_endpoint: str,
    lakefs_access_key: str,
    lakefs_secret_key: str,
) -> None:
    loader = _make_loader(
        lakefs_endpoint, lakefs_access_key, lakefs_secret_key, seeded_repo
    )
    documents = loader.load()

    assert _paths(documents) == {
        "data/hello.txt",
        "data/world.txt",
        "other/note.txt",
    }
    for doc in documents:
        assert doc.metadata["repo"] == seeded_repo
        assert doc.metadata["ref"] == "main"
        assert "path" in doc.metadata


def test_load_with_path_prefix(
    seeded_repo: str,
    lakefs_endpoint: str,
    lakefs_access_key: str,
    lakefs_secret_key: str,
) -> None:
    loader = _make_loader(
        lakefs_endpoint,
        lakefs_access_key,
        lakefs_secret_key,
        seeded_repo,
        path="data/",
    )
    documents = loader.load()

    assert _paths(documents) == {"data/hello.txt", "data/world.txt"}


def test_load_from_branch(
    seeded_repo: str,
    lakefs_endpoint: str,
    lakefs_access_key: str,
    lakefs_secret_key: str,
) -> None:
    loader = _make_loader(
        lakefs_endpoint,
        lakefs_access_key,
        lakefs_secret_key,
        seeded_repo,
        ref="feature",
    )

    feature_paths = _paths(loader.load())
    assert "data/feature-only.txt" in feature_paths

    loader.set_ref("main")
    main_paths = _paths(loader.load())
    assert "data/feature-only.txt" not in main_paths


def test_load_with_user_metadata(
    seeded_repo: str,
    lakefs_endpoint: str,
    lakefs_access_key: str,
    lakefs_secret_key: str,
) -> None:
    loader = _make_loader(
        lakefs_endpoint,
        lakefs_access_key,
        lakefs_secret_key,
        seeded_repo,
        path="data/hello.txt",
        user_metadata=True,
    )
    documents = loader.load()
    hello = next(d for d in documents if d.metadata["path"] == "data/hello.txt")
    assert hello.metadata.get("lang") == "en"

    loader.set_user_metadata(False)
    plain = loader.load()
    hello_plain = next(d for d in plain if d.metadata["path"] == "data/hello.txt")
    assert "lang" not in hello_plain.metadata


def test_load_empty_prefix_returns_all(
    seeded_repo: str,
    lakefs_endpoint: str,
    lakefs_access_key: str,
    lakefs_secret_key: str,
) -> None:
    loader = _make_loader(
        lakefs_endpoint, lakefs_access_key, lakefs_secret_key, seeded_repo
    )
    loader.set_path("")
    documents = loader.load()
    assert len(documents) == 3


def test_load_paginated_listing(
    seeded_repo: str,
    bulk_prefix: str,
    lakefs_endpoint: str,
    lakefs_access_key: str,
    lakefs_secret_key: str,
) -> None:
    """All objects are returned even when the prefix exceeds one page."""
    loader = _make_loader(
        lakefs_endpoint,
        lakefs_access_key,
        lakefs_secret_key,
        seeded_repo,
        path=bulk_prefix,
    )
    documents = loader.load()
    paths = _paths(documents)
    assert len(paths) == 1500
    assert f"{bulk_prefix}00000000.txt" in paths
    assert f"{bulk_prefix}00001499.txt" in paths


def test_validation_missing_repo(
    lakefs_endpoint: str,
    lakefs_access_key: str,
    lakefs_secret_key: str,
) -> None:
    loader = LakeFSLoader(
        lakefs_endpoint=lakefs_endpoint,
        lakefs_access_key=lakefs_access_key,
        lakefs_secret_key=lakefs_secret_key,
    )
    with pytest.raises(ValueError, match="repository"):
        loader.load()


def test_validation_missing_ref(
    seeded_repo: str,
    lakefs_endpoint: str,
    lakefs_access_key: str,
    lakefs_secret_key: str,
) -> None:
    loader = _make_loader(
        lakefs_endpoint, lakefs_access_key, lakefs_secret_key, seeded_repo
    )
    loader.set_ref("")
    with pytest.raises(ValueError, match="ref"):
        loader.load()
