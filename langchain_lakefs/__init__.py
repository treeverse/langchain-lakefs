from importlib import metadata

from langchain_lakefs.chat_models import ChatLakeFS
from langchain_lakefs.document_loaders import LakeFSLoader
from langchain_lakefs.embeddings import LakeFSEmbeddings
from langchain_lakefs.retrievers import LakeFSRetriever
from langchain_lakefs.toolkits import LakeFSToolkit
from langchain_lakefs.tools import LakeFSTool
from langchain_lakefs.vectorstores import LakeFSVectorStore

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = ""
del metadata  # optional, avoids polluting the results of dir(__package__)

__all__ = [
    "ChatLakeFS",
    "LakeFSVectorStore",
    "LakeFSEmbeddings",
    "LakeFSLoader",
    "LakeFSRetriever",
    "LakeFSToolkit",
    "LakeFSTool",
    "__version__",
]
