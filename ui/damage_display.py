"""
ダメージ表示システム
"""
import pygame
import math
from typing import List, Optional
from utils.math_utils import Vector2
from config.settings import Colors, GameConfig


class DamageText:
    """ダメージテキスト表示クラス"""
    
    def __init__(self, x: float, y: float, damage: int):
        self.position = Vector2(x, y)
        self.damage = damage
        self.timer = 0
        self.max_time = 120  # 2秒間表示
        self.active = True
        
        # 浮上アニメーション
        self.velocity = Vector2(0, -1.5)  # 上に浮上
        self.fade_alpha = 255
        
    def update(self, dt: float):
        """ダメージテキストの更新"""
        if not self.active:
            return
            
        self.timer += dt * 60
        
        # 位置の更新
        self.position += self.velocity * dt * 60
        
        # フェードアウト
        fade_ratio = self.timer / self.max_time
        self.fade_alpha = max(0, int(255 * (1 - fade_ratio)))
        
        # 時間経過で非アクティブ化
        if self.timer >= self.max_time:
            self.active = False
    
    def render(self, screen: pygame.Surface, font: pygame.font.Font):
        """ダメージテキストの描画"""
        if not self.active or self.fade_alpha <= 0:
            return
            
        # ダメージの色決定（大ダメージほど赤く）
        if self.damage >= 10:
            color = (255, 50, 50, self.fade_alpha)  # 赤
        elif self.damage >= 5:
            color = (255, 150, 50, self.fade_alpha)  # オレンジ
        else:
            color = (255, 255, 100, self.fade_alpha)  # 黄
            
        # テキスト作成
        damage_text = font.render(str(self.damage), True, color[:3])
        
        # アルファブレンディング適用
        temp_surface = pygame.Surface(damage_text.get_size(), pygame.SRCALPHA)
        temp_surface.set_alpha(self.fade_alpha)
        temp_surface.blit(damage_text, (0, 0))
        
        # 描画
        text_rect = temp_surface.get_rect(center=(int(self.position.x), int(self.position.y)))
        screen.blit(temp_surface, text_rect)


class DamageDisplayManager:
    """ダメージ表示管理クラス - 元のhit_demageシステム"""
    
    def __init__(self):
        self.damage_texts: List[DamageText] = []
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 36)
        
        # 元のhit_place_x, hit_place_y, hit_demage相当
        self.hit_place_x = 0
        self.hit_place_y = 0
        self.hit_damage = 0
        
    def add_damage_text(self, x: float, y: float, damage: int):
        """ダメージテキストを追加 - 元のhit_demage表示"""
        self.hit_place_x = x
        self.hit_place_y = y
        self.hit_damage = damage
        
        # ダメージテキスト作成
        damage_text = DamageText(x, y - 20, damage)  # 少し上にずらして表示
        self.damage_texts.append(damage_text)
        
    def update(self, dt: float):
        """ダメージ表示の更新"""
        # アクティブなダメージテキストの更新
        for damage_text in self.damage_texts[:]:
            damage_text.update(dt)
            if not damage_text.active:
                self.damage_texts.remove(damage_text)
    
    def render(self, screen: pygame.Surface):
        """ダメージ表示の描画"""
        for damage_text in self.damage_texts:
            font = self.big_font if damage_text.damage >= 10 else self.font
            damage_text.render(screen, font)
    
    def clear(self):
        """全てのダメージ表示をクリア"""
        self.damage_texts.clear()