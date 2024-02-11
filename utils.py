import os
import re
import numpy as np
from typing import List, Union

def explore_dir(path):
    files = os.listdir(path)
    md_files = []
    subdirs = []
    for file in files:
        if file.endswith('.md'):
            md_files.append(file)
        elif os.path.isdir(os.path.join(path, file)):
            subdirs.append(file)
    return md_files, subdirs


def check_md_tags_headers(vault_path:str, source: Union[List[str], str]):
    md_files = source if isinstance(source, list) else [source]

    no_tags = []
    multi_tags = []    
    for md_name in md_files:
        tag_flag = 0
        with open(os.path.join(vault_path, md_name), 'r', encoding='utf-8') as f:
            text = f.read()

        for line in text.split('\n'):
            if line == '###### Tags':
                tag_flag += 1
                continue

        if tag_flag == 0:
            no_tags.append(md_name)
        elif tag_flag > 1:
            multi_tags.append(md_name)
        
    return no_tags, multi_tags


#TODO: check for repeated tags
def check_tags_headers(vault_path:str, source: Union[List[str], str], explore_subdirs=False, no_tags = [], multi_tags = [], depth = 0):
    try:
        files_path = os.path.join(os.getcwd(), source)
        is_dir = os.path.isdir(files_path)
    except:
        is_dir = False

    if  is_dir:
        md_files, subdirs = explore_dir(source)
    else:
        md_files = source if isinstance(source, list) else [source]
        subdirs = []

    for md_name in md_files:
        tag_flag = 0
        with open(os.path.join(vault_path, md_name), 'r', encoding='utf-8') as f:
            text = f.read()

        for line in text.split('\n'):
            if line == '###### Tags':
                tag_flag += 1
                continue

        if tag_flag == 0:
            no_tags.append(md_name)
        elif tag_flag > 1:
            multi_tags.append(md_name)
    
    if explore_subdirs & (subdirs != []):
        for subdir in subdirs:
            check_tags_headers(os.path.join(path, subdir), explore_subdirs, no_tags, multi_tags, depth+1)
    
    if depth == 0:
        if no_tags:
            print(f"No tags header found in:")
            for md_name in no_tags:
                print(f" - {md_name[:-3]}")
            print("Make sure these are under '###### Tags' header.")

        if multi_tags:
            print(f"Multiple tags headers found in:")
            for md_name in multi_tags:
                print(f" - {md_name[:-3]}")
        
        return no_tags, multi_tags


def inspect_tags(vault, mds):
    tags = {}
    for md in mds:
        target = os.path.join(vault, md)
        with open(target, 'r', encoding='utf-8') as file:
            line = file.readline()
            while line:
                if line == '###### Tags\n':
                    tags[md] = file.read().split()
                    
                line = file.readline()
    return tags


def inspect_md_tags(vault_path:str, md: Union[List[str], str]):
    tagset = set()
    tag_flag = False
    with open(os.path.join(vault_path, md), 'r', encoding='utf-8') as f:
        text = f.read()
    
    for line in text.split('\n'):
        if tag_flag:
            tags = re.findall(r'#([^ ]+)', line)
            if tags:
                tagset = tagset.union(set(tags))
            else:
                break

        else:
            if line == '###### Tags':
                tag_flag = True
                continue

    return sorted(list(tagset))


def tags_relevance(path):
    md_files, subdirs = explore_dir(path)
    
    tagmultiset = dict()
    for md in md_files:
        with open(os.path.join(path, md), 'r', encoding='utf-8') as f:
            text = f.read()

        tag_flag = False
        for line in text.split('\n'):
            if line == '###### Tags':
                tag_flag = True
                continue
            if tag_flag:
                tags = re.findall(r'#([^ ]+)', line)
                if tags:
                    for tag in tags:
                        tagmultiset[tag] = tagmultiset.get(tag, 0)*1.2 + np.log(len(text))

    tagmultiset = dict(sorted(tagmultiset.items(), key=lambda item: item[1], reverse=True))
    for tag, count in tagmultiset.items():
        print(f'{tag}:{count}')


def demo_suggest_tags(vault, md, n_suggestions):
    from numpy.random import default_rng
    rng = default_rng()
    existing_tags = inspect_md_tags(vault, md) 
    new_tags = []

    while len(new_tags)<n_suggestions:
        tag_ids = rng.integers(0, 10, n_suggestions)
        sug_tags = [f'Tag{id}' for id in tag_ids]
        for tag in sug_tags:
            if (tag not in existing_tags) and (tag not in new_tags):
                new_tags.append(tag)
                if len(new_tags) == n_suggestions:
                    break
    return new_tags


def write_header(vault = 'Software', md = 'test.md'):
    target = os.path.join(vault, md)
    with open(target, 'a') as file:
        file.write('\n###### Tags\n')


def write_tags(vault, md, tags):
    target = os.path.join(vault, md)
    with open(target, 'r') as file:
        text = file.readlines()
        for line in text:
                pass
        if line[-1:]!='\n':
            md.write('\n')         
    
    with open(target, 'a') as md:
        hash_tagged = [f'#{tag} ' for tag in tags]
        md.write(str().join(hash_tagged))

#TODO: find way to not store the whole file in memory using IO stream stuff just for fun
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
