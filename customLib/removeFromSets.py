import maya.cmds as mc

def removeFromAllSets(remSetList=[]):
    for obj in remSetList:
        getSets = mc.listSets(object = obj)
        if getSets:
            for set in getSets:
                mc.sets(obj , rm = set)

def removeFromSet(remSetList=[] , remSet='' ):
        for obj in remSetList :
            mc.sets(obj , rm = remSet)


