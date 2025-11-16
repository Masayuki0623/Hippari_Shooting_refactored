"""
弾（プロジェクタイル）クラス
元のmove_ball関数の機能を再現
"""

import pygame
import math
from pygame import Vector2
from config.settings import GameConfig, Colors

class Projectile:
    """プロジェクタイルクラス - 元のmove_ball関数の再現"""
    
    def __init__(self, x: float, y: float, vx: float, vy: float, 
                 cos_angle: float, sin_angle: float, velocity_b: float = 0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.cos_angle = cos_angle
        self.sin_angle = sin_angle
        self.radius = GameConfig.ELLIPSE_ROUND
        self.active = True
        
        # ダメージ計算用の速度（元のvelocity_b相当）
        self.velocity_b = velocity_b  # オリジナルのvelocity_b値を直接使用
        
        # アニメーション用カウンター
        self.rotation_counter = 0
    
    def get_damage(self) -> int:
        """速度に基づいたダメージ計算 - 元のabs(velocity_b)"""
        # 元: e.hp-=abs(velocity_b);
        return int(abs(self.velocity_b))
        
    def update(self):
        """弾の位置更新"""
        if not self.active:
            return
            
        self.x += self.vx
        self.y += self.vy
        self.rotation_counter += 1
        
        # 画面外チェック
        screen_margin = 100
        if (self.x < -screen_margin or self.x > GameConfig.SCREEN_WIDTH + screen_margin or
            self.y < -screen_margin or self.y > GameConfig.SCREEN_HEIGHT + screen_margin):
            self.active = False
    
    def draw(self, screen: pygame.Surface):
        """弾の描画 - 元のmove_ball関数の描画部分を再現"""
        if not self.active:
            return
            
        # 基本の弾の円（黄色）
        pygame.draw.circle(screen, Colors.YELLOW, (int(self.x), int(self.y)), 
                          int(self.radius / 2))
        
        # 弾の詳細描画（目と線）
        self._draw_projectile_details(screen)
    
    def _draw_projectile_details(self, screen: pygame.Surface):
        """弾の詳細描画（目と線の描画）"""
        r = self.radius
        eye_xr = r / 6
        eye_yr = r / 4
        eye_r = r / 10
        
        # 回転角度計算（元のコード：atan2(ball_vy[i],ball_vx[i])+PI/2+(float)cnt/5）
        base_angle = math.atan2(self.vy, self.vx) + math.pi / 2
        rotation_angle = base_angle + self.rotation_counter / 5.0
        
        cos_rot = math.cos(rotation_angle)
        sin_rot = math.sin(rotation_angle)
        
        # 元のコードのcos_vp, sin_vpに相当する値（簡略化）
        cos_vp = math.cos(math.atan2(self.vy, self.vx))
        sin_vp = math.sin(math.atan2(self.vy, self.vx))
        
        # 線の描画（元のコードの4本の線を再現）
        self._draw_projectile_lines(screen, cos_vp, sin_vp, r, eye_xr, eye_yr)
    
    def _draw_projectile_lines(self, screen: pygame.Surface, cos_vp: float, sin_vp: float,
                              r: float, eye_xr: float, eye_yr: float):
        """弾の線描画（元のコードの線の描画を再現）"""
        # 元のコードの線描画を簡略化
        center_x, center_y = int(self.x), int(self.y)
        
        # 4本の線を描画（元のコードの複雑な計算を簡略化）
        line_length = r / 4
        angles = [0, math.pi/2, math.pi, 3*math.pi/2]
        
        for angle in angles:
            start_x = center_x + line_length * math.cos(angle)
            start_y = center_y + line_length * math.sin(angle)
            end_x = center_x + (line_length / 2) * math.cos(angle + math.pi/4)
            end_y = center_y + (line_length / 2) * math.sin(angle + math.pi/4)
            
            pygame.draw.line(screen, Colors.BLACK, 
                           (int(start_x), int(start_y)), 
                           (int(end_x), int(end_y)), 2)

class ProjectileManager:
    """弾管理クラス"""
    
    def __init__(self):
        self.projectiles = []
        self.max_projectiles = 3
    
    def add_projectile(self, x: float, y: float, vx: float, vy: float,
                      cos_angle: float, sin_angle: float):
        """新しい弾を追加"""
        # 最大数を超えた場合は古い弾を削除
        if len(self.projectiles) >= self.max_projectiles:
            self.projectiles.pop(0)
        
        projectile = Projectile(x, y, vx, vy, cos_angle, sin_angle)
        self.projectiles.append(projectile)
    
    def update(self):
        """全ての弾を更新"""
        # アクティブでない弾を削除
        self.projectiles = [p for p in self.projectiles if p.active]
        
        # 残りの弾を更新
        for projectile in self.projectiles:
            projectile.update()
    
    def draw(self, screen: pygame.Surface):
        """全ての弾を描画"""
        for projectile in self.projectiles:
            projectile.draw(screen)
    
    def get_projectiles(self):
        """アクティブな弾のリストを取得"""
        return [p for p in self.projectiles if p.active]
    
    def clear(self):
        """全ての弾を削除"""
        self.projectiles.clear()