"""
シーン管理クラス
"""
from typing import Dict, Optional
import pygame
from config.settings import SceneType
from utils.math_utils import Vector2


class Scene:
    """基底シーンクラス"""
    
    def __init__(self, scene_type: SceneType):
        self.scene_type = scene_type
        self.active = False
    
    def enter(self):
        """シーン開始時の処理"""
        self.active = True
    
    def exit(self):
        """シーン終了時の処理"""
        self.active = False
    
    def update(self, dt: float, mouse_pos: Vector2, mouse_pressed: bool, keys_pressed: set):
        """シーンの更新処理"""
        pass
    
    def render(self, screen: pygame.Surface):
        """シーンの描画処理"""
        pass
    
    def handle_key_down(self, key: int):
        """キー押下処理"""
        pass
    
    def handle_key_up(self, key: int):
        """キー離し処理"""
        pass
    
    def handle_mouse_down(self, pos: tuple):
        """マウス押下処理"""
        pass
    
    def handle_mouse_up(self, pos: tuple):
        """マウス離し処理"""
        pass
    
    def handle_mouse_move(self, pos: tuple):
        """マウス移動処理"""
        pass


class SceneManager:
    """シーン管理クラス"""
    
    def __init__(self):
        self.scenes: Dict[SceneType, Scene] = {}
        self.current_scene: Optional[Scene] = None
        self.current_scene_type: Optional[SceneType] = None
        
        # 初期化（まずはタイトルシーンを作成）
        self.setup_scenes()
        self.change_scene(SceneType.TITLE)
    
    def setup_scenes(self):
        """シーンの初期化"""
        # 実際のシーンクラスをインポート
        from scenes.game_scene import TitleScene, GameScene, GameOverScene, GameClearScene
        
        # 各シーンを初期化
        self.scenes[SceneType.TITLE] = TitleScene()
        self.scenes[SceneType.STAGE_1] = GameScene(SceneType.STAGE_1)
        self.scenes[SceneType.STAGE_2] = GameScene(SceneType.STAGE_2)
        self.scenes[SceneType.STAGE_3] = GameScene(SceneType.STAGE_3)
        self.scenes[SceneType.GAME_CLEAR] = GameClearScene()
        self.scenes[SceneType.GAME_OVER] = GameOverScene()
        self.scenes[SceneType.DEBUG] = Scene(SceneType.DEBUG)
    
    def change_scene(self, scene_type: SceneType):
        """シーンを切り替える"""
        if self.current_scene:
            self.current_scene.exit()
        
        self.current_scene = self.scenes.get(scene_type)
        self.current_scene_type = scene_type
        
        if self.current_scene:
            self.current_scene.enter()
    
    def update(self, dt: float, mouse_pos: Vector2, mouse_pressed: bool, keys_pressed: set):
        """現在のシーンを更新"""
        if self.current_scene:
            next_scene = self.current_scene.update(dt, mouse_pos, mouse_pressed, keys_pressed)
            if next_scene and next_scene != self.current_scene_type:
                self.change_scene(next_scene)
    
    def render(self, screen: pygame.Surface):
        """現在のシーンを描画"""
        if self.current_scene:
            self.current_scene.render(screen)
    
    def handle_key_down(self, key: int):
        """キー押下処理を現在のシーンに渡す"""
        if self.current_scene:
            self.current_scene.handle_key_down(key)
    
    def handle_key_up(self, key: int):
        """キー離し処理を現在のシーンに渡す"""
        if self.current_scene:
            self.current_scene.handle_key_up(key)
    
    def handle_mouse_down(self, pos: tuple):
        """マウス押下処理を現在のシーンに渡す"""
        if self.current_scene:
            next_scene = self.current_scene.handle_mouse_down(pos)
            if next_scene and next_scene != self.current_scene_type:
                self.change_scene(next_scene)
    
    def handle_mouse_up(self, pos: tuple):
        """マウス離し処理を現在のシーンに渡す"""
        if self.current_scene:
            self.current_scene.handle_mouse_up(pos)
    
    def handle_mouse_move(self, pos: tuple):
        """マウス移動処理を現在のシーンに渡す"""
        if self.current_scene:
            self.current_scene.handle_mouse_move(pos)