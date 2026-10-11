---
분류: 규약
성격: 방향
tags:
  - htmltounity
---

# SkillSystem - 조합 데이터

상위: [SkillSystem](SkillSystem.md)

스킬 하나는 파일 몇 개 복붙이다.

## 모듈 파일

### 요약

- 스킬 하나는 Master · Method · Visual · Shared 파일로 이루어진다.
- 새 스킬은 Master 와 Visual 을 복사해 id · 이름 · 값만 바꾼다.
- Method 는 이름으로 참조해 공유한다. 이유: 발사 방식을 복제하면 투사체 속도 하나 고치는 데 N군데가 된다.

### 규칙

- Master 는 Visual 을 이름으로 가리키지 않는다. 같은 파일 이름이 곧 연결이다.
- 파일 경로(확장자 제외)가 모듈 ID 다.
- 토큰 `@stat.<키>` · `@visual.<키>` 와 id 참조 `#debuff/<경로>` 는 굽기 타임에 치환하는 것이 기본이다. 이유: 런타임 문자열 해석이면 오타가 굽기 검사를 빠져나간다.
- #강제 [원칙 R1](원칙.md#R1) 상태이상 중첩 값은 원본의 중첩 규칙 그대로다.

### 설계

```
[예시] Assets/<게임명>/Editor/SkillData/
  _enums.js                 노드 종류 · 파라미터 키 · 상태이상 종류 (enum 원본. 굽기가 C# enum 을 만든다)
  Skill/Master/<이름>.js     발동 + 대상 + method 참조 + 슬롯 채우기
  Skill/Method/<이름>.js     발사 방식. 형제 노드 목록 + 슬롯. 여러 스킬이 공유
  Skill/Visual/<이름>.js     그림 키 · 색 · 수치 · 레벨 곡선. 파일 이름으로 Master 와 짝
  Shared/buff|debuff/<이름>.js  id 로 조회하는 상태이상 (중첩 정책 포함)
```

- 레벨 곡선은 `levels` (함수 또는 배열)로 적고 굽기가 `maxLevel` 만큼 펼친다. 런타임은 레벨 값을 기본 파라미터보다 먼저 본다.
- 상태이상은 `stackMode` (`Refresh` · `Stack` · `Ignore`) 와 `maxStacks` 로 중첩을 데이터가 정한다.

## 조립 규칙

### 요약

- 트리가 아니라 형제 나열이다.
- 리프 대부분은 컨텍스트에 값을 적기만 하고 마지막 Launch 가 그것을 읽는다.
- 이유: 굽기가 위치를 검사한다.

### 규칙

- Launch 와 Trigger 는 자식을 실행하지 않는다. Hit 을 Launch 자식으로 매달면 피해 0 이 조용히 나간다.
- 자식을 실행하는 것은 흐름 노드뿐이다 (`Cooldown` · `Chance` · `Selector` · `Inverter` · `Parallel`).
- 발사체가 없는 스킬(자기 버프)은 Launch 없이 끝나도 된다.

### 설계

```
[예시]
Sequence
├ Trigger*      발동 조건 (쿨다운 · 공격 시 · 확률)
├ Target*       ctx.Targets
├ Hit*          ctx.HitNode
├ Debuff*       ctx.DebuffNodes
├ Despawn*      ctx.DespawnNode
└ Launch*       위를 전부 읽어 투사체 레코드를 만든다 — 항상 마지막
```

## 굽기 검증

### 요약

- 굽기 검증을 통과 못 하면 아무것도 안 쓴다.
- 막는 결함은 여섯 갈래다.

### 규칙

- #강제 [원칙 R23](원칙.md#R23) 검증 실패는 종료 코드 비0 과 산출물 미갱신이다.
- #강제 [원칙 R23](원칙.md#R23) 미구현 목록은 손으로 맞추지 않는다. 에디터 검사가 레지스트리를 훑어 갱신한다.

### 설계

| 검사 | 안 막으면 |
|---|---|
| Launch 뒤에 노드가 남음 · Launch 2개 이상 | 뒤 노드가 영영 안 돈다 |
| Hit · Despawn 2개 이상 | ctx 슬롯이 하나라 뒤가 앞을 덮는다 |
| 필수 슬롯 미충전 · 선언 안 된 슬롯 충전(오타) | 스킬이 조용히 반쪽으로 나간다 |
| 없는 토큰 키 · 죽은 id 참조 · id 중복 | 기본값 0 으로 조용히 나간다 |
| enum 에만 있고 C# 노드가 없음 (미구현 목록) | 데이터로 써도 아무 일도 안 한다 |
| 중첩 정책 모순 (`Refresh` 인데 `maxStacks > 1`) | 원본과 다른 누적 |

내용이 같으면 파일을 안 건드려 불필요한 리임포트를 막는다.
