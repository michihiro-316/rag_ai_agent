# LangChain チートシート

電車で覚える用。現場で使うものだけに絞りました。

**最終更新日:** 2026-01-06（LangGraphタブを追加、7タブ構成に変更）

---

<!-- タブUI用のHTML/CSS -->
<style>
.tab-container {
  margin: 20px 0;
}
.tab-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  border-bottom: 2px solid #e0e0e0;
  margin-bottom: 20px;
}
.tab-button {
  padding: 10px 16px;
  border: none;
  background: #f5f5f5;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  border-radius: 8px 8px 0 0;
  transition: all 0.2s;
}
.tab-button:hover {
  background: #e8e8e8;
}
.tab-button.active {
  background: #4CAF50;
  color: white;
}
.tab-content {
  display: none;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 0 0 8px 8px;
}
.tab-content.active {
  display: block;
}
</style>

<div class="tab-container">
<div class="tab-buttons">
  <button class="tab-button active" onclick="openTab(event, 'basic')">基礎</button>
  <button class="tab-button" onclick="openTab(event, 'chain')">チェーン</button>
  <button class="tab-button" onclick="openTab(event, 'rag')">RAG</button>
  <button class="tab-button" onclick="openTab(event, 'tools')">ツール</button>
  <button class="tab-button" onclick="openTab(event, 'practice')">実践</button>
  <button class="tab-button" onclick="openTab(event, 'reference')">補足</button>
  <button class="tab-button" onclick="openTab(event, 'langgraph')">LangGraph</button>
</div>

<!-- ==================== 基礎タブ ==================== -->
<div id="basic" class="tab-content active">

## 1. なぜLangChainを使うのか

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

## 2. LLMの初期化（まず動かす）

```python
from dotenv import load_dotenv
load_dotenv()  # .envからAPIキーを読み込む

from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-001",
    project="your-project-id",
    location="us-central1"
)

result = llm.invoke("こんにちは")
print(result.content)
```

**他のLLMを使う場合も同じ書き方:**
```python
# OpenAI
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o")

# Anthropic (Claude)
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-3-5-sonnet")
```

---

## 3. 基本の流れ

```
prompt → llm → output
  ↓       ↓       ↓
テンプレ  AI処理   結果
```

**覚え方: 「prompt で準備 → llm で実行」**

---

## 4. 最小限のコード

```python
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# 準備
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-001",
    project="your-project-id",
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

## 5. プロンプトの書き方

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

### 変数が複数の場合

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "あなたは{role}です"),
    ("human", "{name}さん、{dish}のレシピを教えて")
])

# 変数が複数でもOK（実行方法は6章で説明）
```

---

## 6. チェーン（LCEL記法）

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

### 変数が複数の場合

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "あなたは{role}です"),
    ("human", "{name}さん、{dish}のレシピを教えて")
])

chain = prompt | llm

# 変数が複数 → 辞書に全部入れるだけ
result = chain.invoke({
    "role": "料理の専門家",
    "name": "田中",
    "dish": "カレー"
})
print(result.content)
```

`|` は「左の出力を右の入力に渡す」という意味。

### StrOutputParser（.content を省略）

```python
from langchain_core.output_parsers import StrOutputParser

# LLMの出力
result = llm.invoke("こんにちは")
print(type(result))    # → AIMessage
print(result.content)  # → "こんにちは！"

# StrOutputParser を使うと
chain = prompt | llm | StrOutputParser()
result = chain.invoke(...)
print(type(result))    # → str（文字列）
print(result)          # → "こんにちは！"（.content 不要）
```

**使い所:** チェーンの最後に付けると、`.content` を書かなくて済む

</div>

<!-- ==================== チェーンタブ ==================== -->
<div id="chain" class="tab-content">

## 7. Runnable（パイプラインで関数を使う）

> **このセクションの主要関数:** `lambda` / `RunnableLambda` / `@chain`

### 3つの方法

```python
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables import chain  # ← @chain デコレータ用

# 方法1: lambda（最も一般的）★よく使う
my_chain = (
    (lambda x: x.upper())
    | (lambda x: f"結果: {x}")
)
my_chain.invoke("hello")  # → "結果: HELLO"

# 方法2: RunnableLambda（明示的に書く場合）
RunnableLambda(lambda x: x.upper())

# 方法3: @chain デコレータ（複雑な処理の場合）
# → 下の「@chainの実践例」を参照
```

### 実践パターン: 文字列 → 辞書に変換

```python
# よくあるパターン: 文字列入力を辞書に変換して次に渡す
my_chain = (
    (lambda x: {"dish": x})  # 文字列 → 辞書
    | prompt
    | llm
    | StrOutputParser()
)

my_chain.invoke("オムライス")  # 文字列で直接呼べる
```

### @chain の実践例（複雑な処理をまとめる）

lambdaでは書きにくい「複数行の処理」や「条件分岐」がある場合に使う。

```python
from langchain_core.runnables import chain

@chain
def validate_and_format(input_text: str) -> dict:
    """入力を検証してフォーマットする"""
    # 複数行の処理が書ける
    text = input_text.strip()

    if len(text) < 2:
        return {"error": "入力が短すぎます", "dish": None}

    # 先頭を大文字に
    formatted = text.capitalize()

    return {"dish": formatted, "original": text}

# パイプラインで使える
my_chain = validate_and_format | prompt | llm | StrOutputParser()

my_chain.invoke("カレー")
# → {"dish": "カレー", "original": "カレー"} がpromptに渡る
```

**@chain を使う場面:**
| 場面 | 例 |
|------|-----|
| 複数行の処理 | 入力の検証、整形、変換など |
| 条件分岐 | if文で処理を分ける |
| try-except | エラーハンドリングが必要な時 |
| デバッグ | print文を入れたい時 |

**lambda vs @chain:**
```python
# lambda: 1行で書ける簡単な処理
(lambda x: {"dish": x})

# @chain: 複数行や条件分岐がある処理
@chain
def process(x):
    if not x:
        return {"error": "empty"}
    return {"dish": x.strip()}
```

**まとめ:**
- `lambda x: ...` を使えばOK（90%のケースはこれで十分）
- `RunnableLambda` は明示的に書きたい時だけ
- `@chain` は複数行の処理・条件分岐・エラーハンドリングが必要な時

---

## 7.5 並列実行（RunnableParallel）

> **このセクションの主要関数:** `RunnableParallel`

### 基本の使い方

```python
from langchain_core.runnables import RunnableParallel

chain = RunnableParallel(
    key1=チェーン1,
    key2=チェーン2,
)
result = chain.invoke(入力)
# → {"key1": 結果1, "key2": 結果2}
```

### 実践例: 複数観点で同時分析

```python
from langchain_core.runnables import RunnableParallel

prompt_ingredients = ChatPromptTemplate.from_template("{dish}の材料を3つだけ")
prompt_calories = ChatPromptTemplate.from_template("{dish}のカロリーを数値だけ")

chain = (
    (lambda x: {"dish": x})
    | RunnableParallel(
        ingredients=prompt_ingredients | llm | StrOutputParser(),
        calories=prompt_calories | llm | StrOutputParser(),
    )
)

result = chain.invoke("カレー")
# → {"ingredients": "・玉ねぎ\n・肉\n・ルー", "calories": "約600kcal"}
```

### いつ使う？

| ユースケース | 例 |
|-------------|-----|
| 複数観点で同時分析 | 感情分析 + キーワード抽出 + 要約 |
| RAGで検索と質問を同時処理 | context=retriever, question=質問リライト |
| 多言語同時翻訳 | english=英訳, chinese=中訳, korean=韓訳 |

**ポイント:** 独立した処理を同時に走らせて**時間短縮**

---

## 7.6 条件分岐（RunnableBranch）

> **このセクションの主要関数:** `RunnableBranch`

### 基本の使い方

```python
from langchain_core.runnables import RunnableBranch

branch = RunnableBranch(
    (条件関数1, Trueの時のチェーン),
    (条件関数2, Trueの時のチェーン),
    デフォルトのチェーン,  # ← タプルじゃない = どれにも当てはまらない時
)
```

### 実践例: 入力タイプ別ルーティング

```python
def is_food_question(x):
    dish = x["dish"]  # ← 前のステップの出力がdictなら取り出す
    return "カレー" in dish or "作り方" in dish or "レシピ" in dish

prompt_recipe = ChatPromptTemplate.from_template("料理に関する情報：{dish}")

chain = (
    (lambda x: {"dish": x})
    | RunnableBranch(
        (is_food_question, prompt_recipe | llm | StrOutputParser()),
        lambda x: "料理に関する質問をしてください"
    )
)

chain.invoke("カレーの作り方")  # → レシピが返る
chain.invoke("天気を教えて")    # → "料理に関する質問をしてください"
```

### いつ使う？

| ユースケース | 例 |
|-------------|-----|
| 入力タイプ別ルーティング | コード質問 → コード生成、計算 → 計算チェーン |
| 言語判定 | 日本語 → 日本語チェーン、英語 → 英語チェーン |
| エラーハンドリング | 検索結果あり → RAG回答、なし → フォールバック |

**ポイント:** 入力に応じて**処理を振り分ける**

### よくあるエラー

| エラー | 原因 | 解決 |
|--------|------|------|
| `default must be Runnable` | デフォルトがない | 最後にタプルでない引数を追加 |
| 条件が常にFalse | 条件関数の入力がdictなのに文字列として扱った | `x["key"]` で値を取り出す |

---

## 7.7 並列と分岐の比較

| 項目 | RunnableParallel | RunnableBranch |
|------|------------------|----------------|
| 目的 | 同時実行で時間短縮 | 条件で処理を分岐 |
| 出力 | dict（全結果をまとめる） | 選ばれた1つの結果 |
| 使う時 | 独立した複数処理 | 入力によって処理が変わる |

### 組み合わせも可能

```python
# 分岐の中で並列を使う
RunnableBranch(
    (is_food, RunnableParallel(recipe=..., calories=...)),
    "対応外です",
)
```

---

## 7.8 itemgetter（補足）

> **このセクションの主要関数:** `itemgetter`

dictから値を取り出す方法。lambdaでも書けるが、itemgetterは短く書ける。

```python
from operator import itemgetter

# 同じ意味
lambda x: x["dish"]
itemgetter("dish")

# 複数キー取得はitemgetterが便利
itemgetter("name", "age")  # → (name値, age値) をタプルで返す
```

**結論:** lambdaで慣れてから、必要になったらitemgetterを使えばOK

---

## 7.9 RunnablePassthrough 完全理解ガイド

> **このセクションの主要関数:** `RunnablePassthrough` / `RunnablePassthrough.assign` / `{}`（dictパターン）

**RunnablePassthrough は「荷物をそのまま次に渡す」イメージ**

### 小学生でもわかる例え話

```
🎒 荷物（入力データ）を持って旅をするイメージ

普通のチェーン:
  荷物 → 加工工場 → 新しい荷物（元の荷物は捨てられる）

RunnablePassthrough:
  荷物 → そのまま通過 → 荷物（何も変わらない）

RunnablePassthrough.assign:
  荷物 → そのまま通過しながら、おみやげを追加 → 荷物 + おみやげ
```

---

### RunnablePassthrough() とは？

**「入力をそのまま返す」** だけの超シンプルな部品。

```python
from langchain_core.runnables import RunnablePassthrough

# 何もしない。ただ通すだけ。
RunnablePassthrough().invoke("こんにちは")
# → "こんにちは"（そのまま！）
```

**図解:**
```
┌─────────────────────────────┐
│     RunnablePassthrough()   │
│                             │
│  入力: "こんにちは"          │
│           ↓                 │
│       そのまま通す           │
│           ↓                 │
│  出力: "こんにちは"          │
└─────────────────────────────┘
```

**lambda x: x と同じ意味:**
```python
# この2つは同じ動作
RunnablePassthrough()
lambda x: x
```

---

### RunnablePassthrough.assign() とは？

**「入力をそのまま通しつつ、新しいキーを追加する」** 機能。

```python
from langchain_core.runnables import RunnablePassthrough

chain = (
    (lambda x: {"question": x})  # まず dict を作る
    | RunnablePassthrough.assign(context=retriever)  # context を追加
)

chain.invoke("LangChainとは？")
```

**図解（これが一番大事！）:**
```
┌────────────────────────────────────────────────────────┐
│        RunnablePassthrough.assign(context=retriever)   │
│                                                        │
│  入力: {"question": "LangChainとは？"}                  │
│              ↓                                         │
│  ┌──────────────────────────────────────────────┐      │
│  │  ① Passthrough: 入力をそのまま保持           │      │
│  │     → {"question": "LangChainとは？"}        │      │
│  │                                              │      │
│  │  ② assign: retriever を実行して結果を追加    │      │
│  │     → context: [Doc1, Doc2, ...]             │      │
│  │                                              │      │
│  │  ③ マージ: 両方を合体                        │      │
│  │     → {"question": "...", "context": [...]}  │      │
│  └──────────────────────────────────────────────┘      │
│              ↓                                         │
│  出力: {"question": "LangChainとは？", "context": [...]}│
└────────────────────────────────────────────────────────┘
```

**ポイント:**
- `Passthrough` = 元のdictをそのまま通す（question を保持）
- `assign(context=...)` = 新しいキー `context` を追加
- 元の `question` が消えない！

---

### dictパターン（もう一つの書き方）

**dict `{}` を使うと、暗黙的に `RunnableParallel` に変換される。**

```python
chain = (
    {
        "question": RunnablePassthrough(),  # 入力をそのまま（= lambda x: x）
        "context": retriever                # 入力で検索
    }
    | prompt
    | llm
)

chain.invoke("LangChainとは？")
```

**補足:** `"question": RunnablePassthrough()` は `"question": lambda x: x` と同じ意味。どちらでもOK。

**図解:**
```
         "LangChainとは？"
              ↓
    ┌────────┴────────┐
    ↓                 ↓
 question:         context:
 Passthrough       retriever
    ↓                 ↓
"LangChainとは？"  [Doc1, Doc2]
    ↓                 ↓
    └────────┬────────┘
              ↓
 {"question": "LangChainとは？", "context": [Doc1, Doc2]}
```

**ポイント:**
- 同じ入力が `question` と `context` の両方に渡される
- それぞれの結果を dict にまとめる
- **「入力からdictを組み立てる設計図」** と考えるとわかりやすい

---

### 2つのパターンの比較

```python
# パターンA: dict（シンプル・RAGでよく使う）
{
    "question": RunnablePassthrough(),
    "context": retriever
}

# パターンB: assign（途中でキーを追加したい時）
(lambda x: {"question": x})
| RunnablePassthrough.assign(context=retriever)
```

**どちらも結果は同じ:** `{"question": "...", "context": [...]}`

| パターン | 特徴 | 使う場面 |
|---------|------|---------|
| dict `{}` | 最初からdictを定義 | シンプルなRAG |
| assign | 途中でキーを追加 | 段階的にキーを増やす時 |

---

### まとめ図解

```
┌─────────────────────────────────────────────────────────────┐
│                  RunnablePassthrough 早見表                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  RunnablePassthrough()                                      │
│  ─────────────────────                                      │
│  入力 → そのまま → 出力                                      │
│  "hello" → "hello"                                          │
│                                                             │
│  RunnablePassthrough.assign(key=処理)                        │
│  ─────────────────────────────────────                       │
│  入力dict → そのまま通す + 新しいキー追加 → 出力dict          │
│  {"a": 1} → {"a": 1, "key": 処理結果}                        │
│                                                             │
│  dict {} パターン                                            │
│  ────────────────                                            │
│  入力 → 各キーに処理を割り当て → 出力dict                     │
│  "hello" → {"key1": そのまま, "key2": 処理結果}              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

| 機能 | 入力を保持？ | 出力 |
|------|------------|------|
| `RunnablePassthrough()` | そのまま返す | 入力と同じ |
| `RunnablePassthrough.assign` | **保持する** | 元 + 追加 |
| `RunnableParallel` / dict | 使わない | 新しく作る |

</div>

<!-- ==================== RAGタブ ==================== -->
<div id="rag" class="tab-content">

## 9. RAG（検索拡張生成）

> **このセクションの主要関数:** `VertexAISearchRetriever` / `lambda x: x`

### RAGとは？

**問題:** LLMは学習データにない情報を答えられない

```
ユーザー: 「うちの会社の就業規則は？」
LLM: 「わかりません...」  ← 学習データにない
```

**解決策:** 先に検索して、結果をLLMに渡す

```
検索 → 関連データ取得 → LLMに渡す → 回答生成
 ↓          ↓              ↓           ↓
「就業規則」  就業規則.pdf   「この情報を元に」 「9時出社です」
```

### なぜ全データをLLMに渡さないのか？

```python
# ダメな例: 全部渡す
llm.invoke(f"以下の100ファイルを元に回答して: {全データ}")
```

**問題点:**
- トークン数制限（LLMには入力上限がある）
- コストが高い（トークン数 = お金）
- 遅い（大量データの処理は時間がかかる）

**RAGの解決策:**
- 必要な部分だけ検索して渡す
- 例: 100ファイル中、関連する3ファイルだけ渡す

### RAGの基本コード

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# サンプルデータ（本番ではVector Storeに保存）
documents = {
    "りんご": "りんごは青森県が生産量日本一です。",
    "みかん": "みかんは和歌山県や愛媛県が有名です。",
}

def simple_retriever(query: str) -> str:
    """簡易検索: キーワードが含まれるドキュメントを返す"""
    results = []
    for key, value in documents.items():
        if key in query:
            results.append(value)
    return "\n".join(results) if results else "関連情報が見つかりませんでした"

# プロンプト
prompt = ChatPromptTemplate.from_messages([
    ("system", "以下の情報を元に回答してください:\n{context}"),
    ("human", "{question}")
])

# チェーン
chain = (
    {
        "context": lambda x: simple_retriever(x),  # 検索実行
        "question": lambda x: x                     # 質問はそのまま
    }
    | prompt
    | llm
    | StrOutputParser()
)

# 実行
result = chain.invoke("りんごの産地は？")
print(result)  # → 青森県が生産量日本一です
```

### Vertex AI Search を使う場合（実践）

```python
from langchain_google_community import VertexAISearchRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Vertex AI Search の Retriever を作成
retriever = VertexAISearchRetriever(
    project_id="your-project-id",
    location="global",
    data_store_id="your-data-store-id",
    max_documents=3  # 取得するドキュメント数
)

# プロンプト
prompt = ChatPromptTemplate.from_messages([
    ("system", "以下の検索結果を元に回答してください:\n{context}"),
    ("human", "{question}")
])

# チェーン
chain = (
    {
        "context": retriever,       # Vertex AI Search で検索
        "question": lambda x: x     # 質問はそのまま
    }
    | prompt
    | llm
    | StrOutputParser()
)

# 実行
result = chain.invoke("就業規則について教えて")
print(result)
```

**必要なパッケージ:**
```bash
pip install langchain-google-community
```

---

## 13. Multi-Query RAG

> **このセクションの主要関数:** `retriever.map()` / `with_structured_output`

### Multi-Query RAG とは？

1つの質問から複数の検索クエリを生成し、検索精度を上げる手法。

```
質問: "LangChainとは？"
    ↓ LLMが複数クエリ生成
["LangChainの概要", "LangChainの機能", "LangChainの使い方"]
    ↓ 各クエリで検索
結果をまとめてLLMに渡す → 回答生成
```

### 基本コード

```python
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnablePassthrough

# 複数クエリを生成するための型定義
class QueryGenerationOutput(BaseModel):
    queries: list[str] = Field(..., description="検索クエリのリスト")

# クエリ生成用プロンプト
query_generation_prompt = ChatPromptTemplate.from_messages([
    ("human", """質問に対してベクターデータベースで検索するための
適切な検索クエリを3つ生成してください。
多様な観点からアプローチするクエリを作成します。

質問: {question}""")
])

# クエリ生成チェーン
query_generation_chain = (
    query_generation_prompt
    | llm.with_structured_output(QueryGenerationOutput)
    | (lambda x: x.queries)  # オブジェクトからリストを取り出す
)

# Multi-Query RAG チェーン
multi_query_rag_chain = (
    {
        "question": RunnablePassthrough(),
        "context": query_generation_chain | retriever.map(),
    }
    | prompt
    | llm
    | StrOutputParser()
)
```

### retriever.map() とは？

リストの各要素に対してretrieverを実行する。

```
["クエリ1", "クエリ2", "クエリ3"]
    ↓ retriever.map()
[[Doc1, Doc2], [Doc3, Doc4], [Doc5, Doc6]]
  ↑クエリ1結果  ↑クエリ2結果  ↑クエリ3結果
```

**注意:** 結果は**ネストしたリスト**になる

---

## 14. RAG-Fusion（スコアリングで検索精度UP）

> **このセクションの主要関数:** `reciprocal_rank_fusion` / `retriever.map()`

### RAG-Fusion とは？

Multi-Query RAGの結果を**スコアリング**して、より関連性の高いドキュメントを選ぶ手法。

### 全体の流れ

```
【前提】ベクトルDBには事前にドキュメントが保存されている
┌─────────────────────────────────────────────┐
│ DocA: "LangChainはLLMアプリ開発フレームワーク..."  │
│ DocB: "LangChainのインストール方法は..."          │
│ DocC: "RAGとは検索拡張生成の略で..."              │
│ DocD: "Pythonの基礎文法について..."              │
│ DocE: "LCELはLangChain Expression Languageの略..." │
└─────────────────────────────────────────────┘

ステップ1: クエリ生成（LLM）
─────────────────────────
質問: "LangChainとは？"
    ↓
["LangChainの概要", "LangChainの機能", "LangChainの使い方"]

ステップ2: 各クエリでDB検索（ベクトルDB）
─────────────────────────────────────
クエリ1 → [DocA, DocE, DocB]  ← 類似度順（DBが返す）
クエリ2 → [DocE, DocA, DocC]
クエリ3 → [DocA, DocB, DocE]

※ ここまでLLMは関与しない。DBが類似度計算して返しているだけ。

ステップ3: RRFでスコアリング（数学的計算）
────────────────────────────────────
DocA: クエリ1で1位、クエリ2で2位、クエリ3で1位 → 高スコア
DocE: クエリ1で2位、クエリ2で1位、クエリ3で3位 → 中スコア
DocB: クエリ1で3位、クエリ3で2位              → 低スコア
    ↓
[DocA, DocE, DocB, ...]  ← スコア順にソート

ステップ4: LLMに渡して解答生成（LLM）
─────────────────────────────────
上位ドキュメントをcontextとしてプロンプトに渡す
    ↓
「LangChainは、LLMを使ったアプリケーション開発のための...」
```

### まとめ表

| ステップ | 処理 | 誰がやる |
|---------|------|---------|
| 1 | クエリ3つ生成 | LLM |
| 2 | 各クエリでDB検索 | ベクトルDB |
| 3 | 検索結果をスコアリング | RRF（数学的計算） |
| 4 | 解答生成 | LLM |

**LLMが動くのは最初（クエリ生成）と最後（解答生成）だけ！**

### RRF（Reciprocal Rank Fusion）とは？

**「順位の逆数」を足し合わせるスコアリング手法**

```python
スコア = 1/(k + 順位)   # k=60 が一般的
```

**例：k=60の場合**
| 順位 | スコア |
|------|--------|
| 1位  | 1/61 = 0.0164 |
| 2位  | 1/62 = 0.0161 |
| 3位  | 1/63 = 0.0159 |

**DocAのスコア計算：**
```
クエリ1で1位: 1/61 = 0.0164
クエリ2で2位: 1/62 = 0.0161
クエリ3で1位: 1/61 = 0.0164
─────────────────────────
合計: 0.0489（高い！）
```

**なぜk=60？**
- 順位の差を「なだらかに」するため
- k=0だと1位と2位の差が大きすぎる（2倍の差）
- k=60だと差が小さい（約1.01倍の差）
- 60は論文由来の経験則

### RRFの実装

```python
from langchain_core.documents import Document

def reciprocal_rank_fusion(
    results: list[list[Document]],  # 入力: [[Doc1,Doc2,...], [Doc3,Doc4,...], ...]
    k: int = 60
) -> list[Document]:                 # 出力: [Doc3, Doc1, ...]（スコア順）
    """
    RRF（Reciprocal Rank Fusion）スコアリング

    - 上位に出てくるほど高スコア
    - 複数クエリで出てくるほど高スコア
    """
    fused_scores: dict[str, float] = {}  # {"ドキュメント内容": スコア}
    doc_map: dict[str, Document] = {}    # {"ドキュメント内容": Documentオブジェクト}

    for docs in results:  # 外側: 各クエリの結果（クエリ1→クエリ2→クエリ3）
        for rank, doc in enumerate(docs):  # 内側: 各ドキュメントと順位（0,1,2,3...）
            doc_id = doc.page_content  # ドキュメントの中身をキーに

            if doc_id not in fused_scores:  # 初めて見たドキュメントなら
                fused_scores[doc_id] = 0.0  # スコア初期化
                doc_map[doc_id] = doc       # オブジェクト保存

            # RRFスコアを加算（同じドキュメントが複数回出てきたら加算される）
            fused_scores[doc_id] += 1 / (k + rank + 1)

    # スコアが高い順にソート
    sorted_docs = sorted(
        fused_scores.items(),   # [("Doc内容", 0.048), ("Doc内容", 0.032), ...]
        key=lambda x: x[1],     # タプルの2番目（スコア）でソート
        reverse=True            # 降順（高い順）
    )

    # Documentオブジェクトのリストで返す
    return [doc_map[doc_id] for doc_id, _ in sorted_docs]
```

### ループの動き（具体例）

```
入力: 3クエリ × 各4件 = 12回のスコア加算処理

results = [
    [Doc1, Doc2, Doc3, Doc4],  ← docs（外側1周目）= クエリ1の結果
    [Doc2, Doc5, Doc1, Doc6],  ← docs（外側2周目）= クエリ2の結果
    [Doc1, Doc3, Doc2, Doc7],  ← docs（外側3周目）= クエリ3の結果
]

【外側1周目】クエリ1の結果を処理
    rank=0 → Doc1 に +1/61（1位）
    rank=1 → Doc2 に +1/62（2位）
    rank=2 → Doc3 に +1/63（3位）
    rank=3 → Doc4 に +1/64（4位）

【外側2周目】クエリ2の結果を処理
    rank=0 → Doc2 に +1/61 ← 2回目！加算される
    rank=1 → Doc5 に +1/62
    rank=2 → Doc1 に +1/63 ← 2回目！
    rank=3 → Doc6 に +1/64

【外側3周目】クエリ3の結果を処理
    rank=0 → Doc1 に +1/61 ← 3回目！さらに加算
    rank=1 → Doc3 に +1/62
    rank=2 → Doc2 に +1/63 ← 3回目！
    rank=3 → Doc7 に +1/64

最終スコア:
  Doc1: 1/61 + 1/63 + 1/61 = 0.0487（3回出現、1位が2回）← 最強
  Doc2: 1/62 + 1/61 + 1/63 = 0.0484（3回出現）
  Doc3: 1/63 + 1/62 = 0.0320（2回出現）
  ...

出力: [Doc1, Doc2, Doc3, ...] ← スコア順
```

**ポイント:** 複数クエリで共通して上位に出てくる = 高スコア = 本当に関連性が高い

### RAG-Fusionチェーン

```python
# RAG-Fusionチェーン
rag_fusion_chain = (
    {
        "question": RunnablePassthrough(),
        "context": query_generation_chain | retriever.map() | reciprocal_rank_fusion,
    }
    | prompt
    | llm
    | StrOutputParser()
)
```

### Multi-Query RAG vs RAG-Fusion

```python
# Multi-Query RAG（単純に結合）
"context": query_generation_chain | retriever.map()
# → [[Doc1, Doc2], [Doc3, Doc4]] をそのまま渡す

# RAG-Fusion（スコアリング）
"context": query_generation_chain | retriever.map() | reciprocal_rank_fusion
# → [Doc3, Doc1, Doc4, ...] スコア順にソート
```

| 手法 | 処理 | メリット |
|------|------|---------|
| Multi-Query RAG | 全結果をまとめる | シンプル |
| RAG-Fusion | スコアで順位付け | 重複排除・関連性重視 |

</div>

<!-- ==================== ツールタブ ==================== -->
<div id="tools" class="tab-content">

## 8. 構造化出力（with_structured_output）

> **このセクションの主要関数:** `llm.with_structured_output()` / `BaseModel` / `Field`

LLMの出力を決まった形（Pythonオブジェクト）で取得する。

```python
from pydantic import BaseModel, Field

# 型定義
class Recipe(BaseModel):
    ingredients: list[str] = Field(description="料理の材料のリスト")
    steps: list[str] = Field(description="料理の手順のリスト")

# これだけでOK！
structured_llm = llm.with_structured_output(Recipe)
result = structured_llm.invoke("オムライスのレシピを教えて")

print(result.ingredients)  # → ['卵 3個', '鶏もも肉 100g', ...]
print(result.steps)        # → ['鶏もも肉を切る', '炒める', ...]
```

**覚えること:** `llm.with_structured_output(クラス名)` これだけ！

### with_structured_output の仕組み

実は内部で「systemプロンプト」のように型定義をLLMに伝えている。

```python
# あなたが書いたコード
structured_llm.invoke("オムライスのレシピを教えて")

# 内部でLLMが受け取るメッセージ（イメージ）
[system] 以下のJSON形式で出力してください:
         {
           "ingredients": ["材料1", "材料2"],
           "steps": ["手順1", "手順2"]
         }
[human] オムライスのレシピを教えて
```

**つまり:**
- `with_structured_output(Recipe)` の時点で型定義がLLMに伝わる
- Fieldの `description` もLLMへの指示になる

### パイプラインで使う例（実践）

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field

# 型定義
class Recipe(BaseModel):
    menu: str = Field(description="料理名")
    ingredients: list[str] = Field(description="材料リスト")
    steps: list[str] = Field(description="手順リスト")

# 1つ目のチェーン: 食材から料理名を考える
prompt1 = ChatPromptTemplate.from_template(
    "{ingredient}を使った料理名を1つだけ答えて"
)

# 2つ目のチェーン: 料理名からレシピを構造化して取得
prompt2 = ChatPromptTemplate.from_template(
    "{dish}のレシピを教えて"
)

structured_llm = llm.with_structured_output(Recipe)

# チェーンをつなげる
chain = (
    prompt1
    | llm
    | StrOutputParser()                    # → "オムライス"
    | (lambda x: {"dish": x})              # → {"dish": "オムライス"}
    | prompt2
    | structured_llm                       # → Recipe オブジェクト
)

# 実行
result = chain.invoke({"ingredient": "卵"})
print(result.menu)         # → "オムライス"
print(result.ingredients)  # → ['卵 3個', '鶏もも肉 100g', ...]
print(result.steps)        # → ['鶏もも肉を切る', '炒める', ...]
```

---

## 10. Function Calling

> **このセクションの主要関数:** `@tool` / `.bind_tools()` / `response.tool_calls`

### Function Calling とは？

**AIが「どの関数を呼ぶべきか」を判断し、引数を生成する機能**

```
ユーザー: 「東京の天気は？」
    ↓
AI: 「get_weather関数を、city="東京"で呼ぶべきだ」
    ↓
開発者: 実際に関数を実行
    ↓
結果: 「東京は晴れです」
```

**重要:** AIは「どの関数を呼ぶか」を判断するだけ。**実行は自分でやる**。

### 基本の流れ（3ステップ）

```python
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

# ステップ1: ツールを定義（docstringは必須！）
@tool
def get_weather(city: str) -> str:
    """指定した都市の天気を取得する"""  # ← これがないとエラー
    return f"{city}の天気は晴れです"

# ステップ2: LLMにツールをバインド
llm = ChatGoogleGenerativeAI(...)
llm_with_tools = llm.bind_tools([get_weather])

# ステップ3: 質問 → AIの判断を取得 → 実行
response = llm_with_tools.invoke("東京の天気は？")

if response.tool_calls:
    tool_call = response.tool_calls[0]
    print(tool_call["name"])  # → "get_weather"
    print(tool_call["args"])  # → {"city": "東京"}

    # 実際に実行
    result = get_weather.invoke(tool_call["args"])
    print(result)  # → "東京の天気は晴れです"
```

### 覚えること

| 項目 | 内容 |
|------|------|
| `@tool` | 関数をツール化するデコレータ |
| `"""docstring"""` | **必須**。AIがこれを見て判断する |
| `.bind_tools([...])` | LLMにツールを教える |
| `response.tool_calls` | AIが「呼ぶべき」と判断したツール情報 |
| `tool_call["name"]` | ツール名 |
| `tool_call["args"]` | AIが生成した引数 |

### なぜ docstring が必須？

```python
@tool
def get_weather(city: str) -> str:
    """指定した都市の天気を取得する"""  # ← AIはこれを見て判断する
    return f"{city}の天気は晴れです"
```

**AIの内部処理（イメージ）:**
```
利用可能なツール:
- get_weather: 「指定した都市の天気を取得する」 ← docstringがそのまま使われる

ユーザーの質問: 「東京の天気は？」
→ 天気に関する質問だから get_weather を使おう
→ 引数は city="東京" だな
```

docstringがないと、AIは「この関数が何をするか」がわからない。

### 複数ツールの場合

```python
@tool
def get_weather(city: str) -> str:
    """指定した都市の天気を取得する"""
    return f"{city}の天気は晴れです"

@tool
def calculate(expression: str) -> str:
    """数式を計算する"""
    return str(eval(expression))

# 複数のツールをバインド
llm_with_tools = llm.bind_tools([get_weather, calculate])

# AIが適切なツールを選ぶ
response = llm_with_tools.invoke("100 + 200 は？")
# → tool_call["name"] = "calculate"
# → tool_call["args"] = {"expression": "100 + 200"}
```

### with_structured_output との違い

| 機能 | 用途 | 特徴 |
|------|------|------|
| Function Calling | ツールを呼び出す | AIが「どの関数を呼ぶか」も判断 |
| with_structured_output | 出力形式を固定 | 必ず指定した形式で返す |

**使い分け:**
- 「天気を調べて」「計算して」→ Function Calling（ツール選択が必要）
- 「レシピを教えて」→ with_structured_output（形式を固定したいだけ）

</div>

<!-- ==================== 実践タブ ==================== -->
<div id="practice" class="tab-content">

## 11. 会話履歴（チャットボット用）

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

## 12. ストリーミング（参考程度でOK）

ChatGPTみたいに「文字がポロポロ出てくる」演出。UI演出なので後回しでOK。

「ストリーミング」というワードだけ覚えておけば大丈夫。

```python
for chunk in llm.stream("長い話をして"):
    print(chunk.content, end="", flush=True)
```

---

## 15. よくあるエラー

| エラー | 原因 | 解決 |
|--------|------|------|
| `has no attribute 'text'` | ChatPromptValueに`.text`はない | `.to_string()` を使う |
| `must have a docstring` | @toolにdocstringがない | `"""説明"""` を追加 |
| `{"a", "b"}` がエラー | セットになってる | `("a", "b")` タプルに |

---

## 16. Enumルーティング（質問の種類で振り分け）

> **このセクションの主要関数:** `Enum` / `with_structured_output` / `RunnableLambda`

### Enumルーティングとは？

ユーザーの質問を分類して、適切な処理（retriever等）に振り分ける手法。

```
質問: "Pythonのエラーについて"
    ↓ LLMが分類
Route.TECH（技術系）
    ↓
tech_retriever で検索 → 回答
```

### Step 1: Enumの定義

```python
from enum import Enum

class Route(str, Enum):
    TECH = "tech"        # 技術系の質問
    GENERAL = "general"  # 一般的な質問
```

**`(str, Enum)` の意味:**
- `Enum`: 選択肢を制限（TECH or GENERAL のみ）
- `str`: 値を文字列として扱える

```python
# 使用例
print(Route.TECH.value)      # → "tech"
print(Route.TECH == "tech")  # → True（strを継承しているので比較可能）

# int型にしたい場合
class Priority(int, Enum):
    HIGH = 1
    LOW = 2
```

### Step 2: ルート判定用の型

```python
from pydantic import BaseModel, Field

class RouteOutput(BaseModel):
    route: Route = Field(description="質問の分類")
```

LLMに `with_structured_output(RouteOutput)` で返させる。

### Step 3: 完全なコード例

```python
from enum import Enum
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

# ========== 1. Enum定義 ==========
class Route(str, Enum):
    TECH = "tech"
    GENERAL = "general"

class RouteOutput(BaseModel):
    route: Route = Field(description="質問の分類")

# ========== 2. ダミーretriever（本番はVertex AI等） ==========
tech_docs = {
    "Python": "Pythonは動的型付け言語です。",
    "LangChain": "LangChainはLLMアプリ開発フレームワークです。",
}

general_docs = {
    "天気": "東京の天気は晴れです。",
    "挨拶": "こんにちは！",
}

def tech_retriever(query: str) -> str:
    for keyword, content in tech_docs.items():
        if keyword.lower() in query.lower():
            return content
    return "技術情報が見つかりません。"

def general_retriever(query: str) -> str:
    for keyword, content in general_docs.items():
        if keyword in query:
            return content
    return "一般情報が見つかりません。"

# ========== 3. LLMとプロンプト ==========
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-001",
    project="your-project-id",
    location="us-central1"
)

route_prompt = ChatPromptTemplate.from_messages([
    ("system", """質問を以下のどちらかに分類してください:
- tech: プログラミング、技術、IT関連
- general: 天気、ニュース、日常会話など"""),
    ("human", "{question}")
])

answer_prompt = ChatPromptTemplate.from_messages([
    ("system", "以下の情報を元に回答してください。"),
    ("human", "情報: {context}\n\n質問: {question}")
])

# ========== 4. ルート判定チェーン ==========
route_chain = (
    route_prompt
    | llm.with_structured_output(RouteOutput)
    | (lambda x: x.route)  # Route.TECH or Route.GENERAL
)

# ========== 5. 分岐処理 ==========
def route_and_retrieve(input_dict):
    question = input_dict["question"]
    route = route_chain.invoke({"question": question})

    print(f"📍 ルート判定: {route.value}")

    if route == Route.TECH:
        context = tech_retriever(question)
    else:
        context = general_retriever(question)

    return {"question": question, "context": context}

# ========== 6. 最終チェーン ==========
full_chain = (
    RunnableLambda(lambda x: {"question": x})
    | RunnableLambda(route_and_retrieve)
    | answer_prompt
    | llm
    | StrOutputParser()
)

# ========== 実行 ==========
print(full_chain.invoke("Pythonについて教えて"))
# → 📍 ルート判定: tech
# → Pythonは動的型付け言語です...
```

### なぜEnumを使う？

```python
# ❌ 文字列だとタイポしても気づかない
route = "teck"  # タイポ！でもエラーにならない

# ✅ Enumだとエラーになる
route = Route.TECK  # AttributeError!
```

**LLMの出力を決まった選択肢に制限**できる。

### RunnableLambda が必要な理由

```python
# ❌ 両方とも普通の関数だとエラー
(lambda x: ...) | route_and_retrieve  # TypeError!

# ✅ RunnableLambdaでラップ
RunnableLambda(lambda x: ...) | RunnableLambda(func)
```

**ルール:** `|`の右側がRunnableなら左側は自動変換される。両方普通の関数だとダメ。

### まとめ表

| 要素 | 役割 |
|------|------|
| `Route(str, Enum)` | 選択肢を制限（tech/general のみ） |
| `RouteOutput(BaseModel)` | LLMの出力型 |
| `with_structured_output` | LLMにEnumを返させる |
| `route == Route.TECH` | 分岐条件 |
| `RunnableLambda` | 関数をパイプラインで使う |

---

## 17. Enumルーティング × RAG-Fusion（応用）

> **このセクションの主要関数:** ルーティング + RRF の組み合わせ

### 発展パターン

Enumルーティングで振り分けた後、各retrieverでRAG-Fusionを実行する。

```
質問: "Pythonのエラーについて"
    ↓
ルート判定 → TECH
    ↓
tech用に Multi-Query 生成
    ↓
複数クエリで tech_retriever 検索
    ↓
RRFでスコアリング
    ↓
回答生成
```

### コード例

```python
from langchain_core.runnables import RunnablePassthrough

# クエリ生成（16章と同じ）
class QueryGenerationOutput(BaseModel):
    queries: list[str] = Field(description="検索クエリ3つ")

query_prompt = ChatPromptTemplate.from_messages([
    ("human", "質問に対して検索クエリを3つ生成:\n{question}")
])

query_chain = (
    query_prompt
    | llm.with_structured_output(QueryGenerationOutput)
    | (lambda x: x.queries)
)

# retrieverを辞書で管理
retrievers = {
    Route.TECH: tech_vector_store.as_retriever(),
    Route.GENERAL: general_vector_store.as_retriever(),
}

def route_and_fusion(input_dict):
    """ルーティング → Multi-Query → RRF"""
    question = input_dict["question"]

    # 1. ルート判定
    route = route_chain.invoke({"question": question})
    print(f"📍 ルート: {route.value}")

    # 2. Multi-Query生成
    queries = query_chain.invoke({"question": question})
    print(f"📝 生成クエリ: {queries}")

    # 3. 選ばれたretrieverで検索
    retriever = retrievers[route]
    results = [retriever.invoke(q) for q in queries]

    # 4. RRFでスコアリング
    fused_docs = reciprocal_rank_fusion(results)

    return {
        "question": question,
        "context": fused_docs[:5]  # 上位5件
    }

# 最終チェーン
fusion_chain = (
    RunnableLambda(lambda x: {"question": x})
    | RunnableLambda(route_and_fusion)
    | answer_prompt
    | llm
    | StrOutputParser()
)
```

### 処理の流れ

```
1. 質問: "LangChainのエラー対処法"
    ↓
2. ルート判定: Route.TECH
    ↓
3. Multi-Query生成:
   ["LangChainエラー", "LangChain例外", "LangChainトラブル"]
    ↓
4. tech_retrieverで各クエリ検索:
   クエリ1 → [Doc1, Doc2, Doc3]
   クエリ2 → [Doc2, Doc4, Doc1]
   クエリ3 → [Doc1, Doc3, Doc5]
    ↓
5. RRFスコアリング:
   Doc1: 3回出現・上位 → 高スコア
   Doc2: 2回出現 → 中スコア
   ...
    ↓
6. 上位ドキュメントでLLM回答生成
```

### 本番での使い方

```python
# Vertex AI Searchの場合
from langchain_google_community import VertexAISearchRetriever

retrievers = {
    Route.TECH: VertexAISearchRetriever(
        project_id="...",
        data_store_id="tech-docs",  # 技術文書用
    ),
    Route.GENERAL: VertexAISearchRetriever(
        project_id="...",
        data_store_id="general-docs",  # 一般文書用
    ),
}
```

### まとめ

| 手法 | 処理 |
|------|------|
| Enumルーティング | 質問を分類してretrieverを選択 |
| Multi-Query | 複数の検索クエリを生成 |
| RAG-Fusion (RRF) | 結果をスコアリングして重複排除 |
| 組み合わせ | 分類 → 複数検索 → スコアリング → 回答 |

**この組み合わせで、適切なデータソースから高精度な検索結果を得られる！**

---

## 今後追加予定

- デバッグ方法
- 本番デプロイ時の注意点
- エラーハンドリングのベストプラクティス

</div>

<!-- ==================== 補足タブ ==================== -->
<div id="reference" class="tab-content">

# 補足資料

ここから下は補足。必要な時に見ればOK。

---

## 補足A. Python基礎: クラス・インスタンス・デコレータ

LangChainを理解するために必要なPythonの基礎知識。

### クラスとインスタンス

```python
# クラス = 設計図
class Dog:
    def __init__(self, name):   # 初期化（自動で呼ばれる）
        self.name = name        # self = このインスタンス自体

    def bark(self):             # メソッド（手動で呼ぶ）
        return f"{self.name}がワン！"

# インスタンス = 設計図から作った実体
dog1 = Dog("ポチ")   # → __init__(self=dog1, name="ポチ") が自動実行
dog2 = Dog("タロウ")

dog1.bark()  # → "ポチがワン！"（self = dog1）
dog2.bark()  # → "タロウがワン！"（self = dog2）
```

### selfの理解（重要！）

```python
# selfは「ポチ」ではなく「dog1」
dog1 = Dog("ポチ")

# dog1.bark() が呼ばれると
#   → bark(self=dog1) として実行される
#   → self.name は dog1.name = "ポチ"

# イメージ
# dog1 = 箱（インスタンス）
# "ポチ" = 箱の中身（値）
# self = 箱自体を指す
```

### __init__ の理解

```python
# __init__ = 定義は書くが、呼び出しは書かない
class Dog:
    def __init__(self, name):  # ← 定義は書く
        self.name = name

dog1 = Dog("ポチ")  # ← 呼び出しは書かない（Pythonが自動で呼ぶ）
```

**よくある疑問:**
- Q: `__init__` は「自動で呼ばれる」のに、なぜ書くの？
- A: 「何をするか」は自分で決める必要があるから。Pythonが呼ぶタイミングは決まっているが、処理内容は自分で書く

### __init__ がないクラス

```python
# データを持たない場合は __init__ 不要
class Calculator:
    def add(self, a, b):
        return a + b

calc = Calculator()  # 何も渡さなくてOK
calc.add(1, 2)  # → 3
```

### @（デコレータ）

```python
# 関数を「ラップ」して追加機能を付ける構文

# LangChainでよく使うデコレータ
@tool   # 関数をLLMのツールにする（よく使う）
@chain  # 関数をパイプライン部品にする（あまり使わない）

# 例
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """指定した都市の天気を取得する"""
    return f"{city}の天気は晴れです"

# @tool を付けると .invoke() で呼べるようになる
get_weather.invoke({"city": "東京"})  # → "東京の天気は晴れです"
```

---

## 補足A2. dict 型 vs オブジェクト型（超重要！）

LangChain でデータを扱う時、**dict** と **オブジェクト** の2種類がある。
取り出し方が違うので混乱しがち。

### 基本の違い

```python
# ========== dict 型 ==========
# 定義不要、自由に作れる
d = {"queries": ["a", "b", "c"], "count": 3}

# 取り出し方: ブラケット ["キー名"]
d["queries"]  # → ["a", "b", "c"]
d["count"]    # → 3


# ========== オブジェクト型 ==========
# クラス定義が必要（設計図を先に作る）
from pydantic import BaseModel

class QueryOutput(BaseModel):
    queries: list[str]
    count: int

obj = QueryOutput(queries=["a", "b", "c"], count=3)

# 取り出し方: ドット .属性名
obj.queries   # → ["a", "b", "c"]
obj.count     # → 3
```

### 比較表

| | dict | オブジェクト |
|--|------|-------------|
| 定義 | 不要（その場で作れる） | クラス定義が必要 |
| 構造 | 自由（何でも入れられる） | 事前に決まっている |
| 取り出し | `x["key"]` | `x.属性` |
| 型チェック | なし | あり（間違うとエラー） |
| 用途 | 一時的なデータ | 構造化された出力 |

### LangChain での使い分け

```python
# dict を使う場面: チェーン内のデータ受け渡し
chain = (
    {"question": RunnablePassthrough(), "context": retriever}
    | prompt
    | llm
)
# → {"question": "...", "context": [...]} が prompt に渡る
#   prompt 内で {question} や {context} を使う


# オブジェクトを使う場面: LLM の構造化出力
class Recipe(BaseModel):
    ingredients: list[str]
    steps: list[str]

structured_llm = llm.with_structured_output(Recipe)
result = structured_llm.invoke("カレーのレシピ")

result.ingredients  # → ["じゃがいも", "玉ねぎ", ...]
result.steps        # → ["野菜を切る", "炒める", ...]
```

### よくある間違い

```python
# ❌ dict なのにドットでアクセス
d = {"queries": ["a", "b"]}
d.queries  # AttributeError!

# ✅ dict はブラケット
d["queries"]  # → ["a", "b"]


# ❌ オブジェクトなのにブラケットでアクセス
obj = QueryOutput(queries=["a", "b"])
obj["queries"]  # TypeError!

# ✅ オブジェクトはドット
obj.queries  # → ["a", "b"]
```

### チェーンでの lambda の書き方

```python
# 前のステップの出力が dict の場合
| (lambda x: x["question"])

# 前のステップの出力がオブジェクトの場合
| (lambda x: x.queries)
```

**見分け方:**
- `with_structured_output` の後 → **オブジェクト**（ドット記法）
- `RunnableParallel` / dict パターンの後 → **dict**（ブラケット記法）

### Pydantic の __init__ 自動生成

```python
# 普通のクラス（__init__ を自分で書く）
class MyClass:
    def __init__(self, queries: list[str]):
        self.queries = queries

# Pydantic BaseModel（__init__ 不要！）
class QueryOutput(BaseModel):
    queries: list[str]  # これだけで OK

# どちらも同じように使える
obj1 = MyClass(queries=["a", "b"])
obj2 = QueryOutput(queries=["a", "b"])

obj1.queries  # → ["a", "b"]
obj2.queries  # → ["a", "b"]
```

**BaseModel の強み:**
- `__init__` を書かなくていい
- 型チェックを自動でやってくれる
- LangChain の `with_structured_output` と相性が良い

---

## 補足B. Vector Store と Embedding（本番RAG）

### 簡易検索の限界

```python
# キーワード検索の問題
query = "果物の産地"
if "りんご" in query:  # ← マッチしない！
    return りんごの情報
```

「果物」と「りんご」は関連があるのに、キーワードが違うとヒットしない。

### Embedding（埋め込み）とは？

テキストを「数値の配列（ベクトル）」に変換する技術。

```python
# イメージ
"りんご" → [0.1, 0.8, 0.3, ...]  # 果物っぽい数値
"みかん" → [0.2, 0.7, 0.4, ...]  # 果物っぽい数値（似てる！）
"車"     → [0.9, 0.1, 0.2, ...]  # 全然違う数値
```

**ポイント:** 意味が近い言葉は、数値も近くなる

### Vector Store とは？

Embeddingしたデータを保存・検索するデータベース。

```
テキスト → Embedding → Vector Store に保存
     ↓
検索時: クエリも Embedding → 似たベクトルを検索
```

### Vertex AI Search vs LangChain の違い

| 方法 | チャンク分割 | Embedding | 検索 |
|------|------------|-----------|------|
| Vertex AI Search | 自動 | 自動 | 自動 |
| LangChain | 自分で実装 | 自分で実装 | 自分で実装 |

**Vertex AI Search:**
- ファイルをアップロードするだけでOK
- チャンク分割・Embedding・検索まで全部やってくれる
- 簡単だが、細かい調整ができない

**LangChain:**
- 全部自分で実装する
- 面倒だが、細かい調整ができる
- チャンクサイズ、Embeddingモデルなど選べる

### 精度が悪い時の対処法

1. **元データを修正する**（最も効果的）
   - 表記ゆれを統一（「株式会社」「(株)」など）
   - 不要な情報を削除
   - 見出しや構造を整理

2. **チャンクサイズを調整する**
   - 小さすぎ: 文脈が失われる
   - 大きすぎ: 関係ない情報も含まれる

3. **Embeddingモデルを変える**
   - 日本語に強いモデルを使う

---

## 補足C. Pydantic

### なぜ Pydantic？

```python
# 普通のクラス（型チェックなし）
class Recipe:
    def __init__(self, name, calories):
        self.name = name
        self.calories = calories

recipe = Recipe("カレー", "たくさん")  # ← エラーにならない

# Pydantic（型チェックあり）
from pydantic import BaseModel

class Recipe(BaseModel):
    name: str
    calories: int

recipe = Recipe(name="カレー", calories="たくさん")  # ← エラー！
```

### BaseModel のおかげで省略できること

```python
# 普通のクラス（自分で書く）
class Recipe:
    def __init__(self, name: str, calories: int):
        self.name = name
        self.calories = calories

# Pydantic（自動生成される）
class Recipe(BaseModel):
    name: str
    calories: int
    # __init__ は自動で作られる！
```

### Field の description

```python
class Recipe(BaseModel):
    name: str = Field(description="料理名")
    calories: int = Field(description="カロリー（kcal）")
```

**description は2つの役割:**
1. 開発者向けのドキュメント
2. LLMへの指示（with_structured_output で使う）

---

## 補足D. Python文法メモ

### タプル・辞書・セット

```python
# タプル（LangChainで使う）
("system", "こんにちは")

# 辞書（これもOK）
{"role": "system", "content": "こんにちは"}

# セット（間違い！使わない）
{"system", "こんにちは"}
```

### 文字列の書き方

```python
# シングルクォート（1行）
'こんにちは'

# ダブルクォート（1行）
"こんにちは"

# 三重クォート（複数行OK）
'''
これは
複数行の
文字列です
'''

"""
ダブルでも
同じように
複数行OK
"""
```

### エスケープ文字

```python
# \n = 改行
print("1行目\n2行目")
# 出力:
# 1行目
# 2行目

# \t = タブ
print("名前\t年齢")
# 出力: 名前    年齢

# \' や \" = クォート自体を表示
print("He said \"Hello\"")
# 出力: He said "Hello"

# \\ = バックスラッシュ自体
print("C:\\Users\\name")
# 出力: C:\Users\name
```

### f-string（変数埋め込み）

```python
name = "田中"
age = 30

# f-string（推奨）
f"私は{name}です。{age}歳です。"

# 三重クォート + f-string（複数行で変数埋め込み）
f"""
名前: {name}
年齢: {age}
"""
```

### リスト内包表記（for の短縮形）

```python
# 普通の for（4行）
results = []
for word in ["果物", "フルーツ", "産地"]:
    results.append(word in query)

# リスト内包表記（1行）
results = [word in query for word in ["果物", "フルーツ", "産地"]]
```

### 辞書のループ

```python
documents = {
    "りんご": "りんごは青森県が...",
    "みかん": "みかんは和歌山県が...",
}

# .items() で「キーと値のペア」を取り出せる
for key, value in documents.items():
    print(f"キー: {key}, 値: {value}")

# 変数名は自由（A, B でもOK）
for A, B in documents.items():
    print(A, B)
```

### in 演算子

```python
query = "りんごの産地は？"

"りんご" in query  # → True（含まれてる）
"みかん" in query  # → False（含まれてない）
```

SQLで言うと `WHERE query LIKE '%りんご%'` と同じ意味。

</div>
</div>

<!-- ==================== LangGraphタブ ==================== -->
<div id="langgraph" class="tab-content">

## LangGraph 広告分析チャットボット 完全学習ガイド

LangChain学習済みの方向けに、LangGraphの概念から実装まで段階的に解説します。

---

## Part 1: LangGraphとは何か

### LangChainの限界

LangChainのLCEL（LangChain Expression Language）は直線的な処理に強いです：

```python
# LCEL: パイプラインで繋ぐ
chain = prompt | llm | output_parser
result = chain.invoke({"question": "..."})
```

しかし、**条件分岐**や**複数経路の合流**が必要な場合、LCELだけでは辛くなります。

```
                    ユーザーの質問
                          |
                          v
                    +----------+
                    | 意図判定  |
                    +----------+
                          |
        +---------+-------+-------+---------+
        |         |               |         |
        v         v               v         v
   +--------+ +--------+     +--------+ +--------+
   |データ  | |比較    |     |一般    | |確認    |
   |取得    | |分析    |     |回答    | |質問    |
   +--------+ +--------+     +--------+ +--------+
        |         |               |         |
        +---------+-------+-------+---------+
                          |
                          v
                    +----------+
                    | 回答生成  |
                    +----------+
```

このような複雑なフローをLCELで書くのは大変です。

### LangGraphの位置づけ

```
+------------------------------------------------------------------+
|                   LangChain エコシステム                          |
+------------------------------------------------------------------+
|                                                                  |
|  +------------------+  +------------------+  +------------------+ |
|  |    LangChain     |  |    LangGraph     |  |    LangSmith     | |
|  |     (部品)       |  |   (組み立て)     |  |     (監視)       | |
|  +------------------+  +------------------+  +------------------+ |
|  |                  |  |                  |  |                  | |
|  |  - LLM          |  |  - State         |  |  - トレース      | |
|  |  - Prompt       |  |  - Node          |  |  - 評価          | |
|  |  - Chain        |  |  - Edge          |  |  - デバッグ      | |
|  |  - Tool         |  |  - Graph         |  |                  | |
|  |                  |  |                  |  |                  | |
|  +------------------+  +------------------+  +------------------+ |
|                                                                  |
+------------------------------------------------------------------+
```

| ツール | 役割 | 例え |
|--------|------|------|
| LangChain | 部品（LLM、プロンプト、ツール等） | レゴブロック |
| LangGraph | 部品を組み立てるフレームワーク | 設計図 |
| LangSmith | 動作を監視・デバッグするツール | 検査機器 |

### LangGraphの3つの基本概念

| 概念 | 説明 | 役割 |
|------|------|------|
| **State** | ノード間で共有するデータの入れ物 | 辞書のようなもの |
| **Node** | 処理の単位（関数） | Stateを受け取り、更新して返す |
| **Edge** | ノード間の接続（矢印） | 条件分岐も可能 |

---

## Part 2: 最小構成で理解する

### 2-1. 最もシンプルなLangGraphの例

まず、**2ノードだけ**の最小構成を見てみましょう。

```python
# === 最小構成のLangGraph ===

from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# --- Step 1: Stateを定義 ---
# ノード間で共有するデータ構造
class SimpleState(TypedDict):
    message: str      # 入力メッセージ
    result: str       # 処理結果

# --- Step 2: Nodeを定義 ---
# 関数として実装。Stateを受け取り、更新内容を返す

def process_node(state: SimpleState) -> dict:
    """メッセージを処理するノード"""
    msg = state["message"]
    processed = f"処理済み: {msg}"
    return {"result": processed}  # resultを更新

def output_node(state: SimpleState) -> dict:
    """結果を出力するノード"""
    print(f"最終結果: {state['result']}")
    return {}  # 更新なし

# --- Step 3: Graphを構築 ---
workflow = StateGraph(SimpleState)

# ノードを追加
workflow.add_node("process", process_node)
workflow.add_node("output", output_node)

# エッジを追加（流れを定義）
workflow.add_edge(START, "process")    # 開始 → process
workflow.add_edge("process", "output") # process → output
workflow.add_edge("output", END)       # output → 終了

# グラフをコンパイル
graph = workflow.compile()

# --- Step 4: 実行 ---
initial_state = {"message": "こんにちは", "result": ""}
final_state = graph.invoke(initial_state)

print(final_state)
# {'message': 'こんにちは', 'result': '処理済み: こんにちは'}
```

#### 実行の流れを図解

```
+------------------------------------------+
|             initial_state                |
|  message: "こんにちは"                    |
|  result: ""                              |
+------------------------------------------+
                    |
                    v
              +-----------+
              |   START   |
              +-----------+
                    |
                    v
+------------------------------------------+
|           process_node                   |
+------------------------------------------+
|  入力: state                             |
|    - message: "こんにちは"               |
|    - result: ""                          |
|                                          |
|  処理: resultを更新                      |
|                                          |
|  出力: {"result": "処理済み: こんにちは"} |
+------------------------------------------+
                    |
                    | state が更新される
                    v
+------------------------------------------+
|           output_node                    |
+------------------------------------------+
|  入力: 更新された state                  |
|    - message: "こんにちは"               |
|    - result: "処理済み: こんにちは"       |
|                                          |
|  処理: print で出力                      |
|                                          |
|  出力: {} (更新なし)                     |
+------------------------------------------+
                    |
                    v
              +-----------+
              |    END    |
              +-----------+
                    |
                    v
+------------------------------------------+
|              final_state                 |
|  message: "こんにちは"                    |
|  result: "処理済み: こんにちは"           |
+------------------------------------------+
```

#### 重要ポイント

```python
# Nodeの戻り値は「部分更新」
def process_node(state: SimpleState) -> dict:
    return {"result": processed}  # resultだけ更新
    # messageは自動的に引き継がれる

# 全部返す必要はない！
# NG: return {"message": state["message"], "result": processed}
# OK: return {"result": processed}
```

---

### 2-2. 条件分岐を追加する

次に、**条件によって処理を分ける**例を見てみましょう。

```python
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

# --- State ---
class ChatState(TypedDict):
    message: str
    intent: str       # 意図（追加）
    response: str

# --- Nodes ---
def classifier_node(state: ChatState) -> dict:
    """メッセージの意図を分類"""
    msg = state["message"]

    # シンプルな分類ロジック
    if "天気" in msg:
        intent = "weather"
    elif "時間" in msg:
        intent = "time"
    else:
        intent = "general"

    return {"intent": intent}

def weather_node(state: ChatState) -> dict:
    """天気の回答"""
    return {"response": "今日は晴れです"}

def time_node(state: ChatState) -> dict:
    """時間の回答"""
    return {"response": "現在15時です"}

def general_node(state: ChatState) -> dict:
    """一般的な回答"""
    return {"response": "すみません、よくわかりません"}

# --- 条件分岐の関数 ---
def route_by_intent(state: ChatState) -> Literal["weather", "time", "general"]:
    """intentに基づいて次のノードを決定"""
    intent = state["intent"]
    if intent == "weather":
        return "weather"
    elif intent == "time":
        return "time"
    else:
        return "general"

# --- Graph構築 ---
workflow = StateGraph(ChatState)

# ノード追加
workflow.add_node("classifier", classifier_node)
workflow.add_node("weather", weather_node)
workflow.add_node("time", time_node)
workflow.add_node("general", general_node)

# エッジ追加
workflow.add_edge(START, "classifier")

# 条件分岐エッジ
workflow.add_conditional_edges(
    "classifier",        # 分岐元のノード
    route_by_intent,     # 条件関数
    {                    # 戻り値 → 行き先ノード
        "weather": "weather",
        "time": "time",
        "general": "general",
    }
)

# 各ノード → END
workflow.add_edge("weather", END)
workflow.add_edge("time", END)
workflow.add_edge("general", END)

graph = workflow.compile()

# --- 実行 ---
result1 = graph.invoke({"message": "今日の天気は？", "intent": "", "response": ""})
print(result1["response"])  # → "今日は晴れです"

result2 = graph.invoke({"message": "今何時？", "intent": "", "response": ""})
print(result2["response"])  # → "現在15時です"
```

#### 条件分岐の図解

```
              +-----------+
              |   START   |
              +-----------+
                    |
                    v
          +------------------+
          | classifier_node  |
          |   意図を分類     |
          +------------------+
                    |
                    v
          +------------------+
          | route_by_intent  |
          |    (条件関数)    |
          +------------------+
                    |
      +-------------+-------------+
      |             |             |
      | weather     | time        | その他
      v             v             v
+-----------+ +-----------+ +-----------+
|  weather  | |   time    | |  general  |
|   _node   | |   _node   | |   _node   |
+-----------+ +-----------+ +-----------+
      |             |             |
      +-------------+-------------+
                    |
                    v
              +-----------+
              |    END    |
              +-----------+
```

---

## Part 3: 段階的に機能を追加する

### 3-1. 複数経路の合流

条件分岐の後、**1つのノードに合流**させるパターン：

```python
# 条件分岐後、全て responder に合流
workflow.add_edge("weather", "responder")
workflow.add_edge("time", "responder")
workflow.add_edge("general", "responder")
workflow.add_edge("responder", END)
```

```
          +------------------+
          |    classifier    |
          +------------------+
                    |
          +------------------+
          |     条件分岐     |
          +------------------+
                    |
      +-------------+-------------+
      |             |             |
      v             v             v
+-----------+ +-----------+ +-----------+
|  weather  | |   time    | |  general  |
+-----------+ +-----------+ +-----------+
      |             |             |
      +-------------+-------------+
                    |
                    v
          +------------------+
          |    responder     |
          +------------------+
                    |
                    v
              +-----------+
              |    END    |
              +-----------+
```

### 3-2. Stateの自動マージ（Annotated + reducer）

会話履歴のように「追加していきたい」データがある場合：

```python
from typing import TypedDict, Annotated, List
from operator import add

class ChatState(TypedDict):
    message: str
    response: str
    # ここがポイント！
    history: Annotated[List[str], add]  # addで自動マージ
```

#### reducerの動作

| 種類 | 挙動 | 例 |
|------|------|-----|
| reducer なし | 上書き | `state["response"] = "新"` → 古い値は消える |
| reducer あり | マージ | `state["history"] = ["新"]` → 既存 + 新 |

#### 実際の動き

```python
# Node A が返す
return {"history": ["A処理完了"]}
# state["history"] = [] + ["A処理完了"] = ["A処理完了"]

# Node B が返す
return {"history": ["B処理完了"]}
# state["history"] = ["A処理完了"] + ["B処理完了"] = ["A処理完了", "B処理完了"]
```

#### カスタムreducer

このプロジェクトでは、履歴を**直近15件に制限**しています：

```python
# app/agents/state.py

def merge_history(current: List, new: List) -> List:
    """会話履歴をマージし、直近15件に制限"""
    merged = (current or []) + (new or [])
    return merged[-15:]  # 直近15件のみ

class ChatState(TypedDict):
    history: Annotated[List[Dict], merge_history]  # カスタムreducer
```

---

## Part 4: Pythonファイル間のやり取りを理解する

LangGraphの前に、Pythonの**モジュールシステム**を理解しましょう。

### 4-1. ファイル構成のおさらい

```
広告分析AI/
├── main.py                 # エントリーポイント
└── app/                    # パッケージ（ディレクトリ）
    ├── __init__.py         # パッケージの目印
    ├── config.py           # 設定
    ├── agents/             # サブパッケージ
    │   ├── __init__.py
    │   ├── state.py
    │   ├── nodes.py
    │   └── workflow.py
    └── tools/              # サブパッケージ
        ├── __init__.py
        └── bigquery.py
```

### 4-2. `__init__.py` の役割

`__init__.py` があるディレクトリは**パッケージ**として認識されます。

```python
# app/__init__.py が存在する
# → "app" をパッケージとしてimportできる

import app  # OK
```

#### `__init__.py` で公開APIを定義

```python
# app/agents/__init__.py

from .workflow import run_chatbot  # workflowからインポートして再公開

# これにより、外部から簡潔にアクセスできる
# from app.agents import run_chatbot
```

### 4-3. import の種類

#### 絶対インポート

```python
# main.py から（ルートから見たパス）
from app.agents.workflow import run_chatbot
from app.config import get_settings
```

#### 相対インポート

```python
# app/agents/workflow.py から（自分の位置から見たパス）
from .state import ChatState          # 同じディレクトリ
from .nodes import router_node        # 同じディレクトリ
from ..config import get_settings     # 1つ上のディレクトリ
from ..tools.bigquery import execute_query  # 1つ上 → tools
```

#### 相対インポートの記号

| 記号 | 意味 | 例 |
|------|------|-----|
| `.` | 同じディレクトリ | `from .state import ChatState` |
| `..` | 1つ上のディレクトリ | `from ..config import get_settings` |
| `...` | 2つ上のディレクトリ | （あまり使わない） |

### 4-4. 実際のファイル間の関係を図解

```
+------------------------------------------------------------------+
|                           main.py                                |
|  from app.agents import run_chatbot                              |
|  from app.config import get_settings                             |
+------------------------------------------------------------------+
          |                                    |
          | import                             | import
          v                                    v
+-------------------------+          +------------------------+
| app/agents/__init__.py  |          |     app/config.py      |
| from .workflow import   |          | class Settings         |
|        run_chatbot      |          | def get_settings()     |
+-------------------------+          +------------------------+
          |                                    ^
          | import                             |
          v                                    |
+-------------------------+                    |
| app/agents/workflow.py  |                    |
| from .state import      |                    |
|        ChatState        |---+                |
| from .nodes import      |   |                |
|        router_node      |-+ |                |
| def run_chatbot(...)    | | |                |
+-------------------------+ | |                |
                            | |                |
          +-----------------+ |                |
          |                   |                |
          v                   v                |
+------------------+  +------------------+     |
| app/agents/      |  | app/agents/      |     |
| state.py         |  | nodes.py         |     |
+------------------+  +------------------+     |
| class ChatState  |  | from ..config    |-----+
|   (TypedDict)    |  |   import ...     |
+------------------+  | from ..tools     |--+
                      |   .bigquery      |  |
                      |   import ...     |  |
                      | def router_node  |  |
                      +------------------+  |
                                            |
                                            v
                      +------------------------+
                      | app/tools/bigquery.py  |
                      | def execute_query()    |
                      | def build_agg_query()  |
                      +------------------------+
```

### 4-5. 具体的なコードで追ってみる

#### Step 1: main.py が呼ばれる

```python
# main.py
from app.agents import run_chatbot  # ← ここから追跡

@functions_framework.http
def chat(request):
    result = run_chatbot(message, advertiser_id, history)
    return make_response(result)
```

#### Step 2: app/agents/__init__.py を見る

```python
# app/agents/__init__.py
from .workflow import run_chatbot  # workflow.py から持ってきて公開
```

**なぜ `__init__.py` で再公開するのか？**

```python
# __init__.py がないと...
from app.agents.workflow import run_chatbot  # 長い

# __init__.py で再公開すると...
from app.agents import run_chatbot  # 短い！
```

#### Step 3: app/agents/workflow.py を見る

```python
# app/agents/workflow.py

from .state import ChatState  # 同じディレクトリの state.py
from .nodes import (          # 同じディレクトリの nodes.py
    router_node,
    clarification_node,
    planner_node,
    executor_node,
    responder_node
)

def create_chatbot_graph() -> StateGraph:
    workflow = StateGraph(ChatState)  # state.py の ChatState を使用
    workflow.add_node("router", router_node)  # nodes.py の関数を使用
    ...

def run_chatbot(message, advertiser_id, history):
    graph = get_compiled_graph()
    initial_state: ChatState = {...}  # state.py の型を使用
    final_state = graph.invoke(initial_state)
    return {...}
```

#### Step 4: app/agents/nodes.py を見る

```python
# app/agents/nodes.py

from ..config import get_settings  # 1つ上(app/)の config.py
from ..tools.bigquery import execute_query, build_aggregation_query  # 1つ上 → tools/
from .state import ChatState  # 同じディレクトリの state.py

def router_node(state: ChatState) -> dict:
    settings = get_settings()  # config.py の関数を使用
    ...

def executor_node(state: ChatState) -> dict:
    results = execute_query(sql)  # bigquery.py の関数を使用
    ...
```

### 4-6. importエラーのよくある原因

| エラー | 原因 | 解決策 |
|--------|------|--------|
| 循環インポート | 互いにインポートし合う | 依存関係を整理、関数内でインポート |
| 相対インポートのミス | ドットの数が間違っている | 正しい数に修正 |
| パッケージとして実行していない | `python file.py` で直接実行 | `python -m package.module` で実行 |

---

## Part 5: 実際のプロジェクトを読み解く

### 5-1. プロジェクト全体のフロー

```
+------------------------------------------------------------------+
|                       HTTP リクエスト                             |
|              POST /chat {message: "...", ...}                    |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                          main.py                                 |
|  @functions_framework.http                                       |
|  def chat(request):                                              |
|      result = run_chatbot(message, advertiser_id, history)       |
|      return jsonify(result)                                      |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                   app/agents/workflow.py                         |
|  def run_chatbot(message, advertiser_id, history):               |
|      graph = get_compiled_graph()                                |
|      final_state = graph.invoke(initial_state)                   |
|      return {...}                                                |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                    LangGraph ワークフロー                         |
+------------------------------------------------------------------+
|                                                                  |
|    +-------+     +--------+     +----------+     +-----------+   |
|    | START | --> | Router | --> | Planner  | --> | Executor  |   |
|    +-------+     +--------+     +----------+     +-----------+   |
|                       |               |                |         |
|                       | clarification | テーブル       |         |
|                       v               | なし           |         |
|                 +-------------+       |                |         |
|                 |Clarification|       |                |         |
|                 +-------------+       |                |         |
|                       |               |                |         |
|                       +-------+-------+----------------+         |
|                               |                                  |
|                               v                                  |
|                        +-----------+                             |
|                        | Responder |                             |
|                        +-----------+                             |
|                               |                                  |
|                               v                                  |
|                          +-------+                               |
|                          |  END  |                               |
|                          +-------+                               |
|                                                                  |
+------------------------------------------------------------------+
```

### 5-2. State定義を読む

```python
# app/agents/state.py

from typing import List, Dict, Any, Optional, TypedDict, Annotated
from operator import add

# カスタムreducer
def merge_history(current: List, new: List) -> List:
    merged = (current or []) + (new or [])
    return merged[-15:]

class ChatState(TypedDict):
    """全ノードで共有される状態"""

    # --- 入力（最初に設定、変更されない）---
    user_message: str      # ユーザーの質問
    advertiser_id: str     # 広告主ID

    # --- 会話履歴（Annotatedでreducerを指定）---
    history: Annotated[List[Dict[str, str]], merge_history]

    # --- 各ノードの出力 ---
    intent: str                          # Router → 意図分類結果
    query_plan: Optional[Dict[str, Any]] # Planner → クエリ計画
    query_results: Optional[List[Dict]]  # Executor → クエリ結果
    error: Optional[str]                 # エラー情報
    response: str                        # Responder → 最終回答

    # --- 将来用 ---
    messages: Annotated[List[Dict], add]
```

#### 各フィールドがどのノードで設定されるか

| フィールド | 設定するノード | 内容例 |
|-----------|---------------|--------|
| user_message | (初期値) | "キャンペーン別CVを..." |
| advertiser_id | (初期値) | "ckoaouv1l4skp3uulr4g" |
| history | (初期値→Responder) | 過去の会話リスト |
| intent | Router | "data_query" |
| query_plan | Planner | {tables, metrics, ...} |
| query_results | Executor | [{campaign: A, CV: 10}] |
| error | Executor | エラー時のメッセージ |
| response | Responder | "CVは以下の通りです..." |

### 5-3. 各Nodeを読む

#### Router Node（意図分類）

```python
# app/agents/nodes.py

ROUTER_PROMPT = """ユーザーのメッセージを分析し、意図に分類してください：
- data_query: データ取得が必要な質問
- comparison: 2つの期間を比較
- insight: 深い分析を求める
- general: 一般知識（データ不要）
- clarification: 曖昧で確認が必要
...
"""

def router_node(state: ChatState) -> Dict[str, Any]:
    """ユーザーの意図を分類"""

    # 会話履歴がある場合は文脈も含める
    history = state.get("history", [])
    context_message = state["user_message"]

    if history:
        # 直近の会話を整形してコンテキストに含める
        recent_context = [...]
        context_message = f"【会話履歴】\n{...}\n【現在のメッセージ】\n{state['user_message']}"

    # LLMで分類
    prompt = ROUTER_PROMPT.format(message=context_message)
    response = call_vertex_ai(prompt, temperature=0.1)
    result = parse_json_response(response)

    # intentだけを返す（部分更新）
    return {"intent": result.get("intent", "general")}
```

**ポイント**:
- LLMを使って自然言語で意図を分類
- 会話履歴も考慮して文脈を理解
- `temperature=0.1` で安定した分類

#### Planner Node（クエリ計画）

```python
# app/agents/nodes.py

PLANNER_PROMPT_TEMPLATE = """
【利用可能なテーブル】
- campaign: キャンペーンレベルのデータ
- adgroup: 広告グループレベルのデータ
- keyword: キーワードレベルのデータ

【カラム】
date, campaign_name, Imp, Clicks, Cost, CV, ...

質問: {message}
意図: {intent}

JSON形式で回答:
{{
  "tables_needed": ["campaign"],
  "metrics": ["Imp", "Clicks", "Cost", "CV"],
  "dimensions": ["campaign_name"],
  "date_range": {{"start": "...", "end": "..."}}
}}
"""

def planner_node(state: ChatState) -> Dict[str, Any]:
    """クエリ計画を作成"""

    # 一般的な質問はスキップ
    if state["intent"] == "general":
        return {"query_plan": {"needs_external_knowledge": True, "tables_needed": []}}

    # 日付コンテキストを生成
    date_ctx = get_date_context()  # today, yesterday, this_month_start等

    # LLMでクエリ計画を生成
    prompt = PLANNER_PROMPT_TEMPLATE.format(
        message=state["user_message"],
        intent=state["intent"],
        **date_ctx
    )
    response = call_vertex_ai(prompt, temperature=0.1)
    result = parse_json_response(response)

    return {"query_plan": result}
```

**ポイント**:
- LLMにテーブル構造を教え、適切なクエリ計画を生成させる
- 日付表現（「先月」「今月」等）を具体的な日付に変換

#### Executor Node（クエリ実行）

```python
# app/agents/nodes.py

def executor_node(state: ChatState) -> Dict[str, Any]:
    """BigQueryでクエリを実行"""

    plan = state.get("query_plan")

    # プランがない or テーブル不要なら何もしない
    if not plan or not plan.get("tables_needed"):
        return {"query_results": None}

    advertiser_id = state["advertiser_id"]

    try:
        # クエリを構築・実行
        for table_type in plan["tables_needed"]:
            sql = build_aggregation_query(
                advertiser_id=advertiser_id,
                table_type=table_type,
                metrics=plan.get("metrics", []),
                dimensions=plan.get("dimensions", []),
                date_range=plan.get("date_range"),
            )
            print(f"Executing: {sql[:200]}...")
            results = execute_query(sql)

        return {"query_results": results}

    except Exception as e:
        return {"query_results": None, "error": f"データ取得失敗: {str(e)}"}
```

**ポイント**:
- Plannerの計画に基づいてSQLを動的に構築
- BigQueryで実行して結果を取得
- エラー時はerrorフィールドに記録

#### Responder Node（回答生成）

```python
# app/agents/nodes.py

RESPONDER_PROMPT = """あなたは広告運用のシニアコンサルタントです。
データに基づいて具体的なアクションを提案してください。

質問: {message}
意図: {intent}
データ: {data}
外部情報: {external_info}

以下の構成で回答:
1. データサマリー
2. 原因分析
3. 具体的アクション提案
"""

def responder_node(state: ChatState) -> Dict[str, Any]:
    """最終回答を生成"""

    # 既にresponseがあれば（clarificationから）そのまま返す
    if state.get("response"):
        return {"history": [...]}

    # エラーがあればエラーメッセージを返す
    if state.get("error"):
        return {"response": f"申し訳ありません。{state['error']}", "history": [...]}

    # 回答生成
    prompt = RESPONDER_PROMPT.format(
        message=state["user_message"],
        intent=state["intent"],
        data=str(state.get("query_results")),
        external_info=get_external_context(...),  # 季節性等の外部情報
    )
    response = call_vertex_ai(prompt, temperature=0.4)

    # 回答と履歴を返す
    return {
        "response": response,
        "history": [
            {"role": "user", "content": state["user_message"]},
            {"role": "assistant", "content": response[:500]}
        ]
    }
```

**ポイント**:
- データを元に「コンサルタント」として回答
- 季節性等の外部要因も考慮
- 会話履歴を更新（Annotated + reducerで自動マージ）

### 5-4. Workflowを読む

```python
# app/agents/workflow.py

from langgraph.graph import StateGraph, START, END
from .state import ChatState
from .nodes import router_node, clarification_node, planner_node, executor_node, responder_node

def create_chatbot_graph() -> StateGraph:
    """LangGraphワークフローを構築"""

    workflow = StateGraph(ChatState)

    # === ノードを追加 ===
    workflow.add_node("router", router_node)
    workflow.add_node("clarification", clarification_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("responder", responder_node)

    # === エッジを追加 ===

    # START → Router
    workflow.add_edge(START, "router")

    # Router → Clarification or Planner（条件分岐）
    def route_after_router(state: ChatState) -> str:
        if state.get("intent") == "clarification":
            return "clarification"
        return "planner"

    workflow.add_conditional_edges(
        "router",
        route_after_router,
        {"clarification": "clarification", "planner": "planner"}
    )

    # Clarification → Responder
    workflow.add_edge("clarification", "responder")

    # Planner → Executor or Responder（条件分岐）
    def should_execute(state: ChatState) -> str:
        plan = state.get("query_plan")
        if plan and plan.get("tables_needed"):
            return "executor"
        return "responder"

    workflow.add_conditional_edges(
        "planner",
        should_execute,
        {"executor": "executor", "responder": "responder"}
    )

    # Executor → Responder
    workflow.add_edge("executor", "responder")

    # Responder → END
    workflow.add_edge("responder", END)

    return workflow


# コンパイル済みグラフをキャッシュ
_graph = None

def get_compiled_graph():
    """コンパイル済みグラフを取得（シングルトン）"""
    global _graph
    if _graph is None:
        workflow = create_chatbot_graph()
        _graph = workflow.compile()
    return _graph


def run_chatbot(message: str, advertiser_id: str, history: List = None) -> Dict:
    """チャットボットを実行"""
    graph = get_compiled_graph()

    initial_state: ChatState = {
        "user_message": message,
        "advertiser_id": advertiser_id,
        "history": history or [],
        "intent": "",
        "query_plan": None,
        "query_results": None,
        "error": None,
        "response": "",
        "messages": [],
    }

    final_state = graph.invoke(initial_state)

    return {
        "ok": True,
        "response": final_state.get("response", ""),
        "intent": final_state.get("intent", ""),
        "data": final_state.get("query_results"),
        "history": final_state.get("history", []),
    }
```

### 5-5. 全体のデータフローまとめ

```
+------------------------------------------------------------------+
|                        初期 State                                 |
+------------------------------------------------------------------+
|  user_message: "キャンペーン別のCV数を教えて"                      |
|  advertiser_id: "xxx..."                                         |
|  history: []                                                     |
|  intent: ""  (空)                                                |
|  query_plan: null                                                |
|  query_results: null                                             |
|  response: ""  (空)                                              |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                       Router Node                                |
+------------------------------------------------------------------+
|  入力: user_message                                              |
|  処理: LLMで意図を分類                                           |
|  出力: {intent: "data_query"}                                    |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                       Planner Node                               |
+------------------------------------------------------------------+
|  入力: user_message, intent                                      |
|  処理: LLMでクエリ計画を生成                                     |
|  出力: {query_plan: {tables: [...], metrics: [...], ...}}        |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                       Executor Node                              |
+------------------------------------------------------------------+
|  入力: query_plan, advertiser_id                                 |
|  処理: BigQueryでSQL実行                                         |
|  出力: {query_results: [{campaign: "A", CV: 150}, ...]}          |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                       Responder Node                             |
+------------------------------------------------------------------+
|  入力: user_message, intent, query_results                       |
|  処理: LLMで回答を生成                                           |
|  出力: {response: "...", history: [...]}                         |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                        最終 State                                 |
+------------------------------------------------------------------+
|  user_message: "キャンペーン別のCV数を教えて"                      |
|  intent: "data_query"                                            |
|  query_plan: {tables: [...], metrics: [...], ...}                |
|  query_results: [{campaign: "A", CV: 150}, ...]                  |
|  response: "キャンペーン別のCV数は以下の通りです..."               |
|  history: [{role: "user", ...}, {role: "assistant", ...}]        |
+------------------------------------------------------------------+
```

---

### 付録: よく使うパターン

#### パターン1: エラーハンドリング

```python
def some_node(state: ChatState) -> dict:
    try:
        # 処理
        result = do_something()
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}
```

#### パターン2: 条件によってスキップ

```python
def executor_node(state: ChatState) -> dict:
    # 条件を満たさなければ何もしない
    if not state.get("query_plan"):
        return {}  # 空のdictを返す = 更新なし

    # 処理を実行
    ...
```

#### パターン3: 前のノードの結果を利用

```python
def responder_node(state: ChatState) -> dict:
    # 前のノードが設定した値を参照
    intent = state["intent"]           # Routerが設定
    data = state.get("query_results")  # Executorが設定

    # それらを使って処理
    ...
```

---

## Part 6: 実際の使い方（広告分析AI）

このセクションでは、広告分析AIとしての実際の使用方法を解説します。

### 6-1. セットアップ

#### 必要な環境変数（.env）

```bash
# BigQuery（広告データ）
GCP_PROJECT_ID=your-project-id
BIGQUERY_DATASET=your_dataset_name

# Vertex AI（LLM）
VERTEX_PROJECT_ID=your-vertex-project  # 空の場合はGCP_PROJECT_IDを使用
VERTEX_LOCATION=us-central1
VERTEX_MODEL=gemini-2.0-flash-001

# API認証
API_KEY=your-api-key
```

#### ローカルで実行する方法

**方法1: VSCodeで直接実行（推奨）**

1. VSCodeで `test_chatbot.ipynb` を開く
2. 右上の「カーネルを選択」で `venv` の Python を選ぶ
3. セルを順番に実行（Shift + Enter）

**方法2: ターミナルから実行**

```bash
# 1. プロジェクトディレクトリに移動
cd /path/to/広告分析AI

# 2. 仮想環境を有効化
source venv/bin/activate

# 3. プロンプトが変わったことを確認
#    (venv) $ のように表示される

# 4. Jupyter Notebookを起動
jupyter notebook
```

#### 仮想環境とは？

```
+------------------------------------------------------------------+
|  あなたのPC                                                       |
+------------------------------------------------------------------+
|                                                                  |
|  システムのPython（グローバル）                                    |
|    - いろんなプロジェクトで共有                                    |
|    - パッケージのバージョン競合が起きやすい                        |
|                                                                  |
|  +------------------------------------------------------------+  |
|  | 広告分析AI/venv/（仮想環境）                                |  |
|  +------------------------------------------------------------+  |
|  |  - このプロジェクト専用のPython                             |  |
|  |  - requirements.txt のパッケージだけインストール            |  |
|  |  - 他のプロジェクトに影響しない                             |  |
|  +------------------------------------------------------------+  |
|                                                                  |
+------------------------------------------------------------------+
```

| コマンド | 意味 |
|----------|------|
| `source venv/bin/activate` | 仮想環境を有効化 |
| `deactivate` | 仮想環境を無効化 |
| `which python` | 今どのPythonを使っているか確認 |

### 6-2. 質問の種類と回答例

#### データ取得（data_query）

```python
chat("キャンペーン別のCV数を教えて")
chat("直近1ヶ月で広告グループ別のCTRが高いものを3つ教えて")
chat("キーワード別のコストを教えて")
```

**回答例**:
```
キャンペーン別のCV数は以下の通りです：

| キャンペーン名 | CV数 |
|---------------|------|
| ブランド検索   | 230  |
| 一般検索      | 150  |
| リマーケティング| 85  |

【分析】
ブランド検索キャンペーンが最もCV数が多く...
```

#### 期間比較（comparison）

```python
chat("先月と今月のCVを比較して")
chat("前週比でCTRの変化を教えて")
```

**回答例**:
```
先月と今月のCV比較：

| 期間  | CV数 | 前月比 |
|-------|------|--------|
| 先月  | 420  | -      |
| 今月  | 465  | +10.7% |

【原因分析】
今月はCVが10.7%増加しています。主な要因として...
```

#### 深い分析（insight）

```python
chat("CTRが高い広告グループとその理由を教えて")
chat("CPAを下げるにはどうすればいい？")
```

#### 曖昧な質問（clarification）

```python
chat("調子はどう？")
```

**回答例**:
```
どの指標で評価しますか？
例えば、CVR（成約率）、CPA（獲得単価）、CV数（成約数）など。
```

### 6-3. 会話の継続

会話履歴は自動的に保持されます（直近15件）。

```python
chat("キャンペーン別のCVを教えて")
chat("その中でCPAが低いのは？")
chat("そのキャンペーンの予算を増やすべき？")

# 会話をリセットしたい場合
chat("新しい質問", reset=True)
# または
reset_chat()
```

### 6-4. デバッグモード

```python
chat("キャンペーン別のCVを教えて", show_debug=True)
```

**出力例**:
```
📝 質問: キャンペーン別のCVを教えて
📚 会話履歴: 0件
⏳ 処理中...

🏷️ Intent: data_query
------------------------------------------------------------
[Markdown形式の回答]

📚 更新後の会話履歴: 2件

📊 取得データ（先頭5件）:
  {'campaign_name': 'ブランド検索', 'CV': 230}
  {'campaign_name': '一般検索', 'CV': 150}
  ...

📜 会話履歴:
  👤 キャンペーン別のCVを教えて...
  🤖 キャンペーン別のCV数は以下の通りです...
```

### 6-5. 利用可能な指標とディメンション

#### 指標（メトリクス）

| 指標 | 説明 | 計算式 |
|------|------|--------|
| Imp | インプレッション数 | - |
| Clicks | クリック数 | - |
| Cost | 広告費用 | - |
| CV | コンバージョン数 | - |
| CTR | クリック率 | Clicks / Imp * 100 |
| CVR | コンバージョン率 | CV / Clicks * 100 |
| CPC | クリック単価 | Cost / Clicks |
| CPA | 獲得単価 | Cost / CV |
| ROAS | 広告費用対効果 | Value / Cost * 100 |

#### ディメンション（粒度）

| 粒度 | テーブル | 例 |
|------|----------|-----|
| キャンペーン別 | campaign | 「キャンペーン別のCVを教えて」 |
| 広告グループ別 | adgroup | 「広告グループ別のCTRを教えて」 |
| キーワード別 | keyword | 「キーワード別のコストを教えて」 |
| 媒体別 | campaign | 「媒体別のCPAを教えて」 |
| デバイス別 | campaign | 「デバイス別のCVRを教えて」 |

#### 期間指定

| 表現 | 解釈 |
|------|------|
| 今月 | 今月1日〜今日 |
| 先月 | 先月1日〜先月末日 |
| 今週 | 今週月曜〜今日 |
| 先週 | 先週月曜〜先週日曜 |
| 直近1ヶ月 | 過去30日間 |
| 直近 / 最近 | 全期間（明示されない場合） |

### 6-6. よくある質問例

#### パフォーマンス分析

```python
chat("全体のパフォーマンスを教えて")
chat("CPAが高いキャンペーンは？")
chat("CVRが低下している原因は？")
```

#### 予算・入札

```python
chat("予算を増やすべきキャンペーンは？")
chat("入札を調整すべきキーワードは？")
```

#### 比較分析

```python
chat("先月と今月でCVRを比較して")
chat("Google検索とYahoo!検索の効果を比較")
chat("PCとモバイルの違いを教えて")
```

#### 改善提案

```python
chat("コストを下げるにはどうすればいい？")
chat("CVを増やすための施策を教えて")
chat("このキャンペーンをどう改善すればいい？")
```

---

### 次のステップ

1. `test_chatbot.ipynb` で実際に動かしてみる
2. `nodes.py` のプロンプトを変更して挙動の変化を確認
3. 新しいノードを追加してみる（例: 結果をキャッシュするノード）
4. `workflow.py` でフローを変更してみる

Happy Learning!

</div>
</div>

<!-- タブ切り替え用JavaScript -->
<script>
function openTab(evt, tabName) {
  var i, tabcontent, tabbuttons;

  tabcontent = document.getElementsByClassName("tab-content");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].className = tabcontent[i].className.replace(" active", "");
  }

  tabbuttons = document.getElementsByClassName("tab-button");
  for (i = 0; i < tabbuttons.length; i++) {
    tabbuttons[i].className = tabbuttons[i].className.replace(" active", "");
  }

  document.getElementById(tabName).className += " active";
  evt.currentTarget.className += " active";
}
</script>

---

これで基本はOK！
