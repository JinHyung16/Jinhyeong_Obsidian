---
분류: 규약
성격: 방향
tags:
  - htmltounity
---

# UIFramework - Component

상위: [UIFramework](UIFramework.md)

낱개 UI 는 무조건 동적 생성 + 풀링이다.

## PrefabAuto

### 요약

- `PrefabAuto` 를 클래스에 static 으로 선언한다.
- 생성은 `CreateForUI`, 반환은 `Release` 다.
- 리스트성 UI 는 런타임에 만든다.

### 규칙

- 리스트성 UI 는 런타임에 만든다. 인스펙터에 미리 두지 않는다. 이유: 행 수가 데이터로 갈린다. 박으면 원본과 다른 수가 고정된다.
- 반환(`Release`)을 생성 지점마다 짝지어 확인한다. 이유: 짝이 없으면 풀이 의미가 없다.
- `OnDespawn` 에서 상태를 초기화한다. 이유: 구독이 남으면 다음 사용처에서 두 번 불린다.
- UI 는 `CreateForUI` 를 쓴다. 이유: `RectTransform` 기준으로 붙고 anchoredPosition 을 리셋한다.

### 설계

```csharp
public class ItemComponent : BaseComponent, IPoolable
{
    public static readonly PrefabAuto<ItemComponent> AutoV1 =
        PrefabAuto.Get<ItemComponent>("UI/Components/ItemComponent_V1");

    public void SetData(Sprite icon, string name, int count) { … }   // 외부가 런타임에 주입

    public void OnSpawn() { }
    public void OnDespawn()                     // 이벤트 구독 해제 필수
    {
        OnClicked = null;
        _icon.sprite = null;
    }
}
```

```csharp
var comp = ItemComponent.AutoV1.CreateForUI(parent);   // 생성 (UI 는 CreateForUI)
ItemComponent.AutoV1.Release(comp);                    // 반환
```

## 안 그림과 안 끔

### 요약

- 「안 그림」과 「안 끔」은 다르다.
- 원본은 즉시 모드라 조건이 거짓이면 요소가 아예 안 만들어진다.
- 우리는 유지 모드라 꺼야 사라진다. 원본에 `else` 가 없어도 우리에겐 필요하다.
- 옮길 원본 코드가 없어서 줄 대조로 안 보이고, 스크롤로 셀이 재사용될 때만 드러난다.

### 규칙

- 검수는 열자마자보다 스크롤 왕복 후가 낫다. 이유: 셀이 재사용될 때만 드러난다.

### 설계

```js
if (cond) html += '<div class="badge">…</div>';   // 거짓 → 존재하지 않음
```
```csharp
_badge.SetActive(cond);   // 이 줄이 없으면 이전 셀의 뱃지가 남는다
```

| 원본에 없어서 빠뜨리는 것 | 우리에게 필요한 것 |
|---|---|
| 조건부 요소의 `else` | 안 쓰는 자식을 명시적으로 끈다 |
| 이벤트 해제 | `x.On -= H; x.On += H;` 또는 `OnDespawn` 에서 `null` |
| 캐시 무효화 | 캐시 옆에 입력 목록을 적고 하나라도 바뀌면 버린다 |
| 이전 상태 리셋 | 프레임·색·알파·스프라이트까지 전부 되돌린다 (일부만 되돌리면 섞인다) |

```bash
# 점검 — 해제 없는 구독
grep -rn "+= *On[A-Z]\|+= *Handle" Assets/Scripts/UI --include=*.cs | grep -v "\-="
```

## 표기 책임

### 요약

- UI 는 표기만 한다.
- 기본은 DB id 를 인스펙터에 적는 대신, Management 가 id 와 표기 정보를 `SetData(...)` 로 런타임 주입하는 것이다.
- UI 는 받은 것을 보여준다. 이유: id 가 프리팹에 박히면 데이터가 바뀔 때 프리팹을 고쳐야 한다.

## 설계 순서

### 요약

- 기본 순서는 기존 컴포넌트 재사용 → 프리팹 변형 추가 → 새 클래스다.
- 재사용이 나은 것은 원본 구조가 같을 때다.

### 규칙

- 같은 레이어 구성이 여러 곳에 쓰이면 프리팹 2개 대신 컴포넌트 1개 + 프리팹 변형으로 간다 (아이콘/이름/개수 줄 → `ItemBaseComponent` 하나).
- 이름이 비슷하다고 돌려 쓰지 않는다. 이유: 원본에 없는 설계가 들어온다. 원본 구조가 다르면 새 클래스가 낫다.

### 설계

사례: 확률표를 상점 팝업으로 돌려 썼는데 원본 설계가 달랐다.
