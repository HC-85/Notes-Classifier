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


def add_tags(vault, mds, tags_to_add):
    for md in mds:
        target = os.path.join(vault, md)
        with open(target, 'r+', encoding = 'utf-8') as file:
            line = file.readline()
            while line:
                if line == '###### Tags\n':
                    tag_loc = file.tell()
                    tags = file.read().split()
                    new_tags = [f'#{tag}' for tag in tags_to_add[md]]
                    tags.extend(new_tags)
                    file.seek(tag_loc)
                    for tag in tags:
                        file.write(f" {tag}")
                line = file.readline()
