
import sys
from misc import *

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

    block_name = ""
    parent_block_name = ""
    block_keyvalues = []
    parent_keyvalue = []

    print("QUERY SELECTION\n" + "-" * 15 + "\n")
    while True:
        block_name = getInput("Enter the name of the block you want to modify.\n" +
                              "* wildcard denotes any amount of any character. (including none).",
                              [validateWildString])
        print("")

        if not block_name:
            print("Invalid input.\n")
            continue

        parent_block_name = getInput("Enter the name of the block's parent.\n" +
                                     "Press enter if none\n" +
                                     "* wildcard denotes any amount of any character. (including none)",
                                     [validateWildString])
        print("")

        if not parent_block_name:
            parent_block_name = None

        block_keyvalues = getKeyValues("Enter the keyvalues the block has.")

        parent_keyvalues = getKeyValues("Enter the keyvalues the block's parent has.")

        total_matched_blocks = {}
        for index, pop in zip(file_indexes, pop_objs):
            print(f"Searching {popfiles[index - 1]} for matches ...")
            matched_blocks = pop.queryChildren(block_name, block_keyvalues, parent_block_name, parent_keyvalues)
            print(f"Found {len(matched_blocks)} matches.\n")

            total_matched_blocks[index] = matched_blocks

        raw_input = getInput("Would you like to see the matched blocks?", [validateBoolean])
        print("")

        if raw_input in ["y", "ye", "yes", "1"]:
            for index, blocks in total_matched_blocks.items():
                print(popfiles[index - 1])
                print('-' * len(popfiles[index - 1]))
                
                for block in blocks:
                    print(block)

                raw_input = input("Press enter to continue, or type end to stop viewing.\n")
                if raw_input == "end":
                    break

        raw_input = getInput("Would you like to respecify query parameters?", [validateBoolean])
        print("")

        if raw_input in ["y", "ye", "yes", "1"]:
            continue

        break


    while True:
        print("SELECTION MODIFICATION\n" + "-" * 22 + "\n")

        print("""[0] View Selected Blocks
[1] Add KeyValues
[2] Remove KeyValues
[3] Modify KeyValues
[4] Finish
""")
        raw_input = input()
        print("")
        
        raw_input = raw_input.lower()
        keyvalues = []

        if raw_input in ["0", "view", "selected", "blocks"]:
            for index, blocks in total_matched_blocks.items():
                print(popfiles[index - 1])
                print('-' * len(popfiles[index - 1]))
                
                for block in blocks:
                    print(block)
                    
                raw_input = input("Press enter to continue, or type end to stop viewing.\n")
                if raw_input == "end":
                    break
                
        elif raw_input in ["1", "add"]:
            keyvalues = getKeyValues("Enter the keyvalues you want to add to the selected blocks.")

            if keyvalues:
                for index, blocks in total_matched_blocks.items():
                    for block in blocks:
                        block.add(keyvalues)

                    print(f"Finished editing {popfiles[index - 1]} ...\n")
                        
                print("Finished adding the keyvalues to the selected blocks.\n")
                
        elif raw_input in ["2", "remove"]:
            keyvalues = getKeyValues("Enter the keyvalues you want to remove from the selected blocks.")

            if keyvalues:
                for blocks in total_matched_blocks.values():
                    for block in blocks:
                        block.remove(keyvalues)

                print("Removed the keyvalues from the selected blocks.\n")
                        
        elif raw_input in ["3", "modify"]:
            keyvalues = getKeyValues("Enter the keyvalues you want to modify in the selected blocks.")

            new_keyvalues = []
            if keyvalues:
                for kv in keyvalues:
                    string = ""
                    if isinstance(kv.value, Block):
                        string = str(kv.value)

                        print(string)
                        print("-" * len(string.split('\n')[0]))
                    else:
                        
                        string = kv.key
                        if kv.value:
                            string += " " + kv.value
                        if kv.tag:
                            string += " " + kv.tag

                        print(string)
                        print("-" * len(string))
                            
                    new_keyvalues.append(getKeyValues("What keyvalues do you want to replace this with?"))
                    print("")   

                for index, blocks in total_matched_blocks.items():
                    for block in blocks:
                        for old, new in zip(keyvalues, new_keyvalues):
                            block.replaceKey(old, new)

                    print(f"Finished editing {popfiles[index - 1]} ...\n")

                print("Finished modifying keyvalues in all selected blocks.\n")
                        
                
        elif raw_input in ["4", "finish"]:
            break
        
        else:
            print("Invalid input.\n")
            continue
        

    overwrite = getInput("Should the files be overwritten with the current changes?", [validateBoolean])

    if overwrite in ["y", "ye", "yes", "1"]:
        for index, obj in zip(file_indexes, pop_objs):
            with open(popfiles[index - 1], "r+") as file:
                try:
                    backup = file.read()
                    
                    file.seek(0)
                    file.truncate(0)

                    print("\nWriting file: ", popfiles[index - 1])
                    file.write(str(obj))
                    
                except (TypeError, ValueError) as exception:
                    print("\nERROR: Failed to write popfile!")
                    file.write(backup)
                    sys.exit(0)

        print("\nSaved all files\n\n")

    else:
        save = getInput("Should the files be saved elsewhere then?", [validateBoolean])

        if save in ["y", "ye", "yes", "1"]:
            
            os.chdir(script_path)
            print("Current directory:", os.getcwd())
            savedir = getInput("Enter the directory path.", [validateFileString])
            os.chdir(savedir)
            savedir = os.getcwd()

            for index, obj in zip(file_indexes, pop_objs):
                with open(popfiles[index - 1], "w+") as file:
                    try:
                        backup = file.read()
                    
                        file.seek(0)
                        file.truncate(0)

                        print("\nWriting file: ", popfiles[index - 1])
                        file.write(str(obj))
                        
                    except (TypeError, ValueError) as exception:
                        print("ERROR: Failed to write popfile!\n")
                        file.write(backup)
                        sys.exit(0)

            print("\nSaved all files to copies\n\n")
        
    
                    
