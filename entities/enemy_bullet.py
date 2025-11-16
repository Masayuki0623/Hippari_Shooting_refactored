"""
敵の弾システム - 元のbullet.pdeの完全再現
"""
import pygame
import math
import random
from typing import List
from utils.math_utils import Vector2
from config.settings import GameConfig, Colors


class EnemyBullet:
    """敵弾クラス - 元のBulletクラス完全再現"""
    
    def __init__(self, x: float, y: float, vx: float, vy: float, radius: float, exist: bool = False):
        # 元: Bullet(float xpos,float ypos,float verx,float very,float radius,boolean exist)
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.r = radius
        self.ex = exist  # 元のexistフラグ


class EnemyBulletManager:
    """敵弾管理システム - 元のbullet.pdeシステム完全再現"""
    
    def __init__(self):
        # 元: final int bullet_max=800; Bullet []bullet=new Bullet[bullet_max];
        self.bullet_max = 800
        self.bullets = []
        for i in range(self.bullet_max):
            self.bullets.append(EnemyBullet(-1, -1, -1, -1, -1, False))
        
        # 元: int bullet_number=0; int knife_number=0;
        self.bullet_number = 0
        self.knife_number = 0
        self.delete_knife = 0
        
        # 第二ステージ用
        self.t_number = 0  # ターゲット攻撃用
        
    def reset_bullet(self):
        """弾リセット - 元のreset_bullet()"""
        for i in range(self.bullet_max):
            self.bullets[i].ex = False
    
    def update(self, player_pos: Vector2, scene_manager, player_inb_cnt: int, inb_max: int) -> bool:
        """
        弾更新処理 - 元のbullet()関数の更新部分
        
        Returns:
            プレイヤーがヒットしたかどうか
        """
        player_hit = False
        
        for i in range(self.bullet_max):
            bullet = self.bullets[i]
            
            if bullet.ex:
                # 弾数制限チェック（元: if(bullet_number>bullet_max-100){bullet_number=0;}）
                if self.bullet_number > self.bullet_max - 100:
                    self.bullet_number = 0
                
                # 弾移動（元: bullet[i].x+=bullet[i].vx; bullet[i].y+=bullet[i].vy;）
                bullet.x += bullet.vx
                bullet.y += bullet.vy
                
                # 更新処理のみ（描画はrenderで実行）
                
                # プレイヤーとの衝突判定
                dist = math.sqrt((bullet.x - player_pos.x)**2 + (bullet.y - player_pos.y)**2)
                if (dist <= bullet.r + GameConfig.PLAYER_RADIUS/2 and 
                    player_inb_cnt > inb_max):  # 元: inb_cnt>inb_max
                    
                    bullet.ex = False
                    player_hit = True
                    
                    # シーン別弾消去処理
                    from core.scene_manager import GameScene
                    if scene_manager.is_scene_active(GameScene.STAGE_1):
                        # 元: delete_knife=i-i%10; for(int j=0;j<10;j++){bullet[j+delete_knife].ex=false;}
                        self.delete_knife = i - (i % 10)
                        for j in range(10):
                            if self.delete_knife + j < self.bullet_max:
                                self.bullets[self.delete_knife + j].ex = False
                                
                    elif scene_manager.is_scene_active(GameScene.STAGE_2):
                        # 元: if(t_number<=i&&t_number+6>i){for(int j=0;j<6;j++){bullet[t_number+j].ex=false;}}
                        if self.t_number <= i < self.t_number + 6:
                            for j in range(6):
                                if self.t_number + j < self.bullet_max:
                                    self.bullets[self.t_number + j].ex = False
                
                # 画面外判定（元の条件を修正 - OR条件が正しい）
                if (bullet.x <= -bullet.r or bullet.x >= GameConfig.SCREEN_WIDTH + bullet.r or
                    bullet.y <= -bullet.r or bullet.y >= GameConfig.SCREEN_HEIGHT + bullet.r):
                    bullet.ex = False
                    bullet.vx = 0
                    bullet.vy = 0
                    bullet.x = -100
                    bullet.y = -100
                    
            else:
                # 非アクティブ弾の初期化
                bullet.x = -bullet.r
                bullet.y = -bullet.r
                bullet.vx = 0
                bullet.vy = 0
        
        return player_hit
    
    def render(self, screen: pygame.Surface, scene_manager):
        """
        弾描画処理 - 元のbullet()関数の描画部分
        """
        import colorsys
        from core.scene_manager import GameScene
        
        def hsb_to_rgb(h, s, b):
            """HSB(360,100,100)からRGBへの変換"""
            h_norm = (h % 360) / 360.0
            s_norm = max(0, min(s, 100)) / 100.0
            b_norm = max(0, min(b, 100)) / 100.0
            r, g, b_rgb = colorsys.hsv_to_rgb(h_norm, s_norm, b_norm)
            return (int(r * 255), int(g * 255), int(b_rgb * 255))
        
        for i in range(self.bullet_max):
            bullet = self.bullets[i]
            
            if bullet.ex:
                # シーン別色設定（元のbullet()関数の色指定を完全再現）
                color = (255, 0, 0)  # デフォルト赤
                
                if scene_manager.is_scene_active(GameScene.STAGE_1):
                    # 元: colorMode(HSB,360,100,100); fill(104,70,50);
                    color = hsb_to_rgb(104, 70, 50)
                    
                elif scene_manager.is_scene_active(GameScene.STAGE_2):
                    # 元: if(i%2==0){fill(70,255,255);}else{fill(0,50,210);}
                    # RGB(255,255,255)モードでの指定
                    if i % 2 == 0:
                        color = (70, 255, 255)   # シアン系
                    else:
                        color = (0, 50, 210)     # 青系
                        
                elif scene_manager.is_scene_active(GameScene.STAGE_3):
                    # 元: fill(255,0,0);
                    color = (255, 0, 0)  # 赤
                
                # 弾描画（元: ellipse(bullet[i].x,bullet[i].y,bullet[i].r*2,bullet[i].r*2);）
                pygame.draw.circle(screen, color, 
                                 (int(bullet.x), int(bullet.y)), int(bullet.r))
    
    def update_and_render(self, screen: pygame.Surface, player_pos: Vector2, 
                         scene_manager, player_inb_cnt: int, inb_max: int) -> bool:
        """
        弾更新と描画 - 元のbullet()関数完全再現
        """
        player_hit = self.update(player_pos, scene_manager, player_inb_cnt, inb_max)
        if screen is not None:
            self.render(screen, scene_manager)
        return player_hit
    
    def e1b_knife(self, enemy1_list):
        """
        第一ステージ敵のナイフ攻撃 - 元のe1b_knife()完全再現
        各敵から10個の弾を発射
        """
        for i, enemy in enumerate(enemy1_list):
            if enemy.position.x > 0 and enemy.hp > 0:  # 元: if(enemy1[i].x>0)
                # 元: int rnd=(int)random(10)-5;
                rnd = int(random.random() * 10) - 5
                cos_k = math.cos(rnd * math.pi / 12)
                sin_k = math.sin(rnd * math.pi / 12)
                
                self.knife_number = self.bullet_number
                
                # 10個の弾を生成（元のコードの正確な再現）
                bullet_positions = [
                    (8*cos_k, 8*sin_k),      # 1番目
                    (-8*cos_k, -8*sin_k),    # 2番目（中心）
                    (24*cos_k, 24*sin_k),    # 3番目
                    (-24*cos_k, -24*sin_k),  # 4番目
                    (-18*sin_k, 18*cos_k),   # 5番目
                    (16*cos_k-18*sin_k, 16*sin_k+18*cos_k),  # 6番目
                    (-16*cos_k-18*sin_k, -16*sin_k+18*cos_k), # 7番目
                    (8*cos_k-36*sin_k, 8*sin_k+36*cos_k),     # 8番目
                    (-8*cos_k-36*sin_k, -8*sin_k+36*cos_k),   # 9番目
                    (-54*sin_k, 54*cos_k)    # 10番目
                ]
                
                for dx, dy in bullet_positions:
                    if self.bullet_number < self.bullet_max:
                        bullet = self.bullets[self.bullet_number]
                        bullet.ex = True
                        bullet.x = enemy.position.x + dx
                        bullet.y = enemy.position.y + dy
                        bullet.vx = -5 * sin_k
                        bullet.vy = 5 * cos_k
                        bullet.r = 10
                        self.bullet_number += 1
    
    def rnd_atk(self, enemy2_pos: Vector2, cnt2: int):
        """
        第二ステージランダム攻撃 - 元のrnd_atk()完全再現
        """
        if cnt2 % 2 == 0:  # 元: if(cnt2%2==0)
            rnd = random.random() * 30  # 元: float rnd=random(30);
            
            if self.bullet_number < self.bullet_max:
                bullet = self.bullets[self.bullet_number]
                bullet.ex = True
                bullet.x = enemy2_pos.x
                bullet.y = enemy2_pos.y
                bullet.vx = 8 * math.sin(math.pi/20 * (rnd - 15))
                bullet.vy = 8 * math.cos(math.pi/20 * (rnd - 15))
                bullet.r = 10
                self.bullet_number += 1
    
    def tgt_atk(self, enemy2_pos: Vector2, player_pos: Vector2, cnt2: int, rt: int):
        """
        第二ステージターゲット攻撃 - 元のtgt_atk()完全再現
        """
        if cnt2 % rt == rt * 3 // 4 - 30:  # 元: if(cnt2%rt==rt*3/4-30)
            self.t_number = self.bullet_number
            
            # 6発の弾を準備
            for i in range(6):
                if self.bullet_number + i < self.bullet_max:
                    bullet = self.bullets[self.t_number + i]
                    bullet.ex = True
                    bullet.r = 10
                    bullet.x = enemy2_pos.x
                    bullet.y = enemy2_pos.y + 60
                    bullet.vx = 0
                    bullet.vy = 0
        
        # 弾の軌道計算フェーズ
        if cnt2 % rt <= rt * 3 // 4 and cnt2 % rt > rt * 3 // 4 - 30:
            d_e = math.sqrt((enemy2_pos.x - player_pos.x)**2 + 
                           (enemy2_pos.y + 60 - player_pos.y)**2)
            if d_e > 0:
                cos_e = (player_pos.x - enemy2_pos.x) / d_e
                sin_e = (player_pos.y - (enemy2_pos.y + 60)) / d_e
                
                # 弾を段階的に伸ばす
                for i in range(6):
                    if self.t_number + i < self.bullet_max:
                        bullet = self.bullets[self.t_number + i]
                        progress = cnt2 % rt - rt * 3 // 4 + 30
                        bullet.x = enemy2_pos.x + 20 * i * cos_e / 30 * progress
                        bullet.y = enemy2_pos.y + 60 + 20 * i * sin_e / 30 * progress
        
        # 発射フェーズ
        if cnt2 % rt == rt * 3 // 4:  # 元: if(cnt2%rt==rt*3/4)
            d_e = math.sqrt((enemy2_pos.x - player_pos.x)**2 + 
                           (enemy2_pos.y + 60 - player_pos.y)**2)
            if d_e > 0:
                cos_e = (player_pos.x - enemy2_pos.x) / d_e
                sin_e = (player_pos.y - (enemy2_pos.y + 60)) / d_e
                
                for i in range(6):
                    if self.t_number + i < self.bullet_max:
                        bullet = self.bullets[self.t_number + i]
                        bullet.vx = 15 * cos_e
                        bullet.vy = 15 * sin_e
                        if self.bullet_number < self.bullet_max:
                            self.bullet_number += 1
    
    def clear_all_bullets(self):
        """全敵弾クリア - ステージ遷移時のリセット用"""
        self.reset_bullet()
        self.bullet_number = 0
        self.knife_number = 0
        self.delete_knife = 0
        self.t_number = 0
        print("All enemy bullets cleared")