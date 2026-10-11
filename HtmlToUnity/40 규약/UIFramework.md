---
분류: 규약
성격: 방향
tags:
  - htmltounity
---

# UIFramework

Window · Panel · Component 세 계층으로 화면을 만든다.

## 노트 자리

### 요약

- 방향 노트다. 기본값과 이유를 준다. 판단 대상이 아닌 것은 [원칙](원칙.md) 에만 있다.
- 상위는 [PD](PD.md) 다. 사용자는 [Transfer_Artist](Transfer_Artist.md) 와 [Transfer_Programmer](Transfer_Programmer.md) 다.
- 기본 구조는 Management 가 Window 를 등록해 쓰는 것이다. 창은 키로 식별한다. 창 아래 낱개 UI 는 풀링으로 만든다.
- 프리팹 배치·캔버스 설정은 [PrefabRule](PrefabRule.md) 이 담당한다.
- 창 등록은 [UIFramework - Window](UIFramework%20-%20Window.md), 낱개 컴포넌트는 [UIFramework - Component](UIFramework%20-%20Component.md) 에 있다.

## 폴더

### 요약

- UI 공용 코드는 `Assets/Scripts/UI/` 에 둔다. 게임 폴더 밖이다. 없으면 만든다.
- 기본 구성이다. 이름보다 역할이 맞으면 된다.
- `Scroll/` 과 `Graph/` 는 최소 세트가 아니다.

### 규칙

- #강제 [원칙 R15](원칙.md#R15) `CLAUDE.md` 에 폴더 규칙이 있으면 그쪽이 우선한다.
- `Scroll/` 과 `Graph/` 는 그 화면이 실제로 나올 때 만드는 것이 기본이다 ([GameFramework](GameFramework.md) 「최소 세트」).

### 설계

```
Assets/Scripts/UI/               (없으면 만든다 · 공용 — 게임 폴더 밖)
├─ BaseComponent.cs              Transform/RectTransform 캐시
├─ Window/
│   ├─ BaseWindow.cs   IBaseWindow.cs   WindowType.cs   WindowStateType.cs
│   ├─ WindowKey.cs                     창 식별자 (경로)
│   ├─ WindowManagement.cs              싱글턴 — UI 루트·카메라·전체 스택
│   ├─ WindowRegistry.cs / WindowController.cs / WindowFactory.cs
│   ├─ BaseManagement.cs                콘텐츠별 Management 베이스
│   └─ Singleton/                       MonoSingleton 류
├─ Prefab/
│   ├─ PrefabAuto.cs  PrefabLoader.cs  PrefabPoolCore.cs  IPoolable.cs
├─ Scroll/                       셀 재활용 (RecyclableVerticalScroll · RecyclableViewer …)
├─ Fx/                           UI 움직임 최소 세트 — 배율 몫을 곱하는 스택 + 펄스·호버·상태 (「UI 연출」)
└─ Graph/                        대량 노드 그래프 (NodeGraphView — 노드 수천 개를 메시로)
```

## 로드 방식

### 요약

- 확정표 10-c 가 가른다.
- UI 프리팹은 Resources, 그 밖의 아트와 데이터 JSON 은 Addressables 가 기본값이다.
- 두 경로가 섞이는 것은 의도된 것이다. 어느 쪽인지 코드에서 보이게 둔다.

### 규칙

- `WindowKey("UI/Popup/Xxx")` 는 Resources 경로다. 어드레서블 키는 `~Address`/`~Key` 로 이름 붙인다. 이유: 이름만 보고 두 경로가 갈린다.
- 확정표 10-c 를 다른 값으로 확정했으면 그 값을 따른다. 아래 표는 확정이 없을 때의 출발점이다.
- UI 프리팹이 많거나 무거워 로드/해제 단위가 필요하면(이유 열의 조건이 뒤집히면) Addressables 쪽이 나을 수 있다. 착수 확정 때 근거와 함께 10-c 로 고른다.

### 설계

| 무엇 | 기본값 | 이유 |
|---|---|---|
| UI 프리팹 (`WindowKey` · `PrefabAuto` 의 경로) | Resources | 수가 적고 대개 항상 필요하다. 경로 = 식별자가 성립한다 |
| 그 밖의 아트 (스프라이트 · 배경 · 이펙트 · 사운드) | Addressables | 용량이 크고 로드/해제 단위가 있어야 빌드가 안 부푼다 |
| 데이터 JSON | Addressables 라벨 | `DataManager` 가 라벨 하나로 전부 읽는다 |

## 3계층

### 요약

- 계층은 Window / Panel / Component 셋이다.
- 기본은 Window 최상위 자식을 `XxxPanel` 단위로 자르고, 낱개 위젯은 패널 안에 두는 것이다.
- 이유: 원본 구획과 패널이 짝지어져 대조가 쉽고, 창 루트가 구획 목록으로 읽힌다.

### 규칙

- Window 스크립트는 패널을 `[SerializeField]` 로 물고 프로퍼티로 노출만 하는 것이 기본이다. 이유: 로직은 Management 가 들고 창은 표기만 한다.

### 설계

| 계층 | 베이스 | 무엇 |
|---|---|---|
| Window / Popup | `BaseWindow` | 화면 한 장. Window 는 전체를 덮고, Popup 은 80% 이하로 뜬다 |
| Panel | `BasePanel : BaseComponent` | Window 안의 구획. 원본 flex 컨테이너 하나 = 패널 하나 |
| Component | `BaseComponent` | 재사용 최소 단위 (아이템 칸·스탯 줄·게이지) |

## Window

### 요약

- 창마다 `WindowKey` 를 static 으로 선언한다. 경로가 곧 식별자다.
- Management 가 `AddWindows()` 에서 등록한다.
- 창 종류는 밴드가 먼저, 같은 밴드 안은 여는 순서다.
- 원본 `z-index` 는 값이 아니라 밴드 판정 근거로 쓴다.
- 자세한 것은 [UIFramework - Window](UIFramework%20-%20Window.md) 에 있다.

## `BaseWindow` 수명

### 요약

- 수명은 Open 과 Close 두 흐름이다.
- 콜백보다 먼저 켠다.

### 규칙

- 콜백보다 먼저 켠다. 이유: 창은 비활성으로 생성되어, 늦게 켜면 `onOpenBefore` 의 `VideoPlayer.Prepare()` · `StartCoroutine` 이 조용히 실패한다.
- `CloseType.Handle` 이면 `HandleCanClose()` 가 false 인 동안 닫히지 않는다 (확인창 등).
- `WindowType.HUD` 는 `Close()` 로 닫히지 않는다.
- 매 프레임 갱신은 `IWindowUpdate` 로 받는 것이 기본이다. 이유: 창마다 `Update` 를 두면 호출 순서가 Unity 에 넘어간다 (GameFramework 「Update 를 Manager 마다 갖지 않는다」와 같은 이유).
- 전투가 멈춘 동안에도 도는 연출은 `unscaledDeltaTime` 을 쓴다.

### 설계

```
Open()  → SetEnable(true) → onOpenBefore → OnOpening() → Opened → onOpenAfter
Close() → OnClosing() → SetEnable(false) → Closed
```

## Component

### 요약

- 기본은 동적 생성 + 풀링이다.
- 이유: 행 수가 데이터로 갈리고 생성·반환이 되풀이된다.
- 칸 수가 고정이고 스크롤하지 않는 판이면 「고정 격자」가 낫다.
- `PrefabAuto` 선언 · 「안 그림」과 「안 끔」 · 설계 순서는 [UIFramework - Component](UIFramework%20-%20Component.md) 에 있다.

## 고정 격자

### 요약

- 행·열이 고정이고 스크롤하지 않는 판(보드·격자)은 목록이 아니다.
- 스크롤도 재활용도 아니다. 갈래를 먼저 가른다.

### 설계

| 갈래 | 언제 | 무엇으로 |
|---|---|---|
| 고정 격자 | 칸 수 고정 · 스크롤 없음 · 전부 화면 안 | `GridLayoutGroup` + 시작 시 전 칸 생성. 풀링 불필요 |
| 재활용 목록 | 행 수가 데이터로 갈리고 스크롤한다 | 「스크롤」 |
| 대량 그래프 | 수천 개 · 한 축 정렬 불가 | `Graph/` |

| 기본 | 이유 |
|---|---|
| 인덱스가 곧 좌표다 (`row = i / width` · `col = i % width`) | 원본이 1차원 배열이면 우리도 1차원으로 든다. 2차원으로 바꾸면 인덱스 산술(`i+1` · `i+width` · `i % width` 경계)이 어긋난다 |
| 칸이 상태를 들지 않는다 | 보드 데이터가 진실이고 칸은 표기만 한다 |
| 칸마다 재생 컴포넌트를 두지 않는다 | 칸 수만큼 비용이 붙는다 ([SKILL - 잘못 옮긴 것](SKILL%20-%20잘못%20옮긴%20것.md) 「재생 계층」) |
| 크기·간격은 프리팹(`GridLayoutGroup`)이 든다 | 코드가 좌표를 계산하면 화면이 프리팹과 코드 두 곳에 생긴다 |

## 입력

### 요약

- `Button` 만으로는 HTML5 게임의 절반을 못 옮긴다.
- 기본은 원본이 쓰는 입력을 전수로 세고 대응을 정하는 것이다.
- 이유: 센 입력이 대응표의 분모가 되고, 안 센 입력은 빠진 줄 모른다.

### 규칙

- #강제 [원칙 R1](원칙.md#R1) 원본의 실행 순서 · 판정 좌표계 · 입력 잠금과 해제 시점은 원본대로다.
- 원본의 실행 순서를 그대로 옮긴다. 이유: 원본이 `drop` 에서 먼저 바꾸고 `dragend` 에서 되돌리면 우리도 그 순서다. 「검사 후 실행」으로 뒤집으면 경계 케이스가 달라진다.
- 판정은 원본의 좌표계로 한다. 이유: 원본이 인덱스 차이(`±1` · `±width`)로 인접을 판정하면 우리도 인덱스로 한다. 화면 거리로 바꾸면 행 넘김 등 경계 거동이 사라진다.
- 입력 잠금도 옮긴다. 이유: 원본이 종료 시 `draggable=false` 를 걸면 해제 시점까지 옮긴다. 해제를 빠뜨리면 재시작해도 안 눌린다.

### 설계

| 원본 | Unity | 비고 |
|---|---|---|
| `click` · `onclick` | `Button` | |
| HTML5 DnD (`dragstart`·`dragover`·`dragenter`·`dragleave`·`drop`·`dragend`) | `IBeginDragHandler` · `IDragHandler` · `IEndDragHandler` · `IDropHandler` | 6종이 1:1로 안 맞는다. 어느 이벤트가 어느 핸들러가 되는지 표로 적는다 |
| `mousedown` · `mousemove` · `mouseup` | `IPointerDownHandler` · `IPointerMoveHandler` · `IPointerUpHandler` | |
| `touchstart` · `touchmove` · `touchend` | 위와 같음 (통합된다) | |
| `keydown` | Input System | |
| `:hover` | 터치에는 없다 | 모바일 타깃이면 전수로 세고 각각 판정한다 (버림 / 누름으로 대체 / 드래그로 대체). 빈칸은 판정 안 한 칸이다 |

```bash
# 원본 입력 전수 — 위 표의 분모
grep -nE "addEventListener|onclick=|draggable" 원본.js 원본.html
grep -nE ":hover|:active|cursor:" 원본.css
```

## 화면 맞춤

### 요약

- 폭 하나로 맞추면 콘텐츠가 화면 밖으로 나간다.
- 실제 화면 비율은 기기마다 다르다.
- 캔버스 스케일러를 폭 기준으로 두면 세로가 짧은 화면에서 아래쪽이 넘친다.

### 규칙

- 「안 눌린다」는 신고는 입력보다 배치를 먼저 보는 것이 기본 순서다. 이유: 눌리지 않는 1순위 이유는 거기 없는 것이다.

### 설계

| 기본 | 내용 |
|---|---|
| 기준 해상도가 항상 화면 안에 들어오는 방식을 쓴다 | 폭·높이 중 작은 배율을 택하는 `Expand`. 여백은 생기지만 잘리지 않는다 |
| 여백은 배경이 메운다 | 배경은 안전 영역 밖까지 꽉 채우는 자리에 둔다 (「안전 영역」) |
| 배선 검사가 이 값을 확인한다 | 누가 되돌려도 다음 검사에서 걸린다 |

사례: 「끌어도 안 움직인다」를 입력 문제로 뒤졌으나 판이 화면 아래로 밀려나 있었다.

## 안전 영역

### 요약

- 브라우저 원본에는 노치·펀치홀·제스처 바가 없다.
- 기본은 플랫폼 요구라 원본에 없어도 넣는 것이다.
- 창 구조는 언제나 BG 와 SafeArea 두 덩어리다.
- 적용할 변은 필요한 변만이다.

### 규칙

- 배경은 `SafeArea` 밖에 둔다. 이유: 안에 넣으면 노치 기기 가장자리에 빈 띠가 생긴다. 가려지면 안 되는 것(글자·버튼)과 꽉 차야 하는 것(배경·덮개)은 다른 자리다.
- 배경은 `SafeArea` 보다 먼저 온다. 형제 순서가 그리는 순서다.
- 배경은 루트 `Image` 대신 `BG` 자식으로 둔다. 이유: 루트에 붙이면 구조에서 BG 가 안 보이고 검사가 셀 대상이 사라진다.
- 배경이 없는 창(배경이 씬에 있음)은 없는 이유를 주석으로 남긴다.
- 기본은 필요한 변만 물리는 것이다. 이유: 네 변을 다 물리면 좌우 안전 영역이 0 이 아닌 기기에서 쓸 폭이 괜히 준다.

### 설계

```
Window
├─ BG          ← 화면을 꽉 채운다. 안전 영역을 적용하지 않는다
└─ SafeArea    ← 노치·제스처 바를 피한다
     └─ 그 외 UI 전부
```

| 화면 | 적용할 변 |
|---|---|
| 세로 게임 | 상·하만 (`Vertical`) |
| 가로 게임 | 좌·우 위주 |
| 전면 UI | 필요한 변만 |

에디터에서는 안전 영역이 화면 전체라 눈으로 확인이 안 된다. 아래를 기계로 센다.

- `SafeArea` 가 루트의 직계 자식이고 컴포넌트가 실제로 붙어 있다
- `BG` 가 `SafeArea` 밖이고 먼저 그려지며 화면을 꽉 채운다
- `SafeArea` 안에 꽉 찬 이미지가 없다 (배경이 잘못 들어간 것)
- 콘텐츠가 `SafeArea` 안에 있다

## 모바일 UX 하한

### 요약

- 원본 치수를 그대로 옮기면 폰에서 못 읽고 못 누른다.
- 데스크톱 기준 원본은 글자와 버튼이 모바일에서 작다.
- 플랫폼 이관에 따르는 조정이지만 말없이 바꾸면 파리티 대조가 무너지므로 등재한다.

### 규칙

- #강제 [원칙 R10](원칙.md#R10) 글자·터치 키움도 확정표에 「의도된 차이」로 등재해야 차이로 인정된다 (PD 「원본의 이상 거동」와 같은 취급).

### 설계

| 기본 | 내용 |
|---|---|
| 게임 판(파리티 대상)은 원본 비율 그대로 | 칸 크기·간격처럼 거동에 걸린 치수라, 키우면 거동이 달라진다 |
| 읽는 것·누르는 것만 키운다 | 글자 크기 · 터치 대상 최소 높이 |
| 하한을 검사로 박는다 | 최소값 미만이 없음을 기계로 센다 |

## 간격 배분

### 요약

- 원본의 「간격」은 값이 아니라 배분 규칙일 수 있다.
- 원본이 `justify-content: space-between` 같은 흐름 배치면 간격은 적어 둔 값이 아니라 남는 공간을 나눈 결과다.
- 균일 간격으로 근사하면 모양이 사라진다.

### 규칙

- 기본 점검은 옮긴 뒤 모양 셋을 세는 것이다. ① 겹치는가 ② 나머지 간격이 서로 같은가 ③ 실제로 벌어져 있는가. 이유: 크기가 의도된 차이라 절대값이 아니라 모양을 센다.

### 설계

| 원본 규칙 | 유니티에서 |
|---|---|
| `space-between` (남는 공간 균등 배분) | 사이사이에 늘어나는 빈 칸(flexible)을 넣는다 |
| 음수 마진 (앞 요소와 겹침) | 세로 레이아웃 간격을 음수로 준다. 겹치는 둘을 한 덩어리로 묶는다 |
| 크기 0인 요소가 자리를 차지 | 끄지 않는다. 배분에 참여해야 원본과 같다 |

사례: 균일값으로 근사했던 간격이 실측하니 균등 배분(각 14px)과 한 요소의 음수 마진(−10, 앞 요소와 6px 겹침) 두 규칙이었다.

## UI 연출

### 요약

- 식은 enum, 값은 프리팹, 몫은 곱한다.
- 캐주얼 UI 는 펄스(항상 숨쉬는 버튼) · 호버(포인터 올림) · 상태(고름/평소)로 움직인다.
- 창마다 코드로 짜면 같은 식이 창 수만큼 생기고 값이 `const` 로 박힌다 ([SKILL - 잘못 옮긴 것](SKILL%20-%20잘못%20옮긴%20것.md) 「코드에 남은 상수」).

### 규칙

1. 기본은 이징 프리셋(`OutBounce` 등) 대신 원본 식을 enum 으로 드는 것이다. 이유: 프리셋 근사는 원본과 다른 움직임이다. 새 식이 나오면 enum 을 추가한다. 시간 단위는 ms 다 (소스 상수 `0.005 rad/ms` 를 환산 없이 넣는다).
2. 값은 프리팹 빌더가 소스·실측값으로 넣고, 창 코드는 `Restart()` · `SetSelected()` 만 부르는 것이 기본이다. 시트에서 받을 일이 생기면 `Configure(...)` 한 줄이다. 그 전에 시트 컬럼을 파면 안 읽는 컬럼이 된다.
3. 정지 프리뷰용 앉히기(`SetPhase01`)를 같이 둔다. 골과 마루에 앉혀야 캡처가 결정적이다 ([Fx](Fx.md) 「페이즈 진입 훅」).
4. 호버 틴트를 쓰는 버튼은 유니티 `Button` 의 색 전환(Transition)을 끄는 것이 기본이다. 이유: 둘이 서로 덮는다.

### 설계

| 조각 | 역할 | 프리팹이 드는 값 |
|---|---|---|
| 배율 스택 | 같은 오브젝트의 몫을 전부 곱해 `localScale` 에 한 번 넣는다 (원본도 `hover × pulse` 곱) | 기준 배율 |
| 펄스 | 항상 도는 배율. 식은 enum. `1+0.5·(sin+1)·A` · `1+A·sin` · 커브 | 식 · 진폭 · 각속도(rad/ms) · 위상 |
| 호버 | 포인터 진입/이탈에 배율·틴트 | 배율 · 틴트 |
| 상태 | 고름/평소에 배율·알파 | 상태별 배율·알파 |

사례: 펄스 식·상수가 창 코드 `const` 로 세 벌 반복되어 위 조각으로 승격했다 ([GameFramework](GameFramework.md) 「공용 승격 기준」).

## 스크롤

### 요약

- 행이 많은 목록은 `Scroll/` 의 재활용 뷰가 기본이다.
- 원본이 DOM 을 다 그려도 기본은 전 행을 한 번에 만들지 않고 재활용하는 것이다.
- 이유: 전 행 생성 비용이 창을 여는 순간에 몰린다.
- 칸 수가 고정이고 스크롤이 없으면 「고정 격자」가 낫다.

### 설계

- 순서 있는 목록: `RecyclableVerticalScroll`/`RecyclableHorizontalScroll`/`RecyclableGrid`
- 정렬 없는 자유 배치: `RecyclableViewer` (`IRecyclableScrollDataSource` 구현)

## 원본 MVVM

### 요약

- 원본의 MVVM 을 그대로 옮기지 않는다.
- 원본 `renderTree()` 는 매번 상태 → 문자열 → DOM 을 다시 뱉는다. 그래서 이관하면 `Model → Builder(VM) → View` 3층이 자연히 생긴다.
- UGUI 에서는 그 층 없이 가는 것이 기본이다. 이유: 프리팹이 View 고, 스크롤·레이아웃 그룹이 배치를 든다.
- 판별법은 「Build」·「VM」·「Render(리스트)」 중 하나가 보이면 원본 프레임워크가 따라 들어온 것이다.

### 규칙

- #강제 [원칙 R2](원칙.md#R2) 원본 프레임워크의 렌더 구조를 1:1 로 옮기지 않는다.
- 뷰가 받을 것은 키(id)다. 표기값 묶음이 아니다.
- 값은 뷰가 `UI/Helper` 로 당긴다 (GameFramework 「호출 방향」).
- 색·크기·간격·프레임은 프리팹과 `TreeNodeArtSet` 같은 SO 가 든다. 이유: 코드가 상태별로 색을 고르면 프리팹 수정을 코드가 덮는다.
- 좌표 그래프(연결선·밴드)는 스크롤 목록이면 버린다.
- 노드 수백~수천 개 그래프 화면(줌아웃 스킬트리 등)은 `Graph/`(`NodeGraphView`. 메시로 굽는 전용 모듈) 자리다.
- 갈림 기준: 한 축 정렬이 되면 Scroll, 안 되고 수천 개면 Graph.

### 설계

| 원본이 하던 일 | 이관 초기에 생겼던 것 | 지금 |
|---|---|---|
| `render*()` 가 노드 배열을 만든다 | `XxxBuilder.Build()` | 없앤다. 로직은 Helper, 표기는 View |
| 노드마다 CSS 클래스를 확정한다 | `XxxVM` 60필드 구조체 | 없앤다. View 가 Helper 로 당긴다 |
| `left/top` 을 계산해 박는다 | `RowToY()` · `_rowPitch` | 없앤다. 스크롤·레이아웃 그룹 |
| `innerHTML` 을 통째로 갈아끼운다 | `View.Render(nodes, edges, bands)` | `View.Show(keys)` |

사례: 스킬 트리가 `TreeBuilder`(788줄) → `TreeNodeVM`(60필드) → `TreeCanvasView.Render()` 로 굳어, 원본 CSS 판정(`opacity:.55` · `#16261d`)이 C# 상수가 되어 프리팹 수정을 코드가 덮어썼다.

## 완료 체크리스트

### 요약

- 기본 구조 기준 점검이다.
- 다른 구조를 골랐으면 확정표의 선택으로 바꿔 본다.

### 규칙

- [ ] 창마다 `WindowKey` 가 static 으로 선언돼 있고 경로가 실제 프리팹과 맞는다
- [ ] UI 연출(펄스·호버·상태)이 Fx 조각 + 프리팹 값으로 있고 창 코드에 연출 상수 `const` 가 없다
- [ ] 모든 창이 어느 Management 의 `AddWindows()` 에 등록돼 있다
- [ ] 창마다 `WindowType` 밴드가 정해져 있고 원본과 위·아래가 어긋나는 창은 밴드로 해결했다
- [ ] 리스트성 UI 가 전부 `PrefabAuto` 동적 생성이다 (인스펙터 하드코딩 0)
- [ ] `Release` 가 생성 지점마다 짝지어져 있고 `OnDespawn` 이 구독을 푼다
- [ ] 하위 UI 가 Manager/Management 를 직접 부르지 않는다 (Helper + event)
- [ ] #강제 [원칙 R1](원칙.md#R1) 플로우 diff(PD 「플로우 diff 를 프리팹 대조보다 먼저」) 통과, 원본에 없는 창이 뜨지 않는다
