"""
UI描画システム - 元のUI.pdeを完全再現
オリジナルのハート描画、ブロック描画システムを忠実に再現
"""
import pygame
from config.settings import GameConfig, Colors


class UIRenderer:
    """オリジナルのUI.pdeの描画機能を完全再現"""
    
    def __init__(self):
        # オリジナルのbr値（ブロックサイズ）
        self.br = 10  # final float br=10;
        
    def draw_player_heart(self, screen: pygame.Surface, n: int):
        """
        プレイヤーハート描画（元のdraw_player_heart関数を完全再現）
        オリジナル: void draw_player_heart(int n)
        """
        # 元のコード: float r=15; float xr=r; float x=10+n*(7*r+10); float y=10;
        r = 15
        xr = r
        x = 10 + n * (7 * r + 10)
        y = 10
        
        # HSB色設定（元: colorMode(HSB,360,100,100); fill(0,70,100);）
        # HSB(0,70,100) → 赤色
        color = Colors.RED  # 赤色でハートを描画
        
        # 元のコードのrect描画を完全再現
        rects = [
            # 左部分
            (x, y + r, r, r),
            (x, y + 2*r, r, r), 
            (x, y + 3*r, r, r),
            (x + xr, y, r, r),
            (x + xr, y + r, r, r),
            (x + xr, y + r*2, r, r),
            (x + xr, y + r*3, r, r),
            (x + xr, y + r*4, r, r),
            (x + xr*2, y + r, r, r),
            (x + xr*2, y + r*2, r, r),
            (x + xr*2, y + r*3, r, r),
            (x + xr*2, y + r*4, r, r),
            (x + xr*2, y + r*5, r, r),
            (x + r*3, y + 2*r, r, r),
            (x + r*3, y + 3*r, r, r),
            (x + r*3, y + 4*r, r, r),
            (x + r*3, y + 5*r, r, r),
            (x + r*3, y + 6*r, r, r),
        ]
        
        # 右部分（元: x=x+r*6; xr=-r;）
        x_right = x + r * 6
        xr_right = -r
        right_rects = [
            (x_right, y + r, r, r),
            (x_right, y + 2*r, r, r),
            (x_right, y + 3*r, r, r),
            (x_right + xr_right, y, r, r),
            (x_right + xr_right, y + r, r, r),
            (x_right + xr_right, y + r*2, r, r),
            (x_right + xr_right, y + r*3, r, r),
            (x_right + xr_right, y + r*4, r, r),
            (x_right + xr_right*2, y + r, r, r),
            (x_right + xr_right*2, y + r*2, r, r),
            (x_right + xr_right*2, y + r*3, r, r),
            (x_right + xr_right*2, y + r*4, r, r),
            (x_right + xr_right*2, y + r*5, r, r),
        ]
        
        # 全てのrectを描画
        for rect_x, rect_y, rect_w, rect_h in rects + right_rects:
            pygame.draw.rect(screen, color, (rect_x, rect_y, rect_w, rect_h))
    
    def player_HP(self, screen: pygame.Surface, player_hp: int, scene: list):
        """
        プレイヤーHP表示（元のplayer_HP関数を完全再現）
        元: void player_HP(){ if(!scene[0]&&!scene[4]&&!scene[5]){ for(int i=0;i<player_hp;i++){ fill(255,0,0); draw_player_heart(i); } } }
        """
        # 元の条件: !scene[0]&&!scene[4]&&!scene[5]
        # scene[0]=タイトル, scene[4]=?, scene[5]=ゲームオーバー
        if not (scene[0] or scene[4] or scene[5]):
            for i in range(player_hp):
                self.draw_player_heart(screen, i)
    
    def HP_bar(self, screen: pygame.Surface, x: float, y: float, MAX_HP: float, HP: float, range_val: float):
        """
        HPバー描画（元のHP_bar関数を完全再現）
        元: void HP_bar(float x,float y,float MAX_HP,float HP,float range)
        """
        # 元: float HP_range=range*HP/MAX_HP;
        HP_range = range_val * HP / MAX_HP
        
        # 元: stroke(1); fill(0,255,0); rect(x,y-range/5,HP_range,100/5);
        green_rect = pygame.Rect(x, y - range_val/5, HP_range, 100/5)
        pygame.draw.rect(screen, (0, 255, 0), green_rect)
        pygame.draw.rect(screen, (0, 0, 0), green_rect, 1)  # stroke(1)
        
        # 元: fill(255,0,0); rect(x+HP_range,y-range/5,range-HP_range,100/5);
        red_rect = pygame.Rect(x + HP_range, y - range_val/5, range_val - HP_range, 100/5)
        pygame.draw.rect(screen, (255, 0, 0), red_rect)
        pygame.draw.rect(screen, (0, 0, 0), red_rect, 1)  # stroke(1)
    
    def show_enemy_HP(self, screen: pygame.Surface, enemy_x: float, enemy_y: float, 
                     max_hp: float, current_hp: float, range_val: float, scene: list):
        """
        敵HP表示（元のshow_enemy_HP関数を完全再現）
        元: void show_enemy_HP(Enemy e,float mx,float rng)
        """
        if current_hp > 0:
            if not scene[3]:  # シーン3以外
                # 元: HP_bar(e.x-50,e.y-50,mx,e.hp,rng);
                self.HP_bar(screen, enemy_x - 50, enemy_y - 50, max_hp, current_hp, range_val)
            elif scene[3]:   # シーン3
                # 元: HP_bar(e.x-100,e.y-120,mx,e.hp,rng);
                self.HP_bar(screen, enemy_x - 100, enemy_y - 120, max_hp, current_hp, range_val)
    
    def show_damage(self, screen: pygame.Surface, x: float, y: float, d: float, font: pygame.font.Font, hit_timer: int):
        """
        ダメージ表示（元のshow_demage関数を完全再現）
        元: void show_demage(float x,float y,float d)
        """
        # 元: textSize(30); fill(255,0,0); text(-abs((int)d),x+100,y+20);
        damage_text = font.render(str(-abs(int(d))), True, (255, 0, 0))
        screen.blit(damage_text, (x + 100, y + 20))
        
        # hit_timerの管理は呼び出し側で行う（元: hit_timer++; if(hit_timer>90){ hit=false; hit_timer=0; }）
        return hit_timer + 1
    
    def draw_block_bg(self, screen: pygame.Surface, H_rnd: list, S_rnd: list, B_rnd: list):
        """
        ブロック背景描画（元のUI.pdeの背景システム）
        元のbr（ブロックサイズ）を使った背景描画
        """
        # 元: int w_br=(int)(width/br)+1; int h_br=(int)(height/br)+1;
        w_br = int(GameConfig.SCREEN_WIDTH / self.br) + 1
        h_br = int(GameConfig.SCREEN_HEIGHT / self.br) + 1
        
        for i in range(w_br):
            for j in range(h_br):
                if i < len(H_rnd) and j < len(H_rnd[i]):
                    # HSB値をRGB値に変換して描画
                    h = H_rnd[i][j] % 360
                    s = S_rnd[i][j] % 100
                    b = B_rnd[i][j] % 100
                    
                    # HSBからRGBへの変換（簡易版）
                    rgb_color = self._hsb_to_rgb(h, s, b)
                    
                    # 元: rect(br*i,br*j,br,br);
                    pygame.draw.rect(screen, rgb_color, 
                                   (self.br * i, self.br * j, self.br, self.br))
    
    def _hsb_to_rgb(self, h: float, s: float, b: float) -> tuple:
        """HSB色空間からRGB色空間への変換"""
        import colorsys
        h_norm = h / 360.0
        s_norm = s / 100.0
        b_norm = b / 100.0
        
        r, g, b_rgb = colorsys.hsv_to_rgb(h_norm, s_norm, b_norm)
        return (int(r * 255), int(g * 255), int(b_rgb * 255))
    
    def generate_scene1bg(self) -> tuple:
        """シーン1背景生成（元のgenerate_scene1bg関数を完全再現）"""
        import random
        
        w_br = int(GameConfig.SCREEN_WIDTH / self.br) + 1
        h_br = int(GameConfig.SCREEN_HEIGHT / self.br) + 1
        
        # H_rnd, S_rnd, B_rnd配列の初期化
        H_rnd = [[0 for _ in range(h_br)] for _ in range(w_br)]
        S_rnd = [[0 for _ in range(h_br)] for _ in range(w_br)]
        B_rnd = [[0 for _ in range(h_br)] for _ in range(w_br)]
        
        # 基本背景生成（元のコード）
        for i in range(w_br):
            for j in range(h_br):
                H_rnd[i][j] = 30 + int(random.random() * 5) - 25
                S_rnd[i][j] = int(random.random() * 5) + 5 + 10
                B_rnd[i][j] = 75 + int(random.random() * 5) + 20
        
        # 茂み生成（元のbush生成ロジック）
        bush = 20
        bush_posx = [0] * bush
        bush_posy = [0] * bush
        r = 9
        
        for i in range(bush):
            bush_posx[i] = (i % 5) * 30 + 15
            bush_posy[i] = (i // 5) * 30 + 10
            if 4 < i < 10:
                bush_posx[i] = (i % 5) * 30 + 15 - 15
                
            for j in range(-r, r):
                xr = j + bush_posx[i]
                for k in range(-r, r):
                    yr = k + bush_posy[i]
                    # dist計算（元: dist(xr+random(0.5),yr+random(0.5),bush_posx[i],bush_posy[i])<r）
                    dx = (xr + random.random() * 0.5) - bush_posx[i]
                    dy = (yr + random.random() * 0.5) - bush_posy[i]
                    if (dx*dx + dy*dy)**0.5 < r:
                        if 0 <= xr < w_br and 0 <= yr < h_br:
                            H_rnd[xr][yr] = 120 + int(random.random() * 5) - 25
                            S_rnd[xr][yr] = int(random.random() * 5) + 5 + 10
                            B_rnd[xr][yr] = 70 + int(random.random() * 5) + 10
        
        return (H_rnd, S_rnd, B_rnd)
    
    def generate_scene2bg(self) -> tuple:
        """シーン2背景生成（元のgenerate_scene2bg関数を完全再現）"""
        import random
        
        w_br = int(GameConfig.SCREEN_WIDTH / self.br) + 1
        h_br = int(GameConfig.SCREEN_HEIGHT / self.br) + 1
        
        H_rnd = [[0 for _ in range(h_br)] for _ in range(w_br)]
        S_rnd = [[0 for _ in range(h_br)] for _ in range(w_br)]
        B_rnd = [[0 for _ in range(h_br)] for _ in range(w_br)]
        
        for i in range(w_br):  # 湖
            for j in range(h_br):
                rnd = 5
                y1 = -((i - w_br/2 - random.random() * rnd) * (i - w_br/2 + random.random() * rnd)) / 200 + 30 + random.random() * rnd
                H_rnd[i][j] = int(random.random() * 5) + 90 - int(random.random() * j * 5)
                S_rnd[i][j] = int(random.random() * 5) + 20
                B_rnd[i][j] = 90 + int(random.random() * 5)
        
        return (H_rnd, S_rnd, B_rnd)
    
    def generate_bg(self, scene_number: int) -> tuple:
        """背景生成（元のgenerate_bg関数を完全再現）"""
        import random
        
        w_br = int(GameConfig.SCREEN_WIDTH / self.br) + 1
        h_br = int(GameConfig.SCREEN_HEIGHT / self.br) + 1
        
        H_rnd = [[0 for _ in range(h_br)] for _ in range(w_br)]
        S_rnd = [[0 for _ in range(h_br)] for _ in range(w_br)]
        B_rnd = [[0 for _ in range(h_br)] for _ in range(w_br)]
        
        # 基本背景色決定
        rnd = 0
        if scene_number == 1: rnd = 120
        elif scene_number == 2: rnd = 210
        elif scene_number == 3: rnd = 0
        
        for i in range(w_br):
            for j in range(h_br):
                if scene_number == 5:  # ゲームクリア画面
                    H_rnd[i][j] = int(random.random() * 360)
                    S_rnd[i][j] = int(random.random() * 15)
                    B_rnd[i][j] = 60 + int(random.random() * 15)
                else:
                    # 元: H_rnd[i][j]=120+(int)random(5); 全ステージ共通
                    H_rnd[i][j] = 120 + int(random.random() * 5)
                    S_rnd[i][j] = 10 + int(random.random() * 5)
                    B_rnd[i][j] = 90 + int(random.random() * 5)
        
        return (H_rnd, S_rnd, B_rnd)
    
    def scene0bg(self, screen: pygame.Surface):
        """シーン0背景（タイトル画面、元のscene0bg関数）"""
        # 元: colorMode(HSB,100); background(60,30,90);
        # HSB(60,30,90) をRGBに変換
        color = self._hsb_to_rgb(60 * 3.6, 30, 90)  # HSB(100)スケールをHSB(360,100,100)に変換
        screen.fill(color)
    
    def scene_bg(self, screen: pygame.Surface, H_rnd: list, S_rnd: list, B_rnd: list):
        """シーン背景描画（元のscene2bg/scene3bg関数を統合）"""
        # 元: colorMode(HSB,360,100,100);
        w_br = int(GameConfig.SCREEN_WIDTH / self.br) + 1
        h_br = int(GameConfig.SCREEN_HEIGHT / self.br) + 1
        
        for i in range(min(len(H_rnd), w_br)):
            for j in range(min(len(H_rnd[i]), h_br)):
                # 元: fill(H_rnd[i][j],S_rnd[i][j],B_rnd[i][j]); rect(br*i,br*j,br,br);
                h = H_rnd[i][j] % 360
                s = S_rnd[i][j] % 100
                b = B_rnd[i][j] % 100
                
                rgb_color = self._hsb_to_rgb(h, s, b)
                pygame.draw.rect(screen, rgb_color, (self.br * i, self.br * j, self.br, self.br))
    
    def draw_bush_animated(self, H_bg: list, S_bg: list, B_bg: list) -> tuple:
        """
        アニメーションする茂み描画（元のdraw_bush関数を完全再現）
        毎フレーム呼び出して茂みを揺らす効果を実現
        """
        import random
        
        w_br = int(GameConfig.SCREEN_WIDTH / self.br) + 1
        h_br = int(GameConfig.SCREEN_HEIGHT / self.br) + 1
        bush = 20
        bush_posx = [0] * bush
        bush_posy = [0] * bush
        r = 9
        
        # 背景をベースにリセット（元: H_rnd[i][j]=H_bg[i][j];）
        H_rnd = [[H_bg[i][j] for j in range(len(H_bg[i]))] for i in range(len(H_bg))]
        S_rnd = [[S_bg[i][j] for j in range(len(S_bg[i]))] for i in range(len(S_bg))]
        B_rnd = [[B_bg[i][j] for j in range(len(B_bg[i]))] for i in range(len(B_bg))]
        
        # 茂みのアニメーション位置計算（毎フレーム変化）
        for i in range(bush):
            # 元: bush_posx[i]=i%5*30+15+(int)random(2)-1;
            bush_posx[i] = (i % 5) * 30 + 15 + int(random.random() * 2) - 1
            bush_posy[i] = (i // 5) * 30 + 10 + int(random.random() * 2) - 1
            
            # 特定の茂みの位置調整（元: if(i>4&&i<10)）
            if 4 < i < 10:
                bush_posx[i] = (i % 5) * 30 + 15 - 15 + int(random.random() * 2) - 1
            
            # 茂みの各ピクセルを描画
            for j in range(-r, r):
                xr = j + bush_posx[i]
                for k in range(-r, r):
                    yr = k + bush_posy[i]
                    
                    # 元: if(dist(xr+random(2)-1,yr+random(2)-1,bush_posx[i],bush_posy[i])<r)
                    # ランダムな揺れを追加した距離計算
                    rand_x = xr + random.random() * 2 - 1
                    rand_y = yr + random.random() * 2 - 1
                    dx = rand_x - bush_posx[i]
                    dy = rand_y - bush_posy[i]
                    distance = (dx * dx + dy * dy) ** 0.5
                    
                    if distance < r:
                        if 0 <= xr < w_br and 0 <= yr < h_br:
                            # 茂みの色（緑系）で上書き
                            H_rnd[xr][yr] = 120 + int(random.random() * 5) - 25
                            S_rnd[xr][yr] = int(random.random() * 5) + 5 + 10
                            B_rnd[xr][yr] = 70 + int(random.random() * 5) + 10
        
        return (H_rnd, S_rnd, B_rnd)
    
    def generate_animated_background(self, scene_type: str, base_bg_data: tuple) -> tuple:
        """
        アニメーション付き背景を生成
        scene_type: 'scene1', 'scene2', etc.
        base_bg_data: (H_bg, S_bg, B_bg) ベース背景データ
        """
        if scene_type == 'scene1' and base_bg_data:
            # シーン1のみ茂みアニメーションあり
            H_bg, S_bg, B_bg = base_bg_data
            return self.draw_bush_animated(H_bg, S_bg, B_bg)
        else:
            # 他のシーンは静的背景
            return base_bg_data