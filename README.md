# langchain-lakefs

This package contains the LangChain integration with LakeFS

## Installation

```bash
pip install -U langchain-lakefs
```

And you should configure credentials by setting the following environment variables:

* TODO: fill this out

## Chat Models

`ChatLakeFS` class exposes chat models from LakeFS.

```python
from langchain_lakefs import ChatLakeFS

llm = ChatLakeFS()
llm.invoke("Sing a ballad of LangChain.")
```

## Embeddings

`LakeFSEmbeddings` class exposes embeddings from LakeFS.

```python
from langchain_lakefs import LakeFSEmbeddings

embeddings = LakeFSEmbeddings()
embeddings.embed_query("What is the meaning of life?")
```

## LLMs
`LakeFSLLM` class exposes LLMs from LakeFS.

```python
from langchain_lakefs import LakeFSLLM

llm = LakeFSLLM()
llm.invoke("The meaning of life is")
```
