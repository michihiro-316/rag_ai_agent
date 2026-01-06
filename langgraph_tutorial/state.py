"""
State定義ファイル

【このファイルの役割】
LangGraphで処理するデータの「型」を定義します。
TypedDictを使うと、IDEの補完が効いて開発が楽になります。
"""

from typing import TypedDict, Literal, Annotated, List
from operator import add  # リストを「追加」するためのreducer


class MeetingState(TypedDict):
    """
    議事録要約AIの状態（State）

    【設計のポイント】
    1. 入力: 最初に与えるデータ（raw_text）
    2. 中間: 処理途中で埋まるデータ（summary, is_long）
    3. 出力: 最終的に取り出すデータ（topics, action_items, final_doc）
    """

    # ============================
    # 入力データ（ユーザーが与える）
    # ============================
    raw_text: str  # 会議の生テキスト（Zoom文字起こし等）

    # ============================
    # 中間データ（Nodeが埋めていく）
    # ============================
    summary: str              # 要約結果（300文字程度）
    is_long: bool             # 長い会議か？（条件分岐に使用）
    topics: List[str]        # 議題リスト（例: ["予算", "スケジュール"]）
    action_items: List[str]  # アクションアイテム（例: ["田中: 見積作成"]）

    # ============================
    # 出力データ（最終成果物）
    # ============================
    final_doc: str  # 整形された議事録（Markdown形式）

    # ============================
    # 処理ログ（デバッグ用）
    # Annotated[List, add] = 新しい値が「追加」される
    # → 各Nodeが ["[要約完了]", "[議題抽出完了]"] と追加していく
    # ============================
    logs: Annotated[List[str], add]
