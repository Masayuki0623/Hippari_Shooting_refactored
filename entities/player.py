"""
プレイヤー関連のクラス
"""
import pygame
import math
from typing import List, Optional
from utils.math_utils import Vector2, MathUtils
from config.settings import GameConfig, Colors
from utils.collision import CollisionDetector
from utils.original_physics import OriginalPlayerPhysics


class SimpleProjectile:
    """シンプルなプロジェクタイル（外部インターフェース用）"""
    def __init__(self, position: Vector2, velocity: Vector2, radius: float, velocity_b: float = 0):
        self.position = position
        self.velocity = velocity
        self.radius = radius
        self.active = True
        self.velocity_b = velocity_b  # オリジナルのvelocity_b値
        self.ball_index = -1  # 元のball_x配列のインデックス
        
        # Enemyとの衝突で使用するための位置属性（互換性）
        self.x = position.x
        self.y = position.y
    
    def update_position(self):
        """位置属性を最新のpositionに同期"""
        self.x = self.position.x
        self.y = self.position.y
    
    def get_damage(self) -> int:
        """速度に基づいたダメージ計算 - 元のabs(velocity_b)"""
        return int(abs(self.velocity_b))


class Projectile:
    """プロジェクタイル（発射体）クラス"""
    
    def __init__(self, position: Vector2, velocity: Vector2, radius: float = GameConfig.PLAYER_RADIUS):
        self.position = position
        self.velocity = velocity
        self.radius = radius
        self.active = True
        self.rotation = 0
        
    def update(self, dt: float):
        """プロジェクタイルの更新"""
        if not self.active:
            return
            
        # 位置を更新
        self.position += self.velocity * dt * 60  # 60FPSベースの調整
        
        # 回転を更新（見た目用）
        self.rotation += dt * 5
        
        # 画面外チェック
        if (self.position.x < -self.radius or 
            self.position.x > GameConfig.SCREEN_WIDTH + self.radius or
            self.position.y < -self.radius or 
            self.position.y > GameConfig.SCREEN_HEIGHT + self.radius):
            self.active = False
    
    def render(self, screen: pygame.Surface):
        """プロジェクタイルの描画"""
        if not self.active:
            return
            
        # メインボール
        pygame.draw.circle(screen, Colors.PLAYER_BODY, 
                          (int(self.position.x), int(self.position.y)), 
                          int(self.radius))
        
        # 回転する表情（元のコードを簡略化）
        eye_size = self.radius // 6
        eye_offset = self.radius // 3
        
        # 回転を考慮した目の位置
        cos_r = math.cos(self.rotation)
        sin_r = math.sin(self.rotation)
        
        left_eye_x = self.position.x - eye_offset * cos_r
        left_eye_y = self.position.y - eye_offset * sin_r
        right_eye_x = self.position.x + eye_offset * cos_r  
        right_eye_y = self.position.y + eye_offset * sin_r
        
        # 目を描画（簡略化）
        pygame.draw.circle(screen, Colors.BLACK, 
                          (int(left_eye_x), int(left_eye_y)), eye_size)
        pygame.draw.circle(screen, Colors.BLACK, 
                          (int(right_eye_x), int(right_eye_y)), eye_size)


class Player:
    """プレイヤークラス - 元の挙動を正確に再現"""
    
    def __init__(self, x: float, y: float):
        # 元の物理計算エンジンを使用
        self.original_physics = OriginalPlayerPhysics(x, y)
        
        # 弾管理は物理システム内で行う
        
        # 基本パラメータ
        self.max_hp = GameConfig.PLAYER_MAX_HP
        self.hp = self.max_hp
        
        # 状態管理
        self.invincibility_timer = 0
        self.is_invincible = False
        
        # 視線（敵を見る方向）
        self.eye_target = Vector2(0, 0)
        
        # 入力状態
        self.mouse_pressed = False
        self.last_mouse_pos = Vector2(x, y)
        
        # 目の方向オフセット
        self.eye_offset_x = 0
        self.eye_offset_y = 0
        
    def update(self, dt: float, mouse_pos: Vector2, mouse_pressed: bool, target_enemy_pos: Optional[Vector2] = None):
        """プレイヤーの更新 - 元のplayer.pdeの完全再現"""
        # 無敵時間の更新（元: inb_cnt++）
        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1
            self.is_invincible = self.invincibility_timer > 0
        
        # マウス状態の更新（元のmousePressed処理）
        self._handle_mouse_input(mouse_pos, mouse_pressed)
        
        # プレイヤー配置更新（元: player_place()）
        self._player_place(mouse_pos)
        
        # プレイヤーを自由にする処理（元: free_player()）
        self._free_player()
        
        # 物理計算更新
        self.original_physics.update(dt, mouse_pos, mouse_pressed)
        
        # ボール移動（元: move_ball()）
        self.original_physics.move_ball()
        
        # 視線の更新
        if target_enemy_pos:
            self.eye_target = target_enemy_pos
    
    def handle_event(self, event):
        """イベント処理（空実装 - 必要に応じて実装）"""
        pass
    
    def get_current_velocity_b(self) -> float:
        """現在のvelocity_b値を取得（オリジナルのグローバル変数相当）"""
        return self.original_physics.velocity_b
    
    def _handle_mouse_input(self, mouse_pos: Vector2, mouse_pressed: bool):
        """マウス入力処理 - 元のmousePressed()とmouseReleased()"""
        if mouse_pressed and not self.mouse_pressed:
            # mousePressed()相当
            self.original_physics.pressed = True
            self.original_physics.sling_moving = True
            print("Mouse pressed - sling start")
            
        elif not mouse_pressed and self.mouse_pressed:
            # mouseReleased()相当 
            if self.original_physics.pressed:
                self.original_physics.player_is_free = False
                
                # エネルギーから速度計算（元: if(energy>=0){velocity_b=sqrt(abs(energy));}）
                energy = self.original_physics.physics.energy
                if energy >= 0:
                    self.original_physics.velocity_b = math.sqrt(abs(energy))
                else:
                    self.original_physics.velocity_b = -math.sqrt(abs(energy))
                
                # 発射準備判定（元: if(string_dist>100)）
                if self.original_physics.physics.string_dist > 100:
                    self.original_physics.ready_for_shoot = True
                
                # カウンターリセット
                self.original_physics.time = 0
                self.original_physics.time_cnt = 0
                
                # 発射角度保存
                ball_n = self.original_physics.ball_n
                self.original_physics.cos_b[ball_n] = self.original_physics.physics.cos_p
                self.original_physics.sin_b[ball_n] = self.original_physics.physics.sin_p
                
                print(f"Mouse released - ready to shoot: {self.original_physics.ready_for_shoot}")
        
        self.mouse_pressed = mouse_pressed
        self.last_mouse_pos = mouse_pos
    
    def _player_place(self, mouse_pos: Vector2):
        """プレイヤー配置 - 元のplayer_place()関数を完全再現"""
        physics = self.original_physics.physics
        
        if self.original_physics.player_is_free:  # マウスを動かせるとき
            resist = 5
            self.original_physics.sling_cnt = 0
            
            if abs(physics.energy) >= resist:
                k = 0.03
                
                # エネルギーによる位置オフセット
                self.original_physics.player_x = (mouse_pos.x + 
                    (abs(physics.energy) - resist) * physics.cos_p * 3)
                self.original_physics.player_y = (mouse_pos.y + 
                    (abs(physics.energy) - resist) * physics.sin_p * 3)
                
                # 振動効果（元: if(time%4<2)）
                if self.original_physics.time % 4 < 2:
                    self.original_physics.player_x += abs(physics.energy) * physics.cos_vp * k
                    self.original_physics.player_y += abs(physics.energy) * physics.sin_vp * k
                else:
                    self.original_physics.player_x -= abs(physics.energy) * physics.cos_vp * k
                    self.original_physics.player_y -= abs(physics.energy) * physics.sin_vp * k
            else:
                self.original_physics.player_x = mouse_pos.x
                self.original_physics.player_y = mouse_pos.y
        
        # 画面境界制限（元のコード通り）
        ellipse_round = GameConfig.ELLIPSE_ROUND
        self.original_physics.player_x = max(ellipse_round/2, 
            min(GameConfig.SCREEN_WIDTH - ellipse_round/2, self.original_physics.player_x))
        self.original_physics.player_y = max(ellipse_round/2, 
            min(GameConfig.SCREEN_HEIGHT - ellipse_round/2, self.original_physics.player_y))
        
        # 手の位置制御（元のコード通り）
        if not self.mouse_pressed and self.original_physics.player_is_free:
            # マウスを押していない間
            self.original_physics.handX = self.original_physics.player_x
            self.original_physics.handY = self.original_physics.player_y
            self.original_physics.handX_left = self.original_physics.handX - ellipse_round/2
            self.original_physics.handX_right = self.original_physics.handX + ellipse_round/2
            self.original_physics.handY_left = self.original_physics.handY
            self.original_physics.handY_right = self.original_physics.handY
    
    def _free_player(self):
        """プレイヤーを自由にする - 元のfree_player()関数"""
        if (self.original_physics.sling_cnt >= self.original_physics.sling_cnt_mx and 
            self.original_physics.pressed):
            
            self.original_physics.player_acceleration = 0
            self.original_physics.velocity_p = 0
            self.original_physics.player_is_free = True
    
    def handle_event(self, event):
        """イベント処理 - プレイヤー固有の入力処理"""
        # 現在のPlayer実装では特別な入力処理は不要
        # マウス入力は update() メソッドで処理される
        pass
    
    @property
    def position(self) -> Vector2:
        """プレイヤー位置"""
        return self.original_physics.position
    
    @property
    def radius(self) -> float:
        """プレイヤー半径"""
        return self.original_physics.radius
    
    @property
    def projectiles(self) -> List:
        """プロジェクタイルのリスト（元のball_x, ball_yから変換）"""
        projectiles = []
        
        for i in range(self.original_physics.ball_max):
            ball_x = self.original_physics.ball_x[i]
            ball_y = self.original_physics.ball_y[i]
            
            # アクティブなボールの判定（初期化値以外）
            if (ball_x < GameConfig.SCREEN_WIDTH + 50 and ball_x > -50 and
                ball_y < GameConfig.SCREEN_HEIGHT + 50 and ball_y > -50 and
                not (ball_x >= GameConfig.SCREEN_WIDTH + 50)):
                
                # オリジナルのダメージシステムを正確に再現
                # 注意: オリジナルではvelocity_bはグローバル変数で、発射時のエネルギー値
                current_velocity_b = self.original_physics.velocity_b
                
                # デバッグ情報
                if i == 0 and abs(current_velocity_b) > 0.1:
                    print(f"Ball {i}: pos=({ball_x:.1f}, {ball_y:.1f}), velocity_b={current_velocity_b:.2f}")
                
                proj = SimpleProjectile(
                    Vector2(ball_x, ball_y),
                    Vector2(self.original_physics.ball_vx[i], self.original_physics.ball_vy[i]),
                    self.original_physics.radius,
                    current_velocity_b  # 現在のvelocity_b値を使用
                )
                projectiles.append(proj)
                
        return projectiles
    

    
    def _check_for_new_projectiles(self):
        """新しい発射された弾をProjectileManagerに追加"""
        # 元の物理システムで管理されているボールをチェック
        for i in range(self.original_physics.ball_max):
            ball_x = self.original_physics.ball_x[i]
            ball_y = self.original_physics.ball_y[i] 
            ball_vx = self.original_physics.ball_vx[i]
            ball_vy = self.original_physics.ball_vy[i]
            
            # 速度がある弾を検出（発射された弾）
            if abs(ball_vx) > 0.1 or abs(ball_vy) > 0.1:
                # すでにProjectileManagerに追加されているかチェック
                cos_angle = self.original_physics.cos_b[i]
                sin_angle = self.original_physics.sin_b[i]
                
                # 弾の管理は物理システム内で完結
                pass
    
    def get_position(self) -> Vector2:
        """プレイヤー位置を取得"""
        return self.original_physics.position
    
    def reset_velocity_b_after_hit(self):
        """衝突後のvelocity_bをリセット（オリジナルのvelocity_b=0;）"""
        self.original_physics.velocity_b = 0
        print("velocity_b reset to 0 after hit")
    
    def take_damage(self, damage: int = 1):
        """ダメージを受ける"""
        if not self.is_invincible:
            self.hp = max(0, self.hp - damage)
            self.invincibility_timer = GameConfig.PLAYER_INVINCIBILITY_TIME
            self.is_invincible = True
            return True
        return False
    
    def render(self, screen: pygame.Surface):
        """プレイヤーの描画 - 元のdraw_player()とplayer_img()を再現"""
        # 無敵時間中の点滅効果（元のinb_cnt >= inb_max処理）
        if self.is_invincible:
            if int(self.invincibility_timer) % 10 < 5:
                # 点滅のため一部フレームで描画しない
                return
        
        # 手を描画（元のdraw_hand()）
        self._render_hands(screen)
        
        # プレイヤー本体を描画（元のplayer_img()）
        self._render_player_img(screen)
        
        # プロジェクタイル（ボール）を描画（元のmove_ball()）
        self._render_balls(screen)
        
        # プロジェクタイル描画は物理システムで完結
    
    def _render_hands(self, screen: pygame.Surface):
        """手を描画（元のdraw_hand()関数を再現）"""
        physics = self.original_physics.physics
        
        # スリングショット中の手の角度
        if self.original_physics.player_is_free and self.mouse_pressed:
            cos_li = physics.cos_l
            sin_li = physics.sin_l
            cos_ri = physics.cos_r
            sin_ri = physics.sin_r
        else:
            cos_li = -1
            sin_li = 0  
            cos_ri = 1
            sin_ri = 0
        
        # ひもの太さ（エネルギーに応じて変更）
        w = 1
        if physics.energy < 100:
            w = max(1, int(10 - math.sqrt(abs(physics.energy))))
        
        # プレイヤーの色（エネルギーに応じて変更）
        player_g = 255
        if abs(physics.energy) > 0:
            player_g = max(0, 255 - int(abs(physics.energy) * 3))
        
        # ひもを描画
        if w > 1:
            pygame.draw.line(screen, (255, player_g, 0),
                           (self.original_physics.boh[0], self.original_physics.boh[1]),
                           (self.original_physics.handX_left, self.original_physics.handY_left), w)
            pygame.draw.line(screen, (255, player_g, 0),
                           (self.original_physics.boh[2], self.original_physics.boh[3]),
                           (self.original_physics.handX_right, self.original_physics.handY_right), w)
        
        # 手の描画
        self._render_hand_img(screen, self.original_physics.handX_left, self.original_physics.handY_left,
                            sin_li, cos_li, self.original_physics.ellipse_round / 2, player_g)
        self._render_hand_img(screen, self.original_physics.handX_right, self.original_physics.handY_right,
                            sin_ri, cos_ri, self.original_physics.ellipse_round / 2, player_g)
    
    def _render_hand_img(self, screen: pygame.Surface, x: float, y: float, s: float, c: float, r: float, player_g: int):
        """手の画像描画（元のhand_img()関数を再現）"""
        t = math.atan2(s, c)
        
        # 手の指部分を描画
        # 元のコードの複雑な回転描画を簡略化
        color = (255, player_g, 0)
        finger_radius = r // 4
        
        # 基本的な手の形
        pygame.draw.circle(screen, color, (int(x), int(y)), int(r // 2))
        
        # 指の部分
        for i in range(4):
            finger_angle = t + (i - 1.5) * 0.3
            finger_x = x + math.cos(finger_angle) * r * 0.7
            finger_y = y + math.sin(finger_angle) * r * 0.7
            pygame.draw.circle(screen, color, (int(finger_x), int(finger_y)), finger_radius)
    
    def _render_player_img(self, screen: pygame.Surface):
        """プレイヤー本体描画（元のplayer_img()関数を再現）"""
        x = self.position.x
        y = self.position.y
        r = self.original_physics.ellipse_round
        
        # 目のパラメータ
        eye_xr = r / 6
        eye_yr = r / 4
        eye_r = r / 10
        
        # プレイヤーの色
        player_g = 255
        if abs(self.original_physics.physics.energy) > 0:
            player_g = max(0, 255 - int(abs(self.original_physics.physics.energy) * 3))
        
        # 本体を描画
        pygame.draw.circle(screen, (255, player_g, 0), (int(x), int(y)), int(r / 2))
        
        if not self.mouse_pressed:
            # 通常時の目
            self._calculate_eye_direction()
            
            # 左目の白目
            pygame.draw.ellipse(screen, Colors.WHITE,
                              (x - eye_xr - eye_xr, y - r / 8 - eye_yr, 2 * eye_xr, 2 * eye_yr))
            # 右目の白目  
            pygame.draw.ellipse(screen, Colors.WHITE,
                              (x + eye_xr - eye_xr, y - r / 8 - eye_yr, 2 * eye_xr, 2 * eye_yr))
            
            # 左目の黒目
            pygame.draw.circle(screen, Colors.BLACK,
                             (int(x + self.eye_offset_x - eye_xr), int(y - r / 8 + self.eye_offset_y)),
                             int(eye_r))
            # 右目の黒目
            pygame.draw.circle(screen, Colors.BLACK,
                             (int(x + self.eye_offset_x + eye_xr), int(y - r / 8 + self.eye_offset_y)),
                             int(eye_r))
        else:
            # スリングショット時の目（集中した表情）
            physics = self.original_physics.physics
            eye_y = y - r / 8
            
            # 左目の線
            pygame.draw.line(screen, Colors.BLACK,
                           (x - (3/2 * eye_yr) * physics.cos_vp + (r/8 - 3/2 * eye_xr) * physics.sin_vp,
                            eye_y - (r/8 - 3/2 * eye_xr) * physics.cos_vp - (3/2 * eye_yr) * physics.sin_vp),
                           (x - (eye_xr/4) * physics.cos_vp + (r/8) * physics.sin_vp,
                            eye_y - (r/8) * physics.cos_vp - (eye_xr/4) * physics.sin_vp), 2)
            
            # 右目の線  
            pygame.draw.line(screen, Colors.BLACK,
                           (x + (3/2 * eye_yr) * physics.cos_vp + (r/8 - 3/2 * eye_xr) * physics.sin_vp,
                            eye_y - (r/8 - 3/2 * eye_xr) * physics.cos_vp + (3/2 * eye_yr) * physics.sin_vp),
                           (x + (eye_xr/4) * physics.cos_vp + (r/8) * physics.sin_vp,
                            eye_y - (r/8) * physics.cos_vp + (eye_xr/4) * physics.sin_vp), 2)
    
    def _calculate_eye_direction(self):
        """目の方向計算（元のcal_eye()関数を再現）"""
        if self.eye_target and (self.eye_target.x != 0 or self.eye_target.y != 0):
            dist_e = self.position.distance_to(self.eye_target)
            if dist_e > 0:
                cos = (self.eye_target.x - self.position.x) / dist_e
                sin = (self.eye_target.y - self.position.y) / dist_e
                eye_xr = self.original_physics.ellipse_round / 6
                eye_r = self.original_physics.ellipse_round / 10
                self.eye_offset_x = (eye_xr - eye_r) * cos
                self.eye_offset_y = (eye_xr - eye_r) * sin
            else:
                self.eye_offset_x = 0
                self.eye_offset_y = 0
        else:
            self.eye_offset_x = 0
            self.eye_offset_y = 0
    
    def _render_balls(self, screen: pygame.Surface):
        """ボール描画（元のmove_ball()関数を再現）"""
        physics = self.original_physics.physics
        
        for i in range(3):
            ball_x = self.original_physics.ball_x[i]
            ball_y = self.original_physics.ball_y[i]
            
            # 画面内のボールのみ描画
            if (ball_x < -50 or ball_x > GameConfig.SCREEN_WIDTH + 50 or 
                ball_y < -50 or ball_y > GameConfig.SCREEN_HEIGHT + 50):
                continue
            
            # ボール本体
            r = self.original_physics.ellipse_round
            pygame.draw.circle(screen, Colors.YELLOW, (int(ball_x), int(ball_y)), int(r / 2))
            
            # ボールの表情（回転）
            eye_xr = r / 6
            eye_yr = r / 4
            eye_r = r / 10
            
            # 回転角度
            import pygame as pg
            cnt = pg.time.get_ticks() // 16  # 60FPS相当
            ball_vx = self.original_physics.ball_vx[i]
            ball_vy = self.original_physics.ball_vy[i]
            rotation = math.atan2(ball_vy, ball_vx) + math.pi/2 + cnt/5
            
            # 回転した目を描画（簡略化）
            eye_offset = r / 4
            left_eye_x = ball_x - math.cos(rotation) * eye_offset
            left_eye_y = ball_y - math.sin(rotation) * eye_offset  
            right_eye_x = ball_x + math.cos(rotation) * eye_offset
            right_eye_y = ball_y + math.sin(rotation) * eye_offset
            
            pygame.draw.line(screen, Colors.BLACK,
                           (left_eye_x - 3, left_eye_y - 3), (left_eye_x + 3, left_eye_y + 3), 2)
            pygame.draw.line(screen, Colors.BLACK,
                           (right_eye_x - 3, right_eye_y - 3), (right_eye_x + 3, right_eye_y + 3), 2)
    
    def get_projectiles(self) -> List[SimpleProjectile]:
        """アクティブなプロジェクタイルのリストを取得"""
        projectiles = []
        
        for i in range(self.original_physics.ball_n):
            ball_x = self.original_physics.ball_x[i]
            ball_y = self.original_physics.ball_y[i]
            ball_vx = self.original_physics.ball_vx[i]
            ball_vy = self.original_physics.ball_vy[i]
            
            # 画面内にあるアクティブな弾のみ追加
            if (0 <= ball_x <= GameConfig.SCREEN_WIDTH and 
                0 <= ball_y <= GameConfig.SCREEN_HEIGHT):
                
                projectile = SimpleProjectile(
                    position=Vector2(ball_x, ball_y),
                    velocity=Vector2(ball_vx, ball_vy),
                    radius=self.original_physics.ellipse_round,
                    velocity_b=self.original_physics.velocity_b
                )
                # 弾のインデックスを保存（衝突時の消去用）
                projectile.ball_index = i
                projectiles.append(projectile)
        
        return projectiles
    
    def reset_velocity_b_after_hit(self):
        """衝突後にvelocity_bをリセット（オリジナルのvelocity_b=0相当）"""
        self.original_physics.velocity_b = 0
    
    def remove_projectile_by_collision(self, ball_index: int):
        """衝突した弾を除去 - 元のball_x[i]=width+100;完全再現"""
        if 0 <= ball_index < len(self.original_physics.ball_x):
            # 元: ball_x[i]=width+100;ball_y[i]=height+100;
            self.original_physics.ball_x[ball_index] = GameConfig.SCREEN_WIDTH + 100
            self.original_physics.ball_y[ball_index] = GameConfig.SCREEN_HEIGHT + 100
            # 元: ball_vx[i]=0;ball_vy[i]=0;
            self.original_physics.ball_vx[ball_index] = 0
            self.original_physics.ball_vy[ball_index] = 0
    
    def clear_all_projectiles(self):
        """全ての弾丸をクリア - ステージ遷移時のリセット用"""
        for i in range(len(self.original_physics.ball_x)):
            self.original_physics.ball_x[i] = GameConfig.SCREEN_WIDTH + 100
            self.original_physics.ball_y[i] = GameConfig.SCREEN_HEIGHT + 100
            self.original_physics.ball_vx[i] = 0
            self.original_physics.ball_vy[i] = 0
        
        # velocity_bもリセット
        self.original_physics.velocity_b = 0
        print("All player projectiles cleared")