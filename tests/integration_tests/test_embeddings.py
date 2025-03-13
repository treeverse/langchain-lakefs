"""Test LakeFS embeddings."""

from typing import Type

from langchain_lakefs.embeddings import LakeFSEmbeddings
from langchain_tests.integration_tests import EmbeddingsIntegrationTests


class TestParrotLinkEmbeddingsIntegration(EmbeddingsIntegrationTests):
    @property
    def embeddings_class(self) -> Type[LakeFSEmbeddings]:
        return LakeFSEmbeddings

    @property
    def embedding_model_params(self) -> dict:
        return {"model": "nest-embed-001"}
