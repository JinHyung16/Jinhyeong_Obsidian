---
분류: 규약
성격: 방향
tags:
  - htmltounity
---

# DataFramework - 시트 컨벤션

상위: [DataFramework](DataFramework.md)

엑셀로 승격한 뒤의 규약이다.

## 3행 헤더

### 요약

- 시트는 3행 헤더다. 1행 컬럼명 · 2행 타입 · 3행부터 값이다.
- 기본 컨벤션이다. 프로젝트 컨벤션이 따로 있으면 그쪽이 이긴다 (「Enum 시트」).

### 설계

```
1행  컬럼명   Id      Code        Name    Rate     PickupEligible   Tags
2행  타입     int!    string!     string  float!   bool             stringArray
3행~ 값       1       adj_kate    케이트   0.03     TRUE             a,b,c
```

| 규칙 | 내용 |
|---|---|
| 컬럼명 | PascalCase. `item name` → `ItemName` |
| 기본 자료형 | `int` `float` `double` `long` `bool` `string` |
| 필수 컬럼 | 자료형 뒤에 `!` (`int!` `string!`). 비면 exporter 가 에러 + 누락 위치를 찍는다 |
| 배열 | `intArray` `floatArray` `stringArray`. 표기를 프로젝트 안에서 하나로 통일한다 |
| 배열 오타 | `stringArray\|` · `intArrayl` 같은 꼬리는 조용히 string 으로 떨어진다 |
| `Id` | `int!` 가 기본. 1부터의 순번이고 테이블 키다 |
| `Code` | 문자열 논리 식별자는 `Code`(`string!`)로 따로 둔다. 같은 `Code` 가 여러 행이어도 `Id` 는 유일 |
| 참조 컬럼 | `Code` 값을 담고 이름은 `~Code` / `~Codes` (`ShipCode`). `~Id` 는 피한다 (int 로 오해된다) |
| enum 컬럼 | 타입 칸에 enum 이름을 적는다. 이유: 판별 어휘를 `string` 으로 두면 시트와 코드로 번지고 폴백까지 자란다. 전환 전에 세이브 키인지 본다(인덱스면 안전, 문자열이면 마이그레이션) |
| 경로 컬럼 | `~Path` 로 두고 `Validate` 에 에셋 존재 검사를 넣는다. 이유: 검사가 없으면 값이 낡아도 모른다 |

## 배열과 쉼표

### 요약

- 배열에 쉼표가 들어가야 하면 배열을 쓰지 않는다.
- 요소 안에 쉼표가 있는 데이터(대사 목록 등)는 1:N 시트로 정규화하고 `GetGroup(code)` 로 묶어 읽는 것이 기본이다.
- 이유: 배열 셀은 쉼표로 요소를 가른다.

### 설계

```
CharacterData       : Id / Code / Name / ...          (캐릭터 1행)
CharacterLineData   : Id / Code / LineType / Text      (대사 N행, Code 로 묶인다)
```

## Enum 시트

### 요약

- Enum 은 `_Enum` 시트에서 나온다.
- 규칙이 없는 프로젝트면 `~Type` 접미가 기본값이다.
- 파이프라인이 정규화하고 위반 시 경고를 낸다. 경고가 보이면 시트 원본을 고친다.

### 규칙

- #강제 [원칙 R15](원칙.md#R15) enum 이름 규칙은 진입 파일(`CLAUDE.md`)·코딩 컨벤션이 이긴다. 이 저장소는 `E` 접두사다.
- 규약 문서와 프로젝트 컨벤션이 어긋나면 한쪽을 고쳐 맞춘다. 어느 쪽을 고칠지는 판단한다.

### 설계

```
_Enum 시트
  CurrencyType      enum 이름
    Gold
    Gem
    Ticket
  StatType
    Hp
    Atk
```
