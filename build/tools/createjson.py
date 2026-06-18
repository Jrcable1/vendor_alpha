#!/usr/bin/env python3
#
# Copyright (C) 2019-2025 crDroid Android Project
# Copyright (C) 2025 AlphaDroid
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import sys
import os
import json
import hashlib

def extract_prop(prop, buildprop_path):
    if not os.path.isfile(buildprop_path):
        return ""
    with open(buildprop_path, 'r') as f:
        for line in f:
            if line.startswith(prop + "="):
                return line.strip().split('=', 1)[1]
    return ""

def md5sum(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def sha256sum(filename):
    hash_sha256 = hashlib.sha256()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def main():
    if len(sys.argv) < 4:
        print("Usage: createjson.py <TARGET_DEVICE> <PRODUCT_OUT> <FILE_NAME>")
        sys.exit(1)

    device = sys.argv[1]
    out_dir = sys.argv[2]
    filename = sys.argv[3]

    existing_ota_json = f"./vendor/OTA/{device}.json"
    output_json = f"{out_dir}/{device}.json"
    buildprop = f"{out_dir}/system/build.prop"
    target_file = f"{out_dir}/{filename}"

    version = extract_prop("ro.alpha.build.version", buildprop)
    buildtype = extract_prop("ro.alpha.release.type", buildprop)
    buildvariant = extract_prop("ro.alpha.build.variant", buildprop)
    maintainer = extract_prop("ro.alpha.maintainer", buildprop)
    timestamp_str = extract_prop("ro.system.build.date.utc", buildprop)
    
    timestamp = 0
    if timestamp_str:
        try:
            timestamp = int(timestamp_str)
        except ValueError:
            pass

    if not os.path.isfile(target_file):
        print(f"File {target_file} not found.")
        sys.exit(1)

    md5 = md5sum(target_file)
    sha256 = sha256sum(target_file)
    size = os.path.getsize(target_file)

    # Determine base json to update: prefer the one in OUT (from a previous build), fallback to vendor/OTA
    base_json_path = output_json if os.path.isfile(output_json) else existing_ota_json
    existing_data = {"response": []}
    if os.path.isfile(base_json_path):
        try:
            with open(base_json_path, 'r') as f:
                existing_data = json.load(f)
                if "response" not in existing_data or not isinstance(existing_data["response"], list):
                    existing_data = {"response": []}
        except json.JSONDecodeError:
            pass

    # For default static fields (oem, dt, kernel, etc), strictly use the official vendor/OTA json's first entry
    default_fields = {}
    if os.path.isfile(existing_ota_json):
        try:
            with open(existing_ota_json, 'r') as f:
                ota_data = json.load(f)
                if "response" in ota_data and isinstance(ota_data["response"], list) and len(ota_data["response"]) > 0:
                    default_fields = ota_data["response"][0]
        except json.JSONDecodeError:
            print(f"Failed to parse {existing_ota_json}")

    def get_ota_field(key, default=""):
        return default_fields.get(key, default)

    new_response_item = {
        "maintainer": maintainer if maintainer else "",
        "oem": get_ota_field("oem"),
        "device": device,
        "filename": filename,
        "download": f"https://sourceforge.net/projects/alphadroid-project/files/{device}/{filename}/download",
        "timestamp": timestamp,
        "md5": md5,
        "sha256": sha256,
        "size": size,
        "version": version,
        "buildtype": buildtype,
        "buildvariant": buildvariant,
        "forum": get_ota_field("forum"),
        "gapps": get_ota_field("gapps"),
        "firmware": get_ota_field("firmware"),
        "modem": get_ota_field("modem"),
        "bootloader": get_ota_field("bootloader"),
        "recovery": get_ota_field("recovery"),
        "paypal": get_ota_field("paypal"),
        "telegram": get_ota_field("telegram"),
        "dt": get_ota_field("dt"),
        "common-dt": get_ota_field("common-dt"),
        "kernel": get_ota_field("kernel")
    }

    # Find and update the existing variant, or append a new one
    # Note: older OTA jsons might have stored the variant in 'buildtype'
    updated = False
    for i, item in enumerate(existing_data["response"]):
        item_variant = item.get("buildvariant", item.get("buildtype"))
        if item_variant == buildvariant:
            existing_data["response"][i] = new_response_item
            updated = True
            break
    
    if not updated:
        existing_data["response"].append(new_response_item)

    # Safety check: ensure all existing items have 'buildvariant' to prevent Updater crashes
    for item in existing_data["response"]:
        if "buildvariant" not in item and "buildtype" in item:
            item["buildvariant"] = item["buildtype"]

    # Write output
    with open(output_json, 'w') as f:
        json.dump(existing_data, f, indent=4)

    if not os.path.isfile(existing_ota_json):
        print("There is no official support for this device yet")
        print("Consider adding official support by reading the documentation at https://github.com/alphadroid-devices/OTA/blob/alpha-16.2/README.md")
    else:
        print("\n")
        print(json.dumps(existing_data, indent=4))
        print("\n")

    print("JSON file generation completed")

if __name__ == "__main__":
    main()
