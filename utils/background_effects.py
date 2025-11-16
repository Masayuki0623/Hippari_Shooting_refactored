"""
背景とエフェクトシステム
元のProcessingコードの背景効果を再現
"""

import pygame
import math
import random
from config.settings import GameConfig, Colors
from utils.math_utils import Vector2


class BackgroundEffect:
    """背景エフェクトの基底クラス"""
    
    def __init__(self):
        self.active = True
        
    def update(self, dt: float):
        """エフェクトの更新"""
        pass
    
    def render(self, screen: pygame.Surface):
        """エフェクトの描画"""
        pass


class HSBBackground(BackgroundEffect):
    """元のHSBカラーモード背景を再現"""
    
    def __init__(self):
        super().__init__()
        self.br = 10  # 元のbrパラメータ（final float br=10;）
        self.width_cells = GameConfig.SCREEN_WIDTH // self.br + 1
        self.height_cells = GameConfig.SCREEN_HEIGHT // self.br + 1
        
        # 元のH_rnd, S_rnd, B_rndに相当する配列
        self.H_rnd = [[0 for _ in range(self.height_cells)] for _ in range(self.width_cells)]
        self.S_rnd = [[0 for _ in range(self.height_cells)] for _ in range(self.width_cells)]
        self.B_rnd = [[0 for _ in range(self.height_cells)] for _ in range(self.width_cells)]
        
        # 背景色配列
        self.H_bg = [[0 for _ in range(self.height_cells)] for _ in range(self.width_cells)]
        self.S_bg = [[0 for _ in range(self.height_cells)] for _ in range(self.width_cells)]
        self.B_bg = [[0 for _ in range(self.height_cells)] for _ in range(self.width_cells)]
        
        # ランダム値の初期化（元のsetup関数相当）
        self._initialize_random_values()
    
    def _initialize_random_values(self):
        """ランダム値の初期化 - 元のgenerate_scene1bg()を再現"""
        import random
        for i in range(self.width_cells):
            for j in range(self.height_cells):
                # 元: H_rnd[i][j]=30+(int)random(5)-25;
                self.H_rnd[i][j] = 30 + random.randint(0, 4) - 25
                # 元: S_rnd[i][j]=(int)random(5)+5+10;
                self.S_rnd[i][j] = random.randint(0, 4) + 5 + 10
                # 元: B_rnd[i][j]=75+(int)random(5)+20;
                self.B_rnd[i][j] = 75 + random.randint(0, 4) + 20
    
    def render(self, screen: pygame.Surface):
        """HSB背景の描画 - 元のscene3bg()を完全再現"""
        for i in range(self.width_cells):
            for j in range(self.height_cells):
                # 元: fill(H_rnd[i][j],S_rnd[i][j],B_rnd[i][j]);
                h = self.H_rnd[i][j]
                s = self.S_rnd[i][j]
                b = self.B_rnd[i][j]
                
                rgb = self._hsb_to_rgb(h, s, b)
                
                # 元: rect(br*i,br*j,br,br);
                rect = pygame.Rect(i * self.br, j * self.br, self.br, self.br)
                pygame.draw.rect(screen, rgb, rect)
    
    def _hsb_to_rgb(self, h: float, s: float, b: float) -> tuple:
        """HSBからRGBへの変換 - Processing HSB(360,100,100)モード準拠"""
        # ProcessingのHSB(360,100,100)モードに合わせる
        h = h / 360.0  # 0-360 -> 0-1
        s = s / 100.0  # 0-100 -> 0-1
        b = b / 100.0  # 0-100 -> 0-1
        
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(h, s, b)
        
        return (int(r * 255), int(g * 255), int(b * 255))


class CameraShake(BackgroundEffect):
    """画面揺れエフェクト"""
    
    def __init__(self):
        super().__init__()
        self.shake_intensity = 0
        self.shake_duration = 0
        self.shake_timer = 0
        
    def trigger_shake(self, intensity: float, duration: float):
        """画面揺れを開始"""
        self.shake_intensity = intensity
        self.shake_duration = duration
        self.shake_timer = 0
        
    def update(self, dt: float):
        """画面揺れの更新"""
        if self.shake_timer < self.shake_duration:
            self.shake_timer += dt
        else:
            self.shake_intensity = 0
    
    def get_shake_offset(self) -> Vector2:
        """現在の揺れオフセットを取得"""
        if self.shake_intensity <= 0:
            return Vector2(0, 0)
        
        # 時間経過で揺れが減衰
        progress = self.shake_timer / self.shake_duration
        current_intensity = self.shake_intensity * (1 - progress)
        
        offset_x = random.uniform(-current_intensity, current_intensity)
        offset_y = random.uniform(-current_intensity, current_intensity)
        
        return Vector2(offset_x, offset_y)


class ParticleEffect(BackgroundEffect):
    """パーティクル効果"""
    
    def __init__(self):
        super().__init__()
        self.particles = []
        
    def add_explosion(self, position: Vector2, color: tuple = Colors.ORANGE, count: int = 10):
        """爆発パーティクルを追加"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            
            particle = {
                'pos': Vector2(position.x, position.y),
                'vel': Vector2(math.cos(angle) * speed, math.sin(angle) * speed),
                'life': random.uniform(0.5, 1.5),
                'max_life': 1.0,
                'color': color,
                'size': random.uniform(2, 5)
            }
            self.particles.append(particle)
    
    def update(self, dt: float):
        """パーティクルの更新"""
        for particle in self.particles[:]:  # コピーを作成してイテレート
            particle['pos'] += particle['vel'] * dt
            particle['life'] -= dt
            
            # 重力効果
            particle['vel'].y += 200 * dt
            
            # パーティクルの削除
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def render(self, screen: pygame.Surface):
        """パーティクルの描画"""
        for particle in self.particles:
            # ライフに基づいた透明度
            alpha = particle['life'] / particle['max_life']
            size = particle['size'] * alpha
            
            if size > 0.5:
                pos = (int(particle['pos'].x), int(particle['pos'].y))
                pygame.draw.circle(screen, particle['color'], pos, int(size))


class BackgroundManager:
    """背景エフェクト管理クラス"""
    
    def __init__(self):
        self.effects = []
        
        # デフォルトエフェクトを追加
        self.hsb_background = HSBBackground()
        self.camera_shake = CameraShake()
        self.particle_effect = ParticleEffect()
        
        self.effects = [self.hsb_background, self.camera_shake, self.particle_effect]
        
    def update(self, dt: float):
        """全エフェクトの更新"""
        for effect in self.effects:
            if effect.active:
                effect.update(dt)
    
    def render(self, screen: pygame.Surface):
        """背景の描画"""
        # まず基本背景を描画
        self.hsb_background.render(screen)
        
        # パーティクルエフェクトを描画
        self.particle_effect.render(screen)
    
    def add_explosion_effect(self, position: Vector2, intensity: float = 5.0):
        """爆発エフェクトを追加"""
        # パーティクル効果
        self.particle_effect.add_explosion(position)
        
        # 画面揺れ
        self.camera_shake.trigger_shake(intensity, 0.3)
    
    def get_camera_offset(self) -> Vector2:
        """カメラオフセット（画面揺れ）を取得"""
        return self.camera_shake.get_shake_offset()
    
    def add_custom_effect(self, effect: BackgroundEffect):
        """カスタムエフェクトを追加"""
        self.effects.append(effect)