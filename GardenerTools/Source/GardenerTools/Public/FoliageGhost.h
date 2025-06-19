#pragma once

#include "CoreMinimal.h"
#include "Engine/StaticMeshActor.h"
#include "FoliageType.h"

#include "FGFoliageRemoval.h"
#include "FGFoliageRemovalSubsystem.h"

#include "FoliageGhost.generated.h"

/**
 * 
 */
UCLASS()
class GARDENERTOOLS_API AFoliageGhost : public AStaticMeshActor
{
	GENERATED_BODY()

public:

	UFUNCTION(BlueprintCallable, Category = GardenerToolkit)
	bool RemoveFromWorld(FString& log, bool debug);

	void SetupData(FIntVector levelChunkId, const UFoliageType* foliageTypekey, FVector location, uint32 hash, AFGFoliageRemovalSubsystem* foliageSystem);

private:
	FIntVector mLevelChunkId;
	const UFoliageType* mFoliageTypekey;
	FVector mLocation;
	uint32 mHash;
	AFGFoliageRemovalSubsystem* mFoliageSystem;
};
