---
분류: 규약
성격: 방향
tags:
  - htmltounity
---

# GameFramework

GameInitialize · Manager · Management 로 초기화 순서를 한 곳에 고정한다.

## 노트 자리

### 요약

- 방향 노트다. 기본값과 이유를 준다. 판단 대상이 아닌 것은 [원칙](원칙.md) 에만 있다.
- 상위는 [PD](PD.md) 다. 사용자는 [Transfer_Programmer](Transfer_Programmer.md) 다.
- 이 문서는 초기화 순서를 한 곳에 고정하는 기본 구조를 준다.
- 초기화 골격은 [GameFramework - 초기화](GameFramework%20-%20초기화.md), 설정 반영은 [GameFramework - 프로젝트 설정](GameFramework%20-%20프로젝트%20설정.md) 에 있다.

### 규칙

- 원본 · 장르 · 규모를 보고 더 나은 구조가 있으면 고른다. 고른 것과 이유를 확정표에 남긴다.

## 무작위

### 요약

- 무작위는 한 곳에서만 꺼낸다.
- 게임 코드가 엔진 난수나 `new Random()` 을 직접 부르면 바깥에서 못 바꾼다.
- 같은 판을 다시 만들 수 없어 정답지·결정성 검사가 성립하지 않는다.
- 기본은 착수 시 원본의 난수 호출을 세어서 전부 옮기는 것이다. 이유: 하나라도 남으면 결정성이 깨지고 원인 찾기에 회차가 든다.

### 규칙

- #강제 [원칙 R23](원칙.md#R23) 빈 목록에서 뽑을 때 폴백을 깔지 않고 예외를 낸다. 폴백은 어서트를 무력화해 실패를 숨긴다.

### 설계

| 흔한 방식 | 기본값 |
|---|---|
| 호출부마다 난수를 직접 만든다 | 공용 유틸 하나에서 꺼낸다 |
| 검증용 `DebugSetXxx` 를 게임에 뚫는다 | 그 유틸의 주입 지점으로 세운다 |

유틸이 갖추면 좋은 것 네 가지다.

1. 원천 교체. 검사 하네스가 갈아 끼운다
2. 시드 고정. 같은 시드는 같은 수열
3. 원본과 같은 모양의 API. 원본이 `floor(random()*n)` 이면 `Range(n)`
4. 정해진 값을 순서대로 주는 원천. 원본과 같은 뽑기 순서를 먹인다

```bash
# 원본의 난수 호출 전수 — 세고 나서 매칭된 줄을 눈으로 본다
grep -n "Math.random\|randomInt\|shuffle" <원본 스크립트>
```

## 폴더

### 요약

- 코어 공용 코드는 `Assets/Scripts/Core/` 에 둔다. 게임 폴더 밖이다. 없으면 만든다.
- 기본 구성이다. 이름보다 역할이 맞으면 된다.

### 규칙

- #강제 [원칙 R15](원칙.md#R15) `CLAUDE.md` 에 폴더 규칙이 있으면 그쪽이 우선한다.

### 설계

```
Assets/Scripts/Core/             (없으면 만든다 · 공용 — 게임 폴더 밖)
├─ GameInitialize.cs     이 프로젝트에서 Awake 를 쓰는 유일한 파일
├─ GameManager.cs        Manager 소유 · Bootstrap · Update 분배
├─ BaseManager.cs        Manager 베이스 (순수 C#, MonoBehaviour 아님)
├─ IGameUpdate.cs        Update 가 필요한 Manager 만 구현
├─ GameFlow.cs           화면 전이
└─ GameScreenType.cs
```

## 템플릿 잔재

### 요약

- 신규 프로젝트를 청소한다. 템플릿 잔재는 이관의 노이즈다.
- Unity 템플릿의 예제 씬 · Readme · 튜토리얼 스크립트를 두면 원본 대조 판정이 흐려지고, 빌드에 들어가고, 다음 사람이 지워도 되는지 모른다.
- 가르는 기준은 이름보다 「그 에셋을 누가 참조하는가」가 낫다. 이유: 이름만 템플릿인 설정 에셋이 있다.

### 규칙

- 기본은 지우지 않고 임시 폴더로 옮긴 뒤 「어디로 옮겼다」로 보고하는 것이다. 이유: 첫 커밋 전이면 git 이 되살리지 못한다. 이미 커밋된 잔재라면 바로 지워도 된다.
- 원장 리스트업에는 숫자로 남기는 것이 기본이다. 「후보 N개 중 걷어낸 것 M개 · 이름만 바꾼 것 K개」다.

### 설계

| 판정 | 무엇 | 처리 |
|---|---|---|
| 잔재 | 참조 없음 · 예제 목적 (Readme · 튜토리얼 스크립트 · 예제 아이콘 · 레이아웃 · 샘플 씬) | 걷어낸다 |
| 이름만 템플릿 | 이름에 `Sample`/`Example` 이 있지만 다른 에셋이 참조 (볼륨 프로파일 · 렌더러 설정) | 이름만 바꾼다 (GUID 가 `.meta` 에 있어 참조 유지) |
| 설정 | 파이프라인 에셋 · 렌더러 · 인풋 액션 · 글로벌 세팅 | 남긴다 |

```bash
# 1. 잔재 후보
find Assets -iname "*Tutorial*" -o -iname "*Readme*" -o -iname "*Sample*" -o -iname "*Example*"

# 2. 지우기 전에 — 그 에셋의 GUID 를 누가 참조하는가
G=$(grep -m1 -oE "[0-9a-f]{32}" <에셋>.meta); grep -rl "$G" Assets ProjectSettings
#    자기 .meta 뿐이면 잔재. 다른 파일이 나오면 이름만 템플릿
```

걷어낼 때 같이 챙길 것이다.

- `.meta` 를 같이 옮긴다 (고아 meta 는 다음 임포트에 경고)
- 씬을 걷었으면 `ProjectSettings/EditorBuildSettings.asset` 의 `m_Scenes` 를 비운다
- 빈 폴더도 `.meta` 와 같이 정리한다

## 최소 세트

### 요약

- 처음부터 다 만들지 않는다.
- 이 문서 세트는 프레임워크의 사용법이지 코드가 아니다. 신규 프로젝트에는 `BaseWindow` 도 `DataContainer` 도 없다.
- 구축 자체가 리스트업 항목이다. 빠뜨리면 패스 ①에서 없는 클래스를 부르는 코드가 나온다.
- 기본은 그 게임이 실제로 부르는 것만 만드는 것이다. 이유: 안 쓰는 코드는 검증되지 않고 다음 게임의 걸림돌이 된다.

### 설계

「필요해질 때」 열은 그 화면이나 요구가 실제로 나왔을 때 더한다.

| 계층 | 최소 세트 (첫 게임) | 필요해질 때 |
|---|---|---|
| Core | `GameInitialize` · `GameManager` · `BaseManager` · `IGameUpdate` · `GameFlow` · `GameScreenType` | (전부 최소) |
| UI | `BaseComponent` · `BaseWindow` · `WindowKey` · `WindowManagement` · `BaseManagement` · `PrefabAuto`/`PrefabLoader`/`PrefabPoolCore` | `Scroll/` (재활용 목록) · `Graph/` (대량 노드) |
| Data | `IData` · `IDataKey` · `IDataContainer` · `JsonSettings` · `DataContainer` · `DictionaryContainer` · `DataManager` · `GameRoot` | `DictionaryGroupContainer` · `SingleContainer` · `ListContainer` · 엑셀 exporter · 코드젠 |
| `WindowType` | `Normal` · `Popup` 2개부터 | `HUD` · `GlobalPopup` · `Modal` · `Toast` |

## 로컬 저장

### 요약

- 로컬에 저장하면 지우는 버튼을 같이 낸다.
- 기본은 게임이 로컬에 무엇이든 남기면(최고 기록 · 해금 · 설정 · 진행) 지우는 버튼을 같이 만드는 것이다 [사람 확정].
- 이유: 저장이 쌓이면 처음 켠 사람의 화면(첫 진입 연출 · 잠긴 화면 · 초기 문구)을 다시 대조할 수 없고, 사람에게 엔진을 열어 지우라고 시키게 된다 (#강제 [원칙 R16](원칙.md#R16) 에 걸린다).

### 규칙

- #강제 [원칙 R14](원칙.md#R14) 적용은 앞으로다. 이 저장소는 Undead Slayer 부터 단다. 끝난 게임을 소급해서 고치면 UI 프리팹을 다시 구워 검증 통과한 결과물을 흔들게 된다.
- #강제 [원칙 R10](원칙.md#R10) 원본에 없는 것이라 그 게임 확정표의 의도된 차이에 적는다.
- #강제 [원칙 R7](원칙.md#R7) 회귀 검사는 버튼이 있는지가 아니라 「눌러서 키가 사라졌나」까지 본다 (함정: [만든 것을 옮긴 것으로 센 이관율 분자](함정%20-%20판정%20보고.md#만든%20것을%20옮긴%20것으로%20센%20이관율%20분자)).
- 이 게임에는 다른 방식이 낫다고 보면 선택지와 근거를 착수 확정 때 사람에게 보여 교차 확인한다 ([원칙](원칙.md) 「쓰는 법」).

### 설계

| 무엇 | 어디 |
|---|---|
| 지우는 일을 모으는 자리 | 공용 `Assets/Scripts/Core/SaveWipe.cs` |
| 무엇을 지우나 | 게임 쪽. 키를 아는 곳이 지운다 |
| 버튼 | 그 게임 첫 화면 구석에 작게. 원본 요소와 헷갈리지 않게 연출을 안 건다 |

- 기본은 키 목록보다 지우는 일(action)을 등록하는 것이다. 이유: `World_3` 처럼 이름이 만들어지는 키가 있어 바깥에서 다 알 수 없다.
- 대표 키를 같이 넘기면 검사가 정말 지워졌나를 볼 수 있다 (`PlayerPrefs` 는 키를 훑을 수 없다).
- 버튼 문구는 원본 로케일 표 밖에 두는 것이 기본이다. 이유: 그 표는 원본 전수가 분모라 섞으면 이관율이 거짓이 된다.

주의: 등록을 빠뜨리면 버튼이 있어도 아무것도 안 지우고 오류도 안 난다.

## 공용 승격 기준

### 요약

- 공용으로 올리는 기준은 두 번째 게임이 정한다.
- 「나중에 쓸 것 같아서」는 공용으로 올릴 근거로 약하다. 이유: 두 번째 게임 전까지 아무도 검증하지 않는 코드가 된다.
- 스킬 노드 골격 행은 사람이 고른 설계 기본값이라 승격 기준의 예외다.

### 규칙

- 다르게 두는 편이 낫다고 보면 착수 확정 때 교차 확인한다.

### 설계

| 언제 | 어디 |
|---|---|
| 한 게임만 쓴다 | 게임 폴더 (`Assets/<게임명>/Scripts/`) |
| 두 번째 게임이 같은 것을 요구한다 | 공용(`Assets/Scripts/`)으로 승격 + 두 게임이 같은 것을 쓰는지 확인 |
| 처음부터 명백히 범용 (확장 메서드 · 로더 인터페이스) | 공용 |
| 스킬 노드 골격 (노드 베이스 · 레지스트리 · 빌더 · 컨텍스트 · 수정자) | 공용 `Assets/Scripts/Skill/`. 첫 게임부터 [사람 확정]. 노드 어휘·실행 시스템은 게임 폴더 (`SkillSystem.md`) |

## Manager 와 Management

### 요약

- 두 갈래다. Manager 는 게임 로직, Management 는 UI 조종이다.
- 기본 분리다. 이유: 로직이 순수 C# 라 재생 없이 돈다 (「하네스 호환」).
- 호출 방향 그림을 어기면 되돌린다.

### 규칙

- 하위 UI 는 `GameManager` / `XxxManager` / `XxxManagement` 를 직접 부르지 않는 것이 기본이다.
- 하위 UI 의 데이터 조회는 정적 Helper(`ModeHelper` `CurrencyHelper` `UIFormat`)를 경유한다.
- 하위 UI 에서 위로 올릴 일은 `event` 로 올린다. 쓰기·상태 변경은 Management 가 받아 Manager 를 부른다.
- 어긋난 호출은 되돌리는 것이 기본이다. 다른 구조가 낫다고 보면 근거를 작업 분해 때 보여 교차 확인한다.

### 설계

| | Manager | Management |
|---|---|---|
| 하는 일 | 데이터 처리 · 게임 로직 | UI 열고 닫기 · 표기 갱신 |
| 형태 | 순수 C# (`BaseManager`) | `MonoBehaviour` (`BaseManagement`) |
| 소유 | `GameManager` | `GameInitialize` 가 만든 GameObject |
| 예 | `SaveManager` `StatManager` `CombatManager` | `LobbyManagement` `ShopManagement` |

```
Manager (게임 로직)  ←──→  Management (Window 조종)     ← 서로 호출 가능
      ↑ 직접 호출 금지            ↑ 직접 호출 금지
Window / Panel / Component  ──→  Helper (정적, 읽기 전용) 만 호출 가능
```

기본 그림이다. 이유: 쓰기·상태 변경이 Management 한 경로로 모여 추적되고, 하위 UI 는 표기만 한다.

```
ModeSelectPopup.OnModeSelected
   → LobbyManagement.HandleModeSelected
      → GameManager.Instance.Mode.SelectMode(...)
```

## 초기화

### 요약

- HTML5 원본은 전역 상태와 함수 뭉치다. 그대로 옮기면 초기화 순서가 `Awake` 경합에 맡겨져 회차마다 다른 버그가 난다.
- 기본은 Manager · Management 의 생성 순서를 `GameInitialize` 한 곳이 정하는 것이다.
- `GameManager` 하나가 `IGameUpdate` 목록을 돌린다. Manager 마다 Update 를 갖지 않는다.
- 골격과 코드는 [GameFramework - 초기화](GameFramework%20-%20초기화.md) 에 있다.

## 프로젝트 설정

### 요약

- 확정표를 프로젝트 설정에 반영한다.
- 확정표의 답이 프로젝트 설정에 안 들어가면 확정하지 않은 것과 같다. 에디터에서는 잘 돌아 아무도 모른다.
- 저장소에 게임이 여럿이면 빌드 직전에 그 게임 것을 적용한다.
- 반영 표와 검사는 [GameFramework - 프로젝트 설정](GameFramework%20-%20프로젝트%20설정.md) 에 있다.

## 하네스 호환

### 요약

- 하네스가 쓰는 코드는 재생 밖에서도 서야 한다.
- 정답지 대조·플로우 diff·에셋 감사는 재생 없이(편집 모드, 에디터 다리 또는 배치) 돈다.
- 프레임워크 골격에 재생 중에만 되는 호출이 하나라도 섞이면 하네스에서 그 코드를 못 쓰고, 그 계통은 수치로 판정되지 않는다.

### 규칙

- 판정은 이 클래스를 재생 없이 `new` 하거나 만들 수 있나다. 못 하면 가드를 넣는 것이 기본이다. 이유: 재생에 의존하지 않는 것이 원래 맞는 설계이고, 그래야 하네스가 그 계통을 수치로 판정한다.

### 설계

| 재생 중에만 되는 것 | 대응 |
|---|---|
| 씬 전환에도 살아남게 하는 호출 | 재생 중일 때만 부른다 (`Application.isPlaying` 가드) |
| 코루틴 | 하네스 경로에서 안 쓰거나 동기 경로를 따로 둔다 |
| 프레임 대기 · 물리 스텝 | 틱 함수를 직접 부를 수 있게 만든다 |
| 비동기 로더 | 텍스트를 직접 넣는 우회 경로를 같이 만든다 (`DataFramework` 「DataManager」) |

사례: 싱글턴 베이스가 생성 직후 「씬 전환에도 유지」를 무조건 불러, 편집 모드에서 예외가 나 하네스가 첫 줄에서 죽었다.

## `GameFlow`

### 요약

- 화면 전이를 여기 하나로 모으는 것이 기본이다.
- 원본의 `setScreen` 에 해당한다.
- 이유: Management 마다 흩어지면 없어야 할 창이 생겨도 못 본다 (PD 「플로우 diff 를 프리팹 대조보다 먼저」).

### 규칙

- #강제 [원칙 R1](원칙.md#R1) 전이 표는 `01_게임플로우.md`(학습 산출물) 그대로 만든다. 원본에 없는 전이를 넣지 않는다.

### 설계

```csharp
public class GameFlow
{
    public GameScreenType Current { get; private set; }
    public event Action<GameScreenType, GameScreenType> OnScreenChanged;

    public void ChangeScreen(GameScreenType next)
    {
        if (Current == next) return;
        var prev = Current;
        Current = next;
        OnScreenChanged?.Invoke(prev, next);      // 각 Management 가 구독해 자기 창을 열고 닫는다
    }
}
```

## 완료 체크리스트

### 요약

- 기본 구조 기준 점검이다.
- 다른 구조를 골랐으면 확정표의 선택으로 바꿔 본다.

### 규칙

- [ ] Manager · Management 중 `Awake` 자기초기화가 0개다 (생성은 `GameInitialize` 만)
- [ ] Manager 초기화가 Management 보다 먼저 끝난다
- [ ] Manager 마다 `Update` 를 갖지 않고 `IGameUpdate` 목록 하나가 돈다
- [ ] #강제 [원칙 R1](원칙.md#R1) 원본 메인 루프의 정지 게이트·dt 클램프가 옮겨졌고 원본 라인이 주석에 있다
- [ ] 하위 UI 가 Manager/Management 를 직접 부르지 않는다 (Helper + event 만)
- [ ] 화면 전이가 `GameFlow` 한 곳을 지난다
- [ ] #강제 [원칙 R1](원칙.md#R1) 첫 화면 전이 순서가 원본과 같다 (빈 화면 프레임이 없다)
