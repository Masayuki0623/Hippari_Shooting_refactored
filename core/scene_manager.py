"""
ゲームステージ管理システム - 元のUI.pdeの完全再現
全6ステージの状態管理と遷移を正確に実装
"""
from typing import Dict, List, Callable
from enum import IntEnum
import pygame

from config.settings import GameConfig
from utils.math_utils import Vector2


class GameScene(IntEnum):
    """ゲームシーン定数 - 元のscene配列のインデックス"""
    START_SCREEN = 0      # scene[0] - スタート画面
    STAGE_1 = 1          # scene[1] - 第1ステージ（敵1x3体）
    STAGE_2 = 2          # scene[2] - 第2ステージ（敵2x1体）
    STAGE_3 = 3          # scene[3] - 第3ステージ（敵3x1体）
    ENDING = 4           # scene[4] - エンディング
    GAME_OVER = 5        # scene[5] - ゲームオーバー
    UNUSED = 6           # scene[6] - 未使用


class SceneTransitionCondition:
    """シーン遷移条件を定義するクラス"""
    
    def __init__(self, check_func: Callable, target_scene: GameScene, 
                 setup_func: Callable = None):
        self.check_func = check_func
        self.target_scene = target_scene
        self.setup_func = setup_func
    
    def should_transition(self, game_state) -> bool:
        """遷移条件をチェック"""
        return self.check_func(game_state)
    
    def execute_setup(self, game_state):
        """遷移時のセットアップ処理"""
        if self.setup_func:
            self.setup_func(game_state)


class GameSceneManager:
    """
    ゲームシーン管理クラス
    元のscene_change()関数とscene配列を完全再現
    """
    
    def __init__(self):
        # scene配列の完全再現
        self.scene = [False] * 7  # scene_number = 7
        self.scene[GameScene.START_SCREEN] = True  # 初期状態はスタート画面
        
        self.current_scene = GameScene.START_SCREEN
        
        # カウンター（元のcnt1, cnt2, cnt3相当）
        self.stage1_counter = 0  # cnt1
        self.stage2_counter = 0  # cnt2  
        self.stage3_counter = 0  # cnt3
        
        # 遷移条件を定義
        self._setup_transition_conditions()
    
    def _setup_transition_conditions(self):
        """各シーンの遷移条件を設定"""
        self.transitions = {
            GameScene.START_SCREEN: [
                SceneTransitionCondition(
                    lambda gs: self._check_title_scene_transition(gs),  # TitleSceneの衝突判定結果をチェック
                    GameScene.STAGE_1,
                    self._setup_stage1
                )
            ],
            GameScene.STAGE_1: [
                SceneTransitionCondition(
                    lambda gs: (gs.enemy_manager.enemy1_list[0].hp <= 0 and 
                              gs.enemy_manager.enemy1_list[1].hp <= 0 and 
                              gs.enemy_manager.enemy1_list[2].hp <= 0),
                    GameScene.STAGE_2,
                    self._setup_stage2
                )
            ],
            GameScene.STAGE_2: [
                SceneTransitionCondition(
                    lambda gs: gs.enemy_manager.enemy2.hp <= 0,
                    GameScene.STAGE_3,
                    self._setup_stage3
                )
            ],
            GameScene.STAGE_3: [
                SceneTransitionCondition(
                    lambda gs: gs.enemy_manager.enemy3.hp <= 0,
                    GameScene.ENDING,
                    self._setup_ending
                )
            ],
            GameScene.GAME_OVER: [
                SceneTransitionCondition(
                    lambda gs: gs.restart_button.hp < 0,  # restart.hp < 0
                    GameScene.STAGE_1,
                    self._restart_game
                )
            ]
        }
        
        # 全シーン共通：プレイヤーHP0でゲームオーバー
        self.global_transitions = [
            SceneTransitionCondition(
                lambda gs: gs.player.hp <= 0,
                GameScene.GAME_OVER,
                self._setup_game_over
            )
        ]
    
    def update(self, game_state, dt: float):
        """
        シーン更新とステート管理
        元のscene_change()関数を完全再現
        """
        # グローバル遷移条件（プレイヤー死亡）をチェック
        for transition in self.global_transitions:
            if transition.should_transition(game_state):
                self._change_scene(transition.target_scene, game_state, transition)
                return
        
        # 現在シーンの遷移条件をチェック
        if self.current_scene in self.transitions:
            for transition in self.transitions[self.current_scene]:
                if transition.should_transition(game_state):
                    self._change_scene(transition.target_scene, game_state, transition)
                    return
        
        # シーン別の更新処理
        self._update_current_scene(game_state, dt)
    
    def _change_scene(self, new_scene: GameScene, game_state, transition: SceneTransitionCondition):
        """シーン変更処理"""
        # 全シーンをfalseに
        for i in range(len(self.scene)):
            self.scene[i] = False
        
        # 新しいシーンをtrueに
        self.scene[new_scene] = True
        self.current_scene = new_scene
        
        # 弾丸リセット（元のreset_bullet()）はプレイヤー内で処理
        
        # セットアップ処理実行
        transition.execute_setup(game_state)
    
    def _check_title_scene_transition(self, game_state):
        """TitleSceneからの遷移判定"""
        # TitleSceneがgame_state内に存在する場合の衝突チェック
        if hasattr(game_state, 'title_scene'):
            # プロジェクタイルとスタートボタンの衝突チェック
            projectiles = game_state.player.get_projectiles()
            start_button_pos = Vector2(GameConfig.SCREEN_WIDTH // 2, GameConfig.SCREEN_HEIGHT // 2)
            start_button_radius = 50
            
            for projectile in projectiles:
                distance = projectile.position.distance_to(start_button_pos)
                if distance < start_button_radius + projectile.radius:
                    print("Scene transition triggered: START_SCREEN -> STAGE_1")
                    return True
        
        # フォールバック：従来のstart_button.hp < 0チェック
        return game_state.start_button.hp < 0
    
    def _update_current_scene(self, game_state, dt: float):
        """現在シーンの更新処理"""
        if self.current_scene == GameScene.START_SCREEN:
            self._update_start_screen(game_state, dt)
        elif self.current_scene == GameScene.STAGE_1:
            self._update_stage1(game_state, dt)
        elif self.current_scene == GameScene.STAGE_2:
            self._update_stage2(game_state, dt)
        elif self.current_scene == GameScene.STAGE_3:
            self._update_stage3(game_state, dt)
        elif self.current_scene == GameScene.ENDING:
            self._update_ending(game_state, dt)
        elif self.current_scene == GameScene.GAME_OVER:
            self._update_game_over(game_state, dt)
    
    def _update_start_screen(self, game_state, dt: float):
        """スタート画面の更新"""
        # scene0bg() 相当の背景描画
        pass
    
    def _update_stage1(self, game_state, dt: float):
        """第1ステージの更新"""
        # scene3bg() + enemy1_move() 相当
        self.stage1_counter += 1
        
        # 30フレームごとに茂み描画（元のコメント: if(cnt1%30==0){ draw_bush(); }）
        if self.stage1_counter % 30 == 0:
            # draw_bush() 処理
            pass
        
        # restart.hp = 1 の設定
        game_state.restart_button.hp = 1
    
    def _update_stage2(self, game_state, dt: float):
        """第2ステージの更新"""
        # scene3bg() + enemy2_move() 相当
        self.stage2_counter += 1
        
        # 水描画処理は元ではコメントアウト
        # if(cnt2%30==0){ draw_water(); }
    
    def _update_stage3(self, game_state, dt: float):
        """第3ステージの更新"""
        # scene3bg() + enemy3_move() 相当
        self.stage3_counter += 1
        
        # 10フレームごとにマグマ流動（元: if(cnt3%10==0){ flow_magma(); }）
        if self.stage3_counter % 10 == 0:
            # マグマ流動処理
            pass
    
    def _update_ending(self, game_state, dt: float):
        """エンディングの更新"""
        # background(255) + scene5() 相当
        pass
    
    def _update_game_over(self, game_state, dt: float):
        """ゲームオーバー画面の更新"""
        # scene3bg() + restart_UI() 相当
        pass
    
    # セットアップ関数群（元の遷移時処理を再現）
    
    def _setup_start_screen(self, game_state):
        """スタート画面セットアップ"""
        print("Setting up Start Screen")
        
        # 全敵をクリア
        game_state.enemy_manager.enemy1_list.clear()
        game_state.enemy_manager.all_enemies.clear()
        
        # 敵弾もクリア
        if hasattr(game_state.enemy_manager, 'bullet_manager') and game_state.enemy_manager.bullet_manager:
            game_state.enemy_manager.bullet_manager.clear_all_bullets()
        
        # プレイヤー弾もクリア
        game_state.player.clear_all_projectiles()
        
        # プレイヤー状態をリセット
        game_state.player.hp = GameConfig.PLAYER_MAX_HP
        game_state.player_inb_cnt = game_state.player_inb_max
        
        # 全カウンターリセット
        self.stage1_counter = 0
        self.stage2_counter = 0
        self.stage3_counter = 0
        game_state.cnt1 = 0
        game_state.cnt2 = 0
        game_state.cnt3 = 0
    
    def _setup_stage1(self, game_state):
        """第1ステージセットアップ"""
        print("Setting up Stage 1 with 3 enemies")
        
        # 全ての敵をクリア
        game_state.enemy_manager.enemy1_list.clear()
        game_state.enemy_manager.all_enemies.clear()
        
        # 敵弾もクリア
        if hasattr(game_state.enemy_manager, 'bullet_manager') and game_state.enemy_manager.bullet_manager:
            game_state.enemy_manager.bullet_manager.clear_all_bullets()
        
        # プレイヤー弾もクリア
        game_state.player.clear_all_projectiles()
        
        # プレイヤー状態をリセット
        game_state.player.hp = GameConfig.PLAYER_MAX_HP
        game_state.player_inb_cnt = game_state.player_inb_max
        
        # Enemy1を3体作成して配置
        from entities.enemy import Enemy1
        
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
            enemy.invincibility_timer = 70
            
            print(f"Enemy {i}: pos=({x}, {y}), radius={enemy.radius}, hp={enemy.hp}")
            
            # EnemyManagerの敵リストに直接追加
            game_state.enemy_manager.all_enemies.append(enemy)
            game_state.enemy_manager.enemy1_list.append(enemy)
        
        # カウンターリセット
        self.stage1_counter = 0
        game_state.cnt1 = 0
        
        print(f"Total enemies created: {len(game_state.enemy_manager.all_enemies)}")
    
    def _setup_stage2(self, game_state):
        """第2ステージセットアップ"""
        print("Setting up Stage 2")
        
        # 前ステージの敵をクリア
        game_state.enemy_manager.enemy1_list.clear()
        game_state.enemy_manager.all_enemies.clear()
        
        # 敵弾もクリア
        if hasattr(game_state.enemy_manager, 'bullet_manager') and game_state.enemy_manager.bullet_manager:
            game_state.enemy_manager.bullet_manager.clear_all_bullets()
        
        # プレイヤー弾もクリア
        game_state.player.clear_all_projectiles()
        
        # Enemy2をセットアップ
        from entities.enemy import Enemy2
        if not hasattr(game_state.enemy_manager, 'enemy2') or game_state.enemy_manager.enemy2 is None:
            game_state.enemy_manager.enemy2 = Enemy2(GameConfig.SCREEN_WIDTH // 2, 100, 50, 80)
        else:
            # 既存のenemy2をリセット
            game_state.enemy_manager.enemy2.hp = 80
            game_state.enemy_manager.enemy2.position.x = GameConfig.SCREEN_WIDTH // 2
            game_state.enemy_manager.enemy2.position.y = 100
            game_state.enemy_manager.enemy2.active = True
            game_state.enemy_manager.enemy2.invincibility_timer = 70
        
        # enemy2をall_enemiesにも追加
        game_state.enemy_manager.all_enemies.append(game_state.enemy_manager.enemy2)
        
        # 第二ステージ背景生成（元: generate_scene2bg();）
        from utils.ui_renderer import UIRenderer
        ui_renderer = UIRenderer()
        bg_data = ui_renderer.generate_scene2bg()
        game_state.background_data['scene2'] = bg_data
        print("Generated Scene 2 background")
        
        # カウンターリセット
        self.stage2_counter = 0
        game_state.cnt2 = 0
    
    def _setup_stage3(self, game_state):
        """第3ステージセットアップ"""
        print("Setting up Stage 3")
        
        # 前ステージの敵をクリア
        game_state.enemy_manager.enemy1_list.clear()
        game_state.enemy_manager.all_enemies.clear()
        
        # 敵弾もクリア
        if hasattr(game_state.enemy_manager, 'bullet_manager') and game_state.enemy_manager.bullet_manager:
            game_state.enemy_manager.bullet_manager.clear_all_bullets()
        
        # プレイヤー弾もクリア
        game_state.player.clear_all_projectiles()
        
        # Enemy3をセットアップ
        from entities.enemy import Enemy3
        if not hasattr(game_state.enemy_manager, 'enemy3') or game_state.enemy_manager.enemy3 is None:
            game_state.enemy_manager.enemy3 = Enemy3(GameConfig.SCREEN_WIDTH // 2, 100, 50, 160)
        else:
            # 既存のenemy3をリセット
            game_state.enemy_manager.enemy3.hp = 160
            game_state.enemy_manager.enemy3.position.x = GameConfig.SCREEN_WIDTH // 2
            game_state.enemy_manager.enemy3.position.y = 100
            game_state.enemy_manager.enemy3.active = True
            game_state.enemy_manager.enemy3.invincibility_timer = 70
        
        # enemy3をall_enemiesにも追加
        game_state.enemy_manager.all_enemies.append(game_state.enemy_manager.enemy3)
        
        # 第三ステージ背景生成（元: generate_bg(3);）
        from utils.ui_renderer import UIRenderer
        ui_renderer = UIRenderer()
        bg_data = ui_renderer.generate_bg(3)
        game_state.background_data['scene3'] = bg_data
        print("Generated Scene 3 background")
        
        # カウンターリセット
        self.stage3_counter = 0
        game_state.cnt3 = 0
    
    def _setup_ending(self, game_state):
        """エンディングセットアップ"""
        print("Setting up Ending")
        
        # 全敵をクリア
        game_state.enemy_manager.enemy1_list.clear()
        game_state.enemy_manager.all_enemies.clear()
        
        # 敵弾もクリア
        if hasattr(game_state.enemy_manager, 'bullet_manager') and game_state.enemy_manager.bullet_manager:
            game_state.enemy_manager.bullet_manager.clear_all_bullets()
        
        # プレイヤー弾もクリア
        game_state.player.clear_all_projectiles()
    
    def _setup_game_over(self, game_state):
        """ゲームオーバーセットアップ"""
        print("Setting up Game Over")
        
        # 全敵をクリア
        game_state.enemy_manager.enemy1_list.clear()
        game_state.enemy_manager.all_enemies.clear()
        
        # 敵弾もクリア
        if hasattr(game_state.enemy_manager, 'bullet_manager') and game_state.enemy_manager.bullet_manager:
            game_state.enemy_manager.bullet_manager.clear_all_bullets()
        
        # プレイヤー弾もクリア
        game_state.player.clear_all_projectiles()
        
        # プレイヤーHP復活
        game_state.player.hp = GameConfig.PLAYER_MAX_HP
    
    def _restart_game(self, game_state):
        """ゲーム再開処理"""
        # restart() + generate_scene1bg() 相当
        self._reset_game_state(game_state)
    
    def _reset_game_state(self, game_state):
        """ゲーム状態のリセット（元のrestart()関数相当）"""
        # 全てのゲーム状態を初期値にリセット
        game_state.player.hp = GameConfig.PLAYER_MAX_HP
        
        # 敵の状態リセット
        for enemy in game_state.enemy_manager.enemy1_list:
            enemy.hp = GameConfig.ENEMY1_HP
            enemy.active = True
        
        game_state.enemy_manager.enemy2.hp = GameConfig.ENEMY2_HP
        game_state.enemy_manager.enemy2.active = True
        
        game_state.enemy_manager.enemy3.hp = GameConfig.ENEMY3_HP  
        game_state.enemy_manager.enemy3.active = True
        
        # カウンターリセット
        self.stage1_counter = 0
        self.stage2_counter = 0
        self.stage3_counter = 0
    
    def is_scene_active(self, scene: GameScene) -> bool:
        """指定されたシーンがアクティブかチェック"""
        return self.scene[scene]
    
    def get_current_scene(self) -> GameScene:
        """現在のアクティブシーンを取得"""
        return self.current_scene
    
    def _transition_to_scene(self, target_scene: GameScene, game_state):
        """シーンを強制的に遷移させる"""
        print(f"Transitioning from {self.current_scene} to {target_scene}")
        
        # 全シーンをfalseに
        for i in range(len(self.scene)):
            self.scene[i] = False
        
        # 新しいシーンをtrueに
        self.scene[target_scene] = True
        self.current_scene = target_scene
        
        # セットアップ処理を実行
        if target_scene == GameScene.START_SCREEN:
            self._setup_start_screen(game_state)
        elif target_scene == GameScene.STAGE_1:
            self._setup_stage1(game_state)
        elif target_scene == GameScene.STAGE_2:
            self._setup_stage2(game_state)
        elif target_scene == GameScene.STAGE_3:
            self._setup_stage3(game_state)
        elif target_scene == GameScene.ENDING:
            self._setup_ending(game_state)
        elif target_scene == GameScene.GAME_OVER:
            self._setup_game_over(game_state)