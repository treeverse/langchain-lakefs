import unittest
from typing import Any
from unittest.mock import patch

import lakefs_sdk
import pytest
from lakefs import ObjectReader, Reference, StoredObject

from langchain_lakefs.document_loaders import LakeFSLoader


@pytest.fixture
def mock_get_object() -> Any:
    with patch.object(ObjectReader, "read", return_value=b"pdf content"):
        yield


@pytest.fixture
def mock_get_storage_id() -> Any:
    with patch.object(StoredObject, "storage_id", return_value=""):
        yield


@pytest.fixture
def mock_get_reader() -> Any:
    with patch.object(
        StoredObject,
        "reader",
        return_value=ObjectReader(None, mode="r", pre_sign=True, client=None),
    ):
        yield


@pytest.fixture
def mock_unstructured_local() -> Any:
    with patch(
        "langchain_lakefs.document_loaders.UnstructuredLakeFSLoader"
    ) as mock_unstructured_lakefs:
        mock_unstructured_lakefs.return_value.load.return_value = [
            ("text content", "pdf content")
        ]
        yield mock_unstructured_lakefs.return_value


@pytest.fixture
def mock_list_objects() -> Any:
    fake_list = [
        lakefs_sdk.ObjectStats(
            path="fake_path_1.txt",
            path_type="object",
            physical_address="fake_address_1",
            checksum="checksum1",
            metadata={"key": "value", "key2": "value2"},
            size_bytes=123,
            mtime=1234567890,
        ),
        lakefs_sdk.ObjectStats(
            path="fake_path_2.txt",
            path_type="object",
            physical_address="fake_address_2",
            metadata={"key": "value", "key2": "value2"},
            checksum="checksum2",
            size_bytes=456,
            mtime=1234567891,
        ),
    ]
    with patch.object(Reference, "objects", return_value=fake_list):
        yield


class TestLakeFSLoader(unittest.TestCase):
    lakefs_access_key: str = "lakefs_access_key"
    lakefs_secret_key: str = "lakefs_secret_key"
    endpoint: str = "http://localhost:8000"
    repo: str = "repo"
    ref: str = "ref"
    path: str = "path"

    @pytest.mark.usefixtures("mock_unstructured_local", "mock_list_objects")
    def test_non_presigned_loading(self) -> None:
        loader = LakeFSLoader(
            lakefs_access_key="lakefs_access_key",
            lakefs_secret_key="lakefs_secret_key",
            lakefs_endpoint=self.endpoint,
        )
        loader.set_repo(self.repo)
        loader.set_ref(self.ref)
        loader.set_path(self.path)
        loader.load()

    @pytest.mark.usefixtures(
        "mock_list_objects", "mock_get_object", "mock_get_storage_id", "mock_get_reader"
    )
    def test_load(self) -> None:
        loader = LakeFSLoader(
            lakefs_access_key="lakefs_access_key",
            lakefs_secret_key="lakefs_secret_key",
            lakefs_endpoint=self.endpoint,
        )

        loader.set_repo(self.repo)
        loader.set_ref(self.ref)
        loader.set_path(self.path)
        documents = loader.load()
        self.assertEqual(len(documents), 2)
        self.assertEqual(len(documents[0].metadata), 5)
