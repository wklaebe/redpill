# -*- coding: utf-8 -*-
# encoding=utf8

import re
import sys
import json
import time
import datetime
import curses
from matrix_client.client import MatrixClient, Room
import sys
reload(sys)
sys.setdefaultencoding('utf8')

#import requests
#if "packages" in requests:
#from requests import requests
#requests.packages.urllib3.disable_warnings()

def log(obj, filename='redpill.log'):
    with open(filename, 'a') as the_file:
        the_file.write(str(obj) + "\n")

def loadCredentials(filename):
    global server, base_url, username, access_token, password
    with open(filename) as json_data:
        data = json.load(json_data)

    server = data["home_server"]
    base_url = data.get("base_url", "https://{}".format(server))
    username = data["username"]
    access_token = data.get("access_token", None)
    password = None if access_token else data["password"]

def processMessage(obj):
    global room, rooms, lastEventRoom, room_keys

    log(obj, 'redpill-event.log')

    if "room_id" in obj:
        if room != all_rooms:
            room = obj["room_id"]

        if "room_id" not in rooms:
            room_keys.append(obj["room_id"])


    if ("room_id" in obj and obj["room_id"] != lastEventRoom and "type" in obj and
                obj["type"] != "m.presence" and obj["type"] != "m.typing" and obj["type"] != "m.room.topic"
                and obj["type"] != "m.room.name"):
        lastEventRoom = obj["room_id"]
        obj2 = {}
        obj2["type"] = "m.roomchange"
        obj2["user_id"] = " "
        obj2["content"] = {}
        obj2["content"]["body"] = obj["room_id"]
        obj2["room_id"] = obj["room_id"]
        obj2["content"]["msgtype"] = "m.text"
        rooms[all_rooms].events.append(obj2)
    rooms[all_rooms].events.append(obj)

def getFirstRoomAlias(r):
    name = r.room_id
    if len(r.aliases) > 0:
        name = r.aliases[0]
    return name  #.encode('utf-8')


def start(stdscr):
    global server, base_url, username, access_token, password
    global size, room, data, rooms, endTime, rooms, all_rooms, lastEventRoom, room_keys

    curses.curs_set(0)
    curses.use_default_colors()
    size = stdscr.getmaxyx()

    stdscr.addstr(0, 0, "loading...")
    stdscr.refresh()
    loadCredentials("./credentials.json")

    client = MatrixClient(base_url, token=access_token, user_id='@{}:{}'.format(username, server))
    if access_token is None:
        access_token = client.login_with_password(
            username,
            password,
            size[0])

    rooms = client.get_rooms()

    all_rooms = "all rooms"
    rooms[all_rooms] = Room(client, all_rooms)

    rooms[all_rooms].events = []
    room_keys = list(rooms.keys())
    room = all_rooms  #room_keys[1] # "all_rooms"
    nextRoom = 1
    endTime = client.end

    curses.halfdelay(10)
    maxDisplayName = 24
    displayNamestartingPos = 20
    PAD_COMMENTS = True
    pause = False

    client.add_listener(processMessage)
    client.start_listener_thread()

    curses.echo()
    stdscr.keypad(True)
    inputBuffer = ""
    lastEventRoom = all_rooms
    the_room_to_post_to = None  # store the last room we saw before we started typing

    while(True):
        size = stdscr.getmaxyx()
        maxChars = size[1] - 1 - len(username) - 3

        stdscr.clear()

        # we want NAME aka ALIAS[0] (ROOM_ID)
        # or 2nd choice: ALIAS[0] (ROOM_ID)
        # or fallback: ROOM_ID
        line = str(room)

        if line == all_rooms:
            pass
        elif rooms[room].name is None:
            if len(rooms[room].aliases) > 0 and rooms[room].aliases[0] != room:
                line = rooms[room].aliases[0] + " (" + line + ")"
        else:
            if len(rooms[room].aliases) > 0 and rooms[room].aliases[0] != room:
                line = rooms[room].name + " aka " + getFirstRoomAlias(rooms[room]) + " (" + line + ")"
            else:
                if rooms[room].name != room:
                    line = rooms[room].name + " (" + line + ")"

        #line.encode("utf-8")
        if rooms[room].topic is not None:
            line += " · topic: " + rooms[room].topic

        stdscr.addstr(
            0, 0, (
                "redpill v0.7 · screen size: " + str(size) + " · chat size: "
                + str(len(rooms[room].events)) + " · room: " + str(line) + " the variables: room: " + room + " last: "
                + lastEventRoom
            ), curses.A_UNDERLINE
        )

        current = len(rooms[room].events) - 1

        if True:
            y = 1
            if current >= 0:

                # TODO: something when the first event is a typing event
                currentLine = size[0] - 1

                # input
                space = ""
                for i in range(size[1] - 1):
                    space += " "
                stdscr.addstr(currentLine, 0, space, curses.A_DIM)
                stdscr.addstr(currentLine, 0, "<" + username + ">", curses.A_DIM)
                stdscr.addstr(currentLine - 1, 0, space, curses.A_UNDERLINE)

                for event in reversed(rooms[room].events):
                    if event["type"] == "m.typing":
                    #if True:
                        continue  # do something clever
                    elif event["type"] == "m.presence":
                    #if True:
                        continue  # do something clever

                    elif event["type"] == "m.roomchange":
                        room_id = event["room_id"]
                        #lin = (str(rooms[room_id].name) + " aka " + getFirstRoomAlias(rooms[room_id]) + " (" +
                        #    rooms[room_id].room_id + ")")
                        line = room_id
                        if line == all_rooms:
                            pass
                        elif rooms[line].name is None:
                            if len(rooms[room_id].aliases) > 0 and rooms[room_id].aliases[0] != room_id:
                                line = rooms[room_id].aliases[0] + " (" + line + ")"
                        else:
                            if len(rooms[room_id].aliases) > 0 and rooms[room_id].aliases[0] != room_id:
                                line = rooms[room_id].name + " aka " + getFirstRoomAlias(rooms[room_id]) + " (" + line + ")"
                            else:
                                if rooms[room_id].name != room_id:
                                    line = rooms[room_id].name + " (" + line + ")"

                        #if rooms[room].topic is not None:
                        #    line += " · topic: " + rooms[room].topic

                        currentLine -= 1
                        stdscr.addstr(currentLine, 0, "Event(s) from " + line, curses.A_DIM)


                    else:
                        #currentLine = size[0] - y
                        currentLine -= 1

                        if currentLine < 3:  # how many lines we want to reserve
                            break
                        #if currentLine == 5:
                        #    currentLine -= 1
                        y += 1
                        if "origin_server_ts" in event:
                            convertedDate = datetime.datetime.fromtimestamp(
                                int(
                                    event["origin_server_ts"] / 1000)
                                ).strftime('%Y-%m-%d %H:%M:%S')

                        # assumption: body == normal message
                        length = 0
                        if "user_id" in event:
                            length = len(
                                event["user_id"]
                            )
                        if "body" in event["content"]:

                            rawText = event["content"]["body"].encode('utf-8')

                            if event["content"]["msgtype"] == "m.emote":
                                if len(rawText) > 0 and rawText[0] == " ":
                                    rawText = rawText[1:]

                            linesNeeded = (displayNamestartingPos + maxDisplayName + 3 + len(rawText)) / size[1]
                            lin = (displayNamestartingPos + maxDisplayName + 3 + len(rawText))

                            #if currentLine == size[0] - 2:
                            #    stdscr.addstr(currentLine, 0, str(lin) + " " + str(size[1]) + " " + str(linesNeeded) + "  ", curses.A_UNDERLINE)
                            #else:
                            #    stdscr.addstr(currentLine, 0, str(lin) + " " + str(size[1]) + " " + str(linesNeeded) + "  ")



                            linesNeeded = 0

                            buf = ""
                            lineByLineText = []
                            first = True
                            bufSinceLastWord = ""
                            for char in rawText:
                                if True: #for char in line:

                                    bufSinceLastWord += char

                                    if char == '\n':
                                        linesNeeded += 1
                                        buf += bufSinceLastWord

                                        if PAD_COMMENTS or first:
                                            linesNeeded += (displayNamestartingPos + maxDisplayName + 3 + len(buf)) / size[1]
                                        else:
                                            linesNeeded += len(buf) / size[1]

                                        first = False
                                        lineByLineText.append(buf)
                                        buf = ""
                                        bufSinceLastWord = ""
                                    else:
                                        if ((PAD_COMMENTS and (displayNamestartingPos + maxDisplayName + 3 + len(buf + bufSinceLastWord)) == size[1] - 1)
                                            or (not PAD_COMMENTS and (len(buf + bufSinceLastWord)) == size[1] - 1)):

                                        #if (displayNamestartingPos + maxDisplayName + 3 + len(buf + bufSinceLastWord)) == size[1] - 1:
                                            if len(buf) == 0:
                                                buf += bufSinceLastWord
                                                bufSinceLastWord = ""

                                            if char.isspace():
                                                buf += bufSinceLastWord
                                                lineByLineText.append(buf)
                                                bufSinceLastWord = ""
                                                buf = ""
                                            else:
                                                lineByLineText.append(buf)
                                                buf = bufSinceLastWord
                                                bufSinceLastWord = ""
                                            linesNeeded += 1

                                    if char.isspace():
                                        buf += bufSinceLastWord
                                        bufSinceLastWord = ""

#                                if (displayNamestartingPos + maxDisplayName + 3 + len(buf + bufSinceLastWord)) == size[1] - 1:
                                if ((PAD_COMMENTS and (displayNamestartingPos + maxDisplayName + 3 + len(buf + bufSinceLastWord)) == size[1] - 1)
                                   or (not PAD_COMMENTS and (len(buf + bufSinceLastWord)) == size[1] - 1)):

                                    buf += bufSinceLastWord
                                    bufSinceLastWord = ""
                                    lineByLineText.append(buf)
                                    linesNeeded += 1
                                    buf = ""
                                    #elif char == ' ':   # skip all whitespace
                                    #    self.X += 1
                            buf += bufSinceLastWord
                            lineByLineText.append(buf)
                            linesNeeded += (displayNamestartingPos + maxDisplayName + 3 + len(buf)) / size[1]
                            buf = ""

                            currentLine -= linesNeeded
                            if currentLine - linesNeeded < 2:  # how many lines we want to reserve
                                break

                            if currentLine == size[0] - 2:
                                stdscr.addstr(currentLine, 0, str(lin) + " " + str(size[1]) + " " + str(linesNeeded) + "  ", curses.A_UNDERLINE)
                            else:
                                stdscr.addstr(currentLine, 0, str(lin) + " " + str(size[1]) + " " + str(linesNeeded) + "  ")

                            #for i in range(linesNeeded):


                            if PAD_COMMENTS:
                                pad = displayNamestartingPos + maxDisplayName + 3


                                #if linesNeeded == 0:
                                linesNeeded += 1

                                for i in range(linesNeeded):
                                    buf = rawText[:size[1] - pad]
                                    rawText = rawText[size[1] - pad:]


                                    if currentLine + i == size[0] - 2:
                                        stdscr.addstr(
                                            currentLine + i, displayNamestartingPos +
                                            maxDisplayName + 3, lineByLineText[i],
                                            curses.A_BOLD + curses.A_UNDERLINE
                                        )
                                    else:
                                        try:
                                            stdscr.addstr(
                                                currentLine + i, displayNamestartingPos +
                                                maxDisplayName + 3, lineByLineText[i],
                                                curses.A_BOLD
                                            )
                                        except:
                                            e = sys.exc_info()[0]
                                            print("Error: unable to start thread. " + str(e))
                                            stdscr.addstr(1, 0, str(e))



                            else:
                                # TODO: need to split this out to get proper underline
                                if currentLine == size[0] - 2:
                                    stdscr.addstr(
                                        currentLine, displayNamestartingPos +
                                        maxDisplayName + 3, rawText,
                                        curses.A_BOLD + curses.A_UNDERLINE
                                    )
                                else:
                                    stdscr.addstr(
                                        currentLine, displayNamestartingPos +
                                        maxDisplayName + 3, rawText,
                                        curses.A_BOLD
                                    )

                            usern = event["user_id"]

                            if length > maxDisplayName:
                                usern = usern[:maxDisplayName - 3] + "..."

                            if event["content"]["msgtype"] == "m.emote":

                                usern = "* " + usern
                                if currentLine == size[0] - 2:
                                    stdscr.addstr(
                                        currentLine, displayNamestartingPos + max(0,  maxDisplayName - length),
                                        str(usern),
                                        curses.A_UNDERLINE + curses.A_BOLD
                                    )
                                else:
                                    stdscr.addstr(
                                        currentLine, displayNamestartingPos + max(0,  maxDisplayName - length),
                                        str(usern),
                                        curses.A_BOLD
                                    )
                            else:
                                usern = "<" + usern + ">"
                                if currentLine == size[0] - 2:
                                    stdscr.addstr(
                                        currentLine, displayNamestartingPos + max(0,  maxDisplayName - length),
                                        str(usern),
                                        curses.A_UNDERLINE
                                    )
                                else:
                                    stdscr.addstr(
                                        currentLine, displayNamestartingPos + max(0,  maxDisplayName - length),
                                        str(usern)
                                    )

                            if currentLine == size[0] - 2:
                                stdscr.addstr(currentLine, 0, convertedDate, curses.A_UNDERLINE)
                            else:
                                stdscr.addstr(currentLine, 0, convertedDate)

                            #if currentLine == size[1]:  # last line
                            #    stdscr.addstr(
                            #        currentLine, displayNamestartingPos +
                            #        maxDisplayName + 3, buf[:size[1] -
                            #        (displayNamestartingPos + maxDisplayName + 4)],
                            #         curses.A_BOLD
                            #    )
                            #else:
                            #    stdscr.addstr(
                            #        currentLine, displayNamestartingPos +
                            #        maxDisplayName + 3, buf,
                            #        curses.A_BOLD
                            #    )

                        # membership == join/leave events
                        elif "membership" in event["content"]:
                            buf = " invited someone"
                            if event["content"]["membership"] == "invite":
                                if "state_key" in event:
                                    buf = " invited " + event["state_key"]
                            elif event["content"]["membership"] == "join":
                                buf = " has joined"
                            elif event["content"]["membership"] == "leave":
                                buf = " has left"

                            if length > maxDisplayName:
                                if currentLine == size[0] - 2:
                                    stdscr.addstr(
                                        currentLine,
                                        displayNamestartingPos + 1,
                                        str(event["user_id"]),
                                        curses.A_DIM + curses.A_UNDERLINE
                                    )
                                    stdscr.addstr(
                                        currentLine,
                                        displayNamestartingPos + length + 1,
                                        buf,
                                        curses.A_DIM + curses.A_UNDERLINE
                                    )
                                else:
                                    stdscr.addstr(
                                        currentLine,
                                        displayNamestartingPos + 1,
                                        str(event["user_id"]),
                                        curses.A_DIM
                                    )
                                    stdscr.addstr(
                                        currentLine,
                                        displayNamestartingPos + length + 1,
                                        buf,
                                        curses.A_DIM
                                    )

                            else:
                                if currentLine == size[0] - 2:
                                    stdscr.addstr(
                                        currentLine,
                                        displayNamestartingPos + 1 +
                                        maxDisplayName - length,
                                        str(event["user_id"]),
                                        curses.A_DIM + curses.A_UNDERLINE
                                    )
                                    stdscr.addstr(
                                        currentLine,
                                        displayNamestartingPos + maxDisplayName + 1,
                                        buf,
                                        curses.A_DIM + curses.A_UNDERLINE
                                    )
                                else:
                                    stdscr.addstr(
                                        currentLine,
                                        displayNamestartingPos + 1 +
                                        maxDisplayName - length,
                                        str(event["user_id"]),
                                        curses.A_DIM
                                    )
                                    stdscr.addstr(
                                        currentLine,
                                        displayNamestartingPos + maxDisplayName + 1,
                                        buf,
                                        curses.A_DIM
                                    )

                    current -= 1
        if pause:
            stdscr.addstr(
                int(size[0] / 2) - 1,
                int(size[1] / 2),
                "          ",
                curses.A_REVERSE
            )
            stdscr.addstr(
                int(size[0] / 2),
                int(size[1] / 2),
                "  PAUSED  ",
                curses.A_REVERSE
            )
            stdscr.addstr(
                int(size[0] / 2) + 1,
                int(size[1] / 2),
                "          ",
                curses.A_REVERSE
            )
        try:
            stdscr.addstr(size[0] - 1, len(username) + 3, inputBuffer[-maxChars:])
        except:
            e = sys.exc_info()[0]
            print("Error: unable to start thread. " + str(e))
            stdscr.addstr(1, 0, str(e))

        stdscr.refresh()

 #       getInput(stdscr)

#def getInput(stdscr):
 #   if True:
        try:

            c = stdscr.getch(size[0] - 1, len(username) + 3)
            #c = stdscr.getkey(size[0] - 1, len(username) + 3)

            #stri = stdscr.getstr(size[0] - 1, len(username) + 3, 10)
            if c == -1:
                stdscr.addstr(1, 0, "timeout")
            else:
                if c <= 256 and c != 10 and c != 9: ## enter and tab
                    inputBuffer += chr(c)
                if len(inputBuffer) == 1:  # e.g. just started typing
                    if lastEventRoom != all_rooms:
                        the_room_to_post_to = lastEventRoom

            if c == 9:
                #stdscr.addstr(1, 0, "%s was pressed\n" % c)
                room = room_keys[nextRoom]
                nextRoom = (nextRoom + 1) % len(rooms)
                the_room_to_post_to = None
            elif c == 10: # enter
                with open('redpill-sends.log', 'a') as the_file:
                    the_file.write("the_room_to_post_to:" + str(the_room_to_post_to) + "\n")
                    the_file.write("lastEventRoom: " + str(lastEventRoom) + "\n")
                    the_file.write("room: " + str(room) + "\n")
                    the_file.write("inputBuffer: " + str(inputBuffer) + "\n")
                    the_file.write("---\n")

                if inputBuffer.startswith("/invite"):
                    user_id = inputBuffer[7:].strip()
                    rooms[room].invite_user(user_id)
                elif inputBuffer.startswith("/kick"):
                    user_id = inputBuffer[5:].strip()
                    reason = "no reason..."
                    rooms[room].kick_user(user_id, reason)
                elif inputBuffer.startswith("/power"):
                    user_id = inputBuffer[7:].strip()
                    power_level = 50
                    rooms[room].set_power_level(user_id, power_level)
                elif inputBuffer.startswith("/op"):
                    user_id = inputBuffer[2:].strip()
                    rooms[room].set_power_level(user_id)
                elif inputBuffer.startswith("/ban"): # reason
                    user_id = inputBuffer[4:].strip()
                    reason = "sux" #FIXME
                    rooms[room].ban(user_id, reason)
                elif inputBuffer.startswith("/join"):   # there's a /join that supports aliases
                    room_alias = inputBuffer[5:].strip()
                    client.join_room(room_alias)
                elif inputBuffer.startswith("/j"):
                    room_alias = inputBuffer[2:].strip()
                    client.join_room(room_alias)
                elif inputBuffer.startswith("/leave"):
                    rooms[room].leave_room(room_id)
                elif inputBuffer.startswith("/create"): # create a new room
                    is_public = True
                    invitees = ()
                    #     def create_room(self, alias=None, is_public=False, invitees=()):
                    room_alias = inputBuffer[7:].strip()
                    client.create_room(room_alias, is_public, invitees)
                elif inputBuffer.startswith("/topic"):   # get or set topic
                    new_topic = inputBuffer[6:].strip()
                    if len(new_topic) > 0:
                        rooms[room].topic = new_topic
                    else:
                        pass
                        #rooms[room].topic = "fail"
                else:
                    if room == all_rooms:
                        if the_room_to_post_to is None:
                            if lastEventRoom != all_rooms:
                                the_room_to_post_to = lastEventRoom
                            else:
                                stdscr.addstr(1, 0, "No idea what room to post to!")
                                stdscr.refresh()
                                inputBuffer = "No idea what room to post to!"
                                continue
                    else:
                        the_room_to_post_to = room

                    if inputBuffer.startswith("/me"):
                        rooms[the_room_to_post_to].send_emote(inputBuffer[3:])
                    else:
                        rooms[the_room_to_post_to].send_text(inputBuffer)

                inputBuffer = ""
                the_room_to_post_to = None
            elif c == curses.KEY_DC:
                inputBuffer = ""
                the_room_to_post_to = None
            elif c == curses.KEY_BACKSPACE:
                if len(inputBuffer) > 0:
                    inputBuffer = inputBuffer[:-1]
                if len(inputBuffer) == 0:
                    the_room_to_post_to = None
            elif c == curses.KEY_IC:
                pause = not(pause)
                if pause:
                    curses.nocbreak()
                    curses.cbreak()
                    stdscr.timeout(-1)
                    stdscr.addstr(
                        int(size[0] / 2) - 1,
                        int(size[1] / 2),
                        "          ",
                        curses.A_REVERSE
                    )
                    stdscr.addstr(
                        int(size[0] / 2),
                        int(size[1] / 2),
                        " PAUSING  ",
                        curses.A_REVERSE
                    )
                    stdscr.addstr(
                        int(size[0] / 2) + 1,
                        int(size[1] / 2),
                        "          ",
                        curses.A_REVERSE
                    )
                    stdscr.refresh()
                else:
                    stdscr.addstr(
                        int(size[0] / 2) - 1,
                        int(size[1] / 2),
                        "          ",
                        curses.A_REVERSE
                    )
                    stdscr.addstr(
                        int(size[0] / 2),
                        int(size[1] / 2),
                        " RESUMING ",
                        curses.A_REVERSE
                    )
                    stdscr.addstr(
                        int(size[0] / 2) + 1,
                        int(size[1] / 2),
                        "          ",
                        curses.A_REVERSE
                    )
                    stdscr.refresh()
                    curses.halfdelay(10)
                    stdscr.timeout(1)
            elif c == 27:  # need to test for alt combo or ESC
                curses.cbreak()
                curses.echo()
                #curses.curs_set(1)
                stdscr.keypad(0)
                curses.endwin()
                quit()
            elif c == curses.KEY_F2:
                PAD_COMMENTS = not PAD_COMMENTS

            #stdscr.addstr(2, 0, "time() == %s\n" % time.time())

        finally:
            do_nothing = True


if __name__ == "__main__":
    try:

        #curses.wrapper(main)
        main_screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        main_screen.keypad(1)
        curses.start_color()

        try:
            start(main_screen)
        except:
            import traceback
            with open('redpill-exception.log', 'a') as f:
                traceback.print_exc(file=f)
            raise

    except curses.error:
        curses.nocbreak()
        main_screen.keypad(0)
        curses.echo()
        curses.endwin()
    except KeyError:
        curses.nocbreak()
        main_screen.keypad(0)
        curses.echo()
        curses.endwin()
    finally:
        curses.nocbreak()
        main_screen.keypad(0)
        curses.echo()
        curses.endwin()

