import string
import copy
import os

help_text_keyvalues = """
Each keyvalue should be on it's own line.
Type end on it's own line when you're finished, or type reset to enter the keyvalues again.
You can type end by its self if you have nothing to enter.


Syntax: ["-"] <key> [value] [tag] [comment] ["block"]
Usage Notes:
    Key is the only required parameter.
    If you want to specify a parameter but don't want to fill out the ones before it, type None for them.
    E.g: <key> None None // my comment

    The block parameter tells the program that this is a block and you want to enter additional keyvalues.
    The - parameter tells the program that you DON'T want this keyvalue in your results.
    (Make sure there's a space between - and the key.)
    

Examples:
------------------------------------------
"damage bonus" 2
"fire rate bonus" 0.75 None // not fast
end
------------------------------------------

------------------------------------------
Gravity
end
------------------------------------------

------------------------------------------
end
------------------------------------------

------------------------------------------
Class Scout
AddCond None [$SIGSEGV] None "block"
CharacterAttributes None None // These are two are blocks "block"
end
------------------------------------------

------------------------------------------
Class Demoman
- WeaponRestrictions
end
------------------------------------------

------------------------------------------
Class
- Class Scout
- Class Spy
end
------------------------------------------
"""



class Block:
    def __init__(self, parent, name, keyvalues=[], tag=None, comment=None, is_base=False):
        self.parent  = parent
        self.name    = name

        if keyvalues:
            self.keyvalues = copy.deepcopy(keyvalues)
        else:
            self.keyvalues = []

        if tag == "None":
            tag = None
        self.tag = tag

        if comment == "None":
            comment = None
        elif comment and "//" not in comment:
            comment = "// " + comment
        self.comment = comment

        self.is_base = is_base


    # Return string representation of block
    def __str__(self):
        string = ""

        if self.comment and not self.is_base:
            string += self.comment + '\n'
        
        if not self.is_base:
            string += self.name

            if self.tag:
                string += " " + self.tag

            string += "\n{\n"
        
        for kv in self.keyvalues:
            if isinstance(kv.value, Block):
                if self.is_base:
                    string += str(kv.value)
                else:
                    lines = str(kv.value).split('\n')[:-1]
                    string += '\n'.join(['\t' + line for line in lines]) + '\n'

            else:
                if not self.is_base:
                    string += "\t"
                    
                string += kv.key

                if kv.key != "//":
                    string += " "

                if kv.value:
                    string += kv.value
                
                if kv.tag:
                    string += " " + kv.tag
                    
                if kv.comment:
                    string += " " + kv.comment
                    
                string += "\n"

        if not self.is_base:
            string += "}\n"
            

        return string


    # Return a list of matching child blocks filtered by arguments
    def queryChildren(self, name, keyvalues=[], parent_name=None, parent_keyvalues=[], recurse=True):     
        filtered_blocks = []

        # Check if a string with a wildcard and a regular string are equal
        def areNamesEqual(wildcard_name, name):        
            if '*' not in wildcard_name:
                if wildcard_name == name:
                    return True
                else:
                    return False
            else:
                terms = wildcard_name.split('*')
                if name.startswith(terms[0]) and name.endswith(terms[-1]):
                    return True
                else:
                    return False
        
        # First find all initial blocks with name
        for kv in self.keyvalues:
            if isinstance(kv.value, Block):
                block = kv.value
                
                if areNamesEqual(name, block.name):
                    filtered_blocks.append(block)
                    
                if recurse:
                    childblocks = block.queryChildren(name, keyvalues, parent_name, parent_keyvalues, recurse)
                    if childblocks:
                        filtered_blocks.extend(childblocks)

        # Filter for specified parent
        if parent_name:
            filter_list = []
            
            for block in filtered_blocks:
                if block.parent:
                    if areNamesEqual(parent_name, block.parent.name):
                        filter_list.append(block)

            filtered_blocks = filter_list[:]

        # Filter for specified keyvalues
        if keyvalues:
            filter_list = []
            for block in filtered_blocks:
               if keyValuesIn(block.keyvalues, keyvalues):
                   filter_list.append(block)

            filtered_blocks = filter_list[:]

        # Filter for specified parent keyvalues
        if parent_keyvalues:
            filter_list = []
            for block in filtered_blocks:
                if block.parent:
                    if keyValuesIn(block.parent.keyvalues, parent_keyvalues):
                        filter_list.append(block)
                    
            filtered_blocks = filter_list[:]
            
        return filtered_blocks


    # Add keyvalues to block
    def add(self, keyvalues):
        for kv1 in keyvalues:
            if isinstance(kv1.value, Block):
                createParentStructure(self, kv1.value)
                    
            for index, kv2 in enumerate(self.keyvalues):
                if kv1.equals(kv2):      
                    self.keyvalues[index] = kv1
                    break
            else:
                self.keyvalues.append(kv1)


    # Remove keyvalues from block
    def remove(self, keyvalues):
        newlist = []
        
        for kv1 in self.keyvalues:
            for kv2 in keyvalues:

                # If they're a block with the same name, compare them with keyValuesIn, otherwise KeyValue's equals method
                if (isinstance(kv1.value, Block) and isinstance(kv2.value, Block)
                    and kv1.key == kv2.key
                    and keyValuesIn(kv1.value.keyvalues, kv2.value.keyvalues)) or kv1.equals(kv2):
                    
                    break
            else:
                newlist.append(kv1)

        self.keyvalues = newlist


    # Replace a key[ value] in block with keyvalues
    def replaceKey(self, keyvalue, keyvalues):
        for kv1 in self.keyvalues:
            
            # If they're a block with the same name, compare them with keyValuesIn, otherwise KeyValue's equals method
            if (isinstance(kv1.value, Block) and isinstance(keyvalue.value, Block)
                and kv1.key == keyvalue.key
                and keyValuesIn(kv1.value.keyvalues, keyvalue.value.keyvalues)) or kv1.equals(keyvalue):
                
                self.remove([kv1])

                for kv2 in keyvalues:
                    if isinstance(kv2.value, Block):
                        createParentStructure(self, kv2.value)
                
                self.add(keyvalues)


    # Use KeyValue.equals to compare blocks
    def equals(self, block, nocomment=False):
        return KeyValue("", self).equals(KeyValue("", block), nocomment)


class KeyValue:
    def __init__(self, key, value, tag=None, comment=None, negated=False):
        self.key = key

        if value == "None":
            value = None
        self.value = value

        if tag == "None":
            tag = None
        self.tag = tag

        if comment == "None":
            comment = None
        elif comment and "//" not in comment:
            comment = "// " + comment
        self.comment = comment

        self.negated = negated # Negated is only taken into account when querying for blocks to modify

    def __str__(self):
        string = self.key

        if self.key != "//":
            string += " "

        if self.value:
            string += str(self.value)
                
        if self.tag:
            string += " " + self.tag
                    
        if self.comment:
            string += " " + self.comment

        return string

    
    # Check if two keyvalues are strictly equal, block values must be exactly the same
    def equals(self, keyvalue, nocomments=False):
        if nocomments:
            if self.key == "//" or keyvalue.key == "//":
                return True
            
        kvs1 = [self.key, self.value, self.tag]
        kvs2 = [keyvalue.key, keyvalue.value, keyvalue.tag]

        # Don't compare values or tags if one of them doesn't exist
        if not keyvalue.value or not self.value:
            kvs1.remove(self.value)
            kvs2.remove(keyvalue.value)
        if not keyvalue.tag or not self.tag:
            kvs1.remove(self.tag)
            kvs2.remove(keyvalue.tag)

        for j, k in zip(kvs1, kvs2):
            if isinstance(j, Block) and isinstance(k, Block):
                jkvs = j.keyvalues
                kkvs = k.keyvalues
                
                if nocomments:
                    jkvs = [kv for kv in jkvs if kv.key != "//"]
                    kkvs = [kv for kv in kkvs if kv.key != "//"]
                
                if len(jkvs) != len(kkvs) or j.name != k.name:
                    return False
                
                temp = copy.deepcopy(kkvs)

                # Remove keyvalues that match from temp
                for kv1 in jkvs:
                    for kv2 in temp:
                        if kv1.key == kv2.key:
                            if kv1.equals(kv2, nocomments):
                                temp.remove(kv2)

                            break

                # If it's empty they're the same
                if temp:
                    return False
                else:
                    return True
                                
            else:
                if j != k:
                    return False

        return True


# Set the parent of child to parent, recurse for any blocks within child to set their parents
def createParentStructure(parent, child):
    child.parent = parent

    for kv in child.keyvalues:
        if isinstance(kv.value, Block):
            createParentStructure(child, kv.value)


# Find tags which are not in strings or a comment
# Tags with quotations are not supported, however // can be a tag
def findValidTags(line, tag):
    if len(line) < len(tag):
        return []
    
    in_string  = False
    indexes    = []

    tag_index = 0
    for index, char in enumerate(line):
        # Check char for comment
        if char == '/' and not in_string:
            if tag != "//":
                if index != len(line) - 1:
                    if line[index + 1] == '/':
                        break # In comment, no need to check the rest of the line

        # Check char for string      
        elif char == '"':
            in_string = True if not in_string else False
            continue
            
        # Check char for tag
        if not in_string:
            if char == tag[tag_index]:
                if tag_index == len(tag) - 1:
                    indexes.append(index - tag_index)
                    tag_index = 0
                else:
                    tag_index += 1

    return indexes


# Return whether or not all of keyvalues are not in source
def keyValuesNotIn(source, keyvalues):
    for kv1 in source:
        for kv2 in keyvalues:

            # Note: no recursion into sub blocks, only return False if the current block has keyvalues
            if kv1.equals(kv2):
                return False

    return True
    

# Return whether or not all of keyvalues are in source
def keyValuesIn(source, keyvalues):
    negated   = [kv for kv in keyvalues if kv.negated]
    keyvalues = [kv for kv in keyvalues if not kv.negated]

    if not keyValuesNotIn(source, negated):
        return False
    
    # Length checks before we commit to ludicrously lengthy looping (not really, but alliteration is fun)
    if len(keyvalues) > len(source):
        return False
    elif not len(keyvalues):
        return True

    keyvalues = copy.deepcopy(keyvalues)

    # Remove from keyvalues if they match with source
    for kv1 in source:
        for kv2 in keyvalues:
            if isinstance(kv1.value, Block):
                if kv1.key == kv2.key: # Are block names the same
                    if keyValuesIn(kv1.value.keyvalues, kv2.value.keyvalues):
                        keyvalues.remove(kv2)
                        
            else:
                if kv1.equals(kv2):
                    keyvalues.remove(kv2)

    # If it's empty all of keyvalues are in source
    if keyvalues:
        return False
    else:
        return True
            

# Parse a popfile into an object model (return a base block)
def parsePopFile(filepath):
    with open(filepath, "r+") as file:
        
        key         = None
        val         = None
        tag         = None
        comment     = None
        in_term     = False
        end_term    = False
        in_string   = False
        start_index = None

        tag_ignore_index = -1


        populator     = Block(None, "Populator", is_base=True)
        current_block = populator
        
        for line in file:
            
            # Allow the whitespace logic to always run at the end of a line
            if line[-1] not in string.whitespace:
                line += "\n"

            # Grab the comment from the line if it exists, along with it's start index
            comment_indexes = findValidTags(line, "//")
            comment_index   = -1
            if comment_indexes:
                comment_index = comment_indexes[0]
                comment       = line[comment_index:-1]

            
            for index, char in enumerate(line):
                
                # Don't do anything if we're inside the comment
                if comment_index != -1:
                    if index >= comment_index and index != len(line) - 1:
                        continue

                # Don't do anything if we're inside the tag
                if tag_ignore_index != -1:
                    if index != tag_ignore_index:
                        continue
                    else:
                        tag_ignore_index = -1
                        continue

                # Create a block if we have a key ready
                if char == "{":
                    if not in_string:
                        if in_term or key:
                            if in_term:
                                key = line[start_index:index]
                                
                            block = Block(current_block, key, tag=tag, comment=comment)
                            current_block.keyvalues.append(KeyValue(key, block, tag, comment))
                            current_block = block

                            in_term = False
                            key     = None
                            tag     = None
                            comment = None

                # Finish editing the current block
                elif char == "}":
                    if not in_string:
                        if in_term:
                            val = line[start_index:index]
                            current_block.keyvalues.append(KeyValue(key, val, tag, comment))

                            key     = None
                            val     = None
                            comment = None
                            tag     = None
                            in_term = False
                            
                        current_block = current_block.parent

                elif char not in string.whitespace:
                    if not in_term:
                        start_index = index
                        in_term     = True
                    
                    if char == '"':
                        in_string = True if not in_string else False


                elif char in string.whitespace:
                    if in_term and not in_string:    
                        end_term = True
                    elif not in_term and comment:
                        if index == len(line) - 1:
                            current_block.keyvalues.append(KeyValue("//", comment[2:]))
                            comment = None


                if end_term:
                    if "[$" in line:
                        indexes = findValidTags(line[index:], "[$")
                        if len(indexes) != 0:
                            i = indexes[0]
                            i = index + i

                            # If there's anything between our last term and the tag, don't do anything yet
                            for char in line[index:i]:
                                if char not in string.whitespace:
                                    break
                                            
                            else:
                                # Get the index for the end of the tag
                                k = -1
                                for j, char in enumerate(line[i:]):
                                    if char == "]":
                                        k = i + j
                                        break
                                    
                                if k == -1:
                                    raise ValueError
                                        
                                tag = line[i:k + 1]
                                tag_ignore_index = k

                            
                    if not key:
                        # // directly next to key (specifically block names)
                        if comment and index > comment_index:
                            key = line[start_index:comment_index]
                            
                            current_block.keyvalues.append(KeyValue("//", comment[2:]))
                            comment = None
                        else:
                            key = line[start_index:index]
                            
                    elif not val:
                        if comment and index > comment_index:
                            val = line[start_index:comment_index]
                        else:
                            val = line[start_index:index]
                            
                        current_block.keyvalues.append(KeyValue(key, val, tag, comment))
                        
                        key     = None
                        val     = None
                        comment = None
                        tag     = None

                    
                    in_term  = False
                    end_term = False


        # After parsing file:

        # Extraneous terms
        if (key or tag) and not val:
            raise ValueError

        
        return populator


# Validate text input with list of test functions
def validateTestFncs(inp, testFncs):
    for testFnc in testFncs:
        if testFnc(inp):
            continue
        else:
            return False

    return True


# Get a single line of input
def getInput(prompt, testFncs=None):
    while True:
        print(prompt)
        
        inp = input()

        if testFncs:
            if validateTestFncs(inp, testFncs):
                return inp
            else:
                print("\nInvalid input.\n")
        else:
            return inp

# Get multi-line input
def getMultiInput(prompt, escape_texts=[], testFncs=None, help_text=None):
    print("Type help for any additional information or usage examples.")
    print(prompt)

    lines = []
    while True:
        inp = input()

        if inp in escape_texts:
            if testFncs:
                if validateTestFncs('\n'.join(lines), testFncs):
                    break
                else:
                    lines = []
                    print("Invalid input.\n")
                    print("Type help for any additional information or usage examples.")
                    print(prompt)
            else:
                break

        elif inp == "help":
            if help_text != None:
                print(help_text)

        elif inp == "reset":
            print("Type help for any additional information or usage examples.")
            print(prompt)

            lines = []
            continue

        else:
            lines.append(inp)

    return '\n'.join(lines)


# Parse a line of text for it's terms (essentially a dumb mini version of parsePopFile)
# Used for getting keyvalues from user input
def parseLineTerms(line):

    if not line:
        return []

    # Make sure any term at the end of the line gets added
    if line[-1] not in string.whitespace:
        line = line + '\n'
        
    in_string   = False
    in_tag      = False
    in_term     = False
    in_tag      = False
    start_index = None

    terms = []
    for index, char in enumerate(line):  
        if char == '/':
            if not in_string:
                if index != len(line) - 1:
                    if line[index + 1] == '/':
                        if in_term:
                            terms.append(line[start_index:index])
                            in_term = False

                        if line[-1] in string.whitespace:
                            terms.append(line[index:-1])
                        else:
                            terms.append(line[index:])

                        break

        elif char == '[':
            if not in_string and not in_term:
                if index != len(line) - 1:
                    if line[index + 1] == '$':
                        in_tag = True
                        start_index = index



        if char in string.whitespace:
            if in_term:
                if not in_string and not in_tag:
                    terms.append(line[start_index:index])
                    in_term = False         

        elif char not in string.whitespace:
            if char == '"':
                in_string = True if not in_string else False
                
            if in_tag:
                if char == ']':
                    terms.append(line[start_index:index+1])
                    in_tag = False
                    
            elif not in_term:
                in_term = True
                start_index = index


    return terms


# Prompt user for keyvalues
def getKeyValues(prompt, allow_only_key=True):
    keyvalues = []
    
    while True:
        keyvalues = getMultiInput(prompt, ["end"], help_text=help_text_keyvalues)
        print("")
        
        if not keyvalues:
            return keyvalues 

        keyvalues = keyvalues.split('\n')
        keyvalues = [parseLineTerms(line) for line in keyvalues]

        block_indexes   = []
        negated_indexes = []
        invalid_input   = False

        for index, kv in enumerate(keyvalues):
            if kv[0] == '-':
                if len(kv) > 1:
                    negated_indexes.append(index)
                    keyvalues[index] = kv[1:]
                else:
                    print("\nInvalid input.\n")
                    invalid_input = True
                    break
                    
            if '"block"' in kv:
                keyvalues[index] = kv[:-1]
                block_indexes.append(index)
            else:
                # There is a comment
                if len(kv) >= 4:
                    comment = kv[3]
                        
                    
                    if '"block"' in comment:
                        found_index = comment.rfind('"block"')
                        comment = comment[:found_index]
                        comment = comment.rstrip()

                        keyvalues[index][3] = comment
                        block_indexes.append(index)
                        
        if invalid_input:
            continue

        if allow_only_key:
            if any(map(lambda kv: len(kv) < 1 or len(kv) > 4, keyvalues)):
                print("\nInvalid input.\n")
                continue
            
            else:
                keyvalues = [KeyValue(*kv) if len(kv) > 1 and kv[1] else KeyValue(*kv, value=None) for kv in keyvalues]
        else:
            if any(map(lambda kv: len(kv) < 2 or len(kv) > 4, keyvalues)):
                print("\nInvalid input\n")
                continue
            
            else:
                keyvalues = [KeyValue(*kv) for kv in keyvalues]


        if block_indexes:
            for index in block_indexes:
                kv = keyvalues[index]
                prompt = f"\n{kv.key}\n{'-'*len(kv.key)}\nEnter the keyvalues the block has."
                kv.value = Block(None, kv.key, getKeyValues(prompt), kv.tag, kv.comment)

        if negated_indexes:
            for index in negated_indexes:
                keyvalues[index].negated = True
                

        return keyvalues


# Validate input is a valid filepath
def validateFileString(path):
    return os.path.isdir(path) or os.path.isfile(path)


# Validate file index range is valid
def validateFileIndexes(inp):
    inp = ''.join([char for char in inp if char not in string.whitespace])
    inp = inp.split(',')
    
    for index in inp:
        if not index.isdigit():
            if '-' in index:
                i = index.find('-')
                if not index[:i].isdigit():
                    return False
                if i == len(index) - 1:
                    return False
                if not index[i+1:].isdigit():
                    return False
            else:
                return False

    return True


# Validate input is a boolean value
def validateBoolean(inp):
    if inp.lower() in ["y", "ye", "yes", "n", "no", "0", "1"]:
        return True

    return False


# Validate input has 0 or 1 wildcard (*)
def validateWildString(inp):
    return False if inp.count('*') > 1 else True



if __name__ == "__main__":
    pass
