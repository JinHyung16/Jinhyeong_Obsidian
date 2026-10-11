# -*- coding: utf-8 -*-
"""Checks the difficulty and money curves without playing.

Reads the skill tables for what a fully bought ball can do, applies the same
stage formula the game uses, and prints where the two stop lining up.

The numbers here have to match the C++ or the report is fiction:
  stage formula   URollBallGameInstance::GetStageSetup
  stat totals     URollBallSkillGraph::Recalculate
  clamps          FRollBallSkillStats::ClampAmount
  weapon damage   URollBallWeaponComponent::TickComponent
"""

import csv
import io
import os

DATA = r"C:\jinhyeong_project\UE5_RollBall\Content\Data"

# --- Stage rules, from FRollBallStageRules ---------------------------------

MAX_STAGE = 100
BASE_SURVIVE_SECONDS = 720.0
SURVIVE_SECONDS_PER_STAGE = 6.0
ELITE_SECONDS = 120.0
BOSS_EVERY = 5

ENEMY_HEALTH_GROWTH = 1.038
BASE_SPAWN_INTERVAL = 1.6
SPAWN_RATE_GROWTH = 1.025
MIN_SPAWN_INTERVAL = 0.25
ELITE_SCALE = 2.5
BOSS_SCALE = 18.0

BASE_GOLD_PER_KILL = 5
SURVIVAL_GOLD_PER_MINUTE = 40
REBIRTH_GOLD_PER_STAGE = 800
REBIRTH_GOLD_BONUS = 0.10
GOLD_GROWTH = 1.03

MAX_ALIVE = 70

# --- Weapon rules, from URollBallWeaponComponent ---------------------------

DAMAGE_INTERVAL = 0.5

# Enemy base health, from ARollBallEnemy::Setup.
ENEMY_BASE_HEALTH = {
    "Chaser": 3.0,
    "Roller": 6.0,
    "Blocker": 10.0,
    "Meteor": 4.0,
}

# What the normal phase spawns, from PickKindForPhase.
NORMAL_MIX = {"Chaser": 0.65, "Roller": 0.20, "Blocker": 0.15}
ELITE_MIX = {"Chaser": 0.50, "Roller": 0.25, "Meteor": 0.25}

# Base stat values, from FRollBallSkillStats::BaseAmountOf.
BASE_STATS = {
    "MaxHealth": 1.0,
    "MoveForce": 500.0,
    "MaxSpeed": 1200.0,
    "KnockbackResist": 0.0,
    "PickupRadius": 200.0,
    "GoldGain": 1.0,
    "RebirthMultiplier": 1.0,
    "SawSize": 1.0,
    "SawDamage": 1.0,
    "HammerCount": 1.0,
    "HammerKnockback": 1.0,
    "HammerSpinSpeed": 90.0,
    "HammerDamage": 1.0,
    "BulldozerWidth": 1.0,
    "BulldozerPush": 1.0,
    "DrillDamage": 1.0,
    "DrillPierce": 0.0,
}

# Ceilings, from FRollBallSkillStats::ClampAmount.
CLAMPS = {
    "MaxHealth": (1.0, 7.0),
    "KnockbackResist": (0.0, 0.8),
    "SawSize": (1.0, 2.0),
    "HammerCount": (1.0, 4.0),
    "BulldozerWidth": (1.0, 3.0),
}

UNLOCK_STATS = {"SawUnlock", "HammerUnlock", "BulldozerUnlock", "DrillUnlock", "DrillTopMount"}


def read_csv(name):
    path = os.path.join(DATA, name)
    with io.open(path, encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def full_tree_stats():
    """Every node at max level, the way Recalculate would add them up."""
    definitions = {row["Name"]: row for row in read_csv("DT_SkillDef.csv")}
    placements = read_csv("DT_SkillPlacement.csv")

    totals = dict(BASE_STATS)
    cost = 0

    for placement in placements:
        definition = definitions[placement["DefinitionRowName"]]
        stat = definition["GrantStat"]
        amount = float(definition["AmountPerLevel"])
        max_level = int(definition["MaxLevel"])
        base_cost = int(definition["BaseCost"])
        growth = float(definition["CostGrowth"])

        for level in range(max_level):
            cost += round(base_cost * (growth ** level) / 5) * 5

        if stat == "None":
            continue

        totals[stat] = totals.get(stat, 0.0) + amount * max_level

    for stat, (low, high) in CLAMPS.items():
        if stat in totals:
            totals[stat] = max(low, min(high, totals[stat]))

    for stat in UNLOCK_STATS:
        totals[stat] = min(1.0, totals.get(stat, 0.0))

    if totals.get("HammerUnlock", 0.0) < 1.0:
        totals["HammerCount"] = 0.0

    return totals, cost


def damage_per_second(stats):
    """Sum of every part, each hitting one enemy once per interval."""
    per_hit = 0.0

    if stats.get("HammerUnlock", 0.0) >= 1.0:
        per_hit += stats["HammerCount"] * stats["HammerDamage"]

    if stats.get("SawUnlock", 0.0) >= 1.0:
        per_hit += stats["SawDamage"]

    if stats.get("DrillUnlock", 0.0) >= 1.0:
        drill = stats["DrillDamage"] + stats["DrillPierce"]
        per_hit += drill
        if stats.get("DrillTopMount", 0.0) >= 1.0:
            per_hit += drill

    # The bulldozer only pushes, so it adds nothing here.
    return per_hit / DAMAGE_INTERVAL


def stage_setup(stage):
    steps = stage - 1
    return dict(
        stage=stage,
        survive=BASE_SURVIVE_SECONDS + SURVIVE_SECONDS_PER_STAGE * steps,
        elite=min(ELITE_SECONDS, (BASE_SURVIVE_SECONDS + SURVIVE_SECONDS_PER_STAGE * steps) * 0.5),
        boss=(stage % BOSS_EVERY == 0),
        health=ENEMY_HEALTH_GROWTH ** steps,
        spawn=max(MIN_SPAWN_INTERVAL, BASE_SPAWN_INTERVAL / (SPAWN_RATE_GROWTH ** steps)),
        gold=max(1, round(BASE_GOLD_PER_KILL * (GOLD_GROWTH ** steps))),
    )


def mixed_health(mix, scale, rank_scale):
    return sum(ENEMY_BASE_HEALTH[kind] * weight for kind, weight in mix.items()) * scale * rank_scale


def main():
    stats, tree_cost = full_tree_stats()
    dps = damage_per_second(stats)

    print("만렙 스탯")
    print("  체력 %d, 가속 %d, 최고속도 %d, 밀림저항 %.0f%%"
          % (stats["MaxHealth"], stats["MoveForce"], stats["MaxSpeed"],
             stats["KnockbackResist"] * 100))
    print("  헤머 %d개 피해 %.0f, 톱 피해 %.0f 크기 %.1f배, 드릴 피해 %.0f 관통 %.0f%s"
          % (stats["HammerCount"], stats["HammerDamage"], stats["SawDamage"],
             stats["SawSize"], stats["DrillDamage"], stats["DrillPierce"],
             ", 위쪽 추가" if stats.get("DrillTopMount") else ""))
    print("  골드 획득 %.0f%%, 환생 배수 %.0f%%"
          % (stats["GoldGain"] * 100, stats["RebirthMultiplier"] * 100))
    print("  초당 피해 %.1f (적 하나에게)" % dps)
    print("  트리 전부 사는 값 %s 골드" % format(tree_cost, ","))
    print("")

    header = ("스테이지", "버틸시간", "스폰간격", "초당스폰", "일반체력", "처치초",
              "따라가나", "정예체력", "보스체력", "판당골드")
    print("%-9s %8s %8s %8s %9s %7s %8s %9s %10s %11s" % header)

    trouble_at = None
    rows = [1, 2, 3, 5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100]

    for stage in rows:
        setup = stage_setup(stage)

        normal_health = mixed_health(NORMAL_MIX, setup["health"], 1.0)
        elite_health = mixed_health(ELITE_MIX, setup["health"], ELITE_SCALE)
        boss_health = ENEMY_BASE_HEALTH["Chaser"] * setup["health"] * BOSS_SCALE

        seconds_to_kill = normal_health / dps
        spawns_per_second = 1.0 / setup["spawn"]

        # One ball can only be touching a few enemies at once. Three is a
        # generous guess for hammers sweeping a crowd.
        kills_per_second = 3.0 / seconds_to_kill
        keeps_up = kills_per_second >= spawns_per_second

        if not keeps_up and trouble_at is None:
            trouble_at = stage

        # Everything spawned in a stage, if the cap never bit.
        spawned = setup["survive"] / setup["spawn"]
        kill_gold = min(spawned, setup["survive"] * kills_per_second) * setup["gold"]
        survive_gold = setup["survive"] / 60.0 * round(SURVIVAL_GOLD_PER_MINUTE * (GOLD_GROWTH ** (stage - 1)))
        gold_if_all = (kill_gold + survive_gold) * stats["GoldGain"]

        print("%-9d %8.0f %8.2f %8.1f %9.0f %7.1f %8s %9.0f %10.0f %11s"
              % (stage, setup["survive"], setup["spawn"], spawns_per_second,
                 normal_health, seconds_to_kill, "예" if keeps_up else "아니오",
                 elite_health, boss_health, format(int(gold_if_all), ",")))

    print("")
    print("판정")

    if trouble_at is None:
        print("  처치 속도가 100 스테이지까지 스폰을 따라간다")
    else:
        print("  스테이지 %d 부터 처치 속도가 스폰을 못 따라간다" % trouble_at)

    # How long it takes to buy the tree, once, at a mid stage.
    mid = stage_setup(20)
    mid_health = mixed_health(NORMAL_MIX, mid["health"], 1.0)
    mid_kills = mid["survive"] * (3.0 / (mid_health / dps))
    mid_gold = (min(mid["survive"] / mid["spawn"], mid_kills) * mid["gold"]
                + mid["survive"] / 60.0 * round(SURVIVAL_GOLD_PER_MINUTE * (GOLD_GROWTH ** 19))) * stats["GoldGain"]

    print("  스테이지 20 한 판 수입 %s 골드, 트리 전부 사려면 %.1f 판"
          % (format(int(mid_gold), ","), tree_cost / max(1.0, mid_gold)))

    for stage in (10, 30, 50, 100):
        reward = stage * REBIRTH_GOLD_PER_STAGE * stats["RebirthMultiplier"]
        print("  최고 %d 스테이지에서 환생하면 %s 골드 (트리 총액의 %.0f%%)"
              % (stage, format(int(reward), ","), reward / tree_cost * 100))

    print("")
    print("  환생 %d회 누적 골드 보너스 +%.0f%%" % (10, 10 * REBIRTH_GOLD_BONUS * 100))

    # 첫 판은 무기가 없다. 생존 골드만 들어온다.
    first = stage_setup(1)
    first_survival = first["survive"] / 60.0 * SURVIVAL_GOLD_PER_MINUTE
    print("  첫 판 무기 없이 끝까지 버티면 %d 골드" % int(first_survival))
    print("")

    # 위 표는 트리를 전부 산 공 기준이라 초반이 안 보인다. 실제로 처음 겪는
    # 것은 무기 하나짜리 공이다.
    print("초반 (헤머 하나, 피해 1)")

    early_dps = 1.0 / DAMAGE_INTERVAL
    early_limit = None

    for stage in range(1, MAX_STAGE + 1):
        setup = stage_setup(stage)
        health = mixed_health(NORMAL_MIX, setup["health"], 1.0)
        if 3.0 / (health / early_dps) < 1.0 / setup["spawn"]:
            early_limit = stage
            break

    if early_limit is None:
        print("  무기 하나로 100 스테이지까지 따라간다. 트리가 할 일이 없다")
    else:
        print("  무기 하나로는 스테이지 %d 부터 스폰을 못 따라간다" % early_limit)
        print("  그 전까지 벌 수 있는 골드가 트리의 첫 갈래를 사는 값이어야 한다")


if __name__ == "__main__":
    main()
