## Foliage system summary

Foliage in game is baked-in as part of the map.  
When a foliage item is removed (picked up/chainsawed/blown up), game marks the item as invisible and persists that information in the save file.
This means the game first loads all the foliage items on the map, then destroys the actors for ones that have been marked as removed.
Note: Foliage items consist of flowers, bushes, trees and *rocks* (the decorative ones, not the ones that block resources)

## Logical structure

Foliage removal system contains 100+ entries listing all combinations of map_tile+plant_type, eg. `Tile_X5_Y3 SM_DryBush_01_FoliageType` with some generic `Persistent_Exploration` entries tossed in. They are internally know as `RemovalActors`
When a foliage item gets removed, its coordinates (or actually, full transform consisting of position + rotation + scale) is persisted in a list in appropriate `RemovalActor` for given location and plant type.
These data in turn is persisted in save, to mark the removed foliage, thus making the save file grow as more foliage is removed.
The `RemovalActor` in code also contains the mesh for given plant type (single copy shared for all instances), which can be resused for bringing the object back into the world if needed.

## Save structure

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

Start by grabbing the `AFGFoliageRemovalSubsystem` - it contains methods to access the foliage removal actors (`AFGFoliageRemoval`).
Note that to get `AFGFoliageRemoval`, you need either the Mesh component of foliage item, or its Map_Tile+Foliage_Type_Name. You can either try to find the correct `UHierarchicalInstancedStaticMeshComponent` in foliage you are interacting with, or try your luck with the name pair.  
\[Tip: You can list all instances of `AFGFoliageRemoval` class in blueprints, if you needed to iterate through all of the name pairs\].
Once you get hold of `AFGFoliageRemoval` you can use the `RemoveInstance(...)` method to delete foliage.

To 'undelete' a foliage, you need to remove it from an internal list of removed foliage. This will make the plant/rock reappear at next save load.
Note that this will not make the plant pop back into the world - respawning an correct actor is left as exercise for the reader (its not that simple, but doable - the `AFGFoliageRemoval` contains the mesh used for the plant type, so we can reuse that. At this moment the writer does not know what kind of actor CSS uses for their foliage).  