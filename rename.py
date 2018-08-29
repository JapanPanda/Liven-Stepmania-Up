# This script is designed to rename all of the
# Stepmania files in order to create some comedic titles

import os
import sys
import random
import fileinput
import json

def main():
    choice = intro()
    if choice == "1":
        songFolders = findSongFolders()
        if getInput():
            wordList = getWords()
            confirm()
            changeSongs(wordList, songFolders)
            print("Finished changing songs.\nPlease remember to reload songs/courses in the Stepmania options menu")
            input("Press enter to quit\n")
        else:
            print("\nPlease put the executable in the Stepmania directory "
            "and run it again.\n")
            input("Press enter to quit\n")

    elif choice == "2":
        restoreSongs()
        print("Finished restoring songs.\nPlease remember to reload songs/courses in the Stepmania options menu")
        input("Press enter to quit\n")
    return

# Confirmation
def confirm():
    os.chdir(os.path.dirname(sys.argv[0]))
    if os.path.exists("songBackup"):
        print("\nWarning: You already changed the song names and have not restored them yet")
    choice = input("Are you absolutely sure you want to do this? (Y/N)\n\n>> ")
    choice = choice.lower()
    if choice == "y" or choice == "yes":
        return
    elif choice == "n" or choice == "no":
        sys.exit()
    else:
        print("\nInvalid choice, please choose Y or N.\n")

# Print wordList
def printWords(wordList):
    print("\nThe following words have been found inside words.txt")
    counter = 1
    for word in wordList:
        print(str(counter) + ". " + word)
        counter += 1

# Remove newline in word
def removeNewline(wordList):
    newWordList = [word.replace("\n", "") for word in wordList]
    return newWordList


# Introduce the program
def intro():
    print("This script will replace one of the words in all of"
        " your Stepmania song names \nwith words inside the words.txt file.")
    print("Note: This script will not work with Japanese characters (non-ASCII)\n")
    print("Note: To promote diversity, the script will not change single word titles")
    print("For example: Over the Period --> Over the Fence\n")
    print("Additionally, this script can also restore the names to its original\n")
    return input("What would you like to do?\n1. Change Names\n2. Restore Names\n\n>> ")

# Parse the words.txt file
def getWords():
    os.chdir(os.path.dirname(sys.argv[0]))
    try:
        wordFile = open("words.txt", "r+")
    except IOError:
        print("Could not find a words.txt file, creating one\n")
        wordFile = open("words.txt", "w+")

    wordList = wordFile.readlines()
    wordList = removeNewline(wordList)
    quit = False

    while not quit:
        printWords(wordList)
        choice = input("\nWhat would you like to do?\n1. Continue\n2. Edit words\n3. Quit\n\n>> ")

        if choice == "1":
            return wordList

        elif choice == "2":
            editWords(wordList)

        elif choice == "3":
            sys.exit()

        else:
            print("Error: Valid choices are 1, 2, 3\n")

# Edit the words.txt file
def editWords(wordList):
    quit = False
    while not quit:
        counter = 0
        printWords(wordList)
        choice = input("\nWhat would you like to do?\n1. Add\n2. Delete\n3. Stop Editing\n\n>> ")

        if choice == "1":
            newWord = input("\nWhat word would you like to add?\n\n>> ")
            wordList.append(newWord)

        elif choice == "2":
            printWords(wordList)
            deleteWord = input("\nWhat word would you like to delete\n\n>> ")
            wordList.pop((int(deleteWord) - 1))

        elif choice == "3":
            quit = True

        else:
            print("\nInvalid choice selected\n")

    with open("words.txt", "w") as wordFile:
        for words in wordList:
            wordFile.write(words + "\n")
    return

# Find Song folders
def findSongFolders():
    curPath = os.getcwd()
    try:
        os.chdir(os.path.dirname(sys.argv[0]) + "/Songs")
        curPath = os.getcwd()
        songFolders = next(os.walk(curPath))[1]
    except Exception as e:
        print("\nCould not find Song folder. \nAre you sure the .exe is located in the Stepmania folder?\n")
        print("This script is running from " + curPath)
        input("Press enter to quit\n")
        sys.exit()

    print("\nWorking from " + curPath + "\n\nFound these folders")
    for folder in songFolders:
        print("-- " + folder)
    return songFolders

# Change Song names
def changeSongs(wordList, songFolders):
    os.chdir(os.path.dirname(sys.argv[0]) + "/Songs")
    curPath = os.getcwd()
    backup = dict()
    for folder in songFolders:
        songBackup = dict()
        print("Changing songs in the " + folder + " folder")
        for root, dirs, files in os.walk(curPath + "/" + folder):
            for name in files:
                if name[-3:] == ".sm" or name[-4:] == ".ssc":
                    with open(os.path.join(root, name), "r+", encoding="utf-8-sig") as curFile:
                        try:
                            title = curFile.readline()
                            while not "#TITLE:" in title:
                                title = curFile.readline()
                            newTitle = changeWord(wordList, title)
                            if newTitle == None:
                                continue
                            print(title[7:-2].rstrip() + " --> " + newTitle[7:-2].rstrip())
                            songBackup[name] = title

                            curFile.seek(0)
                            lines = curFile.read().replace(title, newTitle)
                            curFile.seek(0)
                            curFile.truncate(0)
                            curFile.write(lines)
                        except UnicodeDecodeError:
                            print(name)

        backup[folder] = songBackup
    createBackup(backup)
    return

# Generate word to replace and replace a word in the Song name
def changeWord(wordList, title):
    actualTitle = title[7:]
    try:
        actualTitle.encode("ascii")
        word = generateWord(wordList)
        separatedTitle = actualTitle.split(" ")
        if len(separatedTitle) == 1:
            return
        index = random.randint(0, len(separatedTitle) - 1)
        if index == len(separatedTitle) - 1:
            word = word + ";\n"

        if separatedTitle[index].isupper():
            separatedTitle[index] = word.upper()
        elif separatedTitle[index][0].isupper():
            newWord = word[0].upper() + word[1:].lower()
            separatedTitle[index] = newWord
        else:
            word = word.lower()
            separatedTitle[index] = word

        newTitle = "#TITLE:"+ " ".join(separatedTitle)
        return newTitle
    except UnicodeEncodeError:
        print("Discarding " + actualTitle.rstrip())


# Generate word
def generateWord(wordList):
    index = random.randint(0, len(wordList) - 1)
    return wordList[index]

# Add entry to the backup file
def createBackup(backup):
    os.chdir(os.path.dirname(sys.argv[0]))
    with open("songBackup", "w") as backupFile:
      json.dump(backup, backupFile)
    return

# Restore Song names
def restoreSongs():
    os.chdir(os.path.dirname(sys.argv[0]))
    with open("songBackup") as backupFile:
        backup = json.load(backupFile)

    os.chdir(os.getcwd() + "/Songs")
    for folder, songs in backup.items():
        print("Restoring song names in " + folder + " folder")
        for root, dir, files in os.walk(os.getcwd() + "/" + folder):
            for name in files:
                if name in songs:
                    with open(os.path.join(root, name), "r+", encoding="utf-8") as curFile:
                        title = curFile.readline()
                        while not "#TITLE:" in title:
                            title = curFile.readline()
                        curFile.seek(0)
                        lines = curFile.read().replace(title, songs[name])
                        curFile.seek(0)
                        curFile.truncate(0)
                        curFile.write(lines)

    os.chdir(os.path.dirname(sys.argv[0]))
    os.remove("songBackup")
    return

# Get confirmation from user
def getInput():
    print("\n")
    quit = False
    while not quit:
        choice = input("Are these the correct folders? (Y/N)\n\n>> ")
        choice = choice.lower()

        if choice == "y" or choice == "yes":
            return 1

        elif choice == "n" or choice == "no":
            return 0

        else:
            print("\nInvalid choice, please pick Y / N")

if __name__ == "__main__":
    main()
