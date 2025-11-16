"""
色変換ユーティリティ
ProcessingのHSB色空間をPygameのRGBに変換
"""
import colorsys


class ProcessingColorConverter:
    """ProcessingのcolorMode設定に対応した色変換"""
    
    @staticmethod
    def hsb_to_rgb(h: float, s: float, b: float, h_max: float = 360, s_max: float = 100, b_max: float = 100) -> tuple:
        """
        ProcessingのHSB色をPygameのRGB色に変換
        
        Args:
            h: 色相 (0 to h_max)
            s: 彩度 (0 to s_max) 
            b: 明度 (0 to b_max)
            h_max: 色相の最大値 (Processing: 360)
            s_max: 彩度の最大値 (Processing: 100)
            b_max: 明度の最大値 (Processing: 100)
            
        Returns:
            tuple: (r, g, b) 各値は0-255
        """
        # Processing HSBを標準HSVに正規化
        h_normalized = (h % h_max) / h_max  # 0.0 - 1.0
        s_normalized = min(s / s_max, 1.0)   # 0.0 - 1.0
        v_normalized = min(b / b_max, 1.0)   # 0.0 - 1.0
        
        # HSVからRGBに変換 (colorsysは0.0-1.0の範囲)
        r, g, b = colorsys.hsv_to_rgb(h_normalized, s_normalized, v_normalized)
        
        # 0-255の範囲に変換
        return (int(r * 255), int(g * 255), int(b * 255))
    
    @staticmethod
    def processing_color(h: float, s: float = None, b: float = None) -> tuple:
        """
        Processingの色指定を再現
        fill(h) -> グレースケール
        fill(h, s, b) -> HSB色
        """
        if s is None and b is None:
            # グレースケール
            gray = int(min(h, 255))
            return (gray, gray, gray)
        elif s is not None and b is not None:
            # HSB色
            return ProcessingColorConverter.hsb_to_rgb(h, s, b)
        else:
            raise ValueError("Invalid color parameters")


class ProcessingColors:
    """元のProcessingコードで使用されている色定義"""
    
    # 敵1の色 (HSB 360,100,100 モード)
    ENEMY1_BODY_NORMAL = ProcessingColorConverter.hsb_to_rgb(104, 70, 50)      # fill(104,70,50)
    ENEMY1_BODY_INVINCIBLE = ProcessingColorConverter.hsb_to_rgb(0, 60, 90)    # fill(0,60,90)
    ENEMY1_DETAIL_NORMAL = ProcessingColorConverter.hsb_to_rgb(30, 80, 35)     # fill(30,80,35)
    ENEMY1_DETAIL_INVINCIBLE = ProcessingColorConverter.hsb_to_rgb(0, 60, 60)  # fill(0,60,60)
    
    # UI用の色
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    CYAN = (0, 255, 255)
    GRAY = (128, 128, 128)