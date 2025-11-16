"""
ゲーム設定と定数
"""
from enum import Enum


class GameConfig:
    """ゲーム全体の設定定数"""
    
    # 画面設定
    SCREEN_WIDTH = 1237  # 1980*5/8
    SCREEN_HEIGHT = 810  # 1080*3/4
    FPS = 60
    
    # プレイヤー設定
    PLAYER_RADIUS = 25  # ellipse_round/2
    PLAYER_MAX_HP = 3
    PLAYER_INVINCIBILITY_TIME = 60  # inb_max
    
    # スリングショット設定
    SLING_RESISTANCE = 5
    SLING_MAX_COUNT = 15  # sling_cnt_mx
    SLING_MAX_DISTANCE = 200
    
    # 弾丸設定
    MAX_BALLS = 3  # ball_max
    MAX_BULLETS = 800  # bullet_max
    BULLET_RADIUS = 10
    ELLIPSE_ROUND = 50  # 元のellipse_roundの値
    
    # 敵設定（オリジナルの値）
    ENEMY1_RADIUS = 50  # オリジナル: new Enemy(-1,-1,50,16)
    ENEMY1_HP = 16
    ENEMY2_RADIUS = 25
    ENEMY2_HP = 80
    ENEMY3_RADIUS = 50
    ENEMY3_HP = 120
    
    # UI設定
    UI_BLOCK_SIZE = 10  # br
    HEART_SIZE = 15
    
    # 物理設定
    PHYSICS_FORCE = 0.2
    PHYSICS_SPRING_K = 1
    PHYSICS_MASS = 1
    NEARLY_ZERO = 0.000001
    NEARLY_INF = 1 / NEARLY_ZERO


class EnemyType(Enum):
    """敵の種類"""
    BASIC = 1
    BOSS_1 = 2  # enemy2
    BOSS_2 = 3  # enemy3
    PIXIE = 4   # px1, px2


class SceneType(Enum):
    """シーンの種類"""
    TITLE = 0
    STAGE_1 = 1
    STAGE_2 = 2
    STAGE_3 = 3
    GAME_CLEAR = 4
    GAME_OVER = 5
    DEBUG = 6


class Colors:
    """色の定数"""
    # RGB色
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 128, 0)
    CYAN = (0, 255, 255)
    GRAY = (128, 128, 128)
    
    # プレイヤー色
    PLAYER_BODY = (255, 255, 0)
    PLAYER_EYE_WHITE = (255, 255, 255)
    PLAYER_EYE_BLACK = (0, 0, 0)
    
    # 敵色 (HSB値をRGBに変換したもの)
    ENEMY_RED = (255, 0, 0)
    ENEMY_BLUE = (0, 50, 210)
    ENEMY_ORANGE = (255, 128, 0)


class SoundPaths:
    """サウンドファイルのパス"""
    HIT_SOUND = "assets/sounds/hit.wav"
    KILL_SOUND = "assets/sounds/kill.wav"
    DAMAGE_SOUND = "assets/sounds/damage.wav"
    DEATH_SOUND = "assets/sounds/death.wav"
    RESTART_SOUND = "assets/sounds/restart.wav"
    SLING_SOUND = "assets/sounds/sling.wav"
    BGM = "assets/sounds/bgm.wav"


class ImagePaths:
    """画像ファイルのパス"""
    ENEMY1 = "assets/images/enemy1.png"
    FIELD1 = "assets/images/field1.png"
    MAGMA = "assets/images/magma.jpg"