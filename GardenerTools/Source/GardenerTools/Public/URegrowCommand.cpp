#include "URegrowCommand.h"

const int MaxBatchUndeletes = 1000;

int URegrowCommand::Regrow(AFGFoliageRemovalSubsystem* FoliageSystem, FVector playerLocation, int rangeInMeters, bool debug, FString& log, const UObject* WorldContextObject, UClass* FoliageGhostActorClass) {
	bool respawnFoliage = true;
	return Regrow_Internal(FoliageSystem, playerLocation, rangeInMeters, respawnFoliage, log, debug, WorldContextObject, FoliageGhostActorClass);
}

int URegrowCommand::Vision(AFGFoliageRemovalSubsystem* FoliageSystem, FVector playerLocation, int rangeInMeters, bool debug, FString& log, const UObject* WorldContextObject, UClass* FoliageVisionActorClass) {
	bool respawnFoliage = false;
	return Regrow_Internal(FoliageSystem, playerLocation, rangeInMeters, respawnFoliage, log, debug, WorldContextObject, FoliageVisionActorClass);
}

int URegrowCommand::CountRemovals(AFGFoliageRemovalSubsystem* FoliageSystem, bool debug, FString& log)
{
	//return FoliageSystem->Stat_NumRemovedInstances(); //heh, doesnt work
	int deletedCount = 0;

	if (debug)
	{
		int tileCount = FoliageSystem->mSaveData.Num();
		log += FString::Printf(TEXT("Level tiles count: %d"), tileCount);
	}

	for (const TPair<FIntVector, FFoliageRemovalSaveDataPerCell>& level : FoliageSystem->mSaveData)	//iterate map squares
	{
		for (const TPair<const UFoliageType*, FFoliageRemovalSaveDataForFoliageType>& foliageTypes : level.Value.SaveDataMap)	// iterate foliage types
		{
			deletedCount += foliageTypes.Value.Locations().Num();
		}
	}

	return deletedCount;
};

int URegrowCommand::ResetFoliage(AFGFoliageRemovalSubsystem* FoliageSystem, bool debug, FString& log)
{
	int deletedCountBefore = CountRemovals(FoliageSystem, debug, log);

	for (TPair<FIntVector, FFoliageRemovalSaveDataPerCell>& level : FoliageSystem->mSaveData)	//iterate map squares
	{
		for (TPair<const UFoliageType*, FFoliageRemovalSaveDataForFoliageType>& foliageTypes : level.Value.SaveDataMap)	// iterate foliage types
		{
			foliageTypes.Value.RemovedLocations.Empty();
			foliageTypes.Value.RemovedLocationLookup.Empty();
		}
	}

	return deletedCountBefore;
};

int URegrowCommand::Regrow_Internal(AFGFoliageRemovalSubsystem* FoliageSystem, FVector playerLocation, int rangeInMeters, bool respawnFoliage, FString& log, bool debug, const UObject* WorldContextObject, UClass* ActorPrototype)
{
	if (!FoliageSystem)
	{
		log += FString("Error! No subsystem");
		return -1;
	}
	if (!WorldContextObject)
	{
		log += FString("Error, no World object!");
		return -2;
	}

	UWorld* World = GEngine->GetWorldFromContextObject(WorldContextObject, EGetWorldErrorMode::LogAndReturnNull);

	if (!World)
	{
		log += FString("Failed to resolve World object!");
		return -3;
	}

	int range = rangeInMeters * 100; // the internal UE calculations are in centimeters

	if (debug)
	{
		int countBefore = FoliageSystem->GetFoliageCountWithinRadius(playerLocation, range);

		log += FString::Printf(TEXT("Found %d total foliage items in the range.\n"), countBefore);
	}

	int count = UndeleteFoliage_Update8(FoliageSystem, playerLocation, range, respawnFoliage, log, debug, World, ActorPrototype);

	if (debug)
	{
		int countAfter = FoliageSystem->GetFoliageCountWithinRadius(playerLocation, range);

		log += FString::Printf(TEXT("Found %d total foliage items in the range after operation"), countAfter);
	}

	return count;
}

AFoliageGhost* RespawnActor(const UHierarchicalInstancedStaticMeshComponent* mesh, FVector location, UWorld* World, UClass* ActorPrototype, FString& log, bool debug,
	FIntVector levelChunkId, const UFoliageType* foliageTypeKey, uint32 hash, AFGFoliageRemovalSubsystem* FoliageSystem)
{
	FActorSpawnParameters parameters = FActorSpawnParameters();
	parameters.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	parameters.bNoFail = true;
	AFoliageGhost* RespawnedFoliage = World->SpawnActor<AFoliageGhost>(ActorPrototype, location, location.Rotation(), parameters);

	if (RespawnedFoliage)
	{
		RespawnedFoliage->SetMobility(EComponentMobility::Stationary);
		UStaticMeshComponent* MeshComponent = RespawnedFoliage->GetStaticMeshComponent();
		if (MeshComponent)
		{
			MeshComponent->SetStaticMesh(mesh->GetStaticMesh());
		}
		else if (debug)
		{
			log += "Failed to get mesh component of spawned actor!!!\n";
		}

		RespawnedFoliage->SetupData(levelChunkId, foliageTypeKey, location, hash, FoliageSystem);
	}
	else if (debug)
	{
		log += "Actor spawn failed!!!\n";
	}

	return RespawnedFoliage;
}

AStaticMeshActor* RespawnTimedActor(const UHierarchicalInstancedStaticMeshComponent* mesh, FVector location, UWorld* World, UClass* ActorPrototype, FString& log, bool debug)
{
	FActorSpawnParameters parameters = FActorSpawnParameters();
	parameters.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	parameters.bNoFail = true;
	AStaticMeshActor* RespawnedFoliage = World->SpawnActor<AStaticMeshActor>(ActorPrototype, location, location.Rotation(), parameters);

	if (RespawnedFoliage)
	{
		RespawnedFoliage->SetMobility(EComponentMobility::Stationary);
		UStaticMeshComponent* MeshComponent = RespawnedFoliage->GetStaticMeshComponent();
		if (MeshComponent)
		{
			MeshComponent->SetStaticMesh(mesh->GetStaticMesh());
		}
		else if (debug)
		{
			log += "Failed to get mesh component of spawned actor!!!\n";
		}

		// RespawnedFoliage->SetupData(levelChunkId, foliageTypeKey, location, hash, FoliageSystem);
	}
	else if (debug)
	{
		log += "Actor spawn failed!!!\n";
	}

	return RespawnedFoliage;
}

static bool IsInRange(FVector foliageLocation, FVector playerLocation, int range, FString& log, bool debug)
{
	float distance = FVector::Dist(playerLocation, foliageLocation);

	if (debug)
	{
		log += FString::Printf(TEXT("Distance %d\n"), (int)distance);
	}

	return distance <= range;
}

int URegrowCommand::UndeleteFoliage_Update8(AFGFoliageRemovalSubsystem* FoliageSystem, FVector playerLocation, int range, bool respawnFoliage, FString& log, bool debug, UWorld* World, UClass* ActorPrototype)
{
	int undeletedCount = 0;

	for (TPair<FIntVector, FFoliageRemovalSaveDataPerCell>& level : FoliageSystem->mSaveData)	//iterate map squares
	{
		for (TPair<const UFoliageType*, FFoliageRemovalSaveDataForFoliageType>& foliageTypes : level.Value.SaveDataMap)	// iterate foliage types
		{
			for (int32 i = foliageTypes.Value.RemovedLocations.Num() - 1; i >= 0; i--)	//iterate specific removals, backwards, to avoid iterating over removed elements
			{
				if (IsInRange(foliageTypes.Value.RemovedLocations[i], playerLocation, range, log, debug))
				{
					UFoliageType* keyCopy = const_cast<UFoliageType*>(foliageTypes.Key);	//tbh, I have no idea what I'm doing here
					UHierarchicalInstancedStaticMeshComponent* const* mesh = FoliageSystem->mFoliageComponentTypeMapping.FindKey(keyCopy);
					if (mesh)
					{
						if (respawnFoliage)	// foliage regrowth flow
						{
							uint32 hash = AFGFoliageRemovalSubsystem::HashFoliageInstanceLocation(foliageTypes.Value.RemovedLocations[i]);

							if (debug)
							{
								log += FString::Printf(TEXT("Found foliage in range with hash %u \n"), hash);
							}

							AFoliageGhost* RespawnedFoliage = RespawnActor(*mesh, foliageTypes.Value.RemovedLocations[i], World, ActorPrototype, log, debug, level.Key, foliageTypes.Key, hash, FoliageSystem);
							
							if (RespawnedFoliage)
							{
								foliageTypes.Value.RemovedLocations.RemoveAt(i);
								foliageTypes.Value.RemovedLocationLookup.Remove(hash);
							}
							else if (debug)
							{
								log += FString::Printf(TEXT("Null actor for respawned foliage with hash %u!\n"), hash);
							}
						}
						else	// show deleted foliage timed ghosts
						{
							AStaticMeshActor* TemporaryGhost = RespawnTimedActor(*mesh, foliageTypes.Value.RemovedLocations[i], World, ActorPrototype, log, debug);

							if (!TemporaryGhost && debug)
							{
								log += FString::Printf(TEXT("Null actor for respawned foliage!\n"));
							}
						}
					}
					else
					{
						log += FString::Printf(TEXT("Failed to load mesh!!!\n"));
					}

					undeletedCount++;
					if (undeletedCount >= MaxBatchUndeletes)
					{
						return undeletedCount;
					}
				}
			}
		}
	}

	return undeletedCount;
}




