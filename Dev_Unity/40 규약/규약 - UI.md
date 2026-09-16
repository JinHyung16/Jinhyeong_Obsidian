---
분류: 규약
성격: 방향
tags:
  - devunity
  - 규약
---

# 규약 - UI

화면을 Window / Component 로 나누고, 동적으로 불러 풀링하는 모양을 정하는 노트다. UI 화면을 설계하거나 창 · 조각 · 목록 · 깊이를 손볼 때 편다.
게임 종류를 모르는 트렁크다. 이 노트는 계층 · 수명 · 계약의 모양을 정하고, 어떤 화면을 어떤 종류로 둘지는 [확정표 6] 이 채운다.

- 합격 조건: 화면이 N개로 늘어도 한 화면을 여는 비용이 커지지 않는다 (게이트 G8, 게이트 정의는 [역할 - PD](역할%20-%20PD.md) 게이트 절)
- 프레임워크 정본: 패키지 `com.jinhyung.gameframework` 의 `Game_UIFramework` ([규약 - 패키지](규약%20-%20패키지.md))

## 기본 구도 — 프리팹은 골격, 내용은 필요할 때 부른다

"무거워 보이는 화면"과 "무거운 프리팹"은 다른 것이다. 탭 6개짜리 화면을 만드는 길은 둘이다.

| 통짜 | 골격 + 동적 (기본) |
|---|---|
| 탭 6개의 내용물을 전부 프리팹에 넣고 껐다 켠다 | 프리팹에는 탭 버튼 6개와 빈 컨테이너만 |
| 프리팹 수 MB. 열 때 전부 로드 · 인스턴스화 | 프리팹 수십 KB. 누른 탭의 패널만 로드 |
| 안 쓰는 5개가 메모리 · 리빌드 비용을 문다 | 안 본 탭은 존재하지 않는다 |
| 화면이 늘수록 로딩이 선형으로 늘어난다 | 화면이 늘어도 여는 비용이 같다 |

- 기본은 골격 + 동적이다. 이유: 통짜는 화면 수에 비례해 여는 비용이 늘어난다.
- "엄청 무거워 보이는 화면인데 프리팹은 KB 단위"가 정상이다. 프리팹이 MB 로 갔다면 아트가 많은 게 아니라 구조가 틀린 것이다([규약 - 프리팹](규약%20-%20프리팹.md) 용량 예산 절).

## 계층 — Window / Component 둘 (`Game_UIFramework`)

프레임워크는 두 계층만 준다. Panel 계층은 없다. 탭 내용은 "창 안의 창"이 아니라 조각 묶음이거나 별도 창이다.

| 계층 | 무엇 | Canvas | 수명 | 로드 |
|---|---|---|---|---|
| `BaseWindow` | 화면 하나. Canvas 를 가진 유일한 계층 | 있음 | 열림~닫힘 | `WindowKey` 경로로 `Resources.Load` (`WindowFactory`) |
| `BaseComponent` | 반복되는 조각 (슬롯 · 행 · 카드 · 버튼 세트) | 없음 | 풀 반납까지 | `PrefabAuto<T>` — 동적 생성 + 풀링이 기본 |

```
[예시] 계층 그림
<이름>Window (Canvas · 상시 노출 요소 · 빈 컨테이너)
└─ <이름>Component × N   ← PrefabAuto 로 풀에서 꺼내 채운다
```

- 기본은 Canvas 를 중첩하지 않는 것이다. 이유: `WindowManagement` 가 중첩을 감지하면 "깊이가 적용되지 않습니다"로 경고한다.
- 탭이 여럿이면 탭마다 창을 두거나, 한 창에서 조각 묶음을 바꿔 끼운다. 어느 쪽인지 확정표 6행에 적는다.
- 목록은 `RecyclableScrollView` — 창이 `IRecyclableScrollDataSource`(`GetItemCount` · `CreateCell`)를 구현한다.

## 키 선언 — 경로는 클래스가 들고 있는다

기본은 경로 문자열을 호출하는 쪽에 흩뿌리지 않는 것이다. 창 경로는 `Resources` 기준이다.

```csharp
[예시] 창
public class <이름>Window : BaseWindow
{
    public static readonly WindowKey<<이름>Window> Key = new (PrefabPath);
    private const string PrefabPath = "UI/<경로>/<이름>Window";   // Resources 아래
}

[예시] 조각
public class <이름>Component : BaseComponent
{
    public static readonly PrefabAuto<<이름>Component> Auto = PrefabAuto.Get<<이름>Component>(PrefabPath);
    private const string PrefabPath = "UI/<경로>/<이름>Component";
}
```

- 여는 쪽은 경로를 모른다 — `Key` / `Auto` 만 쓴다.
- 경로 상수는 한 클래스에 하나. 이유: 같은 경로가 두 곳에 있으면 한쪽만 고쳐져 다른 쪽이 낡는다.
- 씬을 넘어 사는 조각은 `PrefabAuto.GetGlobal<T>`(`GlobalPrefabPool`), 씬 수명이면 `Get<T>`(`ScenePrefabPool`).

### 등록하고 여는 곳은 `BaseManagement` 하나

```csharp
[예시]
public class <게임>UIManagement : BaseManagement
{
    protected override void AddWindows()
    {
        RegisterWindow(<이름>Window.Key, WindowType.Normal);
        RegisterWindow(<이름>Popup.Key,  WindowType.Popup);
    }
}
BaseManagement.Get<<게임>UIManagement>()   // 여는 쪽은 이걸 통해서만
```

`IWindowController` 가 전부다 — `OpenWindow<T>(key, onOpenBefore, onOpenAfter)` · `CloseWindow<T>` · `ForceCloseWindow<T>` · `GetWindow<T>` · `IsWindowOpen<T>`. 등록 안 된 창은 열 수 없다.

## 바인딩 계약 — "연결만 하면 되는" 상태

클라가 로직을 만드는 동안 아트/UI 가 프리팹을 만들려면([역할 - PD](역할%20-%20PD.md) 트랙), 합류 지점이 먼저 선언돼 있어야 한다. 그 선언이 바인딩 계약이다.

```
[예시] 화면 하나의 바인딩 계약 — 트랙을 열기 전에 적는다
화면      : <이름>Window       종류: WindowType.Normal
경로 상수 : <이름>Window.PrefabPath = "UI/<경로>/<이름>Window"
노드 계층 : Window > SafeArea > Content > { Title, List, BtnClose }
컴포넌트  : Window 루트에 <이름>Window (Canvas 는 같은 노드)
필드      : TextTitle(TMP) ← Content/Title
            ListRoot(RectTransform) ← Content/List
            BtnClose(Button) ← Content/BtnClose
행 조각   : <이름>RowComponent · IListener { OnClickRow(int index) }
```

| 계약에 들어가는 것 | 왜 |
|---|---|
| 노드 이름과 계층 | 아트가 나중에 정리하며 바꾸면 바인딩이 전부 끊긴다 |
| 컴포넌트 이름 + SerializeField 필드명 | 클라가 리팩터로 필드명을 바꾸면 프리팹 참조가 끊긴다 |
| 경로 상수의 소유 클래스 | 두 곳에 같은 경로가 생기는 것을 막는다 |
| Listener 시그니처 | UI 가 위로 말하는 유일한 통로. 이게 있어야 로직 없이 골격을 만든다 |

- 기본은 아트/UI 트랙이 스크립트 0으로 골격만 만들고, 컴포넌트는 클라가 마지막에 붙이는 것이다([역할 - 아트](역할%20-%20아트.md)).
- 계약이 정해진 뒤에는 노드 이름 · 필드명 변경이 곧 계약 변경이다. 바꾸는 작업의 범위는 재바인딩까지다.
- 코드 생성 방식이라면 계약이 곧 빌더가 만드는 노드 이름 표다. 방식이 달라도 계약은 같다.

## Window 수명과 훅

```
OpenInternal(onOpenBefore, onOpenAfter)
  └ Opening → OnOpening() → Opened → 활성화 → 관찰자 통지
Close() / ForcedClose()
  └ HandleCanClose() → BeforeClosed() → Closed → OnClose() → 비활성화
```

기본은 아래 정해진 훅만 쓰는 것이다.

| 훅 | 여기서 하는 일 |
|---|---|
| `OnOpening()` | 데이터 읽어 UI 채우기. 채우는 곳은 여기 하나다 |
| `OnClose()` | 리스너 · 구독 해제 · 풀 반납(`Release`) · 참조 null · `RemoveObserver` |
| `BeforeClosed()` | 닫히기 전 확인(연출 대기 · 저장) |
| `HandleCanClose()` | 조건부로 닫힘을 막을 때만. `_closeType = CloseType.Handle` 인 창이 쓴다 |
| `OnOtherWindowOpened()` | 위에 다른 창이 열렸다 (타이머 정지 등) |
| `OnReOpened()` | 위 창이 닫혀 다시 보인다 — 여기서 값을 새로 읽는다 |

- `Awake`/`Start` 에서 데이터를 읽지 않는 것이 기본이다. 이유: 프리팹 로드 시점과 여는 시점이 다르다.
- 프리팹의 `[SerializeField]` 는 다섯 — `_windowType` · `_closeType` · `_constantDepth` · `_hideBackground` · `_canvas`.
- 매 프레임이 필요하면 `IWindowUpdate`(`OnUpdate` · `OnFixedUpdate`). 창마다 `Update()` 를 두지 않는다(아래 중앙 틱 절).
- 창 상태를 밖에서 보려면 `IWindowObserver`(`OnWindowStateChanged`)를 `AddObserver` 로 걸고 `OnClose` 에서 뗀다.

## 깊이 — `WindowType` 다섯 종이 대역을 정한다

프레임워크가 종류별 대역을 들고 있고, 같은 종류 안에서는 여는 순서대로 간격만큼 쌓인다. 창이 자기 숫자를 정하지 않는다.

| `WindowType` | 시작 깊이 | 간격 | 성격 |
|---|---|---|---|
| `HUD` | 10 | 10 | 인게임 상시 표시 |
| `Normal` | 100 | 10 | 대부분의 콘텐츠 창 |
| `Popup` | 200 | 10 | 확인 · 알림 |
| `Modal` | 400 | 10 | 입력을 잠그는 창 |
| `GlobalPopup` | 500 | 10 | 로딩 · 씬 전환 · 치명적 오류 |

- 새 창은 숫자가 아니라 종류를 먼저 고른다. 등록은 `RegisterWindow(key, WindowType.X)`.
- 창이 닫히면 그 종류의 깊이가 다시 배정된다 — 구멍이 남지 않는다.
- "항상 이 숫자여야 하는 창"만 `_constantDepth` + `SetConstantDepth()`. 예외는 사유를 적는다.
- 뒤 화면을 가리는 창은 `_hideBackground` 를 켠다. 이유: 끄지 않으면 안 보이는 화면이 계속 리빌드된다. UI 성능에서 가장 큰 단일 항목이다.
- 확정표 6행에는 쓸 종류와 종류별 화면 목록을 적는다. 대역 숫자는 프레임워크 값을 그대로 쓴다.

### 창이 여럿 겹칠 때의 계약

| 상황 | 방향 |
|---|---|
| 다른 창이 위에 열림 | `OnOtherWindowOpened()` 로 알려 준다 |
| 위 창이 닫혀 다시 보임 | `OnReOpened()` — 여기서 값을 새로 읽는다 |
| 뒤로 가기 | 깊이 역순으로 하나만 닫는다. `CloseType.Handle` 창은 `HandleCanClose()` 가 막을 수 있다 |

## Component — 동적 생성 + 풀링이 기본

```csharp
[예시]
<이름>Component c = <이름>Component.Auto.CreateForUI(container);   // UI 는 CreateForUI
c.Set(data);
…
<이름>Component.Auto.Release(c);
<이름>Component.Auto.Preload(20);     // 목록이 클 때 미리
```

- 프리팹에 같은 이름 형제를 N개 박지 않고 루트 하나만 둔다. 나머지는 풀이 만든다.
- `Clear()` 로 값 · 리스너를 전부 지운다. 풀에서 다시 나올 때 옛 값이 보이면 이게 빠진 것이다.
- 스폰 · 반납 시점에 할 일이 있으면 `IPoolable`(`OnSpawn` · `OnDespawn`).
- 위로는 자기 인터페이스로만 말한다. 부모 창을 직접 참조하면 그 조각을 다른 화면에서 못 쓴다.

## 텍스트 크기 — 기준 해상도 px 로 단(段)을 정한다

```
[예시] 1280×720 기준
제목 60 · 소제목 28 · 본문 22 · 캡션 16 · 버튼 28   (단 다섯, 그 밖의 값은 두지 않는다)
```

- 값은 `CommonConfig.UI` 한 곳([양식 - CommonConfig](양식%20-%20CommonConfig.md)). 화면마다 `fontSize` 를 손으로 적지 않는다.
- 기준 해상도를 바꾸면 이 표를 같이 바꾼다([함정 62](함정%20-%20UI%20표시.md)).
- 자동 크기(`AutoSize`)는 목록 셀에만. 이유: 제목 · 본문에 걸면 화면마다 다른 크기가 된다.
- 터치 타깃은 글자 크기가 아니라 히트 영역이다 — 최소 크기는 [규약 - 플랫폼](규약%20-%20플랫폼.md) 입력 절.

## UI 는 표기만 한다

- 이유: UI 가 게임 규칙을 계산하면, 같은 규칙이 하네스 · 서버 · 다른 화면에서 다르게 나온다.
- UI 코드에 있어도 되는 것: 값 포맷팅 · 색/아이콘 매핑 · 표시 순서 · 입력을 액션으로 바꾸기
- UI 코드 밖에 두는 것: 데미지 계산 · 확률 추첨 · 해금 판정 · 재화 차감
- "이 버튼을 누를 수 있나"의 판정은 시스템이, 표시는 UI 가 한다.

## 중앙 틱 — 열린 창만 도는 갱신

기본은 창마다 `Update()` 를 두지 않고 옵트인 인터페이스로 받는 것이다.

```
[예시] 옵트인 인터페이스
IWindowUpdate        : 매 프레임
IWindowUpdatePerSec  : 초당 1회 (남은 시간 표시 등)
IWindowLateUpdate    : 후처리 (월드 추종 등)
```

Management 가 열린 창만 돌며 부른다. 닫힌 창은 애초에 목록에 없다.

- 초당 1회로 충분한 것은 매 프레임에 두지 않는다. 타이머 텍스트가 대표 사례다.
- 텍스트는 값이 바뀔 때만 쓴다. 이유: 매 프레임 갱신하면 값이 안 바뀌어도 캔버스가 리빌드된다.

## 구독 — 건 곳에서 푼다

- 시스템 이벤트 구독은 `OnOpening()`, 해제는 `OnClose()`. 짝이 안 맞으면 닫힌 창이 계속 반응한다.
- 풀에서 재사용되는 UI 는 빼고-다시-걸기(`-=` 후 `+=`).
- 정적 이벤트는 특히 조심한다. 이유: 창이 죽어도 델리게이트가 창을 붙잡아 누수가 된다.
- 점검법: `+=` 를 grep 해서 같은 클래스에 `-=` 가 있는지 센다. 없으면 그 자리가 누수다.

## 목록 — 재활용 스크롤이 기본

`RecyclableScrollView` 를 쓴다. 창이 `IRecyclableScrollDataSource` 를 구현하고 `GetItemCount()` · `CreateCell(cell, index)` 만 채운다 — 칸은 보이는 만큼만 만들어 돌려 쓴다.

- 칸 클래스는 `BaseComponent` + `IRecyclableItem`(`RectTransform`).
- 높이가 칸마다 다르면 `IRecyclableVariableSize`.
- 항목이 열 개 미만이고 고정이면 조각을 나열하는 편이 낫다. 그 경계를 확정표 6행에 적는다.

## 확정표 6행의 두 분기

### 로드 방식 — 프레임워크가 정해 놓았다

| 대상 | 로드 |
|---|---|
| 창 프리팹 | `Resources.Load` — `WindowKey.Path` 가 `Resources` 아래 경로 (`WindowFactory`) |
| 조각 프리팹 | `PrefabAuto` / `PrefabLoader` 의 풀 |
| 데이터 JSON | Addressables — 라벨 `game_data` (`DataManager`) |

- `Resources` 에는 창 프리팹만 둔다. 이유: `Resources` 는 참조가 없어도 빌드에 통째로 들어가서 "나중에 쓸지도"가 전부 빌드 용량이 된다.
- 데이터 쪽 주소는 양방향으로 감사하고, 미등록은 에러로 낸다. 이유: 조용한 폴백은 한참 뒤에야 발견된다.

### 생성 방식 — 프리팹 편집 / 코드 생성 / 하이브리드

| | 프리팹 편집 | 코드 생성(빌더) | 하이브리드 |
|---|---|---|---|
| 맞는 때 | 사람이 에디터로 다듬는다 | 사람 손 없이 자동화로 굽는다 | 대부분 |
| 장점 | 미세 조정 · 미리보기 | diff · 재현 · 일괄 변경 | 골격은 코드, 룩은 프리팹 |
| 대가 | 대량 변경이 어렵다 | 룩을 코드로 감 잡기 어렵다 | 경계를 명확히 해야 |
| 검증 | 육안(스크린샷) 필수 | 육안 필수 (코드가 맞다는 건 룩이 맞다는 뜻이 아니다) | 동일 |

어느 쪽이든 육안 검증은 빠지지 않는다. 배치모드로 컴파일만 돌리고 UI 가 됐다고 보고하면 그건 미측정이다([역할 - PD](역할%20-%20PD.md) 미측정은 통과가 아니다 절).

## 완료 체크리스트

- [ ] 화면마다 `WindowType` 이 골라졌다. 손으로 정한 `sortingOrder` 0건 (`_constantDepth` 예외는 사유 기록)
- [ ] 전체 크기 창이 열릴 때 뒤 화면 Canvas 가 꺼진다
- [ ] 경로 상수가 클래스당 하나, 호출부에 경로 문자열 0건
- [ ] 탭/패널이 처음 열 때 로드된다 (열지 않은 탭의 인스턴스 0)
- [ ] 반복 요소가 전부 풀에서 나오고 반납된다 (`Instantiate` 직접 호출 0건)
- [ ] `+=` 와 `-=` 의 짝이 맞는다
- [ ] 창마다 `Update()` 가 없다 (중앙 틱 옵트인)
- [ ] 목록 방식을 골랐고 상한 없는 목록이 재활용 스크롤이다
- [ ] SafeArea 노드 밖에 인터랙티브 요소 0건 ([규약 - 플랫폼](규약%20-%20플랫폼.md))
- [ ] 실제 플레이 스크린샷으로 한글 · 레이아웃 · 잘림을 확인했다
- [ ] 화면 프리팹 용량이 예산 안이다 ([규약 - 프리팹](규약%20-%20프리팹.md))

## 자주 보는 증상

| 증상 | 원인 |
|---|---|
| 화면이 늘수록 로딩이 길어짐 | 통짜 프리팹 · 안 쓰는 패널까지 로드 |
| 숫자 하나 바뀌는데 프레임이 떨어짐 | 캔버스 통째 리빌드 · 매 프레임 텍스트 갱신 |
| 안 보이는 화면이 프레임을 먹음 | 뒤 화면 Canvas 를 안 끔 |
| 다시 연 창이 옛 값을 보여줌 | `OnClose` 에서 참조를 안 끊음 · `OnReOpened` 미구현 |
| 창을 닫았는데 계속 반응함 | 구독 해제 누락 |
| 두 창이 서로를 가림 | `WindowType` 없이 손으로 정한 depth 충돌 |
| 목록을 갱신할수록 느려짐 | 반납 없이 계속 생성 |
| 팝업 뒤의 버튼이 눌림 | 입력 차단막 없음 |
| 에셋을 옮겼더니 null | 하드코딩 경로 |
| 컴포넌트를 다른 화면에서 못 씀 | 부모 타입 직접 참조 (Listener 인터페이스 미사용) |
