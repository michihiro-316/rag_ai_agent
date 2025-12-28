# LangChain チートシート

電車で覚える用。現場で使うものだけに絞りました。

---

## 0. なぜLangChainを使うのか

**各社のSDKは書き方がバラバラ:**

```python
# OpenAI SDK
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "こんにちは"}]
)
print(response.choices[0].message.content)

# Google SDK
import google.generativeai as genai
model = genai.GenerativeModel("gemini-2.0-flash")
response = model.generate_content("こんにちは")
print(response.text)
```

**LangChainなら統一された書き方:**

```python
# どのLLMでも同じ！
llm = ChatGoogleGenerativeAI(...)  # または ChatOpenAI, ChatAnthropic
response = llm.invoke("こんにちは")
print(response.content)  # ← 全部これでOK
```

**メリット:**
- LLMを切り替えても、コードの書き換えが最小限
- `.invoke()` / `.content` など統一されたAPI
- プロンプトテンプレート、チェーン、ツールなど便利機能が揃っている

---

## 1. 基本の流れ

```
prompt → llm → output
  ↓       ↓       ↓
テンプレ  AI処理   結果
```

**覚え方: 「prompt で準備 → llm で実行」**

---

## 2. 最小限のコード

```python
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# 準備
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-001",
    project="dify-chatbot-469403",
    location="us-central1"
)
prompt = ChatPromptTemplate.from_messages([
    ("system", "あなたは料理の専門家です"),
    ("human", "{dish}のレシピを教えて")
])

# 実行（パイプでつなぐ）
chain = prompt | llm
result = chain.invoke({"dish": "カレー"})
print(result.content)
```

---

## 3. プロンプトの書き方

```python
from langchain_core.prompts import ChatPromptTemplate

# 基本形（system + human）
prompt = ChatPromptTemplate.from_messages([
    ("system", "あなたは〇〇です"),
    ("human", "{question}")
])

# シンプルな形（humanだけ）
prompt = ChatPromptTemplate.from_template("{question}に答えて")
```

### メッセージの種類

```python
("system", "...")   # AIへの指示
("human", "...")    # ユーザーの発言
("ai", "...")       # AIの過去の発言
```

---

## 4. チェーン（LCEL記法）

### 基本の書き方（バラバラに実行）

```python
# 1. テンプレートに変数を埋める
prompt_value = prompt.invoke({"question": "こんにちは"})

# 2. AIに送って回答をもらう
result = llm.invoke(prompt_value)
print(result.content)
```

### パイプでつなぐ（ショートカット）

```python
# 上と同じことを1行で
chain = prompt | llm
result = chain.invoke({"question": "こんにちは"})
print(result.content)
```

`|` は「左の出力を右の入力に渡す」という意味。

---

## 5. Function Calling

AIが「どの関数を呼ぶか」を判断する機能。

```python
from langchain_core.tools import tool

# 1. ツールを定義（docstringは必須！）
@tool
def get_weather(city: str) -> str:
    """指定した都市の天気を取得する"""
    return f"{city}の天気は晴れです"

# 2. LLMにツールをバインド
llm_with_tools = llm.bind_tools([get_weather])

# 3. 質問する
response = llm_with_tools.invoke("東京の天気は？")

# 4. ツールを実行（手動）
if response.tool_calls:
    tool_call = response.tool_calls[0]
    result = get_weather.invoke(tool_call["args"])
    print(result)
```

**ポイント:** AIは「どの関数を呼ぶか」を決めるだけ。実行は自分でやる。

---

## 6. 会話履歴（チャットボット用）

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "あなたはアシスタントです"),
    MessagesPlaceholder(variable_name="history", optional=True),
    ("human", "{question}")
])

# 履歴を渡す
result = prompt.invoke({
    "question": "私の名前は？",
    "history": [
        ("human", "私は田中です"),
        ("ai", "こんにちは、田中さん！")
    ]
})
```

---

## 7. ストリーミング（参考程度でOK）

ChatGPTみたいに「文字がポロポロ出てくる」演出。UI演出なので後回しでOK。

「ストリーミング」というワードだけ覚えておけば大丈夫。

```python
for chunk in llm.stream("長い話をして"):
    print(chunk.content, end="", flush=True)
```

---

## 8. LLMの初期化（Vertex AI）

```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-001",
    project="dify-chatbot-469403",
    location="us-central1"
)

result = llm.invoke("こんにちは")
print(result.content)
```

**他のLLMを使う場合も同じ書き方で動く:**
```python
# OpenAI
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o")

# Anthropic (Claude)
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-3-5-sonnet")
```

---

## 9. よくあるエラー

| エラー | 原因 | 解決 |
|--------|------|------|
| `has no attribute 'text'` | ChatPromptValueに`.text`はない | `.to_string()` を使う |
| `must have a docstring` | @toolにdocstringがない | `"""説明"""` を追加 |
| `{"a", "b"}` がエラー | セットになってる | `("a", "b")` タプルに |

---

## 10. Python文法メモ

```python
# タプル（LangChainで使う）
("system", "こんにちは")

# 辞書（これもOK）
{"role": "system", "content": "こんにちは"}

# セット（間違い！使わない）
{"system", "こんにちは"}
```

---

これで基本はOK！
