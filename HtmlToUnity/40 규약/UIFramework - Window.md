---
분류: 규약
성격: 방향
tags:
  - htmltounity
---

# UIFramework - Window

상위: [UIFramework](UIFramework.md)

창을 키로 선언하고 Management 에 등록해 쓴다.

## WindowKey

### 요약

- 창마다 `WindowKey` 를 static 으로 선언한다.
- `WindowKey` 는 경로가 곧 식별자다.
- 창은 한 번 생성 후 캐시된다.

### 규칙

- 위로 올리는 것은 `event` 로만 올린다.

### 설계

```csharp
public class ModeSelectPopup : BaseWindow
{
    public static readonly WindowKey<ModeSelectPopup> Key =
        new WindowKey<ModeSelectPopup>("UI/Popup/ModeSelectPopup");   // Resources 경로

    public event Action<string> OnModeSelected;      // 위로 올리는 것은 event 로만
}
```

## Management 등록

### 요약

- Management 가 `AddWindows()` 에서 등록한다.
- 이벤트 구독은 `OnInitialize`, 해제는 `OnDispose` 에서 한다.
- `OpenWindow` 는 없다.

### 규칙

- `GetWindow(key)` 로 받아 창 자신의 `Open(...)` 을 부른다 (`window.Open(this);`).
- 다른 Management 는 `BaseManagement.Get<T>()` 로 찾는 것이 기본이다. 이유: 직접 참조를 들면 생성 순서에 묶인다.

### 설계

```csharp
public class ShopManagement : BaseManagement
{
    protected override void AddWindows()
    {
        RegisterWindow(ShopPopup.Key,        WindowType.Popup);
        RegisterWindow(LuckyDrawPopup.Key,   WindowType.Popup);
        RegisterWindow(OddsPopup.Key,        WindowType.Popup);
    }

    protected override void OnInitialize()   // 이벤트 구독은 여기서
    {
        var popup = GetWindow(ShopPopup.Key);
        popup.OnProductClicked += HandleProductClicked;
    }

    protected override void OnDispose()      // 구독 해제는 여기서
    {
        …
    }
}
```

`BaseManagement` 헬퍼는 `RegisterWindow` / `CloseWindow` / `ForceCloseWindow` / `GetWindow` / `IsWindowOpen` / `IsAnyPopupOpen` 이다.

## 창 밴드

### 요약

- 창 종류는 대역이 먼저, 층이 그다음이다.
- 같은 밴드 안에서는 나중에 열린 것이 위다. 프레임워크가 열린 순서대로 depth 를 올린다.
- 원본 `z-index` 는 값이 아니라 밴드 판정 근거로 쓴다.
- enum 이름 표기는 프로젝트 컨벤션을 따른다 (`E` 접두사 등).

### 규칙

- #강제 [원칙 R1](원칙.md#R1) 창의 위·아래 관계는 원본과 같다. 밴드는 그것을 맞추는 수단이다.
- 기본은 밴드 안 순위 상수(`WindowLayer`/`LayerPriority` 류) 없이, 「무조건 맨 위」가 필요하면 밴드를 올리는 것이다. 이유: 순위 상수는 절대 depth 처럼 보이지만 실제로는 밴드 안 상대 순위라 오독된다 (걷어낸 전력이 있다).
- 기본은 z-index 수치를 상수로 옮기는 대신, 원본에서 A 가 B 위에 떴다는 사실만 가져와 `WindowType` 밴드를 고르는 것이다. 이유: 수치 상수는 순위 상수와 같은 오독을 부른다.

### 설계

기본 구조는 「밴드가 먼저, 같은 밴드 안은 여는 순서」다.

```csharp
public enum EWindowType
{
    Normal = 0,       // 기본 전체 화면
    Popup = 1,        // 기본 UI 위 팝업
    HUD = 2,          // 항상 열려 있는 것
    GlobalPopup = 3,  // 최상단
    Modal = 4,        // Popup 위, GlobalPopup 아래 (확인/차단형)
    Toast = 5,        // 전부의 위 — 짧게 떴다 사라지는 알림
}
```

같은 밴드 안 순서는 여는 순서가 정한다. 원본도 대부분 「나중에 연 모달이 위」다. 어긋나는 창만 밴드를 올린다.
