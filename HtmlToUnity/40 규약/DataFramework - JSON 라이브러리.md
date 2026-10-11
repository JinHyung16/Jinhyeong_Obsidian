---
분류: 규약
성격: 방향
tags:
  - htmltounity
---

# DataFramework - JSON 라이브러리

상위: [DataFramework](DataFramework.md)

JSON 역직렬화 수단은 하나만 두고 접점을 격리한다.

## 요구 능력

### 요약

- 요구 능력 4가지가 수단을 고르는 조건이다.
- 이게 안 되면 그 수단은 못 쓴다.
- 주의: Unity 내장 `JsonUtility` 는 넷 다 안 되므로 못 쓴다.

### 설계

| 능력 | 왜 필요한가 |
|---|---|
| 최상위 배열 `[{...},{...}]` | 테이블 JSON 이 전부 이 모양이다 |
| 임의 키 맵 (`Dictionary<string, …>`) | 정답지가 임의 키 수백 개짜리 맵이다 |
| `null` 과 기본값 구분 | 「값이 없다」와 「0이다」가 같아지면 폴백 계수 판정이 무너진다 |
| 중첩 제네릭 (`List<T>` 안의 객체) | 1:N 시트를 묶어 담는다 |

## 선택지

### 요약

- 라이브러리는 프로젝트가 고른다.
- 기본은 UPM JSON 패키지다.
- 기본은 PD 착수 확정(PD 「확정표」)의 「전제」 행에 무엇을 쓸지 적고 시작하는 것이다. 이유: 늦으면 컨테이너 수십 개에 라이브러리가 스며든다.

### 설계

| 선택지 | 언제 | 비용 |
|---|---|---|
| UPM JSON 패키지 (예: `com.unity.nuget.newtonsoft-json`) | 기본. 특별한 사정이 없으면 | Package Manager → Add package by name |
| 이미 쓰고 있는 다른 라이브러리 | 이미 있으면 그쪽이 낫다. 이유: 새로 깔면 접점이 둘로 갈린다 | 「접점 격리」 대로 접점만 맞춘다 |
| 직접 짠 최소 파서 | 외부 의존을 넣을 수 없을 때 | 비권장. 쓰면 요구 능력 4가지를 테스트로 먼저 고정한다 |

## 접점 격리

### 요약

- 접점을 한 곳으로 격리한다. 이게 핵심이다.
- 기본은 라이브러리 이름이 `JsonSettings.cs`(설정)와 `DataContainer.Deserialize`(호출) 두 곳에만 나오는 것이다.
- 세 파일 이상이면 격리가 깨진 신호다.
- 이유: 격리돼 있으면 라이브러리 교체가 파일 1개 수정이다. 안 돼 있으면 컨테이너 수십 개의 `using` 과 전 파일의 `[JsonProperty]` 를 걷어내야 한다.

### 규칙

- 행 클래스 속성도 접점이다. 생성기가 `[JsonProperty("Id")]` 를 찍으면 속성 이름을 생성기 설정 한 곳에서 바꿀 수 있게 두는 것이 기본이다.
- 컬럼명과 프로퍼티명이 같으면 대개 속성이 필요 없다.

### 설계

```csharp
// JsonSettings.cs — 설정
namespace JinHyung.Data
{
    public static class JsonSettings
    {
        public static readonly JsonSerializerSettings Default = new JsonSerializerSettings { /* … */ };
    }
}
```

```csharp
// DataContainer.cs — 라이브러리 호출은 이 한 곳뿐이다
protected List<TValue> Deserialize(string text)
    => string.IsNullOrEmpty(text)
        ? null
        : JsonConvert.DeserializeObject<List<TValue>>(text, JsonSettings.Default);
```

## 어셈블리 참조

### 요약

- `.asmdef` 를 쓰는 프로젝트만 해당한다.
- 어셈블리를 나눴다면 참조를 추가한다.
- 판정 기본은 `dotnet build` 다. 이유: 에디터 콘솔은 변경을 아직 안 집어갔을 수 있다 (공통절차 「컴파일·툴 실행 순서」 ⓪-b).

### 설계

| 증상 | 원인 |
|---|---|
| 한 어셈블리에서만 `CS0246` | 그 `.asmdef` 참조 목록에 JSON 라이브러리가 빠졌다 |
| 에디터 전용 코드에서만 실패 | Editor 어셈블리에도 따로 건다 |
