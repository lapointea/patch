import maya.cmds as mc
import marsCore.shapes.defs as shapes
reload(shapes)
import marsCore.orig as orig
reload(orig)
from marsAutoRig_stubby.patch.customLib import patchLib as patchLib
import marsCore.foundations.curveLib as curveLib
import marsCore.foundations.dagLib as dag
import marsAutoRig.brickCore.stickyRibbon as stickyRibbon
import math as math

##################################################################################################################################################################################################
#def patchLib.resetTransform(trgt):
#def patchLib.locksSwitch(sel,T=True,R=True,S=True,V=True,lockdo='unlock',keydo=False)
#def patchLib.getRelatives(side,ctrlBase,digit)
#orig.orig(objlist=[], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')
#shapes.create( sel, shape= 'circle', size= 1, scale= [1, 1, 1 ], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= None, colorDegradeTo= None, replace= True, middle= False)
##################################################################################################################################################################################################
#smartConnect(trgt,smart)
##################################################################################################################################################################################################
#xrivetTrOnNurbs(tr, surface, mainDirection = 1, out = 'worldSpace[0]', u = None, v = None,offsetOrient = [0, 0, 0],min=False)
#getXrivetEntryAvailable(xrivet)
#getOffsetFromXrivet(aim, upv)

def makeVolumeEars(smartParentTarget,smartDupTargets,side,sides):

    ###############################################################################################################################################
    # --- ears smart Rig
    #smartParentTarget = 'head_gimbal_ctrl'
    #smartDupTargets = ['L_ear_fk_ctrl_01_orig','R_ear_fk_ctrl_01_orig']
    earsNoXformGrp = 'ears_ctrl_noXformGrp' 
    WORLDGrp = 'WORLD'       
    ## --- create noXform Grp for ears
    mc.group(n=earsNoXformGrp,em=True)
    mc.parent(earsNoXformGrp,WORLDGrp)
    mc.hide(earsNoXformGrp)

    # --- duplicate the base of the fkHierarchy, will be use as base of smart hierarchy
    smartParent = mc.duplicate(smartParentTarget,po=True,n='%s_smart' %smartParentTarget)[0]
    mc.parent(smartParent,earsNoXformGrp)
    # --- duplicate all of the fks in one go to create fk_smarts
    smartsList = mc.duplicate(smartDupTargets)
    for i,each in enumerate(smartDupTargets):
        mc.parent(smartsList[i],w=True)

    # --- goes into the hierarchy of duplicated Fks and counts the depth of the hierarchy. stops when arrived at end of hierarchy
    hierarchyDepthList = []
    for i,each in enumerate(smartDupTargets): 
        hierarchyDepth = 0
        nexChild = ''
        stopLoop = False
        for j in range(0,20):
            if j == 0:
                nexChild = each
            getChild = mc.listRelatives(nexChild,c=True,f=True)        
            if getChild:
                for child in getChild:
                    if not mc.objectType(child) == 'nurbsCurve':                         
                        if mc.objectType(child) == 'joint':
                            splittedName1 = child.rsplit('|')[-1]
                            splittedName2 = splittedName1.split('offset')
                            
                            checkEnd = splittedName1.rsplit('_',1)[-1]
                            
                            if not len(splittedName2)>1:
                                if not checkEnd == 'end':
                                    nexChild = child
                                else:
                                    stopLoop = True
                                    hierarchyDepthList.append(j)
                                    break
            if stopLoop == True:
                break
        mc.delete(smartsList[i])
    # --- derives controls loop from hierarchy depth
    smartLoopLenthList = []
    for each in  hierarchyDepthList:  
        loopLength = (each/2)+2
        smartLoopLenthList.append(loopLength)
        
    # --- recreates hierarchy as smart nodes

    for i,each in enumerate(smartDupTargets):
        loop = smartLoopLenthList[i]
        baseName = each.split('_ctrl_' , 1)[0]
        ctrlName = 'ctrl'
        offsetName = 'offset'
        suff = '_smart'
        makeShape = False
        color = None

        parentNext = smartParent
        for j in range(0,loop):  
            num = j+1
             
            if j < loop-1 :
                if j == 0 :
                    doOffset = False
                    newCtrls = createFKSection(baseName,ctrlName,offsetName,num,suff,doOffset,makeShape,color)
                    mc.parent( newCtrls[1] , parentNext)
                    
                    trgt = newCtrls[0].rsplit('_',1)[0]
                    origTrgt = newCtrls[1].rsplit('_',1)[0]
                    smartConnect(trgt,newCtrls[0])
                    smartConnect(origTrgt,newCtrls[1])
                    parentNext = newCtrls[0]

                else :
                    doOffset = True
                    newCtrls = createFKSection(baseName,ctrlName,offsetName,num,suff,doOffset,makeShape,color)
                    mc.parent( newCtrls[0][1] , parentNext)
                    
                    trgt = newCtrls[0][0].rsplit('_',1)[0]
                    origTrgt = newCtrls[0][1].rsplit('_',1)[0]
                    offsetTrgt = newCtrls[1][0].rsplit('_',1)[0]
                    origOffsetTrgt = newCtrls[1][1].rsplit('_',1)[0]
                    smartConnect(trgt,newCtrls[0][0])
                    smartConnect(origTrgt,newCtrls[0][1])
                    smartConnect(offsetTrgt,newCtrls[1][0])
                    smartConnect(origOffsetTrgt,newCtrls[1][1])           
                    parentNext = newCtrls[0][0]
                    
            if j == loop-1:
                mc.select(cl=True)
                endJoint = mc.joint(n='%s_%s_end_smart' %(baseName,ctrlName))
                endOffsetOrig = mc.joint(n='%s_%s_%s_%02d_orig_smart' %(baseName,offsetName,ctrlName,loop))
                endOffset = mc.joint(n='%s_%s_%s_%02d_smart' %(baseName,offsetName,ctrlName,loop))
                            
                mc.setAttr('%s.radius' %endJoint, 0.1 )
                mc.setAttr('%s.radius' %endOffsetOrig, 0.1 )
                mc.setAttr('%s.drawStyle' %endOffsetOrig, 2)
                mc.setAttr('%s.radius' %endOffset, 0.1 )
                
                mc.parent(endJoint,parentNext)
                smartConnect('%s_%s_end' %(baseName,ctrlName),endJoint)
                smartConnect('%s_%s_%s_%02d_orig' %(baseName,offsetName,ctrlName,loop),endOffsetOrig)
                smartConnect('%s_%s_%s_%02d' %(baseName,offsetName,ctrlName,loop),endOffset)


    # --- creates volumeSurf and deforms for ears //temporary use of firstSurf
    rigPart = 'ear'
    deformGrp = 'ctrl_DeformGrp'
    endSurfDeformGrp = 'ears_endSurf_%s' %deformGrp

    # --- assign values for columeSurf characteristics
    volspansV = 16
    volspansU = 8
    volDeg = 3
    ## ---creates ears volSurfaces
    earCurveGUIDEList = ['L_topEar_curve_GUIDE','L_topMidtEar_curve_GUIDE','L_midtEar_curve_GUIDE','L_botMidEar_curve_GUIDE','L_BotEar_curve_GUIDE']
    earVolSurfList = []
    # --- create left volume surface
    duplicatedCurves = mc.duplicate(earCurveGUIDEList)
    loftCurves=[]
    mc.parent(duplicatedCurves , w=True)
    for u , curve in enumerate(duplicatedCurves):
        curveName = str(curve)
        strippedName = curveName.rsplit('_',1)[0]    
        loftCurves.append(mc.rename(curve,'%s_loftCurve' %strippedName))
    loftCurves=loftCurves[::-1]    
    volSurf = mc.loft(loftCurves,ch=False,ar=False,d=3,u=True,n='L_%s_volume_surfNurbs' %rigPart)[0]
    mc.rebuildSurface(volSurf,rt=0,su=volspansU , sv=volspansV , kc=True , ch=False)    
    mc.delete(loftCurves)
    mc.parent(volSurf,earsNoXformGrp)
    earVolSurfList.append(volSurf)
    # --- creates right ear surf from scale
    rVolsurf = mc.duplicate(volSurf ,n='R_%s_volume_surfNurbs' %rigPart)[0]
    rVolsurfUSpans = mc.getAttr('%s.spansU' %rVolsurf)
    rVolsurfVSpans = mc.getAttr('%s.spansV' %rVolsurf)
    rVolsurfUDeg = mc.getAttr('%s.degreeU' %rVolsurf)
    rVolsurfVDeg = mc.getAttr('%s.degreeV' %rVolsurf)
    rVolsurfUCount = rVolsurfUSpans+rVolsurfUDeg
    rVolsurfVCount = rVolsurfVSpans
    for u in range(0,rVolsurfUCount):
        for v in range(0,rVolsurfVCount):
            pointPos = mc.pointPosition('%s.cv[%d][%d]' %(rVolsurf,u,v) )
            mc.move(-pointPos[0] , pointPos[1] , pointPos[2] , '%s.cv[%d][%d]' %(rVolsurf,u,v) , a=True, ws=True )
    mc.reverseSurface(rVolsurf,d=1,ch=False)
    earVolSurfList.append(rVolsurf)

    mc.group(n = endSurfDeformGrp , em=True) 
    mc.parent(endSurfDeformGrp,smartParentTarget)
    volumeEarsDeformSKNList = []
    for s , surf in enumerate(earVolSurfList):
        ## --- creates and attaches jointsCloud
        side = sides[s]    
        sideEndSurfDeformGrp = '%s_%s' %(side,endSurfDeformGrp)
        mc.group(n=sideEndSurfDeformGrp,em=True)
        mc.parent(sideEndSurfDeformGrp,endSurfDeformGrp)
        
        UDeformsCount = 9
        VDeformCount = 10   
        endSurf = surf
        tempPOSI = tempPOSI = mc.createNode('pointOnSurfaceInfo', n = 'volumeSpine_temp_posi')
        mc.setAttr('%s.turnOnPercentage' %tempPOSI,True)
        mc.connectAttr('%s.worldSpace[0]' %endSurf , '%s.inputSurface' %tempPOSI )
        for i in range(0,UDeformsCount-1):
            for j in range(0,VDeformCount-1):    
                ## --- creates deform ctrl/skin hierarchy
                mc.select(cl=True)
                deformSkn = mc.joint(n='%s_%s_deform_U%02d_V%02d_SKN' %(side,rigPart,i,j) )
                mc.setAttr('%s.radius' %deformSkn , 0.01)
                mc.select(cl=True)
                deformCtrl = mc.joint(n='%s_%s_deform_U%02d_V%02d_ctrl' %(side,rigPart,i,j) )
                mc.setAttr('%s.radius' %deformCtrl , 0.01)
                mc.setAttr('%s.drawStyle' %deformCtrl,2)
                smartConnect(deformCtrl,deformSkn)
                shapes.create( deformCtrl, shape= 'pyramidDouble', size= 0.05, scale= [1, 1, 1 ], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= [0.5,0,0.5] , colorDegradeTo= None, replace= True, middle= False)        
                deformOrig = orig.orig(objlist=[deformCtrl], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')[0]
                deformAuto = orig.orig(objlist=[deformCtrl], suffix=['_auto'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')[0]
                mc.parent(deformSkn,deformAuto)
                volumeEarsDeformSKNList.append(deformSkn)
                ## --- getWorld Position placement for deform orig from UV
                UValue = ((1.000/(UDeformsCount-1))*i)
                VValue = ((1.000/(VDeformCount-1))*j)                      
                mc.setAttr('%s.parameterU' %tempPOSI , UValue)
                mc.setAttr('%s.parameterV' %tempPOSI , VValue)
                ctrlPos = mc.getAttr('%s.position' %tempPOSI)[0]
                mc.setAttr('%s.translate' %deformOrig , ctrlPos[0],ctrlPos[1],ctrlPos[2] )
                ## --- attach deformer ctrl/joints to endSurface
                xrivetTrOnNurbs(deformOrig, endSurf, mainDirection = 1, out = 'worldSpace[0]', u = None, v = None,
                                offsetOrient = [0,0,0] ,min=False) 
                ## --- reparent deform origs into rig
                mc.parent(deformOrig,sideEndSurfDeformGrp)        
        mc.select(cl=True)
        mc.delete(tempPOSI)
        
    ## --- TempCleanup of ears sets
    volumeEarsSkinSet = 'volume_ears_skin_set'
    mc.sets(volumeEarsDeformSKNList,n=volumeEarsSkinSet)
    mc.sets(volumeEarsSkinSet,add='skin_set')        
    ### --- disconnect inverseScale on ears to allow headScale
    fkEarsOrigs = ['L_ear_fk_ctrl_01_orig','R_ear_fk_ctrl_01_orig']
    for earOrig in fkEarsOrigs:
        mc.disconnectAttr('head_gimbal_ctrl.scale' , '%s.inverseScale' %earOrig )

#################################################################################################
def smartConnect(trgt,smart):
    mc.connectAttr('%s.translate' %trgt , '%s.translate' %smart )
    mc.connectAttr('%s.rotate' %trgt , '%s.rotate' %smart )
    mc.connectAttr('%s.scale' %trgt , '%s.scale' %smart )
    mc.connectAttr('%s.rotateOrder' %trgt , '%s.rotateOrder' %smart )
    if mc.objectType(trgt) == 'joint' :
        if mc.objectType(smart) == 'joint' :
            mc.connectAttr('%s.jointOrient' %trgt , '%s.jointOrient' %smart )
 
#################################################################################################
def xrivetTrOnNurbs(tr, surface, mainDirection = 1, out = 'worldSpace[0]', u = None, v = None,
                    offsetOrient = [0, 0, 0],min=False):
    '''

    :param tr:
    :type tr:
    :param surface:
    :type surface:
    :param mainDirection:
    :type mainDirection:
    :param out:
    :type out:
    :param u:
    :type u:
    :param v:
    :type v:
    :param offsetOrient:
    :type offsetOrient:
    :return:
    :rtype:
    '''
    attrsFrom = ['outTranslation', 'outRotation', 'outScale', 'outShear']
    attrsTo = ['translate', 'rotate', 'scale', 'shear']
    require_plugin = ['xRivet']
    for plugin in require_plugin:
        if not mc.pluginInfo(plugin, q = True, l = True):
            try:
                mc.loadPlugin(plugin, quiet = True)
            except:
                print 'warning : {0} plugin could not load'.format(plugin)
                return
    xRivet = '{0}_xRivetNurbs'.format(surface)
    if not mc.objExists(xRivet):
        xRivet = mc.createNode('xRivetNurbs', n = xRivet)
        mc.connectAttr('{0}.{1}'.format(surface, out), '{0}.inNurbsSurface'.format(xRivet))
    indexLast = getXrivetEntryAvailable(xRivet)
    if u != None and v != None:
        valU, valV = u, v
    else:
        valU, valV = getUvOnSurfaceFromeTr(tr, surface, out)

    # if min:
    #     valV/=2
    #print valV,'***********---------------'
    # xrivetTrans = mc.createNode('transform', n = tr + 'Xrivet')
    mc.setAttr('{0}.xRivetDatas[{1}].uValue'.format(xRivet, indexLast), valU)
    mc.setAttr('{0}.xRivetDatas[{1}].vValue'.format(xRivet, indexLast), valV)
    mc.setAttr('{0}.xRivetDatas[{1}].mainDirection'.format(xRivet, indexLast), mainDirection)
    mc.setAttr('{0}.xRivetDatas[{1}].stretchSquash'.format(xRivet, indexLast), 0)

    # for attrFrom, attrTo in zip(attrsFrom, attrsTo):
    #     mc.connectAttr('{0}.outputTransforms[{1}].{2}'.format(xRivet, indexLast, attrFrom),
    #                    '{0}.{1}'.format(xrivetTrans, attrTo))


    # mc.parentConstraint(xrivetTrans, tr, mo = True)
    mc.connectAttr('{0}.outputTransforms[{1}].{2}'.format(xRivet, indexLast, 'outTranslation'),
                   '{0}.{1}'.format(tr, 'translate'))

    addRot = mc.createNode('animBlendNodeAdditiveRotation', n = tr + 'AdditiveRotation')
    mc.setAttr(addRot + '.accumulationMode', 1)
    mc.connectAttr('{0}.outputTransforms[{1}].{2}'.format(xRivet, indexLast, 'outRotation'),
                   '{0}.{1}'.format(addRot, 'inputA'))
    mc.setAttr(addRot + '.inputB', *offsetOrient)
    mc.connectAttr(addRot + '.output', tr + '.rotate')
    # mc.pointConstraint(xrivetTrans, tr, mo = True)
    # mc.orientConstraint(xrivetTrans, tr, mo = True)

    return xRivet, indexLast
#################################################################################################       
def getXrivetEntryAvailable(xrivet):
    """

    :param xrivet:
    :type xrivet:
    :return:
    :rtype:
    """
    norm = 17
    if mc.objectType(xrivet, i = 'xRivetNurbs'):
        norm = 8
    index = 0
    attrDatas = mc.listAttr(xrivet + '.xRivetDatas', m = True)
    if attrDatas:
        index = len(attrDatas) / norm
    return index
    
def getUvOnSurfaceFromeTr(tr, surface, out):
    '''

    :param tr:
    :type tr:
    :param surface:
    :type surface:
    :param out:
    :type out:
    :return:
    :rtype:
    '''
    closestTmp = mc.createNode('closestPointOnSurface', n = 'closestPointUVGetTmp')
    mc.connectAttr(surface + '.' + out, closestTmp + '.is')
    posi = mc.xform(tr, q = True, ws = True, t = True)
    mc.setAttr(closestTmp + '.ip', *posi)
    u, v = mc.getAttr(closestTmp + '.u'), mc.getAttr(closestTmp + '.v')
    mc.delete(closestTmp)
    #print '----------', v,'*******'
    return u, v
################################################################################################# 
def getOffsetFromXrivet(aim, upv):
    '''

    :param aim:
    :type aim:
    :param upv:
    :type upv:
    :return:
    :rtype:
    '''
    offset = [0, 0, 0]
    if aim == 'x':
        if upv == 'y':
            offset[0:1] = [90]
        if upv == '-y':
            offset[0:1] = [-90]
        if upv == '-z':
            offset[0:1] = [-180]

    if aim == '-x':
        offset[2:3] = [-180]
        if upv == 'y':
            offset[0:1] = [-90]
        if upv == '-y':
            offset[0:1] = [90]
        if upv == 'z':
            offset[0:1] = [-180]

    if aim == 'y':
        offset[2:3] = [-90]
        if upv == 'x':
            offset[1:2] = [-90]
        if upv == '-x':
            offset[1:2] = [90]
        if upv == '-z':
            offset[1:2] = [-180]

    if aim == '-y':
        offset[2:3] = [90]
        if upv == 'x':
            offset[1:2] = [-90]
        if upv == '-x':
            offset[1:2] = [90]
        if upv == '-z':
            offset[1:2] = [-180]

    if aim == 'z':
        offset = [90, 90, 90]
        if upv == 'x':
            offset[1:2] = [-90]
        if upv == 'y':
            offset[1:2] = [0]
        if upv == '-y':
            offset[1:2] = [-180]

    if aim == '-z':
        offset = [90, 90, -90]
        if upv == 'x':
            offset[1:2] = [-180]
        if upv == 'y':
            offset[1:2] = [0]
        if upv == '-y':
            offset[1:2] = [-180]
    return offset
 
# --- fkSection create def ############################################################
def createFKSection(baseName,ctrlName,offsetName,num,suff,doOffset,makeShape,color):
    #baseName:string
    #ctrlName:string    
    #offsetName:string
    #num:int
    #suffix:string
    #doOffset:bool
    #makeShape:bool
    #color: None or List [#,#,#]
    
    ctrlNodeName = '%s_%s_%02d%s' %(baseName,ctrlName,num,suff)
    offsetNodeName = '%s_%s_%s_%02d%s' %(baseName,offsetName,ctrlName,num,suff)
    mc.select(cl=True)
    newCtrl = mc.joint(n=ctrlNodeName)
    mc.setAttr('%s.radius' %newCtrl , 0.1 ) 
    if makeShape == True:
        mc.setAttr('%s.drawStyle' %newCtrl , 2 )
        shapes.create( newCtrl, shape= 'circle', size= .5, scale= [1, 1, 1 ], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= color, colorDegradeTo= None, replace= True, middle= False)
    newCtrlOrig = orig.orig(objlist=[newCtrl], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto') [0]  
    newCtrlOrig = mc.rename(newCtrlOrig, newCtrlOrig.replace('smart_orig','orig_smart') )
    if doOffset == True:
        mc.select(cl=True)
        newOffset = mc.joint(n=offsetNodeName)
        mc.setAttr('%s.radius' %newOffset , 0.1 )    
        if makeShape == True:
            mc.setAttr('%s.drawStyle' %newOffset , 2 )
            shapes.create( newOffset, shape= 'circle', size= .25, scale= [1, 1, 1 ], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= color, colorDegradeTo= None, replace= True, middle= False)
        newOffsetOrig = orig.orig(objlist=[newOffset], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')[0]
        newOffsetOrig = mc.rename(newOffsetOrig,newOffsetOrig.replace('smart_orig','orig_smart') )
        mc.parent(newOffsetOrig,newCtrl)
        return([newCtrl,newCtrlOrig],[newOffset,newOffsetOrig])
    return([newCtrl,newCtrlOrig])
       