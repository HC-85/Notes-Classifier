import os

def inspect_tags(vault, mds):
    tags = {}
    for md in mds:
        target = os.path.join(vault, md)
        with open(rf"{target}", 'r', encoding='utf-8') as file:
            line = file.readline()
            while line:
                if line == '###### Tags\n':
                    tags[md] = file.read().split()
                    
                line = file.readline()
    return tags


def remove_tags(vault, mds, tags_to_remove):
    for md in mds:
        target = os.path.join(vault, md)
        with open(target, 'r+', encoding = 'utf-8') as file:
            line = file.readline()
            while line:
                if line == '###### Tags\n':
                    tag_loc = file.tell()
                    tags = file.read()
                    for tag in tags_to_remove[md]:
                        tags = tags.replace(tag, '').strip()
                    file.seek(tag_loc)
                    file.write(tags)
                    file.truncate(file.tell())
                    break
                line = file.readline()