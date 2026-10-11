import unreal

settings = unreal.GameUserSettings.get_game_user_settings()

settings.set_overall_scalability_level(3)
settings.set_resolution_scale_normalized(1.0)
settings.apply_settings(False)
settings.save_settings()

for command in (
    "r.ScreenPercentage 100",
    "r.MotionBlurQuality 0",
    "r.DefaultFeature.MotionBlur 0",
):
    unreal.SystemLibrary.execute_console_command(None, command)

print("해상도 배율", settings.get_resolution_scale_normalized())
print("전체 품질", settings.get_overall_scalability_level())
