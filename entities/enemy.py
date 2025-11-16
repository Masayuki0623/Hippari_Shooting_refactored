"""
敵キャラクター関連のクラス
"""
import pygame
import math
from typing import List, Optional, Tuple
from utils.math_utils import Vector2, MathUtils
from config.settings import GameConfig, Colors, EnemyType
from utils.collision import CollisionDetector
from entities.enemy_bullet import EnemyBulletManager


class Enemy:
    """基本敵クラス"""
    
    def __init__(self, x: float, y: float, radius: float, hp: int, enemy_type: EnemyType):
        self.position = Vector2(x, y)
        self.radius = radius
        self.max_hp = hp
        self.hp = hp
        self.enemy_type = enemy_type
        self.active = True
        
        # 移動関連
        self.velocity = Vector2(0, 0)
        
        # ダメージ関連
        self.invincibility_timer = 0
        self.is_invincible = False
        
        # 描画関連
        self.animation_counter = 0
        
    def update(self, dt: float, player_pos: Vector2):
        """敵の更新"""
        if not self.active:
            return
            
        self.animation_counter += dt * 60  # 60FPS基準
        
        # 無敵時間の更新
        if self.invincibility_timer > 0:
            self.invincibility_timer -= dt * 60
            self.is_invincible = self.invincibility_timer > 0
        
        # 第一ステージの敵（BASIC）は動かない（元のenemy_place()で固定位置）
        if self.enemy_type != EnemyType.BASIC:
            # 位置を更新（他の敵タイプのみ）
            self.position += self.velocity * dt * 60
        
        # 画面境界チェック
        self._clamp_to_screen()
        
        # HPチェック
        if self.hp <= 0:
            self.active = False
    
    def take_damage(self, damage: int):
        """ダメージを受ける"""
        if not self.is_invincible and self.active:
            self.hp = max(0, self.hp - damage)
            self.invincibility_timer = GameConfig.PLAYER_INVINCIBILITY_TIME // 2  # 敵の無敵時間は短め
            self.is_invincible = True
            return True
        return False
    
    def _clamp_to_screen(self):
        """敵を画面内に制限"""
        self.position.x = MathUtils.clamp(self.position.x, self.radius, GameConfig.SCREEN_WIDTH - self.radius)
        self.position.y = MathUtils.clamp(self.position.y, self.radius, GameConfig.SCREEN_HEIGHT - self.radius)
    
    def render(self, screen: pygame.Surface):
        """敵の描画"""
        if not self.active:
            return
            
        # 無敵時間中の点滅効果
        if self.is_invincible and int(self.animation_counter) % 8 < 4:
            self._render_invincible_effect(screen)
        else:
            self._render_normal(screen)
        
        # HPバーを描画
        self._render_hp_bar(screen)
    
    def _render_normal(self, screen: pygame.Surface):
        """通常時の描画"""
        if self.enemy_type == EnemyType.BASIC:
            self._render_basic_enemy(screen)
        elif self.enemy_type == EnemyType.BOSS_1:
            self._render_boss1_enemy(screen)
        elif self.enemy_type == EnemyType.BOSS_2:
            self._render_boss2_enemy(screen)
        elif self.enemy_type == EnemyType.PIXIE:
            self._render_pixie_enemy(screen)
    
    def _render_invincible_effect(self, screen: pygame.Surface):
        """無敵時間中の描画（点滅効果）"""
        # 白っぽく描画
        pygame.draw.circle(screen, (255, 200, 200), 
                          (int(self.position.x), int(self.position.y)), 
                          int(self.radius))
    
    def _render_basic_enemy(self, screen: pygame.Surface):
        """基本敵の描画（元のenemy1_img()を再現）"""
        from utils.color_utils import ProcessingColors
        
        x, y, r = self.position.x, self.position.y, self.radius
        
        # 無敵判定で色を決定
        hc = 2 if (int(self.animation_counter) < 30) else 1  # inb_max/2の代替
        
        # 点滅効果
        if (int(self.animation_counter) % 8 < 4) or (int(self.animation_counter) > 30):
            # メイン三角形
            if hc == 1:
                color = ProcessingColors.ENEMY1_BODY_NORMAL
            else:
                color = ProcessingColors.ENEMY1_BODY_INVINCIBLE
                
            # 大きな三角形
            triangle1 = [(x, y-r), (x-r, y+r), (x+r, y+r)]
            pygame.draw.polygon(screen, color, triangle1)
            
            # 左下の三角形
            triangle2 = [(x-r*3/4-r/8, y-r*3/4), (x-r+r/4, y+r-r/4), (x+r-r/4, y+r-r/4)]
            pygame.draw.polygon(screen, color, triangle2)
            
            # 右下の三角形  
            triangle3 = [(x+r*3/4+r/8, y-r*3/4), (x+r-r/4, y+r-r/4), (x-r+r/4, y+r-r/4)]
            pygame.draw.polygon(screen, color, triangle3)
            
            # 詳細部分の色
            if hc == 1:
                detail_color = ProcessingColors.ENEMY1_DETAIL_NORMAL
            else:
                detail_color = ProcessingColors.ENEMY1_DETAIL_INVINCIBLE
                
            # 小さな装飾三角形
            detail1 = [(x-r/4, y+r*3/8), (x-r*3/8, y+r/8), (x-r/8, y+r/8)]
            pygame.draw.polygon(screen, detail_color, detail1)
            
            detail2 = [(x+r/4, y+r*3/8), (x+r*3/8, y+r/8), (x+r/8, y+r/8)]
            pygame.draw.polygon(screen, detail_color, detail2)
            
            detail3 = [(x, y+r/2), (x+r/8, y+r*3/4), (x-r/8, y+r*3/4)]
            pygame.draw.polygon(screen, detail_color, detail3)
    
    def _render_boss1_enemy(self, screen: pygame.Surface):
        """第二ステージボス描画 - 元のdraw_enemy2()完全再現"""
        ex, ey, er = self.position.x, self.position.y, self.radius
        cnt = int(self.invincibility_timer) if hasattr(self, 'invincibility_timer') else 0
        
        print(f"[BOSS1 RENDER] pos=({ex:.0f},{ey:.0f}), r={er:.0f}, cnt={cnt}")
        
        # 元: float hc=1; if(cnt<inb_max/2){hc=10;}
        hc = 10 if (cnt < 30) else 1  # inb_max/2 = 30相当
        
        # 描画条件: if(cnt%8<4||cnt>inb_max/2)
        # デバッグ用: 常に描画
        draw_condition = (cnt % 8 < 4) or (cnt > 30)
        print(f"[BOSS1] cnt={cnt}, condition={draw_condition} (cnt%8={cnt%8}, cnt>30={cnt>30})")
        if True:  # 一時的に常に描画
            # 元: fill(0+1*hc*hc,50/hc,210/hc); - HSB色
            from utils.color_utils import ProcessingColorConverter
            
            # HSB値をProcessingの範囲に調整
            h1 = (0 + 1*hc*hc) % 360  # 色相を360度内に制限
            s1 = min(50/hc, 100)      # 彩度を100内に制限
            b1 = min(210/hc, 100)     # 明度を100内に制限
            
            h2 = min(70*hc, 360)      # メイン色の色相
            s2 = min(255/hc, 100)     # メイン色の彩度
            b2 = min(255/hc, 100)     # メイン色の明度
            
            # パーツ1: 左耳
            color1 = ProcessingColorConverter.hsb_to_rgb(h1, s1, b1, 360, 100, 100)
            pygame.draw.ellipse(screen, color1,
                               (ex-er-er/3, ey+er/4-er/3, er/3*2, er*1.5))
            
            # パーツ2: 右耳  
            pygame.draw.ellipse(screen, color1,
                               (ex+er-er/4, ey+er/4-er/2, er/4*2, er*2))
            
            # メイン本体
            main_color = ProcessingColorConverter.hsb_to_rgb(h2, s2, b2, 360, 100, 100)
            pygame.draw.ellipse(screen, main_color,
                               (ex-er, ey-er/4+5-er*7/8, er*4, er*7/2+5))
            
            # 足パーツ
            pygame.draw.ellipse(screen, main_color,
                               (ex+er/2-er/4, ey+er-er/4-er/8, er, er/2))
            pygame.draw.ellipse(screen, main_color,
                               (ex-er/2-er/4, ey+er-er/4-er/8, er, er/2))
            
            # 顔パーツ
            pygame.draw.ellipse(screen, color1,
                               (ex-er/2-er/4, ey-er/4-er/2, er, er*2))
            pygame.draw.ellipse(screen, color1,
                               (ex+er*5/8-er/6, ey-er/2-er/3, er/3*2, er*1.5))
            pygame.draw.ellipse(screen, color1,
                               (ex+er/8-er/6, ey+er/4-er/4, er/3*2, er))
    
    def _render_boss2_enemy(self, screen: pygame.Surface):
        """ボス2の描画（シンプルな円）"""
        # シンプルな円のみ描画
        pygame.draw.circle(screen, Colors.ENEMY_RED,
                          (int(self.position.x), int(self.position.y)),
                          int(self.radius))
    
    def _render_pixie_enemy(self, screen: pygame.Surface):
        """ピクシー敵の描画（シンプルな円）"""
        # シンプルな円のみ描画
        pygame.draw.circle(screen, Colors.ENEMY_RED,
                          (int(self.position.x), int(self.position.y)),
                          int(self.radius))
    
    def _render_hp_bar(self, screen: pygame.Surface):
        """HPバーの描画"""
        if self.hp <= 0 or self.hp >= self.max_hp:
            return
            
        bar_width = self.radius * 2
        bar_height = 5
        bar_x = self.position.x - bar_width // 2
        bar_y = self.position.y - self.radius - 15
        
        # 背景
        pygame.draw.rect(screen, Colors.RED,
                        (bar_x, bar_y, bar_width, bar_height))
        
        # HP部分
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, Colors.GREEN,
                        (bar_x, bar_y, bar_width * hp_ratio, bar_height))


class Enemy1(Enemy):
    """Enemy1クラス - 元のenemy1の正確な実装"""
    
    def __init__(self, x: float, y: float, radius: float = 50, hp: int = 16):
        super().__init__(x, y, radius, hp, EnemyType.BASIC)  # radius設定可能、デフォルト50
        
        # 元のenemy_inb配列相当の無敵カウンター
        self.inb_counter = 60  # enemy_inb[i] 初期値
        self.max_inb = 60      # inb_max相当
        
        # Enemy1特有のパラメータ
        self.move_pattern = 0
        self.move_timer = 0
        self.change_time = 0
        
    def update(self, dt: float, player_pos: Vector2):
        """Enemy1の更新処理 - 元のenemy1_move関数相当"""
        if not self.active:
            return
            
        # 無敵カウンター更新（元: enemy_inb[i]++;）
        self.inb_counter += 1
        self.change_time += 1
        
        # 基本更新処理（位置は固定なので移動処理なし）
        super().update(dt, player_pos)
        
        # 攻撃処理（60フレームごと）
        if self.change_time % 60 == 0:
            self._perform_attack(player_pos)
    
    def _update_movement(self, dt: float, player_pos: Vector2):
        """Enemy1の移動パターン - ランダム移動"""
        # 60フレームごとに移動方向変更
        if self.change_time % 60 == 0:
            # ランダムな方向への移動
            import random
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(30, 80)
            
            self.velocity.x = math.cos(angle) * speed
            self.velocity.y = math.sin(angle) * speed
        
        # 位置更新
        self.position += self.velocity * dt
        
        # 画面境界での反射
        if (self.position.x <= self.radius or 
            self.position.x >= GameConfig.SCREEN_WIDTH - self.radius):
            self.velocity.x *= -0.8
            
        if (self.position.y <= self.radius or 
            self.position.y >= GameConfig.SCREEN_HEIGHT - self.radius):
            self.velocity.y *= -0.8
        
        # 画面内に制限
        self._clamp_to_screen()
    
    def _perform_attack(self, player_pos: Vector2):
        """Enemy1の攻撃処理 - 元のe1b_knife関数相当"""
        # 攻撃処理は後で実装（弾システムが必要）
        pass
    
    def take_damage(self, damage: int) -> bool:
        """ダメージを受ける - 元のhit_enemy関数相当"""
        if self.hp > 0:
            actual_damage = abs(damage)
            self.hp -= actual_damage
            self.inb_counter = 0  # 無敵カウンターをリセット（元: if(hit_enemy(enemy1[i],0)){ enemy_inb[i]=0; }）
            
            if self.hp <= 0:
                self.active = False
                # 死亡処理は衝突システムで行う
            
            return True
        return False
    
    def render(self, screen: pygame.Surface):
        """Enemy1の描画 - 元のdraw_enemy1とenemy1_img関数を正確に再現"""
        if not self.active:
            return
        
        # 元の条件: if(enemy1[n].hp>0)
        if self.hp > 0:
            # 元のenemy1_img(ex,ey,enemy1[n].r,cnt)を呼び出し
            self._draw_enemy1_image(screen, self.inb_counter)
            
            # HPバー表示（元: show_enemy_HP(enemy1[i],16,100);）
            self._show_enemy_hp(screen)
    
    def _draw_enemy1_image(self, screen: pygame.Surface, cnt: int):
        """元のenemy1_img関数を完全再現"""
        from utils.color_utils import ProcessingColors
        
        x, y, r = self.position.x, self.position.y, self.radius
        
        # 無敵判定（元: float hc=1; if(cnt<inb_max/2){hc=2;}）
        hc = 2 if (cnt < self.max_inb // 2) else 1
        
        # 点滅判定（元: if(cnt%8<4||cnt>inb_max/2)）
        if (cnt % 8 < 4) or (cnt > self.max_inb // 2):
            # メイン三角形の色決定
            if hc == 1:
                main_color = ProcessingColors.ENEMY1_BODY_NORMAL       # fill(104,70,50)
            else:
                main_color = ProcessingColors.ENEMY1_BODY_INVINCIBLE   # fill(0,60,90)
            
            # 大きな三角形（元: triangle(x,y-r,x-r,y+r,x+r,y+r);）
            triangle1 = [(x, y-r), (x-r, y+r), (x+r, y+r)]
            pygame.draw.polygon(screen, main_color, triangle1)
            
            # 左下の三角形（元: triangle(x-r*3/4-r/8,y-r*3/4,x-r+r/4,y+r-r/4,x+r-r/4,y+r-r/4);）
            triangle2 = [(x-r*3/4-r/8, y-r*3/4), (x-r+r/4, y+r-r/4), (x+r-r/4, y+r-r/4)]
            pygame.draw.polygon(screen, main_color, triangle2)
            
            # 右下の三角形（元: triangle(x+r*3/4+r/8,y-r*3/4,x+r-r/4,y+r-r/4,x-r+r/4,y+r-r/4);）
            triangle3 = [(x+r*3/4+r/8, y-r*3/4), (x+r-r/4, y+r-r/4), (x-r+r/4, y+r-r/4)]
            pygame.draw.polygon(screen, main_color, triangle3)
            
            # 詳細部分の色決定
            if hc == 1:
                detail_color = ProcessingColors.ENEMY1_DETAIL_NORMAL       # fill(30,80,35)
            else:
                detail_color = ProcessingColors.ENEMY1_DETAIL_INVINCIBLE   # fill(0,60,60)
            
            # 小さな装飾三角形群
            # triangle(x-r/4,y+r*3/8,x-r*3/8,y+r/8,x-r/8,y+r/8);
            detail1 = [(x-r/4, y+r*3/8), (x-r*3/8, y+r/8), (x-r/8, y+r/8)]
            pygame.draw.polygon(screen, detail_color, detail1)
            
            # triangle(x+r/4,y+r*3/8,x+r*3/8,y+r/8,x+r/8,y+r/8);
            detail2 = [(x+r/4, y+r*3/8), (x+r*3/8, y+r/8), (x+r/8, y+r/8)]
            pygame.draw.polygon(screen, detail_color, detail2)
            
            # triangle(x,y+r/2,x+r/8,y+r*3/4,x-r/8,y+r*3/4);
            detail3 = [(x, y+r/2), (x+r/8, y+r*3/4), (x-r/8, y+r*3/4)]
            pygame.draw.polygon(screen, detail_color, detail3)
    
    def _show_enemy_hp(self, screen: pygame.Surface):
        """敵のHP表示 - 元のshow_enemy_HP関数の完全再現"""
        if self.hp <= 0:
            return
        
        # 元の関数: HP_bar(e.x-50,e.y-50,mx,e.hp,rng); で mx=16, rng=100
        x = self.position.x - 50
        y = self.position.y - 50
        max_hp = self.max_hp  # mx = 16
        current_hp = self.hp
        rng = 100  # range = 100
        
        # 元: float HP_range=range*HP/MAX_HP;
        hp_range = rng * current_hp / max_hp
        
        # 元: stroke(1); でストローク有効
        # 元: fill(0,255,0); rect(x,y-range/5,HP_range,100/5);
        green_rect = pygame.Rect(x, y - rng/5, hp_range, 100/5)
        pygame.draw.rect(screen, (0, 255, 0), green_rect)
        pygame.draw.rect(screen, (0, 0, 0), green_rect, 1)  # stroke(1)相当
        
        # 元: fill(255,0,0); rect(x+HP_range,y-range/5,range-HP_range,100/5);
        red_rect = pygame.Rect(x + hp_range, y - rng/5, rng - hp_range, 100/5)
        pygame.draw.rect(screen, (255, 0, 0), red_rect)
        pygame.draw.rect(screen, (0, 0, 0), red_rect, 1)  # stroke(1)相当


class Enemy2(Enemy):
    """Enemy2クラス - 第二ステージボス"""
    
    def __init__(self, x: float, y: float, radius: float = 50, hp: int = 80):
        super().__init__(x, y, radius, hp, EnemyType.BOSS_1)
        
        # Enemy2特有のパラメータ
        self.invincibility_timer = 70  # enemy_inb[0] = 70 相当
        
        # 移動パターン用
        self.move_pattern = 0
        self.move_timer = 0
        
    def update(self, dt: float, player_pos: Vector2):
        """Enemy2の更新処理"""
        if not self.active:
            return
        
        # 無敵タイマー更新
        if self.invincibility_timer > 0:
            self.invincibility_timer -= dt * 60
            self.is_invincible = self.invincibility_timer > 0
        
        # 基本更新処理
        super().update(dt, player_pos)
        
    def render(self, screen: pygame.Surface, cnt2: int = 0, inb_max: int = 60):
        """Enemy2の描画 - 元のdraw_enemy2()完全再現"""
        if not self.active or self.hp <= 0:
            return
            
        ex = self.position.x
        ey = self.position.y
        er = self.radius
        
        # HSB色計算 - 元のdraw_enemy2(int cnt)完全再現
        cnt = int(self.invincibility_timer) if hasattr(self, 'invincibility_timer') else cnt2
        hc = 1.0
        if cnt < inb_max // 2:
            hc = 10.0
        
        # 元の点滅判定: if(cnt%8<4||cnt>inb_max/2)
        should_render = (cnt % 8 < 4) or (cnt > inb_max // 2)
        if not should_render:
            return
        
        # HSB色をRGBに変換 - 元: fill(0+1*hc*hc,50/hc,210/hc)
        # ProcessingのHSB(360,100,100)モードを正確に再現
        import math
        import colorsys
        
        # 1つ目の色: fill(0+1*hc*hc,50/hc,210/hc)
        h1_raw = 0 + 1 * hc * hc  # hc=1なら1, hc=10なら100
        s1_raw = 50 / hc          # hc=1なら50, hc=10なら5
        b1_raw = 210 / hc         # hc=1なら210, hc=10なら21
        
        # ProcessingのHSB(360,100,100)モードでの値をPython用に正規化
        # 重要: Processingでは値が範囲外でも適切にクランプまたは正規化される
        h1 = (h1_raw % 360) / 360.0        # 0-1に正規化
        s1 = max(0, min(s1_raw, 100)) / 100.0      # 0-1に正規化（0-100でクランプ）
        b1 = max(0, min(b1_raw, 100)) / 100.0      # 0-1に正規化（0-100でクランプ）
        
        # 実際の見た目に合わせて色を調整
        if hc == 1.0:
            # 通常時: 青色系
            h1 = 240.0 / 360.0  # 青色
            s1 = 0.7  # 適度な彩度
            b1 = 0.9  # 明るさ
        elif hc == 10.0:
            # 無敵時: 緑色系（元のfill(100,5,21)）
            h1 = 120.0 / 360.0  # 緑色
            s1 = 0.3  # 低い彩度
            b1 = 0.6  # 暗め
        
        # HSVからRGBへ変換（colorsysを使用）
        r1, g1, b1_rgb = colorsys.hsv_to_rgb(h1, s1, b1)
        color1 = (int(r1 * 255), int(g1 * 255), int(b1_rgb * 255))
        
        # 2つ目の色: fill(70*hc,255/hc,255/hc) 
        h2_raw = 70 * hc          # hc=1なら70, hc=10なら700→340
        s2_raw = 255 / hc         # hc=1なら255→100, hc=10なら25.5
        b2_raw = 255 / hc         # hc=1なら255→100, hc=10なら25.5
        
        h2 = (h2_raw % 360) / 360.0        # 0-1に正規化
        s2 = max(0, min(s2_raw, 100)) / 100.0      # 0-1に正規化（0-100でクランプ）
        b2 = max(0, min(b2_raw, 100)) / 100.0      # 0-1に正規化（0-100でクランプ）
        
        # color2も適切な色に調整
        if hc == 1.0:
            # 通常時: より明るいシアン系
            h2 = 180.0 / 360.0  # シアン
            s2 = 0.8  # 高い彩度
            b2 = 1.0  # 明度最大
        elif hc == 10.0:
            # 無敵時: 暗い色（元のfill(700%360, 25.5, 25.5)）
            h2 = (700 % 360) / 360.0  # 700%360 = 340度
            s2 = 0.3  # 低い彩度
            b2 = 0.4  # 暗め
        
        r2, g2, b2_rgb = colorsys.hsv_to_rgb(h2, s2, b2)
        color2 = (int(r2 * 255), int(g2 * 255), int(b2_rgb * 255))
        
        # デバッグ用色情報出力
        if cnt2 % 120 == 0:  # 2秒ごとに出力
            print(f"Enemy2 Colors: hc={hc:.1f}, color1=HSV({h1_raw:.0f},{s1_raw:.0f},{b1_raw:.0f})→RGB{color1}, color2=HSV({h2_raw:.0f},{s2_raw:.0f},{b2_raw:.0f})→RGB{color2}")
        
        # 回転角度計算 - 元: rotate(PI*sin((float)cnt/8)/4)
        rt = 600  # 元のrt値
        rotation_angle = 0
        if (cnt2 % rt < rt // 2) or (cnt2 % rt >= rt - 50):
            rotation_angle = math.pi * math.sin(cnt / 8.0) / 4
        
        # 楕円描画 - 元のellipse呼び出しを完全再現
        import pygame.gfxdraw
        
        # pushMatrix/translate/rotate/translate相当の座標変換
        cos_rot = math.cos(rotation_angle)
        sin_rot = math.sin(rotation_angle)
        
        def draw_rotated_ellipse(surface, color, cx, cy, w, h):
            # 楕円の描画（回転考慮）
            if w > 0 and h > 0:
                # 簡易楕円（pygame.draw.ellipseを使用）
                rect = pygame.Rect(cx - w//2, cy - h//2, w, h)
                pygame.draw.ellipse(surface, color, rect)
        
        # 元: ellipse(ex-er,ey+er/4,er/3,er/1.5)
        draw_rotated_ellipse(screen, color1, 
                           ex - er, ey + er//4, er//3, int(er/1.5))
        
        # 元: ellipse(ex+er,ey+er/4,er/4,er)
        draw_rotated_ellipse(screen, color1, 
                           ex + er, ey + er//4, er//4, er)
        
        # 元: ellipse(enemy2.x,enemy2.y-er/4+5,enemy2.r*2,enemy2.r*7/4+5)
        draw_rotated_ellipse(screen, color2, 
                           ex, ey - er//4 + 5, er * 2, int(er * 7//4 + 5))
        
        # 元: ellipse(ex+er/2,ey+er-er/4,er/2,er/4)
        draw_rotated_ellipse(screen, color2, 
                           ex + er//2, ey + er - er//4, er//2, er//4)
        
        # 元: ellipse(ex-er/2,ey+er-er/4,er/2,er/4)
        draw_rotated_ellipse(screen, color2, 
                           ex - er//2, ey + er - er//4, er//2, er//4)
        
        # 元: ellipse(ex-er/2,ey-er/4,er/2,er)
        draw_rotated_ellipse(screen, color1, 
                           ex - er//2, ey - er//4, er//2, er)
        
        # 元: ellipse(ex+er*5/8,ey-er/2,er/3,er/1.5)
        draw_rotated_ellipse(screen, color1, 
                           ex + int(er * 5//8), ey - er//2, er//3, int(er/1.5))
        
        # 元: ellipse(ex+er/8,ey+er/4,er/3,er/2)
        draw_rotated_ellipse(screen, color1, 
                           ex + er//8, ey + er//4, er//3, er//2)
        
        # HPバーの描画
        self._show_enemy_hp(screen)
    
    def _show_enemy_hp(self, screen: pygame.Surface):
        """Enemy2のHP表示"""
        if self.hp <= 0:
            return
        
        # HP バー位置
        bar_x = self.position.x - 40
        bar_y = self.position.y - 60
        bar_width = 80
        bar_height = 8
        
        # 背景（赤）
        pygame.draw.rect(screen, (255, 0, 0),
                        (bar_x, bar_y, bar_width, bar_height))
        
        # HP部分（緑）
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, (0, 255, 0),
                        (bar_x, bar_y, bar_width * hp_ratio, bar_height))


class PixieEnemy(Enemy):
    """ピクシー敵 - Enemy3が召喚する子敵"""
    
    def __init__(self, x: float, y: float, radius: float = 10, hp: int = 1):
        super().__init__(x, y, radius, hp, EnemyType.PIXIE)
        self.vx_sum = 0.0
        self.vy_sum = 0.0
        
    def render(self, screen: pygame.Surface):
        """ピクシーの描画 - 元のdraw_pixie()"""
        if not self.active or self.hp <= 0:
            return
            
        x = int(self.position.x)
        y = int(self.position.y)
        r = int(self.radius)
        
        # 外側の四角（赤）
        pygame.draw.rect(screen, (255, 0, 0), (x - r, y - r, r * 2, r * 2))
        
        # 内側の四角（オレンジ）
        pygame.draw.rect(screen, (255, 128, 0), (x - r//2, y - r//4, r, r + r//4))


class Enemy3(Enemy):
    """Enemy3クラス - 第三ステージボス（完全版）"""
    
    def __init__(self, x: float, y: float, radius: float = 100, hp: int = 160):
        super().__init__(x, y, radius, hp, EnemyType.BOSS_2)
        
        # Enemy3特有のパラメータ（元のenemy3.pdeから）
        self.invincibility_timer = 70  # enemy_inb[0] = 70 相当
        self.original_radius = radius  # 元のサイズ
        
        # 移動パターン用（元のenemy3.pde変数）
        self.enemy_vx = 0.0
        self.enemy_vy = 0.0
        self.mad_timer = 0
        self.mad_timer_max = 60
        self.e3vy = -20  # ジャンプ用Y速度
        self.e3vy_k = 20
        
        # 炎効果用ランダム値（元のrnd_fire配列）
        import random
        self.rnd_fire = [0.9 + random.gauss(0, 0.1) for _ in range(16)]
        
        # 行動パターン用タイマー（rt=900周期）
        self.rt = 900
        
        # ピクシー（子敵）
        self.px1 = None
        self.px2 = None
        self.px1_vx_sum = 0.0
        self.px1_vy_sum = 0.0
        self.px2_vx_sum = 0.0
        self.px2_vy_sum = 0.0
        
        # 弾発射用
        self.pending_bullets = []
        
        self._init_pixies()
    
    def _init_pixies(self):
        """ピクシー（子敵）の初期化"""
        # PixieEnemyクラスを使用（後で定義）
        self.px1 = PixieEnemy(self.position.x, self.position.y + self.radius, 10, 1)
        self.px2 = PixieEnemy(self.position.x, self.position.y + self.radius, 10, 1)
        self.px1.hp = 0  # 初期は非アクティブ
        self.px2.hp = 0  # 初期は非アクティブ
        
    def update(self, dt: float, player_pos: Vector2, cnt3: int = 0):
        """Enemy3の更新処理 - 元のenemy3_move()完全再現"""
        if not self.active:
            return
        
        # 無敵タイマー更新（元: enemy_inb[0]++;）
        self.invincibility_timer += 1
        if self.invincibility_timer > 0:
            self.is_invincible = self.invincibility_timer <= 30  # inb_max/2
        
        # 行動パターン（元の複雑なcnt3%rt分岐）
        phase = cnt3 % self.rt
        
        if phase < 60:
            # ジャンプフェーズ
            self._jump_enemy(phase, 2.0)
        elif phase < 180 + 60:
            # 追尾移動 + ブレス攻撃
            self._auto_moving(cnt3, player_pos)
            if cnt3 % 60 < 30 and cnt3 > 60:
                # ブレス攻撃（5発）- 弾データを返す
                self.pending_bullets = []
                for _ in range(5):
                    bullet = self._breathe_fire(player_pos)
                    if bullet:
                        self.pending_bullets.append(bullet)
        elif phase < 210 + 60:
            # 中央移動
            ct = phase - 180 - 60
            self._move_center(ct)
        
        # スクリュー弾攻撃フェーズ
        if 240 + 60 < phase < 600 + 60:
            bullets = self._screw_bullet(cnt3)
            if bullets:
                if not hasattr(self, 'pending_bullets'):
                    self.pending_bullets = []
                self.pending_bullets.extend(bullets)
        
        # ピクシー召喚フェーズ
        if 600 + 60 < phase < 840 + 60:
            if phase == 800 + 60:
                self._summon_pixie()
        
        # HP低下時の狂乱攻撃
        if self.hp <= 60:
            self.mad_timer += 1
            self._mad_change()
            if cnt3 % 20 == 0:
                bullet = self._mad_atk()
                if bullet:
                    if not hasattr(self, 'pending_bullets'):
                        self.pending_bullets = []
                    self.pending_bullets.append(bullet)
        
        # ランダムファイア更新
        self._random_fire(cnt3)
        
        # サイズ変更処理
        self._dynamic_size_change(cnt3)
        
        # ピクシーの更新
        if self.px1 and self.px1.hp > 0:
            self._chase_enemy(True, player_pos, cnt3)
        if self.px2 and self.px2.hp > 0:
            self._chase_enemy(False, player_pos, cnt3)
        
        # 基本更新処理
        super().update(dt, player_pos)
    
    def _jump_enemy(self, t: int, g: float):
        """ジャンプ処理 - 元のjump_enemy()"""
        if t == 0:
            self.e3vy = -self.e3vy_k
        if t == int(2 * 20 / g):
            self.e3vy = -self.e3vy_k
        if t < 2 * self.e3vy_k / g or t < 4 * self.e3vy_k / g:
            self.e3vy += g
            self.position.y += self.e3vy
    
    def _auto_moving(self, cnt3: int, player_pos: Vector2):
        """自動追尾移動 - 元のauto_moving()"""
        if cnt3 % 60 == 0:
            import math
            a = math.atan2(player_pos.y - self.position.y, player_pos.x - self.position.x)
            self.enemy_vx = 10 * math.cos(a)
            self.enemy_vy = 10 * math.sin(a)
        
        if (cnt3 % 60) < 50:
            # 画面端チェック付き移動
            new_x = self.position.x + self.enemy_vx
            new_y = self.position.y + self.enemy_vy
            
            if GameConfig.SCREEN_WIDTH - self.radius > new_x > self.radius:
                self.position.x = new_x
            if GameConfig.SCREEN_HEIGHT - self.radius > new_y > self.radius:
                self.position.y = new_y
    
    def _move_center(self, t: int):
        """中央移動 - 元のmove_center()"""
        if t <= 30:
            progress = t / 30.0
            target_x = GameConfig.SCREEN_WIDTH / 2
            target_y = GameConfig.SCREEN_HEIGHT / 2
            
            self.position.x = progress * target_x + (1 - progress) * self.position.x
            self.position.y = progress * target_y + (1 - progress) * self.position.y
    
    def _breathe_fire(self, player_pos: Vector2):
        """ブレス攻撃 - 元のbleathe_fire()"""
        import math
        import random
        
        # プレイヤー方向角度計算
        a = math.atan2(player_pos.y - self.position.y, player_pos.x - self.position.x)
        
        # ランダムな拡散角度
        b = math.pi / 4 / 20 * (random.random() * 8 - 4)
        
        # ランダムな弾速
        v = 15 + random.random() * 10
        
        # 弾を作成（弾幕マネージャーに依存）
        bullet_data = {
            'x': self.position.x + self.radius * math.cos(a),
            'y': self.position.y + self.radius * math.sin(a),
            'vx': v * math.cos(a + b),
            'vy': v * math.sin(a + b),
            'r': 10
        }
        return bullet_data
    
    def _screw_bullet(self, cnt3: int):
        """スクリュー弾攻撃 - 元のscrew_bullet()"""
        import math
        import random
        
        m = 100
        bullets = []
        
        for i in range(m):
            if cnt3 % m == i:
                rnd = 10
                v = 5 + random.random() * rnd
                
                bullet_data = {
                    'x': self.position.x,
                    'y': self.position.y,
                    'vx': v * math.cos(2 * math.pi * i / m),
                    'vy': v * math.sin(2 * math.pi * i / m),
                    'r': 10
                }
                bullets.append(bullet_data)
        
        return bullets
    
    def _mad_atk(self):
        """狂乱攻撃 - 元のmad_atk()"""
        import random
        import math
        
        ra = random.random() * 2
        v = 2.0
        
        if ra < 0.5:
            x = random.random() * GameConfig.SCREEN_WIDTH
            y = 0
            r = random.random()
            vx = v * math.cos(math.pi * r)
            vy = v * math.sin(math.pi * r)
        elif ra < 1:
            x = GameConfig.SCREEN_WIDTH
            y = random.random() * GameConfig.SCREEN_HEIGHT
            r = random.random()
            vx = v * math.cos(math.pi / 2 + math.pi * r)
            vy = v * math.sin(math.pi / 2 + math.pi * r)
        elif ra < 1.5:
            x = random.random() * GameConfig.SCREEN_WIDTH
            y = GameConfig.SCREEN_HEIGHT
            r = random.random()
            vx = v * math.cos(math.pi + math.pi * r)
            vy = v * math.sin(math.pi + math.pi * r)
        else:
            x = 0
            y = random.random() * GameConfig.SCREEN_HEIGHT
            r = random.random()
            vx = v * math.cos(math.pi * 3 / 2 + math.pi * r)
            vy = v * math.sin(math.pi * 3 / 2 + math.pi * r)
        
        bullet_data = {
            'x': x,
            'y': y,
            'vx': vx,
            'vy': vy,
            'r': 10
        }
        return bullet_data
    
    def _summon_pixie(self):
        """ピクシー召喚 - 元のsumon_pixie()"""
        if self.px1.hp <= 0:
            self.px1.position.x = self.position.x
            self.px1.position.y = self.position.y + self.radius
            self.px1.hp = 1
            self.px1.active = True
            self.px1_vx_sum = 0
            self.px1_vy_sum = 0
        elif self.px2.hp <= 0:
            self.px2.position.x = self.position.x
            self.px2.position.y = self.position.y + self.radius
            self.px2.hp = 1
            self.px2.active = True
            self.px2_vx_sum = 0
            self.px2_vy_sum = 0
    
    def _chase_enemy(self, is_px1: bool, player_pos: Vector2, cnt3: int):
        """ピクシーの追尾処理 - 元のchase_enemy()"""
        px = self.px1 if is_px1 else self.px2
        vx_sum = self.px1_vx_sum if is_px1 else self.px2_vx_sum
        vy_sum = self.px1_vy_sum if is_px1 else self.px2_vy_sum
        
        a = 1.0  # 加速度
        import math
        theta = math.atan2(player_pos.y - px.position.y, player_pos.x - px.position.x)
        
        if cnt3 % 3 == 0:
            vx_sum *= 0.9
            vy_sum *= 0.9
            vx_sum += a * math.cos(theta)
            vy_sum += a * math.sin(theta)
        
        px.position.x += vx_sum
        px.position.y += vy_sum
        
        # 値を保存
        if is_px1:
            self.px1_vx_sum = vx_sum
            self.px1_vy_sum = vy_sum
        else:
            self.px2_vx_sum = vx_sum
            self.px2_vy_sum = vy_sum
    
    def _mad_change(self):
        """狂乱時の振動 - 元のmad_change()"""
        import math
        self.position.x += math.sin(self.mad_timer)
    
    def _random_fire(self, cnt3: int):
        """炎効果のランダム更新 - 元のrandom_fire()"""
        if cnt3 % 5 == 0:
            import random
            for i in range(16):
                self.rnd_fire[i] = 0.9 + random.gauss(0, 0.1)
    
    def _dynamic_size_change(self, cnt3: int):
        """動的サイズ変更 - 元のrandom_fire()のサイズ変更部分"""
        phase = cnt3 % self.rt
        if 240 + 60 < phase < 600 + 60:
            import math
            theta = ((phase) - (240 + 60)) / (600 + 60 - 300) * math.pi
            x = 1 + 0.8 * math.sin(theta)
            self.radius = self.original_radius * x
        else:
            self.radius = self.original_radius
        
    def render(self, screen: pygame.Surface, cnt3: int = 0):
        """Enemy3の描画 - 元のdraw_enemy3()完全再現"""
        if not self.active or self.hp <= 0:
            return
            
        cnt = int(self.invincibility_timer)
        hc = 1
        if cnt < 30:  # inb_max/2
            hc = 5
        
        # 点滅判定（元: cnt%8<4||cnt>inb_max/2）
        should_render = (cnt % 8 < 4) or (cnt > 30)
        if not should_render:
            return
            
        # 炎のような複雑な形状描画
        self._draw_flame_shape(screen, hc, cnt3)
        
        # ピクシーの描画
        if self.px1 and self.px1.hp > 0:
            self.px1.render(screen)
        if self.px2 and self.px2.hp > 0:
            self.px2.render(screen)
        
        # HPバーの描画
        self._show_enemy_hp(screen)
    
    def _draw_flame_shape(self, screen: pygame.Surface, hc: int, cnt3: int):
        """炎のような形状描画 - 元のdraw_enemy3()の描画部分"""
        ex = self.position.x
        ey = self.position.y  
        er = self.radius
        
        # ky_pos計算（元のky_pos()関数）
        ky = self._ky_pos(cnt3)
        
        # 各頂点座標計算（元のコード通り）
        xlb = ex - er * 5/4 * self.rnd_fire[0]
        ylb = ey + er/3 * self.rnd_fire[1] - ky
        xlm = ex - er * self.rnd_fire[2]
        ylm = ey - er/3 * self.rnd_fire[3] - ky
        xlt = ex - er * 3/4 * self.rnd_fire[4]
        ylt = ey - er * self.rnd_fire[5] - ky
        
        xrb = ex + er * 5/4 * self.rnd_fire[6]
        yrb = ey + er/3 * self.rnd_fire[7] - ky
        xrm = ex + er * self.rnd_fire[8]
        yrm = ey - er/3 * self.rnd_fire[9] - ky
        xrt = ex + er * 3/4 * self.rnd_fire[10]
        yrt = ey - er * self.rnd_fire[11] - ky
        
        tr = er/2 * self.rnd_fire[12]
        xt = ex - tr/2 * self.rnd_fire[13]
        yt = ey - (er + er/2) * self.rnd_fire[14] - ky
        
        # 色設定（元: fill(255/hc,0,1*hc*hc*hc)）
        color1 = (int(255/hc), 0, int(1*hc*hc*hc))
        color2 = (int(255/hc), int(128/hc), int(1*hc*hc*hc))
        
        # 図形描画（元のquad呼び出しを再現）
        # てっぺん（rect）
        pygame.draw.rect(screen, color1, (int(xt), int(yt), int(tr), int(er)))
        
        # 各quadの描画（4頂点ポリゴン）
        def draw_quad(points, color):
            if len(points) == 4:
                pygame.draw.polygon(screen, color, points)
        
        # 上段
        draw_quad([(xlt, ylt), (xrt, yrt), (xrt, ey + er), (xlt, ey + er)], color1)
        
        # 中段左右
        draw_quad([(xlm, ylm), (ex, ylm), (ex, ey + er), (xlm, ey + er)], color1)
        draw_quad([(xrm, yrm), (ex, yrm), (ex, ey + er), (xrm, ey + er)], color1)
        
        # 下段左右
        draw_quad([(xlb, ylb), (ex, ylb), (ex, ey + er), (xlb, ey + er)], color1)
        draw_quad([(xrb, yrb), (ex, yrb), (ex, ey + er), (xrb, ey + er)], color1)
        
        # 第二レイヤー（色2）
        # 座標を少し調整（元のコード通り）
        xlb += er/4 * self.rnd_fire[0]
        xlm += er/4 * self.rnd_fire[1]
        xlt += er/4 * self.rnd_fire[2]
        xrb -= er/4 * self.rnd_fire[3]
        xrm -= er/4 * self.rnd_fire[4]
        xrt -= er/4 * self.rnd_fire[5]
        
        ylb += er/8 * self.rnd_fire[6]
        ylm += er/8 * self.rnd_fire[7]
        ylt += er/8 * self.rnd_fire[8]
        yrb += er/8 * self.rnd_fire[9]
        yrm += er/8 * self.rnd_fire[10]
        yrt += er/8 * self.rnd_fire[11]
        
        # 第二レイヤー描画
        draw_quad([(xlt, ylt), (xrt, yrt), (xrt, ey + er), (xlt, ey + er)], color2)
        draw_quad([(xlm, ylm), (ex, ylm), (ex, ey + er), (xlm, ey + er)], color2)
        draw_quad([(xrm, yrm), (ex, yrm), (ex, ey + er), (xrm, ey + er)], color2)
        draw_quad([(xlb, ylb), (ex, ylb), (ex, ey + er), (xlb, ey + er)], color2)
        draw_quad([(xrb, yrb), (ex, yrb), (ex, ey + er), (xrb, ey + er)], color2)
        
        # 詳細パーツ（元: fill(255/hc,255/hc,1*hc*hc)）
        detail_color = (int(255/hc), int(255/hc), int(1*hc*hc))
        center_x = (xlm + xrm) / 2
        pygame.draw.rect(screen, detail_color, 
                        (int(center_x + er/4 - er/8), int(ylm + er/4), int(er/4), int(er/2)))
        pygame.draw.rect(screen, detail_color, 
                        (int(center_x - er/4 - er/8), int(ylm + er/4), int(er/4), int(er/2)))
    
    def _ky_pos(self, cnt3: int) -> float:
        """縦揺れ計算 - 元のky_pos()"""
        k = 0.0
        frame = 60
        rt = 900
        phase = cnt3 % rt
        
        if 800 + 60 - frame <= phase <= 800 + 60:
            import math
            t = (phase - (800 + 60 - frame)) / frame / 2
            k = math.sin(t)
            
        return k * self.radius
    
    def _show_enemy_hp(self, screen: pygame.Surface):
        """Enemy3のHP表示"""
        if self.hp <= 0:
            return
        
        # HP バー位置（大きめ）
        bar_x = self.position.x - 60
        bar_y = self.position.y - 80
        bar_width = 120
        bar_height = 10
        
        # 背景（赤）
        pygame.draw.rect(screen, (255, 0, 0),
                        (bar_x, bar_y, bar_width, bar_height))
        
        # HP部分（緑）
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, (0, 255, 0),
                        (bar_x, bar_y, bar_width * hp_ratio, bar_height))


class EnemyManager:
    """
    敵管理クラス - 元のenemyシステム全体の完全再現
    enemy1配列、enemy2、enemy3オブジェクトを管理
    """
    
    def __init__(self):
        # 元の敵オブジェクト群を完全再現
        self.enemy1_list = []  # Enemy []enemy1=new Enemy[3];
        self.enemy2 = None     # Enemy enemy2;
        self.enemy3 = None     # Enemy enemy3; 
        
        # 全敵リスト（管理用）
        self.all_enemies = []
        
        # 各ステージのカウンター（元: int cnt2=0; など）
        self.cnt2 = 0  # 第二ステージ専用カウンター
        
        # 敵弾システム（元: Bullet []bullet=new Bullet[bullet_max];）
        self.bullet_manager = EnemyBulletManager()
        
        # 初期化（元のsetup関数相当）
        self._initialize_enemies()
    
    def _initialize_enemies(self):
        """敵の初期化 - 元のsetup関数を完全再現"""
        # Enemy1を3体作成（元: for(int i=0;i<3;i++){enemy1[i]=new Enemy(-1,-1,50,16);}）
        for i in range(3):
            enemy = Enemy1(-1, -1, 16)  # 初期位置は画面外、HP=16
            self.enemy1_list.append(enemy)
            self.all_enemies.append(enemy)
        
        # Enemy2を1体作成（元: enemy2=new Enemy(width/2,height/4,50,80);）
        self.enemy2 = Enemy2(GameConfig.SCREEN_WIDTH // 2, GameConfig.SCREEN_HEIGHT // 4, 50, 80)
        self.enemy2.invincibility_timer = 0  # 無敵タイマーを初期化
        self.enemy2.active = True  # 明示的にアクティブ化
        self.all_enemies.append(self.enemy2)
        print(f"[ENEMY2 INIT] active={self.enemy2.active}, HP={self.enemy2.hp}")
        
        # Enemy3を1体作成（元: enemy3=new Enemy(width/2,height/4,100,120);）
        self.enemy3 = Enemy3(GameConfig.SCREEN_WIDTH // 2, GameConfig.SCREEN_HEIGHT // 4, 100, 160)
        self.all_enemies.append(self.enemy3)
    
    def update(self, dt: float, player_pos: Vector2, scene_manager, cnt1: int = 0):
        """敵更新処理 - 元のenemy1_move等を完全再現"""
        # シーン別の敵更新
        from core.scene_manager import GameScene
        
        current_scene = scene_manager.get_current_scene()
        
        if scene_manager.is_scene_active(GameScene.STAGE_1):
            self._update_enemy1_stage(dt, player_pos, cnt1)
        elif scene_manager.is_scene_active(GameScene.STAGE_2):
            if self.cnt2 % 120 == 0:  # 2秒ごと
                print(f"[STAGE_2] Updating enemies, scene={current_scene}")
            self._update_enemy2_stage(dt, player_pos)
        elif scene_manager.is_scene_active(GameScene.STAGE_3):
            self._update_enemy3_stage(dt, player_pos)
        else:
            print(f"No matching stage for scene: {current_scene}")
    
    def _update_enemy1_stage(self, dt: float, player_pos: Vector2, cnt1: int):
        """第1ステージの敵更新 - 元のenemy1_move()を完全再現"""
        # 元: for(int i=0;i<3;i++){ enemy_inb[i]++; ... }
        for i, enemy in enumerate(self.enemy1_list):
            if enemy.active:
                enemy.update(dt, player_pos)
        
        # 敵の配置更新（元: enemy_place();）
        self._enemy_place()
        
        # ナイフ攻撃（元: if(cnt1%60==0){ e1b_knife(); }）
        if cnt1 % 60 == 0:
            self.bullet_manager.e1b_knife(self.enemy1_list)
    
    def _update_enemy2_stage(self, dt: float, player_pos: Vector2):
        """第2ステージの敵更新 - 元のenemy2_move()完全再現"""
        if not self.enemy2 or not self.enemy2.active:
            print("Enemy2 is not active or does not exist")
            return
        
        # cnt2++
        self.cnt2 += 1
        
        # enemy_inb[0]++
        if hasattr(self.enemy2, 'invincibility_timer'):
            self.enemy2.invincibility_timer += 1
        else:
            self.enemy2.invincibility_timer = 0
            
        if self.cnt2 % 60 == 0:  # 1秒ごとに表示
            print(f"[ENEMY2 UPDATE] cnt2={self.cnt2}, pos=({self.enemy2.position.x:.0f},{self.enemy2.position.y:.0f})")
        
        # enemy2_place()
        self._enemy2_place()
        
        # hit_enemy(enemy2,0) - 衝突検出はCollisionSystemで処理
        
        # enemy_obj(enemy2) - 基本的な敵オブジェクト処理
        
        # tgt_atk() - ターゲット攻撃
        self._tgt_atk(player_pos)
        
        # draw_enemy2(enemy_inb[0]) - 描画は別途処理
    
    def _enemy2_place(self):
        """第二ステージ敵配置 - 元のenemy2_place()完全再現"""
        if self.enemy2.hp <= 0:
            self.enemy2.position.x = -100
            self.enemy2.position.y = -100
            return
        
        r = 100
        rt = 600
        
        if self.cnt2 % rt < rt // 4:
            # 円運動の第1フェーズ
            self.enemy2.position.x = GameConfig.SCREEN_WIDTH // 2 + r * 1.5 * (1 + math.cos((self.cnt2 - rt // 2) * math.pi / 75 - math.pi))
            self.enemy2.position.y = GameConfig.SCREEN_HEIGHT // 4 + r * math.sin((self.cnt2 - rt // 2) * math.pi / 75 - math.pi)
            if self.cnt2 > 100:
                self._rnd_atk()
        elif self.cnt2 % rt < rt // 2:
            # 円運動の第2フェーズ
            self.enemy2.position.x = GameConfig.SCREEN_WIDTH // 2 + r * 1.5 * (-1 + math.cos(-(self.cnt2 - rt // 2) * math.pi / 75))
            self.enemy2.position.y = GameConfig.SCREEN_HEIGHT // 4 + r * math.sin(-(self.cnt2 - rt // 2) * math.pi / 75)
            self._rnd_atk()
        else:
            # 停止フェーズ
            self.enemy2.position.x = GameConfig.SCREEN_WIDTH // 2
            self.enemy2.position.y = GameConfig.SCREEN_HEIGHT // 4
    
    def _rnd_atk(self):
        """ランダム攻撃 - 元のrnd_atk()完全再現"""
        if self.enemy2 and self.enemy2.hp > 0:
            self.bullet_manager.rnd_atk(self.enemy2.position, self.cnt2)
    
    def _tgt_atk(self, player_pos: Vector2):
        """ターゲット攻撃 - 元のtgt_atk()完全再現"""
        if self.enemy2 and self.enemy2.hp > 0:
            rt = 600  # 元: rt=600;
            self.bullet_manager.tgt_atk(self.enemy2.position, player_pos, self.cnt2, rt)
    
    def _update_enemy3_stage(self, dt: float, player_pos: Vector2):
        """第3ステージの敵更新 - 元のenemy3_move()相当"""
        if self.enemy3 and self.enemy3.active:
            # cnt3をgame_stateから取得または独自管理
            cnt3 = getattr(self, 'cnt3', 0)
            self.cnt3 = cnt3 + 1
            self.enemy3.update(dt, player_pos, cnt3)
            
            # Enemy3の弾を弾幕システムに追加
            if hasattr(self.enemy3, 'pending_bullets') and self.enemy3.pending_bullets:
                for bullet_data in self.enemy3.pending_bullets:
                    self._add_enemy3_bullet(bullet_data)
                self.enemy3.pending_bullets = []
    
    def _add_enemy3_bullet(self, bullet_data: dict):
        """Enemy3の弾を弾幕システムに追加"""
        if self.bullet_manager and self.bullet_manager.bullet_number < self.bullet_manager.bullet_max - 1:
            bullet = self.bullet_manager.bullets[self.bullet_manager.bullet_number]
            bullet.x = bullet_data['x']
            bullet.y = bullet_data['y'] 
            bullet.vx = bullet_data['vx']
            bullet.vy = bullet_data['vy']
            bullet.r = bullet_data['r']
            bullet.ex = True
            self.bullet_manager.bullet_number += 1
    
    def _enemy_place(self):
        """敵の配置 - 元のenemy_place関数の完全再現"""
        for i, enemy in enumerate(self.enemy1_list):
            if enemy.hp <= 0:
                # HPが0以下の敵は画面外に移動（元: enemy1[i].x=-100; enemy1[i].y=-100;）
                enemy.position.x = -100
                enemy.position.y = -100
            else:
                # 固定位置に配置（元の配置ロジック）
                enemy.position.x = GameConfig.SCREEN_WIDTH // 2 + (i - 1) * 100  # width/2+(i-1)*100
                if i == 1:
                    enemy.position.y = 100 + 100  # 真ん中の敵は下に配置
                else:
                    enemy.position.y = 100  # 他の敵は上に配置
    
    def render(self, screen: pygame.Surface):
        """全ての敵を描画"""
        # 敵リストの描画
        for enemy in self.all_enemies:
            if enemy.active and enemy.hp > 0:
                # Enemy2とEnemy3には特別なパラメータを渡す
                if isinstance(enemy, Enemy2):
                    enemy.render(screen, self.cnt2, 60)  # cnt2とinb_maxを渡す
                elif isinstance(enemy, Enemy3):
                    cnt3 = getattr(self, 'cnt3', 0)
                    enemy.render(screen, cnt3)  # cnt3を渡す
                else:
                    enemy.render(screen)
                
        # 第二ステージの敵のデバッグ情報（重要）
        if self.enemy2 and hasattr(self.enemy2, 'position'):
            if self.enemy2.active and self.enemy2.hp > 0:
                print(f"[ENEMY2] Active, HP={self.enemy2.hp}, pos=({self.enemy2.position.x:.0f},{self.enemy2.position.y:.0f})")
            else:
                print(f"[ENEMY2] Inactive or dead - active={self.enemy2.active}, HP={self.enemy2.hp}")
    
    def update_bullets(self, player_pos: Vector2, scene_manager, player_inb_cnt: int, inb_max: int) -> bool:
        """敵弾の更新（元のbullet()関数の更新部分）"""
        return self.bullet_manager.update(player_pos, scene_manager, player_inb_cnt, inb_max)
    
    def render_bullets(self, screen: pygame.Surface, scene_manager):
        """敵弾の描画（元のbullet()関数の描画部分）"""
        self.bullet_manager.render(screen, scene_manager)
    
    def update_and_render_bullets(self, screen: pygame.Surface, player_pos: Vector2, 
                                 scene_manager, player_inb_cnt: int, inb_max: int) -> bool:
        """敵弾の更新と描画（元のbullet()関数）"""
        return self.bullet_manager.update_and_render(screen, player_pos, scene_manager, 
                                                   player_inb_cnt, inb_max)
    
    def reset_bullets(self):
        """弾リセット（シーン変更時など）"""
        self.bullet_manager.reset_bullet()
    
    def get_active_enemy1_list(self) -> List[Enemy1]:
        """アクティブなenemy1リストを取得"""
        return [e for e in self.enemy1_list if e.active and e.hp > 0]
    
    def handle_collision_reset(self, enemy_index: int):
        """衝突時の無敵カウンターリセット - 元のif(hit_enemy(enemy1[i],0)){ enemy_inb[i]=0; }"""
        if 0 <= enemy_index < len(self.enemy1_list):
            self.enemy1_list[enemy_index].inb_counter = 0
    
    def check_stage1_clear(self) -> bool:
        """第1ステージクリア判定"""
        return all(enemy.hp <= 0 for enemy in self.enemy1_list)
    
    def check_stage2_clear(self) -> bool:
        """第2ステージクリア判定"""
        return self.enemy2.hp <= 0
    
    def check_stage3_clear(self) -> bool:
        """第3ステージクリア判定"""
        return self.enemy3.hp <= 0
    
    def get_active_enemies(self) -> List[Enemy]:
        """アクティブな敵のリストを取得"""
        return [e for e in self.all_enemies if e.active and e.hp > 0]
    
    def check_collisions_with_projectiles(self, projectiles: List) -> List[Tuple[Enemy, any]]:
        """プロジェクタイルとの衝突判定"""
        collisions = []
        
        for enemy in self.get_active_enemies():
            for projectile in projectiles:
                if hasattr(projectile, 'active') and projectile.active:
                    # 距離計算
                    dx = enemy.position.x - projectile.x
                    dy = enemy.position.y - projectile.y
                    distance = math.sqrt(dx * dx + dy * dy)
                    
                    if distance < enemy.radius + projectile.radius:
                        collisions.append((enemy, projectile))
        
        return collisions
    
    def apply_damage_from_collisions(self, collisions: List[Tuple[Enemy, any]], damage: int = 1):
        """衝突によるダメージ処理"""
        for enemy, projectile in collisions:
            # プロジェクタイルの速度に基づくダメージ計算（元: e.hp-=abs(velocity_b);）
            if hasattr(projectile, 'get_damage'):
                actual_damage = projectile.get_damage()
            else:
                actual_damage = damage  # デフォルトダメージ
                
            if enemy.take_damage(actual_damage):
                # 敵が倒された場合の処理
                if enemy.hp <= 0:
                    print(f"Enemy defeated! Damage was {actual_damage}")
            
            # プロジェクタイルを無効化
            if hasattr(projectile, 'active'):
                projectile.active = False
    
    def get_active_enemies_count(self) -> int:
        """アクティブな敵の数を取得"""
        return len(self.get_active_enemies())
    
    def check_collisions_with_projectiles(self, projectiles: List) -> List[Tuple[Enemy, any]]:
        """プロジェクタイルとの衝突判定"""
        collisions = []
        
        for enemy in self.get_active_enemies():
            for projectile in projectiles:
                if hasattr(projectile, 'active') and projectile.active:
                    # 距離計算
                    dx = enemy.position.x - projectile.x
                    dy = enemy.position.y - projectile.y
                    distance = math.sqrt(dx * dx + dy * dy)
                    
                    if distance < enemy.radius + projectile.radius:
                        collisions.append((enemy, projectile))
        
        return collisions