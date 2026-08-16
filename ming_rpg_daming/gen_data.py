# -*- coding: utf-8 -*-
"""
数据生成脚本：生成全部UTF-8编码的JSON配置文件
运行: python gen_data.py
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
MAP_DIR = os.path.join(BASE, "map")
DATA_DIR = os.path.join(BASE, "data")

# Tile ID 定义
# 0=草地 1=土路 2=树木(碰撞) 3=水(碰撞) 4=房屋墙(碰撞) 5=房屋地板
# 6=寺庙墙(碰撞) 7=寺庙地板 8=城池墙(碰撞) 9=城池地板 10=沙地
# 11=石板路 12=山(碰撞) 13=农田 14=帐篷(碰撞) 15=宫殿墙(碰撞) 16=宫殿地板
CHAR_TO_TILE = {
    '.': 0, ',': 1, 'T': 2, '~': 3, '#': 4, '_': 5,
    'H': 6, 'h': 7, 'W': 8, 'S': 9, 's': 10, '-': 11,
    'M': 12, 'F': 13, 'P': 14, '@': 15, '=': 16,
}
COLLISION_TILES = [2, 3, 4, 6, 8, 12, 14, 15]


def parse_map(rows, target_width=30):
    """将字符地图转为二维tile数组，自动规范化行宽"""
    tiles = []
    for row in rows:
        tile_row = []
        for ch in row[:target_width]:
            tile_row.append(CHAR_TO_TILE.get(ch, 0))
        while len(tile_row) < target_width:
            tile_row.append(0)  # 不足部分填充草地
        tiles.append(tile_row)
    return tiles


def find_tiles(tiles, tile_id):
    """找出指定tile_id的所有坐标"""
    result = []
    for y, row in enumerate(tiles):
        for x, t in enumerate(row):
            if t == tile_id:
                result.append({"x": x, "y": y})
    return result


def save_json(filepath, data):
    """保存为UTF-8编码的JSON"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  已生成: {os.path.relpath(filepath, BASE)}")


# ============================================================
# 地图1: 钟离北 (出生点) - 乡村田园
# ============================================================
zhongli_north_rows = [
    "..............................",
    "..TT..........TT..............",
    "..TT...FF.....TT....TT........",
    ".......FF...........TT........",
    "...####.....F.................",
    "...#__#____...................",
    "...#__#____...................",
    "...#__#,,,,,..................",
    "........,,....TT..FF..........",
    "........,,....TT..FF..........",
    "........,,........FF..........",
    "........,,....####............",
    "........,,....#__#............",
    "........,,....#__#............",
    "........,,....####............",
    "........,,....................",
    "........,,....TT..............",
    "........,,....TT..............",
    "........,,....................",
    "........,,....................",
    "........,,....................",
    "........,,....................",
    "........,,....................",
    "........,,....................",
    "..............................",
]

# ============================================================
# 地图2: 钟离南 - 荒凉沙地
# ============================================================
zhongli_south_rows = [
    "..............................",
    "..ssss.......................",
    "..ssss...TT..................",
    "..ssss........................",
    "........,,....................",
    "........,,....####............",
    "........,,....#__#............",
    "........,,....#__#............",
    "........,,....####............",
    "........,,....................",
    "........,,....TT..............",
    "........,,....TT..............",
    "........,,....................",
    "........,,......ssss..........",
    "........,,......ssss..........",
    "........,,......ssss..TT......",
    "........,,............TT......",
    "........,,....................",
    "........,,....................",
    "........,,....................",
    "........,,....................",
    "........,,....................",
    "........,,....................",
    "..............................",
    "..............................",
]

# ============================================================
# 地图3: 皇觉寺 - 寺庙场景
# ============================================================
huangjue_rows = [
    "..............................",
    "..TT..........................",
    "..TT....HHHHHHHHHH............",
    "........HhhhhhhhhhH...........",
    "........HhhhhhhhhhH...........",
    "........Hhhh==hhhhH...........",
    "........HhhhhhhhhhH...........",
    "........HHHHHhHHHHH...........",
    ".............h................",
    ".............h................",
    "..TT.........h..........TT....",
    "..TT.........h..........TT....",
    ".............h................",
    ".............h................",
    ".............h................",
    "......####...h...####.........",
    "......#__#...h...#__#.........",
    "......#__#...h...#__#.........",
    "......####...h...####.........",
    ".............h................",
    ".............h................",
    ".............h................",
    ".............h................",
    "..............................",
    "..............................",
]

# ============================================================
# 地图4: 苏州 - 城池
# ============================================================
suzhou_rows = [
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
    "WSSSSSSSSSSSSSSSSSSSSSSSSSSSSW",
    "WS----SSSS####SSSS----SSSSSSSW",
    "WS----SSSS#__#SSSS----SSSSSSSW",
    "WS----SSSS#__#SSSS----SSSSSSSW",
    "WS----SSSS####SSSS----SSSSSSSW",
    "WS----SSSSSSSSSSSS----SSSSSSSW",
    "WS----SSSS####SSSS----SSSSSSSW",
    "WS----SSSS#__#SSSS----SSSSSSSW",
    "WS----SSSS#__#SSSS----SSSSSSSW",
    "WS----SSSS####SSSS----SSSSSSSW",
    "WS----SSSSSSSSSSSS----SSSSSSSW",
    "WS----SSSSSSSSSSSS----SSSSSSSW",
    "WS----SSSS####SSSS----SSSSSSSW",
    "WS----SSSS#__#SSSS----SSSSSSSW",
    "WS----SSSS#__#SSSS----SSSSSSSW",
    "WS----SSSS####SSSS----SSSSSSSW",
    "WS----SSSSSSSSSSSS----SSSSSSSW",
    "WS----SSSSSSSSSSSS----SSSSSSSW",
    "WSSSSSSSSSSSSSSSSSSSSSSSSSSSSW",
    "WSSSSSSSSSSSSSSSSSSSSSSSSSSSSW",
    "WSSSSSSSSSSSSSSSSSSSSSSSSSSSSW",
    "WSSSSSSSSSSSSSSSSSSSSSSSSSSSSW",
    "WSSSSSSSSSSSSSSSSSSSSSSSSSSSSW",
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
]

# ============================================================
# 地图5: 太平府 - 中型城镇
# ============================================================
taipingfu_rows = [
    "..............................",
    "..WWWWWWWWWWWWWWWWWWWWWW......",
    "..WSSSSSSSSSSSSSSSSSSSSW......",
    "..WS----####SS----####SW......",
    "..WS----#__#SS----#__#SW......",
    "..WS----#__#SS----#__#SW......",
    "..WS----####SS----####SW......",
    "..WSSSSSSSSSSSSSSSSSSSSW......",
    "..WS----####SSSSSS----SW......",
    "..WS----#__#SSSSSS----SW......",
    "..WS----#__#SSSSSS----SW......",
    "..WS----####SSSSSS----SW......",
    "..WSSSSSSSSSSSSSSSSSSSSW......",
    "..WS----####SS----####SW......",
    "..WS----#__#SS----#__#SW......",
    "..WS----#__#SS----#__#SW......",
    "..WS----####SS----####SW......",
    "..WSSSSSSSSSSSSSSSSSSSSW......",
    "..WWWWWWWWWWWWWWWWWWWWWW......",
    "..............................",
    "..TT..........................",
    "..TT....TT....................",
    "........TT....................",
    "..............................",
    "..............................",
]

# ============================================================
# 地图6: 应天府 - 大型城池
# ============================================================
yingtianfu_rows = [
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
    "WSSSSSSSSSSSSSSSSSSSSSSSSSSSSW",
    "WS---####SSS---####SSS---####SW",
    "WS---#__#SSS---#__#SSS---#__#SW",
    "WS---#__#SSS---#__#SSS---#__#SW",
    "WS---####SSS---####SSS---####SW",
    "WSSSSSSSSSSSSSSSSSSSSSSSSSSSSW",
    "WS---####SSS---####SSS---####SW",
    "WS---#__#SSS---#__#SSS---#__#SW",
    "WS---#__#SSS---#__#SSS---#__#SW",
    "WS---####SSS---####SSS---####SW",
    "WSSSSSSSSSSSSSSSSSSSSSSSSSSSSW",
    "WSSSSSSSSSSSSSSSSSSSSSSSSSSSSW",
    "WS---####SSS---####SSS---####SW",
    "WS---#__#SSS---#__#SSS---#__#SW",
    "WS---#__#SSS---#__#SSS---#__#SW",
    "WS---####SSS---####SSS---####SW",
    "WSSSSSSSSSSSSSSSSSSSSSSSSSSSSW",
    "WS---####SSS---####SSS---####SW",
    "WS---#__#SSS---#__#SSS---#__#SW",
    "WS---#__#SSS---#__#SSS---#__#SW",
    "WS---####SSS---####SSS---####SW",
    "WSSSSSSSSSSSSSSSSSSSSSSSSSSSSW",
    "WSSSSSSSSSSSSSSSSSSSSSSSSSSSSW",
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
]

# ============================================================
# 地图7: 徽州 - 山地
# ============================================================
huizhou_rows = [
    "MMMMMMMMMMMMMMMMMMMMMMMMMMMMMM",
    "M............................M",
    "M..TT....MMMM....TT..........M",
    "M..TT....M..M....TT..........M",
    "M........M..M................M",
    "M..####..M..M..####..........M",
    "M..#__#..M..M..#__#..........M",
    "M..#__#..M..M..#__#..........M",
    "M..####..M..M..####..........M",
    "M........M..M................M",
    "M..TT....M..M....TT..........M",
    "M..TT....M..M....TT..........M",
    "M........M..M................M",
    "M..####..M..M..####..........M",
    "M..#__#..M..M..#__#..........M",
    "M..#__#..M..M..#__#..........M",
    "M..####..M..M..####..........M",
    "M........M..M................M",
    "M..TT....MMMM....TT..........M",
    "M..TT............TT..........M",
    "M............................M",
    "M............................M",
    "M............................M",
    "M............................M",
    "MMMMMMMMMMMMMMMMMMMMMMMMMMMMMM",
]

# ============================================================
# 地图8: 浙东 - 水乡
# ============================================================
zhedong_rows = [
    "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
    "~............................~",
    "~..TT....~~~~....TT..........~",
    "~..TT....~~~~....TT..........~",
    "~........~~~~................~",
    "~..####..~~~~..####..........~",
    "~..#__#..~~~~..#__#..........~",
    "~..#__#..~~~~..#__#..........~",
    "~..####..~~~~..####..........~",
    "~........~~~~................~",
    "~..TT....~~~~....TT..........~",
    "~..TT....~~~~....TT..........~",
    "~........~~~~................~",
    "~..####..~~~~..####..........~",
    "~..#__#..~~~~..#__#..........~",
    "~..#__#..~~~~..#__#..........~",
    "~..####..~~~~..####..........~",
    "~........~~~~................~",
    "~..TT....~~~~....TT..........~",
    "~..TT............TT..........~",
    "~............................~",
    "~............................~",
    "~............................~",
    "~............................~",
    "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
]

# ============================================================
# 地图9: 元大都 - 宫殿最终BOSS
# ============================================================
yuan_capital_rows = [
    "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",
    "@============================@",
    "@============================@",
    "@==@@======@@======@@======@@=@",
    "@==@@======@@======@@======@@=@",
    "@============================@",
    "@============================@",
    "@==@@======@@======@@======@@=@",
    "@==@@======@@======@@======@@=@",
    "@============================@",
    "@============================@",
    "@=========@@@@@@@============@",
    "@=========@=====@============@",
    "@=========@=====@============@",
    "@=========@=====@============@",
    "@=========@@@@@@@============@",
    "@============================@",
    "@============================@",
    "@==@@======@@======@@======@@=@",
    "@==@@======@@======@@======@@=@",
    "@============================@",
    "@============================@",
    "@============================@",
    "@============================@",
    "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",
]


def build_map_data(name, rows, spawn, exits, monsters, story_trigger=None, bgm=None):
    tiles = parse_map(rows)
    trees = find_tiles(tiles, 2)
    return {
        "name": name,
        "width": len(rows[0]),
        "height": len(rows),
        "tile_size": 24,
        "tiles": tiles,
        "collision_tiles": COLLISION_TILES,
        "exits": exits,
        "trees": trees,
        "monsters": monsters,
        "spawn": spawn,
        "story_trigger": story_trigger,
    }


def generate_all_maps():
    print("=== 生成地图文件 ===")

    # 钟离北
    m1 = build_map_data(
        "钟离北",
        zhongli_north_rows,
        spawn={"x": 4, "y": 5},
        exits=[
            {"x": 8, "y": 24, "target_map": "zhongli_south", "target_x": 8, "target_y": 1, "direction": "south"},
        ],
        monsters=[
            {"x": 18, "y": 10, "type": "shanzei", "level": 1},
            {"x": 22, "y": 16, "type": "shanzei", "level": 2},
        ],
        story_trigger="intro",
    )
    save_json(os.path.join(MAP_DIR, "zhongli_north.json"), m1)

    # 钟离南
    m2 = build_map_data(
        "钟离南",
        zhongli_south_rows,
        spawn={"x": 8, "y": 2},
        exits=[
            {"x": 8, "y": 0, "target_map": "zhongli_north", "target_x": 8, "target_y": 23, "direction": "north"},
            {"x": 29, "y": 12, "target_map": "huangjue_temple", "target_x": 1, "target_y": 12, "direction": "east"},
        ],
        monsters=[
            {"x": 15, "y": 8, "type": "shanzei", "level": 2},
            {"x": 20, "y": 14, "type": "shanzei", "level": 3},
        ],
        story_trigger="famine",
    )
    save_json(os.path.join(MAP_DIR, "zhongli_south.json"), m2)

    # 皇觉寺
    m3 = build_map_data(
        "皇觉寺",
        huangjue_rows,
        spawn={"x": 2, "y": 12},
        exits=[
            {"x": 0, "y": 12, "target_map": "zhongli_south", "target_x": 28, "target_y": 12, "direction": "west"},
            {"x": 13, "y": 24, "target_map": "suzhou", "target_x": 14, "target_y": 22, "direction": "south"},
        ],
        monsters=[
            {"x": 5, "y": 20, "type": "shanzei", "level": 3},
            {"x": 20, "y": 20, "type": "yuan_bing", "level": 4},
        ],
        story_trigger="temple",
    )
    save_json(os.path.join(MAP_DIR, "huangjue_temple.json"), m3)

    # 苏州
    m4 = build_map_data(
        "苏州",
        suzhou_rows,
        spawn={"x": 14, "y": 22},
        exits=[
            {"x": 14, "y": 0, "target_map": "huangjue_temple", "target_x": 13, "target_y": 23, "direction": "north"},
            {"x": 29, "y": 12, "target_map": "taipingfu", "target_x": 1, "target_y": 10, "direction": "east"},
        ],
        monsters=[
            {"x": 5, "y": 12, "type": "yuan_bing", "level": 5},
            {"x": 24, "y": 6, "type": "yuan_bing", "level": 6},
            {"x": 14, "y": 18, "type": "shanzei", "level": 5},
        ],
        story_trigger="red_army",
    )
    save_json(os.path.join(MAP_DIR, "suzhou.json"), m4)

    # 太平府
    m5 = build_map_data(
        "太平府",
        taipingfu_rows,
        spawn={"x": 2, "y": 10},
        exits=[
            {"x": 0, "y": 10, "target_map": "suzhou", "target_x": 28, "target_y": 12, "direction": "west"},
            {"x": 25, "y": 10, "target_map": "yingtianfu", "target_x": 2, "target_y": 12, "direction": "east"},
        ],
        monsters=[
            {"x": 8, "y": 5, "type": "yuan_bing", "level": 7},
            {"x": 18, "y": 14, "type": "yuan_bing", "level": 8},
        ],
        story_trigger=None,
    )
    save_json(os.path.join(MAP_DIR, "taipingfu.json"), m5)

    # 应天府
    m6 = build_map_data(
        "应天府",
        yingtianfu_rows,
        spawn={"x": 2, "y": 12},
        exits=[
            {"x": 0, "y": 12, "target_map": "taipingfu", "target_x": 24, "target_y": 10, "direction": "west"},
            {"x": 29, "y": 12, "target_map": "huizhou", "target_x": 1, "target_y": 12, "direction": "east"},
        ],
        monsters=[
            {"x": 8, "y": 4, "type": "yuan_bing", "level": 10},
            {"x": 18, "y": 9, "type": "yuan_bing", "level": 11},
            {"x": 14, "y": 16, "type": "shanzei", "level": 10},
        ],
        story_trigger=None,
    )
    save_json(os.path.join(MAP_DIR, "yingtianfu.json"), m6)

    # 徽州
    m7 = build_map_data(
        "徽州",
        huizhou_rows,
        spawn={"x": 2, "y": 12},
        exits=[
            {"x": 0, "y": 12, "target_map": "yingtianfu", "target_x": 28, "target_y": 12, "direction": "west"},
            {"x": 29, "y": 12, "target_map": "zhedong", "target_x": 1, "target_y": 12, "direction": "east"},
        ],
        monsters=[
            {"x": 6, "y": 5, "type": "yuan_bing", "level": 13},
            {"x": 22, "y": 14, "type": "yuan_bing", "level": 14},
            {"x": 14, "y": 20, "type": "shanzei", "level": 13},
        ],
        story_trigger=None,
    )
    save_json(os.path.join(MAP_DIR, "huizhou.json"), m7)

    # 浙东
    m8 = build_map_data(
        "浙东",
        zhedong_rows,
        spawn={"x": 2, "y": 12},
        exits=[
            {"x": 0, "y": 12, "target_map": "huizhou", "target_x": 28, "target_y": 12, "direction": "west"},
            {"x": 29, "y": 12, "target_map": "yuan_capital", "target_x": 14, "target_y": 22, "direction": "east"},
        ],
        monsters=[
            {"x": 6, "y": 6, "type": "chen_youliang", "level": 18, "is_boss": True},
            {"x": 22, "y": 14, "type": "zhang_shicheng", "level": 22, "is_boss": True},
            {"x": 14, "y": 20, "type": "yuan_bing", "level": 16},
        ],
        story_trigger="battle",
    )
    save_json(os.path.join(MAP_DIR, "zhedong.json"), m8)

    # 元大都
    m9 = build_map_data(
        "元大都",
        yuan_capital_rows,
        spawn={"x": 14, "y": 22},
        exits=[
            {"x": 14, "y": 24, "target_map": "zhedong", "target_x": 28, "target_y": 12, "direction": "south"},
        ],
        monsters=[
            {"x": 14, "y": 12, "type": "yuan_emperor", "level": 30, "is_boss": True},
        ],
        story_trigger="final",
    )
    save_json(os.path.join(MAP_DIR, "yuan_capital.json"), m9)


def generate_equipment():
    print("=== 生成装备数据 ===")
    equipment = {
        "qualities": {
            "white": {"name": "普通", "color": "#CCCCCC", "multiplier": 1.0},
            "green": {"name": "优秀", "color": "#2ECC71", "multiplier": 1.2},
            "blue": {"name": "稀有", "color": "#3498DB", "multiplier": 1.5},
            "purple": {"name": "珍品", "color": "#9B59B6", "multiplier": 1.8},
            "gold": {"name": "史诗", "color": "#F1C40F", "multiplier": 2.2},
            "red": {"name": "传说", "color": "#E74C3C", "multiplier": 2.8},
        },
        "slots": ["weapon", "armor", "ring", "necklace"],
        "slot_names": {"weapon": "武器", "armor": "衣服", "ring": "戒指", "necklace": "项链"},
        "items": [
            # 武器
            {"id": "wood_sword", "name": "木刀", "slot": "weapon", "quality": "white", "atk": 3, "def": 0, "level_req": 1, "desc": "放牛娃的木刀，聊胜于无"},
            {"id": "iron_sword", "name": "铁剑", "slot": "weapon", "quality": "green", "atk": 8, "def": 0, "level_req": 3, "desc": "普通铁剑，军中常见"},
            {"id": "steel_sword", "name": "钢剑", "slot": "weapon", "quality": "blue", "atk": 15, "def": 0, "level_req": 7, "desc": "精钢打造，锋利无比"},
            {"id": "red_tassel_spear", "name": "红缨枪", "slot": "weapon", "quality": "blue", "atk": 18, "def": 2, "level_req": 10, "desc": "红巾军利器，刺击凌厉"},
            {"id": "dragon_blade", "name": "屠龙刀", "slot": "weapon", "quality": "gold", "atk": 35, "def": 5, "level_req": 20, "desc": "武林至尊，宝刀屠龙"},
            {"id": "heaven_sword", "name": "倚天剑", "slot": "weapon", "quality": "red", "atk": 50, "def": 8, "level_req": 28, "desc": "倚天不出，谁与争锋"},
            # 衣服
            {"id": "cloth_robe", "name": "布衣", "slot": "armor", "quality": "white", "atk": 0, "def": 2, "level_req": 1, "desc": "粗布衣裳，遮体而已"},
            {"id": "leather_armor", "name": "皮甲", "slot": "armor", "quality": "green", "atk": 0, "def": 6, "level_req": 3, "desc": "牛皮缝制，轻便护身"},
            {"id": "iron_armor", "name": "铁甲", "slot": "armor", "quality": "blue", "atk": 0, "def": 12, "level_req": 8, "desc": "铁叶片片，刀枪难入"},
            {"id": "general_armor", "name": "将军铠", "slot": "armor", "quality": "purple", "atk": 3, "def": 20, "level_req": 15, "desc": "大将风范，威震三军"},
            {"id": "dragon_robe", "name": "龙袍", "slot": "armor", "quality": "red", "atk": 5, "def": 35, "level_req": 28, "desc": "九五之尊，天命所归"},
            # 戒指
            {"id": "copper_ring", "name": "铜戒指", "slot": "ring", "quality": "white", "atk": 1, "def": 1, "level_req": 1, "desc": "铜制戒指，朴素无华"},
            {"id": "silver_ring", "name": "银戒指", "slot": "ring", "quality": "green", "atk": 3, "def": 2, "level_req": 5, "desc": "银饰戒指，略有光泽"},
            {"id": "jade_ring", "name": "玉扳指", "slot": "ring", "quality": "blue", "atk": 5, "def": 5, "level_req": 10, "desc": "和田美玉，温润养人"},
            {"id": "gold_ring", "name": "金戒指", "slot": "ring", "quality": "purple", "atk": 8, "def": 6, "level_req": 18, "desc": "足金打造，富贵逼人"},
            # 项链
            {"id": "wood_beads", "name": "木佛珠", "slot": "necklace", "quality": "white", "atk": 0, "def": 2, "level_req": 1, "desc": "皇觉寺佛珠，阿弥陀佛"},
            {"id": "jade_pendant", "name": "玉佩", "slot": "necklace", "quality": "green", "atk": 2, "def": 4, "level_req": 5, "desc": "玉佩吊坠，君子之风"},
            {"id": "gold_pendant", "name": "金锁", "slot": "necklace", "quality": "blue", "atk": 4, "def": 7, "level_req": 10, "desc": "长命金锁，祈福辟邪"},
            {"id": "dragon_necklace", "name": "龙纹项链", "slot": "necklace", "quality": "gold", "atk": 10, "def": 10, "level_req": 22, "desc": "龙纹缠绕，帝王之气"},
        ],
        "drop_table": {
            "tree": {"white": 0.6, "green": 0.3, "blue": 0.08, "purple": 0.02, "gold": 0.0, "red": 0.0},
            "shanzei": {"white": 0.4, "green": 0.35, "blue": 0.18, "purple": 0.06, "gold": 0.01, "red": 0.0},
            "yuan_bing": {"white": 0.25, "green": 0.35, "blue": 0.25, "purple": 0.1, "gold": 0.04, "red": 0.01},
            "boss": {"white": 0.0, "green": 0.1, "blue": 0.3, "purple": 0.35, "gold": 0.2, "red": 0.05},
        },
    }
    save_json(os.path.join(DATA_DIR, "equipment.json"), equipment)


def generate_story():
    print("=== 生成剧情数据 ===")
    story = {
        "intro": {
            "title": "第一章 钟离少年",
            "lines": [
                "元至正四年，濠州钟离。",
                "少年朱重八正在山坡上放牛。",
                "家中早已断粮，父母兄长相继离世……",
                "沉重的赋税和饥荒压得人喘不过气。",
                "【系统】你扮演朱元璋，从这里开始你的传奇之路。",
                "提示：方向键移动，空格砍树/交互，G键挂机修炼，E键打开装备面板。",
            ],
        },
        "famine": {
            "title": "第二章 饥荒流离",
            "lines": [
                "钟离以南，赤地千里。",
                "路边随处可见饿殍，村中人烟稀少。",
                "二哥重六也在逃难中失散了。",
                "为了活命，你决定前往皇觉寺出家。",
            ],
        },
        "temple": {
            "title": "第三章 皇觉寺出家",
            "lines": [
                "皇觉寺中，老僧为你剃度。",
                "师父说：\"佛门广大，可容苦难之人。\"",
                "然而寺中也无余粮，你只得托钵流浪。",
                "三年云游，你见识了民间疾苦，也结识了各路豪杰。",
                "听闻红巾军起义，你心中燃起了一团火。",
            ],
        },
        "red_army": {
            "title": "第四章 投奔红巾军",
            "lines": [
                "你来到郭子兴的红巾军大营。",
                "郭子兴见你相貌奇伟，留为亲兵。",
                "他将义女马氏许配给你——这就是后来的马皇后。",
                "马氏聪慧贤淑，多次在危难中助你脱险。",
                "你正式改名\"朱元璋\"，意为诛灭元朝的利器。",
            ],
        },
        "battle": {
            "title": "第五章 群雄逐鹿",
            "lines": [
                "应天府已定，你以\"高筑墙，广积粮，缓称王\"为策。",
                "鄱阳湖一战，你以火攻大破陈友谅六十万大军。",
                "陈友谅中箭身亡，大汉政权灰飞烟灭。",
                "随后你挥师东进，围困平江。",
                "张士诚困守孤城，终被你所灭。",
                "天下半壁已定，是时候北伐了！",
            ],
        },
        "final": {
            "title": "第六章 北伐灭元",
            "lines": [
                "至正二十七年，你命徐达、常遇春率军二十五万北伐。",
                "\"驱逐胡虏，恢复中华\"的檄文传遍天下。",
                "元顺帝见大势已去，仓皇北逃。",
                "你率军攻入元大都，元朝在中原的统治宣告终结。",
                "洪武元年正月初四，你在应天登基称帝。",
                "国号大明，建元洪武。",
                "一个从放牛娃到开国皇帝的传奇，就此铸就。",
                "【通关】恭喜你完成了《大明王朝》！",
            ],
        },
    }
    save_json(os.path.join(DATA_DIR, "story.json"), story)


def generate_level_unlock():
    print("=== 生成等级解锁数据 ===")
    level_unlock = {
        "zhongli_north": {"level_req": 1, "map_name": "钟离北"},
        "zhongli_south": {"level_req": 1, "map_name": "钟离南"},
        "huangjue_temple": {"level_req": 3, "map_name": "皇觉寺"},
        "suzhou": {"level_req": 6, "map_name": "苏州"},
        "taipingfu": {"level_req": 10, "map_name": "太平府"},
        "yingtianfu": {"level_req": 15, "map_name": "应天府"},
        "huizhou": {"level_req": 18, "map_name": "徽州"},
        "zhedong": {"level_req": 22, "map_name": "浙东"},
        "yuan_capital": {"level_req": 28, "map_name": "元大都"},
    }
    save_json(os.path.join(DATA_DIR, "level_unlock.json"), level_unlock)


if __name__ == "__main__":
    generate_all_maps()
    generate_equipment()
    generate_story()
    generate_level_unlock()
    print("\n=== 全部数据文件生成完毕 ===")
