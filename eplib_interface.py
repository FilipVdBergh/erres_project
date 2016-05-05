import time
from erres_variables import *

class interface:
    def __init__(self, display, player, server, mode=None):
        self.display = display
        self.player = player
        self.server = server
        self.modes = {"Off": 0,
                      "Now playing": 1,
                      "Skip": 2,
                      "Favorites": 3,
                      "Info": 4,
                      "Sync": 5}
        self.modeMax = 4 # THis ensures that the sync option is never available. Also, I'm sure the way the modes are numbered (in a dict) isn't that smart.
        if mode is None:
            self.mode = self.modes["Off"]
        else:
            self.mode = mode
        self.display.create_char(4, self.char("vol_0"))
        self.display.create_char(5, self.char("vol_25"))
        self.display.create_char(6, self.char("vol_50"))
        self.display.create_char(7, self.char("vol_75"))
        self.display.create_char(8, self.char("vol_100"))
        self.modeMin = 1 # The off state is mode 0
        self.volumeColumn = 0
        self.volumeStartRow = 3
        self.volumeDirection = 1
        self.iconLocationColumns = 0
        self.iconLocationRows = 0
        self.progress = {0: "\x04",
                         1: "\x05",
                         2: "\x06",
                         3: "\x07",
                         4: "\x08"}
        self.lineColumn = 2
        self.lines = ("", "", "", "")
        self.favoritesListIndex = 0
        self.favorites = []
        self.syncListIndex = 0
        self.playerList = []
        self.update_player_powerstate()
        self.import_playerlist()

    def char(self, name):
        code = [0,14,17,1,6,4,0,4]
        if name == "vol_0":
            code = [17,17,17,17,17,17,17,17]
        elif name == "vol_25":
            code = [17,17,17,17,17,17,31,31]
        elif name == "vol_50":
            code = [17,17,17,17,31,31,31,31]
        elif name == "vol_75":
            code = [17,17,31,31,31,31,31,31]
        elif name == "vol_100":
            code = [31,31,31,31,31,31,31,31]
        elif name == "note":
            code = [2,3,2,14,30,12,0,31]
        elif name == "RE2":
            code = [14,2,8,14,0,31,8,31]
        elif name == "RE3":
            code = [14,6,2,14,0,31,2,31]
        elif name == "RE4":
            code = [2,10,14,2,0,31,1,31]
        elif name == "sync":
            code = [12,18,22,13,9,6,0,31]
        elif name == "heart":
            code = [0,10,31,31,14,4,0,31]
        elif name == "left":
            code = [0,2,6,14,30,14,6,2]
        elif name == "right":
            code = [0,8,12,14,15,14,12,8]
        elif name == "up":
            code = [0,4,4,14,14,31,31,0]
        elif name == "down":
            code = [0,31,31,14,14,4,4,0]
        elif name == "empty":
            code = [0,0,0,0,0,0,0,0]
        elif name == "folder":
            code = [0,28,19,17,17,31,0,31]
        elif name == "clock":
            code = [0,14,21,23,17,14,0,31]
        return code

    def update_player_powerstate(self):
        #This should change state only if the new state is different.
        if (self.player.get_power_state() and (self.mode == self.modes["Off"])):
            self.mode = self.modes["Now playing"]
            self.display.create_char(1, self.char("note"))
            self.player.play()
            self.display.set_color(LCD_red, LCD_green, LCD_blue)
        elif (not self.player.get_power_state() and (self.mode != self.modes["Off"])):
            self.mode = self.modes["Off"]
            self.display.create_char(1, self.char("empty"))
            self.display.set_color(LCD_off_red, LCD_off_green, LCD_off_blue)

    def message(self,str):
        #This method should filter all strings so that the display doesn't get in trouble drawing accents.
        #It currently doesn't do this. To prevent problems, problems are caught and replaced. This must be replaced later.
        try:
            self.display.message(str)
        except:
            self.display.message("Display error")

    def clear(self):
        self.display.set_cursor(0,0)
        self.message("*" + " " * 19)
        self.display.set_cursor(0, 1)
        self.message(self.progress[0] + " " * 20)
        self.display.set_cursor(0, 2)
        self.message(self.progress[0] + " " * 20)
        self.display.set_cursor(0, 3)
        self.message(self.progress[0] + " " * 20)

    def redraw(self):
        self.update_player_powerstate()
        self.redraw_volume()
        self.redraw_main()

    def redraw_volume(self):
        parts = ((self.player.get_volume()*12)/100)
        if parts > 8:
            self.display.set_cursor(self.volumeColumn, self.volumeStartRow)
            self.display.message(self.progress[4])
            self.display.set_cursor(self.volumeColumn, self.volumeStartRow - 1)
            self.display.message(self.progress[4])
            self.display.set_cursor(self.volumeColumn, self.volumeStartRow - 2)
            self.display.message(self.progress[parts-8])
        elif parts > 4:
            self.display.set_cursor(self.volumeColumn, self.volumeStartRow)
            self.display.message(self.progress[4])
            self.display.set_cursor(self.volumeColumn, self.volumeStartRow - 1)
            self.display.message(self.progress[parts-4])
            self.display.set_cursor(self.volumeColumn, self.volumeStartRow - 2)
            self.display.message(self.progress[0])
        elif parts > 0:
            self.display.set_cursor(self.volumeColumn, self.volumeStartRow)
            self.display.message(self.progress[parts])
            self.display.set_cursor(self.volumeColumn, self.volumeStartRow - 1)
            self.display.message(self.progress[0])
            self.display.set_cursor(self.volumeColumn, self.volumeStartRow - 2)
            self.display.message(self.progress[0])

    def redraw_main(self):
        if self.mode == self.modes["Off"]:
            self.display.create_char(1, self.char("empty"))
            self.lines = ("",
                          time.strftime("%H:%M", time.localtime(time.time())).center(18),
                          time.strftime("%A", time.localtime(time.time())).center(18),
                          time.strftime("%-d %B %Y", time.localtime(time.time())).center(18))
        elif self.mode == self.modes["Now playing"]:
            self.display.create_char(1, self.char("clock"))
            self.display.create_char(2, self.char("left"))
            self.display.create_char(3, self.char("right"))
            mainLine = self.player.get_track_title()
            if self.player.get_track_artist() != "":
                mainLine += " by " + self.player.get_track_artist()
            lastLine = "\x02"
            if self.player.get_time_elapsed() > 3600:
                lastLine += time.strftime("%-H:", time.gmtime(self.player.get_time_elapsed()))
            lastLine += time.strftime("%M:%S", time.gmtime(self.player.get_time_elapsed()))
            if self.player.get_track_duration() > 0:
                lastLine += "/"
                if self.player.get_track_duration() > 3600:
                    lastLine += time.strftime("%-H:", time.gmtime(self.player.get_track_duration()))
                lastLine += time.strftime("%M:%S", time.gmtime(self.player.get_track_duration()))
            lastLine += "\x03"
            lastLine = lastLine.rjust(18)
            self.lines = (mainLine[0:18],
                          mainLine[18:36],
                          mainLine[36:54],
                          lastLine)
        elif self.mode == self.modes["Skip"]:
            self.display.create_char(1, self.char("note"))
            self.display.create_char(2, self.char("left"))
            self.display.create_char(3, self.char("right"))
            if self.player.playlist_track_count() > 1:
                lastLine = ("\x02%s/%s\x03" % (self.player.playlist_current_track_index(), self.player.playlist_track_count())).rjust(18)
            else:
                lastLine = ""
            mainLine = self.player.get_track_title()
            if self.player.get_track_artist() != "":
                mainLine += " by " + self.player.get_track_artist()
            self.lines = (mainLine[0:18],
                          mainLine[18:36],
                          mainLine[36:54],
                          lastLine)
        elif self.mode == self.modes["Info"]:
            self.display.create_char(1, self.char("folder"))
            self.lines = (self.player.get_track_title()[0:18],
                          self.player.get_track_artist()[0:18],
                          self.player.get_track_album()[0:18],
                          self.player.get_track_genre()[0:18])
        elif self.mode == self.modes["Sync"]:
            self.display.create_char(1, self.char("sync"))
            self.display.create_char(2, self.char("up"))
            self.display.create_char(3, self.char("down"))
            temp_sync = "Sync: Nee"
            if self.playerList[self.syncListIndex][2]:
                temp_sync = "Sync: Ja"
            self.lines = ("\x02".center(18),
                          self.playerList[self.syncListIndex][1],
                          temp_sync,
                          "\x03".center(18))
        elif self.mode == self.modes["Favorites"]:
            self.display.create_char(1, self.char("heart"))
            self.display.create_char(2, self.char("left"))
            self.display.create_char(3, self.char("right"))
            self.lines = (self.favorites[self.favoritesListIndex][0][0:18],
                          self.favorites[self.favoritesListIndex][1][0:18],
                          "",
                          ("\x02"+str(self.favoritesListIndex+1)+"/"+str(len(self.favorites))+"\x03").rjust(18))
        self.display.set_cursor(self.iconLocationColumns, self.iconLocationRows)
        self.message("\x01")

        currentLine=0
        for line in self.lines:
            self.display.set_cursor(self.lineColumn, currentLine)
            self.message(str(line).ljust(18))
            currentLine+=1

    def import_playerlist(self):
        player_list = self.server.get_players()
        for player in player_list:
            self.playerList.append((player, player.get_name(), False))
        self.playerList.sort()

    def import_favorites(self, favoritesFile):
        favoritesFile = open("erres_favorites", "rU")
        favoritesName = None
        name = True
        for line in favoritesFile:
            if line[0:1] == "#":  # This is a comment line, and can be ignored
                pass
            elif line == "\n":      # This is an empty line, and can be ignored
                pass
            else:
                if name:
                    favoritesName = line.replace("\n", "")
                    name = False
                else:
                    self.favorites.append((favoritesName, line.replace("\n", "")))
                    name = True

    def mode_right(self):
        self.mode += 1
        if self.mode > self.modeMax:
            self.mode = self.modeMin

    def mode_left(self):
        self.mode -= 1
        if self.mode < self.modeMin:
            self.mode = self.modeMax

    def get_mode(self):
        return self.mode

    def RE1_press(self):
        self.player.set_power_state(not self.player.get_power_state())
        self.update_player_powerstate()
        time.sleep(0.15) # To make sure it doesn't switch immediately again

    def RE1_turn(self, amount):
        if amount > 0:
            self.player.volume_up(5)
        else:
            self.player.volume_down(5)

    def RE2_press(self):
        if self.mode == self.modes["Now playing"]:
            self.player.toggle()
        elif self.mode == self.modes["Skip"]:
            self.player.toggle()
        elif self.mode == self.modes["Favorites"]:
            self.player.playlist_play(self.favorites[self.favoritesListIndex][1])
            self.mode = self.modes["Skip"]
        elif self.mode == self.modes["Sync"]:
            if self.playerList[self.syncListIndex][2]:
                self.player.sync_to(self.playerList[self.syncListIndex][0])
            else:
                self.player.unsync()
            self.playerList[self.syncListIndex][2] = not self.playerList[self.syncListIndex][2]

    def RE2_turn(self, amount):
        if self.mode == self.modes["Now playing"]:
            if amount > 0:
                self.player.forward(30)
            elif amount < 0:
                self.player.rewind(30)
        elif self.mode == self.modes["Skip"]:
            if amount > 0:
                self.player.next()
            elif amount < 0:
                self.player.prev()
        elif self.mode == self.modes["Sync"]:
            if amount > 0:
                self.syncListIndex += 1
                if self.syncListIndex >= len(self.favorites):
                    self.syncListIndex = 0
            elif amount < 0:
                self.syncListIndex -= 1
                if self.syncListIndex < 0:
                    self.syncListIndex = len(self.favorites)-1
        elif self.mode == self.modes["Favorites"]:
            if amount > 0:
                self.favoritesListIndex += 1
                if self.favoritesListIndex >= len(self.favorites):
                    self.favoritesListIndex = 0
            elif amount < 0:
                self.favoritesListIndex -= 1
                if self.favoritesListIndex < 0:
                    self.favoritesListIndex = len(self.favorites)-1

    def RE3_press(self):
        self.mode = self.modes["Now playing"]

    def RE3_turn(self, amount):
        if amount > 0:
            self.mode_right()
        elif amount < 0:
            self.mode_left()


