"""Test embedding model integration."""

from typing import Type

from langchain_tests.unit_tests import EmbeddingsUnitTests

from langchain_lakefs.embeddings import LakeFSEmbeddings


class TestParrotLinkEmbeddingsUnit(EmbeddingsUnitTests):
    @property
    def embeddings_class(self) -> Type[LakeFSEmbeddings]:
        return LakeFSEmbeddings

    @property
    def embedding_model_params(self) -> dict:
        return {"model": "nest-embed-001"}
