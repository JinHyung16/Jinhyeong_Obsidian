---
분류: 지식
성격: 방향
tags:
  - htmltounity
---

# 카드 장식

상위: [UI/UX 파트](UIUX.md)

## 장식과 내용물

### 요약

- 장식과 내용물을 한 필드에 겸하지 않는다.
- 정적 장식은 프리팹에 물리고, 데이터 종속 아트는 런타임에 주입한다.
- 사례: 아이콘 필드가 육각 테두리를 물고 있어 런타임 아이콘 주입 때 테두리가 사라졌다(인스펙터로는 정상).

### 설계

```css
.awep-frame{width:126px;height:126px}          /* 테두리 (등급색 stroke) */
.awep-frame .aug-ic{width:52px;height:52px}    /* 그 안에 든 아이콘 */
```

| 구분 | 예 | 처리 |
|---|---|---|
| 정적 장식 | 프레임, 패널 테두리, 탭 아이콘 | 프리팹에 직접 물린다. 런타임은 건드리지 않는다 |
| 데이터 종속 | 초상·유닛·아이템 아이콘·구역별 배경 | 프리팹 대신 런타임 `SetXxx` 로 주입 |

- 기본은 겹치는 자리를 부모/자식으로 나누고 원본 비율(52/126)을 쓰는 것이다.
- 같이 물드는 등급색은 전용 setter 하나로 묶는다 (원본 `.rk-*` 하나로 테두리·태그·아이콘·프레임이 바뀐다).
- 후보가 유한한 등급별 프레임은 배열 필드에 물리고 인덱스로 고른다. 정적 취급이다.
- 주의: 원본이 `border-color` 면 등급색은 테두리에만 물린다. 배경에 물리면 카드 전체가 칠해진다.

## CSS 클래스 한 벌

### 요약

- CSS 클래스 하나가 만드는 요소를 낱개로 옮기면 반드시 하나가 빠진다.
- 한 클래스가 본체 + `::before` + `::after` 를 같이 그린다.
- 하나가 빠지면 그 클래스를 쓰는 모든 화면에서 빠진다.

### 설계

```css
.hud-frame{ border:1px solid var(--line); ... }                       /* 1) 외곽선 */
.hud-frame::before,::after{ width:32px;height:32px;
                            border:4px solid var(--cyan); opacity:.8; } /* 2) 좌상·우하 ㄱ자 */
```

- 사례: 코너만 옮겨 1px 외곽선이 팝업 아홉 곳에서 빠졌다.
- 기본은 클래스 하나 = 헬퍼 하나다. `AddHudFrame()` 처럼 한 벌을 붙이는 함수를 두고, `AddCornerTicks` 같은 조각 함수 주석에 「이것만 부르면 ○○이 빠진다」를 적는다.
- 옮기기 전에 그 클래스 규칙 수를 세고 옮긴 수와 맞춘다. 클래스명은 원본마다 다르다.

```bash
# 클래스 본체 + 의사요소 + 다른 규칙의 오버라이드까지 한 번에
grep -no "\.hud-frame[^}]*}" 원본.html
grep -no "[^{}]*hud-frame::before[^}]*}" 원본.html   # 카드별 크기 오버라이드가 있다
```

## 테두리 색

### 요약

- 「테두리」는 대개 카드마다 색이 다르다. 한 값으로 굽지 않는다.
- 공용 프레임 클래스의 기본 테두리색을 개별 카드가 덮는다.

### 설계

- 사례: `.shop-card`·`.sk-card` `--ac:var(--cyan)` · `.lucky-card` `#2a3a58` · `.anom-card` `1.5px #b23a3a`(굵기도 다름) · 나머지 `.hud-frame` 상속 `--line`.
- 기본은 헬퍼에 색을 인자로 빼는 것이다. 인자 기본값은 기본 테두리색, 덮는 카드만 넘긴다.
- 공용 프레임 클래스가 아닌데 테두리가 있는 카드(`.lucky-card`·`.lko-card`)가 있으니 「테두리」와 「코너 브래킷」을 따로 받는다.

## 애니메이션 색

### 요약

- 애니메이션의 어두운 구간이 찍힌 캡처를 「정색」으로 오인하지 않는다.
- 기본은 색은 CSS 에서, 밝기 변화는 컴포넌트에서 가져오는 것이다.
- 이유: 캡처 한 장은 주기 중 한 순간이다.

### 설계

사례: 경고 아이콘을 `#8a3a35` 로 구웠다. 원본은 `#ff5a4d` 이고 `anHdBlink` 가 주기 40% 를 `opacity:.25` 로 보낸다.
캡처로 색을 정하기 전에 `animation` / `transition` 을 본다.

```bash
grep -no "\.anom-head \.wic{[^}]*}" 원본.html      # color:#ff5a4d + animation:anHdBlink
grep -no "@keyframes anHdBlink{[^}]*}" 원본.html   # 0%,60%{opacity:1} 61%,100%{opacity:.25}
```

## animation 과 hover

### 요약

- 캡처에 절대 안 찍히는 것이 둘 있다. `animation` 과 `:hover` 다.
- 화면을 열 때 원본 CSS 에서 먼저 훑는다.

### 설계

```bash
grep -no "animation:[^;]*;" 원본.html | sort -u -t: -k3
grep -no "[^{]*:hover{[^}]*}" 원본.html
```

| 원본 | 성질 | 이식 |
|---|---|---|
| `animation: anHdBlink 1.05s steps(1,end)` | 계단. 한 주기에 두 값 | `UIBlink` (듀티 0.6) |
| `transition: transform .25s` + `:hover{rotate(40deg)}` | 상태 전이 | `UIHoverRotate` |

- `steps()` 는 계단 그대로 옮기는 것이 기본이다. 이유: 사인파로 바꾸면 한 주기에 두 값이라는 성질이 사라진다. 듀티는 0.5 가 아니라 원본 60% 다.
- `:hover` 는 무엇이 도는지 본다. `.set-gear:hover{transform:rotate(40deg)}` 는 버튼 판 전체가 돈다.
- 같은 `:hover` 규칙의 `border-color`·`color` 까지 한 컴포넌트가 쥔다.

## 표기 분기

### 요약

- 원본의 표기 분기 개수를 세고 그대로 옮긴다.
- 분기 순서도 옮긴다.
- 갈래별 색도 옮긴다.

### 설계

```js
// 노드 비용 한 자리에 네 갈래가 들어 있다
let costTxt = root  ? '<span class="cost no">시스템</span>'
            : maxed ? '<span class="cost max">MAX</span>'
            : !reach? '<span class="cost no">잠김</span>'
            :         '<span class="cost">◆' + fmtCost(cost) + '</span>';
```

- 사례: `cost.HasValue ? 숫자 : null` 로 옮겨 세 갈래가 빈칸이 됐다.
- 원본 한 자리의 분기 수와 옮긴 코드의 분기 수를 맞춘다.
- 분기 순서도 옮긴다. `maxed` 가 `!reach` 보다 먼저라 MAX 이면서 잠긴 노드는 `MAX` 다.
- 갈래별 색을 옮긴다 (`.cost` amber / `.cost.max` green / `.cost.no` muted).

**「기본 + .on 오버라이드」는 「숨김 + 표시」가 아니다**

```css
.pip     { background:#2a3650; }   /* 미획득도 자리를 보여준다 */
.pip.on  { background:var(--nc); box-shadow:0 0 5px var(--nc); }
```

기본은 `enabled=false` · `SetActive(false)` 대신 색을 바꾸는 것이다. 이유: 숨기면 `1/8` 이 점 하나로 보인다.

**`Infinity` 는 표기 분기를 같이 옮긴다**. `nodeMax` 가 `Infinity` 면 표기가 pips 에서 `Lv N` 으로 갈라진다.

```js
function nodeScaling(k){ const mx=nodeMax(k); return mx===Infinity || mx>12; }
```

사례: `int.MaxValue` 로만 옮겨 `1/2147483647` 과 pips 12개가 겹쳤다.
경계값(`> 12`)이 계약이다. UI 에서 오는 값(pip 슬롯 개수 등)이면 상수 대신 그 배열 길이에서 뽑는 쪽이 낫다.
