# LangChain チートシート

電車で覚える用。現場で使うものだけに絞りました。

---

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

---

## 7. 構造化出力（with_structured_output）

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

## 8. RAG（検索拡張生成）

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

## 9. Function Calling

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

---

## 10. 会話履歴（チャットボット用）

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

## 11. ストリーミング（参考程度でOK）

ChatGPTみたいに「文字がポロポロ出てくる」演出。UI演出なので後回しでOK。

「ストリーミング」というワードだけ覚えておけば大丈夫。

```python
for chunk in llm.stream("長い話をして"):
    print(chunk.content, end="", flush=True)
```

---

## 12. よくあるエラー

| エラー | 原因 | 解決 |
|--------|------|------|
| `has no attribute 'text'` | ChatPromptValueに`.text`はない | `.to_string()` を使う |
| `must have a docstring` | @toolにdocstringがない | `"""説明"""` を追加 |
| `{"a", "b"}` がエラー | セットになってる | `("a", "b")` タプルに |

---

# 補足資料

ここから下は補足。必要な時に見ればOK。

---

## 補足A. Vector Store と Embedding（本番RAG）

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

## 補足B. Pydantic

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

## 補足C. Python文法メモ

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

---

これで基本はOK！
