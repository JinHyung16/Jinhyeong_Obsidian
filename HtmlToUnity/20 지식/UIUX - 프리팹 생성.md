---
분류: 지식
성격: 방향
tags:
  - htmltounity
---

# 프리팹 생성

상위: [UI/UX 파트](UIUX.md)

## 재사용 · 생성

### 요약

- 새로 그리기 전에 기존 컴포넌트 재사용 → 프리팹 변형 → 새 클래스 순으로 찾는다.
- 기본은 빌더 코드가 첫 초안을 굽고, 이후 수정은 기존 프리팹을 여는 것이다.
- UI 는 표기만 한다.

### 규칙

- #강제 [원칙 R22](원칙.md#R22) 사람이 손본 프리팹이 있으면 코드로 다시 구워 덮지 않는다.

### 설계

- 리스트성 UI 는 동적 생성이 기본이다. 개수가 작고 상한이 고정인 것(스택 점 5칸 등)은 프리팹에 만들어 켜고 끄는 쪽이 낫다.
- UI 는 표기만 한다. DB id 는 인스펙터에 적는 대신 외부가 런타임 주입한다.
- 빌더와 프리팹의 주인은 확정표 10-b 「프리팹이 주인」이다. 이유: 인스펙터를 손으로 클릭해 만든 것은 재현이 안 되고, 빌더가 매번 통째로 구우면 손본 것이 날아간다. 그 게임이 「빌더가 주인」으로 확정됐으면 빌더를 고쳐 다시 굽는다.
- `[SerializeField]` private 참조는 리플렉션 주입 헬퍼로 넣는다. UnityEngine.Object 가 아닌 직렬화 클래스 배열은 `SerializedProperty` 로 원소마다 채운다.

## 재사용 단서

### 요약

- 「재사용 우선」에는 단서가 붙는다. 원본 구조가 같을 때만이다.
- 정렬(좌/중앙) · 열 수 · 행 구분(밑줄/카드) · 프레임 종류 · 버튼 배치 중 하나라도 다르면 새로 만든다.
- 공용으로 남길 것은 그보다 작은 단위(행 컴포넌트, 프레임)다.

### 설계

- 원본 두 화면 DOM/CSS 를 나란히 놓고 본다.
- 사례: 모집 확률표를 상점 `OddsPopup` 으로 돌려 썼다가 `RecruitRatesPopup` 을 새로 만들었다.

## 임포트 설정

### 요약

- 구운 뒤 임포트 설정을 안 걸면 굽는 의미가 없다.
- 기본값 `Multiple` 은 자동 슬라이스, `Tight` 메시는 여백 트리밍으로 `sprite.rect` 를 바꾼다.
- 기본은 생성기가 저장 직후 설정을 직접 거는 것이다.

### 설계

사례: 464² 로 구운 5층이 `base 414²` · `alt 284×176` · `reticle 8×13` 으로 잡혀 층마다 배율이 달라졌다.

최소 네 가지다.

```csharp
importer.textureType      = TextureImporterType.Sprite;
importer.spriteImportMode = SpriteImportMode.Single;      // 자동 슬라이스 차단
importer.alphaIsTransparency = true;
settings.spriteMeshType   = SpriteMeshType.FullRect;      // 여백 트리밍 차단
```

이름에 `_0` 이 붙었거나 `sprite.rect != 텍스처 크기` 면 잘린 것이다.

```csharp
var sp = AssetDatabase.LoadAssetAtPath<Sprite>(path);
var tx = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
Log.Success(sp.name + " " + sp.rect.size + " vs " + tx.width + "x" + tx.height);
```

## 캔버스 층 가르기

### 요약

- 캔버스 한 장을 옮길 때는 색과 움직임으로 층을 가른다.
- `<canvas>` 하나에 여러 겹을 그리는 원본은 층을 갈라 굽는 것이 기본이다.
- 이유: 한 장으로 구우면 데이터 색도, 층별 회전도 못 준다.

### 설계

사례: 원본 9층 홀로그램이 이식본에서 배경 한 장이었다.

| 기준 | 처리 |
|---|---|
| 색이 다르다 (`ac` / `ac2`) | 층을 나눠 흰색+알파로 굽고 런타임 tint |
| 회전 속도가 다르다 | 층마다 굽고 `UISpin` 에 원본 rad/s 환산값 |
| 회전이 아니라 폭 변조다 | 정지 프레임을 굽고 과제로 남긴다 |
| 정적이고 색이 같다 | 한 장으로 합친다 |

기본은 알파를 텍스처에 굽는 것이다. 이유: 층별 `globalAlpha`(0.16 / 0.55 / 0.6 / 0.06)는 런타임에서 통일할 수 없다. tint 는 RGB 만, 알파 1.

## 알파 프로파일

### 요약

- 절차 생성 도형은 구운 PNG의 알파를 직접 찍어 확인한다.
- 「뿌옇다」는 대개 알파 프로파일 문제다.
- 기본은 눈 대신 알파 값을 찍어 판별하는 것이다.

### 설계

사례: `RoundRectSdf` 가 직선 구간에서 `qx=qy=0` 이라 `-radius` 로 포화해 카드 전체에 균일 알파(blur 48 → 112/255)가 깔렸다.

```bash
# 구운 뒤 중앙 가로선의 알파를 그대로 찍는다 — 계단이 없으면 포화다
python -c "
from PIL import Image; im=Image.open('out.png').convert('RGBA'); w,h=im.size
print([im.getpixel((x,h//2))[3] for x in range(0,w,4)])"
```

볼 것: 가장자리에서 0으로 떨어지나 · 안쪽이 상수로 굳지 않았나 · 의도한 띠가 계단으로 나오나.

## 팩토리 헬퍼

### 요약

- 공용 팩토리 헬퍼는 입력 조합별 degenerate 케이스를 스캔한다.
- 헬퍼를 고치거나 만들면 호출부의 실제 인자 조합을 전부 굽고 몽타주로 보는 것이 기본이다.

### 설계

사례: `EnsureSlicedSprite` 가 `radius` 만 보고 크기를 잡아 `thickness ≥ half` 에서 안쪽 사각형이 음수가 되어 LR 등급 테두리가 채움 판이 됐다.
