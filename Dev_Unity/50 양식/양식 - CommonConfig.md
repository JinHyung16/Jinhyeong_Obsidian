---
분류: 양식
성격: 방향
tags:
  - devunity
  - 양식
---

# 양식 - CommonConfig

확정표의 값이 코드에 내려앉는 자리 `CommonConfig` 의 절 이름과 행 매핑을 정하는 틀이다. 확정표가 굳어 값을 코드에 옮길 때, 전역 상수를 어디 둘지 고를 때 편다.

[규약 - 코드 컨벤션](규약%20-%20코드%20컨벤션.md) 의 "전역 상수 · 기본값은 `CommonConfig` 한 곳"의 양식이다.
확정표 13행이 굳으면 그 값은 코드 어딘가에 박혀야 한다. 어디에 박히는지가 게임마다 다르면 다음 게임이 그 값을 못 찾는다.
그래서 절 이름과 행 매핑을 고정한다. 게임 고유 절은 그 아래에 자유롭게 늘린다.

## 모양

```csharp
[예시]
namespace <접두어>_Common
{
    public static class CommonConfig
    {
        public static class UI      { … }   // 3·6행
        public static class View    { … }   // 2행
        public static class Budget  { … }   // 4행
        public static class Input   { … }   // 8행
        public static class Audio   { … }
        public static class Save    { … }   // 11행
        // ── 여기부터 게임 고유 (Player · Enemy · Skill · Run …) ──
    }
}
```

- 값은 `const` 또는 `static readonly` 가 기본이다. 이유: `[SerializeField]` 로 흩뿌린 인스펙터 값은 씬마다 다른 값이 된다.
- 필수 절 6개는 이름을 그대로 둔다. 이유: 감사가 이름으로 찾는다.
- 절 안의 키는 `PascalCase`, 단위를 이름에 넣는다 (`HitInvulnerabilitySec` · `MaxAlive` · `ReferenceResolution`)

## 필수 절 — 확정표 행 ↔ 키

| 절 | 확정표 | 필수 키 | 어디서 읽나 |
|---|---|---|---|
| `UI` | 3 · 6 | `ReferenceResolution` `MatchWidthOrHeight` · 텍스트 단 `FontTitle` `FontBody` `FontCaption` `FontButton` · `BandInterval` | CanvasScaler 빌더 · [규약 - UI](규약%20-%20UI.md) 텍스트 크기 · `WindowDepth` |
| `View` | 2 | `CameraPitchDeg` `OrthoSize` 또는 `FieldOfView` · `PixelsPerUnit` · `SortingAxis` | 카메라 리그 · `build_meta.py` PPU · 정렬 |
| `Budget` | 4 | `TargetFrameRate` · `MaxAlive` · `PrewarmEnemy` `PrewarmFx` · `MaxDrawCalls`(선택) | 스포너 예열 · 컬링 · [단계 6 - QA](단계%206%20-%20QA.md) G6 |
| `Input` | 8 | `DefaultPreset` · `TouchTargetMinPx`(모바일) · `DeadZone` | `InputSettings` · [규약 - 플랫폼](규약%20-%20플랫폼.md) |
| `Audio` | — | `VolumeSfx` `VolumeBgm` `VolumeUi` · `SfxSourceCount` · `SfxMinIntervalSec` | `SfxManager` · [역할 - 아트](역할%20-%20아트.md) 오디오 |
| `Save` | 11 | `SchemaVersion` · `Key` | `SaveData` 마이그레이션 · [규약 - 데이터](규약%20-%20데이터.md) 세이브 |

- 행이 "추정"이면 값 옆에 `// 추정 #N` 주석을 단다(스펙 추정 절의 행 번호). 이유: 나중에 값을 바꿀 때 그 행이 근거다.
- 필수 절에는 확정표에 있는 값만 둔다. 게임 고유 값은 고유 절로.

## 게임 고유 절 — 자유, 단 규칙 둘

1. 절 하나 = 시스템 하나 (`Player` `Enemy` `Skill` `Spawner` `Run` …). 시스템 폴더 이름과 같게.
2. 데이터로 갈 값은 여기 두지 않는 것이 기본이다. 적 HP · 스킬 계수 · 라운드 곡선은 `_DataExporter/GameData/` 다.
   여기는 시스템의 상수(예열 수 · 자석 반경 · 피격 무적)만. 콘텐츠를 늘릴 때 이 파일이 바뀌면 그 값은 잘못 온 것이다.

## 검사

설정 감사기(`audit_config.py`, `[예시]` 이 프로젝트 큐 항목 C-13)가 센다.

| 검사 | 실패 조건 |
|---|---|
| 필수 절 | `UI` `View` `Budget` `Input` `Audio` `Save` 중 없는 것 |
| 필수 키 | 위 표의 키가 그 절에 없음 |
| 옛 게임 값 | 킷 복사 직후 — 원본 프로젝트의 숫자가 그대로 남아 있음 (초기화 5단계 누락) |
| 흩어진 상수 | `CommonConfig` 밖 `.cs` 에 `const float/int` 가 있고 그 이름이 위 절의 키와 같음 (두 곳에 진실) |

## 함정

| 증상 | 원인 |
|---|---|
| 해상도를 바꿨는데 일부 화면만 따라옴 | 창마다 `CanvasScaler` 값을 따로 둠. `UI.ReferenceResolution` 한 곳 |
| 새 게임인데 옛 게임 스폰 수로 돈다 | 킷 복사 뒤 `Budget` 을 안 채움 — 초기화 5단계 |
| 밸런스 수치를 고쳤는데 안 바뀜 | 데이터에 있어야 할 값이 여기 상수로도 있다. 두 곳 중 한 곳이 이긴다 |
