---
분류: 양식
성격: 방향
tags:
  - devunity
  - 양식
---

# 양식 - UI 프리팹

UI 창 · 팝업 · HUD · 조각 프리팹이 정확히 어떤 노드로 생겼는지 정하는 틀이다(`Game_UIFramework` 기준). UI 프리팹을 세우거나, 게임 쪽 빌더를 짜거나, 프리팹 감사를 돌릴 때 편다.

[규약 - UI](규약%20-%20UI.md) 의 계층과 [규약 - 프리팹](규약%20-%20프리팹.md) 의 조립 단위가 "무엇을 쪼개나"를 정하면, 이 노트는 "쪼갠 것이 정확히 어떤 노드로 생겼나"를 정한다.
노드 이름 · 자식 순서는 빌더 헬퍼와 아래 검사가 이름과 자리로 찾는다. 그래서 모양은 그대로 두는 것이 기본이다. 이름을 바꾸면 검사가 노드를 못 찾아 위반을 못 센다.

- 베이스 클래스는 패키지(`com.jinhyung.gameframework`)가 주는 것을 쓰는 것이 기본이다. 이유: 직접 만든 사본은 원본과 갈린다. [규약 - 패키지](규약%20-%20패키지.md)
- `[확정표 3]` 플랫폼 · 방향이 SafeArea 변을, `[확정표 6]` 이 화면별 `WindowType` 을, `[확정표 7]` 이 용량 예산을 채운다.

## 세 가지 창 + 조각

| 종류 | 상속 | `WindowType` | `_hideBackground` | 뒤 화면 | 로드 |
|---|---|---|---|---|---|
| Window | `BaseWindow` | `Normal` | true (전체를 덮으면) | Canvas 를 끈다 | `Resources.Load` — `WindowKey.Path` |
| Popup | `BaseWindow` | `Popup` · `Modal` · `GlobalPopup` | false | 살아 있다. `Dim` 으로 덮는다 | `Resources.Load` — `WindowKey.Path` |
| HUD | `BaseWindow` | `HUD` | false | 살아 있다 | `Resources.Load` — `WindowKey.Path` |
| Component | `BaseComponent` | — | — | — | `PrefabAuto<T>` + 풀 |

- Canvas 는 창에만 두는 것이 기본이다. 이유: 조각에 Canvas 를 달면 `WindowManagement` 가 "깊이가 적용되지 않습니다"로 경고한다.
- Popup 은 Window 프리팹 안에 넣지 않고 자기 프리팹으로 따로 둔다. 이유: Popup 도 자기 Canvas 를 가진 창이라, 안에 넣으면 창 안에 Canvas 가 중첩돼 깊이가 안 먹는다(아래 함정 표).
- Panel 계층은 없다. 탭 내용은 탭마다 창이거나, 한 창에서 바꿔 끼우는 조각 묶음이다.

## Window 양식

```
<이름>Window                      RectTransform 스트레치 · Canvas · CanvasScaler · GraphicRaycaster · <이름>Window
├─ Background                     Image 스트레치. SafeArea 밖 — 노치 영역이 게임 화면으로 비치면 안 된다
├─ SafeArea                       RectTransform 스트레치 · SafeArea(게임 쪽 스크립트, 아래 참고)
│  ├─ <고정 요소>                 개수가 고정인 것만 (탭 버튼 · 상단바 · 닫기). 앵커 패턴 4종으로
│  └─ Container                   빈 RectTransform. 조각이 풀에서 여기 붙는다
└─ Fullscreen                     (선택) 전면 연출. SafeArea 밖. 없으면 만들지 않는다
```

`[SerializeField]` 바인딩: `_windowType = Normal` · `_closeType` · `_constantDepth`(보통 0) · `_hideBackground` · `_canvas` + 고정 요소.

## Popup 양식

```
<이름>Popup                       RectTransform 스트레치 · Canvas · CanvasScaler · GraphicRaycaster · <이름>Popup
├─ Dim                            Image 스트레치 · 알파 0.6~0.92 · raycastTarget=true — SafeArea 밖
└─ SafeArea                       RectTransform 스트레치 · SafeArea
   └─ Body                        RectTransform 중앙 고정 · 크기 고정. 9슬라이스 패널 스프라이트
      ├─ Title                    TMP
      ├─ Content                  빈 컨테이너
      └─ Buttons                  HorizontalLayoutGroup. 버튼은 조각으로 풀에서
```

- `_windowType = Popup`(입력을 잠가야 하면 `Modal`, 로딩 · 치명적 오류는 `GlobalPopup`) · `_hideBackground = false`
- Body 는 중앙 고정이 기본이다. 이유: 스트레치로 두면 큰 화면에서 팝업이 화면만큼 커진다.
- Dim 이 클릭을 먹게 둔다. 이유: 안 그러면 뒤 창이 눌린다.
- 닫힘을 막아야 하면 `_closeType = CloseType.Handle` + `HandleCanClose()`
- 결과 화면(`CLEAR!` · `GAME OVER`)도 Popup 이다. [함정 53](함정%20-%20하네스%20측정.md)

## HUD 양식

```
<이름>Hud                         Canvas · CanvasScaler · GraphicRaycaster · <이름>Hud
└─ SafeArea                       RectTransform 스트레치 · SafeArea
   ├─ <상시 표시>                 체력·경험치 막대 · 타이머 · 라운드 배너
   └─ <월드 추적 루트>            피해 숫자 · HP바는 조각으로 풀에서
```

`_windowType = HUD`(시작 깊이 10) · `_hideBackground = false`.
기본은 `OnOpening` 에서 구독하고 `OnClose` 에서 전부 떼는 것이다. 이유: 인게임 내내 열려 있어서 구독을 뗄 자리가 닫힘뿐이다.

## Component 양식

```
<이름>Component                   RectTransform · LayoutElement(필요 시) · <이름>Component
└─ <조각>                         Image · TMP · Button. 자식 Component 없음 (두 단계 규칙)
```

- 두 단계 규칙은 [규약 - 프리팹](규약%20-%20프리팹.md) 계층 절이다.
- 기본은 동적 생성 + 풀링이다. 프리팹에는 루트만 두고 같은 이름 형제를 N개 박지 않는다. 이유: 개수가 고정인 것만 창에 고정 요소로 두고 나머지는 풀에서 붙는다. 박아 둔 형제는 아래 검사가 풀 위반으로 센다.
- `Clear()` 가 값 · 리스너를 전부 지운다. 스폰 · 반납 훅이 필요하면 `IPoolable`
- 목록 칸이면 `IRecyclableItem` 도 구현한다 (`RecyclableScrollView`)

## 프레임워크에 없는 것 — 게임 쪽에 둔다

| 없는 것 | 어떻게 |
|---|---|
| SafeArea | 게임 쪽 스크립트 둘. `SafeArea`(붙은 RectTransform 을 맞춘다) + `SafeAreaUtil`(`Screen.safeArea` → 앵커, 변 선택 Flags). 회전 · 해상도 변경 때 값이 바뀌므로 값 비교로 감시한다. 앵커를 바꾼 뒤 offset 0 리셋이 유틸 안에 있다 |
| 프리팹 빌더 | 확정표 7행이 "빌더로 굽기"면 게임 쪽 에디터 스크립트로. 루트 헬퍼를 만들어 화면마다 같은 이름 · 같은 순서로 세운다 (아래) |
| Panel 계층 | 쓰지 않는다. 탭마다 창 또는 조각 묶음 |

```csharp
[예시] 게임 쪽 빌더 — 첫 줄은 항상 루트 헬퍼
RectTransform safe = MakeWindowRoot("LobbyWindow", applySide, out GameObject root, out Canvas canvas, out CanvasScaler scaler);
RectTransform body = MakePopupRoot("ConfirmPopup", applySide, dimAlpha: 0.8f, bodySize: new Vector2(560f, 320f), out root, out canvas, out scaler);
```

헬퍼가 Canvas · Scaler · Raycaster · Background/Dim · SafeArea 를 같은 이름 · 같은 순서로 만든다.
기본은 헬퍼로 세우는 것이다. 이유: 화면마다 손으로 세우면 Popup 하나 추가할 때 골격이 갈린다.
함수 하나 = 화면 하나, `Save(root, PrefabPath)` 로 끝난다. 같은 경로에 덮어써 GUID 를 유지하고, 두 번 돌려도 결과가 같게 둔다.

## 플랫폼별 — 확정표 3행이 정하는 것

| 확정표 3행 | `SafeArea` 적용 변 | CanvasScaler | 비고 |
|---|---|---|---|
| 모바일 세로 | `Vertical`(상 · 하) | 1080×1920 · Match 0 | 좌우까지 물리면 화면이 괜히 좁아진다 |
| 모바일 가로 | `All` | 1920×1080 · Match 1 | 펀치홀이 좌우에 온다 |
| PC 가로 | `All`(노치 없어 무해) 또는 `None` | 1280×720 · Match 0.5 | 에디터 Game 뷰는 `Screen.SetResolution` 을 안 따른다 — 하네스가 뷰 크기를 따로 잡는다 |
| 태블릿 | 세로/가로 위 규칙 | 확정표 값 | 4:3 과 18:9 양 극단에서 찍는다 |

CanvasScaler 값은 `CommonConfig.UI` 한 곳에 둔다([양식 - CommonConfig](양식%20-%20CommonConfig.md)). 이유: 창마다 다르게 두면 해상도를 바꿨을 때 일부 화면만 따라온다.

## 경로

| 대상 | 어디 |
|---|---|
| 창 프리팹 | `Assets/Resources/UI/<경로>/<이름>Window.prefab` — `Resources.Load` 라 Resources 아래여야 한다 |
| 조각 프리팹 | `PrefabAuto` 경로 규칙에 맞춰 |
| 아트 조각(스프라이트) | `_Art/UI/` — 프리팹에 박지 않고 데이터 · 스킨이 키로 지정 |

`Resources` 에는 창 프리팹만 두는 것이 기본이다. 이유: `Resources` 는 참조가 없어도 빌드에 통째로 들어간다. "나중에 쓸지도"를 거기 두면 그만큼 용량이 는다.

## 검사 — 양식 위반을 센다

| 검사 | 실패 조건 |
|---|---|
| 노드 이름 | 창에 `SafeArea` 없음 · Window 에 `Container` 없음 · Popup 에 `Dim` · `Body` 없음 |
| SafeArea 밖 인터랙티브 | `Background` · `Dim` · `Fullscreen` 이외 노드의 Button/Toggle/InputField 가 SafeArea 밖 |
| Canvas 위치 | Component 프리팹에 Canvas 있음 · 창 안에 Canvas 중첩 |
| 풀 위반 | 같은 이름 형제 ≥ 2 (조각을 박아 둔 것) |
| 로드 경로 | 창 프리팹이 `Resources` 밖에 있음 |

## 함정

| 증상 | 원인 |
|---|---|
| 기기에서만 상단 버튼이 노치에 가림 | 고정 요소를 SafeArea 밖(루트 직속)에 만듦 |
| 배경 위아래에 검은 띠 | Background 를 SafeArea 안에 넣음 |
| 팝업이 큰 화면에서 화면만큼 커짐 | Body 를 스트레치로 둠. 중앙 고정 + 크기 고정 |
| 팝업 뒤 창이 눌림 | Dim 에 `raycastTarget` 없음 |
| 팝업 열자 뒤 창이 사라짐 | `_hideBackground` 를 켰다 · 또는 `WindowType.Normal` 로 만듦 |
| 창을 열었는데 안 보임 | 프리팹이 `Resources` 밖 · 또는 `BaseManagement.AddWindows()` 에 등록 안 됨 |
| 깊이가 안 먹음 | 창 안에 Canvas 가 중첩됐다 (콘솔에 경고가 있다) |
| 세로 게임인데 좌우가 좁다 | `SafeArea` 적용 변을 `All` 로 둠. 세로는 `Vertical` |
