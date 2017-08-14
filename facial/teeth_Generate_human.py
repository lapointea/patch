import maya.cmds as mc
import math
import marsCore.foundations.dagLib as dagLib
import marsCore.foundations.curveLib as curveLib
from marsAutoRig_stubby.patch.customLib import patchLib as patchLib
reload(patchLib)
import marsCore.foundations.skeletonLib as skelLib
import marsCore.orig as orig
import marsCore.shapes.defs as shapes
reload(shapes)

##########################################
def xrivetTrOnNurbs(tr, surface, mainDirection = 1, out = 'worldSpace[0]', u = None, v = None,offsetOrient = [0, 0, 0],min=False):
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
##########################################      
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
##########################################
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
##########################################    
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
##########################################
def createTeethCtrl(guide,visTransform,stack):
    visAttr = 'teethTweakVis'
    baseSkinSet = 'teeth_skin_set'
    skinSet = '%s_teeth_skin_set' %stack
    animSet = 'teeth_anim_set'
    if not mc.ls('%s.%s' %(visTransform,visAttr)):
        mc.addAttr( visTransform , ln = visAttr , at = 'bool' , dv = 0 )
        mc.setAttr('%s.%s' %(visTransform,visAttr) , edit = True , k = True )
    if not mc.objExists('skin_set'):
        mc.select(cl=True)
        mc.sets(n='skin_set')
    if not mc.objExists(baseSkinSet):
        mc.select(cl=True)
        mc.sets(n=baseSkinSet)
        mc.sets(baseSkinSet, add='skin_set') 
    if not mc.objExists(skinSet):
        mc.select(cl=True)
        mc.sets(n=skinSet)
        mc.sets(skinSet, add=baseSkinSet)

    if not mc.objExists('anim_set'):
        mc.select(cl=True)
        mc.sets(n='anim_set')
    if not mc.objExists(animSet):
        mc.select(cl=True)
        mc.sets(n=animSet)
        mc.sets(animSet, add='anim_set')
        
    mc.select(cl=True)
    newCtrl = mc.joint(n=guide.replace('GUIDE','ctrl'))
    mc.setAttr('%s.drawStyle' %newCtrl , 2 )
    mc.parent(newCtrl,guide,r=True)
    mc.parent(newCtrl,w=True)
    mc.sets(newCtrl,add=skinSet)
    mc.sets(newCtrl,add=animSet)    
    guideShapes = mc.listRelatives(guide,s=True)
    if guideShapes:
        for i,shape in enumerate(guideShapes):
            mc.parent( shape,newCtrl, s=True, r=True)
            newShapeName = mc.rename(shape, guide.replace('GUIDE','ctrlShape%d' %i))
            #connectShapesvis
            mc.connectAttr('%s.%s' %(visTransform,visAttr) , '%s.visibility' %newShapeName )
    newCtrl = mc.rename(newCtrl,guide.replace('GUIDE','ctrl'))
    newOrig = orig.orig(objlist=[newCtrl], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')[0]
    mc.disconnectAttr('%s.scale' %newOrig , '%s.inverseScale' %newCtrl )
    return(newCtrl,newOrig)
##########################################

def generateTeeth():
    stacks = ['up','dn']
    sides = ['L','R']

    baseName = 'teeth'
    MainGuideSuff = 'jnt_GUIDE'
    noXformGrp = 'teeth_noXformGrp'
    mouthCtrl = 'mouth_ctrl'
    gumsMesh = 'gum_hi'
    gumsMeshAlt = 'gums_hi'
    teethGuidesGrp = '%s_guides_grp' %baseName

    # --- creating noXformGrp for later use
    mc.group(n=noXformGrp, em=True)
    mc.parent(noXformGrp,'facial_fGrp')
    mc.hide(noXformGrp)

    # --- creating hold_jnt for further use
    mc.select(cl=True)
    holdJnt = mc.joint(n='%s_hold_jnt' %baseName)
    mc.parent(holdJnt,noXformGrp)

    for stack in stacks:
        mainTeethParent = '%s_%s_SKN' %(baseName,stack)
        mainBaseGuide = '%s_%s_%s' %(baseName,stack,MainGuideSuff)
        crvGuidesGrp = '%s_%s_guides_grp' %(baseName,stack)
        
        # --- get all teeth guides from template groups
        mainGuides = mc.listRelatives(mainBaseGuide,c=True , type='joint')  
           
        # --- tweak and realign jawGen generated controls
        allGuides = mainGuides
        mainGuides.append(mainBaseGuide)
        allOrient = []    
        for guide in allGuides:
            parent = mc.listRelatives(guide,p=True)[0]
            mc.parent(guide,w=True)
            RO = mc.getAttr('%s.rotate' %guide)[0]
            JO = mc.getAttr('%s.jointOrient' %guide)[0]
            orient = (RO[0]+JO[0],RO[1]+JO[1],RO[2]+JO[2])
            allOrient.append(orient)
            mc.parent(guide,parent)
            
        parentList = []    
        for g , guide in enumerate(allGuides):
            ctrl = guide.replace('GUIDE','orig') 
            parent = mc.listRelatives(ctrl,p=True)[0]
            parentList.append(parent)
            mc.parent(ctrl,w=True)
            mc.setAttr('%s.jointOrient' %ctrl , 0,0,0)
            mc.setAttr('%s.rotate' %ctrl , allOrient[g][0], allOrient[g][1], allOrient[g][2] )
            
        for g,guide in enumerate(reversed(allGuides)):
            ctrl = guide.replace('GUIDE','orig') 
            parent = parentList[-1-g]        
            mc.parent(ctrl,parent)
            if  g > 0:        
                mc.setAttr('%s.jointOrientX' %ctrl , 0)
                mc.setAttr('%s.jointOrientZ' %ctrl , 0)  
                mc.setAttr('%s.rotateX' %ctrl , 0)        
                mc.setAttr('%s.rotateZ' %ctrl , 0)

        ## --- create midCtrls symmetry
        midCtrls = []
        for g , guide in enumerate(allGuides):
            ctrl = guide.replace('GUIDE','orig')
            splitName = ctrl.rsplit('_',3)[1]
            if splitName == 'mid':
                midCtrls.append(ctrl)
                RCtrls = mc.duplicate(ctrl,n= ctrl.replace('L_','R_'))
                midCtrls.append(RCtrls[0])
                ### --- rename childs of dupilcated control
                RCtrlChilds = mc.listRelatives(RCtrls[0], ad=True, f=True)          
                for c, child in enumerate(RCtrlChilds):
                    if c>0:
                        strippedName = child.rsplit('|',1)[1]                    
                        newName = mc.rename(child, strippedName.replace('L_','R_')) 
                ### --- reconnect control to SKN of duplicated mid Ctrl
                renamedChilds = mc.listRelatives(RCtrls[0],ad=True)
                for  child in renamedChilds:            
                    splitName = child.rsplit('_',1)[1]
                    if splitName == 'ctrl':
                        if not mc.objectType(child) == 'nurbsCurve':
                            patchLib.smartcopyAttr(child,child.replace('_ctrl','_SKN'))     
                            patchLib.smartConnect(child,child.replace('_ctrl','_SKN'))                          
                ### --- position RCtrl on symmetry
                #print ctrl
                mc.setAttr('%s.translateX' %RCtrls[0] ,  -(mc.getAttr('%s.translateX' %ctrl)) )
                mc.setAttr('%s.scaleX' %RCtrls[0] ,  -1 )
        ## --- create new parent placed at origin for midCtrls
        midParent = mc.group(n='%s_%s_mids_orig' %(stack,baseName) , em=True)
        mc.parent(midParent,mainTeethParent)
        mc.parent(midCtrls,midParent)
        
        # --- create world rigs from jawGen generated controls
        ## --- get all the objects that need a world duplicate
        mainTeethChilds = mc.listRelatives(mainTeethParent , c=True, ad=True, s=False)
        worldTargets = []
        for child in mainTeethChilds:
            if not mc.objectType(child) == 'nurbsCurve':
                worldTargets.append(child)
        ## --- create duplicated world objects and connects them to the actual controls
        ### --- create duplicate for main node
        worldParent = mc.duplicate(mainTeethParent, po=True, n= '%s_world' %mainTeethParent)[0]
        mc.parent(worldParent, noXformGrp)
        ### --- create duplicates for every childNode of main node. Connect local Rig to world Rig
        worldParentdict = dict()
        worldNodes = []
        for target in worldTargets:    
            splitName = target.split('_')
            parent = mc.listRelatives(target,p=True)[0]
            
            if not 'ctrl' in splitName:
                if not splitName[0] == 'C':
                    #### --- create world node
                    worldNode = mc.duplicate(target,po=True,n='%s_world' %target)[0]
                    mc.parent(worldNode,noXformGrp)
                    worldNodes.append(worldNode)
                    worldParentdict[worldNode] = (parent)
                    #### --- do the conection   
                    if not 'mid' in splitName:
                        if not 'mids' in splitName:
                            patchLib.smartcopyAttr(target,worldNode)  
                            patchLib.smartConnect(target,worldNode)  
                        elif 'mids' in splitName:
                            pass
                    elif 'mid' in splitName:
                        if not 'orig' in splitName:
                            patchLib.smartcopyAttr(target,worldNode)
                            patchLib.smartConnect(target,worldNode)
                        else :
                            ROCon = mc.listConnections('%s.rotateOrder' %target , s=True,p=True)
                            if ROCon:
                                mc.disconnectAttr(ROCon[0],'%s.rotateOrder' %target)
                            patchLib.smartcopyAttr(worldNode,target)
                            patchLib.smartConnect(worldNode,target)
                                
                elif splitName[0] == 'C':
                    #### --- create world node
                    LWorldNode = mc.duplicate(target,po=True,n='L%s_world' %target)[0]
                    RWorldNode = mc.duplicate(target,po=True,n='R%s_world' %target)[0]
                    mc.parent(LWorldNode,RWorldNode,noXformGrp)  
                    worldNodes.append(LWorldNode)     
                    worldNodes.append(RWorldNode)
                    
                    parentSplit = parent.split('_',1)[0]
                    if not parentSplit == 'C':
                        worldParentdict[LWorldNode] = (parent)
                        worldParentdict[RWorldNode] = (parent)
                    elif parentSplit == 'C':            
                        worldParentdict[LWorldNode] = ('L%s' %parent)
                        worldParentdict[RWorldNode] = ('R%s' %parent)
                    #### --- do the conection   
                    patchLib.smartcopyAttr(target,LWorldNode)  
                    patchLib.smartcopyAttr(target,RWorldNode)
                    patchLib.smartConnect(target,LWorldNode)  
                    patchLib.smartConnect(target,RWorldNode)

        ### --- reparent world nodes to recreate local hierarchy
        for node in worldNodes :
            localParent = worldParentdict.get(node)           
            mc.parent(node, '%s_world' %localParent)

        # --- get all curve teeth guides from template groups
        allCrvGuides = mc.listRelatives(crvGuidesGrp , c=True )

        ## --- separate the loft guides from the rest
        popIndex = 0
        crvLoftGuide = ''
        for g , guide in enumerate(allCrvGuides):
            splitName = guide.rsplit('_crv_')[-1]
            if splitName == 'GUIDE':
                popIndex = g
                crvLoftGuide = allCrvGuides.pop(g)  
        
        # --- lofts from curves and symmetrise them to create n0 surfaces
        ## --- create left loft curves
        LdnCrv = mc.duplicate(crvLoftGuide, n=crvLoftGuide.replace('GUIDE','Loft_00'))[0]
        LupCrv = mc.duplicate(crvLoftGuide, n=crvLoftGuide.replace('GUIDE','Loft_01'))[0]    
        patchLib.locksSwitch(LdnCrv,T=True,R=True,S=True,V=True,lockdo='unlock',keydo=True)
        patchLib.locksSwitch(LupCrv,T=True,R=True,S=True,V=True,lockdo='unlock',keydo=True)     
        mc.parent(LdnCrv,LupCrv,mainTeethParent)
        mc.makeIdentity(LdnCrv,a=True) 
        mc.makeIdentity(LupCrv,a=True)
        mc.makeIdentity(LdnCrv,a=False) 
        mc.makeIdentity(LupCrv,a=False)
        offsetVal = 0.01
        mc.setAttr('%s.translateY' %LdnCrv , (-offsetVal) )
        mc.setAttr('%s.translateY' %LupCrv , offsetVal )
        mc.parent(LdnCrv,LupCrv,w=True)
        mc.makeIdentity(LdnCrv,a=True) 
        mc.makeIdentity(LupCrv,a=True)
        mc.makeIdentity(LdnCrv,a=False) 
        mc.makeIdentity(LupCrv,a=False)
        ## --- create right loft curves
        RdnCrv = mc.duplicate(LdnCrv, n=LdnCrv.replace('L_','R_'))[0]
        RupCrv = mc.duplicate(LupCrv, n=LupCrv.replace('L_','R_'))[0]
        mc.setAttr('%s.scaleX' %RdnCrv , -1 )
        mc.setAttr('%s.scaleX' %RupCrv , -1 )
        mc.makeIdentity(RdnCrv,a=True)
        mc.makeIdentity(RupCrv,a=True)
        mc.makeIdentity(RdnCrv,a=False)
        mc.makeIdentity(RupCrv,a=False)
        ## --- create loft surfaces
        LLoftSurf = mc.loft(LdnCrv,LupCrv, n='L_%s_%s_surf_n0' %(stack,baseName) ,ch=False)[0]
        RLoftSurf = mc.loft(RdnCrv,RupCrv, n='R_%s_%s_surf_n0' %(stack,baseName) ,ch=False)[0]
        loftSurfsN0 = [LLoftSurf,RLoftSurf]    
        loftSurfsN1 = mc.duplicate(loftSurfsN0)
        loftSurfsN2 = mc.duplicate(loftSurfsN0)
        loftSurfsAll = [loftSurfsN0,loftSurfsN1,loftSurfsN2]
        mc.delete(LdnCrv,LupCrv,RdnCrv,RupCrv)
        mc.parent(loftSurfsAll[0],loftSurfsAll[1],loftSurfsAll[2],noXformGrp)
     
        ## --- disconnect unwanted ctrl to joints connections
        for target in worldNodes:  
            splitName = target.split('_')
            if not 'gumsBase' in splitName:
                if 'SKN' in splitName:
                    scaleCons = mc.listConnections('%s.scale' %target , s=True,p=True)
                    if scaleCons:
                        for con in scaleCons:
                            mc.disconnectAttr(con ,'%s.scale' %target )
                            if 'mid' in splitName:
                                mc.connectAttr('%sX' %con,'%s.scaleX' %target)
                            if not 'mid' in splitName:
                                if 'LC' in splitName or 'RC' in splitName:
                                    mc.connectAttr('%sX' %con,'%s.scaleX' %target )                    
                                if 'L'in splitName or 'R' in splitName:
                                    mc.connectAttr('%sZ' %con,'%s.scaleZ' %target )

        ## --- symmetrise teeth guides and creates final teeth hierarchy
        LCtrlList = []
        RCtrlList = []
        ctrlLists = [LCtrlList,RCtrlList]
        for guide in allCrvGuides:
            guideChild = mc.listRelatives(guide, c=True, type = 'transform')[0]
            mainCtrl = createTeethCtrl(guide,mouthCtrl,stack)
            tipCtrl = createTeethCtrl(guideChild,mouthCtrl,stack)
            mc.parent(tipCtrl[1],mainCtrl[0])
            mc.parent(mainCtrl[1], '%s_%s_SKN_world' %(baseName,stack))
            skelLib.jointOrientToRotate(mainCtrl[1])             
            LCtrlList.append(mainCtrl[1])
            
            splitName = guide.split('ibt_01')
            if not len(splitName) > 1:
                getTx = mc.getAttr('%s.translateX' %mainCtrl[1])
                getRy = mc.getAttr('%s.rotateY' %mainCtrl[1])
                symOrig = mc.duplicate(mainCtrl[1] ,ic=True, n = mainCtrl[1].replace('L_','R_'))[0]
                skelLib.jointOrientToRotate(symOrig)   
                mc.setAttr('%s.translateX' %symOrig , -getTx)
                mc.setAttr('%s.rotateY' %symOrig , -getRy)
                symChilds = mc.listRelatives(symOrig,c=True,ad=True,f=True)
                for child in symChilds:
                    splitName = child.rsplit('|',1)[1]
                    mc.rename(child,splitName.replace('L_','R_'))
                RCtrlList.append(symOrig)
        teethGroup = '%s_%s_allCtrls_orig' %(baseName,stack)
        mc.group(n=teethGroup,em=True)
        mc.parent(teethGroup,mainTeethParent)
        mc.parent(LCtrlList,RCtrlList,teethGroup)
        
        ## --- generating surfaces deformers and connections  
        for s, side in enumerate(sides):
            ## --- weighting n0 surface
            n0SKC = mc.skinCluster('%sC_%s_%s_SKN_world' %(side,baseName,stack) , '%s_%s_%s_SKN_world' %(side,baseName,stack) , loftSurfsN0[s], n='%s_SKC' %loftSurfsN0[s] , mi = 2 , tsb=True)[0]
            ### --- create skinWeights anime Curve and reskin Surf from that curve
            skinCurveDef = {'tangentsVal': [0.0, 47.702933224999114, 53.989547386085576, 55.545989790698755], 'keyCount': 4, 'keysValues': [0.0, 0.1322238293848932, 0.6123709362161491, 1.0], 'keysAtFrame': [0.0, 0.404, 0.696, 1.0]}
            skinCurve = patchLib.createAnimCurveFromDef(skinCurveDef,'temp_teeth_skinCurve')
            
            ## --- weighting n1 surfaces and connect n0 outShape to n1 orig
            n1SKC = mc.skinCluster('%s_%s_%s_mid_SKN_world' %(side,baseName,stack), holdJnt , loftSurfsN1[s], n='%s_SKC' %loftSurfsN1[s] , mi = 2 , dr = 2 ,tsb=True)[0]
            patchLib.sineWeightsOnSurf(loftSurfsN1[s],'u',False)
            patchLib.basicBPMOnNurbs(SKC=n1SKC, holdJnt=holdJnt)
            n0OutShape = mc.listConnections('%s.outputGeometry' %n0SKC , sh=True)[0]
            n1ShapeOrig = dagLib.findShapeOrig(loftSurfsN1[s])
            mc.connectAttr('%s.worldSpace[0]' %n0OutShape , '%s.create' %n1ShapeOrig)
            ## --- attache midCtrls to surf n0 with XRivet
            for node in worldNodes:
                splitName = node.split('_')
                if side in splitName:
                    if stack in splitName:
                        if 'mid' in splitName:
                            if 'orig' in splitName:
                                if side == 'L':
                                    offset = getOffsetFromXrivet('x', 'y')
                                elif side == 'R':
                                    offset = getOffsetFromXrivet('-x', '-y')
                                mc.setAttr('%s.rotateOrder' %node , 0 )
                                mc.setAttr('%s.jointOrient' %node , 0,0,0 )
                                midXrivet = xrivetTrOnNurbs(node, loftSurfsN0[s], mainDirection = 1, out = 'worldSpace[0]', u = None, v = None,offsetOrient = offset ,min=False)
                                #print '%s is beeing xrivetted !!! ' %node
            ## --- create node based final n2 surfaces
            ### --- extract new curves from isoParms
            dnCfsi = mc.createNode('curveFromSurfaceIso' , n ='%s_dn_cfsi' %loftSurfsN1[s])
            upCfsi = mc.createNode('curveFromSurfaceIso' , n ='%s_up_cfsi' %loftSurfsN1[s])
            mc.setAttr('%s.isoparmDirection' %dnCfsi , 1 )
            mc.setAttr('%s.isoparmDirection' %upCfsi , 1 )
            mc.setAttr('%s.isoparmValue' %dnCfsi , 0 )
            mc.setAttr('%s.isoparmValue' %upCfsi , 1 )
            mc.connectAttr('%s.worldSpace[0]' %loftSurfsN1[s], '%s.inputSurface' %dnCfsi )
            mc.connectAttr('%s.worldSpace[0]' %loftSurfsN1[s], '%s.inputSurface' %upCfsi )
            ### --- create sliding from rebuild on curves
            dnRc = mc.createNode('rebuildCurve' , n ='%s_dn_rc' %loftSurfsN1[s])
            upRc = mc.createNode('rebuildCurve' , n ='%s_up_rc' %loftSurfsN1[s])
            surfSpans = mc.getAttr('%s.spansV' %loftSurfsN1[s])
            mc.setAttr('%s.spans' %dnRc , surfSpans)
            mc.setAttr('%s.spans' %upRc , surfSpans)
            mc.connectAttr('%s.outputCurve' %dnCfsi , '%s.inputCurve' %dnRc )
            mc.connectAttr('%s.outputCurve' %upCfsi , '%s.inputCurve' %upRc )
            ### --- create finalLoft and connect to surf n2
            loft = mc.createNode('loft' , n= '%s_loft' %loftSurfsN2[s] )
            mc.setAttr('%s.uniform' %loft , 1 )
            mc.connectAttr('%s.outputCurve' %dnRc , '%s.inputCurve[0]' %loft )
            mc.connectAttr('%s.outputCurve' %upRc , '%s.inputCurve[1]' %loft )
            mc.connectAttr('%s.outputSurface' %loft , '%s.create' %loftSurfsN2[s] )
                        
            ## --- attach teeth on n2 surface
            for control in ctrlLists[s]:
                endXrivet = xrivetTrOnNurbs(control, loftSurfsN2[s], mainDirection = 1, out = 'worldSpace[0]', u = None, v = None,offsetOrient = offset ,min=False)
                mc.setAttr('%s.jointOrient' % control, 0,0,0)
            
            ## --- connect teeth ctrl joits to teeth scales
            endsCtrls = ['C_%s_%s_ctrl' %(baseName,stack),'%s_%s_%s_ctrl' %(side,baseName,stack)]
            midCtrl = '%s_%s_%s_mid_ctrl' %(side,baseName,stack)

            for i, each in enumerate(ctrlLists[s]) :
                
                # getting position percentage from position on surface
                ## getVpos from joints, it will be used in the 'curveFromSurfaceUV' node
                surfShape = dagLib.getFirstShape(loftSurfsN2[s])
                cpos = mc.createNode('closestPointOnSurface' , n='temp_cpos' )
                mc.connectAttr('%s.worldSpace[0]' %surfShape , '%s.inputSurface' %cpos)
                pointPos = mc.xform(each, q=True, ws=True, t=True)
                mc.setAttr('%s.inPosition' %cpos , pointPos[0],pointPos[1],pointPos[2] )
                paramV = mc.getAttr('%s.parameterV' %cpos)
                mc.delete(cpos)
                ## creates curve from node and get position percentage of joint from it
                tempCrv = mc.curve(d=3 , p=[(0,0,0),(1,1,1),(2,2,2),(3,3,3)] )
                tempCfsi = mc.createNode('curveFromSurfaceIso' , n = 'temp_cfsi' )
                mc.setAttr('%s.isoparmValue' %tempCfsi , paramV )
                mc.setAttr('%s.isoparmDirection' %tempCfsi , 1)
                mc.connectAttr( '%s.worldSpace[0]' %surfShape, '%s.inputSurface' %tempCfsi )
                mc.connectAttr('%s.outputCurve' %tempCfsi, '%s.create' %tempCrv )
                paramOnCrv = curveLib.getClosestPointOnCurve(tempCrv, pointPos, space='world')[1]
                percent = curveLib.findPercentFromParam(tempCrv, paramOnCrv)
                mc.delete(tempCfsi,tempCrv)
                #print '%s is %s percent' %(each,percent)
              
                # get soft fallof from percent and sine function
                sideSine = ((math.sin((percent*math.pi)-(math.pi/2)))+1)/2
                midSine = math.sin(percent*math.pi)    
                #print '%s is %s sideSine' %(each,sideSine)
                
                PMA = mc.createNode('plusMinusAverage' , n= '%s_scale_pma' %each )
                centerPMA = mc.createNode('plusMinusAverage' , n= '%s_scale_center_pma' %each )    
                sidePMA = mc.createNode('plusMinusAverage' , n= '%s_scale_center_side_pma' %each )     
                midPMA = mc.createNode('plusMinusAverage' , n= '%s_scale_center_mid_pma' %each )
                mc.setAttr('%s.operation' %centerPMA , 2)
                mc.setAttr('%s.input3D[1]' %centerPMA , 1,1,1)
                mc.setAttr('%s.operation' %sidePMA , 2)
                mc.setAttr('%s.input3D[1]' %sidePMA , 1,1,1)    
                mc.setAttr('%s.operation' %midPMA , 2)
                mc.setAttr('%s.input3D[1]' %midPMA , 1,1,1)
                mc.connectAttr('%s.scale' %endsCtrls[0] , '%s.input3D[0]' %centerPMA )
                mc.connectAttr('%s.scale' %endsCtrls[1] , '%s.input3D[0]' %sidePMA )
                mc.connectAttr('%s.scale' %midCtrl , '%s.input3D[0]' %midPMA )  
                    
                centerMD = mc.createNode('multiplyDivide', n = '%s_center_scale_MD' %each)
                sideMD = mc.createNode('multiplyDivide', n = '%s_side_scale_MD' %each)    
                midMD = mc.createNode('multiplyDivide', n = '%s_mid_scale_MD' %each)
                
                mc.connectAttr('%s.output3D' %centerPMA , '%s.input1' %centerMD )
                mc.connectAttr('%s.output3D' %sidePMA , '%s.input1' %sideMD )
                mc.connectAttr('%s.output3D' %midPMA , '%s.input1' %midMD ) 
                
                mc.setAttr( '%s.input2' %centerMD ,1-sideSine ,1-sideSine ,1-sideSine )
                mc.setAttr( '%s.input2' %sideMD ,sideSine ,sideSine ,sideSine )
                mc.setAttr( '%s.input2' %midMD ,midSine ,midSine ,midSine )
                
                mc.setAttr('%s.input2D[0]' %PMA , 1 , 1 )
                
                mc.connectAttr('%s.outputZ' %centerMD, '%s.input2D[1].input2Dx' %PMA )
                mc.connectAttr('%s.outputY' %centerMD, '%s.input2D[1].input2Dy' %PMA )
                
                mc.connectAttr('%s.outputX' %sideMD, '%s.input2D[2].input2Dx' %PMA )
                mc.connectAttr('%s.outputY' %sideMD, '%s.input2D[2].input2Dy' %PMA )
                
                mc.connectAttr('%s.outputZ' %midMD, '%s.input2D[3].input2Dx' %PMA )
                mc.connectAttr('%s.outputY' %midMD, '%s.input2D[3].input2Dy' %PMA )    
                        
                mc.connectAttr('%s.output2Dx' %PMA , '%s.scaleZ' %each )
                mc.connectAttr('%s.output2Dy' %PMA , '%s.scaleY' %each ) 
            
           
        # --- add bpm cluster to top and bottom teeth
        for ctrl in worldTargets :
            splitName = ctrl.split('_')
            if 'gumsBase' in splitName:
                if 'SKN' in splitName:
                    parent = mc.listRelatives(ctrl,p=True)[0]
                    mc.select(cl=True)
                    newClstr = mc.cluster(n='%s_%s_cluster' %(splitName[0],splitName[1]) , bs=True, wn=(ctrl,ctrl) )[0]
                    mc.connectAttr('%s.parentInverseMatrix[0]' %ctrl , '%s.bindPreMatrix' %newClstr )
                    
                    if mc.objExists(gumsMesh):
                        clstrSet = mc.listConnections( newClstr, type="objectSet" )[0]
                        mc.sets( gumsMesh, add=clstrSet )                        
                    elif mc.objExists(gumsMeshAlt):
                        clstrSet = mc.listConnections( newClstr, type="objectSet" )[0]
                        mc.sets( gumsMeshAlt, add=clstrSet )

        # --- tweak shapes and colors of base ctrls
        for ctrl in worldTargets :
            splitName = ctrl.split('_')
            if 'gumsBase' in splitName:
                if 'ctrl' in splitName:
                    shapes.create( ctrl, shape= 'circleLowHalf', size= 0.2, scale= [1, 1, 1 ], axis= 'y', twist= 90, offset= [0, 0, -0.06 ], color= [1,0,0] , colorDegradeTo= None, replace= True, middle= False)
            if 'L' in splitName:
                if 'ctrl' in splitName:
                    if not 'mid' in splitName:
                        shapes.create( ctrl, shape= 'pyramid', size= 0.15, scale= [1, 1, 1 ], axis= 'x', twist= 0, offset= [0.05, 0, 0 ], color= [0,0,1] , colorDegradeTo= None, replace= True, middle= False)
                    if 'mid' in splitName:
                        shapes.create( ctrl, shape= 'pyramid', size= 0.1, scale= [1, 1, 1 ], axis= 'z', twist= 0, offset= [0, 0, 0.05 ], color= [0.5,0.5,1] , colorDegradeTo= None, replace= True, middle= False)
            if 'R' in splitName:
                if 'ctrl' in splitName:
                    if not 'mid' in splitName:
                        shapes.create( ctrl, shape= 'pyramid', size= 0.15, scale= [1, 1, 1 ], axis= '-x', twist= 0, offset= [-0.05, 0, 0 ], color= [1,0,0] , colorDegradeTo= None, replace= True, middle= False)
                    if 'mid' in splitName:
                        shapes.create( ctrl, shape= 'pyramid', size= 0.1, scale= [1, 1, 1 ], axis= 'z', twist= 0, offset= [0, 0, 0.05 ], color= [1,0.5,0.5] , colorDegradeTo= None, replace= True, middle= False)
            if 'C' in splitName:
                if 'ctrl' in splitName:
                    shapes.create( ctrl, shape= 'pyramid', size= 0.15, scale= [1, 1, 1 ], axis= 'z', twist= 0, offset= [0, 0, 0.05 ], color= [1,1,0] , colorDegradeTo= None, replace= True, middle= False)
                       
        # --- cleanup , sets and stuff
        trashNodes = mc.ls('transform?' , type = 'transform')
        mc.delete(trashNodes)
    mc.parent(teethGuidesGrp,'head_%s' %MainGuideSuff )
    addToSetList = ['L_teeth_up_ctrl','R_teeth_up_ctrl','C_teeth_up_ctrl','L_teeth_dn_ctrl','R_teeth_dn_ctrl','C_teeth_dn_ctrl','gumsBase_up_ctrl',
                    'gumsBase_dn_ctrl','L_teeth_up_mid_ctrl','L_teeth_dn_mid_ctrl','R_teeth_up_mid_ctrl','R_teeth_dn_mid_ctrl']
    if mc.objExists('anim_set'):
        mc.sets(addToSetList,add='anim_set')


