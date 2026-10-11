---
분류: UI
성격: 독스
tags:
  - devunreal
  - UI
---

# 독스 - 언리얼 UI 구조

언리얼 UI 가 어떤 층으로 되어 있고, 언제 위젯을 쌓고 언제 직접 그리는지 정리한다. 새 화면을 만들 때 편다.

## 핵심 아이디어

### 층이 둘이다

| 층 | 무엇 | 언어 |
|---|---|---|
| Slate | 실제로 그리고 입력을 받는 층 | C++ 만 |
| UMG | Slate 를 에디터에서 조립하게 만든 껍데기 | 블루프린트와 C++ |

위젯 블루프린트로 버튼을 놓으면, 그 버튼은 안에서 Slate 버튼 하나를 만든다. UMG 는 Slate 를 감싼 것이다.

그래서 UMG 위젯 안에서 Slate 를 직접 쓸 수 있다. `NativePaint` 를 덮어쓰면 그 자리에 무엇이든 그린다.

### 쌓을 것인가 그릴 것인가

칸 하나에 위젯 하나를 두는 방식과, 위젯 하나가 전부를 그리는 방식이 있다.

| | 위젯을 쌓는다 | 직접 그린다 |
|---|---|---|
| 만들기 | 에디터에서 눈으로 | 코드로만 |
| 칸이 10개 | 편하다 | 굳이 |
| 칸이 500개 | 그리기 호출이 500번. 이동할 때마다 배치를 다시 잰다 | 호출이 몇 번이다 |
| 배치 규칙이 데이터에 있다 | 매번 스폰하고 지워야 한다 | 좌표만 바꿔 그린다 |
| 애니메이션, 버튼, 입력 | 공짜로 붙는다 | 직접 만든다 |

기준은 개수와 출처다. 개수가 수백이고 배치가 데이터에서 오면 직접 그린다. 그 외에는 쌓는다.

스킬 트리는 노드 81개에 배치가 표에서 온다. 그래서 직접 그린다.

### 좌표를 세 층으로 나눈다

직접 그릴 때 제일 먼저 정할 것이다. 섞으면 창 크기가 바뀔 때마다 값이 틀어진다.

| 층 | 단위 | 누가 정하나 |
|---|---|---|
| 칸 | 정수 | 사람이 표에 적는다 |
| 월드 | 실수 | 칸 x 칸크기 |
| 화면 | 픽셀 | 줌과 이동이 만든다 |

변환 함수는 두 개고 서로의 역함수여야 한다. 한쪽만 고치면 조용히 어긋난다.

```
픽셀당칸 = 칸크기 x 줌

화면 = 가운데 + (칸 - 이동) x 픽셀당칸      y 는 부호 반대
칸   = 이동 + (화면 - 가운데) / 픽셀당칸     y 는 부호 반대
```

칸과 월드는 위가 플러스고 화면은 아래가 플러스다. 뒤집기는 변환 함수 안에서 정확히 한 번 한다. 빠뜨리면 위아래가 뒤집히고, 두 번 하면 안 한 것과 같다.

### 칸크기와 노드크기를 나눈다

```
노드 사이 간격 = 칸크기
노드 자체 크기 = 노드기본크기 x 노드별배율
```

둘을 하나로 합치면 칸크기를 바꿔도 전부 같은 비율로 커진다. 줌을 만진 것과 구별이 안 되고 화면에 아무 변화가 없다.

나눠 두면 칸크기를 키울 때 노드는 그대로고 간격만 벌어진다.

### 줌은 곱셈이고 지수로 건다

휠 한 칸이 배율 한 번이 되려면 지수여야 한다.

| 식 | 올렸다 내리면 |
|---|---|
| `zoom + step` | 확대할수록 한 칸의 체감이 달라진다 |
| `zoom x (1 + step)` | `1 - step^2` 배. 왕복마다 조금씩 줄어든다 |
| `zoom x exp(step)` | 정확히 제자리다 |

`step` 이 0.06 이면 두 번째 식은 왕복 한 번에 0.36% 씩 어긋난다. 열 번 왕복하면 3.5% 다.

### 커서 아래를 고정한 확대

휠을 굴려도 커서 아래 있던 지점이 안 움직여야 한다. 안 그러면 확대할 때마다 화면이 미끄러진다.

```cpp
const FVector2D Before = LocalToCell(Mouse, CanvasSize);
Zoom = 새 줌;
Pan += Before - LocalToCell(Mouse, CanvasSize);
```

줌이 부드럽게 따라가는 구조라면 보정을 한 번만 하면 안 된다. 따라가는 동안 매 프레임 다시 고정한다. 그게 확대가 어색하다의 정체다.

### 감쇠는 프레임률과 무관해야 한다

```cpp
Zoom = FMath::Lerp(Zoom, Target, 1.0f - FMath::Exp(-Rate * DeltaTime));
```

`Lerp(x, target, 0.2f)` 처럼 계수를 고정하면 60fps 와 120fps 에서 속도가 두 배 다르다.

## 구조

### UUserWidget 수명

| 함수 | 언제 |
|---|---|
| `NativeConstruct` | 화면에 올라갈 때. 델리게이트를 여기서 건다 |
| `NativeTick` | 매 프레임. 크기를 여기서 안다 |
| `NativePaint` | 그릴 때. `const` 라 상태를 못 바꾼다 |
| `NativeDestruct` | 내려갈 때. 걸어 둔 델리게이트를 푼다 |

`NativeConstruct` 에서는 화면 크기를 모른다. 0 이거나 기본값이다. 크기가 필요한 일은 첫 `NativeTick` 까지 미룬다.

### 그리기 세 가지

```cpp
FSlateDrawElement::MakeBox(Elements, Layer, Geometry.ToPaintGeometry(Size, Transform),
    Brush, ESlateDrawEffect::None, Color);

FSlateDrawElement::MakeLines(Elements, Layer, Geometry.ToPaintGeometry(),
    Points, ESlateDrawEffect::None, Color, true, Thickness);

FSlateDrawElement::MakeText(Elements, Layer, Geometry.ToPaintGeometry(Size, Transform),
    Text, Font, ESlateDrawEffect::None, Color);
```

상자는 브러시가 필요하다. 스타일 세트를 끌어오지 않고 흰 브러시 하나를 만들어 색만 바꾸는 쪽이 간단하다.

```cpp
static const FSlateColorBrush Brush(FLinearColor::White);
```

### 레이어

레이어 번호가 앞뒤 순서다. 같은 번호 안에서는 순서가 보장되지 않는다. 겹쳐야 하는 것은 번호를 따로 준다.

```
배경 - 격자 - 간선 - 노드 - 글자 - 툴팁
```

### 글자 크기

상자를 먼저 정하고 글자를 상자에 맞춘다. 반대로 하면 글자 길이에 따라 상자 크기가 들쭉날쭉해진다.

```cpp
Font.Size = FMath::Clamp(FMath::RoundToInt(BoxHeight * 0.42f), 6, 18);
```

재는 것은 측정 서비스다.

```cpp
FSlateApplication::Get().GetRenderer()->GetFontMeasureService()->Measure(Text, Font);
```

상자가 작으면 글자를 아예 안 그린다. 어차피 못 읽는데 재는 비용은 노드 수만큼 든다.

### 입력

| 함수 | 받는 것 |
|---|---|
| `NativeOnMouseButtonDown` | 누름 |
| `NativeOnMouseButtonUp` | 뗌 |
| `NativeOnMouseMove` | 움직임 |
| `NativeOnMouseWheel` | 휠 |
| `NativeOnMouseLeave` | 벗어남 |

`FReply::Handled()` 를 돌려주면 내가 먹었다는 뜻이다. `Unhandled` 면 부모로 올라간다.

끌기는 마우스를 잡아야 한다. 안 잡으면 위젯 밖으로 나가는 순간 움직임이 안 온다.

```cpp
return FReply::Handled().CaptureMouse(TakeWidget());
return FReply::Handled().ReleaseMouseCapture();
```

화면 이동은 왼쪽 버튼에 두지 않는다. 왼쪽은 고르기에 써야 한다.

### 화면 좌표를 위젯 좌표로

마우스 위치는 화면 기준으로 온다. 위젯 기준으로 바꿔야 쓴다.

```cpp
const FVector2D Local = FVector2D(InGeometry.AbsoluteToLocal(InMouseEvent.GetScreenSpacePosition()));
```

### 한글

기본 폰트 Roboto 에는 한글 글자가 없다. Slate 가 없는 글자를 `DroidSansFallback` 으로 대신 찾아 주기 때문에 그냥 나온다. 폰트를 직접 지정할 때만 한글이 든 파일인지 본다.

```cpp
LabelFont = FCoreStyle::GetDefaultFontStyle("Regular", 10);
```

## 전체 코드

<!-- code: Source/RollBall/UI/RollBallSkillGraphWidget.h -->
<details>
<summary>RollBallSkillGraphWidget.h (166줄)</summary>

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "RollBall/Skill/RollBallSkillTypes.h"
#include "RollBallSkillGraphWidget.generated.h"

class URollBallSkillGraph;
class URollBallGameInstance;

UCLASS()
class ROLLBALL_API URollBallSkillGraphWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	URollBallSkillGraphWidget(const FObjectInitializer& ObjectInitializer);

	UFUNCTION(BlueprintCallable, Category = "RollBall|Skill")
	void SetGraph(URollBallSkillGraph* InGraph);

	UFUNCTION(BlueprintCallable, Category = "RollBall|Skill")
	void FrameAll();

	UFUNCTION(BlueprintImplementableEvent, Category = "RollBall|Skill")
	void OnPurchaseRefused(const FText& Reason);

	UFUNCTION(BlueprintImplementableEvent, Category = "RollBall|Skill")
	void OnPurchased(int32 NodeIndex, int32 SpentGold);

protected:
	virtual void NativeConstruct() override;
	virtual void NativeDestruct() override;
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

	virtual int32 NativePaint(const FPaintArgs& Args, const FGeometry& AllottedGeometry,
		const FSlateRect& MyCullingRect, FSlateWindowElementList& OutDrawElements,
		int32 LayerId, const FWidgetStyle& InWidgetStyle, bool bParentEnabled) const override;

	virtual FReply NativeOnMouseButtonDown(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent) override;
	virtual FReply NativeOnMouseButtonUp(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent) override;
	virtual FReply NativeOnMouseMove(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent) override;
	virtual FReply NativeOnMouseWheel(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent) override;
	virtual void NativeOnMouseLeave(const FPointerEvent& InMouseEvent) override;

	virtual FReply NativeOnKeyDown(const FGeometry& InGeometry, const FKeyEvent& InKeyEvent) override;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "격자", meta = (ClampMin = "8"))
	float CellSize = 56.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "격자", meta = (ClampMin = "4"))
	float NodeBaseSize = 34.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "격자", meta = (ClampMin = "0.05"))
	float MinZoom = 0.3f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "격자", meta = (ClampMin = "0.1"))
	float MaxZoom = 3.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "격자")
	float ZoomStep = 0.12f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "격자")
	float ZoomDampRate = 16.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "격자")
	float LabelMinPixelHeight = 16.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "격자")
	float GridMinPixelSpacing = 14.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "색")
	FLinearColor BackgroundColor = FLinearColor(0.043f, 0.047f, 0.063f, 1.0f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "색")
	FLinearColor GridColor = FLinearColor(1.0f, 1.0f, 1.0f, 0.045f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "색")
	FLinearColor EdgeColor = FLinearColor(0.32f, 0.36f, 0.45f, 1.0f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "색")
	FLinearColor EdgeOwnedColor = FLinearColor(0.55f, 0.95f, 0.62f, 1.0f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "색")
	FLinearColor EdgePathColor = FLinearColor(1.0f, 0.85f, 0.35f, 1.0f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "색")
	FLinearColor OwnedBorderColor = FLinearColor(0.42f, 1.0f, 0.5f, 1.0f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "색")
	FLinearColor BuyableBorderColor = FLinearColor(0.95f, 0.95f, 0.98f, 1.0f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "색")
	FLinearColor LockedBorderColor = FLinearColor(0.22f, 0.24f, 0.30f, 1.0f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "색")
	FLinearColor SelectedBorderColor = FLinearColor(1.0f, 0.85f, 0.35f, 1.0f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "색")
	FLinearColor TooltipBackColor = FLinearColor(0.02f, 0.02f, 0.03f, 0.94f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "색")
	FSlateFontInfo LabelFont;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "색")
	FSlateFontInfo TooltipFont;

private:
	UPROPERTY()
	TObjectPtr<URollBallSkillGraph> Graph = nullptr;

	FVector2D Pan = FVector2D::ZeroVector;

	float Zoom = 1.0f;
	float TargetZoom = 1.0f;

	FVector2D FocusLocal = FVector2D::ZeroVector;
	FVector2D FocusCell = FVector2D::ZeroVector;
	bool bFocusing = false;

	bool bPanning = false;
	FVector2D LastPanLocal = FVector2D::ZeroVector;

	FVector2D MouseLocal = FVector2D::ZeroVector;
	bool bMouseInside = false;

	int32 SelectedNodeIndex = INDEX_NONE;
	int32 HoveredNodeIndex = INDEX_NONE;

	TArray<int32> PendingPath;

	FVector2D LastCanvasSize = FVector2D(1024.0, 768.0);

	bool bPendingFrameAll = false;

	float PixelsPerCell() const { return CellSize * Zoom; }

	FVector2D CellToLocal(const FVector2D& Cell, const FVector2D& CanvasSize) const;
	FVector2D LocalToCell(const FVector2D& Local, const FVector2D& CanvasSize) const;

	FBox2D NodeBox(int32 NodeIndex, const FVector2D& CanvasSize) const;

	int32 HitTestNode(const FVector2D& Local, const FVector2D& CanvasSize) const;

	static bool ResolveBend(const FVector2D& A, const FVector2D& B, ERollBallEdgeRoute Route, FVector2D& OutBend);

	void PaintGrid(const FGeometry& Geometry, FSlateWindowElementList& Elements, int32 Layer) const;
	void PaintEdges(const FGeometry& Geometry, FSlateWindowElementList& Elements, int32 Layer) const;
	void PaintNodes(const FGeometry& Geometry, FSlateWindowElementList& Elements, int32 Layer) const;
	void PaintTooltip(const FGeometry& Geometry, FSlateWindowElementList& Elements, int32 Layer) const;

	FLinearColor BranchColorOf(ERollBallSkillBranch Branch) const;
	FLinearColor NodeFillColorOf(int32 NodeIndex) const;
	FLinearColor NodeBorderColorOf(int32 NodeIndex) const;

	void SelectNode(int32 NodeIndex);
	void AttemptPurchase(int32 NodeIndex);
	void RefreshPendingPath();

	URollBallGameInstance* GetRollBallGameInstance() const;
	int32 GetGold() const;
	int32 GetBestStage() const;

	UFUNCTION()
	void HandleGraphChanged();
};
```

</details>
<!-- /code -->

<!-- code: Source/RollBall/UI/RollBallSkillGraphWidget.cpp -->
<details>
<summary>RollBallSkillGraphWidget.cpp (677줄)</summary>

```cpp
#include "RollBallSkillGraphWidget.h"

#include "RollBallPaint.h"

#include "RollBall/Game/RollBallGameInstance.h"
#include "RollBall/Skill/RollBallSkillGraph.h"

#define LOCTEXT_NAMESPACE "RollBallSkill"

using namespace RollBallPaint;

URollBallSkillGraphWidget::URollBallSkillGraphWidget(const FObjectInitializer& ObjectInitializer)
	: Super(ObjectInitializer)
{
	LabelFont = FCoreStyle::GetDefaultFontStyle("Regular", 10);
	TooltipFont = FCoreStyle::GetDefaultFontStyle("Regular", 12);

	SetVisibility(ESlateVisibility::Visible);

	SetIsFocusable(true);
}

void URollBallSkillGraphWidget::NativeConstruct()
{
	Super::NativeConstruct();

	if (URollBallGameInstance* GameInstance = GetRollBallGameInstance())
	{
		SetGraph(GameInstance->EnsureSkillGraph());
	}

	SetKeyboardFocus();
}

void URollBallSkillGraphWidget::NativeDestruct()
{
	if (Graph != nullptr)
	{
		Graph->OnGraphChanged.RemoveDynamic(this, &URollBallSkillGraphWidget::HandleGraphChanged);
	}

	Super::NativeDestruct();
}

void URollBallSkillGraphWidget::SetGraph(URollBallSkillGraph* InGraph)
{
	if (Graph == InGraph)
	{
		return;
	}

	if (Graph != nullptr)
	{
		Graph->OnGraphChanged.RemoveDynamic(this, &URollBallSkillGraphWidget::HandleGraphChanged);
	}

	Graph = InGraph;
	SelectedNodeIndex = INDEX_NONE;
	HoveredNodeIndex = INDEX_NONE;
	PendingPath.Reset();

	if (Graph != nullptr)
	{
		Graph->OnGraphChanged.AddDynamic(this, &URollBallSkillGraphWidget::HandleGraphChanged);
		bPendingFrameAll = true;
	}
}

void URollBallSkillGraphWidget::HandleGraphChanged()
{
	RefreshPendingPath();
	Invalidate(EInvalidateWidgetReason::Paint);
}

FVector2D URollBallSkillGraphWidget::CellToLocal(const FVector2D& Cell, const FVector2D& CanvasSize) const
{
	const float Pixels = PixelsPerCell();
	const FVector2D Centre = CanvasSize * 0.5;

	return FVector2D(
		Centre.X + (Cell.X - Pan.X) * Pixels,
		Centre.Y - (Cell.Y - Pan.Y) * Pixels);
}

FVector2D URollBallSkillGraphWidget::LocalToCell(const FVector2D& Local, const FVector2D& CanvasSize) const
{
	const float Pixels = FMath::Max(0.0001f, PixelsPerCell());
	const FVector2D Centre = CanvasSize * 0.5;

	return FVector2D(
		Pan.X + (Local.X - Centre.X) / Pixels,
		Pan.Y - (Local.Y - Centre.Y) / Pixels);
}

FBox2D URollBallSkillGraphWidget::NodeBox(int32 NodeIndex, const FVector2D& CanvasSize) const
{
	if (Graph == nullptr || !Graph->IsValidNodeIndex(NodeIndex))
	{
		return FBox2D(FVector2D::ZeroVector, FVector2D::ZeroVector);
	}

	const FRollBallSkillNode& Node = Graph->GetNode(NodeIndex);

	const FVector2D Size(
		NodeBaseSize * Zoom * Node.Definition.ScaleX,
		NodeBaseSize * Zoom * Node.Definition.ScaleY);

	const FVector2D Centre = CellToLocal(Node.Cell, CanvasSize);
	return FBox2D(Centre - Size * 0.5, Centre + Size * 0.5);
}

int32 URollBallSkillGraphWidget::HitTestNode(const FVector2D& Local, const FVector2D& CanvasSize) const
{
	if (Graph == nullptr)
	{
		return INDEX_NONE;
	}

	for (int32 i = Graph->GetNodes().Num() - 1; i >= 0; --i)
	{
		if (NodeBox(i, CanvasSize).IsInside(Local))
		{
			return i;
		}
	}
	return INDEX_NONE;
}

bool URollBallSkillGraphWidget::ResolveBend(const FVector2D& A, const FVector2D& B,
	ERollBallEdgeRoute Route, FVector2D& OutBend)
{
	OutBend = FVector2D::ZeroVector;

	if (Route == ERollBallEdgeRoute::Straight
		|| FMath::IsNearlyEqual(A.X, B.X, 0.01)
		|| FMath::IsNearlyEqual(A.Y, B.Y, 0.01))
	{
		return false;
	}

	OutBend = (Route == ERollBallEdgeRoute::VerticalFirst)
		? FVector2D(A.X, B.Y)
		: FVector2D(B.X, A.Y);

	return true;
}

void URollBallSkillGraphWidget::FrameAll()
{
	if (Graph == nullptr || !Graph->IsBuilt())
	{
		return;
	}

	FVector2D Min;
	FVector2D Max;
	Graph->GetCellBounds(Min, Max);

	Pan = (Min + Max) * 0.5;

	const double Span = FMath::Max(2.0, FMath::Max(Max.X - Min.X, Max.Y - Min.Y) + 3.0);
	const double View = FMath::Min(
		FMath::Max(1.0, LastCanvasSize.X),
		FMath::Max(1.0, LastCanvasSize.Y));

	Zoom = FMath::Clamp(static_cast<float>(View / (Span * CellSize)), MinZoom, MaxZoom);
	TargetZoom = Zoom;
	bFocusing = false;
}

void URollBallSkillGraphWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);

	LastCanvasSize = FVector2D(MyGeometry.GetLocalSize());

	if (bPendingFrameAll && LastCanvasSize.X > 1.0 && LastCanvasSize.Y > 1.0)
	{
		bPendingFrameAll = false;
		FrameAll();
	}

	if (!FMath::IsNearlyEqual(Zoom, TargetZoom, 0.0005f))
	{
		const float Alpha = 1.0f - FMath::Exp(-ZoomDampRate * InDeltaTime);
		Zoom = FMath::Lerp(Zoom, TargetZoom, Alpha);
	}
	else if (!FMath::IsNearlyEqual(Zoom, TargetZoom))
	{
		Zoom = TargetZoom;
	}

	if (bFocusing)
	{
		Pan += FocusCell - LocalToCell(FocusLocal, LastCanvasSize);

		if (FMath::IsNearlyEqual(Zoom, TargetZoom, 0.0005f))
		{
			bFocusing = false;
		}
	}
}

int32 URollBallSkillGraphWidget::NativePaint(const FPaintArgs& Args, const FGeometry& AllottedGeometry,
	const FSlateRect& MyCullingRect, FSlateWindowElementList& OutDrawElements,
	int32 LayerId, const FWidgetStyle& InWidgetStyle, bool bParentEnabled) const
{
	const FVector2D CanvasSize = FVector2D(AllottedGeometry.GetLocalSize());

	PaintBox(OutDrawElements, LayerId, AllottedGeometry, FVector2D::ZeroVector, CanvasSize, BackgroundColor);

	PaintGrid(AllottedGeometry, OutDrawElements, LayerId + 1);
	PaintEdges(AllottedGeometry, OutDrawElements, LayerId + 2);
	PaintNodes(AllottedGeometry, OutDrawElements, LayerId + 3);
	PaintTooltip(AllottedGeometry, OutDrawElements, LayerId + 6);

	return Super::NativePaint(Args, AllottedGeometry, MyCullingRect, OutDrawElements,
		LayerId + 8, InWidgetStyle, bParentEnabled);
}

void URollBallSkillGraphWidget::PaintGrid(const FGeometry& Geometry, FSlateWindowElementList& Elements, int32 Layer) const
{
	const float Pixels = PixelsPerCell();
	if (Pixels < GridMinPixelSpacing)
	{
		return;
	}

	const FVector2D CanvasSize = FVector2D(Geometry.GetLocalSize());

	const FVector2D TopLeft = LocalToCell(FVector2D::ZeroVector, CanvasSize);
	const FVector2D BottomRight = LocalToCell(CanvasSize, CanvasSize);

	const int32 FirstX = FMath::FloorToInt(TopLeft.X);
	const int32 LastX = FMath::CeilToInt(BottomRight.X);
	const int32 FirstY = FMath::FloorToInt(BottomRight.Y);
	const int32 LastY = FMath::CeilToInt(TopLeft.Y);

	for (int32 X = FirstX; X <= LastX; ++X)
	{
		const double LocalX = CellToLocal(FVector2D(X, 0.0), CanvasSize).X;
		PaintLine(Elements, Layer, Geometry,
			FVector2D(LocalX, 0.0), FVector2D(LocalX, CanvasSize.Y), GridColor, 1.0f);
	}

	for (int32 Y = FirstY; Y <= LastY; ++Y)
	{
		const double LocalY = CellToLocal(FVector2D(0.0, Y), CanvasSize).Y;
		PaintLine(Elements, Layer, Geometry,
			FVector2D(0.0, LocalY), FVector2D(CanvasSize.X, LocalY), GridColor, 1.0f);
	}
}

void URollBallSkillGraphWidget::PaintEdges(const FGeometry& Geometry, FSlateWindowElementList& Elements, int32 Layer) const
{
	if (Graph == nullptr)
	{
		return;
	}

	const FVector2D CanvasSize = FVector2D(Geometry.GetLocalSize());

	for (const FRollBallSkillEdge& Edge : Graph->GetEdges())
	{
		const FVector2D From = CellToLocal(Graph->GetNode(Edge.NodeIndexA).Cell, CanvasSize);
		const FVector2D To = CellToLocal(Graph->GetNode(Edge.NodeIndexB).Cell, CanvasSize);

		const bool bBothOwned = Graph->IsOwned(Edge.NodeIndexA) && Graph->IsOwned(Edge.NodeIndexB);
		const bool bOnPath = PendingPath.Contains(Edge.NodeIndexA) || PendingPath.Contains(Edge.NodeIndexB);

		FLinearColor Color = EdgeColor;
		float Thickness = 2.0f;

		if (bBothOwned)
		{
			Color = EdgeOwnedColor;
			Thickness = 3.0f;
		}
		else if (bOnPath)
		{
			Color = EdgePathColor;
			Thickness = 3.0f;
		}

		FVector2D Bend;
		if (ResolveBend(From, To, Edge.RouteType, Bend))
		{
			PaintLine(Elements, Layer, Geometry, From, Bend, Color, Thickness);
			PaintLine(Elements, Layer, Geometry, Bend, To, Color, Thickness);
		}
		else
		{
			PaintLine(Elements, Layer, Geometry, From, To, Color, Thickness);
		}
	}
}

void URollBallSkillGraphWidget::PaintNodes(const FGeometry& Geometry, FSlateWindowElementList& Elements, int32 Layer) const
{
	if (Graph == nullptr)
	{
		return;
	}

	const FVector2D CanvasSize = FVector2D(Geometry.GetLocalSize());
	const int32 TextLayer = Layer + 1;

	for (int32 i = 0; i < Graph->GetNodes().Num(); ++i)
	{
		const FBox2D Box = NodeBox(i, CanvasSize);

		if (Box.Max.X < 0.0 || Box.Min.X > CanvasSize.X || Box.Max.Y < 0.0 || Box.Min.Y > CanvasSize.Y)
		{
			continue;
		}

		const FVector2D Size = Box.Max - Box.Min;
		const float BorderWidth = FMath::Max(1.5f, 2.5f * Zoom);

		PaintBox(Elements, Layer, Geometry, Box.Min, Size, NodeBorderColorOf(i));
		PaintBox(Elements, Layer, Geometry,
			Box.Min + FVector2D(BorderWidth, BorderWidth),
			Size - FVector2D(BorderWidth, BorderWidth) * 2.0,
			NodeFillColorOf(i));

		if (Size.Y < LabelMinPixelHeight)
		{
			continue;
		}

		const FRollBallSkillNode& Node = Graph->GetNode(i);

		FString Label = Node.Definition.DisplayName.ToString().Left(2);
		if (Label.IsEmpty())
		{
			Label = TEXT("?");
		}

		FSlateFontInfo Font = LabelFont;
		Font.Size = FMath::Clamp(FMath::RoundToInt(Size.Y * 0.42f), 6, 18);

		const FVector2D LabelSize = MeasureText(Label, Font);
		const FVector2D LabelPos = Box.Min + (Size - LabelSize) * 0.5;

		PaintText(Elements, TextLayer, Geometry, LabelPos, Label, Font,
			Graph->IsOwned(i) ? FLinearColor::White : FLinearColor(0.75f, 0.78f, 0.85f));

		if (Node.Definition.MaxLevel > 1 && Size.Y >= LabelMinPixelHeight * 1.6f)
		{
			FSlateFontInfo SmallFont = LabelFont;
			SmallFont.Size = FMath::Clamp(FMath::RoundToInt(Size.Y * 0.26f), 6, 12);

			const FString Rank = FString::Printf(TEXT("%d/%d"),
				Graph->GetLevel(i), Node.Definition.MaxLevel);

			const FVector2D RankSize = MeasureText(Rank, SmallFont);

			PaintText(Elements, TextLayer, Geometry,
				FVector2D(Box.Max.X - RankSize.X - 2.0, Box.Max.Y - RankSize.Y - 1.0),
				Rank, SmallFont, FLinearColor(1.0f, 0.92f, 0.55f));
		}
	}
}

void URollBallSkillGraphWidget::PaintTooltip(const FGeometry& Geometry, FSlateWindowElementList& Elements, int32 Layer) const
{
	if (Graph == nullptr || !Graph->IsValidNodeIndex(HoveredNodeIndex) || !bMouseInside)
	{
		return;
	}

	const FRollBallSkillNode& Node = Graph->GetNode(HoveredNodeIndex);
	const int32 Level = Graph->GetLevel(HoveredNodeIndex);
	const int32 Cost = Graph->GetNextCost(HoveredNodeIndex);
	const int32 Gold = GetGold();

	TArray<FString> Lines;
	Lines.Add(Node.Definition.DisplayName.ToString().ToUpper());

	if (!Node.Definition.Description.IsEmpty())
	{
		Lines.Add(Node.Definition.Description.ToString());
	}
	else if (Node.Definition.GrantStat != ERollBallSkillStat::None)
	{
		Lines.Add(FRollBallSkillStats::DescribeAmount(
			Node.Definition.GrantStat, Node.Definition.AmountPerLevel).ToString());
	}

	Lines.Add(FString::Printf(TEXT("level: %d/%d"), Level, Node.Definition.MaxLevel));

	if (Node.Definition.NodeKind == ERollBallSkillNodeKind::Gate
		&& !Graph->IsGateOpen(HoveredNodeIndex, GetBestStage()))
	{
		Lines.Add(FString::Printf(TEXT("잠김 - 최고 %d 스테이지 필요"), Node.Definition.RequiredBestStage));
	}
	else if (Cost > 0)
	{
		Lines.Add(FString::Printf(TEXT("$  %d/%d"), Gold, Cost));
	}
	else
	{
		Lines.Add(TEXT("만렙"));
	}

	if (HoveredNodeIndex == SelectedNodeIndex && PendingPath.Num() > 1)
	{
		Lines.Add(FString::Printf(TEXT("경로 %d칸 / 합계 %d"),
			PendingPath.Num(), Graph->GetPathCost(PendingPath)));
	}

	const double PanelPadding = 10.0;
	const double RowHeight = TextLineHeight(TooltipFont) + 2.0;

	double Width = 0.0;
	for (const FString& Row : Lines)
	{
		Width = FMath::Max(Width, MeasureText(Row, TooltipFont).X);
	}

	const FVector2D PanelSize(Width + PanelPadding * 2.0, RowHeight * Lines.Num() + PanelPadding * 2.0);
	const FVector2D CanvasSize = FVector2D(Geometry.GetLocalSize());

	FVector2D PanelPos = MouseLocal + FVector2D(16.0, 16.0);
	PanelPos.X = FMath::Clamp(PanelPos.X, 0.0, FMath::Max(0.0, CanvasSize.X - PanelSize.X));
	PanelPos.Y = FMath::Clamp(PanelPos.Y, 0.0, FMath::Max(0.0, CanvasSize.Y - PanelSize.Y));

	PaintBox(Elements, Layer, Geometry, PanelPos, PanelSize, TooltipBackColor);
	PaintBox(Elements, Layer, Geometry, PanelPos, FVector2D(PanelSize.X, 2.0),
		BranchColorOf(Node.Definition.Branch));

	for (int32 i = 0; i < Lines.Num(); ++i)
	{
		const FLinearColor Color = (i == 0)
			? FLinearColor::White
			: FLinearColor(0.72f, 0.78f, 0.88f);

		PaintText(Elements, Layer + 1, Geometry,
			PanelPos + FVector2D(PanelPadding, PanelPadding + RowHeight * i),
			Lines[i], TooltipFont, Color);
	}
}

FLinearColor URollBallSkillGraphWidget::BranchColorOf(ERollBallSkillBranch Branch) const
{
	switch (Branch)
	{
	case ERollBallSkillBranch::Core:     return FLinearColor(0.85f, 0.85f, 0.90f);
	case ERollBallSkillBranch::Survival: return FLinearColor(0.85f, 0.28f, 0.33f);
	case ERollBallSkillBranch::Mobility: return FLinearColor(0.26f, 0.62f, 0.92f);
	case ERollBallSkillBranch::Weapon:   return FLinearColor(0.78f, 0.45f, 0.92f);
	case ERollBallSkillBranch::Economy:  return FLinearColor(0.95f, 0.75f, 0.25f);
	default:                             return FLinearColor::Gray;
	}
}

FLinearColor URollBallSkillGraphWidget::NodeFillColorOf(int32 NodeIndex) const
{
	const FRollBallSkillNode& Node = Graph->GetNode(NodeIndex);
	FLinearColor Color = BranchColorOf(Node.Definition.Branch);

	if (!Graph->IsOwned(NodeIndex))
	{
		const bool bReachable = Graph->HasOwnedNeighbour(NodeIndex)
			&& Graph->IsGateOpen(NodeIndex, GetBestStage());

		Color *= bReachable ? 0.62f : 0.28f;
		Color.A = 1.0f;
	}

	return Color;
}

FLinearColor URollBallSkillGraphWidget::NodeBorderColorOf(int32 NodeIndex) const
{
	if (NodeIndex == SelectedNodeIndex)
	{
		return SelectedBorderColor;
	}

	if (Graph->IsOwned(NodeIndex))
	{
		return OwnedBorderColor;
	}

	FText Reason;
	if (Graph->CanBuy(NodeIndex, GetGold(), GetBestStage(), Reason))
	{
		return BuyableBorderColor;
	}

	return LockedBorderColor;
}

FReply URollBallSkillGraphWidget::NativeOnMouseButtonDown(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent)
{
	const FVector2D Local = FVector2D(InGeometry.AbsoluteToLocal(InMouseEvent.GetScreenSpacePosition()));
	const FVector2D CanvasSize = FVector2D(InGeometry.GetLocalSize());

	if (InMouseEvent.GetEffectingButton() == EKeys::MiddleMouseButton
		|| InMouseEvent.GetEffectingButton() == EKeys::RightMouseButton)
	{
		bPanning = true;
		bFocusing = false;
		LastPanLocal = Local;
		return FReply::Handled().CaptureMouse(TakeWidget());
	}

	if (InMouseEvent.GetEffectingButton() == EKeys::LeftMouseButton)
	{
		const int32 Hit = HitTestNode(Local, CanvasSize);

		if (Hit == INDEX_NONE)
		{
			SelectNode(INDEX_NONE);
		}
		else if (Hit == SelectedNodeIndex)
		{
			AttemptPurchase(Hit);
		}
		else
		{
			SelectNode(Hit);
		}

		return FReply::Handled();
	}

	return FReply::Unhandled();
}

FReply URollBallSkillGraphWidget::NativeOnMouseButtonUp(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent)
{
	if (bPanning
		&& (InMouseEvent.GetEffectingButton() == EKeys::MiddleMouseButton
			|| InMouseEvent.GetEffectingButton() == EKeys::RightMouseButton))
	{
		bPanning = false;
		return FReply::Handled().ReleaseMouseCapture();
	}

	return FReply::Unhandled();
}

FReply URollBallSkillGraphWidget::NativeOnMouseMove(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent)
{
	const FVector2D Local = FVector2D(InGeometry.AbsoluteToLocal(InMouseEvent.GetScreenSpacePosition()));
	const FVector2D CanvasSize = FVector2D(InGeometry.GetLocalSize());

	MouseLocal = Local;
	bMouseInside = true;

	if (bPanning)
	{
		const FVector2D Before = LocalToCell(LastPanLocal, CanvasSize);
		const FVector2D Now = LocalToCell(Local, CanvasSize);
		Pan += Before - Now;

		LastPanLocal = Local;
		return FReply::Handled();
	}

	HoveredNodeIndex = HitTestNode(Local, CanvasSize);
	return FReply::Handled();
}

FReply URollBallSkillGraphWidget::NativeOnMouseWheel(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent)
{
	const FVector2D Local = FVector2D(InGeometry.AbsoluteToLocal(InMouseEvent.GetScreenSpacePosition()));
	const FVector2D CanvasSize = FVector2D(InGeometry.GetLocalSize());

	TargetZoom = FMath::Clamp(
		TargetZoom * FMath::Exp(InMouseEvent.GetWheelDelta() * ZoomStep),
		MinZoom, MaxZoom);

	FocusLocal = Local;
	FocusCell = LocalToCell(Local, CanvasSize);
	bFocusing = true;

	return FReply::Handled();
}

void URollBallSkillGraphWidget::NativeOnMouseLeave(const FPointerEvent& InMouseEvent)
{
	Super::NativeOnMouseLeave(InMouseEvent);

	bMouseInside = false;
	HoveredNodeIndex = INDEX_NONE;
}

FReply URollBallSkillGraphWidget::NativeOnKeyDown(const FGeometry& InGeometry, const FKeyEvent& InKeyEvent)
{
	if (InKeyEvent.GetKey() == EKeys::Escape)
	{
		RemoveFromParent();
		return FReply::Handled();
	}

	if (InKeyEvent.GetKey() == EKeys::Home)
	{
		FrameAll();
		return FReply::Handled();
	}

	return Super::NativeOnKeyDown(InGeometry, InKeyEvent);
}

void URollBallSkillGraphWidget::SelectNode(int32 NodeIndex)
{
	SelectedNodeIndex = NodeIndex;
	RefreshPendingPath();
}

void URollBallSkillGraphWidget::RefreshPendingPath()
{
	PendingPath.Reset();

	if (Graph == nullptr || !Graph->IsValidNodeIndex(SelectedNodeIndex))
	{
		return;
	}

	Graph->FindPathTo(SelectedNodeIndex, GetBestStage(), PendingPath);
}

void URollBallSkillGraphWidget::AttemptPurchase(int32 NodeIndex)
{
	URollBallGameInstance* GameInstance = GetRollBallGameInstance();
	if (Graph == nullptr || GameInstance == nullptr)
	{
		return;
	}

	const int32 GoldBefore = GetGold();
	FText Reason;

	if (Graph->CanBuy(NodeIndex, GoldBefore, GetBestStage(), Reason))
	{
		if (GameInstance->BuySkillNode(NodeIndex, Reason))
		{
			OnPurchased(NodeIndex, GoldBefore - GetGold());
			RefreshPendingPath();
			return;
		}
	}

	else if (PendingPath.Num() > 0)
	{
		if (GameInstance->BuySkillPath(PendingPath, Reason))
		{
			OnPurchased(NodeIndex, GoldBefore - GetGold());
			RefreshPendingPath();
			return;
		}
	}

	OnPurchaseRefused(Reason);
}

URollBallGameInstance* URollBallSkillGraphWidget::GetRollBallGameInstance() const
{
	return GetGameInstance<URollBallGameInstance>();
}

int32 URollBallSkillGraphWidget::GetGold() const
{
	const URollBallGameInstance* GameInstance = GetRollBallGameInstance();
	return GameInstance != nullptr ? GameInstance->GetGold() : 0;
}

int32 URollBallSkillGraphWidget::GetBestStage() const
{
	const URollBallGameInstance* GameInstance = GetRollBallGameInstance();
	return GameInstance != nullptr ? GameInstance->GetBestStage() : 0;
}

#undef LOCTEXT_NAMESPACE
```

</details>
<!-- /code -->

## 사용 방법

### C++ 위젯을 블루프린트로 만들기

1. 콘텐츠 브라우저에서 위젯 블루프린트를 새로 만든다
2. 부모 클래스를 묻는 창에서 만든 C++ 클래스를 고른다
3. 직접 그리는 위젯이면 캔버스에 아무것도 안 올려도 된다

이미 만든 위젯의 부모를 바꾸려면 그래프 탭의 Class Settings 에서 Parent Class 를 고른다.

### 화면에 올리기

```cpp
UUserWidget* Widget = CreateWidget(GetWorld(), WidgetClass);
Widget->AddToViewport();
```

마우스를 쓰는 화면이면 입력 모드를 같이 바꾼다. 안 하면 클릭이 게임으로 샌다.

```cpp
PlayerController->SetShowMouseCursor(true);
UWidgetBlueprintLibrary::SetInputMode_UIOnlyEx(PlayerController, Widget);
```

## 함정

### NativePaint 는 const 라 상태를 못 바꾼다

그리는 김에 무엇을 계산해 저장할 수 없다. 계산은 입력이나 `NativeTick` 에서 하고, 그리기는 읽기만 한다.

### 그리기와 클릭이 다른 도형이면 안 잡힌다

원으로 잡고 사각형으로 그리면 모서리가 안 잡힌다. 보이는데 안 눌리는 버그가 여기서 난다.

상자를 만드는 함수를 하나 두고 그리기와 클릭이 같이 쓴다.

```cpp
FBox2D NodeBox(int32 NodeIndex, const FVector2D& CanvasSize) const;
```

### 지역 변수 이름이 부모와 겹치면 빌드가 멈춘다

`UUserWidget` 에 `Padding` 이라는 멤버가 있다. 함수 안에서 같은 이름을 쓰면 경고가 나고, 언리얼은 경고를 오류로 다루므로 빌드가 실패한다.

```
error C4458: declaration of 'Padding' hides class member
```

이름을 바꾼다. `PanelPadding` 처럼 무엇의 여백인지 붙인다.

### 첫 프레임에는 화면 크기가 없다

`NativeConstruct` 에서 전체를 화면에 맞추면 기본 크기로 계산된다. 열자마자 줌이 엉뚱하다.

크기가 필요한 일은 깃발로 미룬다.

```cpp
if (bPendingFrameAll && LastCanvasSize.X > 1.0)
{
    bPendingFrameAll = false;
    FrameAll();
}
```

### 델리게이트를 안 풀면 위젯이 안 죽는다

`NativeConstruct` 에서 `AddDynamic` 했으면 `NativeDestruct` 에서 `RemoveDynamic` 한다. 안 풀면 화면을 닫아도 참조가 남는다.
