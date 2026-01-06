"""
メインファイル - グラフの組み立てと実行

【このファイルの役割】
1. 各パーツ（State, Node, Routing）をimport
2. グラフを組み立てる
3. 実行する
"""

from langgraph.graph import StateGraph, START, END

# 自作モジュールをimport
from state import MeetingState
from nodes import (
    summarize_node,
    check_length_node,
    extract_topics_node,
    extract_actions_node,
    format_doc_node,
)
from routing import route_by_length


def create_meeting_graph():
    """
    議事録要約グラフを構築する

    【グラフの流れ】
    START → summarize → check_length → [分岐]
        → (長い) extract_topics → extract_actions → format_doc → END
        → (短い) format_doc → END
    """

    # ============================================
    # 1. グラフを作成（Stateの型を指定）
    #    → この型に従ってデータが流れる
    # ============================================
    workflow = StateGraph(MeetingState)

    # ============================================
    # 2. ノードを追加
    #    add_node("表示名", 関数)
    #    表示名はエッジ接続時に使う
    # ============================================
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("check_length", check_length_node)
    workflow.add_node("extract_topics", extract_topics_node)
    workflow.add_node("extract_actions", extract_actions_node)
    workflow.add_node("format_doc", format_doc_node)

    # ============================================
    # 3. エッジを追加（固定の接続）
    #    START: 処理の開始点（特殊なNode）
    #    END: 処理の終了点（特殊なNode）
    # ============================================
    workflow.add_edge(START, "summarize")        # 開始 → 要約
    workflow.add_edge("summarize", "check_length")  # 要約 → 長さチェック

    # ============================================
    # 4. 条件分岐を追加
    #    add_conditional_edges(分岐元, 条件関数, マッピング)
    # ============================================
    workflow.add_conditional_edges(
        "check_length",     # どのNodeから分岐するか
        route_by_length,    # 条件を判定する関数
        {
            # 条件関数の戻り値 → 次に進むNode
            "detailed": "extract_topics",  # 長い → 議題抽出へ
            "simple": "format_doc",       # 短い → 整形へ直行
        }
    )

    # 詳細モードの続き: 議題 → アクション → 整形
    workflow.add_edge("extract_topics", "extract_actions")
    workflow.add_edge("extract_actions", "format_doc")

    # 最後は全てENDへ
    workflow.add_edge("format_doc", END)

    # ============================================
    # 5. compile()で実行可能なグラフに変換
    # ============================================
    return workflow.compile()


if __name__ == "__main__":
    # ============================================
    # サンプル会議テキスト（長いバージョン）
    # 実際にはZoomの文字起こしや議事メモを入れる
    # ============================================
    sample_meeting = """
    【プロジェクト進捗会議】2024年1月15日

    田中: 今週の進捗を報告します。フロントエンドのUI改修は80%完了。
    残りはモバイル対応です。来週水曜までに完了予定。

    鈴木: バックエンドのAPI改修は予定より遅れています。
    認証周りで問題が発生し、解決に2日かかりました。
    来週金曜までには完了できる見込みです。

    山田: QAテストの準備は完了しています。
    来週月曜からテスト開始できます。
    テスト項目は150件、3日間で実施予定です。

    田中: 予算について確認です。追加で10万円必要になりそうです。
    理由はサーバー増強のため。

    鈴木: 承認します。経理に連絡しておきます。

    次回の会議は来週月曜10時から。
    """

    # ============================================
    # グラフを作成して実行
    # ============================================
    graph = create_meeting_graph()

    # invoke()で実行（入力はdictで渡す）
    result = graph.invoke({
        "raw_text": sample_meeting,  # 必須: 会議テキスト
        "logs": []                    # 必須: 空リストで初期化
    })

    # ============================================
    # 結果を表示
    # ============================================
    print("=" * 50)
    print("【生成された議事録】")
    print("=" * 50)
    print(result["final_doc"])

    print("\n【処理ログ】")
    for log in result["logs"]:
        print(f"  {log}")

    # ファイルに保存したい場合
    # with open("output/meeting_notes.md", "w") as f:
    #     f.write(result["final_doc"])
    # print("\n✅ output/meeting_notes.md に保存しました")
