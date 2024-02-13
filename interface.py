import curses
from curses.textpad import rectangle
from issues import check_md_tags_headers, write_header
from inspection import inspect_tags, remove_tags
from suggest import demo_suggest_tags, append_tags
from utils import explore_dir


def disp_suggest_tags(stdscr, vault, mds, ticked, n_suggestions=3):
    mds = [md for md, tick in zip(mds, ticked) if tick]
    tag_ticks = [[False for _ in range(n_suggestions)] for _ in mds]
    tags = {}
    for md in mds:
        tags[md] = demo_suggest_tags(vault, md, n_suggestions)

    stdscr.clear()
    stdscr.addstr(0, 1, 'Current Vault: '+ vault, curses.A_UNDERLINE)
    stdscr.addstr(1, 1, "Select tags to add:", colors['YELLOW_AND_BLACK'])
    stdscr.addstr(curses.LINES - 3, len("[s]:select/deselect") + 2, "[a]:add to file")
    stdscr.addstr(curses.LINES - 3, 1 , "[s]:select/deselect")
    stdscr.addstr(curses.LINES - 2, 1 , "[t]:back")
    stdscr.addstr(curses.LINES - 2, curses.COLS - 10, "[q]:quit")

    selection_md_id = 0
    selection_tag_id = 0
    while True:
        try:
            key = stdscr.getkey()
        except:
            key = None

        if key == "KEY_UP":
            selection_md_id-=1
        elif key == "KEY_DOWN":
            selection_md_id+=1
        elif key == "KEY_LEFT":
            selection_tag_id-=1
        elif key == "KEY_RIGHT":
            selection_tag_id+=1

        elif key == "s":
            tag_ticks[selection_md_id][selection_tag_id] = not tag_ticks[selection_md_id][selection_tag_id]

        elif key == "t":
            disp_md_selection(stdscr, vault, ticked)

        elif key == "a":
            tags_to_add = {md: [tag for tag, tick in zip(tags[md], ticked) if tick] for md, ticked in zip(mds, tag_ticks)}
            append_tags(vault, mds, tags_to_add)
            stdscr.clear()
            stdscr.addstr(0, 1, 'Current Vault: '+ vault, curses.A_UNDERLINE)
            stdscr.addstr(1, 1, "Operation successful.", colors['YELLOW_AND_BLACK'])
            stdscr.addstr(curses.LINES - 2, curses.COLS - 10, "[q]:quit")
            stdscr.addstr(curses.LINES - 2, 1, "[any]:back")
            stdscr.refresh()
            stdscr.nodelay(False)
            stdscr.getkey()
            disp_md_selection(stdscr, vault, ticked)

        elif key == "q":
            quit()
            

        if len(mds)>0:
            selection_tag_id = selection_tag_id % n_suggestions
            selection_md_id = selection_md_id % len(mds)
            row = 1
            md_id = 0
            for md in mds:
                row+=1
                stdscr.addstr(row, 1, f"{md[:-3]}:", colors["CYAN_AND_BLACK"])
                row+=1
                stdscr.addstr(row, 1, "")
                
                tag_id = 0
                for tag in tags[md]:
                    if (selection_tag_id==tag_id)&(selection_md_id==md_id):

                        if tag_ticks[md_id][tag_id]:
                            color = colors["GREEN_AND_WHITE"]
                        else:
                            color = colors["RED_AND_WHITE"]
                    else:
                        if tag_ticks[md_id][tag_id]:
                            color = colors["GREEN_AND_BLACK"]
                        else:
                            color = colors["RED_AND_BLACK"]
                    
                    stdscr.addstr(f"#{tag}", color)
                    stdscr.addstr(f" ")
                    tag_id+=1
                row+=1
                md_id+=1

        stdscr.refresh()

#TODO: check if header is at the end of the file
#TODO: tool to fix tags formatting
def disp_check_headers(stdscr, vault, mds, ticked):
    mds = [md for md, tick in zip(mds, ticked) if tick]

    stdscr.clear()
    stdscr.addstr(0, 1, 'Current Vault: '+ vault, curses.A_UNDERLINE)
    no_tags, multi_tags = check_md_tags_headers(vault, mds)
    
    row = 1
    if not (no_tags or multi_tags):
        stdscr.addstr(row, 1, "No issues found!", colors["GREEN_AND_BLACK"]); row+=1

    if no_tags:
        stdscr.addstr(row, 1, "No Tags header found in:", colors["GREEN_AND_BLACK"]); row+=1
        for md in no_tags:
            stdscr.addstr(row, 1, f" * {md[:-3]}"); row+=1

    if multi_tags:
        if no_tags:
            row+=1
        stdscr.addstr(row, 1, "Multiple Tags headers found in:", colors["GREEN_AND_BLACK"]); row+=1
        for md in multi_tags:
            stdscr.addstr(row, 1, f" * {md[:-3]}"); row+=1

    stdscr.addstr(curses.LINES - 3, 1 , "[f]:fix headers")
    stdscr.addstr(curses.LINES - 2, 1 , "[c]:back")
    stdscr.addstr(curses.LINES - 2, curses.COLS - 10, "[q]:quit")

    stdscr.refresh()
    while True:
        try:
            key = stdscr.getkey()
        except:
            key = None

        if key == "c":
            disp_md_selection(stdscr, vault, ticked)
        
        elif key == "f":
            disp_fix_headers(stdscr, vault, mds, ticked)

        elif key == "q":
            quit()


def disp_fix_headers(stdscr, vault, mds, ticked):
    mds = [md for md, tick in zip(mds, ticked) if tick]
    stdscr.clear()
    stdscr.addstr(0, 1, 'Current Vault: '+ vault, curses.A_UNDERLINE)
    no_tags, multi_tags = check_md_tags_headers(vault, mds)
    
    row = 1
    if no_tags:
        for md in no_tags:
            write_header(vault, md)
        
        stdscr.addstr(row, 1, "Headers added!", colors["YELLOW_AND_BLACK"]); row+=1

    if multi_tags:
        if no_tags:
            row+=1
        stdscr.addstr(row, 1, "Multiple Tags headers found in:", colors["GREEN_AND_BLACK"]); row+=1
        for md in multi_tags:
            stdscr.addstr(row, 1, f" * {md[:-3]}"); row+=1
        row+=1
        stdscr.addstr(row, 1, "Multi-tag issues must be solved manually", colors['RED_AND_BLACK']); row+=1
        

    stdscr.addstr(curses.LINES - 2, 1 , "[c]:back")
    stdscr.addstr(curses.LINES - 2, curses.COLS - 10, "[q]:quit")

    stdscr.refresh()
    while True:
        try:
            key = stdscr.getkey()
        except:
            key = None

        if key == "c":
            disp_md_selection(stdscr, vault, ticked)
        
        elif key == "q":
            quit()


def disp_inspect_tags(stdscr, vault, mds, ticked):
    mds = [md for md, tick in zip(mds, ticked) if tick]
    tags = inspect_tags(vault, mds)
    tag_ticks = [[True for _ in range(len(tags[md]))] for md in mds]
    stdscr.clear()
    stdscr.addstr(0, 1, 'Current Vault: '+ vault, curses.A_UNDERLINE)
    stdscr.addstr(1, 1, "Existing tags:", colors['YELLOW_AND_BLACK'])

    stdscr.addstr(curses.LINES - 3, len("[s]:select/deselect") + 2 , "[r]:remove tags in ")
    stdscr.addstr("red", colors["RED_AND_BLACK"])
    stdscr.addstr(curses.LINES - 3, 1, "[s]:select/deselect")
    stdscr.addstr(curses.LINES - 2, 1 , "[i]:back")
    stdscr.addstr(curses.LINES - 2, curses.COLS - 10, "[q]:quit")

    stdscr.refresh()
    selection_md_id = 0
    selection_tag_id = 0
    while True:
        try:
            key = stdscr.getkey()
        except:
            key = None

        if key == "KEY_UP":
            selection_md_id-=1
        elif key == "KEY_DOWN":
            selection_md_id+=1
        elif key == "KEY_LEFT":
            selection_tag_id-=1
        elif key == "KEY_RIGHT":
            selection_tag_id+=1

        elif key == "s":
            tag_ticks[selection_md_id][selection_tag_id] = not tag_ticks[selection_md_id][selection_tag_id]

        elif key == "i":
            disp_md_selection(stdscr, vault, ticked)
        elif key == "r":
            tags_to_remove = {md: [tag for tag, tick in zip(tags[md], ticked) if not tick] for md, ticked in zip(mds, tag_ticks)}
            stdscr.clear()
            stdscr.addstr(2, 1, "The following tags will be removed:", colors["YELLOW_AND_BLACK"])
            row = 2
            for md in mds:
                if len(tags_to_remove[md])>0:
                    row+=1; stdscr.addstr(row, 1, f"{md[:-3]}:", colors["CYAN_AND_BLACK"])
                    row+=1; stdscr.addstr(row, 1, "")
                    
                    for tag in tags_to_remove[md]:
                        stdscr.addstr(f'{tag} ', colors["RED_AND_BLACK"])

            disp_confirmation_screen(stdscr, vault, ticked, remove_tags, vault, mds, tags_to_remove)

        elif key == "q":
            quit()
    
        if len(mds)>0:
            try:
                selection_tag_id = selection_tag_id % len(tags[mds[selection_md_id]])
            except:
                if key == "KEY_UP":
                    selection_md_id-=1
                elif key == "KEY_DOWN":
                    selection_md_id+=1

            selection_md_id = selection_md_id % len(mds)
            row = 1
            md_id = 0
            for md in mds:
                row+=1
                stdscr.addstr(row, 1, f"{md[:-3]}:", colors["CYAN_AND_BLACK"])
                row+=1
                stdscr.addstr(row, 1, "")
                
                tag_id = 0
                for tag in tags[md]:
                    if (selection_tag_id==tag_id)&(selection_md_id==md_id):

                        if tag_ticks[md_id][tag_id]:
                            color = colors["GREEN_AND_WHITE"]
                        else:
                            color = colors["RED_AND_WHITE"]
                    else:
                        if tag_ticks[md_id][tag_id]:
                            color = colors["GREEN_AND_BLACK"]
                        else:
                            color = colors["RED_AND_BLACK"]
                    
                    stdscr.addstr(f"{tag}", color)
                    stdscr.addstr(f" ")
                    tag_id+=1
                row+=1
                md_id+=1


def disp_confirmation_screen(stdscr, vault, ticked, proceed_fn, *fn_args):
    stdscr.addstr(0, 1, 'Current Vault: '+ vault, curses.A_UNDERLINE)
    stdscr.addstr(1, 1, "Are you sure you want to proceed?", colors['YELLOW_AND_BLACK'])
    stdscr.addstr(curses.LINES - 2, len("[y]:yes") + 2, "[n]:no")
    stdscr.addstr(curses.LINES - 2, 1 , "[y]:yes")
    stdscr.addstr(curses.LINES - 2, curses.COLS - 10, "[q]:quit")

    stdscr.refresh()
    
    while True:
        try:
            key = stdscr.getkey()
        except:
            key = None

        if key == "y":
            proceed_fn(*fn_args)
            stdscr.clear()
            stdscr.addstr(0, 1, "Operation successful.", colors['YELLOW_AND_BLACK'])
            stdscr.addstr(curses.LINES - 2, curses.COLS - 10, "[q]:quit")
            stdscr.addstr(curses.LINES - 2, 1, "[any]:back")

            stdscr.refresh()
            stdscr.nodelay(False)
            stdscr.getkey()
            disp_md_selection(stdscr, vault, ticked)

        elif key == "n":
            disp_md_selection(stdscr, vault, ticked)
        
        elif key == "q":
            quit()


def disp_md_selection(stdscr, vault, ticked):
    stdscr.clear()
    mds, _ = explore_dir(vault)
    mds = mds if isinstance(mds, list) else [mds]
    if ticked is None:
        ticked = [True for _ in mds]
    height, width = stdscr.getmaxyx()

    stdscr.addstr(0, 1, 'Current Vault: ' + vault, curses.A_UNDERLINE)
    stdscr.addstr(1, 1, "Select files to process:", colors['YELLOW_AND_BLACK'])
    stdscr.refresh()
    
    stdscr.nodelay(True)
    selection = 0
    while True:
        try:
            key = stdscr.getkey()
        except:
            key = None

        if key == "KEY_UP":
            selection-=1
        elif key == "KEY_DOWN":
            selection+=1

        elif key == "s":
            ticked[selection] = not ticked[selection]
        elif key == "a":
            if all(ticked):
                ticked = [False for _ in mds]
            else:
                ticked = [True for _ in mds]

        elif key == "c":
            disp_check_headers(stdscr, vault, mds, ticked)

        elif key == "i":
            disp_inspect_tags(stdscr, vault, mds, ticked)

        elif key == "t":
            disp_suggest_tags(stdscr, vault, mds, ticked)

        elif key == "q":
            quit()

        selection = selection % len(mds)
        row = 2
        for i, md in enumerate(mds):
            pre = '+' if ticked[i] else '-'
            pre_color = colors['GREEN_AND_BLACK'] if ticked[i] else colors['RED_AND_BLACK']
            stdscr.addstr(row, 1, pre, pre_color)
            stdscr.addstr(row, 3, md[:-3], curses.A_STANDOUT if selection == i else colors["CYAN_AND_BLACK"]) 
            row+=1

        stdscr.addstr(height - 3, (len("[s]:select/deselect [a]:select/deselect all") + 2), "[t]:suggest tags")
        stdscr.addstr(height - 3, 1, "[c]:check headers")
        stdscr.addstr(height - 3, len("[s]:select/deselect") + 2, "[i]:inspect tags")
        stdscr.addstr(height - 2, 1, "[s]:select/deselect")
        stdscr.addstr(height - 2, len("[s]:select/deselect") + 2, "[a]:select/deselect all")
        stdscr.addstr(height - 2, width - 10, "[q]:quit")
        
        stdscr.refresh()


def quit():
    curses.endwin()
    exit()


stdscr = curses.initscr()
stdscr.clear()
stdscr.keypad(True)

curses.curs_set(0)
curses.noecho()
curses.cbreak()

colors = dict()
curses.start_color()

curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
colors['GREEN_AND_BLACK'] = curses.color_pair(1)

curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
colors['MAGENTA_AND_BLACK'] = curses.color_pair(2)

curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
colors['CYAN_AND_BLACK'] = curses.color_pair(3)

curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
colors['YELLOW_AND_BLACK'] = curses.color_pair(4)

curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
colors['RED_AND_BLACK'] = curses.color_pair(5)

curses.init_pair(6, curses.COLOR_GREEN, curses.COLOR_WHITE)
colors['GREEN_AND_WHITE'] = curses.color_pair(6)

curses.init_pair(7, curses.COLOR_RED, curses.COLOR_WHITE)
colors['RED_AND_WHITE'] = curses.color_pair(7)

vault = r'D:\Documents (HD)\Obsidian Vaults\Software'
disp_md_selection(stdscr, vault, None)