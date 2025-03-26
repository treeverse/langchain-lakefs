"""LakeFS document loader using the official lakeFS Python SDK."""
import tempfile
import os
from typing import List, Optional, Any
import lakefs.branch
from lakefs.client import Client
from langchain_core.document_loaders.base import BaseLoader
from langchain_core.documents import Document
from langchain_community.document_loaders.unstructured import UnstructuredBaseLoader
from unstructured.partition.auto import partition


class LakeFSLoader(BaseLoader):
    """
    LakeFS document loader integration using the official lakeFS Python SDK.

    Setup:
        Install ``langchain-lakefs`` and ``lakefs``:

        .. code-block:: bash

            pip install -U langchain-lakefs lakefs-client

    Instantiate:
        .. code-block:: python
            from langchain_lakefs.document_loaders import LakeFSLoader

            loader = LakeFSLoader(
                lakefs_endpoint="https://example.my-lakefs.com",
                lakefs_access_key="your-access-key",
                lakefs_secret_key="your-secret-key",
                repo="my-repo",
                ref="main",
                path="path/to/files"
            )
    """

    def __init__(
            self,
            lakefs_endpoint: str,
            lakefs_access_key: str,
            lakefs_secret_key: str,
            repo: str = "",
            ref: str = "main",
            path: str = "",
    ):
        self.client = Client(
            host=lakefs_endpoint,
            username=lakefs_access_key,
            password=lakefs_secret_key
        )
        self.repo = repo
        self.ref = ref
        self.path = path
        self.user_metadata = False

    def set_path(self, path: str) -> None:
        """Set the path to load documents from."""
        self.path = path

    def set_ref(self, ref: str) -> None:
        """Set the ref to load documents from."""
        self.ref = ref

    def set_repo(self, repo: str) -> None:
        """Set the repository to load documents from."""
        self.repo = repo

    def set_user_metadata(self, user_metadata: bool) -> None:
        """Set whether to load user metadata."""
        self.user_metadata = user_metadata

    def load(self) -> List[Document]:
        """Load documents from lakeFS using presigned URLs if supported."""

        self.__validate_instance()

        objects = lakefs.repository(self.repo, client=self.client).ref(self.ref).objects(user_metadata=True, prefix=self.path)
        documents = [
            doc
            for obj in objects  # Iterate over ObjectInfo instances
            for doc in UnstructuredLakeFSLoader(
                obj.physical_address,  # Extract physical_address
                self.repo,
                self.ref,
                obj.path,  # Extract path
                user_metadata=obj.metadata,  # Extract metadata
                client=self.client,
            ).load()
        ]

        return documents

    def __validate_instance(self) -> None:
        if self.repo is None or self.repo == "":
            raise ValueError(
                "no repository was provided. use `set_repo` to specify a repository"
            )
        if self.ref is None or self.ref == "":
            raise ValueError("no ref was provided. use `set_ref` to specify a ref")
        if self.path is None:
            raise ValueError("no path was provided. use `set_path` to specify a path")


class UnstructuredLakeFSLoader(UnstructuredBaseLoader):
    """Load from `lakeFS` as unstructured data."""

    def __init__(
            self,
            url: str,
            repo: str,
            ref: str = "main",
            path: str = "",
            presign: bool = True,
            client: Optional[Client] = None,
            # presign: bool = False,
            user_metadata: Optional[dict[str,str]] = None,
            **unstructured_kwargs: Any,
    ):
        """Initialize UnstructuredLakeFSLoader.

        Args:
        :param url:
        :param repo:
        :param ref:
        :param path:
        :param presign:
        :param user_metadata:
        :param lakefs_access_key:
        :param lakefs_secret_key:
        :param lakefs_endpoint:
        """

        super().__init__(**unstructured_kwargs)
        self.user_metadata = user_metadata
        self.url = url
        self.repo = repo
        self.ref = ref
        self.path = path
        self.presign = presign
        self.client = client

    def _get_metadata(self) -> dict[str, any]:
        metadata = {"repo": self.repo, "ref": self.ref, "path": self.path}
        if self.user_metadata:
            for key, value in self.user_metadata.items():
                if key not in metadata:
                    metadata[key] = value
        return metadata

    def _get_elements(self) -> List:
        local_prefix = "local://"
        if self.url.startswith(local_prefix):
            local_path = self.url[len(local_prefix):]
            return partition(filename=local_path)
        else:
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = f"{temp_dir}/{self.path.split('/')[-1]}"
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                obj = lakefs.repository(self.repo, client=self.client).ref(self.ref).object(self.path)
                with open(file_path, mode="wb") as file:
                    file.write(obj.reader().read())
                    return partition(filename=file_path)
