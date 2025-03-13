"""Test chat model integration."""

from typing import Type

from langchain_lakefs.chat_models import ChatLakeFS
from langchain_tests.unit_tests import ChatModelUnitTests


class TestChatLakeFSUnit(ChatModelUnitTests):
    @property
    def chat_model_class(self) -> Type[ChatLakeFS]:
        return ChatLakeFS

    @property
    def chat_model_params(self) -> dict:
        # These should be parameters used to initialize your integration for testing
        return {
            "model": "bird-brain-001",
            "temperature": 0,
            "parrot_buffer_length": 50,
        }
