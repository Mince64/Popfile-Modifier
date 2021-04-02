
from PIL import Image, ImageDraw, ImageFont
from shutil import rmtree
from misc import *
import sys
import collections
import random


default_classicons = {
                        "scout*"    : "scout",
                        "soldier*"  : "soldier",
                        "pyro*"     : "pyro",
                        "demoman*"  : "demo",
                        "heavy*"    : "heavy",
                        "engineer*" : "engineer",
                        "medic*"    : "medic",
                        "sniper*"   : "sniper",
                        "spy*"      : "spy"
                     }

try:

    font_icon_count = ImageFont.truetype("font\\LSANSD.TTF", 18)

    wave_icon_crit   = Image.open("materials\\wavebar\\wave_icon_crit.png")
    wave_icon_giant  = Image.open("materials\\wavebar\\wave_icon_giant.png")
    wave_icon_normal = Image.open("materials\\wavebar\\wave_icon_normal.png")

    wave_progress_bar_image = Image.open("materials\\wavebar\\wave_progress_bar.png")

except OSError:
    print("ERROR: Missing essential icon or font files!")
    input()
    sys.exit(0)


# Get the final composite image for an icon image
def getIconFinalImage(image, data, is_giant=False, is_support=False):
    image = image.resize((32, 32))
    final = Image.new("RGBA", (40, 80), (77, 82, 88, 255))
    
    if data[1]:
        temp = wave_icon_crit.resize((40, 40))
        final.paste(temp)
        
    if not is_support and is_giant:
        temp = wave_icon_giant.resize((40, 40))
        final.paste(temp, (0, 0), mask=temp)
    else:
        temp = wave_icon_normal.resize((40, 40))
        final.paste(temp, (0, 0), mask=temp)

    try:
        final.paste(image, (4, 4), mask=image)
    except ValueError:
        final.paste(image, (4, 4))

    draw = ImageDraw.Draw(final)

    if not is_support:
        if data[0] > 999:
            data[0] = 999
            
        w, h = draw.textsize(str(data[0]), font_icon_count)
        w_padding = (40 - w) // 2
        draw.text((w_padding, 45), str(data[0]), font=font_icon_count, fill=(235, 228, 202, 255))

    return final
    

# Get the wavebar image for a single wave
def createWaveBar(wave_icon_dict, wavenums, totalcurrency):
    wave_label = "Wave " + str(wavenums[0]) + " / " + str(wavenums[1]) + "  [$" + str(totalcurrency) + "]"
    
    wave_title_height = ImageDraw.Draw(Image.new("RGBA", (300, 300))).textsize(wave_label, font_icon_count)[1]
    
    wave_progress_bar_width  = 405
    wave_progress_bar_height = 23
    wave_progress_bar_vertical_padding = 5
    
    icon_width   = 40
    icon_spacing = 16
    
    support_bar_spacing = 14
    support_bar_width   = 2
    
    support_label_left_spacing = 10
    support_label_width        = ImageDraw.Draw(Image.new("RGBA", (300, 300))).textsize("Support", font_icon_count)[0]

    # Calculate total image dimensions needed
    normal_icon_count  = len(wave_icon_dict["giant"]) + len(wave_icon_dict["normal"])
    support_icon_count = len(wave_icon_dict["support"])
    total_icon_count   = normal_icon_count + support_icon_count

    total_width = 0
    if normal_icon_count:
        total_width += (icon_width * normal_icon_count) + (icon_spacing * (normal_icon_count - 1))

    if support_icon_count:
        total_width += (support_bar_spacing * 2) + support_bar_width

    w1 = 0
    w2 = 0

    if support_icon_count:
        w1 = total_width + (icon_width * support_icon_count) + (icon_spacing * (support_icon_count - 1))
        w2 = total_width + support_label_width

    if support_icon_count:
        total_width = max(w1, w2)
        
    iconbar_width = total_width
    total_width = max(total_width, wave_progress_bar_width)

    total_height = wave_title_height + wave_progress_bar_height + (wave_progress_bar_vertical_padding * 2) + 80

    # Build image
    wavebar = Image.new("RGBA", (total_width, total_height), (77, 82, 88, 255))
    draw    = ImageDraw.Draw(wavebar)

    # Draw Wave title
    current_pos = (0, 0)
    w, h = draw.textsize(wave_label, font=font_icon_count)
    x    = (total_width - w) // 2
    current_pos = (x, 0)
    draw.text(current_pos, wave_label, font=font_icon_count, fill=(235, 228, 202, 255))

    # Draw Wave progress bar
    x = (total_width - wave_progress_bar_width) // 2
    current_pos = (x, h + wave_progress_bar_vertical_padding)
    wavebar.paste(wave_progress_bar_image, current_pos, mask=wave_progress_bar_image)

    # Draw icons

    # If progress bar is widest part of image:
    w = total_width
    if iconbar_width < total_width:
        w = iconbar_width

    # Draw iconbar
    iconbar_image = Image.new("RGBA", (w, 80), (77, 82, 88, 255))
    x = 0
    support_start_x = -1

    normallen = len(wave_icon_dict["normal"].keys())
    giantlen  = len(wave_icon_dict["giant"].keys())
    for group, icondict in wave_icon_dict.items():
        for icon, data in icondict.items():
            iconimage = getIconFinalImage(data[0], data[1], group == "giant", group == "support")

            # Don't do this just yet if support is the only group
            if normal_icon_count:
                iconbar_image.paste(iconimage, (x, 0), mask=iconimage)
                x += icon_width
                
            last_normal_group = None
            if not normallen:
                if giantlen:
                    last_normal_group = "giant"
            else:
                last_normal_group = "normal"
                
            if group == last_normal_group and icon == list(icondict.keys())[-1]:               
                x += support_bar_spacing
                draw = ImageDraw.Draw(iconbar_image)
                draw.line([(x, 0), (x, 65)], (235, 228, 202, 255), support_bar_width)
                x += support_bar_width + support_bar_spacing
                support_start_x = x

            # Only group is "support"
            elif last_normal_group == None:
                if icon == list(icondict.keys())[0]:
                    x += support_bar_spacing
                    draw = ImageDraw.Draw(iconbar_image)
                    draw.line([(x, 0), (x, 65)], (235, 228, 202, 255), support_bar_width)
                    x += support_bar_width + support_bar_spacing
                    support_start_x = x
                
                iconbar_image.paste(iconimage, (x, 0), mask=iconimage)
                x += icon_width + icon_spacing
                
            else:
                x += icon_spacing
    
    # Draw Support label
    if support_start_x != -1:
        current_pos = (support_start_x, 45)
        draw.text(current_pos, "Support", font=font_icon_count, fill=(235, 228, 202, 255))

    # Add iconbar to wavebar
    x = (total_width - iconbar_image.width)
    if x:
        x //= 2

    y = current_pos[1] + wave_progress_bar_vertical_padding
    y += total_height - (y + 80)

    current_pos = (x, y)
    wavebar.paste(iconbar_image, current_pos)
    
    return wavebar


# Get the wavebar image for an entire mission
def createWaveScheduleBar(wave_icon_dicts, filename, totalcurrency_list):
    wavebars = [createWaveBar(wave, (index+1, len(wave_icon_dicts)), totalcurrency_list[index]) for index, wave in enumerate(wave_icon_dicts)]

    # Calculate total image dimensions needed
    margin     = 15
    max_width  = 0
    max_height = 0

    for wavebar in wavebars:
        if wavebar.width > max_width:
            max_width = wavebar.width

        max_height += wavebar.height

    # Draw wavebars into final image
    waveschedulebar = Image.new("RGBA", (max_width, max_height), (77, 82, 88, 255))
    current_pos = (0, 0)
    for wavebar in wavebars:
        x = (max_width - wavebar.width)
        if x:
            x //= 2

        current_pos = (0 + x, current_pos[1])
        waveschedulebar.paste(wavebar, current_pos)
        current_pos = (0, current_pos[1] + wavebar.height)

    mission_name = filename.lower().split('_')
    
    if mission_name[-1].endswith('pop'):
        mission_name[-1] = mission_name[-1][:-4]
        
    mission_name = [term.capitalize() for term in mission_name if term != "mvm"]
    mission_name = ' '.join(mission_name)
                            
    mission_name_size    = ImageDraw.Draw(Image.new("RGBA", (1000, 300))).textsize(mission_name, font_icon_count)
    mission_name_padding = 5
    
    width  = waveschedulebar.width + (margin * 2)
    height = waveschedulebar.height + mission_name_size[1] + (mission_name_padding + margin) + (margin * 2)
    final = Image.new("RGBA", (width, height), (77, 82, 88, 255))

    draw = ImageDraw.Draw(final)
    x    = (final.width - mission_name_size[0])
    if x:
        x //= 2
        
    draw.text((x, margin), mission_name, font=font_icon_count, fill=(235, 228, 202, 255))
    draw.line([(x, margin + mission_name_size[1] + 4), (x + mission_name_size[0], margin + mission_name_size[1] + 4)], (235, 228, 202, 255), 2)
    
    x = (final.width - waveschedulebar.width) // 2
    y = mission_name_size[1] + (mission_name_padding + (margin * 2))
    final.paste(waveschedulebar, (x, y))
    
    return final


# Get an equally distributed random list of integers summing to num (very bad random, but it works)
def getRandIntList(list_length, num):
    if not list_length:
        return []
    if not num:
        return [0 for i in range(list_length)]
    
    randlist = [random.random() for i in range(list_length)]
    s        = sum(randlist)
    randlist = [round(num * (i / s)) for i in randlist]

    if sum(randlist) != num:
        dif = sum(randlist) - num

        while dif != 0:
            index = random.randint(0, list_length-1)
            if dif < 0:
                randlist[index] += 1
                dif += 1
            elif dif > 0:
                if randlist[index] == 0:
                    continue
                randlist[index] -= 1
                dif -= 1
           
    return randlist
    

# Get template blocks from a popfile and it's #base files
def getTemplates(obj, popdir, filename, filename_stack=[], notify_warnings=True):                 
    waveschedule = obj.getWaveSchedule()

    if not waveschedule:
        return None                   
                    
    if os.path.isdir(popdir):
        os.chdir(popdir)
    else:
        return None
    
    popfiles   = [file for file in os.listdir(popdir) if file.endswith(".pop")]
    base_files = [kv.value for kv in obj.keyvalues if areWildNamesEqual(kv.key, "#base", False)]
    templates  = []

    #note stack size
    stack_size = len(filename_stack)

    # Get templates from base files
    for file in base_files:
        os.chdir(popdir)
        
        # A file is trying to #base from another file that will inevitably #base back to it (an infinite loop)
        if file in filename_stack:
            print(f"ERROR: Infinitely recursive #base structure. ({filename} includes {file}, which in turn includes {filename})")
            input()
            sys.exit(0)
            
        if file not in popfiles:
            if file in ["robot_standard.pop", "robot_giant.pop", "robot_gatebot.pop"]:
                os.chdir(script_path + "\\scripts")
            else:
                if notify_warnings:
                    print(f"WARNING: Popfiles directory specified does not contain required #base file {file}.")
                continue

        filename_stack.append(filename)
        base_templates = getTemplates(parsePopFile(file), popdir, file, filename_stack, notify_warnings)
            
        for template1 in templates:
            for template2 in base_templates:
                if template1.name.lower() == template2.name.lower():
                    # This isn't an error in-game, but it's behavior is a bit wonky
                    # and i'd rather not spend a bunch of time for this edge case
                    if notify_warnings:
                        print(f"WARNING: Template redefinition. ({template1.name})")

                    base_templates.remove(template2)
                    
        templates.extend(base_templates)

        filename_stack = filename_stack[:stack_size] # Resize the stack back once we're done with this #base chain

    # Get templates from current file
    templates_obj = waveschedule.queryChildren("Templates", recurse=False, case_sensitive_names=False)
    if templates_obj:
        templates_obj  = templates_obj[0]
        file_templates = templates_obj.queryChildren("*", recurse=False)
        
        for template1 in templates:
            for template2 in base_templates:
                if template1.name.lower() == template2.name.lower():
                    # This isn't an error in-game, but it's behavior is a bit wonky
                    # and i'd rather not spend a bunch of time for this edge case
                    if notify_warnings:
                        print(f"WARNING: Template redefinition. ({template1.name})")

                    base_templates.remove(template2)

        templates.extend(file_templates)

    os.chdir(script_path)
    return templates


# Insert icon data structure into wave_icon_dict
"""
    wave_icon_dict = {
        "giant"   : { "icon_string" : [totalcount, hascrits], ...},
        "normal"  : { "icon_string" : [totalcount, hascrits], ...},
        "support" : { "icon_string" : [totalcount, hascrits], ...}
    }
"""
def getTFBotIconString(tfbot, wave_icon_dict, templates, totalcount, support, notify_warnings=True):

    # It isn't going to be displayed anyways
    if not totalcount and not support:
        if notify_warnings:
            print("WARNING: Non-support TFBot not displayed as a result of 0 totalcount. (Possible result of RandomChoice)")
            print(tfbot)
        return
    
    classicon = None
    miniboss  = False
    hascrits  = False
    tfclass   = None

    # test this
    template_stack = []

    current_template = tfbot
    while True:
        template_stack.append(current_template)
        template        = None
        ignore_template = False
        
        for kv in current_template.keyvalues:
            if not classicon and kv.equals(KeyValue("ClassIcon", None, flags="iq")): # -iq for how dumb this is
                classicon = kv.value.lower().replace('"', "")
            elif not miniboss and kv.equals(KeyValue("Attributes", "MiniBoss", flags="iq")):
                miniboss = True
            elif not tfclass and kv.equals(KeyValue("Class", None, flags="iq")):
                tfclass = kv.value
            elif not hascrits and kv.equals(KeyValue("Attributes", "AlwaysCrit", flags="iq")):
                hascrits = True
            elif kv.equals(KeyValue("Template", None, flags="i")):
                if not ignore_template:
                    template = kv.value.lower()
                    ignore_template = True
            elif kv.equals(KeyValue("EventChangeAttributes", None, flags="iq")):
                if isinstance(kv.value, Block):
                    for block in kv.value.queryChildren("*"):
                        for kv2 in block.keyvalues:
                            if not miniboss and kv2.equals(KeyValue("Attributes", "MiniBoss", flags="iq")):
                                miniboss = True
                            elif not hascrits and kv2.equals(KeyValue("Attributes", "AlwaysCrit", flags="iq")):
                                hascrits = True


        # We have all we need, we don't need to keep going up the template chain
        if classicon != None and miniboss and support and hascrits and tfclass != None:
            break

        # Look through templates if we dont
        else:
            if template:
                try:
                    if template in template_stack:
                        print(f"ERROR: Infinitely recursive template structure. ({tfbot.name})")
                        print(tfbot)
                        input()
                        sys.exit(0)

                    current_template = templates[template]
                    continue
                except KeyError:
                    if notify_warnings:
                        print(F"WARNING: Missing template! ({template}) Please ensure all base files are correctly formed.")
                    break
            else:
                break

    if not tfclass:
        if notify_warnings:
            print(f"WARNING: Invalid TFBot, bot has no class keyvalue. ({tfbot.name})")
            print(tfbot)
        classicon = "debugempty"

    if not classicon:
        for cls, icon in default_classicons.items():
            if areWildNamesEqual(cls, tfclass, False):
                classicon = icon
                break

        if not classicon:
            if notify_warnings:
                print("WARNING: Invalid TFBot, bot has an invalid class value.")
                print(tfbot)
            classicon = "debugempty"

    if support:
        try:
            wave_icon_dict["support"][classicon] = [wave_icon_dict["support"][classicon][0] + totalcount, hascrits if hascrits else wave_icon_dict["support"][classicon][1]]
        except KeyError:
            wave_icon_dict["support"][classicon] = [totalcount, hascrits]
    elif miniboss:
        try:
            wave_icon_dict["giant"][classicon] = [wave_icon_dict["giant"][classicon][0] + totalcount, hascrits if hascrits else wave_icon_dict["giant"][classicon][1]]
        except KeyError:
            wave_icon_dict["giant"][classicon] = [totalcount, hascrits]
    else:
        try:
            wave_icon_dict["normal"][classicon] = [wave_icon_dict["normal"][classicon][0] + totalcount, hascrits if hascrits else wave_icon_dict["normal"][classicon][1]]
        except KeyError:
            wave_icon_dict["normal"][classicon] = [totalcount, hascrits]

    
    # Simulate normal to giant icon stacking
    newicons = copy.deepcopy(wave_icon_dict)
                
    for icon, data in wave_icon_dict["normal"].items():
        if icon in newicons["giant"]:
            newicons["giant"][icon] = [data[0] + newicons["giant"][icon][0], data[1] if data[1] else newicons["giant"][icon][1]]
            del newicons["normal"][icon]

    for group in wave_icon_dict.keys():
        wave_icon_dict[group] = newicons[group]
    


# Insert icon data structure into wave_icon_dict
"""
    wave_icon_dict = {
        "giant"   : { "icon_string" : [totalcount, hascrits], ...},
        "normal"  : { "icon_string" : [totalcount, hascrits], ...},
        "support" : { "icon_string" : [totalcount, hascrits], ...}
    }
"""
def getTankIconString(tank, wave_icon_dict, templates, totalcount, support):

    # It isn't going to be displayed anyways
    if not totalcount and not support:
        return

    classicon = None

    # test this
    template_stack = []

    current_template = tank
    while True:
        template_stack.append(current_template)
        template        = None
        ignore_template = False
        
        for kv in current_template.keyvalues:
            if not classicon and kv.equals(KeyValue("ClassIcon", None, flags="i")):
                classicon = kv.value
            elif kv.equals(KeyValue("Template", None, flags="i")):
                if not ignore_template:
                    template = kv.value.lower()
                    ignore_template = True

        # We have all we need, we don't need to keep going up the template chain
        if classicon != None:
            break

        # Look through templates if we dont
        else:
            if template:
                try:
                    if template in template_stack:
                        print(f"ERROR: Infinitely recursive template structure. ({tank.name})")
                        input()
                        sys.exit(0)
                        
                    current_template = templates[template]
                    continue
                except KeyError:
                    break
            else:
                break

    if not classicon:
        classicon = "tank"

    if support:
        try:
            wave_icon_dict["support"][classicon] = [wave_icon_dict["support"][classicon][0] + totalcount, False]
        except KeyError:
            wave_icon_dict["support"][classicon] = [totalcount, False]
    else:
        try:
            wave_icon_dict["giant"][classicon] = [wave_icon_dict["giant"][classicon][0] + totalcount, False]
        except KeyError:
            wave_icon_dict["giant"][classicon] = [totalcount, False]



script_path = os.path.abspath(os.path.dirname(__file__))


while True:
    pop_objs = []

    os.chdir(script_path)

    print("Current directory:", os.getcwd())    
    popfilesdir = getInput("Enter the popfiles directory path:", [validateFileString])
    os.chdir(popfilesdir)
    popfilesdir = os.getcwd()

    popfiles = [file for file in os.listdir(popfilesdir) if file.endswith(".pop")]
    
    print(f"Found {len(popfiles)} popfiles in {popfilesdir}")
    for index, file in enumerate(popfiles):
        print(f"[{index + 1}]\t{file}")
    print("\n")

    if not len(popfiles):
        continue

    while True:
        file_indexes = []
        raw_input = getInput("""Enter the file indexes / ranges you want to use, separated by comma:
(Example: 5, 7 - 9, 1) <- Selects 1, 5, 7, 8, and 9""",
                                [validateFileIndexes])

        raw_input = raw_input.split(',')
        for index in raw_input:
            if '-' not in index:
                file_indexes.append(int(index))
            else:
                index = ''.join([char for char in index if char not in string.whitespace])
                mid = index.find('-')
                low = int(index[:mid])
                high = int(index[mid+1:])

                for i in range(low, high + 1):
                    file_indexes.append(i)
            
        if not file_indexes or max(file_indexes) > len(popfiles) or min(file_indexes) < 1:
            print("Invalid file indexes.\n")
            
        else:
            file_indexes.sort()
            print("\nYou selected these files:")
            for index in file_indexes:
                print(f"[{index}]\t{popfiles[index - 1]}")
            print("")
            
            raw_input = getInput("Is this correct?", [validateBoolean])
            print("")

            if raw_input in ["y", "ye", "yes", "1"]:
                break
            

    for index in file_indexes:
        print(f"Parsing {popfiles[index - 1]} ...")
        try:
            pop_objs.append(parsePopFile(popfiles[index - 1]))
            
        except (ValueError, AttributeError) as exception:
            print("\nERROR: Something went wrong while parsing this file.")
            print("Please ensure the file has proper syntax.")
            input()
            sys.exit(0)
        
        print("Finished parsing successfuly.\n")

    raw_input = getInput("Would you like to see the parsed files?", [validateBoolean])
    print("")

    if raw_input in ["y", "ye", "yes", "1"]:
        for pop in pop_objs:
            print(pop)
            raw_input = input("Press enter to continue, or type end to stop viewing.\n")
            if raw_input.lower() == "end":
                break


    os.chdir(script_path)
    print("Current directory:", os.getcwd())
    savedir = getInput("Enter the directory path where you want your wavebars to be saved.", [validateFileString])
    print("")
    
    # Format it into full path
    os.chdir(savedir)
    savedir = os.getcwd()

    tfdir = ""
    while True:
        os.chdir(script_path) 
        print("Current directory:", os.getcwd())
        tfdir = getInput("Enter the directory path of your tf folder.", [validateFileString])

        if not tfdir.endswith("tf"):
            if os.path.isdir(tfdir + "\\tf"):
                tfdir += "\\tf"
            else:
                print("Invalid input. File path is not the tf folder.")
                continue

        # Format it into full path
        os.chdir(tfdir)
        tfdir = os.getcwd()
        
        break


    grab_images = False
    if os.listdir(script_path + "\\materials\\images"):
        raw_input = getInput("\nHave any of your icons changed or have new ones been added? (If so, the program will re-acquire them.)", [validateBoolean])
        print("")

        if raw_input in ["y", "ye", "yes", "1"]:
            grab_images = True

    else:
        grab_images = True


    if grab_images:
        # Clear contents of materials/images
        if os.listdir(script_path + "\\materials\\images"):
            os.chdir(script_path + "\\materials\\images")
            for file in os.listdir(os.getcwd()):
                if os.path.isfile(file):
                    os.remove(file)
                # Just in case
                elif os.path.isdir(file):
                    rmtree(file)

        # Create PNG versions of VTFs from materials/hud in materials/images
        os.chdir(script_path)
        hudpath    = script_path + "\\materials\\hud\\*.vtf"
        outputpath = script_path + "\\materials\\images"
        command    = f'vtfcmd.exe -folder "{hudpath}" -output "{outputpath}" -exportformat "png" -silent'
        os.system(f'cmd /c "echo Copying default VTF files to PNG versions... && cd VTFLIB132/bin/x86 && {command}"')
        
        # Create PNG versions of VTFs from tf/materials/hud in materials/images
        os.chdir(script_path)
        if os.path.isdir(tfdir + "\\materials\\hud"):
            tfhudpath  = tfdir + "\\materials\\hud\\*.vtf"
            outputpath = script_path + "\\materials\\images"
            command    = f'vtfcmd.exe -folder "{tfhudpath}" -output "{outputpath}" -exportformat "png" -silent'
            os.system(f'cmd /c "echo Copying user VTF files to PNG versions... && cd VTFLIB132/bin/x86 && {command}"')


    raw_input = getInput("Do you want to be notified of warnings?", [validateBoolean])
    print("")

    notify_warnings = False
    if raw_input in ["y", "ye", "yes", "1"]:
        notify_warnings = True    

    for fileindex, obj in zip(file_indexes, pop_objs):
        print(f"Generating wavebar for {popfiles[fileindex - 1]} ...\n")

        templates = getTemplates(obj, popfilesdir, popfiles[fileindex - 1], notify_warnings=notify_warnings)
        templates = { template.name.lower() : template for template in templates }
        
        iconstrings = []
        waves       = obj.getWaveSchedule().queryChildren("Wave", recurse=False, case_sensitive_names=False)

        if not waves:
            if notify_warnings:
                print("WARNING: Popfile has no waves, ignoring.\n")
            continue
        else:
            totalcurrency_list = []
            
            # Get icons from WaveSpawns for each Wave
            for index, wave in enumerate(waves):
                iconstrings.append(collections.OrderedDict({
                                        "giant"   : collections.OrderedDict(),
                                        "normal"  : collections.OrderedDict(),
                                        "support" : collections.OrderedDict()
                                   }))

                wavespawns = wave.queryChildren("WaveSpawn", recurse=False, case_sensitive_names=False)
                
                totalcurrency = 0
                
                if not wavespawns:
                    totalcurrency_list.append(totalcurrency)
                    continue
                else:
                    for wavespawn in wavespawns:
                        spawner    = None
                        totalcount = 0
                        support    = False
                        
                        for kv in wavespawn.keyvalues:
                            if not support and kv.equals(KeyValue("Support", None, flags="i")):
                                support = True
                            elif not totalcount and kv.equals(KeyValue("TotalCount", None, flags="i")):
                                try:
                                    totalcount = int(kv.value)
                                except ValueError:
                                    print(f"ERROR: WaveSpawn has invalid TotalCount ({kv.value}).")
                                    print(wavespawn)
                                    input()
                                    sys.exit(0)
                            elif kv.equals(KeyValue("TotalCurrency", None, flags="i")):
                                try:
                                    totalcurrency += int(kv.value)
                                except ValueError:
                                    if notify_warnings:
                                        print(f"WARNING: WaveSpawn has invalid TotalCurrency ({kv.value}).")
                                        print(f"         TotalCurrency for Wave {index + 1} will be incorrect.")
                                        print(wavespawn)
                                    continue
                        
                        for name in ["TFBot", "Tank", "RandomChoice", "Squad"]:
                            spawner = wavespawn.queryChildren(name, recurse=False, case_sensitive_names=False)
                            if spawner:
                                spawner = spawner[0]
                                break

                        if not spawner:
                            if notify_warnings:
                                print("WARNING: WaveSpawn has no Spawner, ignoring.")
                                print(wavespawn)
                            continue
                        else:
                            if spawner.name.lower() == "tfbot":
                                getTFBotIconString(spawner, iconstrings[index], templates, totalcount, support, notify_warnings)

                            elif spawner.name.lower() == "tank":
                                getTankIconString(spawner, iconstrings[index], templates, totalcount, support)
                            
                            elif spawner.name.lower() == "randomchoice":
                                blocks       = spawner.queryChildren("*", recurse=False)
                                blocks       = [block for block in blocks if block.name.lower() in ["tfbot", "tank"]]
                                blocks_count = len(blocks)

                                if not blocks_count:
                                    continue
                                
                                random_totalcounts = getRandIntList(blocks_count, totalcount)
                                
                                for block in blocks:
                                    randindex = random.randint(0, len(random_totalcounts) - 1)
                                    
                                    if block.name.lower() == "tfbot":
                                        getTFBotIconString(block, iconstrings[index], templates, random_totalcounts[randindex], support, notify_warnings)
                                    elif block.name.lower() == "tank":
                                        getTankIconString(block, iconstrings[index], templates, random_totalcounts[randindex], support)
                                    
                                    del random_totalcounts[randindex]

                            elif spawner.name.lower() == "squad":
                                blocks     = spawner.queryChildren("*", recurse=False)
                                tfbotcount = len([True for block in blocks if block.name.lower() == "tfbot"])

                                if not tfbotcount:
                                    continue

                                notified = False
                                for block in blocks:
                                    if block.name.lower() == "tfbot":
                                        count = 0
                                        if totalcount >= tfbotcount:
                                            count = totalcount // tfbotcount

                                        if not count:
                                            if notify_warnings and not notified:
                                                notified = True
                                                print("WARNING: Squad has higher number of TFBot blocks than TotalCount, it will not be displayed.")
                                                print(spawner)


                                        getTFBotIconString(block, iconstrings[index], templates, count, support, notify_warnings)
                                            
                                
                            else:
                                print(f"ERROR: Invalid spawner. ({spawner.name})")
                                input()
                                sys.exit(0)

                        
                totalcurrency_list.append(totalcurrency)

            # Get icons from Mission blocks
            missions = obj.getWaveSchedule().queryChildren("Mission", recurse=False, case_sensitive_names=False)

            for block in missions:
                wave        = 0
                wave_length = 0
                totalcount  = 0
                spawner     = None

                sentrybuster = False
                for kv in block.keyvalues:
                    
                    # Ignore sentry busters
                    if kv.equals(KeyValue("Objective", "DestroySentries", flags="i")):
                        sentrybuster = True
                        break
                    
                    if not wave and kv.equals(KeyValue("BeginAtWave", None, flags="i")):
                        wave = int(kv.value)
                    elif not totalcount and kv.equals(KeyValue("DesiredCount", None, flags="i")):
                        totalcount = int(kv.value)
                    elif not wave_length and kv.equals(KeyValue("RunForThisManyWaves", None, flags="i")):
                        wave_length = int(kv.value)
                        
                if sentrybuster:
                    continue

                for name in ["TFBot", "RandomChoice", "Squad"]:
                    spawner = block.queryChildren(name, recurse=False, case_sensitive_names=False)
                    if spawner:
                        spawner = spawner[0]
                        break
                
                if not wave or not wave_length or not totalcount or not spawner:
                    if notify_warnings:
                        print("WARNING: Mission is not complete.")
                        print(block)
                    continue

                if spawner.name.lower() == "tfbot":
                    for w in iconstrings[wave - 1:(wave - 1) + wave_length]:
                        getTFBotIconString(spawner, w, templates, totalcount, True, notify_warnings)

                elif spawner.name.lower() == "tank":
                    for w in iconstrings[wave - 1:(wave - 1) + wave_length]:
                        getTankIconString(spawner, w, templates, totalcount, True)
			
                elif spawner.name.lower() == "randomchoice":
                    blocks       = spawner.queryChildren("*", recurse=False)
                    blocks       = [block for block in blocks if block.name.lower() in ["tfbot", "tank"]]
                    blocks_count = len(blocks)

                    if not blocks_count:
                        continue
				
                    random_totalcounts = getRandIntList(blocks_count, totalcount)
		
                    for block in blocks:
                        randindex = random.randint(0, len(random_totalcounts) - 1)
					
                        if block.name.lower() == "tfbot":
                            for w in iconstrings[wave - 1:(wave - 1) + wave_length]:
                                getTFBotIconString(block, w, templates, random_totalcounts[randindex], True, notify_warnings)
                        elif block.name.lower() == "tank":
                            for w in iconstrings[wave - 1:(wave - 1) + wave_length]:
                                getTankIconString(block, w, templates, random_totalcounts[randindex], True)
					
                        del random_totalcounts[randindex]

                elif spawner.name.lower() == "squad":
                    blocks     = spawner.queryChildren("*", recurse=False)
                    tfbotcount = len([True for block in blocks if block.name.lower() == "tfbot"])

                    if not tfbotcount:
                        continue

                    notified = False
                    for block in blocks:
                        if block.name.lower() == "tfbot":
                            count = 0
                            if totalcount >= tfbotcount:
                                count = totalcount // tfbotcount

                            if not count:
                                if notify_warnings and not notified:
                                    notified = True
                                    print("WARNING: Squad has higher number of TFBot blocks than TotalCount, it will not be displayed.")
                                    print(spawner)

                            for w in iconstrings[wave - 1:(wave - 1) + wave_length]:
                                getTFBotIconString(block, w, templates, count, True, notify_warnings)
							
				
                else:
                    print(f"ERROR: Invalid spawner. ({spawner.name})")
                    input()
                    sys.exit(0)

            # Debug
            """
            for index, wave in enumerate(iconstrings):
                print(f"Wave {index + 1}" + "\n" + "=" * 25)
                for group, dic in wave.items():
                    print(group)
                    for k, v in dic.items():
                        print("\t", k, ":", v)
                print()
            print()
            """

            os.chdir(script_path + "\\materials\\hud")
            
            iconimages = []


            def getVMTTexture(filename):
                with open(filename, "r") as file:
                    for line in file:
                        terms = parseLineTerms(line)
                        if '"$basetexture"' in map(lambda term: term.lower(), terms):
                            for term in terms:
                                if "leaderboard_class_" in term.lower():                               
                                    index = -1
                                    for char in reversed(term):
                                        if char == "\\" or char == "/":
                                            index += 1
                                            break
                                        index -= 1

                                    return term[index:].replace('"', "")

                    return "debugempty"

                        
            # Replace icon strings with icon Image objects
            for index, wave in enumerate(iconstrings):
                iconimages.append(collections.OrderedDict({
                                    "giant"   : collections.OrderedDict(),
                                    "normal"  : collections.OrderedDict(),
                                    "support" : collections.OrderedDict()
                                  }))
                for group, icondict in wave.items():
                    for icon, data in icondict.items():
                        os.chdir(script_path + "\\materials\\hud")
                        texturename = "debugempty"

                        if icon != "debugempty":
                            filename = "leaderboard_class_" + icon + ".vmt"
                            if filename in os.listdir(os.getcwd()):
                                texturename = getVMTTexture(filename)
                            else:
                                os.chdir(tfdir + "\\materials\\hud")
                                if filename in os.listdir(os.getcwd()):
                                    texturename = getVMTTexture(filename)

                                
                        os.chdir(script_path + "\\materials\\images")
                        image = None

                        try:
                            image = Image.open(texturename + ".png")
                        except OSError:
                            if texturename != "debugempty":
                                try:
                                    image = Image.open("debugempty.png")
                                except OSError:
                                    print("ERROR: images/debugempty.png missing.")
                                    input()
                                    sys.exit(0)
                            else:
                                print("ERROR: images/debugempty.png missing.")
                                input()
                                sys.exit(0)
                                
                        iconimages[index][group][icon] = [image, data]


            os.chdir(savedir)

            createWaveScheduleBar(iconimages, popfiles[fileindex - 1], totalcurrency_list).save(popfiles[fileindex - 1][:-4] + ".png")

