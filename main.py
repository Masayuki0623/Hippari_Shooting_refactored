"""
ひっぱりシューティングゲーム - リファクタリング版
メインエントリーポイント
"""

import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.game import Game


def main():
    """メイン関数"""
    try:
        game = Game()
        game.run()
    except KeyboardInterrupt:
        print("ゲームが中断されました")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("ゲームを終了しました")


if __name__ == "__main__":
    main()