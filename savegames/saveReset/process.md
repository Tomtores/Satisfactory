# Resetting your save progression - SCIM megaprint method

*Note: Satis 1.0 save is asumed.*

## What will be copied:
- [SCIM] All buildings
- [SCIM] All building inventories
- [script] Total playtime and ingame days counter
- [script] *Saved* vehicle paths
- [script] Color swatches and saved color presets (named colors)

## What will be reset:
- Milestones and mam research
- Game phase
- Collectables, map, foliage
- Dropped items
- Train schedules

## The process
**BACKUP your save!**

### On your SOURCE save:
- Turn off autosave, set enemies to passive in game options for peace of mind. Load your save to convert.
- Dismantle all drones (they bug when copying megaprint)
- Dismantle Space Elevator and HUB (and any modded unique buildings)
- PICK UP all the cups and loose equipment you placed on the ground. You don't have to pick up *placed* statues, but do pick the dropped ones, as SCIM megaprint will not preserve dropped things.
- Screenshot the layout of all your blueprint menus for easy recreation.
- [manual] Write down your swatches (pair of colours for each). You can skip this step if you use the script.
- [optional] Go through all of your trucks and save the paths with descriptive name. We will try to copy those over to new save with a script (you can skip this step if you don't want to bother with scripts)
- [Optional] Place "JUNK" container outside base - ensure nothing is built under or above it, so you can find it on SCIM 2d map. In the container place:
	- All your HDDs -> drop pods will reset and you get a full new set to gather.
	- Mercer spheres and Somersloops - the collectibles will reset
	- Slugs (optional - as these are infinite by doggo farming, so feel free to keep them if you want)
- Empty your player inventory - everything you are holding will not carry over. Store your equipment, also the one you are wearing, into a box. Store rest of the items too.
- Write down/screenshot your save total game time
- Save as new save and give it meaningful name, "SOURCE" will be assumed in this guide.

BACKUP your saves (even if you did so - backup them again)

### New save preparation

- Start a new game - you have to pick new session name. You can skip onboarding if you want, but there are some story pieces in it, so do watch it if you did not start new game in 1.0 yet. You do not need to do any progress - preferably do not build anything and position your character in a spot that you know is clear from buildings in your SOURCE save.
- Save the game with meaningful name, for example TARGET. 
- Exit the game and locate your SOURCE and TARGET saves.
- Copy the saves into known folder, eg. SAVE_RESET on desktop.

### [optional] Transplanting data via save editing
We will be using Grehak Save parser - download it from `https://github.com/GreyHak/sat_sav_parse` and unpack to known folder (`SAVE_RESET/sav_parse_v1.6_full_release` on desktop)
- Copy SOURCE and TARGET saves into the folder with the tool
- Download and save the provided [`transplant.py`](https://github.com/Tomtores/Satisfactory/blob/main/savegames/saveReset/TRANSPLANT.py) into the folder with the tool (containing `sav_cli.py`)
- Shift-rightclick and select powershell or your shell of choice, then run following command:

`python transplant.py SOURCE.sav TARGET.sav --playtime --vehicles --colors`

The command will take some time to execute (especially if you have multiple truck paths) - be patient.
- The result will ba saved into TARGET_Edited.sav
- **Remember** to use the modified TARGET_Edited.sav save in next steps ;-)
- Note: If the Target_Edited.sav does not load properly after pasting the megaprint, try opening the edited save in game and resaving it as new file. That fixed the issue for me.

### Copying your buildings with inventories via SCIM:

- Go to SCIM interactive map and load the SOURCE save. (https://satisfactory-calculator.com/en/interactive-map)
- [optional] Find the container with items you wanted to delete [mercers, sloops, drives], rightlick it and select Clear Inventory.
- Use selection tool to select everything on the map. Scroll to selection option and pick "Copy to Megaprint"
- On left, click the rectangle-with-legs icon and in new menu "Download megaprint". Save the file in known location.
- Close the browser tab
- Open new tab with the SCIM tool. Load your TARGET save (use TARGET_Edited one if you used the script to modify it)
- Click the rectangle-with-legs icon again and insert your megaprint from previous step. 
- A new button will appear below - click it to actually paste the factory back into the new save. It will take some time, based how big your original save was.
- Use button to download the final save.
- Put the save in your game saves folder and load the game.
- You may want to resave as new file to ensure it works fine.
- [optional] Load the save with AGS on or Flying mod installed. Spend some time inspect your factory. Take your time. Once you are done, quit the game without saving. You don't want your achievements disabled due to AGS, do you?
- Once you are certain the save looks correct, restart the game, turn off passive mode, turn on autosave, load the final modified save and enjoy your first day of working for Ficsit (or whichever subsidiary you contracted for). You will have to manually load the truck paths and redo your hotbars, but hey, at least you kept your factory and swatches.
