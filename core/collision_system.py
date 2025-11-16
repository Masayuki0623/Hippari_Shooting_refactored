"""
衝突検出とダメージシステム - 元のenemy.pdeの完全再現
hit_enemy()、enemy_obj()、show_damage()を忠実に実装
"""
import pygame
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass

from config.settings import GameConfig
from utils.math_utils import Vector2


@dataclass
class HitInfo:
    """ヒット情報を格納するクラス"""
    position: Vector2
    damage: float
    timer: int = 0


class CollisionSystem:
    """
    衝突検出システム - 元のhit_enemy()とenemy_obj()を完全再現
    オリジナルのゲーム性を一切変更しない
    """
    
    def __init__(self, audio_manager=None):
        self.audio_manager = audio_manager
        
        # ヒット情報（元のhit_place_x, hit_place_y, hit_demage相当）
        self.hit_info: Optional[HitInfo] = None
        self.hit_timer = 0  # 元のhit_timer
        
        # グローバル変数（元のコード通り）
        self.velocity_b = 0  # 現在の弾の速度
    
    def check_projectile_enemy_collision(self, projectiles: List, enemies: List, 
                                       scene_manager) -> List[Tuple]:
        """
        弾と敵の衝突検出 - 元のhit_enemy()関数を完全再現
        
        オリジナル: boolean hit_enemy(Enemy e,int img){
        for(int i=0;i<3;i++){
            if(dist(ex+er,ey+er,ball_x[i],ball_y[i])<e.r+ellipse_round){
                e.hp-=abs(velocity_b);
        
        Args:
            projectiles: 弾のリスト（ball_x, ball_y相当）
            enemies: 敵のリスト
            scene_manager: シーン管理（scene配列チェック用）
            
        Returns:
            衝突したペアのリスト
        """
        collisions = []
        
        for enemy in enemies:
            if not enemy.active or enemy.hp <= 0:
                continue
                
            hit_result = self._hit_enemy_original(enemy, projectiles, scene_manager)
            if hit_result['hit']:
                hit_projectile = projectiles[hit_result['projectile_index']] if hit_result['projectile_index'] >= 0 else None
                collisions.append((enemy, hit_projectile))
        
        return collisions
    
    def _hit_enemy_original(self, enemy, projectiles: List, scene_manager) -> dict:
        """
        元のhit_enemy()関数の完全再現
        
        Args:
            enemy: 対象の敵
            projectiles: 弾のリスト
            scene_manager: シーンマネージャー
            
        Returns:
            ヒット結果の辞書
        """
        hit = False
        projectile_hit_index = -1
        
        # 元の判定: er = (img==1) ? e.r : 0;
        # imgパラメータは常に0で呼ばれているため、er=0
        er = 0
        
        ex = enemy.position.x
        ey = enemy.position.y
        
        # 3つの弾をチェック（元: for(int i=0;i<3;i++)）
        for i in range(min(3, len(projectiles))):
            projectile = projectiles[i]
            if not hasattr(projectile, 'active') or not projectile.active:
                continue
                
            ball_x = projectile.position.x
            ball_y = projectile.position.y
            
            # 距離判定（元: dist(ex+er,ey+er,ball_x[i],ball_y[i])<e.r+ellipse_round）
            distance = math.sqrt((ex + er - ball_x)**2 + (ey + er - ball_y)**2)
            collision_distance = enemy.radius + GameConfig.ELLIPSE_ROUND
            
            if distance < collision_distance:
                # プロジェクタイルからvelocity_b値を取得（元のグローバル変数velocity_b相当）
                if hasattr(projectile, 'velocity_b'):
                    current_velocity_b = projectile.velocity_b
                elif hasattr(projectile, 'get_damage'):
                    # get_damage()がabs(velocity_b)を返すため、符号を考慮
                    current_velocity_b = projectile.get_damage()
                else:
                    current_velocity_b = 1  # フォールバック値
                    
                print(f"Collision detected! velocity_b = {current_velocity_b}, enemy HP = {enemy.hp}")
                
                # サウンド再生判定（ダメージ適用前のHPで判定）
                if not scene_manager.is_scene_active(5) and not scene_manager.is_scene_active(0):
                    if abs(current_velocity_b) < enemy.hp:
                        # hit_sound再生
                        if self.audio_manager:
                            self.audio_manager.play_hit_sound()
                    else:
                        # kill_sound再生
                        if self.audio_manager:
                            self.audio_manager.play_kill_sound()
                else:
                    # restart_sound再生
                    if self.audio_manager:
                        self.audio_manager.play_restart_sound()
                
                # ダメージ適用（元: e.hp-=abs(velocity_b);）
                enemy.hp -= abs(current_velocity_b)
                print(f"Damage applied! Enemy HP after hit: {enemy.hp}")
                
                # 弾を画面外に移動（元: ball_x[i]=width+100;ball_y[i]=height+100;）
                projectile.position.x = GameConfig.SCREEN_WIDTH + 100
                projectile.position.y = GameConfig.SCREEN_HEIGHT + 100
                projectile.velocity = Vector2(0, 0)  # ball_vx[i]=0;ball_vy[i]=0;
                projectile.active = False
                
                # 元の物理システムの弾配列も更新（重要！）
                self.hit_projectile_index = getattr(projectile, 'ball_index', -1)
                
                # ヒット情報記録（元: hit_place_x=ex; hit_place_y=ey; hit_demage=velocity_b;）
                self.hit_info = HitInfo(
                    position=Vector2(ex, ey),
                    damage=current_velocity_b,
                    timer=0
                )
                
                # 衝突フラグ
                hit = True
                projectile_hit_index = i
                
                # velocity_bを保存（戻り値で使用）
                self.velocity_b = current_velocity_b
                
                # 元: if(!scene[0]){hit=true;} - 常にtrue
                # 元: velocity_b=0; hit=true; - この時点でvelocity_bを0にリセット
                self.velocity_b = 0
                
                break  # 最初の衝突で終了
        
        return {
            'hit': hit,
            'projectile_index': projectile_hit_index
        }
    
    def check_player_enemy_collision(self, player, enemies, inb_cnt: int, 
                                   inb_max: int) -> bool:
        """
        プレイヤーと敵の衝突検出 - 元のenemy_obj()関数を完全再現
        
        Args:
            player: プレイヤーオブジェクト
            enemies: 敵のリスト
            inb_cnt: 無敵カウンター
            inb_max: 無敵時間最大値
            
        Returns:
            衝突が発生したかどうか
        """
        collision_occurred = False
        
        for enemy in enemies:
            if self._enemy_obj_original(player, enemy, inb_cnt, inb_max):
                collision_occurred = True
        
        return collision_occurred
    
    def check_player_boss_collision(self, player, boss_enemies, inb_cnt: int, 
                                  inb_max: int) -> bool:
        """
        プレイヤーとボスの衝突検出 - ボス専用の接触ダメージ
        
        Args:
            player: プレイヤーオブジェクト
            boss_enemies: ボス敵のリスト（Enemy2, Enemy3, ピクシー含む）
            inb_cnt: 無敵カウンター
            inb_max: 無敵時間最大値
            
        Returns:
            衝突が発生したかどうか
        """
        collision_occurred = False
        
        for boss in boss_enemies:
            if boss.active and boss.hp > 0:
                if self._boss_collision_check(player, boss, inb_cnt, inb_max):
                    collision_occurred = True
        
        return collision_occurred
    
    def _enemy_obj_original(self, player, enemy, inb_cnt: int, inb_max: int) -> bool:
        """
        元のenemy_obj()関数の完全再現
        
        Args:
            player: プレイヤー
            enemy: 敵
            inb_cnt: 無敵カウンター  
            inb_max: 無敵時間最大値
            
        Returns:
            衝突が発生したかどうか
        """
        # 元の判定条件を完全再現
        # if(dist(player_x,player_y,e.x,e.y)<=ellipse_round/2+e.r&&inb_cnt>inb_max&&e.hp>0)
        
        distance = math.sqrt((player.position.x - enemy.position.x)**2 + 
                           (player.position.y - enemy.position.y)**2)
        
        collision_distance = GameConfig.ELLIPSE_ROUND / 2 + enemy.radius
        
        if (distance <= collision_distance and 
            inb_cnt > inb_max and 
            enemy.hp > 0):
            
            # ダメージ処理（元: inb_cnt=0; player_hp--;）
            # inb_cntのリセットは呼び出し元で行う
            player.hp -= 1
            
            # サウンド再生（元のコード通り）
            if player.hp > 0:
                if self.audio_manager:
                    self.audio_manager.play_damage_sound()
            else:
                if self.audio_manager:
                    self.audio_manager.play_death_sound()
            
            return True
        
        return False
    
    def _boss_collision_check(self, player, boss, inb_cnt: int, inb_max: int) -> bool:
        """
        ボスとの衝突判定 - より大きな当たり判定
        """
        distance = math.sqrt((player.position.x - boss.position.x)**2 + 
                           (player.position.y - boss.position.y)**2)
        
        # ボスは通常の敵より大きい当たり判定
        collision_distance = GameConfig.PLAYER_RADIUS + boss.radius
        
        if (distance <= collision_distance and 
            inb_cnt > inb_max and 
            boss.hp > 0):
            
            # プレイヤーにダメージ
            player.hp -= 1
            
            # サウンド再生
            if player.hp > 0:
                if self.audio_manager:
                    self.audio_manager.play_damage_sound()
            else:
                if self.audio_manager:
                    self.audio_manager.play_death_sound()
            
            return True
        
        return False
    
    def update_hit_display(self, dt: float):
        """
        ヒット表示の更新 - 元のshow_damage()タイマー処理
        """
        if self.hit_info:
            self.hit_info.timer += dt * 60  # 60FPS基準
            
            # 90フレーム後に非表示（元: if(hit_timer>90)）
            if self.hit_info.timer > 90:
                self.hit_info = None
                self.hit_timer = 0
    
    def render_hit_damage(self, screen: pygame.Surface, font: pygame.font.Font):
        """
        ヒットダメージ表示 - 元のshow_damage()関数を完全再現
        """
        if not self.hit_info:
            return
            
        # 元の描画位置（元: text(-abs((int)d),x+100,y+20);）
        damage_text = str(-abs(int(self.hit_info.damage)))
        text_x = self.hit_info.position.x + 100
        text_y = self.hit_info.position.y + 20
        
        # 赤色テキスト（元: fill(255,0,0);）
        text_surface = font.render(damage_text, True, (255, 0, 0))
        screen.blit(text_surface, (text_x, text_y))
    
    def set_projectile_velocity(self, velocity: float):
        """弾の速度を設定（velocity_b相当）"""
        self.velocity_b = velocity


class AudioManager:
    """
    音声管理クラス - 元のサウンド再生を管理
    """
    
    def __init__(self):
        # TODO: pygame.mixerでサウンドファイル読み込み
        self.hit_sound = None      # hit_sound.wav
        self.kill_sound = None     # kill_sound.wav
        self.damage_sound = None   # damage_sound.wav
        self.death_sound = None    # death_sound.wav
        self.restart_sound = None  # restart_sound.wav
    
    def play_hit_sound(self):
        """ヒット音再生"""
        if self.hit_sound:
            self.hit_sound.play()
    
    def play_kill_sound(self):
        """撃破音再生"""
        if self.kill_sound:
            self.kill_sound.play()
    
    def play_damage_sound(self):
        """ダメージ音再生"""
        if self.damage_sound:
            self.damage_sound.play()
    
    def play_death_sound(self):
        """死亡音再生"""
        if self.death_sound:
            self.death_sound.play()
    
    def play_restart_sound(self):
        """リスタート音再生"""
        if self.restart_sound:
            self.restart_sound.play()