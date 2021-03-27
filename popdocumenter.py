
import collections
from string import whitespace
from misc import *


# Modify keyvalues in modified_keyvalues with old base values if they are different
def modifyWithDifferences(modified_keyvalues, base_keyvalues):
    def keyvalueInList(keyvalue, keyvalues):
        for kv in keyvalues:
            if kv.key == keyvalue.key:
                return True
        else:
            return False

    # Add commented out keyvalues to modified keyvalues if they exist in the base but not the modified          
    for kv2 in base_keyvalues:
        if not keyvalueInList(kv2, modified_keyvalues):
            for kv1 in modified_keyvalues:
                if kv1.key == "//":
                    if isinstance(kv1.value, str) and kv1.value.count(kv2.key):
                        break
            else:
                modified_keyvalues.append(KeyValue("// ", kv2.key + " " + kv2.value))

    # Change values in modified to <old base value> --> <new value> if different from base           
    for kv1 in modified_keyvalues:
        if kv1.key != "//":
            for kv2 in base_keyvalues:
                if kv1.key == kv2.key and not kv1.equals(kv2):
                     kv1.value = kv2.value  + " --> " + kv1.value
                     break


# Get a keyvalue in a block
def getBlockKeyValue(block, keyvalue):
    if isinstance(block, Block):
        for kv in block.keyvalues:
            if kv.equals(keyvalue):
                return kv
    return None
        

script_path = os.path.abspath(os.path.dirname(__file__))

while True:
    pop_objs = []

    os.chdir(script_path)

    print("Current directory:", os.getcwd())    
    path = getInput("Enter the directory path:", [validateFileString])
    os.chdir(path)
    path = os.getcwd()

    popfiles = [file for file in os.listdir(path) if file.endswith(".pop")]
    
    print(f"Found {len(popfiles)} popfiles in {path}")
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
    savedir = getInput("Enter the directory where you want the doc files to be saved.", [validateFileString])

    # Format it into full path
    os.chdir(savedir)
    savedir = os.getcwd()
    

    os.chdir(script_path)
    print("\nCurrent directory:", os.getcwd())
    upgradesdir = getInput("Enter the directory where custom upgrades files are located.", [validateFileString])

    # Format it into full path
    os.chdir(upgradesdir)
    upgradesdir = os.getcwd()
            
    os.chdir(upgradesdir)


    write_strings = []
    for index, obj in zip(file_indexes, pop_objs):

        # Get WaveSchedule (or whatever the hipsters call it since it can annoyingly be called anything)
        waveschedule = None
        for kv in obj.keyvalues:
            if isinstance(kv.value, Block):
                waveschedule = kv.value

        if not waveschedule:
            print(f"\nERROR: {popfiles[index - 1]} is incomplete.")
            print("Please ensure the file has proper syntax.")
            input()
            sys.exit(0)

        waveschedule_names = [
                                "ClassLimit", "ItemWhitelist", "ItemBlacklist", "PlayerAttributes",
                                "ItemAttributes", "PlayerAddCond", "ExtendedUpgrades"
                             ]
        
        wave_names         = ["PlayerAttributes", "PlayerAddCond"]


        waveschedule_doc_objs  = collections.OrderedDict({ name: waveschedule.queryChildren(name, recurse=False) for name in waveschedule_names })
        
        wave_objs     = waveschedule.queryChildren("Wave", recurse=False)
        wave_doc_objs = [ collections.OrderedDict({name: wave.queryChildren(name, recurse=False) for name in wave_names}) for wave in wave_objs ]


        write_string = '\n\n'.join([str(block) for blocks in waveschedule_doc_objs.values() for block in blocks])


        upgrade_files = [kv.value for kv in waveschedule.keyvalues if kv.key == "CustomUpgradesFile"]
        
            
        for index, file in enumerate(upgrade_files):
            if isinstance(file, str):
                upgrade_files[index] = file.replace('"', '')
                
        
        if upgrade_files:
            os.chdir(upgradesdir)
            custom_upgrades = [parsePopFile(file) if os.path.isfile(file) else None for file in upgrade_files]

            os.chdir(script_path)
            upgrades = parsePopFile("mvm_upgrades.txt")
            
            
            for name, file_obj in zip(upgrade_files, custom_upgrades):
                try:
                    # Is the file different from the base?
                    if not file_obj.equals(upgrades, True):
                        file_obj_itemupgrades   = file_obj.queryChildren('"ItemUpgrades"')[0]
                        file_obj_playerupgrades = file_obj.queryChildren('"PlayerUpgrades"')[0]

                        upgrades_itemupgrades   = upgrades.queryChildren('"ItemUpgrades"')[0]
                        upgrades_playerupgrades = upgrades.queryChildren('"PlayerUpgrades"')[0]


                        if file_obj_itemupgrades.equals(upgrades_itemupgrades, True):
                            file_obj.remove([KeyValue(file_obj_itemupgrades.name, file_obj_itemupgrades)])
                            file_obj_itemupgrades = None

                        if file_obj_playerupgrades.equals(upgrades_playerupgrades, True):
                            file_obj.remove([KeyValue(file_obj_playerupgrades.name, file_obj_playerupgrades)])
                            file_obj_playerupgrades = None


                        # Remove upgrade blocks that are the same as default
                        for obj1, obj2 in zip([file_obj_itemupgrades, file_obj_playerupgrades],
                                              [upgrades_itemupgrades, upgrades_playerupgrades]):
                            if obj1:
                                for kv1, kv2 in zip(obj1.keyvalues, obj2.keyvalues):
                                    attribute1 = getBlockKeyValue(kv1.value, KeyValue('"attribute"', None))
                                    
                                    # Just in case order is changed
                                    if kv1.key != kv2.key:
                                        for kv3 in obj2.keyvalues[1:]:
                                            attribute2 = getBlockKeyValue(kv3.value, KeyValue('"attribute"', None))
                                            if (attribute1 and attribute2) and attribute1.equals(attribute2):
                                                if kv1.equals(kv3, True):
                                                    obj1.remove([kv1])
                                    else:
                                        attribute2 = getBlockKeyValue(kv2.value, KeyValue('"attribute"', None))
                                        if (attribute1 and attribute2) and attribute1.equals(attribute2):
                                            if kv1.equals(kv2, True):
                                                obj1.remove([kv1])

                        # Remove comments from "upgrades" and file_obj
                        for block in [file_obj, file_obj.queryChildren('"upgrades"')[0]]:
                            removelist = []
                            for kv in block.keyvalues:
                                if kv.key == "//":
                                    removelist.append(kv)
                            block.remove(removelist)

                        # Add previous default values to changed keyvalues
                        for obj1, obj2 in zip([file_obj_itemupgrades, file_obj_playerupgrades],
                                              [upgrades_itemupgrades, upgrades_playerupgrades]):
                            if obj1:
                                for kv1 in obj1.keyvalues:
                                    for kv2 in obj2.keyvalues:
                                        if kv1.key == kv2.key:
                                            if kv1.key != "//" or kv2.key != "//":
                                                attribute1 = getBlockKeyValue(kv1.value, KeyValue('"attribute"', None))
                                                attribute2 = getBlockKeyValue(kv2.value, KeyValue('"attribute"', None))
                                                
                                                if (attribute1 and attribute2) and attribute1.equals(attribute2):
                                                    modifyWithDifferences(kv1.value.keyvalues, kv2.value.keyvalues)

                        file_obj.queryChildren('"upgrades"')[0].name = '"' + name + '"'

                                               
                        write_string += "\n\n" + str(file_obj)

                except (ValueError, AttributeError, TypeError) as exception:
                    print(f"\nERROR: Something went wrong while parsing {name}.")
                    print("Please ensure the file exists or has proper syntax.")
                    input()
                    sys.exit(0)

        if write_string:
            write_string += "\n"
        for index, wave in enumerate(wave_doc_objs):
            keyvalues = [KeyValue(kv2.name, kv2) for kv1 in wave.values() for kv2 in kv1]
            if keyvalues:
                block = Block(None, "Wave", keyvalues, comment="Wave " + str(index + 1))

                write_string += str(block)

        write_string = write_string.strip()
        write_strings.append(write_string)

        
    os.chdir(savedir)
    
    # Write to files
    i = 0
    for findex, string in zip(file_indexes, write_strings):
        name = popfiles[findex - 1]
        name = name[:-4] + "_changelog.txt"
        with open(name, "w+") as file:
            file.seek(0)
            file.truncate(0)

            print("\nWriting file:", os.getcwd() + "\\" + name)
            file.write(write_strings[i])

        i += 1

    print("\nSaved all files\n\n")
                
