"""
ゲーム状態管理クラス
全てのゲームオブジェクトと状態を一元管理
"""
from dataclasses import dataclass
from typing import Optional
import pygame

from config.settings import GameConfig
from entities.player import Player
from entities.enemy import EnemyManager
# ProjectileManagerは他のクラスから使用
from core.scene_manager import GameSceneManager
from core.collision_system import CollisionSystem, AudioManager
from utils.math_utils import Vector2


@dataclass
class UIButton:
    """UIボタン（元のgame_startとrestart相当）"""
    x: float
    y: float
    radius: float
    hp: int
    
    def is_clicked(self, mouse_pos: Vector2) -> bool:
        """マウスクリック判定"""
        distance = ((mouse_pos.x - self.x) ** 2 + (mouse_pos.y - self.y) ** 2) ** 0.5
        return distance <= self.radius


class GameState:
    """
    ゲーム全体の状態管理
    元のグローバル変数群を整理して管理
    """
    
    def __init__(self):
        # タイトルシーンを作成
        from scenes.game_scene import TitleScene
        self.title_scene = TitleScene()
        
        # プレイヤー
        self.player = Player(GameConfig.SCREEN_WIDTH // 2, GameConfig.SCREEN_HEIGHT // 2)
        
        # 敵管理
        self.enemy_manager = EnemyManager()
        
        # 弾丸管理はPlayerクラス内で行う
        
        # シーン管理
        self.scene_manager = GameSceneManager()
        
        # 衝突システム
        self.audio_manager = AudioManager()
        self.collision_system = CollisionSystem(self.audio_manager)
        
        # UIボタン（元のgame_startとrestart相当）
        self.start_button = UIButton(
            GameConfig.SCREEN_WIDTH // 2, 
            GameConfig.SCREEN_HEIGHT // 2, 
            100, 
            1
        )
        self.restart_button = UIButton(
            GameConfig.SCREEN_WIDTH // 2, 
            GameConfig.SCREEN_HEIGHT // 2, 
            100, 
            1
        )
        
        # 無敵カウンター（元のinb_cnt, inb_max）
        self.player_inb_cnt = 60  # 初期値
        self.player_inb_max = 60
        
        # フレームカウンター
        self.frame_counter = 0
        
        # デバッグ表示（元のstatus変数）
        self.show_debug = False
        
        # 背景システム（元のH_rnd, S_rnd, B_rnd配列）
        self.background_data = {}        # 静的背景データ
        self.base_background_data = {}   # アニメーションベースデータ（H_bg, S_bg, B_bg）
        self.current_animated_bg = {}    # 現在のアニメーション背景キャッシュ
        self.background_generated = set()
        
        # シーン固有のカウンター（元のcnt1, cnt2, cnt3）
        self.cnt1 = 0  # シーン1用カウンター
        self.cnt2 = 0  # シーン2用カウンター
        self.cnt3 = 0  # シーン3用カウンター
        
        self._generate_backgrounds()
    
    def update(self, dt: float, events: list):
        """ゲーム状態の更新"""
        self.frame_counter += 1
        
        # イベント処理
        self._handle_events(events)
        
        # マウス状態を取得
        mouse_pos = Vector2(*pygame.mouse.get_pos())
        mouse_pressed = pygame.mouse.get_pressed()[0]  # 左クリック
        keys_pressed = set()  # 必要に応じて実装
        
        # シーン固有カウンターの更新（元のcnt1++, cnt2++, cnt3++）
        current_scene = self.scene_manager.get_current_scene()
        from core.scene_manager import GameScene
        if current_scene == GameScene.STAGE_1:
            self.cnt1 += 1
        elif current_scene == GameScene.STAGE_2:
            self.cnt2 += 1
        elif current_scene == GameScene.STAGE_3:
            self.cnt3 += 1
        
        # 現在のシーンによって更新処理を分岐
        from core.scene_manager import GameScene
        
        # デバッグ：現在のシーン状態を表示
        current_scene = self.scene_manager.get_current_scene()
        is_start_active = self.scene_manager.is_scene_active(GameScene.START_SCREEN)
        if self.frame_counter % 60 == 0:  # 1秒ごとに表示
            print(f"Current scene: {current_scene}, START_SCREEN active: {is_start_active}")
        
        if self.scene_manager.is_scene_active(GameScene.START_SCREEN):
            # タイトルシーンの更新
            scene_transition = self.title_scene.update(dt, mouse_pos, mouse_pressed, keys_pressed)
            if scene_transition:
                # シーン遷移が発生した場合
                print(f"Scene transition triggered: {scene_transition}")
                self.scene_manager._transition_to_scene(GameScene.STAGE_1, self)
                return
        else:
            # ゲームプレイシーンの更新
            # 無敵カウンター更新
            if self.player_inb_cnt <= self.player_inb_max:
                self.player_inb_cnt += 1
            
            # プレイヤー更新
            self.player.update(dt, mouse_pos, mouse_pressed)
            
            # 敵更新  
            player_pos = Vector2(self.player.original_physics.position.x, 
                                self.player.original_physics.position.y)
            self.enemy_manager.update(dt, player_pos, self.scene_manager, self.cnt1)
        
        # シーン管理更新
        self.scene_manager.update(self, dt)
        
        # 弾丸更新はプレイヤー内で行われる
        
        # 敵弾の更新とプレイヤー衝突処理
        if self.enemy_manager:
            player_pos = Vector2(self.player.original_physics.position.x, 
                                self.player.original_physics.position.y)
            player_hit_by_bullet = self.enemy_manager.update_bullets(
                player_pos, self.scene_manager, 
                self.player_inb_cnt, self.player_inb_max
            )
            
            # プレイヤーが敵弾に当たった場合
            if player_hit_by_bullet:
                self.player_inb_cnt = 0  # 無敵カウンターリセット
                self.player.hp -= 1      # HP減少
                print(f"Player hit by enemy bullet! HP: {self.player.hp}")
        
        # 衝突検出
        self._handle_collisions()
        
        # ヒット表示更新
        self.collision_system.update_hit_display(dt)
    
    def _handle_events(self, events: list):
        """イベント処理"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                # デバッグ用シーン切り替え（0-4キー）
                if event.key == pygame.K_0:
                    print("Debug: Switching to START_SCREEN")
                    from core.scene_manager import GameScene
                    self.scene_manager._transition_to_scene(GameScene.START_SCREEN, self)
                elif event.key == pygame.K_1:
                    print("Debug: Switching to STAGE_1")
                    from core.scene_manager import GameScene
                    self.scene_manager._transition_to_scene(GameScene.STAGE_1, self)
                elif event.key == pygame.K_2:
                    print("Debug: Switching to STAGE_2")
                    from core.scene_manager import GameScene
                    self.scene_manager._transition_to_scene(GameScene.STAGE_2, self)
                elif event.key == pygame.K_3:
                    print("Debug: Switching to STAGE_3")
                    from core.scene_manager import GameScene
                    self.scene_manager._transition_to_scene(GameScene.STAGE_3, self)
                elif event.key == pygame.K_4:
                    print("Debug: Switching to GAME_OVER")
                    from core.scene_manager import GameScene
                    self.scene_manager._transition_to_scene(GameScene.GAME_OVER, self)
                else:
                    # デバッグ表示切り替え（元のkeyPressed）
                    self.show_debug = not self.show_debug
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = Vector2(event.pos[0], event.pos[1])
                
                # ボタンクリック判定
                if self.start_button.is_clicked(mouse_pos):
                    self.start_button.hp = -1  # ゲーム開始
                
                if self.restart_button.is_clicked(mouse_pos):
                    self.restart_button.hp = -1  # リスタート
            
            # プレイヤーの入力処理
            self.player.handle_event(event)
    
    def _handle_collisions(self):
        """衝突検出と処理"""
        # 弾と敵の衝突
        projectile_collisions = self.collision_system.check_projectile_enemy_collision(
            self.player.get_projectiles(),
            self.enemy_manager.get_active_enemy1_list(),
            self.scene_manager
        )
        
        # 衝突処理
        for enemy, projectile in projectile_collisions:
            # オリジナルのダメージシステムを再現： e.hp-=abs(velocity_b);
            if hasattr(projectile, 'get_damage'):
                damage = projectile.get_damage()
                print(f"Enemy hit! Damage: {damage}")
                enemy.take_damage(damage)
            else:
                # フォールバックダメージ
                enemy.take_damage(1)
            
            # 弾を除去（元: ball_x[i]=width+100;ball_y[i]=height+100;ball_vx[i]=0;ball_vy[i]=0;）
            if hasattr(projectile, 'ball_index') and projectile.ball_index >= 0:
                self.player.remove_projectile_by_collision(projectile.ball_index)
                print(f"Projectile {projectile.ball_index} removed from physics system")
                
            # velocity_bをリセット（元: velocity_b=0;）
            self.player.reset_velocity_b_after_hit()
            
            # 無敵カウンターリセット（元のenemy_inb[i]=0）
            if hasattr(enemy, 'inb_counter'):
                enemy.inb_counter = 0
        
        # プレイヤーと敵の衝突
        player_collision = self.collision_system.check_player_enemy_collision(
            self.player,
            self.enemy_manager.get_active_enemy1_list(),
            self.player_inb_cnt,
            self.player_inb_max
        )
        
        # プレイヤーとボスの衝突（Enemy2, Enemy3, ピクシー）
        boss_enemies = []
        if self.enemy_manager.enemy2 and self.enemy_manager.enemy2.active:
            boss_enemies.append(self.enemy_manager.enemy2)
        if self.enemy_manager.enemy3 and self.enemy_manager.enemy3.active:
            boss_enemies.append(self.enemy_manager.enemy3)
            # ピクシーも追加
            if hasattr(self.enemy_manager.enemy3, 'px1') and self.enemy_manager.enemy3.px1.hp > 0:
                boss_enemies.append(self.enemy_manager.enemy3.px1)
            if hasattr(self.enemy_manager.enemy3, 'px2') and self.enemy_manager.enemy3.px2.hp > 0:
                boss_enemies.append(self.enemy_manager.enemy3.px2)
        
        boss_collision = self.collision_system.check_player_boss_collision(
            self.player,
            boss_enemies,
            self.player_inb_cnt,
            self.player_inb_max
        )
        
        if player_collision or boss_collision:
            self.player_inb_cnt = 0  # 無敵カウンターリセット
    
    def render(self, screen: pygame.Surface, font: pygame.font.Font):
        """全体の描画"""
        from core.scene_manager import GameScene
        from utils.ui_renderer import UIRenderer
        
        # 1. 画面クリア（元: background(0);）
        screen.fill((0, 0, 0))
        
        # 2. 背景描画（格子状ブロック背景）
        ui_renderer = UIRenderer()
        current_scene = self.scene_manager.get_current_scene()
        
        if self.scene_manager.is_scene_active(GameScene.START_SCREEN):
            # タイトル画面背景（元: scene0bg()）
            ui_renderer.scene0bg(screen)
            # タイトルシーン描画
            self.title_scene.render(screen)
        elif self.scene_manager.is_scene_active(GameScene.GAME_OVER):
            # ゲームオーバー画面背景（カラフル）
            if 'scene5' in self.background_data:
                H_rnd, S_rnd, B_rnd = self.background_data['scene5']
                ui_renderer.scene_bg(screen, H_rnd, S_rnd, B_rnd)
        else:
            # ゲームプレイシーン背景
            if current_scene == GameScene.STAGE_1 and 'scene1' in self.background_data:
                # シーン1は30フレームごとに茂み更新（元: if(cnt1%30==0){ draw_bush(); }）
                base_data = self.base_background_data.get('scene1')
                if base_data and self.cnt1 % 30 == 0:
                    # 30フレームごとに茂みを更新
                    H_rnd, S_rnd, B_rnd = ui_renderer.generate_animated_background('scene1', base_data)
                    self.current_animated_bg['scene1'] = (H_rnd, S_rnd, B_rnd)
                
                # キャッシュされたアニメーション背景を使用
                if 'scene1' in self.current_animated_bg:
                    H_rnd, S_rnd, B_rnd = self.current_animated_bg['scene1']
                else:
                    H_rnd, S_rnd, B_rnd = self.background_data['scene1']
                
                ui_renderer.scene_bg(screen, H_rnd, S_rnd, B_rnd)
            elif current_scene == GameScene.STAGE_2 and 'scene2' in self.background_data:
                H_rnd, S_rnd, B_rnd = self.background_data['scene2']
                ui_renderer.scene_bg(screen, H_rnd, S_rnd, B_rnd)
            elif current_scene == GameScene.STAGE_3 and 'scene3' in self.background_data:
                H_rnd, S_rnd, B_rnd = self.background_data['scene3']
                ui_renderer.scene_bg(screen, H_rnd, S_rnd, B_rnd)
            
            # 無敵時の画面振動効果（元のtranslate処理）
            offset_x, offset_y = self._get_screen_shake_offset()
            
            # 3. ゲームオブジェクトの描画
            # 3. ゲームオブジェクトの描画
            self.player.render(screen)
            
            if self.enemy_manager:
                self.enemy_manager.render(screen)
                
            # プロジェクタイルはプレイヤー内で描画される
            # 敵弾の描画（元: bullet();）
            if self.enemy_manager:
                self.enemy_manager.render_bullets(screen, self.scene_manager)
            
            # 4. ヒットダメージ表示（元のshow_damage）
            self.collision_system.render_hit_damage(screen, font)
            
            # 5. UI描画
            self._render_ui(screen, font)
        
        # デバッグ情報表示
        if self.show_debug:
            self._render_debug_info(screen, font)
    
    def _get_screen_shake_offset(self) -> tuple:
        """画面振動オフセット計算 - 元のtranslate処理"""
        if self.player_inb_cnt < 5:  # 元: if(inb_cnt<5)
            t = 0
            if self.player_inb_cnt % 2 == 0:
                t = self.player_inb_cnt
            else:
                t = -self.player_inb_cnt
            
            return (3 * t, 3 * t)  # 元: translate(3*t,3*t)
        
        return (0, 0)
    
    def _render_ui(self, screen: pygame.Surface, font: pygame.font.Font):
        """UI要素の描画"""
        from core.scene_manager import GameScene
        from utils.ui_renderer import UIRenderer
        
        if self.scene_manager.is_scene_active(GameScene.START_SCREEN):
            self._render_start_screen(screen, font)
        elif self.scene_manager.is_scene_active(GameScene.GAME_OVER):
            self._render_game_over_screen(screen, font)
        else:
            # ゲームプレイ中のUI（元のplayer_HP()関数を再現）
            ui_renderer = UIRenderer()
            
            # シーン状態を配列として構築（元のscene[]配列を再現）
            scene = [False] * 7  # final int scene_number=7;
            current_scene = self.scene_manager.get_current_scene()
            
            # 現在のシーンに応じてscene配列を設定
            from core.scene_manager import GameScene
            if current_scene == GameScene.STAGE_1:
                scene[1] = True
            elif current_scene == GameScene.STAGE_2:
                scene[2] = True
            elif current_scene == GameScene.STAGE_3:
                scene[3] = True
            
            # オリジナルのプレイヤーHP表示（ハート形式）
            ui_renderer.player_HP(screen, self.player.hp, scene)
    
    def _render_start_screen(self, screen: pygame.Surface, font: pygame.font.Font):
        """スタート画面の描画"""
        if self.start_button.hp > 0:
            # ボタン描画
            pygame.draw.circle(screen, (255, 255, 0), 
                             (int(self.start_button.x), int(self.start_button.y)), 
                             int(self.start_button.radius))
            
            # テキスト描画
            text_surface = font.render("GAME START", True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(self.start_button.x, self.start_button.y))
            screen.blit(text_surface, text_rect)
    
    def _render_game_over_screen(self, screen: pygame.Surface, font: pygame.font.Font):
        """ゲームオーバー画面の描画"""
        # Game Overテキスト
        text_surface = font.render("Game Over", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, 
                                                 GameConfig.SCREEN_HEIGHT // 2 - 100))
        screen.blit(text_surface, text_rect)
        
        # リスタートボタン
        if self.restart_button.hp > 0:
            pygame.draw.circle(screen, (255, 0, 0), 
                             (int(self.restart_button.x), int(self.restart_button.y)), 
                             int(self.restart_button.radius))
    
    def _render_debug_info(self, screen: pygame.Surface, font: pygame.font.Font):
        """デバッグ情報の描画 - 元のstatus表示"""
        debug_lines = [
            f"Player HP: {self.player.hp}",
            f"Inb Count: {self.player_inb_cnt}",
            f"Player Pos: ({self.player.position.x:.1f}, {self.player.position.y:.1f})",
            f"Scene: {self.scene_manager.current_scene}",
            f"Frame: {self.frame_counter}"
        ]
        
        y_offset = 50
        for line in debug_lines:
            text_surface = font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (10, y_offset))
            y_offset += 25
    
    def _generate_backgrounds(self):
        """各シーンの背景を事前生成（元のgenerate_***bg関数群）"""
        from utils.ui_renderer import UIRenderer
        ui_renderer = UIRenderer()
        
        # シーン1背景生成（アニメーション用にベースも保存）
        if 'scene1' not in self.background_generated:
            bg_data = ui_renderer.generate_scene1bg()
            self.background_data['scene1'] = bg_data
            # H_bg, S_bg, B_bgとしてベース保存（アニメーション用）
            self.base_background_data['scene1'] = bg_data
            # 初期アニメーション背景を生成
            animated_bg = ui_renderer.generate_animated_background('scene1', bg_data)
            self.current_animated_bg['scene1'] = animated_bg
            self.background_generated.add('scene1')
        
        # シーン2背景生成
        if 'scene2' not in self.background_generated:
            self.background_data['scene2'] = ui_renderer.generate_scene2bg()
            self.background_generated.add('scene2')
        
        # シーン3背景生成
        if 'scene3' not in self.background_generated:
            self.background_data['scene3'] = ui_renderer.generate_bg(3)
            self.background_generated.add('scene3')
        
        # ゲームオーバー背景生成
        if 'scene5' not in self.background_generated:
            self.background_data['scene5'] = ui_renderer.generate_bg(5)
            self.background_generated.add('scene5')