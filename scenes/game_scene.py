"""
ゲームシーンの実装
"""
import pygame
from scenes.scene_manager import Scene
from config.settings import GameConfig, SceneType, Colors
from entities.player import Player
from entities.enemy import EnemyManager
from utils.math_utils import Vector2
from utils.background_effects import BackgroundManager
from typing import Optional


class GameScene(Scene):
    """メインゲームシーン"""
    
    def __init__(self, scene_type: SceneType):
        super().__init__(scene_type)
        
        # ゲームオブジェクト
        self.player = Player(GameConfig.SCREEN_WIDTH // 2, GameConfig.SCREEN_HEIGHT // 2)
        self.enemy_manager = EnemyManager()
        self.background_manager = BackgroundManager()
        
        # ゲーム状態
        self.score = 0
        self.game_timer = 0
        
        # フォント
        try:
            self.font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 24)
        except:
            self.font = pygame.font.SysFont('arial', 36)
            self.small_font = pygame.font.SysFont('arial', 24)
    
    def enter(self):
        """シーン開始時の処理"""
        super().enter()
        
        # シーンタイプに応じた初期化
        if self.scene_type == SceneType.STAGE_1:
            self._setup_stage1()
        elif self.scene_type == SceneType.STAGE_2:
            self._setup_stage2()
        elif self.scene_type == SceneType.STAGE_3:
            self._setup_stage3()
    
    def _setup_stage1(self):
        """ステージ1のセットアップ（オリジナル通りの配置）"""
        # Enemy1を3体作成して配置
        from entities.enemy import Enemy1
        
        print(f"Setting up Stage 1 with {3} enemies")
        
        for i in range(3):
            # オリジナル通りの配置: enemy1[i].x = width/2 + (i-1) * 100
            x = GameConfig.SCREEN_WIDTH // 2 + (i - 1) * 100
            # オリジナル通りの配置: i==1なら y=200, それ以外は y=100
            if i == 1:
                y = 200  # 中央下
            else:
                y = 100  # 左上・右上
            
            # 全ての敵を同じradius=50で統一
            enemy = Enemy1(x, y, 50, 16)  # radius=50, hp=16
            enemy.active = True
            
            print(f"Enemy {i}: pos=({x}, {y}), radius={enemy.radius}, hp={enemy.hp}")
            
            # EnemyManagerの敵リストに直接追加
            self.enemy_manager.enemies.append(enemy)
            self.enemy_manager.enemy1_list.append(enemy)
        
        print(f"Total enemies created: {len(self.enemy_manager.enemies)}")
    
    def _setup_stage2(self):
        """ステージ2のセットアップ"""
        # ボス1を作成
        from entities.enemy import Enemy1
        boss = Enemy1(GameConfig.SCREEN_WIDTH // 2, GameConfig.SCREEN_HEIGHT // 4, 80)
        boss.radius = 80  # ボスサイズ
        boss.active = True
        self.enemy_manager.enemies.append(boss)
        self.enemy_manager.enemy1_list.append(boss)
    
    def _setup_stage3(self):
        """ステージ3のセットアップ"""
        # ボス2を作成
        from entities.enemy import Enemy1
        boss = Enemy1(GameConfig.SCREEN_WIDTH // 2, GameConfig.SCREEN_HEIGHT // 4, 120)
        boss.radius = 100  # 大きなボスサイズ
        boss.active = True
        self.enemy_manager.enemies.append(boss)
        self.enemy_manager.enemy1_list.append(boss)
    
    def update(self, dt: float, mouse_pos: Vector2, mouse_pressed: bool, keys_pressed: set):
        """シーンの更新処理"""
        self.game_timer += dt
        
        # 背景エフェクトの更新
        self.background_manager.update(dt)
        
        # プレイヤーの更新  
        active_enemies = self.enemy_manager.get_active_enemies()
        enemy_pos = active_enemies[0].position if active_enemies else None
        self.player.update(dt, mouse_pos, mouse_pressed, enemy_pos)
        
        # 敵の更新
        self.enemy_manager.update(dt, self.player.position)
        
        # 衝突判定
        # プロジェクタイルと敵の衝突
        projectiles = self.player.projectile_manager.get_projectiles()
        collisions = self.enemy_manager.check_collisions_with_projectiles(projectiles)
        
        # 衝突エフェクトの追加
        for enemy, projectile in collisions:
            self.background_manager.add_explosion_effect(enemy.position, 3.0)
        
        self.enemy_manager.apply_damage_from_collisions(collisions)
        self.score += len(collisions) * 100
        
        # プレイヤーと敵の衝突（簡単な距離チェック）
        for enemy in active_enemies:
            distance = self.player.position.distance_to(enemy.position)
            if distance < self.player.radius + enemy.radius:
                if self.player.take_damage():
                    pass  # ダメージ効果音などを追加可能
        
        # ゲーム終了条件のチェック
        if self.player.hp <= 0:
            # ゲームオーバー
            return SceneType.GAME_OVER
        elif len(active_enemies) == 0:
            # ステージクリア
            if self.scene_type == SceneType.STAGE_1:
                return SceneType.STAGE_2
            elif self.scene_type == SceneType.STAGE_2:
                return SceneType.STAGE_3
            elif self.scene_type == SceneType.STAGE_3:
                return SceneType.GAME_CLEAR
        
        return None
    
    def render(self, screen: pygame.Surface):
        """シーンの描画処理"""
        # カメラシェイクオフセットを取得
        camera_offset = self.background_manager.get_camera_offset()
        
        # 一時的な画面を作成（カメラシェイク用）
        if camera_offset.x != 0 or camera_offset.y != 0:
            temp_screen = pygame.Surface((GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT))
            render_target = temp_screen
        else:
            render_target = screen
        
        # 背景の描画
        self.background_manager.render(render_target)
        
        # ゲームオブジェクトの描画
        self.enemy_manager.render(render_target)
        self.player.render(render_target)
        
        # カメラシェイクがある場合、オフセットして描画
        if camera_offset.x != 0 or camera_offset.y != 0:
            screen.fill((0, 0, 0))  # 背景をクリア
            screen.blit(temp_screen, (camera_offset.x, camera_offset.y))
        
        # UIの描画（シェイクの影響を受けない）
        self._render_ui(screen)
    
    def _render_ui(self, screen: pygame.Surface):
        """UIの描画 - 元のUI.pdeの機能を再現"""
        # 半透明の背景パネル
        ui_panel = pygame.Surface((GameConfig.SCREEN_WIDTH, 80), pygame.SRCALPHA)
        ui_panel.fill((0, 0, 0, 128))  # 半透明黒
        screen.blit(ui_panel, (0, 0))
        
        # スコア
        score_text = self.font.render(f"Score: {self.score:06d}", True, Colors.YELLOW)
        screen.blit(score_text, (10, 10))
        
        # HP表示（ハート + 数値）
        self._render_hp_display(screen)
        
        # ステージ情報
        stage_name = {
            SceneType.STAGE_1: "Stage 1",
            SceneType.STAGE_2: "Boss 1", 
            SceneType.STAGE_3: "Boss 2"
        }.get(self.scene_type, "Unknown")
        
        stage_text = self.font.render(stage_name, True, Colors.CYAN)
        screen.blit(stage_text, (GameConfig.SCREEN_WIDTH - 150, 10))
        
        # 敵の残り数
        active_enemies = self.enemy_manager.get_active_enemies()
        enemy_count = len(active_enemies)
        enemy_text = self.small_font.render(f"Enemies: {enemy_count}", True, Colors.WHITE)
        screen.blit(enemy_text, (GameConfig.SCREEN_WIDTH - 150, 45))
        
        # 無敵時間の表示
        if self.player.is_invincible:
            inv_time = int(self.player.invincibility_timer)
            inv_text = self.small_font.render(f"Invincible: {inv_time}", True, Colors.GREEN)
            screen.blit(inv_text, (10, GameConfig.SCREEN_HEIGHT - 30))
        
        # デバッグ情報（オプション）
        if hasattr(self, 'debug_mode') and self.debug_mode:
            self._render_debug_info(screen)
    
    def _render_hp_display(self, screen: pygame.Surface):
        """HP表示の詳細描画"""
        hp_x = 10
        hp_y = 45
        
        # HPラベル
        hp_label = self.small_font.render("HP:", True, Colors.WHITE)
        screen.blit(hp_label, (hp_x, hp_y))
        
        # ハートアイコン
        heart_start_x = hp_x + 35
        for i in range(self.player.max_hp):
            heart_x = heart_start_x + i * 25
            if i < self.player.hp:
                # フルハート（赤）
                self._render_heart(screen, heart_x, hp_y, Colors.RED)
            else:
                # 空ハート（灰色）
                self._render_heart(screen, heart_x, hp_y, Colors.GRAY)
        
        # HP数値
        hp_text = self.small_font.render(f"{self.player.hp}/{self.player.max_hp}", True, Colors.WHITE)
        screen.blit(hp_text, (heart_start_x + self.player.max_hp * 25 + 10, hp_y))
    
    def _render_debug_info(self, screen: pygame.Surface):
        """デバッグ情報の表示"""
        debug_y = 100
        
        # プレイヤー情報
        pos_text = self.small_font.render(
            f"Player: ({int(self.player.position.x)}, {int(self.player.position.y)})", 
            True, Colors.YELLOW
        )
        screen.blit(pos_text, (10, debug_y))
        
        # 物理情報
        physics = self.player.original_physics
        debug_y += 20
        physics_text = self.small_font.render(
            f"Energy: {physics.physics.energy:.1f}, SlingCnt: {physics.sling_cnt}", 
            True, Colors.YELLOW
        )
        screen.blit(physics_text, (10, debug_y))
        
        # プロジェクタイル数
        debug_y += 20
        proj_count = len(self.player.projectile_manager.get_projectiles())
        proj_text = self.small_font.render(f"Projectiles: {proj_count}", True, Colors.YELLOW)
        screen.blit(proj_text, (10, debug_y))
    
    def _render_heart(self, screen: pygame.Surface, x: int, y: int, color: tuple = Colors.RED):
        """ハートの描画（改良版）"""
        # よりハートらしい形状
        size = 8
        
        # 左の円
        pygame.draw.circle(screen, color, (x + size//2, y + size//2), size//2)
        # 右の円  
        pygame.draw.circle(screen, color, (x + size, y + size//2), size//2)
        
        # 下の三角形
        points = [
            (x, y + size//2),
            (x + size + size//2, y + size//2),
            (x + size//2 + size//4, y + size + size//2)
        ]
        pygame.draw.polygon(screen, color, points)
    
    def handle_key_down(self, key: int):
        """キー押下処理"""
        # デバッグ用：Rキーでリスタート
        if key == pygame.K_r:
            self.enter()  # シーンを再初期化


class TitleScene(Scene):
    """タイトルシーン"""
    
    def __init__(self):
        super().__init__(SceneType.TITLE)
        # 日本語対応フォントの設定
        self._setup_japanese_fonts()
        
        # アニメーション用の変数
        self.animation_time = 0
        self.title_pulse_scale = 1.0
        self.button_glow_intensity = 0.5
        
        # プレイヤーとスタートボタン（敵として実装）
        self.player = Player(GameConfig.SCREEN_WIDTH // 2, GameConfig.SCREEN_HEIGHT - 100)
        
        # スタートボタン（シンプルな当たり判定対象として実装）
        self.start_button_pos = Vector2(GameConfig.SCREEN_WIDTH // 2, GameConfig.SCREEN_HEIGHT // 2 + 80)
        self.start_button_radius = 50
        self.start_button_hit = False
    
    def _setup_japanese_fonts(self):
        """日本語対応フォントのセットアップ"""
        # 日本語フォントの候補リスト（Windows向け）
        japanese_fonts = [
            'meiryoui',          # Meiryo UI
            'meiryo',            # Meiryo
            'msgothic',          # MS Gothic
            'msmincho',          # MS Mincho  
            'yumidkaiti',        # YuMincho
            'notosanscjk',       # Noto Sans CJK
            'hiragino sans',     # macOS
        ]
        
        # タイトル用フォント（大きいサイズ）
        self.title_font = None
        for font_name in japanese_fonts:
            try:
                self.title_font = pygame.font.SysFont(font_name, 72)
                break
            except:
                continue
        
        # フォールバック
        if self.title_font is None:
            try:
                self.title_font = pygame.font.Font(None, 72)
            except:
                self.title_font = pygame.font.SysFont('arial', 72)
        
        # 通常テキスト用フォント
        self.font = None
        for font_name in japanese_fonts:
            try:
                self.font = pygame.font.SysFont(font_name, 36)
                break
            except:
                continue
                
        # フォールバック
        if self.font is None:
            try:
                self.font = pygame.font.Font(None, 36)
            except:
                self.font = pygame.font.SysFont('arial', 36)
        
        # 小さいテキスト用フォント
        self.small_font = None
        for font_name in japanese_fonts:
            try:
                self.small_font = pygame.font.SysFont(font_name, 28)
                break
            except:
                continue
                
        if self.small_font is None:
            try:
                self.small_font = pygame.font.Font(None, 28)
            except:
                self.small_font = pygame.font.SysFont('arial', 28)
    
    def render(self, screen: pygame.Surface):
        """タイトル画面の描画"""
        # グラデーション背景の描画
        self._draw_gradient_background(screen)
        
        # 装飾的な星を描画
        self._draw_background_stars(screen)
        
        # タイトルテキスト（パルス効果付き）
        self._draw_title(screen)
        
        # サブタイトル
        subtitle_text = self.small_font.render("～ Slingshot Shooting Game ～", True, Colors.CYAN)
        subtitle_rect = subtitle_text.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, 170))
        screen.blit(subtitle_text, subtitle_rect)
        
        # 説明文（より整理された形で）
        self._draw_instructions(screen)
        
        # スタートボタンを描画（グロー効果付き）
        self._draw_start_button(screen)
        
        # プレイヤーを描画
        self.player.render(screen)
    
    def _draw_gradient_background(self, screen: pygame.Surface):
        """グラデーション背景を描画"""
        # 縦方向のグラデーション（深い青から薄い紫へ）
        for y in range(GameConfig.SCREEN_HEIGHT):
            # グラデーションの計算
            ratio = y / GameConfig.SCREEN_HEIGHT
            
            # 上部: 深い紺色 (20, 20, 80)
            # 下部: 薄い紫 (60, 40, 100)
            r = int(20 + (60 - 20) * ratio)
            g = int(20 + (40 - 20) * ratio)  
            b = int(80 + (100 - 80) * ratio)
            
            color = (r, g, b)
            pygame.draw.line(screen, color, (0, y), (GameConfig.SCREEN_WIDTH, y))
    
    def _draw_background_stars(self, screen: pygame.Surface):
        """背景の装飾的な星を描画"""
        import math
        
        # アニメーションに基づいた星の位置計算
        star_positions = [
            (100, 100), (200, 80), (300, 120), (500, 90), (600, 110),
            (150, 200), (400, 180), (550, 220), (700, 190), (800, 210),
            (80, 300), (250, 320), (450, 280), (650, 310), (780, 290),
            (120, 400), (350, 420), (520, 380), (680, 410), (810, 390)
        ]
        
        for i, (x, y) in enumerate(star_positions):
            # 星の明滅効果
            pulse = math.sin(self.animation_time * 0.05 + i * 0.5) * 0.3 + 0.7
            alpha = int(255 * pulse * 0.6)
            
            # 星の色（白からやや黄色）
            star_color = (255, int(255 * pulse), int(200 * pulse))
            
            # 星を描画（小さい十字形）
            size = 2
            pygame.draw.line(screen, star_color, (x-size, y), (x+size, y), 1)
            pygame.draw.line(screen, star_color, (x, y-size), (x, y+size), 1)
    
    def _draw_title(self, screen: pygame.Surface):
        """パルス効果付きのタイトル描画"""
        import math
        
        # パルス効果の計算
        pulse = math.sin(self.animation_time * 0.03) * 0.1 + 1.0
        
        # タイトルテキストを作成
        title_text = self.title_font.render("ひっぱりシューティング", True, Colors.YELLOW)
        
        # パルス効果を適用（スケーリング）
        if pulse != 1.0:
            original_size = title_text.get_size()
            new_size = (int(original_size[0] * pulse), int(original_size[1] * pulse))
            title_text = pygame.transform.scale(title_text, new_size)
        
        # 中央に配置（位置を上に移動）
        title_rect = title_text.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, 100))
        screen.blit(title_text, title_rect)
        
        # タイトルの影効果
        shadow_text = self.title_font.render("ひっぱりシューティング", True, (100, 100, 0))
        if pulse != 1.0:
            shadow_text = pygame.transform.scale(shadow_text, new_size)
        shadow_rect = shadow_text.get_rect(center=(GameConfig.SCREEN_WIDTH // 2 + 3, 103))
        screen.blit(shadow_text, shadow_rect)
        
        # メインテキストを再描画
        screen.blit(title_text, title_rect)
    
    def _draw_instructions(self, screen: pygame.Surface):
        """整理された説明文を描画"""
        # メインの説明
        main_instruction = "スリングショットでスタートボタンを撃とう！"
        main_text = self.font.render(main_instruction, True, Colors.WHITE)
        main_rect = main_text.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, 230))
        screen.blit(main_text, main_rect)
        
        # 操作説明のヘッダー
        control_header = "操作方法"
        header_text = self.small_font.render(control_header, True, Colors.CYAN)
        header_rect = header_text.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, 280))
        screen.blit(header_text, header_rect)
        
        # 操作説明の詳細
        controls = [
            "マウスドラッグ: スリングショットを引く",
            "マウスリリース: 弾を発射"
        ]
        
        y_offset = 310
        for control in controls:
            text = self.small_font.render(control, True, Colors.WHITE)
            text_rect = text.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, y_offset))
            screen.blit(text, text_rect)
            y_offset += 30
    
    def _draw_start_button(self, screen: pygame.Surface):
        """グロー効果付きのスタートボタン描画"""
        import math
        
        # グロー効果の計算
        glow = math.sin(self.animation_time * 0.08) * 0.3 + 0.7
        
        button_x = int(self.start_button_pos.x)
        button_y = int(self.start_button_pos.y)
        
        # グローエフェクト（複数の円で表現）
        for i in range(3, 0, -1):
            glow_radius = self.start_button_radius + i * 8
            glow_alpha = int(50 * glow / (i + 1))
            glow_color = (0, 255, 0, glow_alpha)
            
            # 透明サーフェスを作成してグローを描画
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surface, (button_x - glow_radius, button_y - glow_radius))
        
        # メインボタンの描画
        button_color = (int(0 + 100 * glow), int(255), int(0 + 100 * glow))
        pygame.draw.circle(screen, button_color, (button_x, button_y), self.start_button_radius)
        
        # ボタンの枠（強調）
        pygame.draw.circle(screen, Colors.WHITE, (button_x, button_y), self.start_button_radius, 4)
        
        # 内側の装飾
        inner_radius = self.start_button_radius - 8
        pygame.draw.circle(screen, (255, 255, 255, 100), (button_x, button_y), inner_radius, 2)
        
        # スタートボタンのラベル（フォントサイズを小さくしてボタン内に収める）
        # ボタン内に収まるようより小さいフォントを使用
        button_font = None
        for font_name in ['meiryoui', 'meiryo', 'msgothic', 'arial']:
            try:
                button_font = pygame.font.SysFont(font_name, 24)
                break
            except:
                continue
        if button_font is None:
            button_font = pygame.font.Font(None, 24)
            
        start_text = button_font.render("スタート", True, Colors.BLACK)
        start_rect = start_text.get_rect(center=(self.start_button_pos.x, self.start_button_pos.y))
        screen.blit(start_text, start_rect)
    
    def update(self, dt: float, mouse_pos: Vector2, mouse_pressed: bool, keys_pressed: set):
        """タイトルシーンの更新"""
        # アニメーション時間の更新
        self.animation_time += 1
        
        # プレイヤーの更新（スリングショット機能）
        self.player.update(dt, mouse_pos, mouse_pressed, self.start_button_pos)
        
        # プロジェクタイルとスタートボタンの当たり判定（シンプルな距離チェック）
        projectiles = self.player.get_projectiles()
        
        # デバッグ：プロジェクタイル数を表示
        if len(projectiles) > 0:
            print(f"Projectiles detected: {len(projectiles)}")
            
        for projectile in projectiles:
            # デバッグ：プロジェクタイルとスタートボタンの位置を表示
            distance = projectile.position.distance_to(self.start_button_pos)
            print(f"Projectile at ({projectile.position.x:.1f}, {projectile.position.y:.1f}), "
                  f"Start button at ({self.start_button_pos.x:.1f}, {self.start_button_pos.y:.1f}), "
                  f"Distance: {distance:.1f}, Required: {self.start_button_radius + projectile.radius:.1f}")
                  
            if distance < self.start_button_radius + projectile.radius:
                print("Start button hit! Starting game...")
                # スタートボタンに当たったらゲーム開始
                return SceneType.STAGE_1
        
        return None
    
    def handle_mouse_down(self, pos: tuple):
        """マウスクリックでゲーム開始"""
        return SceneType.STAGE_1


class GameOverScene(Scene):
    """ゲームオーバーシーン"""
    
    def __init__(self):
        super().__init__(SceneType.GAME_OVER)
        try:
            self.title_font = pygame.font.Font(None, 72)
            self.font = pygame.font.Font(None, 36)
        except:
            self.title_font = pygame.font.SysFont('arial', 72)
            self.font = pygame.font.SysFont('arial', 36)
    
    def render(self, screen: pygame.Surface):
        """ゲームオーバー画面の描画"""
        screen.fill((60, 30, 30))
        
        # ゲームオーバー
        game_over_text = self.title_font.render("GAME OVER", True, Colors.RED)
        game_over_rect = game_over_text.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, 200))
        screen.blit(game_over_text, game_over_rect)
        
        # リトライ指示
        retry_text = self.font.render("クリックしてリトライ", True, Colors.WHITE)
        retry_rect = retry_text.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, 400))
        screen.blit(retry_text, retry_rect)
    
    def handle_mouse_down(self, pos: tuple):
        """マウスクリックでリトライ"""
        return SceneType.TITLE


class GameClearScene(Scene):
    """ゲームクリアシーン"""
    
    def __init__(self):
        super().__init__(SceneType.GAME_CLEAR)
        try:
            self.title_font = pygame.font.Font(None, 72)
            self.font = pygame.font.Font(None, 36)
        except:
            self.title_font = pygame.font.SysFont('arial', 72)
            self.font = pygame.font.SysFont('arial', 36)
    
    def render(self, screen: pygame.Surface):
        """ゲームクリア画面の描画"""
        screen.fill((30, 60, 30))
        
        # ゲームクリア
        clear_text = self.title_font.render("GAME CLEAR!", True, Colors.GREEN)
        clear_rect = clear_text.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, 200))
        screen.blit(clear_text, clear_rect)
        
        # お疲れさまメッセージ
        thanks_text = self.font.render("お疲れさまでした！", True, Colors.WHITE)
        thanks_rect = thanks_text.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, 300))
        screen.blit(thanks_text, thanks_rect)
        
        # リトライ指示
        retry_text = self.font.render("クリックしてタイトルに戻る", True, Colors.WHITE)
        retry_rect = retry_text.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, 400))
        screen.blit(retry_text, retry_rect)
    
    def handle_mouse_down(self, pos: tuple):
        """マウスクリックでタイトルに戻る"""
        return SceneType.TITLE