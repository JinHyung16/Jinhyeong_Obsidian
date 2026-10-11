---
분류: 규약
성격: 방향
tags:
  - htmltounity
---

# DataFramework

시트에서 JSON 으로, JSON 에서 Container 로 간다.

## 노트 자리

### 요약

- 방향 노트다. 기본값과 이유를 준다. 판단 대상이 아닌 것은 [원칙](원칙.md) 에만 있다.
- 상위는 [PD](PD.md) 다. 사용자는 [Transfer_Programmer](Transfer_Programmer.md) 다.
- HTML5 원본의 JS 상수·테이블을 게임이 읽는 데이터로 만드는 기본 설계다.
- 하위 노트는 [JSON 라이브러리](DataFramework%20-%20JSON%20라이브러리.md) · [시트 컨벤션](DataFramework%20-%20시트%20컨벤션.md) · [컨테이너](DataFramework%20-%20컨테이너.md) 셋이다.

### 규칙

- #강제 [원칙 R7](원칙.md#R7) 컨테이너로 조회가 성공해야 이관이다. 파일만 있는 것은 이관이 아니다.

## JSON 라이브러리

### 요약

- 전제는 JSON 역직렬화 수단 하나다. 라이브러리는 프로젝트가 고른다.
- 요구 능력 4가지가 수단을 고르는 조건이다.
- 주의: Unity 내장 `JsonUtility` 는 넷 다 안 되므로 못 쓴다.
- 요구 능력 · 선택지 · 접점 격리는 [DataFramework - JSON 라이브러리](DataFramework%20-%20JSON%20라이브러리.md) 에 있다.

## JSON 전용과 엑셀 승격

### 요약

- 확정표 9번의 기본값은 JSON 전용이다.
- 이유: 엑셀 파이프라인은 exporter · 코드젠 · 시트 규약까지 필요한데 원본 데이터는 대개 표 몇 개다.
- 밸런스 행이 수백을 넘거나 기획이 직접 만지면 엑셀 파이프라인이 낫다.
- 컨테이너 · `Validate` · `DataManager` · `GameRoot` 규약은 두 경로가 같다. 갈리는 것은 JSON 을 누가 만드느냐뿐이다.

### 규칙

- #강제 [원칙 R22](원칙.md#R22) 승격 후 JSON 은 엑셀에서만 고친다. 승격 전 JSON 전용 단계에서는 JSON 이 진실 소스라 손으로 고치는 것이 정상이다.
- #강제 [원칙 R7](원칙.md#R7) 행 수 어설션이 행 클래스 결함을 잡는 최소 증명이다. 컨테이너마다 건다.
- 예외: 공격·스킬·무기가 2종 이상인 조합형 데이터는 처음부터 JS 모듈 + 익스포터로 굽는 것이 기본값이다 [사람 확정 · 확정표 9-b]. 이유: 평면 JSON 으로 가면 스킬 1종 추가마다 C# 을 고친다. 평면 표(적 스탯 · 레벨 표 · 문구)는 그대로 JSON 전용이다 (`SkillSystem.md`).
- 이 기본값과 다르게 가는 편이 낫다고 보이면 선택지와 근거를 착수 확정 때 사람에게 보여 교차 확인한다 ([원칙](원칙.md) 「쓰는 법」).
- 주의: 승격은 되돌리기 어렵다. 손으로 고친 JSON 이 다음 export 에 날아간다. 기본은 승격 전에 「기획이 정말 직접 만지는가」를 사람에게 묻고, 답과 승격 시점을 원장에 적는 것이다. 묻지 않고 승격하는 편이 낫다고 보이면 그 근거를 착수 확정이나 작업 분해 때 사람에게 보여 교차 확인한다 ([원칙](원칙.md) 「쓰는 법」).

### 설계

| | JSON 전용 (기본) | 엑셀 파이프라인 (승격) |
|---|---|---|
| 진실 소스 | `Assets/<게임명>/Data/<테이블>.json` | 엑셀 → JSON 을 생성 |
| 행 클래스 · enum | 사람이 쓴다 | 코드젠 (enum 은 `_Enum` 시트) |
| `Generated/` 폴더 | 없음 | 있음 |
| 언제 | 테이블 수 한 자리 · 행 수 수십 | 밸런스 행이 수백을 넘거나, 기획이 직접 만진다 |

JSON 전용일 때 행 클래스는 손으로 쓰고 컨테이너 옆에 두는 것이 기본이다.

- `[JsonProperty]` 없이 컬럼명과 프로퍼티명을 같게 맞춘다. 이유: 속성도 라이브러리 접점이다 ([DataFramework - JSON 라이브러리](DataFramework%20-%20JSON%20라이브러리.md) 「접점 격리」).
- `IDataKey<T>` 의 `Key` 만 구현한다. 나머지는 순수 데이터다.
- setter 는 `public` 이 기본이다. 이유: `private set` 은 라이브러리에 따라 예외 없이 전 행이 기본값으로 들어온다.
- JSON 을 먼저 쓰고 클래스를 맞춘다. 이유: 반대면 원본과 대조할 기준이 사라진다.
- 원본 라인을 클래스 주석에 인용한다.

사례: `{ get; private set; }` 로 전 행이 `Id=0` · `null` 로 들어왔고 행 수 어설션(「행 수 1, 원본 6」)만 잡았다.

나중에 엑셀로 승격할 때는 JSON 에서 엑셀을 만든다. 반대가 아니다.

| # | 하는 일 |
|---|---|
| 1 | JSON 의 키·자료형으로 3행 헤더 시트를 만든다 (1행 컬럼명 · 2행 타입 · 3행~ 값) |
| 2 | 타입은 JSON 값에서 추론하고, `null` 이 한 번도 없는 컬럼에 `!` 를 붙인다 |
| 3 | 컬럼명이 「시트 컨벤션」과 다르면 그때 고친다 (`~Id` → `~Code`, enum 접미 등) |
| 4 | 그 시점부터 진실 소스는 엑셀이다. JSON 은 생성물이 된다 |
| 5 | 승격 시점과 대상 테이블을 원장에 적는다 |

JSON 전용 단계에서도 컬럼명·자료형 규칙(`Id` 는 `int`, 참조는 `~Code`, 판별 어휘는 enum, PascalCase)을 미리 맞춰 두는 것이 기본이다. 이유: 승격 3번에서 고칠 것이 줄어든다.

## 폴더 · 파이프라인

### 요약

- 아래는 엑셀 승격 후의 모양이다.
- JSON 전용이면 `Generated/` 가 없고 행 클래스가 컨테이너 옆에 있다.
- 기본은 두 출력을 나누는 것이다. 기획의 exporter 는 JSON 만, C# 코드젠은 Unity 메뉴가 같은 엑셀을 읽어 낸다.

### 규칙

- #강제 [원칙 R15](원칙.md#R15) 폴더는 `CLAUDE.md` 「폴더 규칙」이 우선한다.
- 생성 코드를 기획이 올리면 개발 영역 경계가 무너진다. 그래서 C# 코드젠은 Unity 메뉴(`Tools/GameData/Generate Code`, Ctrl+G)가 낸다.
- 유일한 JSON 예외는 `_Enum.json` 이다. 런타임 소비처가 없는 enum 코드젠 입력이라 Ctrl+G 쪽도 갱신하고, 이어서 enum 제너레이터가 `GameEnum.cs` 를 낸다.
- 등록과 접근 프로퍼티는 코드젠이 아니다. 컨테이너를 만든 사람이 `<게임>ContainerRegister.cs` 와 `GameRoot.<게임>.cs` 에 한 줄씩 손으로 추가한다.

### 설계

```
Assets/Scripts/Data/            공용 (한 번 만들고 안 건드린다)
├─ IData.cs  IDataKey.cs  IDataContainer.cs  JsonSettings.cs
├─ DataContainer.cs             로드 골격 + Sub 훅
├─ DictionaryContainer.cs       <Key, Value>
├─ DictionaryGroupContainer.cs  <Key, List<Value>>          (아직 없음 — 필요한 게임이 만든다)
├─ SingleContainer.cs           행 하나짜리 설정 테이블 (`Data`) (아직 없음)
├─ ListContainer.cs             평면 리스트                   (아직 없음)
├─ DataManager.cs               로드 · 검증
└─ GameRoot.cs                  partial

Assets/<게임명>/Scripts/Data/
├─ Generated/                   자동 생성. 시트·생성기에서 고친다
│   ├─ <테이블>Data.cs           행 클래스
│   └─ Containers.Generated.cs  추상 베이스 3종 x 테이블 수
├─ <테이블>DataContainer.cs      사람이 쓴다. 쓰는 테이블만
├─ <게임>ContainerRegister.cs    등록 목록. 사람이 쓴다
├─ GameRoot.<게임>.cs            접근 프로퍼티. 사람이 쓴다
└─ GameEnum.cs                  자동 생성 — public enum 나열뿐, 래퍼 클래스 없음

시트(엑셀/스프레드시트)
  -> exporter (기획)          -> Assets/<게임명>/Data/<테이블>.json   (런타임이 읽는 것)
  -> Unity Ctrl+G (개발)      -> Assets/<게임명>/Scripts/Data/Generated/
```

## 시트로 옮길 값

### 요약

- 시트를 만들기 전에, 원본 상수를 전부 옮기지 않는다.
- 원본 JS 의 배치 좌표 · 프레임 번호 · 트림 박스 · 프레임 개수를 시트로 옮기면 프리팹 · AnimationClip · 스프라이트 임포터 · 앵커의 몫을 표가 덮는다.
- 화면은 정상이라 파리티 검증에도 안 걸린다.
- 가르는 질문은 「이 값을 누가 눈으로 맞추나」다. 아트면 프리팹, 기획이면 시트, 아무도 안 맞추면 코드다.

### 규칙

- #강제 [원칙 R3](원칙.md#R3) 컬럼은 `03_데이터.md` 의 원본 근거로 만든다. 기억은 근거가 아니다.
- 원본이 JS 상수였다는 사실은 답이 아니다. 그대로 코드에 두는 것도 이관이 아니다.
- 이 구분은 사람이 고른 설계 기본값(프리팹이 주인)을 따른다. 다르게 가르는 편이 낫다고 보이면 착수 확정 때 교차 확인한다.
- 주의: 기본은 시뮬 길이 단위는 코드, 개체 크기는 데이터·프리팹으로 나누는 것이다. 이유: 둘을 섞어 개체가 크거나 빠르게 보일 때 뷰 배율로 덮으면 충돌 반경은 그대로라 판정과 그림이 갈린다. 단위부터 본다.

### 설계

| 원본 상수의 성격 | 유니티에서 담당 | 시트로 |
|---|---|---|
| 요소의 위치·크기 (정규화든 절대든) | 프리팹 + 앵커 (정규화 −1~1 좌표는 앵커 그 자체) | 아니오 |
| 프레임 접두어·시작 번호·개수·fps·loop | 재생 계층. 다수 풀링 개체는 중앙 틱, 단발·복합 트랙은 AnimationClip ([SKILL - 잘못 옮긴 것](SKILL%20-%20잘못%20옮긴%20것.md) 「재생 계층」) | 아니오 (fps 는 그 계층 설정) |
| 스프라이트 시트 크롭 / 여백 트림 박스 | 스프라이트 임포터 · 아틀라스 패커 | 아니오 |
| 폴더의 파일 개수 | 파일이 진실 | 아니오 (같은 사실이 두 곳에 생긴다) |
| 판별 어휘 (모드·난이도·종류) | enum | 값이 아니라 타입으로 |
| 아트 주소 | 컬럼 | 예 `~Path` |
| 기획이 정하는 배정·밸런스·확률·문구 | 표 | 예 |
| 좌표계 단위 기준 (시뮬이 쓰는 길이 단위 자체) | 코드 `const` (바꾸면 다른 상수 전부가 틀어진다) | 아니오 |

옮기다 만 방향은 두 갈래다. 반대편인 코드 `const` 로 남은 것은 시트에도 프리팹에도 안 보여 더 늦게 발견된다. 기본은 착수 시 세고 표로 만드는 것이다 ([SKILL - 잘못 옮긴 것](SKILL%20-%20잘못%20옮긴%20것.md) 「코드에 남은 상수」).

착수 전에 센다.

1. 새 표의 행 수가 상위 표와 같은가. 같으면 컬럼(배열 포함)으로 접는 것이 기본이다. 실질 컬럼 1개짜리 표는 대개 상위 표의 컬럼이다.
2. 같은 값이 프리팹에도 있는가. 거동 컬럼(속도·주기·시차)은 전수로 센다. 두 곳에 있으면 화면마다 읽는 쪽이 갈린다.
3. 개수 컬럼이 파일 개수와 같은가. 같으면 중복이다.

사고 기록은 [함정 색인](함정%20색인.md) 이다.

원본 HTML5 에서 시트를 설계할 때의 출처는 `03_데이터.md` 다. 학습 단계 산출물(PD 「산출물 목록」)의 `03_데이터.md` 에 적힌 원본 JS 객체의 키·자료형·행 수가 시트 설계도다.

```bash
# 원본 JS 객체의 키 수를 세어 시트 행 수와 맞춘다
node -e "const M=require('./scripts/data/gamedata.js'); console.log(Object.keys(M.SHOP).length)"
```

## 시트 컨벤션

### 요약

- 엑셀로 승격한 뒤의 규약이다.
- 시트는 3행 헤더다. 1행 컬럼명 · 2행 타입 · 3행부터 값이다.
- 기본 컨벤션이다. 프로젝트 컨벤션이 따로 있으면 그쪽이 이긴다.
- 컬럼 규칙 · 배열 · enum 시트는 [DataFramework - 시트 컨벤션](DataFramework%20-%20시트%20컨벤션.md) 에 있다.

## 컨테이너

### 요약

- 컨테이너는 베이스 · 자동 생성물 · 사람이 쓰는 콘크리트 셋으로 나뉜다.
- `DataContainer` 가 로드 골격이고 Sub 훅이 그 외 컬럼 인덱스를 만든다.
- 검증 함수는 컨테이너에 같이 넣는다.
- 인터페이스 · 코드 · 검증은 [DataFramework - 컨테이너](DataFramework%20-%20컨테이너.md) 에 있다.

## DataManager

### 요약

- `DataManager` 가 발견 · 로드 · 검증을 한다.
- 라벨 하나로 게임 폴더 `Data/` 의 JSON 을 전부 읽는다.
- 기본은 리플렉션 스캔 대신 사람이 쓴 등록 목록이다.

### 규칙

- 등록 목록을 사람이 들고 있어야 무엇이 로드되는지 파일 하나로 보인다. 스캔은 안 쓰는 컨테이너까지 만들고 로드 순서를 숨긴다.
- JSON 매칭 키는 `IDataContainer.Name` 이다. JSON 파일명에서 확장자를 뺀 것이다.
- `InitializeFromJson` 을 같이 만드는 것이 기본이다. 이유: 재생해야만 도는 데이터는 정답지 채점·헤드리스 검증에 못 쓴다 (Client 「ⓕ 하네스는 사용자 세이브를 건드릴 수 없어야 한다」).

### 설계

```csharp
public class DataManager
{
    public const string GameDataLabel = "game_data";   // 게임 폴더 Data/ JSON 의 어드레서블 라벨

    public async Task InitializeAsync(CancellationToken ct = default)
    {
        RegisterContainers();                                   // ContainerRegister 의 손으로 쓴 목록
        var jsonByName = await LoadJsonTextByNameAsync(ct);      // 라벨 하나로 전 JSON 로드
        foreach (var kv in _containers) { LoadOne(kv.Key, kv.Value, jsonByName); await Task.Yield(); }
        ValidateAll();              // Validate 전부
        AfterAllLoaded();           // AfterAllTableLoaded 전부
        _initialized = true;
    }

    /// 에디터 검증 하네스 전용 — 어드레서블·Play 없이 JSON 텍스트를 직접 넣는다
    public void InitializeFromJson(IReadOnlyDictionary<string, string> jsonByName) { … }

    public void Register<T>(T container) where T : DataContainer { _containers[typeof(T)] = container; }

    public T GetContainer<T>() where T : class, IDataContainer { … }
}
```

## GameRoot

### 요약

- 접근은 `GameRoot` 하나로 한다.
- 기본 창구는 GameRoot 프로퍼티다.
- 이유: 게임별 접근이 `GameRoot.<게임>.cs` 한 곳에 도메인 묶음으로 모인다.

### 규칙

- `DataManager.Instance.GetContainer<T>()` 직접 호출은 그 목록을 우회한다.

### 설계

```csharp
var mode  = GameRoot.Instance.ModeDataContainer.Get(StageLevelType.Normal);          // enum 키 단건
var parts = GameRoot.Instance.UnitPartDataContainer.GetGroup("unit_code");           // Code 묶음
var theme = GameRoot.Instance.StageThemeDataContainer.Get(0);                        // int Id
var all   = GameRoot.Instance.CurrencyDataContainer.AllValues;
```

```csharp
// GameRoot.cs (공용 partial) — 게임별 프로퍼티는 GameRoot.<게임>.cs 에 도메인 묶음으로 쓴다
public sealed partial class GameRoot
{
    public static GameRoot Instance => _instance ??= new GameRoot();

    public ModeDataContainer ModeDataContainer => GetContainer<ModeDataContainer>();
    public ModeBgDataContainer ModeBgDataContainer => GetContainer<ModeBgDataContainer>();

    private static GameRoot _instance;
    private GameRoot() { }
    private T GetContainer<T>() where T : class, IDataContainer => DataManager.Instance.GetContainer<T>();
}
```

## 함정

### 요약

- JSON·클래스가 다 있어도 등록이 빠지면 안 읽는다. 에러도 없다.
- 자동 생성물을 직접 고치면 다음 생성에 날아간다.

### 설계

| 함정 | 증상 | 대응 |
|---|---|---|
| 콘크리트 컨테이너 미작성 · `ContainerRegister` 등록 누락 | JSON·클래스가 다 있는데 안 읽는다. 에러도 없다 | 새 테이블은 `AllValues.Count` 를 찍어 확인 |
| Generated 직접 수정 | exporter 재실행에 날아간다 | 시트나 exporter 를 고친다 |
| 헤드리스 하네스에서 컨테이너 null | `GameRoot.Instance.XxxContainer` 가 null → 코드 폴백값으로 돈다 | `InitializeFromJson` 으로 직접 세운다 |
| `~Id` 라는 이름의 참조 컬럼 | int 로 오해해 잘못 조회한다 | `~Code` 로 바꾼다 |
| enum 이름 규칙 위반 | 파이프라인 경고 | 시트를 고친다. 생성 코드는 다음 생성에 덮인다 |
| 배열 표기 꼬리 오타 | 조용히 string 컬럼이 된다 | exporter 로그에서 타입 확인 |
| 계수를 코드에 하드코딩 | 밸런스가 시트 밖에 흩어진다 | `*ConfigData` 시트로 뺀다. 폴백값은 코드에 두고 주석에 원본 인용 |
