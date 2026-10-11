# -*- coding: utf-8 -*-
"""Makes the assets that cannot be made from C++, without opening the editor.

Run it headless:

    UnrealEditor-Cmd.exe RollBall.uproject -run=pythonscript -script="Tools/setup_assets.py"

It creates the two empty maps the game travels between, imports the three
skill tables, and points the GameInstance Blueprint at them. Running it twice
is safe: anything already there is left alone.
"""

import unreal

CONTENT = "/Game"
MENU_MAP = CONTENT + "/L_MainMenu"
STAGE_MAP = CONTENT + "/L_Stage_01"

DATA_DIR = CONTENT + "/Data"
CSV_DIR = unreal.Paths.project_content_dir() + "Data/"

TABLES = [
    ("DT_SkillDef", "DT_SkillDef.csv", "RollBallSkillDefRow"),
    ("DT_SkillPlacement", "DT_SkillPlacement.csv", "RollBallSkillPlacementRow"),
    ("DT_SkillEdge", "DT_SkillEdge.csv", "RollBallSkillEdgeRow"),
]

assets = unreal.EditorAssetLibrary
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)


def make_empty_map(path):
    """An empty level. The arena builds its own floor and lighting, so there
    is nothing to place here by hand."""
    if assets.does_asset_exist(path):
        unreal.log("이미 있음: " + path)
        return False

    levels.new_level(path)
    unreal.log("맵 만듦: " + path)
    return True


def import_table(name, csv_name, row_struct_name):
    target = DATA_DIR + "/" + name
    if assets.does_asset_exist(target):
        unreal.log("이미 있음: " + target)
        return

    row_struct = unreal.load_object(None, "/Script/RollBall." + row_struct_name)
    if row_struct is None:
        unreal.log_error("행 구조체를 못 찾음: " + row_struct_name)
        return

    factory = unreal.CSVImportFactory()
    factory.automated_import_settings.import_row_struct = row_struct

    task = unreal.AssetImportTask()
    task.filename = CSV_DIR + csv_name
    task.destination_path = DATA_DIR
    task.destination_name = name
    task.factory = factory
    task.automated = True
    task.replace_existing = True
    task.save = True

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    unreal.log("표 가져옴: " + target)


def assign_tables_to_game_instance():
    """Puts the three tables on the GameInstance Blueprint so the packaged
    game finds them. The C++ CSV fallback only runs in the editor."""
    blueprint = assets.load_asset("/Game/BP/BP_RollBallGameInstance")
    if blueprint is None:
        unreal.log_warning("BP_RollBallGameInstance 를 못 찾음")
        return

    defaults = unreal.get_default_object(blueprint.generated_class())
    if defaults is None:
        unreal.log_warning("기본 오브젝트를 못 읽음")
        return

    pairs = [
        ("skill_definition_table", "DT_SkillDef"),
        ("skill_placement_table", "DT_SkillPlacement"),
        ("skill_edge_table", "DT_SkillEdge"),
    ]

    for prop, name in pairs:
        table = assets.load_asset(DATA_DIR + "/" + name)
        if table is None:
            continue
        try:
            defaults.set_editor_property(prop, table)
            unreal.log("%s = %s" % (prop, name))
        except Exception as error:
            unreal.log_warning("%s 설정 실패: %s" % (prop, error))

    assets.save_asset("/Game/BP/BP_RollBallGameInstance")


def main():
    for name, csv_name, row_struct in TABLES:
        import_table(name, csv_name, row_struct)

    assign_tables_to_game_instance()

    # Maps last: creating one opens it, which would drop whatever else is
    # half done.
    make_empty_map(STAGE_MAP)
    make_empty_map(MENU_MAP)

    unreal.log("끝")


main()
