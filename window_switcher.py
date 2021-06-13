#!/bin/python

import json
import re
import subprocess

output = subprocess.check_output(["swaymsg", "-t", "get_tree"])
data = {}
try:
    data = json.loads(output)
except Exception as e:
    raise e

monitors = []
if "nodes" in data:
    monitors = data["nodes"]


including_virtual_displays = []
for monitor in monitors:
    if "nodes" in monitor:
        including_virtual_displays.append(monitor["nodes"])


windows = []
for display in including_virtual_displays:
    for d in display:
        if "nodes" in d:
            for window in d["nodes"]:
                class_name = ""
                if "window_properties" in window:
                    class_name = window["window_properties"]["class"]
                elif "app_id" in window:
                    class_name = window["app_id"]

                if "nodes" in window:
                    if len(window["nodes"]) > 0:
                        for n in window["nodes"]:
                            class_name = ""
                            if "window_properties" in n:
                                class_name = n["window_properties"]["class"]
                            elif "app_id" in n:
                                class_name = n["app_id"]
                            windows.append(
                                {"name": n["name"], "id": n["id"], "app": class_name}
                            )
                    else:
                        windows.append(
                            {
                                "name": window["name"],
                                "id": window["id"],
                                "app": class_name,
                            }
                        )

                if "floating_nodes" in window:
                    for f in window["floating_nodes"]:
                        windows.append(
                            {"name": f["name"], "id": f["id"], "app": class_name}
                        )
        if "floating_nodes" in d:
            for window in d["floating_nodes"]:
                class_name = ""
                if "window_properties" in window:
                    class_name = window["window_properties"]["class"]
                elif "app_id" in window:
                    class_name = window["app_id"]
                windows.append(
                    {"name": window["name"], "id": window["id"], "app": class_name}
                )


wofi_windows = []
for window in windows:
    if window["name"] != None:
        wofi_windows.append(
            str(window["app"])
            + " - "
            + window["name"].strip().replace('"', "")
            + " - "
            + str(window["id"])
        )

wofi_windows = "\n".join(wofi_windows)

ps = subprocess.Popen(("echo", wofi_windows), stdout=subprocess.PIPE)
try:
    output = subprocess.check_output(
        ("wofi", "--dmenu", "-i", "-p", "Active windows:"), stdin=ps.stdout
    )
    if output:
        app_id = re.search(r"\- (\d+)$", output.decode("utf-8"))
        if app_id:
            app_id = app_id.group(1)
            subprocess.check_output(
                ("swaymsg", '[con_id="' + str(app_id) + '"]', "focus")
            )
except Exception as e:
    pass
