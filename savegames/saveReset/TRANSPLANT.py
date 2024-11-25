# V4 - final version (for now)
# base layout generated with help of chat GPT, methods hand-implemented by a human

import argparse
import subprocess
import os
import json

import sav_parse

# Helper functions to convert .sav to JSON and vice versa
def sav_to_json(sav_file, json_file):
    subprocess.run(["py", "sav_cli.py", "--to-json", sav_file, json_file], check=True)

def json_to_sav(json_file, sav_file):
    subprocess.run(["py", "sav_cli.py", "--from-json", json_file, sav_file], check=True)

def transplant_playtime_data(source_json, target_json):
    # Load source and target JSON files
    with open(source_json, 'r') as src_file:
        source_data = json.load(src_file)
    with open(target_json, 'r') as tgt_file:
        target_data = json.load(tgt_file)

    # Define the paths for properties to copy
    playtime_fields = ["playDurationInSeconds", "saveDateTimeInTicks", "saveDatetime"]
    
    # Transplant main playtime fields from saveFileInfo
    if "saveFileInfo" in source_data and "saveFileInfo" in target_data:
        for field in playtime_fields:
            if field in source_data["saveFileInfo"]:
                target_data["saveFileInfo"][field] = source_data["saveFileInfo"][field]
                print(f"Copied {field}: {source_data['saveFileInfo'][field]}")
    else:
        print("Error: 'saveFileInfo' object not found in one or both JSON files.")

    #mdayseconds and mnumberofpasseddays
    for objects in source_data["levels"]["null"]["objects"]:
        if "properties" in objects:
            properties = objects["properties"]
            if len(properties) > 0 and properties[0][0] == "mDaySeconds":
                mDaySeconds_source = properties[0][1]
            if len(properties) > 1 and properties[1][0] == "mNumberOfPassedDays":
                mNumberOfPassedDays_source = properties[1][1]            

    print("Read mDaySeconds: " + str(mDaySeconds_source) + " mNumberOfPassedDays: " + str(mNumberOfPassedDays_source))

    for objects in target_data["levels"]["null"]["objects"]:
        if "properties" in objects:
            properties = objects["properties"]
            if len(properties) > 0 and properties[0][0] == "mDaySeconds":
                properties[0][1] = mDaySeconds_source
            if len(properties) > 1 and properties[1][0] == "mNumberOfPassedDays":
                properties[1][1] = mNumberOfPassedDays_source

    print("Written mDaySeconds & mNumberOfPassedDays to Target")

    for objects in source_data["levels"]["null"]["objects"]:
        if "instanceName" in objects and "properties" in objects:
            instance = objects["instanceName"]
            if str(instance).startswith("Persistent_Level:PersistentLevel.BP_GameState"):
                for properties in objects["properties"]:
                    if properties[0] == "mPlayDurationWhenLoaded":
                        mPlayDurationWhenLoaded = properties[1]

    print("Read mPlayDurationWhenLoaded: " + str(mPlayDurationWhenLoaded))

    for objects in target_data["levels"]["null"]["objects"]:
        if "instanceName" in objects and "properties" in objects:
            instance = objects["instanceName"]
            if str(instance).startswith("Persistent_Level:PersistentLevel.BP_GameState"):
                for properties in objects["properties"]:
                    if properties[0] == "mPlayDurationWhenLoaded":
                        properties[1] = mPlayDurationWhenLoaded

    print("Written mPlayDurationWhenLoaded to Target")

    # Write the updated target JSON file
    with open(target_json, 'w') as tgt_file:
        json.dump(target_data, tgt_file, indent=4)
#end transplant playtime

def create_vehicle_subsystem(target_json):
    with open(target_json, 'r') as tgt_file:
        target_data = json.load(tgt_file)
    
    for objects in target_data["levels"]["null"]["objects"]:
        if "instanceName" in objects and "properties" in objects:
            instance = objects["instanceName"]
            if str(instance).startswith("Persistent_Level:PersistentLevel.VehicleSubsystem"):
                if not any(item[0] == "mSavedPaths" for item in objects):
                    objects["properties"].append(["mSavedPaths", [] ])
                    objects["propertyTypes"].append(["mSavedPaths", ["ArrayProperty", "ObjectProperty"], 0])
    
    # Write the updated target JSON file
    with open(target_json, 'w') as tgt_file:
        json.dump(target_data, tgt_file, indent=4)
#end create vehicle subsystem

def transplant_vehicle_paths(sourceSavExt, edited_sav_ext, temp_dir):
        
    def list_paths(sourceSavExt):   #list vehicle paths from source, copied from save cli cause it prints instead of returnz
        paths = []
        (saveFileInfo, headhex, grids, levels, extraObjectReferenceList) = sav_parse.readFullSaveFile(sourceSavExt)
        savedPathList = []
        for (levelName, actorAndComponentObjectHeaders, collectables1, objects, collectables2) in levels:
            for object in objects:
               if object.instanceName == "Persistent_Level:PersistentLevel.VehicleSubsystem":
                  savedPaths = sav_parse.getPropertyValue(object.properties, "mSavedPaths")
                  if savedPaths != None:
                     for savedPath in savedPaths:
                        savedPathList.append(savedPath.pathName)
               if object.instanceName in savedPathList:
                  pathName = sav_parse.getPropertyValue(object.properties, "mPathName")
                  if pathName != None:
                     paths.append(pathName)
        return paths
    #end list paths

    def export_paths_json(sourceSavExt, paths): #extract paths to json files
        for index, path in enumerate(paths):
            filename = os.path.join(temp_dir, f"VP{index}.json")
            subprocess.run(["py", "sav_cli.py", "--export-vehicle-path", path, sourceSavExt, filename], check=False)
    #end export paths json

    def import_paths_json(edited_sav_ext, paths): #import paths to json files
        for index, path in enumerate(paths):
            filename = os.path.join(temp_dir, f"VP{index}.json")
            subprocess.run(["py", "sav_cli.py", "--import-vehicle-path", path, edited_sav_ext, filename, edited_sav_ext, "--same-time"], check=False)
    #end import paths json

    paths = list_paths(sourceSavExt)
    print(paths)
    export_paths_json(sourceSavExt, paths)
    import_paths_json(edited_sav_ext, paths)
#end transplant vehicle paths

def transplant_color_swatches(source_json, target_json):
    
    def transplant_color_slots(source_data, target_data):
        color_slots = False
        for src_object in source_data["levels"]["null"]["objects"]:
            if "instanceName" in src_object and "properties" in src_object:
                instance = src_object["instanceName"]
                if str(instance).startswith("Persistent_Level:PersistentLevel.BuildableSubsystem"):
                    for src_prop in src_object["properties"]:
                        if str(src_prop[0]) == "mColorSlots_Data":
                            source_colors = src_prop[1]
        
        for tgt_object in target_data["levels"]["null"]["objects"]:
            if "instanceName" in tgt_object and "properties" in tgt_object:
                instance = tgt_object["instanceName"]
                if str(instance).startswith("Persistent_Level:PersistentLevel.BuildableSubsystem"):
                    for tgt_prop in tgt_object["properties"]:
                        if str(tgt_prop[0]) == "mColorSlots_Data":
                            tgt_prop[1] = source_colors
                            color_slots = True
                    if not color_slots:
                        tgt_object["properties"].append(["mColorSlots_Data", source_colors])
                        tgt_object["propertyTypes"].append(["mColorSlots_Data", ["ArrayProperty", "StructProperty", "FactoryCustomizationColorSlot"], 0])
    #end transplant_color_slots

    def transplant_color_presets(source_data, target_data):
        color_presets = False
        for src_object in source_data["levels"]["null"]["objects"]:
            if "instanceName" in src_object and "properties" in src_object:
                instance = src_object["instanceName"]
                if str(instance).startswith("Persistent_Level:PersistentLevel.BP_GameState"):
                    for src_prop in src_object["properties"]:
                        if str(src_prop[0]) == "mPlayerGlobalColorPresets":
                            source_colorPresets = src_prop[1]

        for tgt_object in target_data["levels"]["null"]["objects"]:
            if "instanceName" in tgt_object and "properties" in tgt_object:
                instance = tgt_object["instanceName"]
                if str(instance).startswith("Persistent_Level:PersistentLevel.BP_GameState"):
                    for tgt_prop in tgt_object["properties"]:
                        if str(tgt_prop[0]) == "mPlayerGlobalColorPresets":
                            tgt_prop[1] = source_colorPresets
                            color_presets = True
                    if not color_presets:
                        tgt_object["properties"].append(["mPlayerGlobalColorPresets", source_colorPresets])
                        tgt_object["propertyTypes"].append(["mPlayerGlobalColorPresets", ["ArrayProperty", "StructProperty", "GlobalColorPreset"], 0])
    #end transplant_color_presets

    def transplant_light_colors(source_data, target_data):
        light_colors = False
        for src_object in source_data["levels"]["null"]["objects"]:
            if "instanceName" in src_object and "properties" in src_object:
                instance = src_object["instanceName"]
                if str(instance).startswith("Persistent_Level:PersistentLevel.BP_GameState"):
                    for src_prop in src_object["properties"]:                    
                        if str(src_prop[0]) == "mBuildableLightColorSlots":
                            source_lightColors = src_prop[1]

        for tgt_object in target_data["levels"]["null"]["objects"]:
            if "instanceName" in tgt_object and "properties" in tgt_object:
                instance = tgt_object["instanceName"]
                if str(instance).startswith("Persistent_Level:PersistentLevel.BP_GameState"):
                    for tgt_prop in tgt_object["properties"]:
                        if str(tgt_prop[0]) == "mBuildableLightColorSlots":
                            tgt_prop[1] = source_lightColors
                            light_colors = True
                    if not light_colors:
                        tgt_object["properties"].append(["mBuildableLightColorSlots", source_lightColors])
                        tgt_object["propertyTypes"].append(["mBuildableLightColorSlots", ["ArrayProperty", "StructProperty", "LinearColor"], 0])
    #end transplant_light_colors


    with open(source_json, 'r') as src_file:
        source_data = json.load(src_file)
    with open(target_json, 'r') as tgt_file:
        target_data = json.load(tgt_file)

    transplant_color_slots(source_data, target_data)
    transplant_color_presets(source_data, target_data)
    transplant_light_colors(source_data, target_data)

    # Write the updated target JSON file
    with open(target_json, 'w') as tgt_file:
        json.dump(target_data, tgt_file, indent=4)

    print(f"Swatches copied into target save")
#end transplant_color_swatches

# Main function
def main():
    parser = argparse.ArgumentParser(description="Transplant data from SOURCE save file to TARGET save file.")
    parser.add_argument("source", help="Source save file (.sav)")
    parser.add_argument("target", help="Target save file (.sav)")
    parser.add_argument("--playtime", action="store_true", help="Transplant playtime data")
    parser.add_argument("--vehicles", action="store_true", help="Transplant vehicle paths")
    parser.add_argument("--colors", action="store_true", help="Transplant color swatches")
    parser.add_argument("--debug", action="store_true", help="Produce a json-dump of the final save to compare with original")

    args = parser.parse_args()

    # Strip .sav extension if present and set savefile names
    sourceSav = os.path.splitext(args.source)[0]
    targetSav = os.path.splitext(args.target)[0]

    # readd sav extension
    sourceSavExt = f"{sourceSav}.sav"
    targetSavExt = f"{targetSav}.sav"

    # Create temp directory if it doesn't exist
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)

    # Set paths for intermediate JSON files
    source_json = os.path.join(temp_dir, f"{sourceSav}.json")
    target_json = os.path.join(temp_dir, f"{targetSav}.json")

    # Convert SOURCE and TARGET save files to JSON
    sav_to_json(sourceSavExt, source_json)
    sav_to_json(targetSavExt, target_json)

    # Data manipulation section 

    if args.playtime:
        transplant_playtime_data(source_json, target_json)

    if args.vehicles:
        create_vehicle_subsystem(target_json)

    if args.colors:
        transplant_color_swatches(source_json, target_json)

    # Convert modified JSON back to new .sav file
    edited_sav_ext = f"{targetSav}_Edited.sav"
    json_to_sav(target_json, edited_sav_ext)

    if args.vehicles:
        transplant_vehicle_paths(sourceSavExt, edited_sav_ext, temp_dir)

    print(f"Edited save file created: {edited_sav_ext}")

    if args.debug:
        target_original_json = os.path.join(temp_dir, f"{targetSav}_Original.json")
        sav_to_json(targetSavExt, target_original_json)
        target_edited_json = os.path.join(temp_dir, f"{targetSav}_Edited.json")
        sav_to_json(edited_sav_ext, target_edited_json)
        print(f"Created json dumps of original {target_original_json} and edited save {target_edited_json}")

if __name__ == "__main__":
    main()
