"""
スリングショット物理計算の正確な再現
元のProcessingコードの物理計算を忠実に再現
"""
import math
from utils.math_utils import Vector2, MathUtils
from config.settings import GameConfig


class SlinghotPhysics:
    """元のコードの物理計算を正確に再現するクラス"""
    
    def __init__(self):
        # 物理定数（元のコードから）
        self.F = 0.2  # Force
        self.k = 1    # Spring constant
        self.m = 1    # Mass
        self.nearly_zero = 0.000001
        self.nearly_inf = 1 / self.nearly_zero
        
        # 角度関連
        self.cos_p = 0
        self.sin_p = 0
        self.cos_vp = 0
        self.sin_vp = 0
        self.tan_p = 0
        self.tan_vp = 0
        
        # 距離関連
        self.string_dist = 0
        self.dist_l = 0
        self.dist_r = 0
        
        # 手関連
        self.cos_l = 0
        self.sin_l = 0
        self.cos_r = 0
        self.sin_r = 0
        
        # エネルギー関連
        self.energy = 0
        self.energy_l = 0
        self.energy_r = 0
        self.energy_x = 0
        self.energy_y = 0
        self.energy_xl = 0
        self.energy_yl = 0
        self.energy_xr = 0
        self.energy_yr = 0
        
        # 速度関連
        self.velocity_p = 0
        self.velocity_x = 0
        self.velocity_y = 0
        
        # 加速度関連
        self.player_acceleration = 0
        self.acceleration_x = 0
        self.acceleration_y = 0
        
        # 差分（diff）関連
        self.diff_x = 0
        self.diff_y = 0
        
    def calculate_liner_equation(self, player_pos: Vector2, hand_pos: Vector2):
        """一次方程式を求める（元のliner_equation関数）"""
        if abs(player_pos.x - hand_pos.x) >= self.nearly_zero:
            self.cos_p = (hand_pos.x - player_pos.x) / self.string_dist
            self.sin_p = (hand_pos.y - player_pos.y) / self.string_dist
            self.tan_p = self.sin_p / self.cos_p
        elif player_pos.y > hand_pos.y:
            self.cos_p = 0
            self.sin_p = 1
            self.tan_p = self.nearly_inf
        else:
            self.cos_p = 0
            self.sin_p = -1
            self.tan_p = -self.nearly_inf
    
    def calculate_vertical_line(self):
        """垂直線の計算（元のvertical_line関数）"""
        self.cos_vp = self.sin_p
        self.sin_vp = -self.cos_p
        
        if abs(self.cos_vp) >= self.nearly_zero:
            self.tan_vp = self.sin_vp / self.cos_vp
        elif (self.cos_p > 0 and self.sin_p < 0) or (self.cos_p > 0 and self.sin_p > 0):
            self.cos_vp = 0
            self.sin_vp = 1
            self.tan_vp = self.nearly_inf
        else:
            self.cos_vp = 0
            self.sin_vp = -1
            self.tan_vp = -self.nearly_inf
    
    def calculate_distances(self, player_pos: Vector2, hand_pos: Vector2, 
                          hand_left: Vector2, hand_right: Vector2,
                          boh: list):
        """距離計算（元のcaluculate_dist関数）"""
        self.string_dist = player_pos.distance_to(hand_pos)
        self.dist_l = math.sqrt((boh[0] - hand_left.x)**2 + (boh[1] - hand_left.y)**2)
        self.dist_r = math.sqrt((boh[2] - hand_right.x)**2 + (boh[3] - hand_right.y)**2)
        self.diff_x = player_pos.x - hand_pos.x
        self.diff_y = player_pos.y - hand_pos.y
    
    def calculate_hand_vectors(self, hand_left: Vector2, hand_right: Vector2, boh: list):
        """手のベクトル計算（元のcalculate_hand_vector関数）"""
        if self.dist_l > 0:
            self.cos_l = (hand_left.x - boh[0]) / self.dist_l
            self.sin_l = (hand_left.y - boh[1]) / self.dist_l
        else:
            self.cos_l = 0
            self.sin_l = 0
            
        if self.dist_r > 0:
            self.cos_r = (hand_right.x - boh[2]) / self.dist_r
            self.sin_r = (hand_right.y - boh[3]) / self.dist_r
        else:
            self.cos_r = 0
            self.sin_r = 0
    
    def calculate_energy(self):
        """エネルギー計算（元のcalculate_energy関数）"""
        self.energy = (self.F * self.string_dist - self.m * self.velocity_p) * self.k
        self.energy_l = (self.F * self.dist_l - self.m * self.velocity_p) * self.k
        self.energy_r = (self.F * self.dist_r - self.m * self.velocity_p) * self.k
        
        self.energy_x = self.energy * self.cos_p
        self.energy_y = self.energy * self.sin_p
        
        self.energy_xl = self.energy_l * self.cos_l
        self.energy_yl = self.energy_l * self.sin_l
        self.energy_xr = self.energy_r * self.cos_r
        self.energy_yr = self.energy_r * self.sin_r
    
    def calculate_acceleration(self):
        """加速度計算（元のcalculate_player_acceleration関数）"""
        self.player_acceleration = self.energy
        self.acceleration_x = self.energy_xl + self.energy_xr
        self.acceleration_y = self.energy_yl + self.energy_yr
    
    def calculate_velocity(self, is_free: bool):
        """速度計算（元のcalculate_player_velocity関数）"""
        if not is_free:
            self.velocity_p += self.player_acceleration
            self.velocity_x += self.acceleration_x
            self.velocity_y += self.acceleration_y
        else:
            self.velocity_p = 0
            self.velocity_x = 0
            self.velocity_y = 0
    
    def calculate_position_update(self):
        """位置更新計算（元のcalculate_player_xy関数）"""
        self.diff_x += self.velocity_x
        self.diff_y += self.velocity_y
        
        return Vector2(self.diff_x, self.diff_y)
    
    def get_velocity_b(self):
        """発射時の速度計算（元のmouseReleased関数から）"""
        if self.energy >= 0:
            return math.sqrt(abs(self.energy))
        else:
            return -math.sqrt(abs(self.energy))
    
    def full_calculation_cycle(self, player_pos: Vector2, hand_pos: Vector2,
                              hand_left: Vector2, hand_right: Vector2,
                              boh: list, is_free: bool):
        """完全な物理計算サイクル"""
        # 1. 距離計算
        self.calculate_distances(player_pos, hand_pos, hand_left, hand_right, boh)
        
        # 2. 一次方程式計算
        self.calculate_liner_equation(player_pos, hand_pos)
        
        # 3. 垂直線計算
        self.calculate_vertical_line()
        
        # 4. 手のベクトル計算
        self.calculate_hand_vectors(hand_left, hand_right, boh)
        
        # 5. エネルギー計算
        self.calculate_energy()
        
        # 6. 加速度計算
        self.calculate_acceleration()
        
        # 7. 速度計算
        self.calculate_velocity(is_free)
        
        # 8. 位置更新
        return self.calculate_position_update()


class OriginalPlayerPhysics:
    """元のプレイヤー物理挙動を正確に再現"""
    
    def __init__(self, x: float, y: float):
        self.position = Vector2(x, y)
        self.radius = GameConfig.PLAYER_RADIUS
        
        # 元のコードの変数を正確に再現
        self.ellipse_round = GameConfig.PLAYER_RADIUS * 2
        self.player_is_free = True
        self.sling_cnt = 0
        self.sling_cnt_mx = GameConfig.SLING_MAX_COUNT
        self.pressed = False
        self.ready_for_shoot = False
        self.sling_moving = False
        
        # 手の位置
        self.handX = x
        self.handY = y
        self.handX_left = x - self.ellipse_round / 2
        self.handX_right = x + self.ellipse_round / 2
        self.handY_left = y
        self.handY_right = y
        
        # 手の一時保存
        self.hand_tmp = [0, 0, 0, 0]
        
        # 手の付け根（base of hand）
        self.boh = [x - self.ellipse_round / 2, y, 
                   x + self.ellipse_round / 2, y]
        
        # 物理計算エンジン
        self.physics = SlinghotPhysics()
        
        # 発射関連
        self.a_before = 0
        self.a_after = 0
        self.velocity_b = 0.0
        
        # プレイヤー位置（元のplayer_x, player_y）
        self.player_x = x
        self.player_y = y
        
        # 速度・加速度関連
        self.velocity_p = 0.0
        self.player_acceleration = 0.0
        
        # 時間カウンター
        self.time = 0
        self.time_cnt = 0
        
        # ボール関連
        self.ball_max = 3
        self.ball_n = 0
        self.ball_x = [GameConfig.SCREEN_WIDTH + 100] * self.ball_max
        self.ball_y = [GameConfig.SCREEN_HEIGHT + 100] * self.ball_max
        self.ball_vx = [0] * self.ball_max
        self.ball_vy = [0] * self.ball_max
        self.cos_b = [0] * self.ball_max
        self.sin_b = [0] * self.ball_max
        self.cos_b = [0] * self.ball_max
        self.sin_b = [0] * self.ball_max
    
    def player_place(self, mouse_x: float, mouse_y: float, mouse_pressed: bool):
        """元のplayer_place関数の正確な再現"""
        if self.player_is_free:  # マウスを動かせるとき
            resist = 5
            self.sling_cnt = 0
            
            if abs(self.physics.energy) >= resist:
                k = 0.03
                
                self.position.x = mouse_x + (abs(self.physics.energy) - resist) * self.physics.cos_p * 3
                self.position.y = mouse_y + (abs(self.physics.energy) - resist) * self.physics.sin_p * 3
                
                # 時間に基づく振動効果
                import pygame
                time = pygame.time.get_ticks() // 16  # 60FPSを模擬
                if time % 4 < 2:
                    self.position.x += abs(self.physics.energy) * self.physics.cos_vp * k
                    self.position.y += abs(self.physics.energy) * self.physics.sin_vp * k
                else:
                    self.position.x -= abs(self.physics.energy) * self.physics.cos_vp * k
                    self.position.y -= abs(self.physics.energy) * self.physics.sin_vp * k
            else:
                self.position.x = mouse_x
                self.position.y = mouse_y
        else:
            # スリングショット中：プレイヤーはマウスに追従
            self.position.x = mouse_x
            self.position.y = mouse_y
        
        # 画面境界チェック
        if self.position.x >= GameConfig.SCREEN_WIDTH - self.ellipse_round / 2:
            self.position.x = GameConfig.SCREEN_WIDTH - self.ellipse_round / 2
        if self.position.y >= GameConfig.SCREEN_HEIGHT - self.ellipse_round / 2:
            self.position.y = GameConfig.SCREEN_HEIGHT - self.ellipse_round / 2
        if self.position.x <= 0 + self.ellipse_round / 2:
            self.position.x = 0 + self.ellipse_round / 2
        if self.position.y <= 0 + self.ellipse_round / 2:
            self.position.y = 0 + self.ellipse_round / 2
        
        # 手の位置計算（シンプルな実装）
        hand_left_pos = Vector2(self.handX_left, self.handY_left)
        hand_right_pos = Vector2(self.handX_right, self.handY_right)
        string_dist = math.sqrt((hand_left_pos.x - hand_right_pos.x)**2 + 
                               (hand_left_pos.y - hand_right_pos.y)**2)
        
        if string_dist <= 200 or self.physics.string_dist < 200 and self.sling_cnt < self.sling_cnt_mx:
            # 元のProcessingコードを正確に再現（hand_diff配列の計算）
            # hand_diff[0][2] = string_dist, hand_diff[1][2] = 0を回転
            # 回転前: X方向にstring_dist, Y方向に0
            # 回転後: cos_vp * string_dist, sin_vp * string_dist
            
            hand_diff_x = self.physics.cos_vp * self.physics.string_dist
            hand_diff_y = self.physics.sin_vp * self.physics.string_dist
            
            # 元コード通り: handX_left=handX+hand_diff[0][2]/2; handX_right=handX-hand_diff[0][2]/2;
            self.handX_left = self.handX + hand_diff_x / 2
            self.handX_right = self.handX - hand_diff_x / 2
            self.handY_left = self.handY + hand_diff_y / 2
            self.handY_right = self.handY - hand_diff_y / 2
        
        if not mouse_pressed and self.player_is_free or self.sling_cnt >= self.sling_cnt_mx:
            # マウスを押していない間
            self.handX = self.position.x
            self.handY = self.position.y
            self.handX_left = self.handX - self.ellipse_round / 2
            self.handX_right = self.handX + self.ellipse_round / 2
            self.handY_left = self.handY
            self.handY_right = self.handY
        
        if mouse_pressed:
            self.hand_tmp[0] = self.handX_left
            self.hand_tmp[1] = self.handX_right
            self.hand_tmp[2] = self.handY_left
            self.hand_tmp[3] = self.handY_right
        
        if not self.player_is_free:
            # calculate_player_xy()の呼び出し
            pos_update = self.physics.calculate_position_update()
            self.position.x = pos_update.x + self.handX
            self.position.y = pos_update.y + self.handY
            
            if self.sling_cnt < self.sling_cnt_mx:
                self.handX_left = self.hand_tmp[0]
                self.handX_right = self.hand_tmp[1]
                self.handY_left = self.hand_tmp[2]
                self.handY_right = self.hand_tmp[3]
            
            self.sling_cnt += 1
        
        if self.sling_cnt >= self.sling_cnt_mx:
            self.handX_left = self.handX - self.ellipse_round / 2
            self.handX_right = self.handX + self.ellipse_round / 2
            self.handY_left = self.handY
            self.handY_right = self.handY
            self.sling_moving = False
    
    def update(self, dt: float, mouse_pos: Vector2, mouse_pressed: bool):
        """メイン更新処理"""
        # sling_cntのインクリメント（元のコード: if(!player_is_free){ sling_cnt++; }）
        if not self.player_is_free:
            self.sling_cnt += 1
            if self.sling_cnt % 60 == 0:  # デバッグ用に1秒毎に表示
                print(f"sling_cnt: {self.sling_cnt}, sling_cnt_mx: {self.sling_cnt_mx}, ready_for_shoot: {self.ready_for_shoot}")
        
        # 物理計算の実行
        hand_pos = Vector2(self.handX, self.handY)
        hand_left = Vector2(self.handX_left, self.handY_left)
        hand_right = Vector2(self.handX_right, self.handY_right)
        
        self.physics.full_calculation_cycle(
            self.position, hand_pos, hand_left, hand_right,
            self.boh, self.player_is_free
        )
        
        # プレイヤーの位置更新
        self.player_place(mouse_pos.x, mouse_pos.y, mouse_pressed)
        
        # 手の付け根位置更新
        self.hand_place()
        
        # 発射判定（重要：free_playerの前に実行）
        self.shoot(mouse_pressed)
        
        # 自由状態への復帰判定
        self.free_player()
    
    def hand_place(self):
        """手の付け根位置更新（元のhand_place関数）"""
        if self.sling_moving:
            self.boh[0] = self.position.x + self.ellipse_round / 2 * self.physics.cos_vp
            self.boh[1] = self.position.y + self.ellipse_round / 2 * self.physics.sin_vp
            self.boh[2] = self.position.x - self.ellipse_round / 2 * self.physics.cos_vp
            self.boh[3] = self.position.y - self.ellipse_round / 2 * self.physics.sin_vp
        else:
            self.boh[0] = self.position.x + self.ellipse_round / 2 * 1
            self.boh[1] = self.position.y + self.ellipse_round / 2 * 0
            self.boh[2] = self.position.x - self.ellipse_round / 2 * 1
            self.boh[3] = self.position.y - self.ellipse_round / 2 * 0
    
    def mouse_pressed(self):
        """マウス押下処理（元のmousePressed関数）"""
        self.pressed = True
        self.sling_moving = True
        
        # スリング開始時の手の中心位置を記録
        self.handX = self.position.x
        self.handY = self.position.y
        # スリングの中心位置を現在のプレイヤー位置に設定
        self.handX = self.position.x
        self.handY = self.position.y
    
    def mouse_released(self, string_dist: float):
        """マウス離脱処理（元のmouseReleased関数）"""
        print(f"Mouse released! String dist: {string_dist}, Pressed: {self.pressed}")
        
        if self.pressed:
            self.player_is_free = False
            # velocity_bの計算
            if self.physics.energy >= 0:
                self.velocity_b = math.sqrt(abs(self.physics.energy))
            else:
                self.velocity_b = -math.sqrt(abs(self.physics.energy))
            
            # 発射準備判定（重要：pressedがTrueの時のみ）
            if string_dist > 100:
                self.ready_for_shoot = True
                print(f"Ready to shoot set to True! String dist: {string_dist}")
        
        # タイマーをリセット
        self.time = 0
        self.time_cnt = 0
        
        # 発射方向を記録
        self.cos_b[self.ball_n] = self.physics.cos_p
        self.sin_b[self.ball_n] = self.physics.sin_p
        
        # 注意：元のコードではmouseReleased()でpressedをfalseにしない
        # pressedはfree_player()でplayer_is_free=trueになったときにリセットされる
    
    def shoot(self, mouse_pressed: bool):
        """発射処理（元のshoot関数）"""
        self.a_after = abs(self.physics.player_acceleration)
        
        # デバッグ：発射条件を詳細に表示
        condition1 = self.a_after > self.a_before
        condition2 = self.sling_cnt > 1
        condition3 = not mouse_pressed  # 元のコードの!mousePressed
        condition4 = self.ready_for_shoot
        
        all_conditions = condition1 and condition2 and condition3 and condition4
        
        if self.sling_cnt % 30 == 0 or self.ready_for_shoot:  # デバッグ用
            print(f"Shoot conditions - a_after:{self.a_after:.2f} > a_before:{self.a_before:.2f}={condition1}, "
                  f"sling_cnt:{self.sling_cnt}>1={condition2}, !mousePressed={condition3}, ready={condition4} => {all_conditions}")
        
        # 元の発射条件: a_after>a_before&&sling_cnt>1&&!mousePressed&&ready_for_shoot
        # 注意：!mousePressed は現在のマウス状態、!pressed は独立したフラグ
        if all_conditions:
            print(f"🚀 SHOOTING! Ball {self.ball_n} at ({self.position.x:.1f}, {self.position.y:.1f})")
            
            self.ready_for_shoot = False
            self.ball_x[self.ball_n] = self.position.x
            self.ball_y[self.ball_n] = self.position.y
            # 元: ball_vx[ball_n]=velocity_x/2; ball_vy[ball_n]=velocity_y/2;
            self.ball_vx[self.ball_n] = self.physics.velocity_x / 2
            self.ball_vy[self.ball_n] = self.physics.velocity_y / 2
            
            print(f"Ball velocity: ({self.ball_vx[self.ball_n]:.2f}, {self.ball_vy[self.ball_n]:.2f})")
            print(f"Energy: {self.physics.energy:.2f}")
            
            self.ball_n += 1
            if self.ball_n >= self.ball_max:
                self.ball_n = 0
        
        self.a_before = abs(self.physics.player_acceleration)
    
    def move_ball(self):
        """ボール移動処理（元のmove_ball関数）"""
        for i in range(3):
            self.ball_x[i] += self.ball_vx[i]
            self.ball_y[i] += self.ball_vy[i]
    
    def free_player(self):
        """プレイヤー自由化処理（元のfree_player関数）"""
        # 元の条件: if(sling_cnt>=sling_cnt_mx&&pressed)
        if self.sling_cnt >= self.sling_cnt_mx and self.pressed:
            print(f"Free player! sling_cnt={self.sling_cnt}, sling_cnt_mx={self.sling_cnt_mx}, pressed={self.pressed}")
            self.physics.player_acceleration = 0
            self.physics.velocity_p = 0
            self.player_is_free = True
            self.sling_moving = False
            # pressedフラグもここでリセット
            self.pressed = False
            print("Pressed flag reset to False in free_player")
