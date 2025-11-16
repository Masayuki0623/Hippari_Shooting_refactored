# ひっぱりシューティングゲーム - リファクタリング版

Processingで作成されたひっぱりシューティングゲームをPythonのPygameでリファクタリングしたバージョンです。

## 改善された点

### 1. コード構造の改善
- **クラス設計**: 機能ごとにクラスを分離し、責任を明確化
- **ファイル構成**: 機能別にファイルを整理
- **グローバル変数削減**: クラスメンバ変数に移行
- **定数の集約**: 設定ファイルにまとめて管理

### 2. 保守性の向上  
- **命名規則統一**: Pythonの標準的な命名規則に統一
- **関数の分割**: 長大な関数を小さな関数に分割
- **重複コード削減**: 共通処理をユーティリティクラスに移行

### 3. 拡張性の向上
- **シーンシステム**: ゲームシーンを管理するシステムを導入
- **コンポーネント設計**: 機能を独立したクラスとして実装
- **設定の外部化**: ゲームバランス調整が容易

## ファイル構成

```
hippari_shooting_refactored/
├── main.py              # エントリーポイント
├── config/
│   └── settings.py      # ゲーム設定・定数
├── core/
│   └── game.py          # メインゲームクラス
├── entities/
│   ├── player.py        # プレイヤー関連
│   └── enemy.py         # 敵関連
├── scenes/
│   ├── scene_manager.py # シーン管理
│   └── game_scene.py    # ゲームシーン
├── utils/
│   ├── math_utils.py    # 数学計算
│   └── collision.py     # 衝突判定
└── ui/                  # UI関連（今後実装予定）
```

## インストール

1. Pygameのインストール:
```bash
pip install pygame
```

2. ゲームを実行:
```bash
python main.py
```

## 操作方法

- **マウスドラッグ**: スリングショットを引く
- **マウスリリース**: 弾を発射
- **R**: リスタート
- **F1**: デバッグモード切り替え
- **ESC**: ゲーム終了

## ゲームの流れ

1. **タイトル画面**: クリックでゲーム開始
2. **ステージ1**: 基本敵3体を倒す
3. **ステージ2**: ボス1を倒す  
4. **ステージ3**: ボス2を倒す
5. **ゲームクリア**: 全ステージクリア

## 主なクラス

### `Player`
- スリングショット機能
- プロジェクタイル発射
- HP管理
- 無敵時間

### `Enemy` & `EnemyManager`
- 複数の敵タイプ
- HP管理
- 衝突判定
- 描画パターン

### `Game` & `SceneManager`
- ゲームループ
- シーン管理
- 入力処理
- 状態管理

## 今後の拡張予定

- [ ] 弾幕システムの実装
- [ ] サウンドシステムの追加
- [ ] エフェクトシステム
- [ ] セーブ・ロード機能
- [ ] 設定画面
- [ ] より多くの敵パターン

## 元のコードからの主な変更点

### Before (Processing):
```processing
// グローバル変数が散在
float player_x, player_y;
int player_hp = 3;
boolean mousePressed;

void draw() {
  // 全てがdraw関数に集約されていた
}
```

### After (Python/Pygame):
```python
class Player:
    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.hp = GameConfig.PLAYER_MAX_HP
    
    def update(self, dt, mouse_pos, mouse_pressed):
        # 責任が明確に分離された更新処理
        pass
```
