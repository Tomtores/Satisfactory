# generated with help of chat GPT and hand-fixed to actually work.

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
    #todo list paths from original save. add all paths to target save. may need to create the subsystem in targetjson first?.
    
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
            subprocess.run(["py", "sav_cli.py", "--export-vehicle-path", path, sourceSavExt, filename], check=True)
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

# Main function
def main():
    parser = argparse.ArgumentParser(description="Transplant data from SOURCE save file to TARGET save file.")
    parser.add_argument("source", help="Source save file (.sav)")
    parser.add_argument("target", help="Target save file (.sav)")
    parser.add_argument("--playtime", action="store_true", help="Transplant playtime data")
    parser.add_argument("--vehicles", action="store_true", help="Transplant vehicle paths")
    parser.add_argument("--swatches", action="store_true", help="Transplant color swatches")
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

    # Convert modified JSON back to new .sav file
    edited_sav_ext = f"{targetSav}_Edited.sav"
    json_to_sav(target_json, edited_sav_ext)

    if args.vehicles:
        transplant_vehicle_paths(sourceSavExt, edited_sav_ext, temp_dir)

    print(f"Edited save file created: {edited_sav_ext}")

    if args.debug:
        target_edited_json = os.path.join(temp_dir, f"{targetSav}_Edited.json")
        sav_to_json(edited_sav_ext, target_edited_json)
        sav_to_json(targetSavExt, target_json)

if __name__ == "__main__":
    main()
