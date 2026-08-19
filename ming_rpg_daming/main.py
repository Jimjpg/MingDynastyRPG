# -*- coding: utf-8 -*-
"""
《大明王朝》复古像素RPG - 主程序
技术栈: Python + Pygame
玩法: 地图探索 / 等级挂机 / 装备收集 / 野怪战斗 / 主线剧情
操作: 方向键移动 | 空格砍树/交互 | G挂机 | E装备面板 | F1地图编辑器 | 1-9选地块
"""
import pygame
import json
import os
import sys
import random
import math

# ============================================================
# 【可调参数】直接修改下面数值即可调试游戏，无需改动其他代码
# ============================================================
MOVE_SPEED = 3            # 【移动速度】像素/帧，范围1-6，越大越快
EXP_MULTIPLIER = 1.0      # 【经验倍率】全局经验获取倍率，1.0为标准
AFK_EXP_PER_SEC = 8       # 【挂机经验】挂机模式每秒获得经验值
DROP_RATE_TREE = 0.35     # 【砍树掉落率】0~1，砍树获得装备的概率
DROP_RATE_MONSTER = 0.65  # 【怪物掉落率】0~1，击杀怪物获得装备的概率
TILE_SIZE = 24            # 像素格子大小（FC吞食天地规格）
# ============================================================

# 窗口与布局
WIN_WIDTH = 800
WIN_HEIGHT = 680
MAP_OFFSET_X = 40
MAP_OFFSET_Y = 10
MAP_PIXEL_W = 30 * TILE_SIZE   # 720
MAP_PIXEL_H = 25 * TILE_SIZE   # 600
STATUS_BAR_Y = MAP_OFFSET_Y + MAP_PIXEL_H + 5  # 615

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (60, 60, 60)
LIGHT_GRAY = (200, 200, 200)
RED = (220, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 220)
YELLOW = (240, 200, 50)
GOLD = (255, 215, 0)
PURPLE = (155, 89, 182)
BROWN = (139, 90, 43)
DARK_BROWN = (80, 50, 20)

# Tile色块（无外部素材时用纯色块占位渲染，放入素材后自动替换）
TILE_COLORS = {
    0: (34, 139, 34),    # 草地
    1: (160, 130, 90),   # 土路
    2: (20, 90, 20),     # 树木
    3: (40, 100, 180),   # 水
    4: (150, 100, 60),   # 房屋墙
    5: (200, 170, 120),  # 房屋地板
    6: (180, 160, 100),  # 寺庙墙
    7: (220, 200, 150),  # 寺庙地板
    8: (100, 100, 110),  # 城池墙
    9: (170, 170, 175),  # 城池地板
    10: (210, 190, 140), # 沙地
    11: (140, 140, 145), # 石板路
    12: (90, 80, 70),    # 山
    13: (180, 160, 50),  # 农田
    14: (160, 80, 60),   # 帐篷
    15: (120, 50, 50),   # 宫殿墙
    16: (200, 170, 80),  # 宫殿地板
}

TILE_NAMES = {
    0: "草地", 1: "土路", 2: "树木", 3: "水", 4: "房屋墙", 5: "房屋地板",
    6: "寺庙墙", 7: "寺庙地板", 8: "城池墙", 9: "城池地板", 10: "沙地",
    11: "石板路", 12: "山", 13: "农田", 14: "帐篷", 15: "宫殿墙", 16: "宫殿地板",
}

# 怪物模板数据
MONSTER_TEMPLATES = {
    "shanzei": {"name": "山贼", "hp": 40, "atk": 8, "def": 2, "exp": 20, "sprite_color": (80, 60, 40)},
    "yuan_bing": {"name": "元兵", "hp": 60, "atk": 12, "def": 5, "exp": 35, "sprite_color": (60, 60, 120)},
    "chen_youliang": {"name": "陈友谅", "hp": 300, "atk": 30, "def": 15, "exp": 200, "sprite_color": (150, 30, 30)},
    "zhang_shicheng": {"name": "张士诚", "hp": 400, "atk": 35, "def": 18, "exp": 300, "sprite_color": (150, 100, 30)},
    "yuan_emperor": {"name": "元顺帝", "hp": 800, "atk": 50, "def": 25, "exp": 1000, "sprite_color": (100, 30, 100)},
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def resource_path(relative_path):
    """获取资源绝对路径，兼容 PyInstaller 打包后的临时解压目录"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(BASE_DIR, relative_path)


def get_save_dir():
    """获取可写目录（保存编辑的地图等），打包后使用 exe 所在目录"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.dirname(sys.executable)
    return BASE_DIR


# ============================================================
# 工具函数
# ============================================================
def load_json(rel_path):
    """加载UTF-8编码的JSON文件"""
    full_path = resource_path(rel_path)
    with open(full_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(rel_path, data):
    """保存为UTF-8编码JSON"""
    save_dir = get_save_dir()
    full_path = os.path.join(save_dir, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


_cached_fonts = {}

# Windows中文字体文件路径候选（按文件直接加载，绕开SysFont在部分系统上的字体枚举bug）
_CJK_FONT_PATHS = [
    os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "msyh.ttc"),    # 微软雅黑
    os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "simhei.ttf"),  # 黑体
    os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "simsun.ttc"),  # 宋体
    os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "simkai.ttf"),  # 楷体
    os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "simfang.ttf"), # 仿宋
]

def get_font(size):
    """获取支持中文的字体，优先系统中文字体"""
    if size in _cached_fonts:
        return _cached_fonts[size]
    font = None
    for path in _CJK_FONT_PATHS:
        if os.path.exists(path):
            try:
                font = pygame.font.Font(path, size)
                break
            except Exception:
                continue
    if font is None:
        font = pygame.font.Font(None, size)
    _cached_fonts[size] = font
    return font


def quality_color(quality):
    """装备品质颜色"""
    colors = {
        "white": (200, 200, 200), "green": (46, 204, 113),
        "blue": (52, 152, 219), "purple": (155, 89, 182),
        "gold": (241, 196, 15), "red": (231, 76, 60),
    }
    return colors.get(quality, WHITE)


# ============================================================
# 素材加载（assets/ 像素素材，缺失时自动回退纯色块占位）
# ============================================================
# 地块素材文件名（对应 tile 编号 0-16）
TILE_FILENAMES = {
    0: "grass.png", 1: "dirt_road.png", 2: "tree.png", 3: "water.png",
    4: "house_wall.png", 5: "house_floor.png", 6: "temple_wall.png",
    7: "temple_floor.png", 8: "city_wall.png", 9: "city_floor.png",
    10: "sand.png", 11: "stone_path.png", 12: "mountain.png",
    13: "farmland.png", 14: "tent.png", 15: "palace_wall.png",
    16: "palace_floor.png",
}

# 角色精灵文件名（key 与玩家/怪物 type 一致）
SPRITE_FILENAMES = {
    "player": "player.png",
    "shanzei": "shanzei.png",
    "yuan_bing": "yuan_bing.png",
    "chen_youliang": "chen_youliang.png",
    "zhang_shicheng": "zhang_shicheng.png",
    "yuan_emperor": "yuan_emperor.png",
}

# 精灵表规格：192×96（6列×3行），每帧32×32
SPRITE_FRAME_W = 32
SPRITE_FRAME_H = 32
SPRITE_ANIMS = {
    "idle": {"row": 0, "frames": 4},    # 待机呼吸（cols 0-3）
    "walk": {"row": 1, "frames": 6},    # 行走（cols 0-5）
    "attack": {"row": 2, "frames": 4},  # 攻击（cols 0-3）
}
ANIM_FPS = {"idle": 2.5, "walk": 8.0, "attack": 10.0}
ITEM_ICON_SIZE = 20


def load_image(rel_path):
    """加载PNG并转为带alpha的surface；缺失/损坏时返回None。"""
    full = resource_path(rel_path)
    if not os.path.exists(full):
        return None
    try:
        img = pygame.image.load(full)
        return img.convert_alpha()
    except Exception:
        try:
            return pygame.image.load(full)
        except Exception:
            return None


def load_tile_images():
    """加载并缩放地块素材到 TILE_SIZE。"""
    images = {}
    for tid, fname in TILE_FILENAMES.items():
        img = load_image(os.path.join("assets", "tiles", fname))
        if img is not None and img.get_size() != (TILE_SIZE, TILE_SIZE):
            img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        images[tid] = img
    return images


def load_sprite_sheet(rel_path):
    """把192×96精灵表切成 {动画名: [帧Surface...]}；失败返回None。"""
    sheet = load_image(rel_path)
    if sheet is None:
        return None
    anims = {}
    for name, spec in SPRITE_ANIMS.items():
        frames = []
        for c in range(spec["frames"]):
            r = pygame.Rect(c * SPRITE_FRAME_W, spec["row"] * SPRITE_FRAME_H,
                            SPRITE_FRAME_W, SPRITE_FRAME_H)
            if sheet.get_width() >= r.right and sheet.get_height() >= r.bottom:
                frames.append(sheet.subsurface(r).copy())
            else:
                break
        anims[name] = frames
    return anims


def load_sprite_sheets():
    sheets = {}
    for key, fname in SPRITE_FILENAMES.items():
        sheets[key] = load_sprite_sheet(os.path.join("assets", "sprites", fname))
    return sheets


def load_item_images(item_list):
    images = {}
    for item in item_list:
        img = load_image(os.path.join("assets", "items", f"{item['id']}.png"))
        if img is not None:
            img = pygame.transform.scale(img, (ITEM_ICON_SIZE, ITEM_ICON_SIZE))
        images[item["id"]] = img
    return images


# ============================================================
# 玩家类
# ============================================================
class Player:
    def __init__(self):
        self.x = 100.0  # 像素坐标
        self.y = 100.0
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.level = 1
        self.exp = 0
        self.exp_to_next = 100
        self.hp = 100
        self.max_hp = 100
        self.base_atk = 10
        self.base_def = 5
        self.equipment = {"weapon": None, "armor": None, "ring": None, "necklace": None}
        self.inventory = []
        self.afk_mode = False
        self.direction = "down"
        self.anim_timer = 0
        self.afk_timer = 0.0
        self.gold = 0
        # 精灵动画状态
        self.anim_state = "idle"  # idle / walk / attack
        self.anim_frame = 0
        self.anim_elapsed = 0.0

    @property
    def atk(self):
        total = self.base_atk + self.level * 2
        for item in self.equipment.values():
            if item:
                total += item.get("atk", 0)
        return total

    @property
    def defense(self):
        total = self.base_def + self.level
        for item in self.equipment.values():
            if item:
                total += item.get("def", 0)
        return total

    def gain_exp(self, amount):
        actual = int(amount * EXP_MULTIPLIER)
        self.exp += actual
        leveled = False
        while self.exp >= self.exp_to_next:
            self.exp -= self.exp_to_next
            self.level_up()
            leveled = True
        return leveled, actual

    def level_up(self):
        self.level += 1
        self.exp_to_next = int(100 * math.pow(1.3, self.level - 1))
        self.max_hp = 100 + (self.level - 1) * 20
        self.hp = self.max_hp
        self.base_atk += 3
        self.base_def += 2

    def equip_item(self, item):
        slot = item["slot"]
        old = self.equipment[slot]
        self.equipment[slot] = item
        if item in self.inventory:
            self.inventory.remove(item)
        if old:
            self.inventory.append(old)
        return old

    def unequip(self, slot):
        item = self.equipment[slot]
        if item:
            self.equipment[slot] = None
            self.inventory.append(item)
        return item

    def get_grid_pos(self):
        gx = int((self.x + self.width // 2) / TILE_SIZE)
        gy = int((self.y + self.height // 2) / TILE_SIZE)
        return gx, gy

    def get_front_grid(self):
        gx, gy = self.get_grid_pos()
        if self.direction == "up":
            gy -= 1
        elif self.direction == "down":
            gy += 1
        elif self.direction == "left":
            gx -= 1
        elif self.direction == "right":
            gx += 1
        return gx, gy

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)


# ============================================================
# 怪物类
# ============================================================
class Monster:
    def __init__(self, data):
        template = MONSTER_TEMPLATES.get(data["type"], MONSTER_TEMPLATES["shanzei"])
        self.type = data["type"]
        self.name = template["name"]
        self.level = data.get("level", 1)
        self.is_boss = data.get("is_boss", False)
        lv_scale = 1.0 + (self.level - 1) * 0.15
        self.max_hp = int(template["hp"] * lv_scale)
        self.hp = self.max_hp
        self.atk = int(template["atk"] * lv_scale)
        self.defense = int(template["def"] * lv_scale)
        self.exp_reward = int(template["exp"] * lv_scale)
        self.sprite_color = template["sprite_color"]
        self.x = float(data["x"] * TILE_SIZE)
        self.y = float(data["y"] * TILE_SIZE)
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.alive = True
        self.move_timer = 0
        self.move_dir = random.choice(["up", "down", "left", "right"])
        self.anim_state = "idle"
        self.anim_frame = 0
        self.anim_elapsed = 0.0
        self.chasing = False

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def update(self, dt, player, game_map):
        """简单AI：随机游走，靠近玩家时追击"""
        if not self.alive:
            self.chasing = False
            return
        dx = player.x - self.x
        dy = player.y - self.y
        self.chasing = math.hypot(dx, dy) < 150
        self.move_timer += dt
        if self.move_timer < 0.8:
            return
        self.move_timer = 0
        speed = 1 if self.is_boss else 1
        if self.chasing:
            if abs(dx) > abs(dy):
                self.move_dir = "right" if dx > 0 else "left"
            else:
                self.move_dir = "down" if dy > 0 else "up"
        else:
            if random.random() < 0.3:
                self.move_dir = random.choice(["up", "down", "left", "right"])
        nx, ny = self.x, self.y
        if self.move_dir == "up":
            ny -= speed * TILE_SIZE * 0.5
        elif self.move_dir == "down":
            ny += speed * TILE_SIZE * 0.5
        elif self.move_dir == "left":
            nx -= speed * TILE_SIZE * 0.5
        elif self.move_dir == "right":
            nx += speed * TILE_SIZE * 0.5
        if not game_map.is_pixel_collision(nx, ny, self.width, self.height):
            self.x, self.y = nx, ny


# ============================================================
# 战斗系统
# ============================================================
class Battle:
    def __init__(self, player, monster):
        self.player = player
        self.monster = monster
        self.turn = "player"
        self.log = [f"遭遇 {monster.name}！"]
        self.over = False
        self.victory = False
        self.fled = False
        self.anim_shake = 0
        self.player_attack_start = 0
        self.monster_attack_start = 0

    def player_attack(self):
        if self.over or self.turn != "player":
            return
        dmg = max(1, self.player.atk - self.monster.defense // 2 + random.randint(-3, 3))
        self.monster.hp -= dmg
        self.log.append(f"你对{self.monster.name}造成 {dmg} 点伤害")
        self.anim_shake = 8
        self.player_attack_start = pygame.time.get_ticks()
        if self.monster.hp <= 0:
            self.monster.hp = 0
            self.over = True
            self.victory = True
            self.log.append(f"{self.monster.name} 被击败了！")
        else:
            self.turn = "monster"

    def monster_attack(self):
        if self.over or self.turn != "monster":
            return
        dmg = max(1, self.monster.atk - self.player.defense // 2 + random.randint(-2, 2))
        self.player.hp -= dmg
        self.log.append(f"{self.monster.name}对你造成 {dmg} 点伤害")
        self.anim_shake = 6
        self.monster_attack_start = pygame.time.get_ticks()
        if self.player.hp <= 0:
            self.player.hp = 0
            self.over = True
            self.victory = False
            self.log.append("你被击败了……")
        else:
            self.turn = "player"

    def try_flee(self):
        if self.over:
            return False
        if self.monster.is_boss:
            self.log.append("BOSS战无法逃跑！")
            return False
        if random.random() < 0.6:
            self.over = True
            self.victory = False
            self.fled = True
            self.log.append("成功逃跑！")
            return True
        else:
            self.log.append("逃跑失败！")
            self.turn = "monster"
            return False


# ============================================================
# 地图管理器
# ============================================================
class GameMap:
    def __init__(self, map_data, map_name):
        self.name = map_data["name"]
        self.map_name = map_name
        self.width = map_data["width"]
        self.height = map_data["height"]
        # 防御性规范化：确保每行宽度一致
        self.tiles = []
        for row in map_data["tiles"]:
            normalized = list(row[:self.width])
            while len(normalized) < self.width:
                normalized.append(0)
            self.tiles.append(normalized)
        self.collision_tiles = set(map_data["collision_tiles"])
        self.exits = map_data["exits"]
        self.trees = [dict(t) for t in map_data["trees"]]
        self.monsters_data = map_data["monsters"]
        self.spawn = map_data["spawn"]
        self.story_trigger = map_data.get("story_trigger")
        self.monsters = []
        self._init_monsters()

    def _init_monsters(self):
        for md in self.monsters_data:
            self.monsters.append(Monster(md))

    def get_tile(self, gx, gy):
        if 0 <= gx < self.width and 0 <= gy < self.height:
            return self.tiles[gy][gx]
        return 2  # 越界视为山（碰撞）

    def set_tile(self, gx, gy, tile_id):
        if 0 <= gx < self.width and 0 <= gy < self.height:
            self.tiles[gy][gx] = tile_id

    def is_collision(self, gx, gy):
        return self.get_tile(gx, gy) in self.collision_tiles

    def is_pixel_collision(self, px, py, pw, ph):
        """检测像素矩形是否与碰撞tile重叠"""
        corners = [
            (px + 2, py + 2),
            (px + pw - 2, py + 2),
            (px + 2, py + ph - 2),
            (px + pw - 2, py + ph - 2),
        ]
        for cx, cy in corners:
            gx = int(cx / TILE_SIZE)
            gy = int(cy / TILE_SIZE)
            if self.is_collision(gx, gy):
                return True
        return False

    def find_tree_at(self, gx, gy):
        for i, t in enumerate(self.trees):
            if t["x"] == gx and t["y"] == gy:
                return i
        return -1

    def remove_tree(self, index):
        if 0 <= index < len(self.trees):
            t = self.trees.pop(index)
            self.set_tile(t["x"], t["y"], 0)  # 变草地

    def check_exit(self, player):
        gx, gy = player.get_grid_pos()
        pdir = player.direction
        dir_map = {"north": "up", "south": "down", "east": "right", "west": "left"}
        for ex in self.exits:
            if abs(gx - ex["x"]) <= 1 and abs(gy - ex["y"]) <= 1:
                # 仅当玩家朝出口方向移动时触发，防止刚进图就被反向出口弹回
                if dir_map.get(ex.get("direction"), pdir) == pdir:
                    return ex
        return None

    def to_dict(self):
        return {
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "tile_size": TILE_SIZE,
            "tiles": self.tiles,
            "collision_tiles": sorted(list(self.collision_tiles)),
            "exits": self.exits,
            "trees": self.trees,
            "monsters": self.monsters_data,
            "spawn": self.spawn,
            "story_trigger": self.story_trigger,
        }


# ============================================================
# 游戏主类
# ============================================================
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        pygame.display.set_caption("大明王朝RPG - 复古像素")
        self.clock = pygame.time.Clock()
        self.font_sm = get_font(14)
        self.font_md = get_font(18)
        self.font_lg = get_font(24)
        self.font_xl = get_font(32)

        # 加载数据
        self.equipment_data = load_json("data/equipment.json")
        self.story_data = load_json("data/story.json")
        self.level_unlock = load_json("data/level_unlock.json")
        self.item_list = self.equipment_data["items"]
        self.drop_table = self.equipment_data["drop_table"]

        # 加载像素素材（缺失时自动回退纯色块占位）
        self.tile_images = load_tile_images()
        self.sprite_sheets = load_sprite_sheets()
        self.item_images = load_item_images(self.item_list)

        # 游戏状态
        self.state = "playing"  # playing / dialog / battle / equipment / editor / gameover / victory
        self.player = Player()
        self.current_map = None
        self.current_map_name = ""
        self.battle = None
        self.dialog_lines = []
        self.dialog_title = ""
        self.dialog_index = 0
        self.dialog_triggered = set()
        self.message = ""
        self.message_timer = 0
        self.equip_panel_page = 0
        self.editor_tile = 1
        self.editor_mode = False
        self.running = True
        self.last_time = pygame.time.get_ticks()

        # 加载初始地图
        self.load_map("zhongli_north", use_spawn=True)

    def load_map(self, map_name, use_spawn=False, spawn_override=None):
        data = load_json(f"map/{map_name}.json")
        self.current_map = GameMap(data, map_name)
        self.current_map_name = map_name
        if use_spawn:
            sp = self.current_map.spawn
            self.player.x = float(sp["x"] * TILE_SIZE)
            self.player.y = float(sp["y"] * TILE_SIZE)
        if spawn_override:
            self.player.x = float(spawn_override[0] * TILE_SIZE)
            self.player.y = float(spawn_override[1] * TILE_SIZE)
        # 触发剧情
        trigger = self.current_map.story_trigger
        if trigger and trigger not in self.dialog_triggered:
            self.start_dialog(trigger)

    def start_dialog(self, trigger_key):
        if trigger_key in self.story_data:
            sd = self.story_data[trigger_key]
            self.dialog_title = sd["title"]
            self.dialog_lines = sd["lines"]
            self.dialog_index = 0
            self.state = "dialog"
            self.dialog_triggered.add(trigger_key)

    def show_message(self, msg, duration=2.0):
        self.message = msg
        self.message_timer = duration

    # ----------------------------------------------------------
    # 事件处理
    # ----------------------------------------------------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.handle_key_down(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN and self.editor_mode:
                self.handle_editor_click(event)

    def handle_key_down(self, key):
        if self.state == "dialog":
            if key in (pygame.K_SPACE, pygame.K_RETURN):
                # 空格/回车：逐句阅读剧情
                self.dialog_index += 1
                if self.dialog_index >= len(self.dialog_lines):
                    self.state = "playing"
            else:
                # 其它任意键：直接跳过整段剧情，避免卡住
                self.state = "playing"
            return

        if self.state == "battle":
            self.handle_battle_key(key)
            return

        if self.state == "equipment":
            self.handle_equipment_key(key)
            return

        if self.state == "gameover":
            if key in (pygame.K_SPACE, pygame.K_RETURN):
                self.__init__()
            return

        if self.state == "victory":
            if key in (pygame.K_SPACE, pygame.K_RETURN):
                self.running = False
            return

        # 正常游戏状态
        if key == pygame.K_g:
            self.player.afk_mode = not self.player.afk_mode
            self.show_message("挂机开启：原地修炼，每秒+8经验（按G取消）" if self.player.afk_mode else "挂机已关闭，可自由移动")
        elif key == pygame.K_e:
            self.state = "equipment"
            self.equip_panel_page = 0
        elif key == pygame.K_SPACE:
            self.try_chop_tree()
        elif key == pygame.K_F1:
            self.editor_mode = not self.editor_mode
            self.show_message("地图编辑器开启" if self.editor_mode else "地图编辑器关闭")
        elif key == pygame.K_s and self.editor_mode:
            self.save_editor_map()
        elif self.editor_mode and pygame.K_1 <= key <= pygame.K_9:
            self.editor_tile = key - pygame.K_1 + 1
            self.show_message(f"当前地块: {TILE_NAMES.get(self.editor_tile, '?')}")

    def handle_battle_key(self, key):
        if key == pygame.K_1:
            self.battle.player_attack()
        elif key == pygame.K_2:
            self.battle.try_flee()
        elif key == pygame.K_SPACE and self.battle.over:
            self.finish_battle()

    def handle_equipment_key(self, key):
        if key == pygame.K_e or key == pygame.K_ESCAPE:
            self.state = "playing"
        elif key == pygame.K_LEFT:
            self.equip_panel_page = max(0, self.equip_panel_page - 1)
        elif key == pygame.K_RIGHT:
            max_page = max(0, (len(self.player.inventory) - 1) // 6)
            self.equip_panel_page = min(max_page, self.equip_panel_page + 1)
        elif pygame.K_1 <= key <= pygame.K_4:
            slots = ["weapon", "armor", "ring", "necklace"]
            idx = key - pygame.K_1
            slot = slots[idx]
            if self.player.equipment[slot]:
                self.player.unequip(slot)
                self.show_message(f"已卸下 {self.equipment_data['slot_names'][slot]}")
        elif pygame.K_5 <= key <= pygame.K_9:
            idx = key - pygame.K_5 + self.equip_panel_page * 5
            if idx < len(self.player.inventory):
                item = self.player.inventory[idx]
                if item["level_req"] <= self.player.level:
                    self.player.equip_item(item)
                    self.show_message(f"已装备 {item['name']}")
                else:
                    self.show_message(f"需要等级 {item['level_req']}")

    def handle_editor_click(self, event):
        mx, my = event.pos
        gx = int((mx - MAP_OFFSET_X) / TILE_SIZE)
        gy = int((my - MAP_OFFSET_Y) / TILE_SIZE)
        if 0 <= gx < self.current_map.width and 0 <= gy < self.current_map.height:
            if event.button == 1:  # 左键放置
                self.current_map.set_tile(gx, gy, self.editor_tile)
            elif event.button == 3:  # 右键擦除为草地
                self.current_map.set_tile(gx, gy, 0)

    def save_editor_map(self):
        path = f"map/{self.current_map_name}_edited.json"
        save_json(path, self.current_map.to_dict())
        self.show_message(f"地图已保存到 {path}")

    # ----------------------------------------------------------
    # 游戏逻辑更新
    # ----------------------------------------------------------
    def update(self):
        now = pygame.time.get_ticks()
        dt = (now - self.last_time) / 1000.0
        self.last_time = now

        if self.message_timer > 0:
            self.message_timer -= dt

        if self.state != "playing":
            if self.state == "battle" and self.battle and self.battle.turn == "monster" and not self.battle.over:
                pygame.time.delay(400)
                self.battle.monster_attack()
            return

        if self.editor_mode:
            return

        # 挂机模式
        if self.player.afk_mode:
            self.player.afk_timer += dt
            if self.player.afk_timer >= 1.0:
                self.player.afk_timer -= 1.0
                leveled, gained = self.player.gain_exp(AFK_EXP_PER_SEC)
                if leveled:
                    self.show_message(f"升级了！当前等级 Lv.{self.player.level}")
            return

        # 玩家移动
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -MOVE_SPEED
            self.player.direction = "up"
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = MOVE_SPEED
            self.player.direction = "down"
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -MOVE_SPEED
            self.player.direction = "left"
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = MOVE_SPEED
            self.player.direction = "right"

        if dx != 0 or dy != 0:
            self.player.anim_timer += dt
            new_x = self.player.x + dx
            new_y = self.player.y + dy
            # 分轴碰撞检测
            if not self.current_map.is_pixel_collision(new_x, self.player.y, self.player.width, self.player.height):
                self.player.x = new_x
            if not self.current_map.is_pixel_collision(self.player.x, new_y, self.player.width, self.player.height):
                self.player.y = new_y
            # 边界限制
            self.player.x = max(0, min(self.player.x, MAP_PIXEL_W - self.player.width))
            self.player.y = max(0, min(self.player.y, MAP_PIXEL_H - self.player.height))

        # 玩家精灵动画：移动=行走，静止=待机
        self.advance_anim(self.player, "walk" if (dx != 0 or dy != 0) else "idle", dt)

        # 检测出口
        exit_info = self.current_map.check_exit(self.player)
        if exit_info:
            self.try_change_map(exit_info)

        # 怪物更新与碰撞
        for monster in self.current_map.monsters:
            if not monster.alive:
                continue
            monster.update(dt, self.player, self.current_map)
            self.advance_anim(monster, "walk" if monster.chasing else "idle", dt)
            if monster.rect().colliderect(self.player.rect()):
                self.start_battle(monster)
                break

    def try_change_map(self, exit_info):
        target = exit_info["target_map"]
        unlock = self.level_unlock.get(target, {})
        req_level = unlock.get("level_req", 1)
        if self.player.level < req_level:
            self.show_message(f"等级不足！进入{unlock.get('map_name', target)}需要 Lv.{req_level}")
            # 把玩家推回
            self.player.x -= 10 if exit_info.get("direction") == "east" else 0
            self.player.x += 10 if exit_info.get("direction") == "west" else 0
            self.player.y -= 10 if exit_info.get("direction") == "south" else 0
            self.player.y += 10 if exit_info.get("direction") == "north" else 0
            return
        tx = exit_info.get("target_x", 5)
        ty = exit_info.get("target_y", 5)
        self.load_map(target, spawn_override=(tx, ty))

    def try_chop_tree(self):
        gx, gy = self.player.get_front_grid()
        idx = self.current_map.find_tree_at(gx, gy)
        if idx >= 0:
            self.current_map.remove_tree(idx)
            self.show_message("砍伐了一棵树")
            # 砍树经验
            self.player.gain_exp(5)
            # 随机掉落
            if random.random() < DROP_RATE_TREE:
                item = self.roll_drop("tree")
                if item:
                    self.player.inventory.append(item)
                    self.show_message(f"获得装备: {item['name']}")
        else:
            # 检查面前是否是可交互NPC（暂用消息提示）
            self.show_message("这里没有可砍伐的树木")

    def roll_drop(self, source):
        table = self.drop_table.get(source, self.drop_table["tree"])
        r = random.random()
        cumulative = 0
        chosen_quality = "white"
        for q in ["white", "green", "blue", "purple", "gold", "red"]:
            cumulative += table.get(q, 0)
            if r <= cumulative:
                chosen_quality = q
                break
        candidates = [it for it in self.item_list if it["quality"] == chosen_quality]
        if not candidates:
            candidates = [it for it in self.item_list if it["quality"] == "white"]
        if candidates:
            return dict(random.choice(candidates))
        return None

    def start_battle(self, monster):
        self.battle = Battle(self.player, monster)
        self.state = "battle"

    def flee_from_monster(self, monster):
        """逃跑成功后，把玩家朝远离怪物的方向推移一段距离，避免刚结束战斗又立刻遭遇。"""
        dx = self.player.x - monster.x
        dy = self.player.y - monster.y
        dist = math.hypot(dx, dy)
        if dist < 0.001:
            # 玩家与怪物重叠时，按玩家当前朝向推开
            dir_dx, dir_dy = {
                "up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0),
            }[self.player.direction]
        else:
            dir_dx, dir_dy = dx / dist, dy / dist

        step = TILE_SIZE
        # 逐步推开，最多移动约4格，遇到碰撞或边界则停下
        for _ in range(4):
            nx = self.player.x + dir_dx * step
            ny = self.player.y + dir_dy * step
            if self.current_map.is_pixel_collision(nx, ny, self.player.width, self.player.height):
                break
            self.player.x = nx
            self.player.y = ny

        # 兜底：若仍与怪物重叠，把怪物朝反方向推开一格
        if self.player.rect().colliderect(monster.rect()):
            mx = monster.x - dir_dx * step
            my = monster.y - dir_dy * step
            if not self.current_map.is_pixel_collision(mx, my, monster.width, monster.height):
                monster.x = mx
                monster.y = my

        # 边界限制
        self.player.x = max(0, min(self.player.x, MAP_PIXEL_W - self.player.width))
        self.player.y = max(0, min(self.player.y, MAP_PIXEL_H - self.player.height))

    def finish_battle(self):
        battle = self.battle
        monster = battle.monster
        if battle.victory:
            monster.alive = False
            leveled, gained = self.player.gain_exp(monster.exp_reward)
            self.show_message(f"获得 {gained} 经验值")
            # 怪物掉落
            source = "boss" if monster.is_boss else monster.type
            if random.random() < DROP_RATE_MONSTER:
                item = self.roll_drop(source)
                if item:
                    self.player.inventory.append(item)
                    self.show_message(f"获得装备: {item['name']}")
            if leveled:
                self.show_message(f"升级了！当前等级 Lv.{self.player.level}")
            # 最终BOSS通关
            if monster.type == "yuan_emperor":
                self.state = "victory"
                return
        else:
            if self.player.hp <= 0:
                self.state = "gameover"
                return
            if battle.fled:
                self.flee_from_monster(monster)
        self.battle = None
        self.state = "playing"

    # ----------------------------------------------------------
    # 精灵动画辅助
    # ----------------------------------------------------------
    def advance_anim(self, entity, anim_state, dt):
        """根据当前动画状态推进帧序号。"""
        if entity.anim_state != anim_state:
            entity.anim_state = anim_state
            entity.anim_frame = 0
            entity.anim_elapsed = 0.0
        entity.anim_elapsed += dt
        interval = 1.0 / ANIM_FPS.get(anim_state, 8.0)
        while entity.anim_elapsed >= interval:
            entity.anim_elapsed -= interval
            entity.anim_frame += 1

    def get_sprite_frame(self, key, anim, frame_index, flip=False):
        """取某角色指定动画的指定帧；无素材返回None。"""
        anims = self.sprite_sheets.get(key)
        if not anims:
            return None
        frames = anims.get(anim) or anims.get("idle")
        if not frames:
            return None
        frame = frames[frame_index % len(frames)]
        if flip:
            frame = pygame.transform.flip(frame, True, False)
        return frame

    def draw_sprite(self, key, anim, frame_index, x, y, flip=False, size=TILE_SIZE):
        """在屏幕坐标(x,y)绘制精灵（自动缩放）；无素材返回False。"""
        frame = self.get_sprite_frame(key, anim, frame_index, flip)
        if frame is None:
            return False
        if frame.get_size() != (size, size):
            frame = pygame.transform.scale(frame, (size, size))
        self.screen.blit(frame, (x, y))
        return True

    def _battle_sprite(self, key, attack_start, now):
        """战斗界面精灵帧：攻击时播attack，其余时间播idle呼吸。"""
        anims = self.sprite_sheets.get(key)
        if not anims:
            return None
        if attack_start and now - attack_start < 400:
            frames = anims.get("attack") or anims.get("idle")
            if not frames:
                return None
            return frames[((now - attack_start) // 100) % len(frames)]
        frames = anims.get("idle")
        if not frames:
            return None
        return frames[(now // 400) % len(frames)]

    # ----------------------------------------------------------
    # 渲染
    # ----------------------------------------------------------
    def draw(self):
        self.screen.fill((20, 20, 30))
        self.draw_map()
        self.draw_monsters()
        self.draw_player()
        self.draw_status_bar()
        self.draw_editor_overlay()

        if self.state == "dialog":
            self.draw_dialog()
        elif self.state == "battle":
            self.draw_battle()
        elif self.state == "equipment":
            self.draw_equipment_panel()
        elif self.state == "gameover":
            self.draw_gameover()
        elif self.state == "victory":
            self.draw_victory()

        if self.message and self.message_timer > 0:
            self.draw_message()

    def draw_map(self):
        """渲染地图瓦片（有素材用素材，无素材回退纯色块）"""
        for gy in range(self.current_map.height):
            for gx in range(self.current_map.width):
                tile_id = self.current_map.get_tile(gx, gy)
                px = MAP_OFFSET_X + gx * TILE_SIZE
                py = MAP_OFFSET_Y + gy * TILE_SIZE
                img = self.tile_images.get(tile_id)
                if img is not None:
                    self.screen.blit(img, (px, py))
                    continue
                color = TILE_COLORS.get(tile_id, (128, 0, 128))
                rect = pygame.Rect(px, py, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.screen, color, rect)
                # 树木额外绘制树冠
                if tile_id == 2:
                    pygame.draw.circle(self.screen, (10, 60, 10), rect.center, 9)
                    pygame.draw.circle(self.screen, (30, 100, 30), rect.center, 6)
                # 水波纹
                elif tile_id == 3:
                    pygame.draw.line(self.screen, (80, 140, 200), rect.topleft, rect.bottomright, 1)
                # 墙壁纹理
                elif tile_id in (4, 6, 8, 12, 15):
                    pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
        # 地图边框
        border = pygame.Rect(MAP_OFFSET_X - 2, MAP_OFFSET_Y - 2, MAP_PIXEL_W + 4, MAP_PIXEL_H + 4)
        pygame.draw.rect(self.screen, GOLD, border, 2)

    def draw_player(self):
        p = self.player
        px = MAP_OFFSET_X + int(p.x)
        py = MAP_OFFSET_Y + int(p.y)
        flip = (p.direction == "left")
        if not self.draw_sprite("player", p.anim_state, p.anim_frame, px, py, flip, TILE_SIZE):
            # 回退：纯色块
            rect = pygame.Rect(px, py, p.width, p.height)
            pygame.draw.rect(self.screen, (200, 50, 50), rect)  # 红衣（朱元璋）
            head = pygame.Rect(px + 4, py + 2, 16, 10)
            pygame.draw.rect(self.screen, (240, 200, 160), head)
            ex, ey = px + 12, py + 6
            if p.direction == "left":
                ex, ey = px + 6, py + 6
            elif p.direction == "right":
                ex, ey = px + 18, py + 6
            elif p.direction == "up":
                ex, ey = px + 12, py + 3
            pygame.draw.circle(self.screen, BLACK, (ex, ey), 2)
        # 挂机标记
        if p.afk_mode:
            afk_text = self.font_sm.render("ZZZ", True, YELLOW)
            self.screen.blit(afk_text, (px + 2, py - 14))

    def draw_monsters(self):
        for monster in self.current_map.monsters:
            if not monster.alive:
                continue
            mx = MAP_OFFSET_X + int(monster.x)
            my = MAP_OFFSET_Y + int(monster.y)
            flip = (monster.move_dir == "left")
            if not self.draw_sprite(monster.type, monster.anim_state, monster.anim_frame, mx, my, flip, TILE_SIZE):
                # 回退：纯色块
                rect = pygame.Rect(mx, my, monster.width, monster.height)
                pygame.draw.rect(self.screen, monster.sprite_color, rect)
                head = pygame.Rect(mx + 4, my + 2, 16, 8)
                pygame.draw.rect(self.screen, (200, 160, 120), head)
                pygame.draw.circle(self.screen, RED, (mx + 8, my + 5), 1)
                pygame.draw.circle(self.screen, RED, (mx + 16, my + 5), 1)
            # BOSS标记
            if monster.is_boss:
                boss_text = self.font_sm.render("BOSS", True, RED)
                self.screen.blit(boss_text, (mx, my - 14))
            # 血条
            hp_w = monster.width
            hp_h = 3
            hp_ratio = monster.hp / monster.max_hp
            pygame.draw.rect(self.screen, BLACK, (mx, my - 5, hp_w, hp_h))
            pygame.draw.rect(self.screen, GREEN if hp_ratio > 0.5 else RED, (mx, my - 5, int(hp_w * hp_ratio), hp_h))

    def draw_status_bar(self):
        """底部状态栏：等级、HP、经验条、攻击防御、位置"""
        bar_rect = pygame.Rect(MAP_OFFSET_X, STATUS_BAR_Y, MAP_PIXEL_W, 55)
        pygame.draw.rect(self.screen, DARK_GRAY, bar_rect)
        pygame.draw.rect(self.screen, GOLD, bar_rect, 1)

        p = self.player
        # 等级
        lv_text = self.font_md.render(f"Lv.{p.level}", True, GOLD)
        self.screen.blit(lv_text, (bar_rect.x + 10, bar_rect.y + 5))

        # HP
        hp_text = self.font_sm.render(f"HP: {p.hp}/{p.max_hp}", True, RED)
        self.screen.blit(hp_text, (bar_rect.x + 70, bar_rect.y + 5))
        hp_bar_w = 120
        hp_ratio = p.hp / p.max_hp if p.max_hp > 0 else 0
        pygame.draw.rect(self.screen, BLACK, (bar_rect.x + 70, bar_rect.y + 24, hp_bar_w, 8))
        pygame.draw.rect(self.screen, RED, (bar_rect.x + 70, bar_rect.y + 24, int(hp_bar_w * hp_ratio), 8))

        # 经验条
        exp_text = self.font_sm.render(f"EXP: {p.exp}/{p.exp_to_next}", True, BLUE)
        self.screen.blit(exp_text, (bar_rect.x + 210, bar_rect.y + 5))
        exp_bar_w = 150
        exp_ratio = p.exp / p.exp_to_next if p.exp_to_next > 0 else 0
        pygame.draw.rect(self.screen, BLACK, (bar_rect.x + 210, bar_rect.y + 24, exp_bar_w, 8))
        pygame.draw.rect(self.screen, BLUE, (bar_rect.x + 210, bar_rect.y + 24, int(exp_bar_w * exp_ratio), 8))

        # 属性
        atk_text = self.font_sm.render(f"攻击:{p.atk}", True, YELLOW)
        def_text = self.font_sm.render(f"防御:{p.defense}", True, GREEN)
        self.screen.blit(atk_text, (bar_rect.x + 380, bar_rect.y + 5))
        self.screen.blit(def_text, (bar_rect.x + 380, bar_rect.y + 24))

        # 位置
        map_text = self.font_sm.render(f"地图:{self.current_map.name}", True, WHITE)
        self.screen.blit(map_text, (bar_rect.x + 470, bar_rect.y + 5))
        gx, gy = p.get_grid_pos()
        pos_text = self.font_sm.render(f"坐标:({gx},{gy})", True, LIGHT_GRAY)
        self.screen.blit(pos_text, (bar_rect.x + 470, bar_rect.y + 24))

        # 操作提示
        hint = "方向键移动 | 空格砍树 | G挂机 | E装备 | F1编辑器"
        hint_text = self.font_sm.render(hint, True, (150, 150, 150))
        self.screen.blit(hint_text, (bar_rect.x + 590, bar_rect.y + 15))

    def draw_dialog(self):
        overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        box_w, box_h = 680, 180
        box_x = (WIN_WIDTH - box_w) // 2
        box_y = WIN_HEIGHT - box_h - 30
        box = pygame.Rect(box_x, box_y, box_w, box_h)
        pygame.draw.rect(self.screen, (30, 20, 10), box)
        pygame.draw.rect(self.screen, GOLD, box, 3)

        title = self.font_lg.render(self.dialog_title, True, GOLD)
        self.screen.blit(title, (box_x + 20, box_y + 10))

        if self.dialog_index < len(self.dialog_lines):
            line = self.dialog_lines[self.dialog_index]
            text = self.font_md.render(line, True, WHITE)
            self.screen.blit(text, (box_x + 20, box_y + 55))

        page_text = self.font_sm.render(f"[{self.dialog_index + 1}/{len(self.dialog_lines)}] 空格逐句 | 任意键跳过", True, LIGHT_GRAY)
        self.screen.blit(page_text, (box_x + box_w - 160, box_y + box_h - 25))

    def draw_battle(self):
        overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        box_w, box_h = 700, 450
        box_x = (WIN_WIDTH - box_w) // 2
        box_y = (WIN_HEIGHT - box_h) // 2
        box = pygame.Rect(box_x, box_y, box_w, box_h)
        pygame.draw.rect(self.screen, (20, 10, 10), box)
        pygame.draw.rect(self.screen, RED, box, 3)

        title = self.font_xl.render("⚔ 战斗 ⚔", True, RED)
        self.screen.blit(title, (box_x + box_w // 2 - 60, box_y + 10))

        b = self.battle
        # 玩家信息
        p = b.player
        pygame.draw.rect(self.screen, (50, 20, 20), (box_x + 30, box_y + 70, 200, 120))
        pygame.draw.rect(self.screen, GOLD, (box_x + 30, box_y + 70, 200, 120), 2)
        p_name = self.font_md.render("朱元璋", True, GOLD)
        self.screen.blit(p_name, (box_x + 50, box_y + 80))
        p_hp = self.font_sm.render(f"HP: {p.hp}/{p.max_hp}", True, WHITE)
        self.screen.blit(p_hp, (box_x + 50, box_y + 110))
        p_atk = self.font_sm.render(f"攻击: {p.atk}  防御: {p.defense}", True, WHITE)
        self.screen.blit(p_atk, (box_x + 50, box_y + 135))
        pygame.draw.rect(self.screen, BLACK, (box_x + 50, box_y + 160, 160, 12))
        pygame.draw.rect(self.screen, GREEN, (box_x + 50, box_y + 160, int(160 * p.hp / p.max_hp), 12))

        # VS
        vs = self.font_xl.render("VS", True, YELLOW)
        self.screen.blit(vs, (box_x + box_w // 2 - 20, box_y + 110))

        # 怪物信息
        m = b.monster
        m_color = RED if m.is_boss else (150, 50, 50)
        pygame.draw.rect(self.screen, (40, 10, 10), (box_x + 470, box_y + 70, 200, 120))
        pygame.draw.rect(self.screen, m_color, (box_x + 470, box_y + 70, 200, 120), 2)
        m_name = self.font_md.render(m.name + (" [BOSS]" if m.is_boss else ""), True, m_color)
        self.screen.blit(m_name, (box_x + 490, box_y + 80))
        m_hp = self.font_sm.render(f"HP: {m.hp}/{m.max_hp}", True, WHITE)
        self.screen.blit(m_hp, (box_x + 490, box_y + 110))
        m_atk = self.font_sm.render(f"攻击: {m.atk}  防御: {m.defense}", True, WHITE)
        self.screen.blit(m_atk, (box_x + 490, box_y + 135))
        pygame.draw.rect(self.screen, BLACK, (box_x + 490, box_y + 160, 160, 12))
        pygame.draw.rect(self.screen, RED, (box_x + 490, box_y + 160, int(160 * m.hp / m.max_hp), 12))

        # 双方精灵立绘（攻击时播放攻击动画，否则待机呼吸）
        now = pygame.time.get_ticks()
        p_sprite = self._battle_sprite("player", b.player_attack_start, now)
        m_sprite = self._battle_sprite(b.monster.type, b.monster_attack_start, now)
        if p_sprite is not None:
            self.screen.blit(pygame.transform.scale(p_sprite, (48, 48)), (box_x + 250, box_y + 90))
        if m_sprite is not None:
            self.screen.blit(pygame.transform.scale(m_sprite, (48, 48)), (box_x + 402, box_y + 90))

        # 战斗日志
        log_box = pygame.Rect(box_x + 30, box_y + 210, box_w - 60, 150)
        pygame.draw.rect(self.screen, (10, 10, 20), log_box)
        pygame.draw.rect(self.screen, GRAY, log_box, 1)
        log_start = max(0, len(b.log) - 6)
        for i, line in enumerate(b.log[log_start:]):
            lt = self.font_sm.render(line, True, WHITE)
            self.screen.blit(lt, (log_box.x + 10, log_box.y + 5 + i * 22))

        # 操作按钮
        if not b.over:
            if b.turn == "player":
                btn1 = self.font_md.render("[1] 攻击", True, GREEN)
                btn2 = self.font_md.render("[2] 逃跑", True, YELLOW)
                self.screen.blit(btn1, (box_x + 150, box_y + box_h - 45))
                self.screen.blit(btn2, (box_x + 400, box_y + box_h - 45))
            else:
                wait = self.font_md.render("敌方回合...", True, RED)
                self.screen.blit(wait, (box_x + box_w // 2 - 50, box_y + box_h - 45))
        else:
            result = "胜利！" if b.victory else "战败……"
            rc = GREEN if b.victory else RED
            rt = self.font_lg.render(result + " 空格继续", True, rc)
            self.screen.blit(rt, (box_x + box_w // 2 - 100, box_y + box_h - 45))

    def draw_equipment_panel(self):
        overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        box_w, box_h = 700, 500
        box_x = (WIN_WIDTH - box_w) // 2
        box_y = (WIN_HEIGHT - box_h) // 2
        box = pygame.Rect(box_x, box_y, box_w, box_h)
        pygame.draw.rect(self.screen, (20, 15, 5), box)
        pygame.draw.rect(self.screen, GOLD, box, 3)

        title = self.font_xl.render("装备面板", True, GOLD)
        self.screen.blit(title, (box_x + box_w // 2 - 70, box_y + 10))

        p = self.player
        slots = ["weapon", "armor", "ring", "necklace"]
        slot_names = self.equipment_data["slot_names"]

        # 已装备区域
        eq_title = self.font_md.render("【已装备】按1-4卸下", True, LIGHT_GRAY)
        self.screen.blit(eq_title, (box_x + 20, box_y + 60))
        for i, slot in enumerate(slots):
            y = box_y + 90 + i * 45
            item = p.equipment[slot]
            slot_label = self.font_sm.render(f"[{i+1}]{slot_names[slot]}:", True, WHITE)
            self.screen.blit(slot_label, (box_x + 30, y))
            if item:
                qc = quality_color(item["quality"])
                icon = self.item_images.get(item["id"])
                if icon is not None:
                    self.screen.blit(icon, (box_x + 100, y - 2))
                item_text = self.font_sm.render(f"{item['name']}  攻+{item['atk']} 防+{item['def']}", True, qc)
                self.screen.blit(item_text, (box_x + 130, y))
            else:
                empty_text = self.font_sm.render("（空）", True, GRAY)
                self.screen.blit(empty_text, (box_x + 130, y))

        # 总属性
        total_text = self.font_md.render(f"总攻击: {p.atk}  总防御: {p.defense}  HP: {p.hp}/{p.max_hp}", True, YELLOW)
        self.screen.blit(total_text, (box_x + 20, box_y + 280))

        # 背包区域
        inv_title = self.font_md.render(f"【背包】按5-9装备 (第{self.equip_panel_page + 1}页)", True, LIGHT_GRAY)
        self.screen.blit(inv_title, (box_x + 20, box_y + 315))
        start_idx = self.equip_panel_page * 5
        for i in range(5):
            idx = start_idx + i
            y = box_y + 345 + i * 28
            if idx < len(p.inventory):
                item = p.inventory[idx]
                qc = quality_color(item["quality"])
                icon = self.item_images.get(item["id"])
                if icon is not None:
                    self.screen.blit(icon, (box_x + 30, y - 2))
                locked = " [等级不足]" if item["level_req"] > p.level else ""
                it = self.font_sm.render(f"[{i+5}]{item['name']}({slot_names[item['slot']]}) 攻+{item['atk']} 防+{item['def']}{locked}", True, qc)
                self.screen.blit(it, (box_x + 56, y))
            else:
                self.screen.blit(self.font_sm.render("——", True, GRAY), (box_x + 30, y))

        hint = self.font_sm.render("E/ESC关闭 | ←→翻页", True, (150, 150, 150))
        self.screen.blit(hint, (box_x + box_w - 180, box_y + box_h - 25))

    def draw_editor_overlay(self):
        if not self.editor_mode:
            return
        info = self.font_sm.render(f"编辑器模式 | 当前地块:{self.editor_tile}({TILE_NAMES.get(self.editor_tile,'?')}) | 1-9切换 | S保存 | F1退出", True, YELLOW)
        bg = pygame.Rect(MAP_OFFSET_X, MAP_OFFSET_Y - 22, info.get_width() + 10, 20)
        pygame.draw.rect(self.screen, (0, 0, 0), bg)
        self.screen.blit(info, (bg.x + 5, bg.y + 2))
        # 高亮鼠标格子
        mx, my = pygame.mouse.get_pos()
        gx = int((mx - MAP_OFFSET_X) / TILE_SIZE)
        gy = int((my - MAP_OFFSET_Y) / TILE_SIZE)
        if 0 <= gx < self.current_map.width and 0 <= gy < self.current_map.height:
            rect = pygame.Rect(MAP_OFFSET_X + gx * TILE_SIZE, MAP_OFFSET_Y + gy * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(self.screen, YELLOW, rect, 2)

    def draw_message(self):
        if not self.message:
            return
        text = self.font_md.render(self.message, True, WHITE)
        bg_w = text.get_width() + 30
        bg_h = 36
        bg = pygame.Rect((WIN_WIDTH - bg_w) // 2, 80, bg_w, bg_h)
        pygame.draw.rect(self.screen, (0, 0, 0), bg)
        pygame.draw.rect(self.screen, GOLD, bg, 2)
        self.screen.blit(text, (bg.x + 15, bg.y + 6))

    def draw_gameover(self):
        overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))
        t1 = self.font_xl.render("你战死了……", True, RED)
        t2 = self.font_md.render("空格重新开始", True, WHITE)
        self.screen.blit(t1, (WIN_WIDTH // 2 - 100, WIN_HEIGHT // 2 - 30))
        self.screen.blit(t2, (WIN_WIDTH // 2 - 70, WIN_HEIGHT // 2 + 20))

    def draw_victory(self):
        overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 10, 0, 230))
        self.screen.blit(overlay, (0, 0))
        t1 = self.font_xl.render("大 明 王 朝", True, GOLD)
        t2 = self.font_lg.render("洪武元年，朱元璋登基称帝", True, YELLOW)
        t3 = self.font_md.render("恭喜通关！", True, WHITE)
        t4 = self.font_sm.render("空格退出游戏", True, LIGHT_GRAY)
        self.screen.blit(t1, (WIN_WIDTH // 2 - 120, WIN_HEIGHT // 2 - 80))
        self.screen.blit(t2, (WIN_WIDTH // 2 - 160, WIN_HEIGHT // 2 - 30))
        self.screen.blit(t3, (WIN_WIDTH // 2 - 50, WIN_HEIGHT // 2 + 20))
        self.screen.blit(t4, (WIN_WIDTH // 2 - 60, WIN_HEIGHT // 2 + 60))

    # ----------------------------------------------------------
    # 主循环
    # ----------------------------------------------------------
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
