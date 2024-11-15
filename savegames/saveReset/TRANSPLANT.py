# generated with help of chat GPT and hand-fixed to actually work.

import argparse
import subprocess
import os
import json

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

    # process the other properties spread throughout the file
    playtime_properties = [
        "mPlayDurationWhenLoaded",
        "mShipLandTimeStampSave"
    ]

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

# Main function
def main():
    parser = argparse.ArgumentParser(description="Transplant data from SOURCE save file to TARGET save file.")
    parser.add_argument("source", help="Source save file (.sav)")
    parser.add_argument("target", help="Target save file (.sav)")
    parser.add_argument("--playtime", action="store_true", help="Transplant playtime data")
    parser.add_argument("--awesomePoints", action="store_true", help="Transplant AWESOME points")
    parser.add_argument("--vehiclePaths", action="store_true", help="Transplant vehicle paths")
    parser.add_argument("--colorSwatches", action="store_true", help="Transplant color swatches")

    args = parser.parse_args()

    # Strip .sav extension if present and set savefile names
    sourceSav = os.path.splitext(args.source)[0]
    targetSav = os.path.splitext(args.target)[0]

    # Create temp directory if it doesn't exist
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)

    # Set paths for intermediate JSON files
    source_json = os.path.join(temp_dir, f"{sourceSav}.json")
    target_json = os.path.join(temp_dir, f"{targetSav}.json")

    # Convert SOURCE and TARGET save files to JSON
    sav_to_json(f"{sourceSav}.sav", source_json)
    sav_to_json(f"{targetSav}.sav", target_json)

    # Data manipulation section (to be added later)

    if args.playtime:
        transplant_playtime_data(source_json, target_json)

    # Convert modified JSON back to new .sav file
    edited_sav_filename = f"{targetSav}_Edited.sav"
    json_to_sav(target_json, edited_sav_filename)
    print(f"Edited save file created: {edited_sav_filename}")

if __name__ == "__main__":
    main()
