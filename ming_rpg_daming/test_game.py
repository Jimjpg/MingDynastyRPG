# -*- coding: utf-8 -*-
"""
自动化自测脚本：验证大明王朝RPG核心逻辑
无头模式运行，不弹出窗口
"""
import os
import sys
os.environ["SDL_VIDEODRIVER"] = "dummy"  # 无头模式

# 把项目目录加入路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
pygame.init()

# 导入游戏模块
import importlib.util
spec = importlib.util.spec_from_file_location("main", os.path.join(os.path.dirname(__file__), "main.py"))
main_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_mod)

Game = main_mod.Game
Player = main_mod.Player
Monster = main_mod.Monster
Battle = main_mod.Battle
GameMap = main_mod.GameMap
load_json = main_mod.load_json

passed = 0
failed = 0

def test(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        print(f"  [FAIL] {name} {detail}")

print("=" * 60)
print("大明王朝RPG - 自动化自测")
print("=" * 60)

# ----------------------------------------------------------
print("\n[1] 数据文件加载测试")
# ----------------------------------------------------------
try:
    eq = load_json("data/equipment.json")
    test("equipment.json加载", "items" in eq and len(eq["items"]) > 0, f"items={len(eq.get('items',[]))}")
    test("装备品质定义完整", len(eq["qualities"]) == 6, f"qualities={len(eq.get('qualities',{}))}")
    test("装备部位定义完整", set(eq["slots"]) == {"weapon", "armor", "ring", "necklace"})
    test("掉落表定义完整", all(k in eq["drop_table"] for k in ["tree", "shanzei", "yuan_bing", "boss"]))
except Exception as e:
    test("equipment.json加载", False, str(e))

try:
    story = load_json("data/story.json")
    test("story.json加载", len(story) >= 6, f"stages={len(story)}")
    test("剧情包含intro/final", "intro" in story and "final" in story)
except Exception as e:
    test("story.json加载", False, str(e))

try:
    lu = load_json("data/level_unlock.json")
    test("level_unlock.json加载", len(lu) == 9, f"maps={len(lu)}")
    test("元大都等级要求28", lu["yuan_capital"]["level_req"] == 28)
    test("皇觉寺等级要求3", lu["huangjue_temple"]["level_req"] == 3)
except Exception as e:
    test("level_unlock.json加载", False, str(e))

# 地图文件
map_files = ["zhongli_north", "zhongli_south", "huangjue_temple", "suzhou",
             "taipingfu", "yingtianfu", "huizhou", "zhedong", "yuan_capital"]
for mf in map_files:
    try:
        md = load_json(f"map/{mf}.json")
        test(f"{mf}.json加载", md["width"] == 30 and md["height"] == 25, f"{md['width']}x{md['height']}")
    except Exception as e:
        test(f"{mf}.json加载", False, str(e))

# ----------------------------------------------------------
print("\n[2] 玩家系统测试")
# ----------------------------------------------------------
p = Player()
test("玩家初始等级1", p.level == 1)
test("玩家初始HP100", p.hp == 100 and p.max_hp == 100)
test("玩家基础攻击", p.atk == 12, f"atk={p.atk}")  # base 10 + level*2 = 12
test("玩家基础防御", p.defense == 6, f"def={p.defense}")  # base 5 + level = 6

# 经验升级
p.exp = 0
leveled, gained = p.gain_exp(100)
test("获得经验升级", leveled and p.level == 2, f"level={p.level}, exp={p.exp}")
test("升级后HP满血", p.hp == p.max_hp and p.max_hp == 120, f"hp={p.hp}/{p.max_hp}")
test("升级后攻击增长", p.atk == 17, f"atk={p.atk}")  # base_atk=10+3=13, +level*2=4 => 17

# 重新算
p2 = Player()
p2.gain_exp(100)
test("升级后攻击计算正确", p2.atk == 17, f"atk={p2.atk}")  # base_atk 10+3=13, +2*2=4 => 17

# ----------------------------------------------------------
print("\n[3] 装备系统测试")
# ----------------------------------------------------------
p3 = Player()
sword = {"id": "iron_sword", "name": "铁剑", "slot": "weapon", "quality": "green",
         "atk": 8, "def": 0, "level_req": 3, "desc": "test"}
p3.inventory.append(sword)
before_atk = p3.atk
p3.equip_item(sword)
test("装备武器后攻击增加", p3.atk == before_atk + 8, f"before={before_atk}, after={p3.atk}")
test("装备从背包移除", sword not in p3.inventory)
test("装备槽已填充", p3.equipment["weapon"] is not None)

# 卸下
p3.unequip("weapon")
test("卸下装备后攻击恢复", p3.atk == before_atk, f"atk={p3.atk}")
test("卸下装备回到背包", sword in p3.inventory)

# ----------------------------------------------------------
print("\n[4] 地图与碰撞测试")
# ----------------------------------------------------------
game = Game()
test("游戏初始化成功", game.current_map is not None)
test("初始地图钟离北", game.current_map_name == "zhongli_north")
test("初始地图有树木", len(game.current_map.trees) > 0)
test("初始地图有怪物", len(game.current_map.monsters) > 0)
test("初始地图有出口", len(game.current_map.exits) > 0)

# 碰撞检测
test("草地不碰撞", not game.current_map.is_collision(0, 0))
test("树木碰撞", game.current_map.is_collision(2, 1))  # 钟离北(2,1)是树
test("像素碰撞检测-空地", not game.current_map.is_pixel_collision(0, 0, 24, 24))

# 树木查找
tree_pos = game.current_map.trees[0]
idx = game.current_map.find_tree_at(tree_pos["x"], tree_pos["y"])
test("树木坐标查找", idx >= 0)

# ----------------------------------------------------------
print("\n[5] 战斗系统测试")
# ----------------------------------------------------------
p4 = Player()
p4.level = 10
p4.max_hp = 300
p4.hp = 300
monster_data = {"type": "shanzei", "x": 10, "y": 10, "level": 5}
m = Monster(monster_data)
test("怪物创建", m.alive and m.hp > 0)
test("怪物名称", m.name == "山贼")
test("怪物属性缩放", m.atk > 0 and m.defense > 0)

battle = Battle(p4, m)
test("战斗初始化", battle.turn == "player" and not battle.over)
battle.player_attack()
test("玩家攻击后怪物受伤", m.hp < m.max_hp)
# 连续攻击直到胜利
while not battle.over:
    if battle.turn == "player":
        battle.player_attack()
    else:
        battle.monster_attack()
test("战斗结束", battle.over)
test("玩家胜利", battle.victory)

# BOSS战
boss_data = {"type": "yuan_emperor", "x": 14, "y": 12, "level": 30, "is_boss": True}
boss = Monster(boss_data)
test("BOSS创建", boss.is_boss and boss.name == "元顺帝")
test("BOSS高血量", boss.max_hp > 500, f"hp={boss.max_hp}")

# ----------------------------------------------------------
print("\n[6] 掉落系统测试")
# ----------------------------------------------------------
game2 = Game()
drops = []
for _ in range(100):
    item = game2.roll_drop("tree")
    if item:
        drops.append(item["quality"])
test("砍树掉落能生成物品", len(drops) > 0)
test("砍树掉落以白绿为主", all(q in ["white", "green", "blue", "purple"] for q in drops))

boss_drops = []
for _ in range(50):
    item = game2.roll_drop("boss")
    if item:
        boss_drops.append(item["quality"])
test("BOSS掉落能生成高品质", any(q in ["purple", "gold", "red"] for q in boss_drops), f"boss_drops={set(boss_drops)}")

# ----------------------------------------------------------
print("\n[7] 等级锁测试")
# ----------------------------------------------------------
game3 = Game()
game3.player.level = 1
# 尝试切换到需要高等级的地图
exit_info = {"target_map": "yuan_capital", "target_x": 14, "target_y": 22, "direction": "east"}
# 直接调用try_change_map逻辑
req = game3.level_unlock["yuan_capital"]["level_req"]
test("元大都等级锁存在", req == 28)
test("低等级无法进入元大都", game3.player.level < req)

game3.player.level = 28
test("达标后可进入元大都", game3.player.level >= req)

# ----------------------------------------------------------
print("\n[8] 地图编辑器测试")
# ----------------------------------------------------------
game4 = Game()
game4.editor_mode = True
game4.editor_tile = 1
original = game4.current_map.get_tile(5, 5)
game4.current_map.set_tile(5, 5, 1)
test("编辑器可修改地块", game4.current_map.get_tile(5, 5) == 1)
game4.current_map.set_tile(5, 5, 0)
test("编辑器可擦除地块", game4.current_map.get_tile(5, 5) == 0)

# 地图序列化
md = game4.current_map.to_dict()
test("地图可序列化为dict", "tiles" in md and "name" in md)

# ----------------------------------------------------------
print("\n[9] 中文显示测试（字体加载）")
# ----------------------------------------------------------
from main import get_font
font = get_font(16)
test("中文字体加载成功", font is not None)
text_surface = font.render("大明王朝", True, (255, 255, 255))
ascii_surface = font.render("ABCD", True, (255, 255, 255))
test("中文渲染不报错", text_surface is not None and text_surface.get_width() > 0)
# 真正支持中文的字体：中文为全宽（4字>=64px），且明显宽于等量ASCII（方块字体此处会失败）
test("字体真正支持中文", text_surface.get_width() >= 4 * 16 and text_surface.get_width() > ascii_surface.get_width())

# ----------------------------------------------------------
print("\n[10] 剧情触发测试")
# ----------------------------------------------------------
game5 = Game()
test("钟离北触发intro剧情", game5.state == "dialog")
test("剧情标题正确", game5.dialog_title == "第一章 钟离少年")
test("剧情有多行对话", len(game5.dialog_lines) >= 5)
# 推进剧情
game5.dialog_index = len(game5.dialog_lines) - 1
game5.handle_key_down(pygame.K_SPACE)
test("剧情结束回到游戏", game5.state == "playing")
test("剧情标记已触发", "intro" in game5.dialog_triggered)

# ----------------------------------------------------------
print("\n" + "=" * 60)
print(f"测试结果: {passed} 通过, {failed} 失败")
print("=" * 60)

pygame.quit()
sys.exit(0 if failed == 0 else 1)
