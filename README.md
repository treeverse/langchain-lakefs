# langchain-lakefs

This package provides a LangChain integration with [lakeFS](https://lakefs.io/), allowing you to load documents from lakeFS repositories into your LangChain workflows.

## Features

- Load documents from lakeFS repositories using the official lakeFS Python SDK
- Support for user metadata retrieval
- Configurable repository, reference, and path specifications
- Integration with LangChain's document loading infrastructure

## Installation

```bash
pip install -U langchain-lakefs
```

## Configuration

You can configure the `LakeFSLoader` in three ways:

### 1. Direct Initialization

Provide the access key, secret key, and endpoint during initialization:

```python
from langchain_lakefs.document_loaders import LakeFSLoader

lakefs_loader = LakeFSLoader(
    lakefs_access_key='your_access_key',
    lakefs_secret_key='your_secret_key',
    lakefs_endpoint='https://path-to.lakefs.com',
    repo='your_repo',
    ref='main',
    path='path/to/files'
)
```

### 2. Configuration File

The package will automatically read credentials from the `~/.lakectl.yaml` file if available.

### 3. Environment Variables

Set the following environment variables to configure the loader:

```bash
export LAKECTL_CREDENTIALS_ACCESS_KEY_ID='your_access_key'
export LAKECTL_CREDENTIALS_SECRET_ACCESS_KEY='your_secret_key'
export LAKECTL_SERVER_ENDPOINT_URL='https://path-to.lakefs.com'
```

## Usage

### Document Loader

The `LakeFSLoader` class allows you to load documents from lakeFS. You need to specify:

- The repository (`repo`)
- The reference (`ref`) - branch, commit or tag
- The path to the files you want to load

If you would like to load the metadata of the files, you can set the `user_metadata` parameter to `True`:

```python
from langchain_lakefs.document_loaders import LakeFSLoader

# Initialize the loader
lakefs_loader = LakeFSLoader(
    lakefs_access_key='your_access_key',
    lakefs_secret_key='your_secret_key',
    lakefs_endpoint='https://path-to.lakefs.com',
    repo='your_repo',
    ref='main',
    path='path/to/files',
    user_metadata=True
)

# Load documents from lakeFS
documents = lakefs_loader.load()

# Process the documents
for doc in documents:
    print(f"Content: {doc.page_content}")
    print(f"Metadata: {doc.metadata}")
```

### Modifying Loader Settings

You can modify the loader settings after initialization:

```python
# Change the repository
lakefs_loader.set_repo("another-repo")

# Change the reference (branch or commit)
lakefs_loader.set_ref("feature-branch")

# Change the path
lakefs_loader.set_path("another/path")

# Toggle user metadata retrieval
lakefs_loader.set_user_metadata(True)
```

## Examples

### Loading Documents from a Specific Path

```python
from langchain_lakefs.document_loaders import LakeFSLoader

loader = LakeFSLoader(
    lakefs_endpoint="https://example.my-lakefs.com",
    lakefs_access_key="your-access-key",
    lakefs_secret_key="your-secret-key",
    repo="my-repo",
    ref="main",
    path="data/documents"
)

documents = loader.load()
```
