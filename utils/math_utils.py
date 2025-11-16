"""
数学関連のユーティリティ
"""
import math
import random
from typing import Tuple


class Vector2:
    """2次元ベクトルクラス"""
    
    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float):
        return Vector2(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar: float):
        return Vector2(self.x / scalar, self.y / scalar)
    
    def __repr__(self):
        return f"Vector2({self.x}, {self.y})"
    
    @property
    def length(self) -> float:
        """ベクトルの長さ"""
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    @property
    def length_squared(self) -> float:
        """ベクトルの長さの二乗（計算コスト削減用）"""
        return self.x * self.x + self.y * self.y
    
    def normalized(self):
        """正規化されたベクトルを返す"""
        length = self.length
        if length == 0:
            return Vector2(0, 0)
        return Vector2(self.x / length, self.y / length)
    
    def distance_to(self, other) -> float:
        """他のベクトルとの距離"""
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)
    
    def angle_to(self, other) -> float:
        """他のベクトルへの角度"""
        return math.atan2(other.y - self.y, other.x - self.x)
    
    def rotate(self, angle: float):
        """ベクトルを回転させる"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        new_x = self.x * cos_a - self.y * sin_a
        new_y = self.x * sin_a + self.y * cos_a
        return Vector2(new_x, new_y)
    
    def to_tuple(self) -> Tuple[float, float]:
        """タプルに変換"""
        return (self.x, self.y)


class MathUtils:
    """数学関連のユーティリティ関数"""
    
    @staticmethod
    def clamp(value: float, min_val: float, max_val: float) -> float:
        """値を指定範囲内にクランプ"""
        return max(min_val, min(max_val, value))
    
    @staticmethod
    def lerp(a: float, b: float, t: float) -> float:
        """線形補間"""
        return a + (b - a) * t
    
    @staticmethod
    def map_range(value: float, in_min: float, in_max: float, 
                  out_min: float, out_max: float) -> float:
        """値の範囲を変換"""
        return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    
    @staticmethod
    def distance(x1: float, y1: float, x2: float, y2: float) -> float:
        """2点間の距離"""
        dx = x2 - x1
        dy = y2 - y1
        return math.sqrt(dx * dx + dy * dy)
    
    @staticmethod
    def angle_between(x1: float, y1: float, x2: float, y2: float) -> float:
        """2点間の角度"""
        return math.atan2(y2 - y1, x2 - x1)
    
    @staticmethod
    def random_range(min_val: float, max_val: float) -> float:
        """指定範囲の乱数"""
        return random.uniform(min_val, max_val)
    
    @staticmethod
    def random_gaussian(mean: float = 0, std: float = 1) -> float:
        """ガウス分布の乱数"""
        return random.gauss(mean, std)