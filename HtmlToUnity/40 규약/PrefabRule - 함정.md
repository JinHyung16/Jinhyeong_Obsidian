---
분류: 규약
성격: 방향
tags:
  - htmltounity
---

# PrefabRule - 함정

상위: [PrefabRule](PrefabRule.md)

프리팹 배치에서 실제로 걸렸던 것들이다.

## 레이아웃

### 요약

- 레이아웃 그룹의 기본값이 원본과 다른 배치를 만든다.
- 빌드 시점의 rect 크기는 아직 레이아웃 전 값이다.

### 설계

| 함정 | 실제 |
|---|---|
| 빌드 시점 `rect.width` 로 비율 계산 | 레이아웃 전이라 기본값 100 이 잡힌다. 절대 폭을 `preferredWidth` 로 주고 `childForceExpandWidth=false` |
| `VerticalLayoutGroup` 의 `childControlHeight` | 코드로 붙이면 false 로 남아 자식이 기본 100 으로 앉는다. 쓰는 자리에서 명시 |
| `HorizontalLayoutGroup` 의 `childForceExpandWidth` | 기본 true. `preferredWidth` 가 무시되고 합이 부모 폭을 넘으면 0폭까지 눌린다 |
| `childControlHeight=true` 아래 버튼 | `preferredHeight` 가 -1 이면 0 높이로 수축해 클릭 영역이 사라진다 |
| 레이아웃 그룹의 자식에 `ContentSizeFitter` | 부모와 높이를 두고 싸운다. 스크롤 Content(그룹 밖)에만 |
| 그룹 안의 테두리·코너 장식 | `LayoutElement.ignoreLayout` 을 준다. 없으면 한 행으로 취급된다 |
| 그룹 아래 작은 아이콘에 `LayoutElement` 누락 | 점 하나가 행 폭으로 늘어나 타원이 된다 |

## 렌더링

### 요약

- 한 GameObject 에 Graphic 은 하나다.
- 9-slice · Tiled · 중첩 Canvas 는 원본 픽셀 크기와 루트 설정에 매인다.

### 설계

| 함정 | 실제 |
|---|---|
| 한 GameObject 에 Graphic 하나 | TMP 오브젝트에 `AddComponent<Image>()` 는 null 반환 → NRE. 배경은 별도 자식으로 |
| `Image.type = Filled` | sprite 가 없으면 무시된다. 흰 스프라이트를 물린다 |
| `Image.Type.Tiled` | 원본 픽셀 크기로 가로·세로 양쪽 반복한다. `pixelsPerUnitMultiplier` 로 주기를 맞춘다 |
| 9-slice 보더 | 원본 픽셀 크기로 그려진다. 좌우 보더 합이 배치 크기를 넘으면 가운데가 사라진다. 그 아트를 쓰는 가장 작은 자리 기준으로 잡는다 |
| 원본이 `background-size:100% 100%` | 9-slice 가 아니라 통짜 스트레치다 |
| 세로로 크게 눌리는 장식 아트 | 속이 뭉개진다. 캡처 색으로 단색 판을 깔고 아트는 테두리로만 |
| 중첩 Canvas | `overrideSorting` + `sortingOrder` + `GraphicRaycaster` + 루트와 같은 `renderMode`/`worldCamera` 세트를 완성한다. `worldCamera` 가 비면 WorldSpace 렌더에서 하위가 통째로 안 그려진다 |
| 중첩 Canvas 의 order 를 프리팹에 굽기 | 루트 `sortingOrder` 는 창이 열릴 때 나중에 들어온다. `OnEnable` 에서 한 번만 읽으면 낮은 값으로 굳어 전면 히트 영역에 먹힌다. 루트 order 변화를 따라가는 컴포넌트를 붙인다 |
| 형제 순서로 해결되는데 중첩 Canvas | 형제 순서로 충분하면 중첩 Canvas 없이 간다 |
| 투명 히트 판 | 이미지 헬퍼는 대개 `raycastTarget=false` 가 기본이다. 명시적으로 true |
| 클리핑 누락 | 원본이 `clip()` / `overflow:hidden` 이면 `RectMask2D` 가 필요하다 |

## 판정

### 요약

- 재생 중 좌표는 루트 Canvas 의 렌더 모드를 거쳐야 한다.
- 기준 캡처가 렌더 전 상태면 그대로 베끼면 안 된다.

### 설계

| 함정 | 실제 |
|---|---|
| 재생 중 레이캐스트 좌표 | 루트가 `ScreenSpaceCamera` 라 월드 좌표를 그대로 넣으면 전부 `NONE` 으로 「다 막혔다」고 오판한다. `RectTransformUtility.WorldToScreenPoint(rootCanvas.worldCamera, center)` 를 쓴다 |
| 판 안쪽 y 를 화면 절대값으로 | 판이 상단 stretch 로 앉으면 자식 y 는 판 상단 기준이다 |
| CSS 우선순위 | `#id .class` 가 `#id` 를 이긴다. id 선택자만 보고 판단하면 틀린다 |
| 기준 캡처가 렌더 전 상태 | 그대로 베끼면 조작 불가능한 빈 칸이 남는다. 원본 코드가 실제로 그리는 것을 만든다 |
