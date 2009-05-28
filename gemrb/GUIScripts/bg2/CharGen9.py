# -*-python-*-
# GemRB - Infinity Engine Emulator
# Copyright (C) 2003-2004 The GemRB Project
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# $Id$
# character generation (CharGen9.py)
import GemRB
from CharGenCommon import *
from ie_stats import *
from ie_slots import *
from ie_spells import *
from GUICommon import *
from GUICommonWindows import *
from LUProfsSelection import *

CharGenWindow = 0

def OnLoad():
	global CharGenWindow
	DisplayOverview (9)

	return

# we need to redefine this or we're stuck in an include loop with CharGenCommon
def NextPress():
	FinishCharGen()
	return

def FinishCharGen():
	# Lay on hands, turn undead and backstab multiplier get set by the core
	# set my character up
	MyChar = GemRB.GetVar ("Slot")
	Class = GemRB.GetPlayerStat (MyChar, IE_CLASS)
	ClassIndex = ClassTable.FindValue (5, Class)
	ClassName = ClassTable.GetRowName (ClassIndex)
	IsMulti = IsMultiClassed (MyChar, 1)
	Levels = [GemRB.GetPlayerStat (MyChar, IE_LEVEL), GemRB.GetPlayerStat (MyChar, IE_LEVEL2), \
			GemRB.GetPlayerStat (MyChar, IE_LEVEL3)]

	# weapon proficiencies
	# set the base number of attacks; effects will add the proficiency bonus
	GemRB.SetPlayerStat (MyChar, IE_NUMBEROFATTACKS, 2)
	ProfsSave (MyChar, LUPROFS_TYPE_CHARGEN)

	#lore, thac0, and saves
	SetupSavingThrows (MyChar)
	SetupThaco (MyChar)
	SetupLore (MyChar)

	# mage spells
	TableName = ClassSkillsTable.GetValue (Class, 2, 0)
	if TableName != "*":
		index = 0
		if IsMulti[0]>1:
			#find out which class gets mage spells
			for i in range (IsMulti[0]):
				if ClassSkillsTable.GetValue (IsMulti[i+1], 2, 0) != "*":
					index = i
					break
		SetupSpellLevels(MyChar, TableName, IE_SPELL_TYPE_WIZARD, Levels[index])

	# apply class/kit abilities
	KitIndex = GetKitIndex (MyChar)
	if IsMulti[0]>1:
		#get the class abilites for each class
		for i in range (IsMulti[0]):
			TmpClassName = ClassTable.GetRowName (ClassTable.FindValue (5, IsMulti[i+1]) )
			ABTable = ClassSkillsTable.GetValue (TmpClassName, "ABILITIES")
			if ABTable != "*" and ABTable[:6] != "CLABMA":
				AddClassAbilities (MyChar, ABTable, Levels[i], Levels[i])
	else:
		if KitIndex:
			ABTable = KitListTable.GetValue (str(KitIndex), "ABILITIES")
		else:
			ABTable = ClassSkillsTable.GetValue (ClassName, "ABILITIES")
		if ABTable != "*" and ABTable[:6] != "CLABMA": # mage kits specify ability tables which don't exist
			AddClassAbilities (MyChar, ABTable, Levels[0], Levels[0])

	# apply starting (alignment dictated) abilities
	# pc, table, new level, level diff, alignment
	AlignmentTable = GemRB.LoadTableObject ("aligns")
	AlignmentAbbrev = AlignmentTable.FindValue (3, GemRB.GetPlayerStat (MyChar, IE_ALIGNMENT))
	AddClassAbilities (MyChar, "abstart", 7,7, AlignmentAbbrev)

	# setup starting gold (uses a roll dictated by class
	TmpTable = GemRB.LoadTableObject ("strtgold")
	temp = GemRB.Roll (TmpTable.GetValue (Class, 1),TmpTable.GetValue (Class, 0), TmpTable.GetValue (Class, 2))
	GemRB.SetPlayerStat (MyChar, IE_GOLD, temp * TmpTable.GetValue (Class, 3))

	# save the appearance
	SetColorStat (MyChar, IE_HAIR_COLOR, GemRB.GetVar ("HairColor") )
	SetColorStat (MyChar, IE_SKIN_COLOR, GemRB.GetVar ("SkinColor") )
	SetColorStat (MyChar, IE_MAJOR_COLOR, GemRB.GetVar ("MajorColor") )
	SetColorStat (MyChar, IE_MINOR_COLOR, GemRB.GetVar ("MinorColor") )
	#SetColorStat (MyChar, IE_METAL_COLOR, 0x1B )
	#SetColorStat (MyChar, IE_LEATHER_COLOR, 0x16 )
	#SetColorStat (MyChar, IE_ARMOR_COLOR, 0x17 )
	GemRB.SetPlayerStat (MyChar, IE_EA, 2 )

	# save the name and starting xp (can level right away in game)
	GemRB.SetPlayerName (MyChar, GemRB.GetToken ("CHARNAME"), 0)

	# does all the rest
	LargePortrait = GemRB.GetToken ("LargePortrait")
	SmallPortrait = GemRB.GetToken ("SmallPortrait")
	GemRB.FillPlayerInfo (MyChar, LargePortrait, SmallPortrait)

	# add the starting inventory for tob
	if GameIsTOB():
		# get the kit (or use class if no kit) to load the start table
		if KitIndex == 0:
			EquipmentColName = ClassName
			# sorcerers are missing from the table, use the mage equipment instead
			if EquipmentColName == "SORCERER":
				EquipmentColName = "MAGE"
		else:
			EquipmentColName = KitListTable.GetValue (KitIndex, 0)

		EquipmentTable = GemRB.LoadTableObject ("25stweap")

		# a map of slots in the table to the real slots
		# SLOT_BAG is invalid, so use the inventory (first occurence)
		# SLOT_INVENTORY: use -1 instead, that's what CreateItem expects
		RealSlots = [ SLOT_ARMOUR, SLOT_SHIELD, SLOT_HELM, -1, SLOT_RING, \
					SLOT_RING, SLOT_CLOAK, SLOT_BOOT, SLOT_AMULET, SLOT_GLOVE, \
					SLOT_BELT, SLOT_QUIVER, SLOT_QUIVER, SLOT_QUIVER, \
					SLOT_ITEM, SLOT_ITEM, SLOT_ITEM, -1, -1, SLOT_WEAPON ]

		#loop over rows - item slots
		for slot in range(0, EquipmentTable.GetRowCount ()):
			slotname = EquipmentTable.GetRowName (slot)
			item = EquipmentTable.GetValue (slotname, EquipmentColName)

			# no item - go to next
			if item == "*":
				continue
			
			realslot = GemRB.GetSlots (MyChar, RealSlots[slot], -1)

			if realslot == (): # this shouldn't happen!
				continue

			# if an item contains a comma, the rest of the value is the stack
			if "," in item:
				item = item.split(",")
				count = int(item[1])
				item = item[0]
			else:
				count = 0

			targetslot = realslot[0]
			SlotType = GemRB.GetSlotType (targetslot, MyChar)
			i = 1

			# if there are no free slots, CreateItem will create the item on the ground
			while not GemRB.CanUseItemType (SlotType["Type"], item, MyChar) and i < len(realslot):
				targetslot = realslot[i]
				SlotType = GemRB.GetSlotType (targetslot, MyChar)
				i = i + 1

			GemRB.CreateItem(MyChar, item, targetslot, count, 0, 0)
 			GemRB.ChangeItemFlag (MyChar, targetslot, IE_INV_ITEM_IDENTIFIED, OP_OR)

	playmode = GemRB.GetVar ("PlayMode")
	if playmode >=0:
		#LETS PLAY!!
		GemRB.EnterGame()
	else:
		#leaving multi player pregen
		if CharGenWindow:
			CharGenWindow.Unload ()
		#when export is done, go to start
		if HasTOB():
			GemRB.SetToken ("NextScript","Start2")
		else:
			GemRB.SetToken ("NextScript","Start")
		GemRB.SetNextScript ("ExportFile") #export
	return
