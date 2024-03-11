## Foliage system summary

Foliage in game is baked-in as part of the map.  
When a foliage item is removed (picked up/chainsawed/blown up), game marks the item as invisible and persists that information in the save file.
This means the game first loads all the foliage items on the map, then destroys the actors for ones that have been marked as removed.
Note: Foliage items consist of bushes, trees, corals and *rocks* (the decorative ones, not the ones that block resources). Everything you can chainsaw directly or as collateral is considered foliage.

## Logical structure

Foliage removal system contains entries for map tiles (around 10k when fully populated).  
These tiles in turn contain list of foliage types.  
And each foliage type entry finally has an array of vectors that lists every removed object.  
When a foliage item gets removed, its coordinates (or actually, position + rotation) is persisted in a list in appropriate Tile for given plant type. 
Note1: that there is no scale info available in that list. Some objects are scaled, and will look odd if restored at original size, but we have no access to scaling info here.
Note 2: there is a second list storing hashes of the vectors. Element has to be removed from both lists to be "undeleted"
These lists are persisted in save directly, to mark the removed foliage, thus making the save file grow as more foliage is removed.
The foliage removal subsystem in code also contains the list of foliage meshes. We can use those meshes for bringing the object back into the world if needed.

## Save structure [not updated, may be wrong]

Save file contains an `FactoryGame.FGFoliageRemoval` section which lists 100+ entries for `RemovalActors`, which in turn may contain 0 or more coordinates of removed plants. 
To bring a plant back into the world, simply remove the child removed instances.

```
+ FactoryGame.FGFoliageRemoval
  - Persistent_Level:PersistentLevel.FGFoliageRemoval_2147471854
  - Persistent_Level:PersistentLevel.FGFoliageRemoval_2147471853	[The items to remove are inside this nodes]
  - Persistent_Level:PersistentLevel.FGFoliageRemoval_2147471852 
  [...]
```

## Code structure

Start by grabbing the `AFGFoliageRemovalSubsystem` - it contains the persistent save data for the foliage (`mSaveData`) and a list of foliage type meshes (`mFoliageComponentTypeMapping`).  
Remember to make some friends on the way, as those are private.
There is also an `mMeshComponentsOctree` that handles physical allocation of currently loaded mesh instances, but we should not be touching that here.
Inside `mSaveData` there is a list of pairs - vector serving as key for the map cell, and `FFoliageRemovalSaveDataPerCell` with actual removal data.  
Inside each `FFoliageRemovalSaveDataPerCell` we have another list of pairs - `UFoliageType` (we can use this to find the correct mesh in `mFoliageComponentTypeMapping`) and a `FFoliageRemovalSaveDataForFoliageType` struct.  
The `FFoliageRemovalSaveDataForFoliageType` finally contains two arrays of interest - `RemovedLocations` and `RemovedLocationLookup`. To "undelete" a foliage item, we have to remove its location vector from first array AND the associated hash from second array.  
Note: the hash is calculated using `AFGFoliageRemovalSubsystem::HashFoliageInstanceLocation`.
Once both entries are cleared, the foliage object will reappear at next save load (or level stream in).  
Respawning a correct actor when user undeletes foliage is left as exercise for the reader.
Hint: You can use the `mFoliageComponentTypeMapping` and location to put a placeholder. There is no scale information available, so it will look a bit out of whack, but better than nothing. 
