"""
Node定義ファイル

【このファイルの役割】
各処理（要約、議題抽出など）を個別の関数として定義します。
関数は必ず「Stateを受け取り、更新する部分だけをdictで返す」形式です。
"""

from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import ChatPromptTemplate
from state import MeetingState  # Step 2で作ったStateをimport
from datetime import datetime

# ============================================
# LLMの初期化（全Nodeで共有）
# temperature=0: 出力を安定させる（毎回同じ結果）
# ============================================
llm = ChatVertexAI(
    model="gemini-1.5-flash",  # 高速・低コスト
    temperature=0              # 創造性を抑えて安定した出力
)


def summarize_node(state: MeetingState) -> dict:
    """
    【要約ノード】
    会議テキスト → 300文字程度の要約

    なぜ要約から始める？
    → 長い会議テキストをそのまま後続処理に渡すと、
      トークン数が増えてコストが上がる＆精度が下がる
    """

    # プロンプトを定義（systemとhumanの2つのメッセージ）
    prompt = ChatPromptTemplate.from_messages([
        ("system", """あなたは議事録作成のプロです。
以下の会議内容を300文字程度で要約してください。
- 重要な決定事項を優先
- 具体的な数字や期日は必ず含める
- 箇条書きではなく文章で"""),
        ("human", "{text}")  # {text}に実際のテキストが入る
    ])

    # LangChain式: prompt | llm で「チェーン」を作成
    chain = prompt | llm

    # Stateから生テキストを取り出してLLMに渡す
    result = chain.invoke({"text": state["raw_text"]})

    # 更新したいフィールドだけをdictで返す
    # → LangGraphが自動でStateにマージしてくれる
    return {
        "summary": result.content,
        "logs": ["[summarize] 要約完了"]
    }


def check_length_node(state: MeetingState) -> dict:
    """
    【長さチェックノード】
    会議テキストの長さで「詳細モード or 簡易モード」を判定

    なぜ分岐が必要？
    → 長い会議: 議題・アクション抽出をしっかり
    → 短い会議: シンプルに要約だけでOK
    """

    # 2000文字以上なら「長い会議」と判定
    text_length = len(state["raw_text"])
    is_long = text_length > 2000

    print(f"[check_length] テキスト長: {text_length}文字 → {'詳細モード' if is_long else '簡易モード'}")

    return {
        "is_long": is_long,
        "logs": [f"[check_length] {text_length}文字"]
    }


def extract_topics_node(state: MeetingState) -> dict:
    """
    【議題抽出ノード】
    要約から主要な議題を抽出（リスト形式）

    ポイント: LLMの出力を「改行区切り」にしてsplit()で分割
    → JSON形式より確実に動作する
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", """以下の会議要約から、議題を抽出してください。
- 1行に1議題
- 議題のみを出力（番号や記号なし）
- 最大5個まで"""),
        ("human", "{summary}")
    ])

    chain = prompt | llm
    result = chain.invoke({"summary": state["summary"]})

    # 改行で分割してリスト化
    topics = [
        line.strip()
        for line in result.content.split("\n")
        if line.strip()  # 空行を除外
    ]

    return {
        "topics": topics,
        "logs": [f"[topics] {len(topics)}件抽出"]
    }


def extract_actions_node(state: MeetingState) -> dict:
    """
    【アクションアイテム抽出ノード】
    「誰が」「何を」「いつまでに」を抽出
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", """以下の会議要約から、アクションアイテムを抽出してください。
形式: 担当者: タスク内容（期限があれば記載）
- 1行に1アクション
- 具体的なタスクのみ抽出"""),
        ("human", "{summary}")
    ])

    chain = prompt | llm
    result = chain.invoke({"summary": state["summary"]})

    actions = [line.strip() for line in result.content.split("\n") if line.strip()]

    return {
        "action_items": actions,
        "logs": [f"[actions] {len(actions)}件抽出"]
    }


def format_doc_node(state: MeetingState) -> dict:
    """
    【整形ノード】
    全ての情報をMarkdown形式の議事録に整形

    LLMを使わない処理: テンプレートに値を埋め込むだけ
    → コスト削減＆高速化
    """

    # 議題をMarkdownリストに変換
    topics_md = "\n".join([f"- {t}" for t in state.get("topics", [])])

    # アクションアイテムをMarkdownリストに変換
    actions_md = "\n".join([f"- [ ] {a}" for a in state.get("action_items", [])])

    # Markdown形式で議事録を生成
    doc = f"""# 議事録
**作成日時**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 要約
{state.get('summary', '(要約なし)')}

## 議題
{topics_md or '(議題なし)'}

## アクションアイテム
{actions_md or '(アクションなし)'}
"""

    return {
        "final_doc": doc,
        "logs": ["[format] 議事録生成完了"]
    }
