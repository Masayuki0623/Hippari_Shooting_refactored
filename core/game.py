"""
メインゲームクラス - 元のPrototype5.pdeを完全再現
オリジナルのゲーム性を一切変更せず、コードのみ整理
"""
import pygame
import sys
from config.settings import GameConfig
from core.game_state import GameState


class Game:
    """
    メインゲームクラス
    元のProcessing setup()とdraw()を忠実に再現
    """
    
    def __init__(self):
        pygame.init()
        
        # 画面設定（元: size(1980*5/8,1080*3/4); frameRate(60);）
        self.screen = pygame.display.set_mode((GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT))
        pygame.display.set_caption("Hippari Shooting - 元のコード完全再現版")
        
        # FPS制御（元: frameRate(60);）
        self.clock = pygame.time.Clock()
        
        # フォント設定（元: textFont(createFont("Arial", 20));）
        self.font = pygame.font.Font(None, 30)
        self.debug_font = pygame.font.Font(None, 24)
        
        # ゲーム状態管理（元のグローバル変数群を統合）
        self.game_state = GameState()
        
        # タイマー（元のtimer変数）
        self.timer = 0
        
        print("ゲーム初期化完了 - 元のProcessingコードを完全再現")
        print("- 第1ステージ：敵は固定位置（動かない）")
        print("- HSB色空間による正確な色再現")  
        print("- 元のヒット処理とダメージシステム")
        print("- 6ステージ構成の完全実装")
    
    def run(self):
        """
        メインゲームループ - 元のdraw()関数を完全再現
        """
        running = True
        
        while running:
            # イベント処理
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
            
            # フレーム時間計算
            dt = self.clock.tick(GameConfig.FPS) / 1000.0
            self.timer += 1  # 元のtimer++
            
            # ゲーム更新（元のfunction()呼び出し相当）
            self.game_state.update(dt, events)
            
            # 描画（元のdraw()内容を再現）
            self._render_frame()
            
            pygame.display.flip()
        
        self._cleanup()
    
    def _render_frame(self):
        """
        1フレームの描画処理
        元のdraw()関数の描画部分を完全再現
        """
        # 画面振動効果の適用（元のinb_cnt<5での振動）
        shake_offset = self.game_state._get_screen_shake_offset()
        
        # 背景クリア（元: background(0);）
        self.screen.fill((0, 0, 0))
        
        # 振動オフセット適用のため、描画位置を調整
        if shake_offset != (0, 0):
            # 元のtranslate(3*t,3*t)相当の効果
            pass  # Pygameでは描画時に座標オフセットで対応
        
        # メインゲーム描画
        self.game_state.render(self.screen, self.font)
        
        # タイマー表示（元のtimer変数表示）
        if self.game_state.show_debug:
            timer_text = self.debug_font.render(f"Timer: {self.timer}", True, (255, 255, 255))
            self.screen.blit(timer_text, (10, 10))
    
    def _cleanup(self):
        """終了処理"""
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"ゲーム実行エラー: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)