#pragma once

#include "Kismet/BlueprintFunctionLibrary.h"
#include "Containers/Map.h"
#include "Engine/World.h"
#include "Engine/EngineTypes.h"
#include "Engine/StaticMeshActor.h"
#include "Components/HierarchicalInstancedStaticMeshComponent.h"

#include "FGFoliageRemovalSubsystem.h"

#include "FoliageGhost.h"
#include "URegrowCommand.generated.h"


UCLASS()
class GARDENERTOOLS_API URegrowCommand : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:

	UFUNCTION(BlueprintCallable, Category=GardenerToolkit, meta = (WorldContext = "WorldContextObject"))
	static int Regrow(AFGFoliageRemovalSubsystem* FoliageSystem, FVector playerLocation, int rangeInMeters, bool debug, FString& log, const UObject* WorldContextObject, UClass* FoliageGhostActorClass);
	
	UFUNCTION(BlueprintCallable, Category = GardenerToolkit, meta = (WorldContext = "WorldContextObject"))
	static int Vision(AFGFoliageRemovalSubsystem* FoliageSystem, FVector playerLocation, int rangeInMeters, bool debug, FString& log, const UObject* WorldContextObject, UClass* FoliageVisionActorClass);

	UFUNCTION(BlueprintCallable, Category = GardenerToolkit)
	static int CountRemovals(AFGFoliageRemovalSubsystem* FoliageSystem, bool debug, FString& log);	

	UFUNCTION(BlueprintCallable, Category = GardenerToolkit)
	static int ResetFoliage(AFGFoliageRemovalSubsystem* FoliageSystem, bool debug, FString& log);

private:

	// has to be in interface so it can acess private parts of foliage system
	static int UndeleteFoliage_Update8(AFGFoliageRemovalSubsystem* FoliageSystem, FVector playerLocation, int range, bool respawnFoliage, FString& log, bool debug, UWorld* World, UClass* ActorPrototype);
	static int Regrow_Internal(AFGFoliageRemovalSubsystem* FoliageSystem, FVector playerLocation, int rangeInMeters, bool respawnFoliage, FString& log, bool debug, const UObject* WorldContextObject, UClass* ActorPrototype);
};

