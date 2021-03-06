# -*- coding: utf-8 -*-
""" *==LICENSE==*

CyanWorlds.com Engine - MMOG client, server and tools
Copyright (C) 2011  Cyan Worlds, Inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Additional permissions under GNU GPL version 3 section 7

If you modify this Program, or any covered work, by linking or
combining it with any of RAD Game Tools Bink SDK, Autodesk 3ds Max SDK,
NVIDIA PhysX SDK, Microsoft DirectX SDK, OpenSSL library, Independent
JPEG Group JPEG library, Microsoft Windows Media SDK, or Apple QuickTime SDK
(or a modified version of those libraries),
containing parts covered by the terms of the Bink SDK EULA, 3ds Max EULA,
PhysX SDK EULA, DirectX SDK EULA, OpenSSL and SSLeay licenses, IJG
JPEG Library README, Windows Media SDK EULA, or QuickTime SDK EULA, the
licensors of this Program grant you additional
permission to convey the resulting work. Corresponding Source for a
non-source form of such a combination shall include the source code for
the parts of OpenSSL and IJG JPEG Library used as well as that of the covered
work.

You can contact Cyan Worlds, Inc. by email legal@cyan.com
 or by snail mail at:
      Cyan Worlds, Inc.
      14617 N Newport Hwy
      Mead, WA   99021

 *==LICENSE==* """
kChronCurCGZGame = "CurCGZGame"


from Plasma import *
from PlasmaTypes import *
import string
import xMarkerGameManager

def GetCGZGameName(num):
    "returns the name of the game"
    if num < 0:
        return None

    try:
        mg = mgs[num]
        return mg[1]
    except:
        return None

def GetCurrentCGZGame():
    "return which game (if any) is playing now"
    gameData = xMarkerGameManager.chronicleMarkerGameData()
    return gameData.data['CGZGameNum']

def GetCurrentGameType():
    "returns which game type (if any) is currently played"
    gameData = xMarkerGameManager.chronicleMarkerGameData()
    return gameData.data['svrGameTypeID']


def UpdateScore(gameNum, startTime, bestTime):
    "Updates the score of a specified game, only updates best time if it's a better time"
    #TODO: Tye: We need to change this from 14 single entries in the chronicle, to a single entry!

    #SPECIAL NOTES:
    #   If startTime < 0 or bestTime < 0 it will NOT update the corresponding value!
    if gameNum < 0 or gameNum > len(mgs):
        PtDebugPrint("ERROR: grtzMarkerGames.UpdateScore():\tAborting update, invalid game number: %s" %gameNum)
        return
       
    vault = ptVault()
    gameName = GetCGZGameName(gameNum)    
    entry = vault.findChronicleEntry(gameName)
    isNewBestTime = 0
    
    if type(entry) == type(None):
        # Here we actually do need to save a startTime value (negative is invalid)
        # But only if we're creating a new variable!
        if startTime < 0:
            startTime = 0.0
        vault.addChronicleEntry(gameName, 1, "%f,%f" % (startTime, bestTime))

        if bestTime > 0:
            isNewBestTime = 1
            PtDebugPrint("grtzMarkerGames.UpdateScore():\tDEBUG: Found no previous bestTime entry, setting new best time!")

        PtDebugPrint("grtzMarkerGames.UpdateScore():\tDEBUG: Game Num: %d, updated for the first time: StartTime = %f  BestTime = %f" %(gameNum,startTime,bestTime))
        return
    else:
        statString = entry.chronicleGetValue()
        statList = statString.split(",")

        if len(statList) == 2:
            try:
                # If we're not updating startTime, then we'd better get the old one!
                if startTime < 0:
                    startTime = string.atof(statList[0])
                
                #Only update bestTime if we have a better time
                oldBestTime = string.atof(statList[1])
                if bestTime > 0.1:
                    if bestTime < oldBestTime or oldBestTime < 0.1:
                        isNewBestTime = 1
                        PtDebugPrint("grtzMarkerGames.UpdateScore():\tDEBUG: Found new best time, updating...   old best time score: %f" % oldBestTime)
                    else:
                        bestTime = oldBestTime
                else:
                    bestTime = oldBestTime
            except:
                pass

                PtDebugPrint("grtzMarkerGames.UpdateScore():\tDEBUG: Game Num: %d, updated score: Start Time = %f  BestTime = %f" %(gameNum,startTime,bestTime))
        entry.chronicleSetValue("%f,%f" %(startTime,bestTime))
        entry.save()

def GetGameTime(gameName):
    "returns the currentTime,bestTime"
    # assume no times
    startTime = 0.0
    bestTime = 0.0
    vault = ptVault()
    
    # is there a chronicle for the GZ games?
    entry = vault.findChronicleEntry(gameName)
    if type(entry) != type(None):
        progressString = entry.chronicleGetValue()
        progList = progressString.split(',')
        if len(progList) == 2:
            try:
                startTime = string.atof(progList[0])
            except ValueError:
                pass
            try:
                bestTime = string.atof(progList[1])
            except ValueError:
                pass
    return startTime,bestTime
    
def GetGameProgress():
    "returns the game number, number of captured markers, and number of markers for the currently played game"
    gameData = xMarkerGameManager.chronicleMarkerGameData()
    return gameData.data['CGZGameNum'], gameData.data['numCapturedMarkers'], gameData.data['numMarkers']


def GetGameScore(gameNum):
    "returns the score for the specified CGZ game number"
    vault = ptVault()
    gameName = GetCGZGameName(gameNum)
    entry = vault.findChronicleEntry(gameName)
    if type(entry) == type(None):
        return -1
     
    statString = entry.chronicleGetValue()
    statList = statString.split(",")

    #Make sure that we've got the correct input
    if len(statList) != 2:
        if statString != "":  
            #If we're here, then we've got corrupted stats, delete existing game stats!
            entry.chronicle.SetValue("")
            entry.save()
        return -1
        
    try:
        bestTime = string.atof(statList[1])
    except:
        bestTime = -1
    return bestTime


def GetNumMarkers(gameNum):
    "returns the number of markers in this game"
    try:
        mg = mgs[gameNum]
        return len(mg[0][4])
    except:
        return 0

# [ ownerID,ownerName,type,roundLength,
# [ [markerText,x,y,z,age,torans,hspans,vspans],]]
#
# GZ markers  one
MG01 = [ 1, "GZ guy", 2, 120 ,
  [
    [ "3, 53, -80", 0.113123, -156.593, 221.15, "city", 3, 53, -80 ],
    [ "62334, 63, -85", 17.0199, -315.718, 144.806, "city", 62334, 63, -85 ],
    [ "62432, 63, -86", 6.97063, -312.509, 131.561, "city", 62432, 63, -86 ],
    [ "62143, 71, -89", 40.9337, -437.902, 82.8586, "city", 62143, 71, -89 ],
    [ "32257, 84, -93", -142.135, -634.978, 8.21551, "city", 32257, 84, -93 ],
    [ "61728, 78, -93", 97.9118, -555.991, 6.74272, "city", 61728, 78, -93 ],
    [ "61363, 80, -93", 146.221, -571.129, 9.02309, "city", 61363, 80, -93 ],
    [ "61984, 75, -93", 62.3171, -496.638, 6.83943, "city", 61984, 75, -93 ],
    [ "61188, 45, -79", 95.1365, -14.2289, 243.928, "city", 61188, 45, -79 ],
    [ "59651, 44, -76", 198.983, 27.1469, 291.171, "city", 59651, 44, -76 ],
    [ "60329, 44, -76", 154.969, 4.03381, 290.841, "city", 60329, 44, -76 ],
    [ "9, 64, -85", -0.621237, -329.797, 135.381, "city", 9, 64, -85 ],
  ]
]

MG02 = [ 1, "GZ guy", 2, 120 ,
  [
    [ "56815, 100, -79", 866.687, -645.153, 238.134, "city", 56815, 100, -79 ],
    [ "56972, 104, -79", 884.89, -722.404, 232.785, "city", 56972, 104, -79 ],
    [ "56953, 99, -79", 840.865, -645.9, 244.26, "city", 56953, 99, -79 ],
    [ "61041, 70, -84", 164.1, -408.321, 162.822, "city", 61041, 70, -84 ],
    [ "32495, 62, -86", -130.384, -284.278, 127.039, "city", 32495, 62, -86 ],
    [ "32479, 62, -86", -128.733, -283.422, 127.041, "city", 32479, 62, -86 ],
    [ "32461, 62, -86", -126.874, -283.311, 127.042, "city", 32461, 62, -86 ],
    [ "32452, 62, -86", -125.991, -283.299, 127.043, "city", 32452, 62, -86 ],
    [ "32143, 58, -86", -90.4871, -233.48, 127.11, "city", 32143, 58, -86 ],
    [ "32372, 59, -86", -112.979, -239.741, 127.444, "city", 32372, 59, -86 ],
    [ "32449, 59, -86", -121.025, -244.955, 131.027, "city", 32449, 59, -86 ],
    [ "32712, 60, -86", -147.008, -248.051, 127.11, "city", 32712, 60, -86 ],
    [ "33992, 44, -80", -199.518, 19.7047, 225.826, "city", 33992, 44, -80 ],
    [ "34005, 44, -80", -199.09, 24.6076, 225.826, "city", 34005, 44, -80 ],
    [ "33954, 43, -80", -193.792, 30.2368, 225.826, "city", 33954, 43, -80 ],
    [ "34580, 43, -78", -234.291, 47.5248, 253.739, "city", 34580, 43, -78 ],
    [ "35207, 45, -78", -290.803, 25.9652, 254.499, "city", 35207, 45, -78 ],
    [ "35030, 40, -78", -245.232, 104.78, 254.478, "city", 35030, 40, -78 ],
    [ "60876, 66, -83", 173.349, -349.866, 180.313, "city", 60876, 66, -83 ],
    [ "56945, 99, -79", 841.677, -644.558, 244.414, "city", 56945, 99, -79 ],
    [ "60826, 66, -83", 179.525, -354.162, 180.313, "city", 60826, 66, -83 ],
    [ "61133, 77, -84", 169.036, -519.697, 160.798, "city", 61133, 77, -84 ],
    [ "56971, 99, -79", 839.212, -648.525, 243.975, "city", 56971, 99, -79 ],
    [ "57070, 101, -81", 845.905, -690.159, 209.033, "city", 57070, 101, -81 ],
  ]
]
MG03 = [ 1, "GZ guy", 2, 120 ,
  [
    [ "57090, 94, -78", 779.755, -587.08, 259.243, "city", 57090, 94, -78 ],
    [ "58559, 73, -75", 454.014, -382.702, 297.221, "city", 58559, 73, -75 ],
    [ "57287, 109, -78", 873.06, -808.26, 259.243, "city", 57287, 109, -78 ],
    [ "56817, 111, -78", 966.86, -801.529, 259.254, "city", 56817, 111, -78 ],
    [ "57116, 107, -78", 885.322, -770.273, 259.243, "city", 57116, 107, -78 ],
    [ "57046, 107, -77", 898.188, -768.307, 269.941, "city", 57046, 107, -77 ],
    [ "56510, 107, -77", 972.309, -712.254, 269.975, "city", 56510, 107, -77 ],
    [ "56679, 98, -77", 867.876, -607.192, 269.983, "city", 56679, 98, -77 ],
    [ "57191, 99, -77", 806.465, -662.197, 269.863, "city", 57191, 99, -77 ],
    [ "57473, 87, -78", 675.79, -518.872, 256.664, "city", 57473, 87, -78 ],
    [ "58059, 71, -78", 491.578, -324.465, 251.259, "city", 58059, 71, -78 ],
  ]
]
MG04 = [ 1, "GZ guy", 2, 120 ,
  [
    [ "60415, 78, -79", 262.733, -532.497, 239.805, "city", 60415, 78, -79 ],
    [ "60676, 77, -80", 225.478, -513.173, 216.521, "city", 60676, 77, -80 ],
    [ "32205, 84, -93", -135.211, -637.171, 10.4902, "city", 32205, 84, -93 ],
    [ "57235, 109, -78", 881.076, -803.77, 259.244, "city", 57235, 109, -78 ],
    [ "57253, 108, -78", 877.444, -803.838, 259.244, "city", 57253, 108, -78 ],
    [ "57287, 108, -78", 870.754, -803.964, 259.244, "city", 57287, 108, -78 ],
    [ "57438, 107, -79", 840.792, -804.53, 246.271, "city", 57438, 107, -79 ],
    [ "5, 63, -85", -0.0876787, -314.3, 144.145, "city", 5, 63, -85 ],
    [ "62339, 53, -80", 13.9271, -154.523, 224.159, "city", 62339, 53, -80 ],
    [ "31905, 50, -80", -59.7848, -110.308, 221.673, "city", 31905, 50, -80 ],
    [ "32534, 54, -80", -118.658, -163.122, 221.597, "city", 32534, 54, -80 ],
    [ "32813, 55, -80", -146.071, -180.047, 218.473, "city", 32813, 55, -80 ],
    [ "33459, 59, -82", -215.992, -225.902, 186.949, "city", 33459, 59, -82 ],
    [ "33293, 58, -82", -197.099, -213.275, 194.361, "city", 33293, 58, -82 ],
    [ "32998, 57, -80", -165.729, -195.325, 220.011, "city", 32998, 57, -80 ],
    [ "61600, 51, -80", 75.1814, -125.345, 223.846, "city", 61600, 51, -80 ],
    [ "60901, 65, -83", 167.221, -328.274, 178.47, "city", 60901, 65, -83 ],
    [ "60287, 67, -83", 238.621, -351.974, 181.112, "city", 60287, 67, -83 ],
    [ "59951, 73, -83", 296.351, -428.617, 178.973, "city", 59951, 73, -83 ],
    [ "59898, 78, -79", 323.009, -503.966, 244.604, "city", 59898, 78, -79 ],
  ]
]
MG05 = [ 1, "GZ guy", 2, 120 ,
  [
    [ "60315, 43, -76", 152.191, 21.0605, 293.854, "city", 60315, 43, -76 ],
    [ "58121, 56, -78", 383.555, -111.711, 257.587, "city", 58121, 56, -78 ],
    [ "57888, 47, -76", 343.068, 16.5379, 292.971, "city", 57888, 47, -76 ],
    [ "58029, 45, -76", 318.848, 41.6997, 291.357, "city", 58029, 45, -76 ],
    [ "62028, 53, -80", 40.6364, -152.596, 224.379, "city", 62028, 53, -80 ],
    [ "61452, 59, -82", 100.535, -247.86, 193.841, "city", 61452, 59, -82 ],
    [ "57064, 94, -78", 782.075, -583.084, 259.243, "city", 57064, 94, -78 ],
    [ "57268, 87, -78", 704.187, -510.593, 259.243, "city", 57268, 87, -78 ],
    [ "56531, 86, -75", 779.124, -436.175, 296.512, "city", 56531, 86, -75 ],
    [ "56122, 83, -75", 798.406, -367.264, 297.593, "city", 56122, 83, -75 ],
    [ "56783, 77, -75", 672.346, -335.633, 297.594, "city", 56783, 77, -75 ],
    [ "57442, 66, -75", 521.539, -233.122, 294.92, "city", 57442, 66, -75 ],
    [ "58796, 74, -75", 431.085, -401.132, 294.896, "city", 58796, 74, -75 ],
    [ "59227, 77, -75", 399.419, -467.361, 299.302, "city", 59227, 77, -75 ],
    [ "59302, 82, -77", 416.217, -547.247, 277.85, "city", 59302, 82, -77 ],
    [ "59674, 82, -79", 370.373, -565.982, 239.353, "city", 59674, 82, -79 ],
    [ "59992, 76, -79", 306.196, -485.725, 243.624, "city", 59992, 76, -79 ],
    [ "60421, 78, -79", 262.047, -532.807, 237.377, "city", 60421, 78, -79 ],
    [ "60536, 74, -81", 234.399, -468.967, 208.197, "city", 60536, 74, -81 ],
    [ "60288, 73, -81", 261.147, -452.115, 206.569, "city", 60288, 73, -81 ],
    [ "59939, 73, -83", 298.73, -431.849, 178.966, "city", 59939, 73, -83 ],
    [ "60343, 66, -83", 230.511, -343.587, 178.72, "city", 60343, 66, -83 ],
    [ "60667, 65, -83", 191.976, -327.469, 178.508, "city", 60667, 65, -83 ],
    [ "61584, 46, -80", 68.7406, -40.7315, 230.585, "city", 61584, 46, -80 ],
    [ "58848, 42, -76", 244.142, 67.786, 291.356, "city", 58848, 42, -76 ],
#    [ "57756, 45, -76", 332.792, 58.5213, 291.296, "city", 57756, 45, -76 ],
#    [ "58265, 52, -77", 349.096, -67.2592, 274.02, "city", 58265, 52, -77 ],
#    [ "57142, 56, -75", 462.965, -72.0451, 297.591, "city", 57142, 56, -75 ],
  ]
]
MG06 = [ 1, "GZ guy", 2, 120 ,
  [
    [ "60283, 1005, -70", 275.215, -713.491, 19.1162, "Neighborhood", 60283, 1005, -70 ],
    [ "60270, 1003, -70", 261.281, -750.158, 21.5005, "Neighborhood", 60270, 1003, -70 ],
    [ "60238, 1003, -71", 213.126, -767.487, 9.8439, "Neighborhood", 60238, 1003, -71 ],
    [ "60213, 1003, -71", 172.793, -775.21, 3.32227, "Neighborhood", 60213, 1003, -71 ],
    [ "60275, 1000, -71", 280.228, -796.492, 9.01678, "Neighborhood", 60275, 1000, -71 ],
    [ "60234, 998, -71", 226.41, -854.221, 1.65846, "Neighborhood", 60234, 998, -71 ],
    [ "60160, 994, -73", 123.435, -931.588, -19.6041, "Neighborhood", 60160, 994, -73 ],
    [ "60218, 1002, -73", 186.016, -792.772, -18.2181, "Neighborhood", 60218, 1002, -73 ],
    [ "60209, 1005, -72", 160.845, -750.635, -10.8941, "Neighborhood", 60209, 1005, -72 ],
    [ "60302, 1005, -70", 305.288, -706.162, 21.0971, "Neighborhood", 60302, 1005, -70 ],
    [ "60327, 1003, -70", 354.996, -742.071, 19.1236, "Neighborhood", 60327, 1003, -70 ],
    [ "60306, 1002, -70", 324.906, -766.67, 19.1239, "Neighborhood", 60306, 1002, -70 ],
    [ "60218, 999, -71", 195.939, -835.297, 5.82845, "Neighborhood", 60218, 999, -71 ],
    [ "60191, 1004, -71", 135.273, -767.306, 11.7715, "Neighborhood", 60191, 1004, -71 ],
  ]
]
MG07 = [ 1, "GZ guy", 2, 120 ,
  [
    [ "60109, 1006, -71", 0.380994, -771.841, 8.10068, "Neighborhood", 60109, 1006, -71 ],
    [ "60143, 1004, -71", 59.4292, -782.611, 8.15849, "Neighborhood", 60143, 1004, -71 ],
    [ "60100, 1005, -71", -11.4838, -788.725, 8.10068, "Neighborhood", 60100, 1005, -71 ],
    [ "60096, 1006, -71", -20.6219, -775.695, 8.10068, "Neighborhood", 60096, 1006, -71 ],
    [ "60095, 1007, -71", -25.0077, -763.53, 8.10068, "Neighborhood", 60095, 1007, -71 ],
    [ "60155, 1003, -71", 84.2148, -804.868, 15.692, "Neighborhood", 60155, 1003, -71 ],
    [ "60125, 1004, -66", 31.4565, -796.199, 81.4172, "Neighborhood", 60125, 1004, -66 ],
    [ "60224, 997, -73", 214.071, -873.879, -18.5609, "Neighborhood", 60224, 997, -73 ],
    [ "60256, 1003, -71", 240.256, -759.147, 9.85464, "Neighborhood", 60256, 1003, -71 ],
    [ "60266, 997, -71", 280.289, -857.252, 5.71199, "Neighborhood", 60266, 997, -71 ],
    [ "60142, 1005, -70", 55.9215, -780.317, 29.2447, "Neighborhood", 60142, 1005, -70 ],
    [ "60179, 1006, -71", 107.642, -735.816, 7.56582, "Neighborhood", 60179, 1006, -71 ],
    [ "60193, 1004, -71", 137.585, -766.796, 12.0827, "Neighborhood", 60193, 1004, -71 ],
    [ "60219, 1003, -71", 182.913, -774.13, 10.5281, "Neighborhood", 60219, 1003, -71 ],
    [ "60259, 1002, -71", 250.806, -779.415, 9.80428, "Neighborhood", 60259, 1002, -71 ],
    [ "60287, 1001, -71", 297.308, -783.464, 9.14582, "Neighborhood", 60287, 1001, -71 ],
  ]
]
MG08 = [ 1, "GZ guy", 2, 120 ,
  [
    [ "59972, 78, -79", 316.219, -514.793, 237.373, "city", 59972, 78, -79 ],
    [ "59700, 82, -79", 365.981, -563.018, 237.389, "city", 59700, 82, -79 ],
    [ "59283, 81, -77", 415.82, -538.035, 274.685, "city", 59283, 81, -77 ],
    [ "58884, 74, -75", 425.815, -416.746, 294.899, "city", 58884, 74, -75 ],
    [ "58296, 71, -75", 469.789, -341.995, 294.9, "city", 58296, 71, -75 ],
    [ "58273, 70, -75", 467.679, -330.837, 294.91, "city", 58273, 70, -75 ],
    [ "58246, 70, -77", 465.28, -318.14, 268.098, "city", 58246, 70, -77 ],
    [ "59585, 56, -78", 260.434, -160.43, 260.027, "city", 59585, 56, -78 ],
    [ "60078, 55, -78", 214.6, -160.99, 259.761, "city", 60078, 55, -78 ],
    [ "61042, 55, -80", 129.821, -176.251, 215.822, "city", 61042, 55, -80 ],
    [ "60692, 65, -83", 189.439, -327.706, 178.497, "city", 60692, 65, -83 ],
    [ "60749, 64, -83", 180.853, -314.042, 177.981, "city", 60749, 64, -83 ],
    [ "60186, 66, -84", 245.511, -333.635, 150.648, "city", 60186, 66, -84 ],
    [ "61719, 52, -80", 65.3244, -127.249, 221.673, "city", 61719, 52, -80 ],
    [ "35, 44, -80", -2.39575, -13.6359, 220.941, "city", 35, 44, -80 ],
    [ "31681, 53, -77", -42.9333, -145.408, 277.339, "city", 31681, 53, -77 ],
    [ "31789, 56, -76", -54.6834, -191.584, 278.654, "city", 31789, 56, -76 ],
    [ "31978, 55, -77", -71.0139, -181.946, 274.244, "city", 31978, 55, -77 ],
    [ "31966, 54, -76", -68.8656, -167.067, 284.985, "city", 31966, 54, -76 ],
    [ "467, 56, -77", -42.0513, -195.511, 277.165, "city", 467, 56, -77 ],
  ]
]
MG09 = [ 1, "GZ guy", 2, 120 ,
  [
    [ "62480, 52, -80", 1.77311, -143.133, 220.935, "city", 62480, 52, -80 ],
    [ "31746, 52, -80", -47.6192, -128.094, 221.671, "city", 31746, 52, -80 ],
    [ "32656, 56, -80", -133.881, -194.159, 221.659, "city", 32656, 56, -80 ],
    [ "31642, 48, -80", -36.892, -77.407, 221.679, "city", 31642, 48, -80 ],
    [ "33745, 44, -80", -182.53, 15.0192, 221.679, "city", 33745, 44, -80 ],
    [ "161, 46, -80", -11.8993, -39.2203, 220.12, "city", 161, 46, -80 ],
    [ "31354, 41, -80", -13.1011, 35.0907, 220.104, "city", 31354, 41, -80 ],
    [ "62068, 47, -80", 32.8043, -51.3977, 221.76, "city", 62068, 47, -80 ],
    [ "61889, 51, -80", 50.5303, -118.34, 221.66, "city", 61889, 51, -80 ],
    [ "61990, 52, -80", 42.9236, -133.187, 221.661, "city", 61990, 52, -80 ],
    [ "60797, 45, -78", 123.175, -9.2883, 261.196, "city", 60797, 45, -78 ],
    [ "61535, 53, -80", 82.4942, -144.117, 222.015, "city", 61535, 53, -80 ],
    [ "61746, 57, -82", 70.1662, -220.908, 195.87, "city", 61746, 57, -82 ],
    [ "51, 57, -82", -4.62847, -215.158, 194.066, "city", 51, 57, -82 ],
    [ "62417, 56, -81", 7.58955, -205.743, 199.97, "city", 62417, 56, -81 ],
    [ "62485, 49, -80", 1.26902, -94.9741, 220.931, "city", 62485, 49, -80 ],
  ]
]
MG10 = [ 1, "GZ guy", 2, 120 ,
  [
    [ "32489, 82, -93", -169.248, -599.338, 8.22528, "city", 32489, 82, -93 ],
    [ "32437, 80, -93", -159.089, -572.478, 8.22528, "city", 32437, 80, -93 ],
    [ "32370, 78, -93", -146.356, -536.789, 8.22528, "city", 32370, 78, -93 ],
    [ "62074, 74, -90", 50.8871, -483.389, 62.6932, "city", 62074, 74, -90 ],
    [ "62442, 70, -88", 6.66464, -425.883, 92.6597, "city", 62442, 70, -88 ],
    [ "26, 61, -84", -2.43234, -276.531, 155.824, "city", 26, 61, -84 ],
    [ "62466, 53, -80", 2.97976, -148.419, 223.733, "city", 62466, 53, -80 ],
    [ "61768, 52, -80", 61.4058, -129.401, 221.671, "city", 61768, 52, -80 ],
    [ "61208, 54, -80", 113.078, -162.948, 214.661, "city", 61208, 54, -80 ],
    [ "57996, 69, -75", 489.8, -304.099, 294.899, "city", 57996, 69, -75 ],
    [ "56916, 64, -75", 549.031, -170.577, 297.581, "city", 56916, 64, -75 ],
    [ "57008, 65, -75", 553.686, -196.203, 297.581, "city", 57008, 65, -75 ],
    [ "56889, 68, -75", 588.206, -227.224, 297.593, "city", 56889, 68, -75 ],
    [ "56898, 70, -75", 603.84, -253.754, 297.593, "city", 56898, 70, -75 ],
    [ "56809, 76, -75", 666.27, -332.168, 297.594, "city", 56809, 76, -75 ],
    [ "56149, 81, -75", 775.175, -341.96, 297.595, "city", 56149, 81, -75 ],
    [ "56238, 85, -75", 801.331, -397.677, 297.595, "city", 56238, 85, -75 ],
    [ "56477, 85, -75", 777.84, -421.14, 299.93, "city", 56477, 85, -75 ],
    [ "57179, 87, -78", 715.306, -504.603, 256.659, "city", 57179, 87, -78 ],
    [ "57176, 93, -78", 765.788, -589.046, 259.234, "city", 57176, 93, -78 ],
    [ "56459, 95, -78", 874.804, -556.476, 259.243, "city", 56459, 95, -78 ],
    [ "56182, 100, -78", 951.983, -589.045, 259.243, "city", 56182, 100, -78 ],
    [ "56248, 102, -78", 968.839, -630.479, 259.243, "city", 56248, 102, -78 ],
    [ "56381, 108, -78", 1000.34, -713.188, 259.243, "city", 56381, 108, -78 ],
    [ "56481, 110, -78", 1003.1, -748.014, 259.243, "city", 56481, 110, -78 ],
#    [ "56588, 109, -78", 978.66, -745.66, 259.243, "city", 56588, 109, -78 ],
#    [ "57190, 109, -78", 893.636, -809.511, 259.243, "city", 57190, 109, -78 ],
#    [ "57452, 109, -80", 849.176, -824.857, 222.094, "city", 57452, 109, -80 ],
  ]
]
#
# distance ferry
MG11 = [ 1, "GZ guy", 2, 120 ,
  [
    [ "3, 53, -80", -0.0891117, -155.874, 223.466, "city", 3, 53, -80 ],
    [ "3, 75, -93", 0.0849568, -510.678, 6.83298, "city", 3, 75, -93 ],
    [ "3, 73, -92", 0.046029, -468.112, 30.0315, "city", 3, 73, -92 ],
    [ "3, 70, -88 ", 0.0126944, -425.414, 90.2389, "city", 3, 70, -88 ],
    [ "3, 64, -85", 0.0880445, -330.854, 134.733, "city", 3, 64, -85 ],
    [ "3, 63, -85 ", -0.0940349, -308.747, 144.135, "city", 3, 63, -85 ],
    [ "3, 49, -80", 0.107221, -82.8188, 220.945, "city", 3, 49, -80 ],
    [ "3, 41, -80", 0.0100019, 31.4722, 220.945, "city", 3, 41, -80 ],
    [ "0, 1, -3", 0.000921001, -25.3192, -40.0522, "GreatZero", 0, 1, -3 ],
  ]
]
#
# ferry hieght
MG12 = [ 1, "GZ guy", 2, 120 ,
  [
    [ "31851, 73, -93", -76.7246, -463.087, 8.21978, "city", 31851, 73, -93 ],
    [ "97, 69, -88", -10.8075, -413.394, 92.4359, "city", 97, 69, -88 ],
    [ "114, 63, -86 ", -11.6655, -320.016, 133.759, "city", 114, 63, -86 ],
    [ "39, 63, -85", -3.82988, -312.859, 144.135, "city", 39, 63, -85 ],
    [ "32254, 62, -86", -107.042, -293.259, 130.295, "city", 32254, 62, -86 ],
    [ "32694, 57, -86", -140.033, -212.729, 127.077, "city", 32694, 57, -86 ],
    [ "32694, 57, -77", -140.033, -212.729, 274.241, "city", 32694, 57, -77 ],
    [ "62496, 53, -80 ", 0.388106, -150.975, 220.94, "city", 62496, 53, -80 ],
    [ "61577, 46, -80", 69.3479, -41.5769, 221.68, "city", 61577, 46, -80 ],
  ]
]
#
# circles
MG13 = [ 1, "GZ guy", 2, 120 ,
  [
    [ "22, 3, -3", -0.107815, -48.5057, -40.0535, "GreatZero", 22, 3, -3 ],
    [ "18929, 3, -3 ", -46.3505, 16.0544, -40.0403, "GreatZero", 18929, 3, -3 ],
    [ "40365, 3, -3 ", 38.3031, 29.4412, -40.04, "GreatZero", 40365, 3, -3 ],
    [ "32420, 74, -93", -146.164, -481.771, 8.22064, "city", 32420, 74, -93 ],
    [ "31834, 74, -93 ", -76.4565, -492.799, 7.64378, "city", 31834, 74, -93 ],
    [ "41, 74, -93", -4.83725, -489.336, 6.84302, "city", 41, 74, -93 ],
    [ "61808, 74, -90 ", 83.4286, -493.755, 60.0126, "city", 61808, 74, -90 ],
    [ "60496, 74, -81", 239.618, -470.852, 208.239, "city", 60496, 74, -81 ],
#    [ "GZ markers  one marker", -158.327, -582.118, 8.22524, "city", 32417, 80, -93 ],
#    [ "GZ markers  one marker", 97.3248, -544.326, 6.83208, "city", 30420, 78, -93 ],
#    [ "GZ markers  one marker", 108.532, -551.111, 6.82993, "city", 30336, 78, -93 ],
#    [ "GZ markers  one marker", 86.5805, -492.784, 60.0166, "city", 30473, 74, -90 ],
#    [ "GZ markers  one marker", -132.169, -637.239, 8.11365, "city", 32177, 84, -93 ],
  ]
]
#
# Palace
MG14 = [ 1, "GZ guy", 2, 120 ,
  [
    [ "58277, 70, -75 ", 467.321, -331.116, 294.91, "city", 58277, 70, -75 ],
    [ "58384, 60, -78 ", 386.313, -177.083, 260.518, "city", 58384, 60, -78 ],
    [ "57792, 46, -76 ", 338.75, 41.1883, 291.95, "city", 57792, 46, -76 ],
    [ "58422, 44, -76 ", 282.086, 53.5703, 293.757, "city", 58422, 44, -76 ],
    [ "60215, 66, -84", 243.691, -339.626, 157.405, "city", 60215, 66, -84 ],
    [ "60822, 64, -84", 173.38, -315.199, 158.217, "city", 60822, 64, -84 ],
    [ "60987, 69, -83 ", 167.893, -392.185, 181.574, "city", 60987, 69, -83 ],
    [ "61857, 56, -81 ", 58.2999, -197.159, 209.46, "city", 61857, 56, -81 ],
    [ "61013, 55, -80", 131.894, -172.566, 216.863, "city", 61013, 55, -80 ],
    [ "31661, 53, -77 ", -41.2759, -146.405, 274.388, "city", 31661, 53, -77 ],
    [ "60963, 52, -78 ", 128.527, -122.188, 261.352, "city", 60963, 52, -78 ],
    [ "46, 43, -80 ", -3.08397, 12.4945, 223.141, "city", 46, 43, -80 ],
    [ "32498, 46, -80 ", -98.4153, -28.1701, 223.632, "city", 32498, 46, -80 ],
    [ "33231, 55, -81", -182.556, -170.771, 198.891, "city", 33231, 55, -81 ],
    [ "33290, 58, -82 ", -196.998, -214.11, 196.267, "city", 33290, 58, -82 ],
    [ "31789, 47, -80 ", -47.6542, -61.9222, 221.684, "city", 31789, 47, -80 ],
    [ "32022, 50, -80", -68.2777, -96.0332, 221.684, "city", 32022, 50, -80 ],
    [ "32188, 47, -80", -77.9, -55.3034, 221.684, "city", 32188, 47, -80 ],
    [ "31995, 48, -80", -64.4581, -74.3091, 221.684, "city", 31995, 48, -80 ],
  ]
]



mgs = [(MG01,'MG01'),(MG02,'MG02'),(MG03,'MG03'),(MG04,'MG04'),(MG05,'MG05'),(MG06,'MG06'),(MG07,'MG07'),(MG08,'MG08'),(MG09,'MG09'),(MG10,'MG10'),(MG11,'MG11'),(MG12,'MG12'),(MG13,'MG13'),(MG14,'MG14'),]
