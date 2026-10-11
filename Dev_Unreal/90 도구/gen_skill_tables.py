# -*- coding: utf-8 -*-
"""Generates the three skill-tree DataTable CSVs.

Layout: a core at the origin, four stems out to four rectangular rings, each
ring with a spur that runs through a gate to a keystone, plus four bridges
that tie neighbouring rings together so the graph has loops rather than
being a plain tree.
"""

import os
import sys

OUT = r"C:\jinhyeong_project\UE5_RollBall\Content\Data"

# ---------------------------------------------------------------------------
# Definitions: (row name, display, branch, kind, stat, amount, maxlevel, cost,
#               growth, required best stage)
# ---------------------------------------------------------------------------

DEFS = []


def add_def(name, display, branch, kind, stat, amount, max_level, cost,
            growth=1.5, required_stage=0, scale=1.0, desc=""):
    DEFS.append(dict(Name=name, DisplayName=display, Description=desc,
                     Branch=branch, NodeKind=kind, ScaleX=scale, ScaleY=scale,
                     GrantStat=stat, AmountPerLevel=amount, MaxLevel=max_level,
                     BaseCost=cost, CostGrowth=growth,
                     RequiredBestStage=required_stage))


add_def("Core", "시작", "Core", "Core", "None", 0, 1, 0, 1.0, 0, 1.3,
        "여기서부터 뻗어 나갑니다.")

# --- Survival (north) ------------------------------------------------------
add_def("Resist_T1", "밀림저항", "Survival", "Small", "KnockbackResist", 0.03, 5, 40)
add_def("Resist_T2", "밀림저항", "Survival", "Small", "KnockbackResist", 0.04, 5, 90)
add_def("Pickup_T1", "획득범위", "Survival", "Small", "PickupRadius", 20, 5, 30)
add_def("Pickup_T2", "획득범위", "Survival", "Small", "PickupRadius", 30, 5, 70)
add_def("Hp_T1", "체력", "Survival", "Notable", "MaxHealth", 1, 1, 150, 1.0, 0, 1.25)
add_def("Hp_T2", "체력", "Survival", "Notable", "MaxHealth", 1, 1, 320, 1.0, 0, 1.25)
add_def("Hp_T3", "체력", "Survival", "Notable", "MaxHealth", 1, 1, 640, 1.0, 0, 1.25)

# --- Mobility (south) ------------------------------------------------------
add_def("Force_T1", "가속", "Mobility", "Small", "MoveForce", 30, 5, 30)
add_def("Force_T2", "가속", "Mobility", "Small", "MoveForce", 45, 5, 70)
add_def("Speed_T1", "속도", "Mobility", "Small", "MaxSpeed", 50, 5, 35)
add_def("Speed_T2", "속도", "Mobility", "Small", "MaxSpeed", 70, 5, 80)
add_def("Force_N", "가속강화", "Mobility", "Notable", "MoveForce", 150, 1, 260, 1.0, 0, 1.25)
add_def("Speed_N", "속도강화", "Mobility", "Notable", "MaxSpeed", 250, 1, 280, 1.0, 0, 1.25)

# --- Weapons: hammer and saw (west) ---------------------------------------
add_def("HammerUnlock", "헤머", "Weapon", "Notable", "HammerUnlock", 1, 1, 300, 1.0, 0, 1.35,
        "공 주변을 도는 헤머를 답니다.")
add_def("HammerCount", "헤머추가", "Weapon", "Notable", "HammerCount", 1, 3, 400, 1.7, 0, 1.3,
        "헤머가 한 개 늘어납니다. 최대 4개.")
add_def("HammerKnock", "헤머넉백", "Weapon", "Small", "HammerKnockback", 0.15, 5, 60)
add_def("HammerSpin", "헤머회전", "Weapon", "Small", "HammerSpinSpeed", 20, 5, 50)
add_def("HammerDmg", "헤머피해", "Weapon", "Small", "HammerDamage", 1, 5, 70)
add_def("SawUnlock", "전기톱", "Weapon", "Notable", "SawUnlock", 1, 1, 300, 1.0, 0, 1.35,
        "공 앞에 전기톱을 답니다.")
add_def("SawSize", "톱크기", "Weapon", "Small", "SawSize", 0.1, 5, 80)
add_def("SawDmg", "톱피해", "Weapon", "Small", "SawDamage", 1, 5, 70)

# --- Weapons: bulldozer and drill, plus economy (east) --------------------
add_def("DozerUnlock", "불도저", "Weapon", "Notable", "BulldozerUnlock", 1, 1, 350, 1.0, 0, 1.35,
        "공 앞에 밀어내는 날을 답니다.")
add_def("DozerWidth", "불도저폭", "Weapon", "Small", "BulldozerWidth", 0.2, 5, 80)
add_def("DozerPush", "밀어내기", "Weapon", "Small", "BulldozerPush", 0.15, 5, 60)
add_def("DrillUnlock", "드릴", "Weapon", "Notable", "DrillUnlock", 1, 1, 350, 1.0, 0, 1.35,
        "공 앞에 드릴을 답니다.")
add_def("DrillDmg", "드릴피해", "Weapon", "Small", "DrillDamage", 1, 5, 70)
add_def("DrillPierce", "드릴관통", "Weapon", "Small", "DrillPierce", 1, 3, 150, 1.6)
add_def("Gold_T1", "골드", "Economy", "Small", "GoldGain", 0.05, 5, 60)
add_def("Gold_T2", "골드", "Economy", "Small", "GoldGain", 0.07, 5, 130)
add_def("Gold_N", "골드강화", "Economy", "Notable", "GoldGain", 0.2, 1, 420, 1.0, 0, 1.25)
add_def("Rebirth_S", "환생배수", "Economy", "Small", "RebirthMultiplier", 0.1, 5, 220, 1.8)

# --- Gates and keystones ---------------------------------------------------
add_def("Gate_10", "관문", "Core", "Gate", "None", 0, 1, 200, 1.0, 10, 1.15,
        "최고 10 스테이지에 닿아야 열립니다.")
add_def("Gate_20", "관문", "Core", "Gate", "None", 0, 1, 400, 1.0, 20, 1.15,
        "최고 20 스테이지에 닿아야 열립니다.")
add_def("Gate_35", "관문", "Core", "Gate", "None", 0, 1, 700, 1.0, 35, 1.15,
        "최고 35 스테이지에 닿아야 열립니다.")
add_def("Gate_50", "관문", "Core", "Gate", "None", 0, 1, 1100, 1.0, 50, 1.15,
        "최고 50 스테이지에 닿아야 열립니다.")

add_def("Key_Fortress", "철벽", "Survival", "Keystone", "MaxHealth", 1, 1, 2000, 1.0, 0, 1.5,
        "체력이 하나 더 늘어납니다.")
add_def("Key_Rebirth", "환생", "Economy", "Keystone", "RebirthMultiplier", 0.5, 1, 1800, 1.0, 0, 1.5,
        "환생 보상이 50% 늘어납니다.")
add_def("Key_Saw", "거대톱", "Weapon", "Keystone", "SawSize", 0.5, 1, 1600, 1.0, 0, 1.5,
        "전기톱이 훨씬 커집니다.")
add_def("Key_Drill", "이중드릴", "Weapon", "Keystone", "DrillTopMount", 1, 1, 1900, 1.0, 0, 1.5,
        "공 위쪽에 드릴을 하나 더 답니다.")

DEF_NAMES = {d["Name"] for d in DEFS}

# ---------------------------------------------------------------------------
# Placements
# ---------------------------------------------------------------------------

placements = []          # dicts
edges = []               # (from_id, to_id, route)
by_cell = {}             # (x, y) -> placement id
next_id = [1]


def place(def_name, x, y):
    assert def_name in DEF_NAMES, "unknown definition: " + def_name
    assert (x, y) not in by_cell, "two nodes on cell %s" % ((x, y),)

    pid = next_id[0]
    next_id[0] += 1
    placements.append(dict(PlacementId=pid, DefinitionRowName=def_name,
                           CellX=x, CellY=y))
    by_cell[(x, y)] = pid
    return pid


def link(a, b, route="HorizontalFirst"):
    edges.append((a, b, route))


def chain(def_names, cells, start_from=None):
    """Places a run of nodes and wires them up in order."""
    previous = start_from
    ids = []
    for def_name, cell in zip(def_names, cells):
        pid = place(def_name, cell[0], cell[1])
        if previous is not None:
            link(previous, pid)
        previous = pid
        ids.append(pid)
    return ids


def ring_cells(x0, y0, x1, y1, entry):
    """Perimeter cells of a rectangle, walked from the entry cell round."""
    cells = []
    for x in range(x0, x1 + 1):
        cells.append((x, y0))
    for y in range(y0 + 1, y1 + 1):
        cells.append((x1, y))
    for x in range(x1 - 1, x0 - 1, -1):
        cells.append((x, y1))
    for y in range(y1 - 1, y0, -1):
        cells.append((x0, y))

    start = cells.index(entry)
    return cells[start:] + cells[:start]


def build_ring(x0, y0, x1, y1, entry, def_cycle, corner_defs, stem_end):
    """Rings give the graph its loops: the last node links back to the first."""
    cells = ring_cells(x0, y0, x1, y1, entry)
    corners = {(x0, y0), (x1, y0), (x0, y1), (x1, y1)}

    ids = []
    corner_index = 0
    cycle_index = 0

    for cell in cells:
        if cell in corners:
            def_name = corner_defs[corner_index % len(corner_defs)]
            corner_index += 1
        else:
            def_name = def_cycle[cycle_index % len(def_cycle)]
            cycle_index += 1

        ids.append(place(def_name, cell[0], cell[1]))

    for i in range(len(ids) - 1):
        link(ids[i], ids[i + 1])
    link(ids[-1], ids[0])          # closes the loop
    link(stem_end, ids[0])

    return dict(zip(cells, ids))


core = place("Core", 0, 0)

# --- North: survival -------------------------------------------------------
north_stem = chain(["Resist_T1", "Pickup_T1"], [(0, 1), (0, 2)], start_from=core)
north = build_ring(-2, 3, 2, 6, (0, 3),
                   ["Resist_T2", "Pickup_T2", "Resist_T2", "Pickup_T2", "Resist_T2"],
                   ["Hp_T1", "Hp_T2", "Hp_T2", "Hp_T3"],
                   north_stem[-1])
chain(["Pickup_T2", "Gate_10", "Key_Fortress"], [(0, 7), (0, 8), (0, 9)],
      start_from=north[(0, 6)])

# --- South: mobility -------------------------------------------------------
south_stem = chain(["Force_T1", "Speed_T1"], [(0, -1), (0, -2)], start_from=core)
south = build_ring(-2, -6, 2, -3, (0, -3),
                   ["Force_T2", "Speed_T2", "Force_T2", "Speed_T2", "Force_T2"],
                   ["Force_N", "Speed_N", "Force_N", "Speed_N"],
                   south_stem[-1])
chain(["Speed_T2", "Gate_20", "Key_Rebirth"], [(0, -7), (0, -8), (0, -9)],
      start_from=south[(0, -6)])

# --- West: hammer and saw --------------------------------------------------
west_stem = chain(["HammerKnock", "HammerSpin", "HammerDmg"],
                  [(-1, 0), (-2, 0), (-3, 0)], start_from=core)
west = build_ring(-7, -2, -4, 2, (-4, 0),
                  ["HammerKnock", "HammerDmg", "SawDmg", "HammerSpin", "SawSize"],
                  ["HammerUnlock", "HammerCount", "SawUnlock", "HammerCount"],
                  west_stem[-1])
chain(["SawSize", "Gate_35", "Key_Saw"], [(-8, 0), (-9, 0), (-10, 0)],
      start_from=west[(-7, 0)])

# --- East: bulldozer, drill, gold -----------------------------------------
east_stem = chain(["Gold_T1", "DozerPush", "DrillDmg"],
                  [(1, 0), (2, 0), (3, 0)], start_from=core)
east = build_ring(4, -2, 7, 2, (4, 0),
                  ["Gold_T2", "DozerWidth", "DrillDmg", "DozerPush", "DrillPierce"],
                  ["DozerUnlock", "Gold_N", "DrillUnlock", "Gold_N"],
                  east_stem[-1])
chain(["DrillPierce", "Gate_50", "Key_Drill"], [(8, 0), (9, 0), (10, 0)],
      start_from=east[(7, 0)])

# --- Bridges: the only edges that actually turn a corner -------------------
link(north[(-2, 3)], west[(-4, 2)], "VerticalFirst")
link(west[(-4, -2)], south[(-2, -3)], "HorizontalFirst")
link(south[(2, -3)], east[(4, -2)], "VerticalFirst")
link(east[(4, 2)], north[(2, 3)], "HorizontalFirst")

# --- Rebirth smalls hanging off the economy ring ---------------------------
chain(["Rebirth_S", "Rebirth_S"], [(6, 3), (6, 4)], start_from=east[(6, 2)])

# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------


def csv_cell(value):
    text = str(value)
    if any(ch in text for ch in [',', '"', '\n']):
        return '"' + text.replace('"', '""') + '"'
    return text


def write_csv(path, columns, rows):
    lines = [",".join(columns)]
    for row in rows:
        lines.append(",".join(csv_cell(row[c]) for c in columns))
    with open(path, "w", encoding="utf-8-sig", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")
    print("%-28s %d rows" % (os.path.basename(path), len(rows)))


def_columns = ["Name", "DisplayName", "Description", "Branch", "NodeKind",
               "ScaleX", "ScaleY", "GrantStat", "AmountPerLevel", "MaxLevel",
               "BaseCost", "CostGrowth", "RequiredBestStage"]

placement_rows = []
for p in placements:
    placement_rows.append(dict(Name="P_%03d" % p["PlacementId"], **p))

edge_rows = []
for i, (a, b, route) in enumerate(edges, start=1):
    edge_rows.append(dict(Name="E_%03d" % i, FromPlacementId=a,
                          ToPlacementId=b, RouteType=route))

if not os.path.isdir(OUT):
    print("missing output directory: " + OUT)
    sys.exit(1)

write_csv(os.path.join(OUT, "DT_SkillDef.csv"), def_columns, DEFS)
write_csv(os.path.join(OUT, "DT_SkillPlacement.csv"),
          ["Name", "PlacementId", "DefinitionRowName", "CellX", "CellY"],
          placement_rows)
write_csv(os.path.join(OUT, "DT_SkillEdge.csv"),
          ["Name", "FromPlacementId", "ToPlacementId", "RouteType"], edge_rows)

# ---------------------------------------------------------------------------
# Sanity checks - the same ones the C++ validator runs
# ---------------------------------------------------------------------------

ids = [p["PlacementId"] for p in placements]
assert len(ids) == len(set(ids)), "duplicate placement id"

seen_pairs = set()
for a, b, _ in edges:
    assert a != b, "self edge"
    key = (min(a, b), max(a, b))
    assert key not in seen_pairs, "duplicate edge %s" % (key,)
    seen_pairs.add(key)

by_id = {p["PlacementId"]: p for p in placements}
adjacency = {i: [] for i in ids}
for a, b, _ in edges:
    adjacency[a].append(b)
    adjacency[b].append(a)

# Everything has to be reachable from the core, or it can never be bought.
queue = [core]
seen = {core}
for head in range(10 ** 9):
    if head >= len(queue):
        break
    for nxt in adjacency[queue[head]]:
        if nxt not in seen:
            seen.add(nxt)
            queue.append(nxt)

assert len(seen) == len(ids), "unreachable nodes: %s" % (set(ids) - seen)

cost_by_def = {d["Name"]: (d["BaseCost"], d["MaxLevel"], d["CostGrowth"]) for d in DEFS}
total = 0
for p in placements:
    base, max_level, growth = cost_by_def[p["DefinitionRowName"]]
    for level in range(max_level):
        total += round(base * (growth ** level) / 5) * 5

print("")
print("노드 %d, 간선 %d, 정의 %d" % (len(placements), len(edges), len(DEFS)))
print("전부 만렙까지 찍는 데 드는 골드: %s" % format(int(total), ","))
