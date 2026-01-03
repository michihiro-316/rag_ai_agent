# LangChain チートシート

電車で覚える用。現場で使うものだけに絞りました。

**最終更新日:** 2026-01-02

---

<!-- タブUI用のHTML/CSS -->
<style>
.tab-container {
  margin: 20px 0;
}
.tab-buttons {
  display: flex;
  gap: 4px;
  border-bottom: 2px solid #e0e0e0;
  margin-bottom: 20px;
}
.tab-button {
  padding: 12px 24px;
  border: none;
  background: #f5f5f5;
  cursor: pointer;
  font-size: 16px;
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
  <button class="tab-button" onclick="openTab(event, 'advanced')">応用</button>
  <button class="tab-button" onclick="openTab(event, 'reference')">補足</button>
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

<!-- ==================== 応用タブ ==================== -->
<div id="advanced" class="tab-content">

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

### よくある疑問

**Q: なぜ `RunnablePassthrough()` を使う？ `lambda x: x` でいいのでは？**

A: 機能は同じ。でも `RunnablePassthrough()` は：
- LangChainの公式パターン
- デバッグで見やすい
- コードの意図が明確

**Q: assign の `context=retriever` で、retriever には何が渡されるの？**

A: **チェーンへの元の入力**（文字列）が渡される。

```python
chain.invoke("LangChainとは？")
#                ↓
# retriever.invoke("LangChainとは？") が実行される
```

**Q: 「Passthrough」って結局何をしてるの？**

A: **question を消さないようにしている**。

```python
# もし Passthrough がなかったら...
chain = retriever | prompt | llm
# → retriever の出力 [Doc1, Doc2] だけがpromptに渡る
# → {question} を埋められない！エラー！

# Passthrough.assign を使うと
chain = (lambda x: {"question": x}) | RunnablePassthrough.assign(context=retriever)
# → {"question": "...", "context": [...]} がpromptに渡る
# → {question} も {context} も埋められる！
```

---

### 実践: RAGでの使い方

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

prompt = ChatPromptTemplate.from_messages([
    ("system", "以下のドキュメントを参考に質問に答えてください。"),
    ("human", "ドキュメント:\n{context}\n\n質問: {question}")
])

# 方法1: dict パターン（シンプル）★おすすめ
chain = (
    {
        "question": RunnablePassthrough(),  # = lambda x: x
        "context": retriever
    }
    | prompt
    | llm
    | StrOutputParser()
)

# 方法2: assign パターン
chain = (
    (lambda x: {"question": x})
    | RunnablePassthrough.assign(context=retriever)
    | prompt
    | llm
    | StrOutputParser()
)

# どちらも同じ結果
chain.invoke("LangChainとは？")
```

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

---

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

**ポイント:**
- `StrOutputParser()` で文字列に変換
- `lambda x: {"dish": x}` で次のプロンプト用に辞書化
- 最後に `structured_llm` で構造化データを取得

**この方法の強み:**
- 途中で何段階パイプを通しても、**最後の出力形式を `Recipe` クラスで強制できる**
- プログラムで扱いやすい（`result.ingredients` でアクセス可能）
- LLMが文章で返す心配がない

**注意:**
- 関係ない入力を渡すと、LLMが適当に埋めてしまう
```python
# 例: レシピと関係ない質問
result = chain.invoke({"ingredient": "今日の天気"})
# → LLMが無理やり Recipe 形式で返そうとする
#    menu: "天気サラダ"（？）みたいに適当に埋まる
```
- 入力とクラス定義の整合性は自分で担保する必要がある

---

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

### Q: lambda x: x って何？なぜ必要？

**疑問:** なぜ `{"question": "りんご"}` じゃダメなの？

**答え:** チェーンは「関数」を期待しているから

```python
# これはダメ（固定値）
{"question": "りんご"}  # ← 毎回「りんご」になってしまう

# これがOK（関数）
{"question": lambda x: x}  # ← 入力をそのまま返す関数
```

**イメージ:**
```python
# lambda x: x の動き
入力: "りんごの産地は？"
  ↓
lambda x: x が受け取る
  ↓
出力: "りんごの産地は？"  # そのまま返す
```

**なぜ関数が必要？**
- チェーンは実行時に「入力を受け取って処理する」仕組み
- 固定値だと、`invoke("みかん")` しても「りんご」のまま
- 関数なら、実行時に入力を受け取って動的に処理できる

### 複数の入力がある場合

```python
# 入力が辞書の場合
chain.invoke({"question": "りんご", "category": "果物"})

# 辞書から特定のキーを取り出す
{
    "question": lambda x: x["question"],   # questionを取り出す
    "category": lambda x: x["category"]    # categoryを取り出す
}
```

### Vertex AI Search を使う場合（実践）

上の例では `simple_retriever` を自作したが、本番では Vertex AI Search を使う。

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

**ポイント:**
- `simple_retriever` の代わりに `VertexAISearchRetriever` を使うだけ
- チャンク分割・Embedding・検索は Vertex AI Search が自動でやってくれる
- `max_documents` で取得件数を調整

**必要なパッケージ:**
```bash
pip install langchain-google-community
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

### 構造化データの取得にも使える

Function Callingは「関数を実行する」だけでなく、「構造化データを取得する」用途にも使える。

```python
# 構造化されていない（ただの文字列）
"田中太郎は30歳で東京に住んでいます"

# 構造化されている（決まった形）
{"name": "田中太郎", "age": 30, "city": "東京"}
```

```python
@tool
def extract_person(name: str, age: int, city: str) -> dict:
    """人物情報を抽出する"""
    return {"name": name, "age": age, "city": city}

llm_with_tools = llm.bind_tools([extract_person])
response = llm_with_tools.invoke("田中太郎、30歳、東京在住です")

# AIが勝手に構造化してくれる
response.tool_calls[0]["args"]
# → {"name": "田中太郎", "age": 30, "city": "東京"}
```

### with_structured_output との違い

| 機能 | 用途 | 特徴 |
|------|------|------|
| Function Calling | ツールを呼び出す | AIが「どの関数を呼ぶか」も判断 |
| with_structured_output | 出力形式を固定 | 必ず指定した形式で返す |

**使い分け:**
- 「天気を調べて」「計算して」→ Function Calling（ツール選択が必要）
- 「レシピを教えて」→ with_structured_output（形式を固定したいだけ）

---

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

## 13. よくあるエラー

| エラー | 原因 | 解決 |
|--------|------|------|
| `has no attribute 'text'` | ChatPromptValueに`.text`はない | `.to_string()` を使う |
| `must have a docstring` | @toolにdocstringがない | `"""説明"""` を追加 |
| `{"a", "b"}` がエラー | セットになってる | `("a", "b")` タプルに |

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
