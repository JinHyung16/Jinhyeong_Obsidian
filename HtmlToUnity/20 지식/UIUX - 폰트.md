---
분류: 지식
성격: 방향
tags:
  - htmltounity
---

# 폰트 · 글리프

상위: [UI/UX 파트](UIUX.md)

## 주폰트

### 요약

- 「원본 폰트를 가져오면 된다」가 아니다. 원본 CSS 폰트가 모든 글리프를 그리지 않는다.
- 주폰트는 가장 넓은 글리프 집합이 가져간다.
- 자형은 2순위다.

### 설계

사례: `Chakra Petch` + `Share Tech Mono` 는 한글 0자(cmap 실측)라 원본에서도 OS 폴백이 한글을 그렸고, 주폰트가 될 수 없었다.

1. 화면에 나오는 문자 집합(본문 언어 + 기호 + 이모지)을 센다.
2. 후보 폰트 cmap 을 실측해 표로 만든다.
3. 기본은 본문 언어를 100% 덮는 폰트를 주폰트로 정하는 것이다. 자형은 2순위다.
4. 남는 구멍만 스프라이트로 내린다.

- 사례(프로젝트마다 다시 잰다): Noto Sans KR 23,174 글리프 · 한글 11172/11172 · U+2715 U+25C8 U+2699 외 기호 있음 / Chakra Petch 725 · 한글 0 / Share Tech Mono 267 · 한글 0. 한글을 쥔 폰트가 하나라 자형 차이는 허용 오차로 못박았다.
- 「원본 폰트 주 + 본문 언어 폴백」은 기본에서 뺀다. 이유: 거의 모든 문자열이 폴백을 타 비용이 같다.

## 폴백

### 요약

- 폴백 폰트는 쓰지 않는다. 「폰트는 하나」가 기본값이다.
- 이유: 폴백은 한 글자를 위해 폰트를 하나 더 들인다.
- 폴백은 두 곳에 있고 둘 다 세야 「0」이다.

### 설계

폴백을 들이면 이렇게 된다.

- 빌드에 폰트 파일이 더 실린다 (다이내믹이면 TTF 통째로).
- 없는 글자를 새로 써도 조용히 메워 드러나지 않는다.
- 자형이 섞인다.

폴백을 얹기 전에 주폰트 cmap 을 실측하고, 남는 구멍은 스프라이트로 내리는 쪽(「주폰트」)을 먼저 본다.

```bash
# TTF 의 cmap 을 직접 파싱해 대상 코드포인트 유무를 찍는다 (fontTools 없어도 된다)
python cmap.py *.ttf
```

| 자리 | 확인 |
|---|---|
| 엔진 전역 설정 | `TMP_Settings.fallbackFontAssets` |
| 폰트 에셋마다 | `TMP_FontAsset.fallbackFontAssetTable`. 안 쓰는 기본 에셋에도 붙어 있다 |

점검은 메뉴(`Verify No Font Fallback`)로 둔다.

## 폰트 교체

### 요약

- 폰트를 바꾸면 「참조가 끊긴 프리팹」이 남는다. 화면에서만 멀쩡해 보인다.
- 옛 폰트 에셋을 지우면 프리팹이 죽은 GUID 를 가리키지만, TMP 가 로드 때 기본 폰트로 대체해 에디터에서는 멀쩡하다.
- 기본은 메모리가 아니라 직렬화 파일에서 판정하는 것이다.

### 설계

사례: 일괄 교체 도구가 0개 변경을 보고했다. 메모리(`text.font`)는 새 폰트였고 직렬화 파일만 깨져 있었다.
이유: 에디터 겉보기로는 대체된 폰트와 새 폰트가 갈리지 않는다.

```bash
grep -rl "<옛 폰트 GUID>" Assets/ | wc -l      # 0 이어야 한다
```

1. 스크립트로 굽는 프리팹은 다시 굽는다.
2. 스크립트가 소유하지 않는 것(손으로 만든 공용 프리팹·머티리얼)은 `m_fontAsset` · `m_sharedMaterial` · 머티리얼 `_MainTex` 셋을 같이 간다.
3. 프리팹 전수로 `font == null` 을 센다(`Verify TMP Font References`).

## Dynamic 폰트

### 요약

- Dynamic 폰트는 에디터에서 계속 자란다.
- 글리프가 수천 자(한글)면 Dynamic 이 맞다.

### 설계

- 에디터에서 화면을 열 때마다 에셋이 커져 2MB 넘는 diff 가 생긴다.
- 커밋 전에 아틀라스를 비우는 메뉴(`ClearFontAssetData`)를 두는 쪽이 낫다. 런타임 영향은 없다.

## 스프라이트 크기

### 요약

- 스프라이트가 활자와 같은 크기로 앉게 만드는 법이다.
- `faceInfo.pointSize` 가 0 이면 TMP 가 `ascentLine / metrics.height` 로 정규화해 `metrics.height` 는 최종 크기에 영향이 없다.
- 기본은 `metrics` 를 글리프 바운딩박스 그대로 두고, 크기는 `scale` 하나로 잡는 것이다.

### 설계

```
렌더 높이   = ascentLine / pointSize * fontSize * spriteCharacter.scale
렌더 폭     = 렌더 높이 * metrics.width / metrics.height     (종횡비는 metrics 가 정한다)
advance     = 렌더 높이 * metrics.horizontalAdvance / metrics.height
baseline까지 = 렌더 높이 * metrics.horizontalBearingY / metrics.height
```

`metrics` 는 비율만 맞으면 된다.

```
scale = 목표높이(em) / (ascentLine / pointSize)
```

목표 높이는 바꾸기 전에 폴백이 그리던 값을 실측한다.

```csharp
tmp.text = "A" + (char)0x2605 + (char)0x221E + "H"; tmp.ForceMeshUpdate(true, true);   // 별 + 무한대
var ci = tmp.textInfo.characterInfo[i];
// 높이 = topLeft.y - bottomRight.y,  yMax = topLeft.y - baseLine,  advance = xAdvance - origin
// 주의: 월드스페이스 TMP 는 0.1 배수가 끼어 있다 — fontSize 가 아니라 fontSize/10 으로 나눠야 em 이 된다
// 주의: 활자 쪽 실측값에는 SDF 패딩이 포함된다. 스프라이트에도 같은 여유를 주면 상쇄된다
```

사례: `∞` 를 LiberationSans 폴백에서 스프라이트로 내린 오차. 높이 +1.2% · yMax +0.4% · advance +0.25%.

## 글리프 아트

### 요약

- 아트는 손으로 그리지 않는다.
- 기본은 손으로 다시 그리는 대신 글리프를 래스터라이즈하거나 이미 있는 아트를 픽셀 그대로 쓰는 것이다.

### 규칙

- #강제 [원칙 R11](원칙.md#R11) 원본 그림을 그대로 가져오는 것은 원본을 쓸 권리가 있는 게임(허용 라이선스 원본 등)에서만 한다. 상용 원본이면 규격만 재서 다시 만든다. 픽셀을 어디까지 맞출지는 그 게임 확정표를 따른다.

### 설계

- `∞` 는 폴백 폰트 글리프를 래스터라이즈해 굽는다 (PIL `ImageFont.truetype` → `anchor="ls"` 베이스라인 렌더 → 알파 bbox 크롭).
- 별(U+2605)·체크(U+2713)는 게임이 쓰는 아트를 픽셀 그대로 가져온다. 인라인 별과 별 컴포넌트 모양을 맞추기 위해서다.

## 치환 경로

### 요약

- 치환 Helper 를 안 타는 경로가 남는다. 그게 진짜 버그다.
- 폴백을 떼면 드러난다.
- 기본은 그 글자가 든 데이터 컬럼을 세고, 그 컬럼의 표시 경로를 전부 훑는 것이다.

### 설계

```bash
# 어느 테이블 · 어느 컬럼에 들어 있는지부터 센다
python -c "...json 순회해서 컬럼별 카운트..."   # 결과 예: Name 12 · Description 164 · Script 1
# 그 다음 그 컬럼을 읽는 코드를 전부 찾는다
grep -rn "row\.Name\|node\.Name\|\.Description\b" Assets/Scripts/UI
```

- 사례: 트리 노드 이름(별 12개)이 치환을 안 타 원래부터 공백이었다.
- 치환 함수는 결과에 원래 글자가 남지 않게 해 두 번 호출해도 안전하게 만든다.

## TMP 일반

### 요약

- 폰트에 없는 기호는 텍스트 대신 Image/스프라이트로 얹는 것이 기본이다.
- TMP 는 같은 숫자를 브라우저보다 크게 그린다(실측 약 25%).
- 자형·자간 차이는 허용 오차다.

### 설계

CSS `font-size` 대신 캡처 글리프 높이로 역산한다.
