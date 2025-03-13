from typing import Type

from langchain_lakefs.retrievers import LakeFSRetriever
from langchain_tests.integration_tests import (
    RetrieversIntegrationTests,
)


class TestLakeFSRetriever(RetrieversIntegrationTests):
    @property
    def retriever_constructor(self) -> Type[LakeFSRetriever]:
        """Get an empty vectorstore for unit tests."""
        return LakeFSRetriever

    @property
    def retriever_constructor_params(self) -> dict:
        return {"k": 2}

    @property
    def retriever_query_example(self) -> str:
        """
        Returns a str representing the "query" of an example retriever call.
        """
        return "example query"
