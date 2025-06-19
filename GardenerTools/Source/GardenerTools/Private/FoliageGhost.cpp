#include "FoliageGhost.h"

void AFoliageGhost::SetupData(FIntVector levelChunkId, const UFoliageType* foliageTypekey, FVector location, uint32 hash, AFGFoliageRemovalSubsystem* foliageSystem)
{
	this->mLevelChunkId = levelChunkId;
	this->mFoliageTypekey = foliageTypekey;
	this->mLocation = location;
	this->mHash = hash;
	this->mFoliageSystem = foliageSystem;
}

bool AFoliageGhost::RemoveFromWorld(FString& log, bool debug)
{
	if (!mFoliageSystem)
	{
		log += "Foliage subsystem missing!\n";
		return false;
	}

	FFoliageRemovalSaveDataPerCell* levelChunk = mFoliageSystem->mSaveData.Find(mLevelChunkId);
	if (!levelChunk)
	{
		log += "Failed to resolve level chunk!\n";
		return false;
	}

	FFoliageRemovalSaveDataForFoliageType* foliageRemoval = levelChunk->SaveDataMap.Find(mFoliageTypekey);
	if (!foliageRemoval)
	{
		log += "Failed to resolve removal actor!\n";
		return false;
	}

	if (debug)
	{
		log += FString::Printf(TEXT("Removed instances before %d\n"), foliageRemoval->Locations().Num());
	}

	foliageRemoval->RemovedLocations.Add(mLocation);
	foliageRemoval->RemovedLocationLookup.Add(mHash);

	if (debug)
	{
		log += FString::Printf(TEXT("Removed instances before %d\n"), foliageRemoval->Locations().Num());
	}

	return this->Destroy();
}