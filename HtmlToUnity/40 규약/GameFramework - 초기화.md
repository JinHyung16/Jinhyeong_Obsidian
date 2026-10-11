---
분류: 규약
성격: 방향
tags:
  - htmltounity
---

# GameFramework - 초기화

상위: [GameFramework](GameFramework.md)

생성 순서를 한 파일에 모으고 Update 를 한 곳에서 돌린다.

## GameInitialize

### 요약

- `GameInitialize` 는 순서의 유일한 출처다.
- 기본은 Manager · Management 의 생성 순서를 `GameInitialize` 한 곳이 정하고, 둘은 `Awake` 에서 자기초기화하지 않는 것이다.
- 이유: 순서가 Unity 에 맡겨지면 Manager 가 없는 시점에 Management 가 깨어난다.

### 규칙

- 프리팹에 붙는 View·Visual·프레임워크 컴포넌트는 자기 `Awake` 로 자기 참조를 캐시해도 된다. 순서 의존이 아니다.

### 설계

```csharp
public class GameInitialize : MonoBehaviour
{
    [Header("Camera")]  [SerializeField] Camera _mainCamera;  [SerializeField] Camera _uiCamera;
    [Header("Root")]    [SerializeField] Transform _uiRoot, _objectRoot, _managerRoot, _managementRoot;
    [Header("Loading")] [SerializeField] LoadingWindow _loadingWindow;

    private async void Awake() => await InitAsync(_cts.Token);

    private async Task InitAsync(CancellationToken ct)
    {
        BindUIEnvironment();                                  // ① UI 루트·카메라를 WindowManagement 에 넘긴다
        await DataManager.Instance.InitializeAsync(ct);       // ② 데이터
        await LoadImmediateArtAsync(ct);                      // ③ 첫 화면 아트만 (프로바이더 이름은 프로젝트가 정한다)
        await WaitStartRequestedAsync();                      // ④ 시작 버튼·인트로 게이트 — 사람 입력을 기다린다
        CreateManagers();                                     // ⑤ 로직 (GameManager.Bootstrap)
        CreateManagements();                                  // ⑥ UI 조종자 (Manager 를 곧바로 읽는다)
        GameManager.Instance.GameFlow.ChangeScreen(GameScreenType.Lobby);   // ⑦ 첫 화면
        PreloadRemainingArt(ct);                              // ⑧ 나머지 아트는 화면을 띄운 뒤 (await 하지 않는다)
    }
}
```

## 초기화 순서

### 요약

- 순서가 규약이다. 어기면 나는 증상이 정해져 있다.
- 생성 순서가 곧 초기화 순서다. 헬퍼가 그 유일한 출처다.

### 규칙

- #강제 [원칙 R1](원칙.md#R1) 화면 전이 순서는 원본이 「A 를 띄운 뒤 B 를 걷는다」면 그대로다. 뒤집으면 빈 화면 프레임이 스친다.

### 설계

| 순서 | 어기면 |
|---|---|
| 데이터 → Manager | Manager 가 폴백값으로 초기화되고 그 값이 세이브에 굳는다 |
| Manager → Management | Management 가 `Initialize` 에서 Manager 를 읽다 NRE |
| 첫 화면 → 나머지 아트 | 로딩이 길어진다. 원본도 지연 로드다 |

```csharp
private void CreateManagers()
{
    GameManager.Instance.transform.SetParent(_managerRoot);
    GameManager.Instance.Bootstrap();          // 등록 + Initialize 순서까지 여기서
}

private void CreateManagements()
{
    AddManagement<LobbyManagement>();
    AddManagement<ShopManagement>();
    // 생성 순서 = 초기화 순서. 여기가 유일한 출처다
}

private T AddManagement<T>() where T : BaseManagement
{
    var go = new GameObject(typeof(T).Name);
    go.transform.SetParent(_managementRoot);
    T m = go.AddComponent<T>();
    m.Initialize();            // Awake 가 아니라 여기서 명시적으로
    return m;
}
```

## `BaseManager`

### 요약

- Manager 베이스는 순수 C# 이다.
- `Initialize` 와 `Dispose` 가 중복 호출을 막는다.
- Update 가 필요한 Manager 만 `IGameUpdate` 를 구현한다.

### 설계

```csharp
public abstract class BaseManager
{
    public bool IsInitialized { get; private set; }
    public void Initialize() { if (IsInitialized) return; OnInitialize(); IsInitialized = true; }
    public void Dispose()    { if (!IsInitialized) return; OnDispose();   IsInitialized = false; }
    protected virtual void OnInitialize() { }
    protected virtual void OnDispose() { }
}

public interface IGameUpdate
{
    void OnUpdate(float deltaTime);
    void OnFixedUpdate(float fixedDeltaTime);
}
```

## `GameManager`

### 요약

- `GameManager` 가 Manager 를 소유하고 등록 순서가 의존 순서다.
- Update 를 Manager 마다 갖지 않는다. `GameManager` 하나가 `IGameUpdate` 목록을 돌린다.
- 이유: Manager 마다 MonoBehaviour 를 붙이면 호출 순서가 Unity 에 넘어가 원본의 「한 루프 안에서 이 순서로」가 깨진다.

### 규칙

- 매니저 프로퍼티는 전부 `~Mgr` 접미다.
- dt 클램프는 루프를 돌리는 쪽 한 곳(`GameManager` 상수)에 두는 것이 기본이다. 이유: 두 곳에 있으면 한쪽이 낡는다.

### 설계

```csharp
public class GameManager : MonoSingleton<GameManager>
{
    private const float MaxDeltaTime = 0.033f;   // 원본 dt 클램프와 같은 값 — 클램프는 여기 한 곳

    public GameFlow GameFlow { get; private set; }
    public SaveManager SaveMgr { get; private set; }
    public StatManager StatMgr { get; private set; }
    public CombatManager CombatMgr { get; private set; }
    // 매니저 프로퍼티는 전부 ~Mgr 접미

    private List<BaseManager> _managers = new List<BaseManager>(16);
    private List<IGameUpdate> _updatables = new List<IGameUpdate>(8);

    public void Bootstrap()
    {
        if (IsBootstrapped) return;
        GameFlow = new GameFlow();

        SaveMgr   = Register(new SaveManager());     // 등록 순서 = 의존 순서
        StatMgr   = Register(new StatManager());
        CombatMgr = Register(new CombatManager());

        for (int i = 0; i < _managers.Count; i++) { _managers[i].Initialize(); }
        IsBootstrapped = true;
    }

    private T Register<T>(T m) where T : BaseManager
    {
        _managers.Add(m);
        if (m is IGameUpdate u) { _updatables.Add(u); }
        return m;
    }

    private void Update()
    {
        if (!IsBootstrapped) return;
        float dt = Time.deltaTime;
        for (int i = 0; i < _updatables.Count; i++) { _updatables[i].OnUpdate(dt); }
    }
}
```

## 메인 루프 게이트

### 요약

- 원본 메인 루프의 게이트 조건을 한 줄씩 옮긴다.
- 원본 `_loopBody` 에는 대개 정지 조건이 섞여 있다.
- 함수 단위로 이식하면 이 `if` 가 사라진다.

### 규칙

- #강제 [원칙 R1](원칙.md#R1) 원본 루프의 정지 게이트 · dt 클램프 값은 빠짐없이 옮긴다.
- 기본 자리는 `IGameUpdate` 진입부다. 정지 게이트·시드 고정을 그대로 옮긴다.

### 설계

```js
// 원본 예 — 모달이 열려 있으면 시뮬 자체가 멈춘다
if (modalOpen) return;
dt = Math.min(dt, 0.033);
```
