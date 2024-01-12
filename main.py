import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import json
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from PIL import Image, ImageTk

width = 600
height = 200

root = tk.Tk()
root.title("Psych to Codename Character Converter")
root.resizable(False, False)
root.iconbitmap('icon.ico')

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x = (screen_width - width) // 2
y = (screen_height - height) // 2

root.geometry(f"{width}x{height}+{x}+{y}")

# variables

char_json = None
isPlayer = tk.BooleanVar(value=False)
isGF = tk.BooleanVar(value=False)

label_char_path = tk.StringVar(value='No file selected')

# functions

def select_char_file():
    global char_json
    char_path = filedialog.askopenfile(title="Select Psych Character file", filetypes=[("JSON Files", "*.json")])

    if char_path:
        char_json = json.loads(char_path.read())
        label_char_path.set(char_path.name)
        start_button.config(state='normal')
        isplayer_checkbox.config(state='normal')
        isgf_checkbox.config(state='normal')

    if label_char_path.get() == 'No file selected':
        start_button.config(state='disabled')
        isplayer_checkbox.config(state='disabled')
        isgf_checkbox.config(state='disabled')

def save_xml_file(content):
    file_name = os.path.basename(label_char_path.get()).replace(".json", ".xml")
    file_path = filedialog.asksaveasfile(title="Save Character file", defaultextension=".xml", filetypes=[("XML Files", "*.xml")], initialfile=file_name)
    try:
        if file_path:
            with open(file_path.name, 'w') as file:
                file.write(content)
                messagebox.showinfo("Success!", "Convert successful")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def dict_to_xml(data, root_name='root'):
    root = ET.Element(root_name)
    dict_to_xml_recursive(root, data)
    return ET.ElementTree(root)

def dict_to_xml_recursive(element, data):
    for key, value in data.items():
        if key.startswith("@"):
            element.set(key[1:], str(value))
        elif isinstance(value, list):
            for item in value:
                sub_element = ET.SubElement(element, key)
                dict_to_xml_recursive(sub_element, item)
        else:
            sub_element = ET.SubElement(element, key)
            dict_to_xml_recursive(sub_element, value)

def build_char_file():
    global char_json
    dict_char = {}
    char_name = os.path.basename(label_char_path.get()).replace(".json", "")
    codename_char_doctype = "<!DOCTYPE codename-engine-character>"

    if isPlayer.get() != False:
        dict_char["@isPlayer"] = str(isPlayer.get()).lower()

    if isGF.get() != False:
        dict_char["@isGF"] = str(isGF.get()).lower()

    if char_json["position"] != None:
        if char_json["position"][0] != 0: dict_char["@x"] = str(char_json["position"][0])
        if char_json["position"][1] != 0: dict_char["@y"] = str(char_json["position"][1])

    if char_json["animations"] != None and len(char_json["animations"]) > 0:
        dict_char["anim"] = []
        for i, anim in enumerate(char_json["animations"]):
            dict_anim = {}
            if anim["anim"] != None: dict_anim["@name"] = anim["anim"]
            if anim["name"] != None: dict_anim["@anim"] = anim["name"]
            if anim["fps"] != None: dict_anim["@fps"] = str(anim["fps"])
            if anim["loop"] != None: dict_anim["@loop"] = str(anim["loop"]).lower()
            if anim["offsets"] != None and len(anim["offsets"]) > 0:
                dict_anim["@x"] = anim["offsets"][0]
                dict_anim["@y"] = anim["offsets"][1]
            if anim["indices"] != None and len(anim["indices"]) > 0:
                indices = ""
                for i, num in enumerate(anim["indices"]):
                    if i == len(anim["indices"])-1: indices += str(num)
                    else: indices += str(num) + ","
                dict_anim["@indices"] = indices
            dict_char["anim"].insert(i, dict_anim)
    
    if char_json["sing_duration"] != None and char_json["sing_duration"] != 4:
        dict_char["@holdTime"] = str(char_json["sing_duration"])

    if char_json["camera_position"] != None:
        if char_json["camera_position"][0] != 0: dict_char["@camx"] = str(char_json["camera_position"][0])
        if char_json["camera_position"][1] != 0: dict_char["@camy"] = str(char_json["camera_position"][1])

    if char_json["flip_x"] != None and char_json["flip_x"] != False:
        dict_char["@flipX"] = str(char_json["flip_x"]).lower()

    if char_json["healthicon"] != None and char_json["healthicon"] != char_name:
        dict_char["@icon"] = char_json["healthicon"]

    if char_json["healthbar_colors"] != None and len(char_json["healthbar_colors"]) > 0:
        color = char_json["healthbar_colors"]
        dict_char["@color"] = "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2]).upper()

    if char_json["scale"] != None and char_json["scale"] != 1:
        dict_char["@scale"] = str(char_json["scale"])
    
    if char_json["no_antialiasing"] != None and not char_json["no_antialiasing"] != True:
        dict_char["@antialiasing"] = str(char_json["no_antialiasing"]).lower()

    if char_json["image"] != None and char_json["image"] != char_name:
        if char_json["image"].startswith("characters/"):
            char_json["image"] = char_json["image"].removeprefix("characters/")
        dict_char["@sprite"] = char_json["image"]

    tree = dict_to_xml(dict_char, root_name='character')
    xml_string = ET.tostring(tree.getroot(), encoding='utf-8').decode('utf-8')
    dom = minidom.parseString(xml_string)
    pretty_xml_string = dom.toprettyxml(indent="\t").replace('<?xml version="1.0" ?>', codename_char_doctype)

    save_xml_file(content=pretty_xml_string)

# elements

char_path_text = tk.Label(root, textvariable=label_char_path)
char_path_text.place(x=114, y=20)

select_char_button = tk.Button(root, text="Select Character", command=select_char_file)
select_char_button.place(x=10, y=16)

isplayer_checkbox = tk.Checkbutton(root, text="isPlayer", variable=isPlayer)
isplayer_checkbox.config(state='disabled')
isplayer_checkbox.place(x=10, y=48)

isgf_checkbox = tk.Checkbutton(root, text="isGF", variable=isGF)
isgf_checkbox.config(state='disabled')
isgf_checkbox.place(x=90, y=48)

start_button = tk.Button(root, text="Convert", state='disabled', command=build_char_file)
start_button.place(x=10, y=140)

made_by = tk.StringVar(value='Created by Fellyn')
char_path_text = tk.Label(root, textvariable=made_by)
char_path_text.pack(side='bottom')

image = Image.open('icon.ico').resize((20, 20))
photo = ImageTk.PhotoImage(image)
label = tk.Label(root, image=photo)
label.photo = photo
label.pack(side='bottom')

root.mainloop()
