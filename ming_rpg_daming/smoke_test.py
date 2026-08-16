# -*- coding: utf-8 -*-
"""运行时烟雾测试：启动游戏并模拟运行多帧，排查崩溃"""
import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
pygame.init()

import importlib.util
spec = importlib.util.spec_from_file_location("main", os.path.join(os.path.dirname(__file__), "main.py"))
main_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_mod)

Game = main_mod.Game

print("=== 运行时烟雾测试 ===")
errors = []

try:
    game = Game()
    print("[OK] 游戏初始化成功")
    print(f"  初始状态: {game.state}")
    print(f"  当前地图: {game.current_map.name}")
    print(f"  玩家等级: {game.player.level}")
    print(f"  玩家位置: ({game.player.x:.0f}, {game.player.y:.0f})")

    # 模拟100帧游戏运行
    for i in range(100):
        # 模拟一些按键事件
        if i == 10:
            # 模拟按空格推进对话
            event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
            pygame.event.post(event)
        if i == 20:
            event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
            pygame.event.post(event)
        if i == 30:
            # 模拟按A开启挂机
            event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a)
            pygame.event.post(event)
        if i == 50:
            # 模拟按A关闭挂机
            event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a)
            pygame.event.post(event)
        if i == 60:
            # 模拟按E打开装备面板
            event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
            pygame.event.post(event)
        if i == 70:
            # 模拟按E关闭装备面板
            event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
            pygame.event.post(event)
        if i == 80:
            # 模拟按F1进入编辑器
            event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F1)
            pygame.event.post(event)
        if i == 90:
            # 模拟按F1退出编辑器
            event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F1)
            pygame.event.post(event)

        game.handle_events()
        game.update()
        game.draw()

    print("[OK] 100帧模拟运行无崩溃")
    print(f"  最终状态: {game.state}")
    print(f"  挂机模式: {game.player.afk_mode}")
    print(f"  编辑器模式: {game.editor_mode}")

    # 测试所有地图加载
    map_files = ["zhongli_north", "zhongli_south", "huangjue_temple", "suzhou",
                 "taipingfu", "yingtianfu", "huizhou", "zhedong", "yuan_capital"]
    for mf in map_files:
        try:
            game.load_map(mf, use_spawn=True)
            game.draw()
            print(f"[OK] 地图加载并渲染: {mf} ({game.current_map.name})")
        except Exception as e:
            errors.append(f"地图{mf}加载失败: {e}")
            print(f"[FAIL] 地图加载: {mf} - {e}")

    # 测试战斗模拟
    game.load_map("zhongli_north", use_spawn=True)
    game.player.level = 10
    game.player.hp = 500
    game.player.max_hp = 500
    from main import Monster
    test_monster = Monster({"type": "shanzei", "x": 5, "y": 5, "level": 3})
    game.start_battle(test_monster)
    print(f"[OK] 进入战斗状态: {game.state}")

    # 模拟战斗回合
    for i in range(20):
        if game.battle and game.battle.turn == "player" and not game.battle.over:
            game.battle.player_attack()
        game.update()
        game.draw()
        if game.battle and game.battle.over:
            break

    if game.battle:
        print(f"[OK] 战斗结束: victory={game.battle.victory}, over={game.battle.over}")

    # 测试砍树
    game.state = "playing"
    game.battle = None
    tree_count_before = len(game.current_map.trees)
    if tree_count_before > 0:
        t = game.current_map.trees[0]
        game.player.x = t["x"] * 24 - 24
        game.player.y = t["y"] * 24
        game.player.direction = "right"
        game.try_chop_tree()
        tree_count_after = len(game.current_map.trees)
        print(f"[OK] 砍树: {tree_count_before} -> {tree_count_after} 棵")

    print("\n=== 烟雾测试完成 ===")
    if errors:
        print(f"发现 {len(errors)} 个错误:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("全部通过，无运行时错误")

except Exception as e:
    import traceback
    traceback.print_exc()
    errors.append(str(e))

pygame.quit()
sys.exit(0 if not errors else 1)
