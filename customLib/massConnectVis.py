import maya.cmds as mc

'''
those defs are used to create custom visibility attributes
They are created from a bunch of object sets
The creation part is meant to be run during publish of the rig_skin, but can be run anyTime as long as the ctrl shapes are not replaced later along the pipeline
'''

def disconnectVisAttr(ctrl='',attr=''):    
    # --- disconnect connections to Ik ctrl vis switch on spines
    # ctrl = neckIkRoot
    # attr = 'ikCtrlVis'    
    outCons = mc.listConnections('%s.%s' %(ctrl,attr) , p=True)
    if outCons:
        for con in outCons:
            mc.setAttr(con,l=False)
            mc.setAttr('%s.%s' %(ctrl,attr),1)
            mc.disconnectAttr('%s.%s' %(ctrl,attr),con)
            

def massConnectVis(testCon=False):
    # --- uses the sets in the rigSkin scene to connect visibility attributes
    visSwitchSuffix = 'visSwitch_set'
    if mc.objExists('all_%s' %visSwitchSuffix):

        allVisSets = []

        trackdval = mc.ls('*.dval' )
        for track in trackdval:
            if mc.objectType(track) == 'objectSet':
                strippedName = track.split('.',1)[0]
                allVisSets.append(strippedName)

        for visSet in allVisSets:
            strippedName = visSet.split('__')
            nodeName = strippedName[0]
            attrName = strippedName[1]
            dval = mc.getAttr('%s.dval' %visSet)
            objList = mc.listConnections('%s.dagSetMembers' %visSet)
            
            if not mc.ls('%s.________' %nodeName):
                mc.addAttr( nodeName , ln = '________' , at = 'enum' , en = 'ctrl_vis_extra' )
                mc.setAttr('%s.________' %nodeName , edit = True , cb = True , l=True)            
            
            if not mc.ls('%s.%s' %(nodeName,attrName)):
                mc.addAttr( nodeName , ln = attrName , at = 'bool' , dv = dval )
                mc.setAttr('%s.%s' %(nodeName,attrName) , edit = True , k = True )
                
            for obj in objList:
                if mc.objExists(obj):
                    objShapes = mc.listRelatives(obj,s=True )
                    for objShape in objShapes:
                        mc.setAttr('%s.visibility' %objShape, l=False)
                        shapeCon = mc.listConnections('%s.visibility' %objShape , p=True)
                        if shapeCon:
                            mc.disconnectAttr(shapeCon[0],'%s.visibility' %objShape)
                        mc.connectAttr('%s.%s' %(nodeName,attrName),'%s.visibility' %objShape )
        if testCon == False:
            allVisSwitch = mc.ls('*visSwitch_set')
            mc.delete(allVisSwitch)
            
            allVisSets = []
            trackdval = mc.ls('*.dval' )
            for track in trackdval:
                if mc.objectType(track) == 'objectSet':
                    strippedName = track.split('.',1)[0]
                    allVisSets.append(strippedName)        
            mc.delete(allVisSets)
            
        elif testCon == True:
            mc.rename('all_%s' %visSwitchSuffix , 'TESTED____all_%s____PLEASE_UNDO' %visSwitchSuffix)


def massCreateVisSets(CtrlToVisAttrList):
    # --- uses list of dictionnaries to connect visibility attributes
    '''
    The py file creating the list of dictionnaries must be organised as follow:
    
    ctrlSource = ''
    attrSource = ''
    dval = 0
    objList = [[],dval]
    attrToVisList = {ctrlSource:{attrSource:objList}}
    CtrlToVisAttrList = [attrToVisList]
                
    '''
    visSwitchMainSet = 'all_visSwitch_set'
    if not mc.objExists(visSwitchMainSet):
        mc.sets(n=visSwitchMainSet)

    for ctrlDict in CtrlToVisAttrList:
        ctrlSource = ctrlDict.keys()[0]
        attrDict = ctrlDict.get(ctrlSource)
        attrSource = attrDict.keys()[0]
        objDict = attrDict.get(attrSource)
        objList = objDict[0]
        dval = objDict[1]

        sourceSetName = '%s__source_visSwitch_set' %ctrlSource
        attrSetName = '%s__%s__set' %(ctrlSource,attrSource)

        if not mc.objExists(sourceSetName):
            mc.sets(n=sourceSetName)
            mc.sets(sourceSetName,add=visSwitchMainSet)
        if not mc.objExists(attrSetName):
            mc.sets(n=attrSetName)
            mc.sets(attrSetName,add=sourceSetName)
            mc.addAttr( attrSetName , ln = 'dval' , at = 'bool' , dv = dval )
            mc.setAttr('%s.dval' %attrSetName , edit = True , k = True )

        for obj in objList:
            print obj
            if mc.objExists(obj):
                mc.sets(obj,add=attrSetName)


def createNewAttrSet():
    # --- create no set from selection. selected object will host new attribute
    visSwitchMainSet = 'RIG:all_visSwitch_set'
    ctrlSource = mc.ls(sl=True)[0]
    mc.select(cl=True)

    ctrlSourceSet = '%s__source_visSwitch_set' %ctrlSource
    if not mc.objExists(ctrlSourceSet):
        mc.sets(n=ctrlSourceSet)
        mc.sets(ctrlSourceSet , add=visSwitchMainSet)

    blankAttrSet = '%s__NEWATTR__set' %ctrlSource
    mc.sets(n=blankAttrSet)
    mc.sets(blankAttrSet , add=ctrlSourceSet)

    mc.addAttr( blankAttrSet , ln = 'dval' , at = 'bool' , dv = 1 )
    mc.setAttr('%s.dval' %blankAttrSet , edit = True , k = True )
