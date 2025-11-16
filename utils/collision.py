"""
衝突判定のユーティリティ
"""
from utils.math_utils import Vector2
from typing import Tuple


class CollisionDetector:
    """衝突判定クラス"""
    
    @staticmethod
    def circle_circle(pos1: Vector2, radius1: float, 
                     pos2: Vector2, radius2: float) -> bool:
        """円と円の衝突判定"""
        distance = pos1.distance_to(pos2)
        return distance <= (radius1 + radius2)
    
    @staticmethod
    def point_in_circle(point: Vector2, center: Vector2, radius: float) -> bool:
        """点が円の中にあるかの判定"""
        return point.distance_to(center) <= radius
    
    @staticmethod
    def circle_rect(circle_pos: Vector2, circle_radius: float,
                   rect_pos: Vector2, rect_width: float, rect_height: float) -> bool:
        """円と矩形の衝突判定"""
        # 矩形の最も近い点を計算
        closest_x = max(rect_pos.x, min(circle_pos.x, rect_pos.x + rect_width))
        closest_y = max(rect_pos.y, min(circle_pos.y, rect_pos.y + rect_height))
        
        # 円の中心と最も近い点の距離を計算
        distance = Vector2(circle_pos.x - closest_x, circle_pos.y - closest_y).length
        return distance <= circle_radius
    
    @staticmethod
    def point_in_rect(point: Vector2, rect_pos: Vector2, 
                     rect_width: float, rect_height: float) -> bool:
        """点が矩形の中にあるかの判定"""
        return (rect_pos.x <= point.x <= rect_pos.x + rect_width and
                rect_pos.y <= point.y <= rect_pos.y + rect_height)