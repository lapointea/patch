#!/usr/bin/env python
# coding:utf-8
""":mod:`lib`
===================================

.. module:: patchLib
   :platform: Unix
   :synopsis: patch.lib
   :author: jbagory
   :date: 2017
"""
import maya.cmds as mc
import marsCore.foundations.curveLib as curveLib
import marsCore.foundations.dagLib as dag
import math as math

####################################################
def resetTransform(trgt):
    '''
    
    cheap ass reset transfrom with setattr
    resetTransform(trgt)    
    '''
    mc.setAttr( '%s.translate' % trgt , 0 ,0 ,0 )     
    mc.setAttr( '%s.rotate' % trgt , 0 ,0 ,0 )    
    mc.setAttr( '%s.scale' % trgt , 1 ,1 ,1 )
    
####################################################################
def locksSwitch(sel,T=True,R=True,S=True,V=True,lockdo='unlock',keydo=False):
    '''
    lock/unlock channels
    
    locksSwitch(sel,T=True,R=True,S=True,V=True,lockdo='unlock',keydo=False)
    '''
    lockstate = True
    keyState = True
    
    if lockdo =='lock':
        lockstate = True
    elif lockdo =='unlock':
        lockstate = False
    if keydo ==True:
        keyState = True
    elif keydo ==False:
        keyState = False
    if T == True :
        mc.setAttr('%s.translateX' % sel , l = lockstate , k = keyState)
        mc.setAttr('%s.translateY' % sel , l = lockstate , k = keyState)
        mc.setAttr('%s.translateZ' % sel , l = lockstate , k = keyState)
    if R == True :
        mc.setAttr('%s.rotateX' % sel , l = lockstate , k = keyState)
        mc.setAttr('%s.rotateY' % sel , l = lockstate , k = keyState)
        mc.setAttr('%s.rotateZ' % sel , l = lockstate , k = keyState)
    if S == True :
        mc.setAttr('%s.scaleX' % sel , l = lockstate , k = keyState)    
        mc.setAttr('%s.scaleY' % sel , l = lockstate , k = keyState)     
        mc.setAttr('%s.scaleZ' % sel , l = lockstate , k = keyState)
    if V == True :
        mc.setAttr('%s.visibility' % sel , l = lockstate , k = keyState)    


####################################################
def getRelatives(side,ctrlBase,digit):
    '''
    
    TEMP - get ctrl name, orig name, end of chain childrens
    getRelatives(side,ctrlBase,digit)
    '''
    
    ctrlName = '%s_%s_ctrl' % (side,ctrlBase)
    ctrlOrig = '%s_%s_ctrl_orig' % (side,ctrlBase) 
    ctrlEnd = '%s_%s_ctrl_end' % (side,ctrlBase)   
    if not mc.objExists(ctrlEnd):
        ctrlEnd = ctrlName        
    if digit :
        ctrlName = '%s_%02d' % ( ctrlName , digit )
        ctrlOrig = '%s_%s_ctrl_%02d_orig' % (side,ctrlBase,digit)
    ctrlEndChilds = mc.listRelatives( ctrlEnd , typ = 'transform', c = True  )

    
    return (ctrlName,ctrlOrig,ctrlEnd,ctrlEndChilds)

########################################################################################################
def linearWeightsOnSurf(surf,dir,reverseInf):
    '''

    changes weights on a surfaces with 2 influences tu get a linear weighting
    
    linearWeightsOnSurf(surf,dir,reverseInf)

    surf = 'nurbsPlane1'
    dir = 'u'
    reverseInf = False
    '''
    
    cvPercent = []
    crvPointNum = []

    # --- get surface skinCluster and infs
    surfShape = dag.getFirstShape(surf)
    surkSKN = mc.listConnections('%s.create' % surfShape , s = True )[0]
    if mc.objectType(surkSKN) == 'skinCluster' :
        surfSknInfs = mc.skinPercent(surkSKN , '%s.cv[*][*]' % surf , q = True , t = None)
        
        if not len(surfSknInfs) == 2 :
            print 'only works with 2 influencies'
            
        else :        
            # --- create curve from surface to get CV position percentages
            curveFromSurf = mc.duplicateCurve( '%s.%s[0.5]' %(surf,dir) , ch= False, o=True )[0]
            mc.rebuildCurve( curveFromSurf , ch=False,kcp=True,kr=0 )
            crvSpans = mc.getAttr('%s.spans' % curveFromSurf )
            crvDeg = mc.getAttr('%s.degree' % curveFromSurf )
            crvPointNum = crvSpans+crvDeg
            # --- get cv position percentages and use it as linear skinWeights on surface
            for i in range(0,crvPointNum):
                cvPos = mc.pointPosition('%s.cv[%d]' %(curveFromSurf,i) )
                param = curveLib.getClosestPointOnCurve(curveFromSurf, cvPos, space='world')[1]
                percent = curveLib.findPercentFromParam(curveFromSurf, param)   

                if reverseInf == False :
                    if dir == 'u':
                        mc.skinPercent(surkSKN,'%s.cv[*][%d]' %(surf,i) , transformValue=[(surfSknInfs[0],1 - percent), (surfSknInfs[1],percent)])
                    if dir == 'v':
                        mc.skinPercent(surkSKN,'%s.cv[%d][*]' %(surf,i) , transformValue=[(surfSknInfs[0],1 - percent), (surfSknInfs[1],percent)])
                elif reverseInf == True :
                    if dir == 'u':
                        mc.skinPercent(surkSKN,'%s.cv[*][%d]' %(surf,i) , transformValue=[(surfSknInfs[1],1 - percent), (surfSknInfs[0],percent)])
                    if dir == 'v':
                        mc.skinPercent(surkSKN,'%s.cv[%d][*]' %(surf,i) , transformValue=[(surfSknInfs[1],1 - percent), (surfSknInfs[0],percent)]) 
        mc.delete(curveFromSurf)        
    else :
        print 'No skinCluster on surf'


########################################################################################################
def fromCurveWeightsOnSurf(surf,dir,reverseInf,animeCurve):
    ''' 
    
    changes weights on a surfaces with 2 influences, uses an animationCurve to go from linear to custom (curve must be from 0 to 1 in every axis )
    
    fromCurveWeightsOnSurf(surf,dir,reverseInf,animeCurve)
    
    surf = 'nurbsPlane1'
    dir = 'u'
    reverseInf = False
    animeCurve = 'locator3_translateY'   
    '''

    cvPercent = []
    crvPointNum = []

    # --- get surface skinCluster and infs
    surfShape = dag.getFirstShape(surf)
    surkSKN = mc.listConnections('%s.create' % surfShape , s = True )[0]
    if mc.objectType(surkSKN) == 'skinCluster' :
        surfSknInfs = mc.skinPercent(surkSKN , '%s.cv[*][*]' % surf , q = True , t = None)
        
        if not len(surfSknInfs) == 2 :
            print 'only works with 2 influencies'
            
        else :        
            # --- create curve from surface to get CV position percentages
            curveFromSurf = mc.duplicateCurve( '%s.%s[0.5]' %(surf,dir) , ch= False, o=True )[0]
            mc.rebuildCurve( curveFromSurf , ch=False,kcp=True,kr=0 )
            crvSpans = mc.getAttr('%s.spans' % curveFromSurf )
            crvDeg = mc.getAttr('%s.degree' % curveFromSurf )
            crvPointNum = crvSpans+crvDeg
            # --- creates frameCacheNode for linear convert
            convertFC = mc.createNode('frameCache' , n = 'tempConvert_fc' )
            mc.connectAttr('%s.output' % animeCurve , '%s.stream' % convertFC , f = True )               
            # --- get cv position percentages and use it as linear skinWeights on surface
            for i in range(0,crvPointNum):
                cvPos = mc.pointPosition('%s.cv[%d]' %(curveFromSurf,i) )
                param = curveLib.getClosestPointOnCurve(curveFromSurf, cvPos, space='world')[1]
                percent = curveLib.findPercentFromParam(curveFromSurf, param)
                mc.setAttr('%s.varyTime' % convertFC , percent )
                percent = mc.getAttr( '%s.varying' % convertFC )

                if reverseInf == False :
                    if dir == 'u':
                        mc.skinPercent(surkSKN,'%s.cv[*][%d]' %(surf,i) , transformValue=[(surfSknInfs[0],1 - percent), (surfSknInfs[1],percent)])
                    if dir == 'v':
                        mc.skinPercent(surkSKN,'%s.cv[%d][*]' %(surf,i) , transformValue=[(surfSknInfs[0],1 - percent), (surfSknInfs[1],percent)])
                elif reverseInf == True :
                    if dir == 'u':
                        mc.skinPercent(surkSKN,'%s.cv[*][%d]' %(surf,i) , transformValue=[(surfSknInfs[1],1 - percent), (surfSknInfs[0],percent)])
                    if dir == 'v':
                        mc.skinPercent(surkSKN,'%s.cv[%d][*]' %(surf,i) , transformValue=[(surfSknInfs[1],1 - percent), (surfSknInfs[0],percent)]) 
        mc.delete(curveFromSurf,convertFC)        
    else :
        print 'No skinCluster on surf'

###############################################################################
def sineWeightsOnSurf(surf,dir,reverseInf):
    ''' 
    
    changes weights on a surfaces with 2 influences, uses cosinus to create a perfect spline fallof
    
    sineWeightsOnSurf(surf,dir,reverseInf)
    
    surf = 'nurbsPlane1'
    dir = 'u'
    reverseInf = False 
    '''
    
    cvPercent = []
    crvPointNum = []

    # --- get surface skinCluster and infs
    surfShape = dag.getFirstShape(surf)
    surkSKN = mc.listConnections('%s.create' % surfShape , s = True )[0]
    if mc.objectType(surkSKN) == 'skinCluster' :
        surfSknInfs = mc.skinPercent(surkSKN , '%s.cv[*][*]' % surf , q = True , t = None)
        
        if not len(surfSknInfs) == 2 :
            print 'only works with 2 influencies'
            
        else :        
            # --- create curve from surface to get CV position percentages
            curveFromSurf = mc.duplicateCurve( '%s.%s[0.5]' %(surf,dir) , ch= False, o=True )[0]
            mc.rebuildCurve( curveFromSurf , ch=False,kcp=True,kr=0 )
            crvSpans = mc.getAttr('%s.spans' % curveFromSurf )
            crvDeg = mc.getAttr('%s.degree' % curveFromSurf )
            crvPointNum = crvSpans+crvDeg
            # --- get cv position percentages and use it as linear skinWeights on surface
            for i in range(0,crvPointNum):
                cvPos = mc.pointPosition('%s.cv[%d]' %(curveFromSurf,i) )
                param = curveLib.getClosestPointOnCurve(curveFromSurf, cvPos, space='world')[1]
                percent = curveLib.findPercentFromParam(curveFromSurf, param)
                percent = ((math.cos(2*percent*(math.pi)))+1)/2

                if reverseInf == False :
                    if dir == 'u':
                        mc.skinPercent(surkSKN,'%s.cv[*][%d]' %(surf,i) , transformValue=[(surfSknInfs[0],1 - percent), (surfSknInfs[1],percent)])
                    if dir == 'v':
                        mc.skinPercent(surkSKN,'%s.cv[%d][*]' %(surf,i) , transformValue=[(surfSknInfs[0],1 - percent), (surfSknInfs[1],percent)])
                elif reverseInf == True :
                    if dir == 'u':
                        mc.skinPercent(surkSKN,'%s.cv[*][%d]' %(surf,i) , transformValue=[(surfSknInfs[1],1 - percent), (surfSknInfs[0],percent)])
                    if dir == 'v':
                        mc.skinPercent(surkSKN,'%s.cv[%d][*]' %(surf,i) , transformValue=[(surfSknInfs[1],1 - percent), (surfSknInfs[0],percent)]) 
            mc.delete(curveFromSurf)        
    else :
        print 'No skinCluster on surf'
        
###############################################################################
def removeFromAllSets(remSetList=[]):
    '''
    remove objects in list from all sets

    :param remSetList: list
    :return:
    '''
    for obj in remSetList:
        getSets = mc.listSets(object = obj)
        if getSets:
            for set in getSets:
                mc.sets(obj , rm = set)

def removeFromSet(remSetList=[], remSet=''):
    '''
    remove list of objects from defined set
    :param remSetList: list
    :param remSet: string
    :return:
    '''
    for obj in remSetList:
        mc.sets(obj, rm=remSet)
###################################################################################################################

#######################################################################
def getAnimCurveDef(curveName):
    '''
    
    gets curveSpecification
    only works with auto and unified tangents

    getAnimCurveDef(curveName)
    '''
    keyCount = mc.keyframe( curveName , keyframeCount = True, q = True )
    keysAtFrame = mc.keyframe(curveName, query=True, index=(0,keyCount))
    keysValues = mc.keyframe(curveName, query=True, vc = True ,a = True, index=(0,keyCount))
    tangentsVal = mc.keyTangent(curveName , query = True , ia = True )
    curveDef = dict()
    curveDef['keyCount'] =keyCount
    curveDef['keysAtFrame'] =keysAtFrame
    curveDef['keysValues'] =keysValues
    curveDef['tangentsVal'] =tangentsVal
    print curveDef
    return curveDef

###################################################################################################################
def createAnimCurveFromDef(curveDef,curveNodeName):
    '''
    
    give dictionary definition of curve to function to recreate the animeCurve
    
    dict() # curveDef = {'tangentsVal': [0.0, 0.0, 56.329492519973265, 60.702413199576945], 'keyCount': 4, 'keysValues': [0.0, 0.0, 0.1531658647581936, 1.0], 'keysAtFrame': [0.0, 0.276, 0.5, 1.0]}
    string # curveNodeName = 'testAnimCurve'
    '''

    animCurve = mc.createNode('animCurveTU' , n = curveNodeName )
    for i in range(0,curveDef['keyCount']):
        mc.setKeyframe( curveNodeName , t = curveDef['keysAtFrame'][i] , v = curveDef['keysValues'][i] , itt = 'auto' , ott = 'auto' )
        mc.keyTangent( curveNodeName , edit = True , index = (i,i) , inAngle = curveDef['tangentsVal'][i] , outAngle = curveDef['tangentsVal'][i])
    #mc.lockNode(animCurve)
    
    return curveNodeName

#################################################################################################
def smartConnect(source,trgt):
    '''
    
    mass connect of one object base Attributes 'translate,rotate,scale,rotateOrder,jointOrient' to another
    smartConnect(source,trgt)
    '''
    mc.connectAttr('%s.translate' %source , '%s.translate' %trgt )
    mc.connectAttr('%s.rotate' %source , '%s.rotate' %trgt )
    mc.connectAttr('%s.scale' %source , '%s.scale' %trgt )
    mc.connectAttr('%s.rotateOrder' %source , '%s.rotateOrder' %trgt )
    if mc.objectType(source) == 'joint' :
        if mc.objectType(trgt) == 'joint' :
            mc.connectAttr('%s.jointOrient' %source , '%s.jointOrient' %trgt )

#################################################################################################
def smartcopyAttr(source,trgt):
    '''
    
    mass copy of one object base Attributes 'translate,rotate,scale,rotateOrder,jointOrient' to another
    smartcopyAttr(source,trgt)
    '''
    TR = mc.getAttr('%s.translate' %source)[0]
    RO = mc.getAttr('%s.rotate' %source)[0]
    SC = mc.getAttr('%s.scale' %source)[0]
    
    try:mc.setAttr('%s.translate' %trgt, TR[0],TR[1],TR[2])
    except:pass
    try:mc.setAttr('%s.rotate' %trgt, RO[0],RO[1],RO[2])   
    except:pass 
    try:mc.setAttr('%s.scale' %trgt, SC[0],SC[1],SC[2])   
    except:pass 
    try:mc.setAttr('%s.rotateOrder' %trgt, mc.getAttr('%s.rotateOrder' %source))
    except:pass
    if mc.objectType(source) == 'joint' :
        if mc.objectType(trgt) == 'joint' :
            JO = mc.getAttr('%s.jointOrient' %source)[0]
            try:mc.setAttr('%s.jointOrient' %trgt, JO[0],JO[1],JO[2])
            except:pass

###########################################################################################################
def basicBPMOnNurbs(SKC='', holdJnt=''):
    '''
    makes basic bpm connections on nurbs
    basicBPMOnNurbs(SKC='', holdJnt='')
    :param SKC: string
    :param holdJnt: string
    :return:
    '''
    if mc.objExists(SKC):
        shape = mc.listConnections('%s.outputGeometry[0]' %SKC , s=True)[0]
        cvs = mc.ls('%s.cv[*][*]' %shape)       
        skinJts = mc.skinPercent(SKC, cvs, transform=None, query=True)
        for i,jnt in enumerate(skinJts):
            if jnt == holdJnt :
                mc.connectAttr('%s.worldInverseMatrix[0]' %jnt, '%s.bindPreMatrix[%d]' %(SKC, i) ) 
            else:
                mc.connectAttr('%s.parentInverseMatrix[0]' %jnt, '%s.bindPreMatrix[%d]' %(SKC, i) )

###########################################################################################################
def addTag(targets=[],tag=''):
    '''
    
    addTag(targets=[],tag='')
    addTag : wil add a string extra attribute, that will allow you to track back the object later
    '''
    taggedList = []
    for each in targets :
        Attr = tag
        if not mc.ls('%s.%s' %(each,Attr)):
            mc.addAttr( each , ln = Attr , dt = 'string')
            mc.setAttr('%s.%s' %(each,Attr) , l=True)
            taggedList.append(each)
    return taggedList
            
            
def trackTag(tag=''):
    '''
    
    trackTag(tag='')
    trackTag : will allow you to track back objects from their tags
    '''
    nodeList = []
    trackNodes = mc.ls('*.%s' %tag)
    for node in trackNodes:
        strippedName = node.replace('.%s' %tag , '')
        nodeList.append(strippedName)
    return(nodeList)
###########################################################################################################
def getAxises(aimAsVec,upvAsVec):
    '''

    :param aimAsVec: vector as a list [0,0,0]
    :param upvAsVec: vector as a list [0,0,0]
    :return: return list of axises and directions like [['y', '-1'], ['x', '1'], ['z', '1']]
    '''
    vecSum = [ aimAsVec[0]+upvAsVec[0],aimAsVec[1]+upvAsVec[1],aimAsVec[2]+upvAsVec[2] ]

    lastindex = 0
    for a, axis in enumerate(vecSum):
        if not axis == 1:
            lastindex = a        
    lastVec = [0,0,0]
    lastVec[lastindex] = 1

    vectorList = (aimAsVec,upvAsVec,lastVec)
    axises = [[],[],[]]

    for i, each in enumerate(vectorList):
        for a, axis in enumerate(each):
            if not axis == 0:
                direction = ''
                if axis >0: direction = '1'
                if axis <0: direction = '-1'
                transformAxis = ''
                if a == 0 : transformAxis = 'x'
                if a == 1 : transformAxis = 'y'
                if a == 2 : transformAxis = 'z'
                
                axises[i] = [transformAxis,direction]
    return axises
#copySkinCluster############################################################################################
def copySkinClusterPoly(skinsource,skintarget):
    skinClusterSource = mc.ls(mc.listHistory(skinsource, pdo=True),type='skinCluster')
    vtxList = mc.polyEvaluate(skinsource, vertex=True)
    vtx = '%s.vtx[0:%d]' % (skinsource, vtxList)
    skinJts = mc.skinPercent(skinClusterSource[0], vtx, transform=None, query=True)
    newSkinCluster = mc.skinCluster(skinJts, skintarget, n='%s_skinCluster' % skintarget, tsb = True)[0]
    mc.copySkinWeights( ss=skinClusterSource[0], ds=newSkinCluster, noMirror=True )
    mc.setAttr('%s.skinningMethod' %newSkinCluster , mc.getAttr('%s.skinningMethod' %skinClusterSource[0]) )  
    return newSkinCluster
#copySkinCluster############################################################################################
def copySkinClusterNurbs(skinsource,skintarget):
    skinClusterSource = mc.ls(mc.listHistory(skinsource, pdo=True),type='skinCluster')
    vtx = '%s.cv[*][*]' %skinsource
    skinJts = mc.skinPercent(skinClusterSource[0], vtx, transform=None, query=True)
    newSkinCluster = mc.skinCluster(skinJts, skintarget, n='%s_skinCluster' % skintarget, tsb = True)[0]
    mc.copySkinWeights( ss=skinClusterSource[0], ds=newSkinCluster, noMirror=True )
    mc.setAttr('%s.skinningMethod' %newSkinCluster , mc.getAttr('%s.skinningMethod' %skinClusterSource[0]) )    
    return newSkinCluster
########################################################################################################
def getNurbsWeightsDict(surfSource):
    skinClusterSource = mc.ls(mc.listHistory(surfSource, pdo=True),type='skinCluster')[0]
    vtx = '%s.cv[*][*]' %surfSource
    getInfs = mc.skinPercent(skinClusterSource, vtx, transform=None, query=True)
    getWeights = dict()
    cvs = mc.ls('%s.cv[*][*]' %surfSource , fl=True )            
    for cv in cvs:
        weightList = []
        for inf in getInfs:
            infWeight = mc.skinPercent(skinClusterSource,cv,q=True, t=inf)
            weightList.append([inf,infWeight])
        getWeights[cv] = weightList        
    return getWeights
########################################################################################################    
def switchInfInWeightDict(weightDict,switchInf):
    newWeightDict = dict()
    infsTargets = weightDict.keys()
    for key in infsTargets:
        infList = weightDict.get(key)
        for i, inf in enumerate(infList):
            if inf[0] == switchInf[0]:
                inf[0] = switchInf[1]
        newWeightDict[key] = infList
    return newWeightDict
######################################################################################################## 
def reassignWeightDict(surfSource,newWeightDict,outInf):
    skinClusterSource = mc.ls(mc.listHistory(surfSource, pdo=True),type='skinCluster')[0]
    mc.setAttr('%s.normalizeWeights' %skinClusterSource , 1 )
    reapplyWeightDict = newWeightDict
    infTargets = reapplyWeightDict.keys()
    for key in infTargets:
        infList = reapplyWeightDict.get(key)
        for i, inf in enumerate(infList):
            infOnPoint = mc.skinPercent(skinClusterSource, key, transform=None, query=True)
            if not inf[0] in infOnPoint:
                mc.skinCluster(skinClusterSource,e=True, ai=inf[0])
        mc.skinPercent(skinClusterSource,key,tv = infList )  
    if outInf:
        mc.skinCluster(skinClusterSource,e=True,ri=outInf)
######################################################################################################## 
def getOppositeRo(roIndex):
    roSwitchList = [5,3,4,1,2,0]
    oppositeRo = roSwitchList[roIndex]
    return oppositeRo
######################################################################################################## 
def createOppositeRoSwitch(inputNode,outputNode):
    roSwitchList = [5,3,4,1,2,0]
    choiceNode = mc.createNode('choice',n= '%s_ch' %inputNode)
    for i,each in enumerate(roSwitchList):
        mc.addAttr( choiceNode , ln = 'ro%d' %i , at = 'long' , dv = roSwitchList[i] )
        mc.connectAttr('%s.ro%d' %(choiceNode,i) , '%s.input[%s]' %(choiceNode,i) )
    mc.connectAttr('%s.rotateOrder' %inputNode ,'%s.selector' %choiceNode)
    mc.connectAttr('%s.output' %choiceNode , '%s.rotateOrder' %outputNode )

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

