"""
ルーティング関数

【このファイルの役割】
条件分岐のロジックを定義します。
Stateの値を見て「次にどのNodeに進むか」を返します。

重要: ルーティング関数はStateを「読むだけ」で「更新しない」
→ 戻り値は文字列（次のNodeの名前）
"""

from typing import Literal
from state import MeetingState


def route_by_length(state: MeetingState) -> Literal["detailed", "simple"]:
    """
    【長さによるルーティング】

    Stateの`is_long`フラグを見て、次の処理を決定する

    戻り値の型ヒント Literal["detailed", "simple"] は
    「この2つの文字列しか返さない」ことを示す
    → タイポ防止＆IDEの補完が効く
    """

    # check_length_nodeで設定されたフラグを参照
    is_long = state.get("is_long", False)

    if is_long:
        # 長い会議 → 詳細な議題抽出へ
        print("[routing] 詳細モードへ分岐")
        return "detailed"
    else:
        # 短い会議 → シンプルな整形へ
        print("[routing] 簡易モードへ分岐")
        return "simple"
