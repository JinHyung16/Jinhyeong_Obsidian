---
분류: 지식
성격: 방향
tags:
  - htmltounity
---

# 레이아웃

상위: [UI/UX 파트](UIUX.md)

## 계층

### 요약

- Window → Panel 두 단계까지만 간다.
- 원본이 `.screen > .body > 블록들` 이면 우리도 그렇게 만든다.
- 블록 높이만 실측해 넣으면 접힘/펼침이 자동으로 맞는다.

### 설계

```
XxxWindow            Canvas + Scaler + Raycaster + XxxWindow.cs
├ BG                 anchor 0,0~1,1 / sizeDelta 0
├ TopBarPanel        상단 고정
├ BodyPanel          원본 flex 컨테이너 → VerticalLayoutGroup
│  ├ AaaPanel        늘어나는 블록은 LayoutElement.flexibleHeight = 1
│  └ BbbPanel        나머지는 preferredHeight (캡처 실측값)
└ NavPanel
```

- Window 최상위 자식은 낱개 위젯이 아니라 `XxxPanel` 단위로 자르는 것이 기본이다. 원본 블록 구성이 다르면 원본 구조를 따른다.
- Window 스크립트는 패널을 프로퍼티로 노출만 한다. 로직 없음.

## 앵커 패턴

### 요약

- 용도별 앵커·피벗 기본값이다.
- 캡처는 왼쪽 변을 재므로 변 기준이 기본이다.

### 설계

| 용도 | anchorMin/Max | pivot | 비고 |
|---|---|---|---|
| 전체 배경 | (0,0)~(1,1) | (0.5,0.5) | sizeDelta 0 |
| 상단 고정 바 | (0,1)~(1,1) | (0.5,1) | `sizeDelta.x`=음수(좌우 인셋) |
| 세로 스택 블록 | (0,1)~(1,1) | (0.5,1) | `anchoredPosition.y` = -y |
| 하단 버튼 바 | (0,0)~(1,0) | (0.5,0) | |
| 중앙 카드 | (0.5,0.5) | (0.5,0.5) | 팝업 기본 |

- 「중심 좌표」와 「왼쪽 변 좌표」 헬퍼를 구분한다.
- 회전시킬 rect 는 앵커·피벗을 직접 잡는 쪽이 낫다. 상단 피벗 헬퍼는 그 축으로 돈다.
- 부모 변에 붙이는 아이콘은 앵커까지 옮긴다.

## 레이아웃 함정

### 요약

- 실제로 걸렸던 것들이다.
- 레이아웃 그룹의 기본값이 대부분의 원인이다.

### 설계

- 행 폭 헬퍼는 세로 스택 밖에서 쓰는 것이 기본이다. 이유: 레이아웃 전 `rect.width` 기본값 100을 본다. 세로 스택 안이면 `LayoutElement.preferredWidth` + `childForceExpandWidth = false` 로 고정한다.
- 세로 레이아웃 헬퍼는 `childControlHeight` 를 건드리지 않는다(가로판은 켠다). false 로 남으면 자식이 기본 100으로 앉으니 쓰는 자리에서 명시한다.
- `HorizontalLayoutGroup` 은 `childForceExpandWidth` 기본 true 다. `preferredWidth` 가 무시되고 합이 부모 폭을 넘으면 0폭까지 눌린다.
- 레이아웃 그룹 아래 낱개 아이콘에는 `LayoutElement` 를 주는 것이 기본이다. 이유: 없으면 점 하나가 행 전체로 늘어 타원이 된다.
  ```csharp
  var le = dot.gameObject.AddComponent<LayoutElement>();
  le.preferredWidth = size; le.preferredHeight = size; le.flexibleWidth = 0f;
  ```
- `childControlHeight=true` 아래 버튼은 높이를 명시한다. `preferredHeight` -1이면 0 높이로 수축해 클릭 영역이 사라진다.
- `ContentSizeFitter` 를 레이아웃 그룹의 자식에 붙이면 부모와 높이를 두고 싸운다. 기본은 그 자리에서 빼는 것이다.
- 레이아웃 그룹 안 테두리·코너 틱은 `ignoreLayout` 을 준다.
- 행 수가 상황마다 다른 카드는 `ContentSizeFitter` 로 늘리는 쪽이 낫다. 중앙 앵커면 위아래로 같이 자란다.

## 원본 좌표 계산

### 요약

- 원본의 좌표 계산은 옮기는 게 아니라 버리는 것이다.
- HTML5 는 코드가 요소마다 좌표를 박고(`left:36%` · `top:rowY(y)px`), UGUI 는 컨테이너가 배치를 소유한다.
- 원본 배치 계산을 이식하면 배치 주체가 둘이 되어 프리팹 값이 안 먹거나 스크롤 길이가 어긋난다.

### 규칙

- #강제 [원칙 R2](원칙.md#R2) 요소마다 좌표를 박는 원본 배치 계산은 구조째 옮기지 않는다.

### 설계

기본은 격자·리스트로 표현되는 것은 전부 프리팹, 진짜 좌표 그래프만 데이터로 두는 것이다. 원본이 좌표로 정의한 노드 그래프면 데이터로 남기는 쪽이 낫다.

| 원본이 코드로 하던 것 | 이식하면 |
|---|---|
| `x:36` → `left:%` 환산 | 버린다. 데이터는 행 안 순위만, 위치는 LayoutGroup |
| `rowY(y)=y*ROWH + GAP*band` | 프리팹 필드 (`_rowPitch` · `_bandGap`) |
| `SA={3:[22,50,78]}` 배치표 | 프리팹 필드 (직렬화 배열) |
| 그리드를 「행 래퍼 컴포넌트」로 흉내 | 스크롤 뷰에 열 수 필드 하나 |
| 노드 그래프 좌표 (스킬 트리) | 남긴다. 원본이 좌표로 정의했다 |

- UI 픽셀은 프리팹 인스펙터 값으로 두는 것이 기본이다. 이유: DB 컬럼이나 코드 상수로 옮기거나 인스펙터 값을 코드 상수로 되돌리면 배치 주체가 다시 둘이 된다.
- 사례: 유령 노드 띄움값을 DB 컬럼으로, 행 간격·밴드 여백을 C# 상수로, 유닛 트리 x(0~100)를 데이터로 남겨 한 회차에 네 번 틀렸다.
- 바꾸기 전에 최종 산출물로 대조한다. 중간 판정이 갈려도 결과는 같을 수 있다.
- 사례: 트리 x 를 순위로 바꾸자 중앙 승격 판정이 156행 중 26행 달랐지만 최종 좌표는 전 노드 동일했다.

## CSS 대응표

### 요약

- CSS 레이아웃 프리미티브는 Unity 와 1:1이 아니다.
- 비슷한 것으로 대체하면 줄바꿈이 생기는 순간 어긋난다.
- 대응표를 보고, 없으면 만든다.

### 설계

| CSS | Unity 대응 | 주의 |
|---|---|---|
| `display:flex; flex-direction:row` | `HorizontalLayoutGroup` | `childForceExpandWidth` 끄고 시작 |
| `display:flex; flex-direction:column` | `VerticalLayoutGroup` | `childControlHeight` 를 쓰는 자리에서 명시 |
| `flex:1` | `LayoutElement.flexibleWidth/Height = 1` | |
| `display:grid` (칸 크기 고정) | `GridLayoutGroup` | 칸 크기가 고정일 때만 |
| `flex-wrap:wrap` + `justify-content:center` | 없다 | `GridLayoutGroup` 은 마지막 줄을 왼쪽에 붙인다 |
| `gap` | `spacing` | |
| `align-items:center` | `childAlignment` | |
| `overflow:hidden` / `clip()` | `RectMask2D` | 빠뜨리면 창 밖 요소가 보인다 |
| `border-radius` | 둥근 채움 스프라이트 + `Image.Type.Sliced` | 채움과 테두리를 같은 반경으로 |

- 대응이 없으면 그 속성 하나만 흉내 내는 최소 컴포넌트를 만들고 이름에 대상을 적는 것이 기본이다. 범용 레이아웃 시스템을 짜는 대신 이쪽을 먼저 본다.
- 사례: 줄마다 중앙 정렬하는 픽업 칩 때문에 `UIFlowLayout` 을 만들었다.

## CSS 흐름

### 요약

- CSS 흐름을 고정 박스로 옮기면 「길이가 변하는 순간」 전부 깨진다.
- 기본은 증상을 보고 y 를 미는 대신 원본 흐름 종류로 처방을 고르는 것이다.
- 이유: y 를 밀어 맞춘 자리는 길이가 다시 변할 때 또 깨진다.

### 설계

사례: 한 회차 세 화면. 설명(고정 높이 104 + 가운데 정렬로 위아래 넘침), 단계 행(라벨 고정 폭 120px 로 겹침), 단계 버튼(`childControlHeight` 아래 0 수축).

| 원본이 | 옮기는 법 |
|---|---|
| 세로로 흐른다 | 세로 레이아웃 + `preferredHeight`. 고정 y 면 가장 긴 경우를 담는 높이 |
| 가로로 흐른다 (인라인) | 가로 레이아웃 + 내용 폭(`NoWrap` + `flexibleWidth=0`). 고정 폭 칸으로 자르면 겹친다 |
| `padding` 으로 높이가 정해진다 | 높이 = `padding×2 + fontSize×lineHeight`. 계산 후 캡처로 검증 (「CSS 수치 검증」) |

- 고정 박스를 써야 하면 위 기준(Top)으로 두어 아래로만 넘치게 하는 쪽이 낫다. 가운데 정렬은 위 요소까지 친다.
- 한 요소 높이를 늘리면 아래 요소와 카드 높이도 같이 키운다. 고정 y 화면은 자동으로 밀리지 않는다.

## CSS 수치 검증

### 요약

- CSS 수치는 「계산 → 캡처로 검증」 2단계다. 한쪽만 하면 반드시 틀린다.
- 양방향으로 틀린다. 폰트는 CSS 값이 크게 나오고([폰트](UIUX%20-%20폰트.md) 「TMP 일반」), 캡처 눈대중은 작게 나온다(사례: 원본보다 20% 작음).

### 설계

1. CSS 에서 계산한다. 규칙을 grep 해 `width`/`height`/`padding`/`font-size` 를 뽑고 상속·우선순위(`#id .class` 가 `#id` 를 이긴다)까지 본다.
2. 캡처로 검증한다. 요소 픽셀 bbox 가 1번과 맞는지 본다. 글리프처럼 렌더가 개입하면 캡처가 이긴다(역산).
3. 둘이 다르면 이유를 밝힌 뒤에 넣는 것이 기본이다. 이유: 원인을 모르고 고른 값은 일치를 증명하지 못한다.
