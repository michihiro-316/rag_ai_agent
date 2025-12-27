# RAG AI Agent

生成AI・RAG・LangChainの学習用Python環境です。

## セットアップ

### 1. 仮想環境の有効化

```bash
source .venv/bin/activate
```

### 2. 環境変数の設定

プロジェクトルートに`.env`ファイルを作成し、APIキーを設定してください。

```bash
cp .env.example .env
# .envファイルを編集してAPIキーを設定
```

## 使い方

### JupyterLabの起動

```bash
jupyter lab
```

ブラウザが自動で開き、Jupyter環境が利用できます。

### VSCodeでの利用

1. `.ipynb`ファイルを直接開く
2. 右上のカーネル選択で`.venv`を選択

## インストール済みライブラリ

### データサイエンス
- numpy
- pandas
- matplotlib

### 生成AI / LLM
- openai
- tiktoken

### LangChain
- langchain
- langchain-openai
- langchain-community
- langchain-chroma

### RAG / ベクトルDB
- chromadb

### ユーティリティ
- python-dotenv
- jupyterlab

## サンプルコード

### OpenAI APIの利用

```python
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

### LangChainの利用

```python
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o")
response = llm.invoke("Hello!")
print(response.content)
```

### RAG (ChromaDB + LangChain)

```python
from dotenv import load_dotenv
load_dotenv()

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# ベクトルストアの作成
embeddings = OpenAIEmbeddings()
vectorstore = Chroma(
    collection_name="my_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

# ドキュメントの追加
vectorstore.add_texts(["Hello, world!", "LangChain is great!"])

# 類似検索
results = vectorstore.similarity_search("greeting", k=1)
print(results)
```

## 環境の終了

```bash
deactivate
```
