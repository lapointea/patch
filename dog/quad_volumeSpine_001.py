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

def makeSpine():

    ### --- importList
    #defList_quad_volumeSpine
    ### --- importList
    ######################################################################################################################################################################################
    ######################################################################################################################################################################################
    #TEMP DEF MERGE#######################################################################################################################################################################
    ######################################################################################################################################################################################
    ######################################################################################################################################################################################

    ##################################################################################################################################################################################################
    #def patchLib.resetTransform(trgt):
    #def patchLib.locksSwitch(sel,T=True,R=True,S=True,V=True,lockdo='unlock',keydo=False)
    #def patchLib.getRelatives(side,ctrlBase,digit)
    #orig.orig(objlist=[], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')
    #shapes.create( sel, shape= 'circle', size= 1, scale= [1, 1, 1 ], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= None, colorDegradeTo= None, replace= True, middle= False)
    ##################################################################################################################################################################################################
    #smartConnect(trgt,smart)
    #makeMidSmartJoints(targetList,rigRoot,rigLvl,rigPart,noXformGrp,smartJointsGrp,smartParent)
    #assignMidSmartToSurf(smartList,centerMidSurf,True,centerEndSurf)
    ##################################################################################################################################################################################################
    #linearWeightsOnSurf(surf,dir,reverseInf)
    #sineWeightsOnSurf(surf,dir,reverseInf)
    ##################################################################################################################################################################################################
    #xrivetTrOnNurbs(tr, surface, mainDirection = 1, out = 'worldSpace[0]', u = None, v = None,offsetOrient = [0, 0, 0],min=False)
    #getXrivetEntryAvailable(xrivet)
    #getOffsetFromXrivet(aim, upv)
    ##################################################################################################################################################################################################
    #addTanMidCtrls(mainMidCtrl,parentBase,parentTip)
    #createAnimCurveFromDef(curveDef,curveNodeName)
    #convertIkMidToThreeMid(surf,dir,holdJnt,newJoints)

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
    def makeMidSmartJoints(targetList,rigRoot,rigLvl,rigPart,noXformGrp,smartJointsGrp,smartParent):
        smartJoints = []

        for target in targetList:
            smartNoXformGrp = '%s_%s' %(rigPart,noXformGrp)
            if not mc.objExists(smartNoXformGrp):
                mc.group(n=smartNoXformGrp,em=True)   
            
            targetParent = mc.listRelatives(target,p=True)[0]
            
            mc.select(cl=True)
            smartJoint = mc.joint(n='%s_%sSmart' %(target,rigLvl))
            mc.setAttr('%s.radius' %smartJoint,0.1)
            smartConnect(target,smartJoint)
            
            mc.select(cl=True)    
            smartOrigJoint = mc.joint(n='%s_%sSmart' %(targetParent,rigLvl))
            mc.setAttr('%s.radius' %smartOrigJoint,0.1)
            mc.setAttr('%s.drawStyle' %smartOrigJoint,2)    
            smartConnect(targetParent,smartOrigJoint)
            
            mc.parent(smartJoint,smartOrigJoint)
            if smartParent:
                mc.parent(smartOrigJoint,smartParent)
            else :
                rigRootSmart = n='%s_%s%s' %(rigRoot,rigLvl,smartJointsGrp)
                if not mc.objExists(rigRootSmart):
                    mc.group(n=rigRootSmart , em=True )
                    mc.parent(rigRootSmart,rigRoot)
                    patchLib.resetTransform(rigRootSmart)
                    mc.parent(rigRootSmart,smartNoXformGrp)
                mc.parent(smartOrigJoint,rigRootSmart)
            smartJoints.append(smartJoint)
        return smartJoints
    #################################################################################################
    def assignMidSmartToSurf(smartList,surf,conToNext,nextSurf):
        SKC = mc.skinCluster(smartList,centerMidSurf,tsb=True)[0]
        linearWeightsOnSurf(surf,'v',False)    
        if conToNext == True :
            SKCTemp = mc.skinCluster(smartList,nextSurf,tsb=True)
            mc.delete(SKCTemp)
            orig = mc.listConnections('%s.create' %nextSurf , sh=True)[0]
            mc.connectAttr('%s.outputGeometry[0]' %SKC , '%s.create' %orig)        
    #################################################################################################
    def linearWeightsOnSurf(surf,dir,reverseInf):
        # changes weights on a surfaces with 2 influences tu get a linear weighting
        #surf = 'nurbsPlane1'
        #dir = 'u'
        #reverseInf = False
        
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
    #################################################################################################
    def sineWeightsOnSurf(surf,dir,reverseInf):
        # changes weights on a surfaces with 2 influences tu get a linear weighting
        #surf = 'nurbsPlane1'
        #dir = 'u'
        #reverseInf = False
        
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
        
    # --- add tangent controls to midLayer################################################################################################################
    def addTanMidCtrls(mainMidCtrl,parentBase,parentTip):
        #mainMidCtrl = 'spine_mid'
        #parentBase = 'spine_base'
        #parentTip = 'spine_tip_adjust'
        baseMid = '%s_Tan_ctrl' %parentBase
        tipMid = '%s_Tan_ctrl'%parentTip

        newMidsList = [baseMid,tipMid]
        parentsList = [parentBase,parentTip]

        newCtrlsList = []

        #creates new mid Ctrls and smart ctrls, parent them and connect ctrls to smartCtrls. Then places them at 1/4 of the distance parent - midCtrl
        for i , newMid in enumerate(newMidsList):
            newMidList = []
            
            #creates the new transforms
            mc.select(cl=True)
            midCtrl = mc.joint(n = newMid)
            mc.select(cl=True)
            smartMidCtrl = mc.joint(n = '%s_spinesurfNurbsSmart' % newMid)
            
            newMidList.append(midCtrl)
            newMidList.append(smartMidCtrl)    
            newCtrlsList.append(newMidList)
            
            mc.setAttr('%s.drawStyle' %midCtrl ,2)
            mc.setAttr('%s.radius' %midCtrl ,0.2)
            mc.setAttr('%s.drawStyle' %smartMidCtrl ,1)    
            mc.setAttr('%s.radius' %smartMidCtrl ,0.2)    
            shapes.create( midCtrl, shape= 'pinPyramid', size= 1, scale= [1, 1, 1 ], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= [255,255,0], colorDegradeTo= None, replace= True, middle= False)
            newOrigs = orig.orig(objlist=[midCtrl,smartMidCtrl], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')    
            #parent new controls in existing hierarchy
            mc.parent(newOrigs[0],parentsList[i] , r=True)
            mc.parent(newOrigs[1],'%s_spinesurfNurbsSmart' %parentsList[i] , r=True) 
            #connects ctrls to smart Ctrls
            transformList = ['translate','rotate','scale','rotateOrder']
            for transform in transformList:
                mc.connectAttr('%s.%s' %(midCtrl,transform) , '%s.%s' %(smartMidCtrl,transform) , f=True)
                mc.connectAttr('%s.%s' %(newOrigs[0],transform) , '%s.%s' %(newOrigs[1],transform) , f=True)
            #places ctrls at 1/4 of the distance parent - midCtrl
            ctrlWrldPos = mc.xform(midCtrl , ws=True, t=True, q=True)
            mainMidWrldPos = mc.xform(mainMidCtrl , ws=True, t=True, q=True)
            toCenterVector = [(mainMidWrldPos[0]-ctrlWrldPos[0]),(mainMidWrldPos[1]-ctrlWrldPos[1]),(mainMidWrldPos[2]-ctrlWrldPos[2])]
            newCtrlOffset = [toCenterVector[0]/4,toCenterVector[1]/4,toCenterVector[2]/4]
            mc.setAttr('%s.translate' %newOrigs[0], newCtrlOffset[0],newCtrlOffset[1],newCtrlOffset[2])

        return newCtrlsList       
    # --- add tangent controls to midLayer################################################################################################################
                
    # --- create AnimeCurve from def#######################################################################################################################            
    def createAnimCurveFromDef(curveDef,curveNodeName):
        #give dictionary definition of curve to function to recreate the animeCurve
        
        #dict() # curveDef = {'tangentsVal': [0.0, 0.0, 56.329492519973265, 60.702413199576945], 'keyCount': 4, 'keysValues': [0.0, 0.0, 0.1531658647581936, 1.0], 'keysAtFrame': [0.0, 0.276, 0.5, 1.0]}
        #string # curveNodeName = 'testAnimCurve'

        animCurve = mc.createNode('animCurveTU' , n = curveNodeName )
        for i in range(0,curveDef['keyCount']):
            mc.setKeyframe( curveNodeName , t = curveDef['keysAtFrame'][i] , v = curveDef['keysValues'][i] , itt = 'auto' , ott = 'auto' )
            mc.keyTangent( curveNodeName , edit = True , index = (i,i) , inAngle = curveDef['tangentsVal'][i] , outAngle = curveDef['tangentsVal'][i])
        
        return curveNodeName
    # --- create AnimeCurve from def####################################################################################################################### 

    # --- convert IK mid weights to trhee mids weights##################################################################################################### 
    def convertIkMidToThreeMid(surf,dir,holdJnt,newJoints):

        #surf = 'spinesurfNurbs'
        #dir = 'u'
        newJntsCount = 2
        #reverseInf = False
        #holdJnt = 'spinesurfNurbsRestSmart'
        #newJoints = ['thirdMidJoint_01','thirdMidJoint_02']
        curveDef = {'tangentsVal': [77.5, 0.0, 0.0], 'keyCount': 3, 'keysValues': [0.0, 1.0, 1.0], 'keysAtFrame': [0.0, 0.5, 1.0]}   
        animeCurve = createAnimCurveFromDef(curveDef,'tempWeightCurve')

        # --- get surface skinCluster and infs
        surfShape = dag.getFirstShape(surf)
        surfdegree = mc.getAttr('%s.degree%s' %(surfShape,dir.upper()))
        surfSpans = mc.getAttr('%s.spans%s' %(surfShape,dir.upper()))
        surfCvRows = surfdegree+surfSpans
        surfSKN = mc.listConnections('%s.create' % surfShape , s = True )[0]
        if mc.objectType(surfSKN) == 'skinCluster' :
            surfSknInfs = mc.skinPercent(surfSKN , '%s.cv[*][*]' % surf , q = True , t = None)   
            if not len(surfSknInfs) == 2 :
                print 'only works with 2 influencies'
            
            else:
                # --- adds new joints into skinCluster and connects its bpm
                mc.skinCluster( surfSKN , e=True,wt = 0.0, ai = newJoints ) 
                for joint in newJoints:
                    jointOrig = mc.listRelatives(joint,p=True)[0]
                    skinPlugs = mc.listConnections('%s.matrix' %surfSKN , c=True )
                    newInfs = []
                    infsPlugs = []
                    for plug in skinPlugs:
                        nameCut = plug.split('.')
                        if len(nameCut) == 2:
                            infsPlugs.append(plug)
                        elif len(nameCut) == 1:
                            newInfs.append(plug)
                    for k , inf in enumerate(newInfs):
                        if inf == joint:
                            plugNumber = infsPlugs[k].rsplit('matrix',)[1]
                            mc.connectAttr('%s.worldInverseMatrix[0]' % jointOrig , '%s.bindPreMatrix%s' %(surfSKN,plugNumber))
            
            
                    
                
                # --- creates frameCacheNode for linear convert
                convertFC = mc.createNode('frameCache' , n = 'tempConvert_fc' )
                mc.connectAttr('%s.output' % animeCurve , '%s.stream' % convertFC , f = True ) 
                 
                # --- create halfSurfaces adn halfCurves

                surfSpan = mc.getAttr('%s.spans%s' %(surf,dir.upper()))
                subSurfNode1 = mc.createNode('subSurface' , n = 'TEMP_subSurfNode_01' )
                subSurfNode2 = mc.createNode('subSurface' , n = 'TEMP_subSurfNode_02' )
                curveFromIsoNode1 = mc.createNode('curveFromSurfaceIso' , n = 'TEMP_curveFromSurfaceIso_01' )
                curveFromIsoNode2 = mc.createNode('curveFromSurfaceIso' , n = 'TEMP_curveFromSurfaceIso_02' )
                rebuildNode1 = mc.createNode('rebuildCurve' , n = 'TEMP_rebuildCurve_01' )
                rebuildNode2 = mc.createNode('rebuildCurve' , n = 'TEMP_rebuildCurve_02' )
                curveNode1 = mc.createNode('nurbsCurve', n = 'TEMP_nurbsCurve_01' )
                curveNode2 = mc.createNode('nurbsCurve', n = 'TEMP_nurbsCurve_02' )

                surfNodes = [subSurfNode1,subSurfNode2]
                curveFromIsoNodes = [curveFromIsoNode1,curveFromIsoNode2]
                rebuildNodes = [rebuildNode1,rebuildNode2]
                halfCurves = [curveNode1,curveNode2]


                for i , surfNode in enumerate(surfNodes):
                    firstFace = (surfSpan/newJntsCount)*i
                    
                    mc.connectAttr('%s.local' %surfShape , '%s.inputSurface' %surfNode )       
                    mc.connectAttr('%s.outputSurface' %surfNode , '%s.inputSurface' %curveFromIsoNodes[i] )    
                    mc.setAttr('%s.isoparmValue' %curveFromIsoNodes[i] , 0.5 )
                    mc.setAttr('%s.relativeValue' %curveFromIsoNodes[i] , 1 )      
                    mc.connectAttr('%s.outputCurve' %curveFromIsoNodes[i] , '%s.inputCurve' %rebuildNodes[i] )   
                    mc.setAttr('%s.keepControlPoints' %rebuildNodes[i] , 1 )         
                    mc.setAttr('%s.keepRange' %rebuildNodes[i] , 0 )   
                    mc.connectAttr('%s.outputCurve' %rebuildNodes[i] , '%s.create' %halfCurves[i])
                           
                    if dir == 'u':    
                        mc.setAttr('%s.firstFace%s' %(surfNode,dir.upper()) , firstFace )
                        mc.setAttr('%s.faceCount%s' %(surfNode,dir.upper()) , surfSpan/newJntsCount )    
                        mc.setAttr('%s.firstFaceV' %surfNode , 0 )
                        mc.setAttr('%s.faceCountV' %surfNode , 1 )        
                        mc.setAttr('%s.isoparmDirection' %curveFromIsoNodes[i] , 0 )        
                                
                    elif dir == 'v':
                        mc.setAttr('%s.firstFace%s' %(surfNode,dir.upper()) , firstFace )
                        mc.setAttr('%s.faceCount%s' %(surfNode,dir.upper()) , surfSpan/newJntsCount )    
                        mc.setAttr('%s.firstFaceU' %surfNode , 0 )
                        mc.setAttr('%s.faceCountU' %surfNode , 1 )        
                        mc.setAttr('%s.isoparmDirection' %curveFromIsoNodes[i] , 1 )    

                # --- get list of correlation halfCurveCv / surfCV per halfCurve , hold joint weight and newJoint weight

                for i , curve  in enumerate(halfCurves):
                    curvedegree = mc.getAttr('%s.degree' %curve)
                    curveSpans = mc.getAttr('%s.spans' %curve)
                    curveCvs = curvedegree+curveSpans
                    
                    cvRelatedList = []
                    if i == 0:
                        for j in range(0,curveCvs-2):
                            surfPoints = '%s.cv[%d][:]' %(surfShape,j)           
                            #gets average weight onrelated  surface cvs
                            surfPointList = mc.ls(surfPoints,fl=True)
                            surfWeight = 0
                            for point in surfPointList:
                                weight = mc.skinPercent(surfSKN , point , t = holdJnt ,q=True)
                                surfWeight = surfWeight + weight
                            surfWeight = surfWeight / len(surfPointList)  
                            #creates newJointWeight
                            cvPos = mc.pointPosition('%s.cv[%d]' %(curve,j ))
                            param = curveLib.getClosestPointOnCurve(curve, cvPos, space='world')[1]
                            percent = curveLib.findPercentFromParam(curve, param)
                            mc.setAttr('%s.varyTime' % convertFC , percent )
                            percent = mc.getAttr( '%s.varying' % convertFC )
                            newJointWeight =  surfWeight *  percent
                            surfWeight = surfWeight - newJointWeight       
                            #creates list compoud
                            cvRelated = ['%s.cv[%d]' %(curve,j) , surfPoints , surfWeight ,newJointWeight]
                            cvRelatedList.append(cvRelated)
                            #creates special case for middle point
                            if j == curveCvs-3 :
                                cvRelated = ['%s.cv[%d]' %(curve,j+2) , '%s.cv[%d][:]' %(surfShape,j+1) , 0 ,0]
                                cvRelatedList.append(cvRelated)
                            
                    elif i == 1:
                        for j in range(2,curveCvs):
                            surfPoints = '%s.cv[%d][:]' %(surfShape,j+2)           
                            #gets average weight onrelated  surface cvs
                            surfPointList = mc.ls(surfPoints,fl=True)            
                            surfWeight = 0
                            for point in surfPointList:
                                weight = mc.skinPercent(surfSKN , point , t = holdJnt ,q=True)
                                surfWeight = surfWeight + weight
                            surfWeight = surfWeight / len(surfPointList)  
                            #creates newJointWeight
                            cvPos = mc.pointPosition('%s.cv[%d]' %(curve,j ))
                            param = curveLib.getClosestPointOnCurve(curve, cvPos, space='world')[1]
                            percent = curveLib.findPercentFromParam(curve, param)
                            mc.setAttr('%s.varyTime' % convertFC , 1 - percent )
                            percent = mc.getAttr( '%s.varying' % convertFC )
                            newJointWeight =  surfWeight *  percent
                            surfWeight = surfWeight - newJointWeight     
                            #creates list compoud
                            cvRelated = ['%s.cv[%d]' %(curve,j) , surfPoints, surfWeight ,newJointWeight]
                            cvRelatedList.append(cvRelated)

                    mc.setAttr('%s.normalizeWeights' %surfSKN , 0)
                    for compound in cvRelatedList :
                        mc.skinPercent(surfSKN,compound[1],transformValue=[(holdJnt,compound[2]),(newJoints[i],compound[3])]  )      
                    mc.setAttr('%s.normalizeWeights' %surfSKN , 1)
                    
                # --- cleanup
                mc.delete(surfNodes,curveFromIsoNodes,rebuildNodes,animeCurve)
                for curve in halfCurves:
                    transform = mc.listRelatives(curve,p=True)[0]
                    mc.delete(transform)
    # --- convert IK mid weights to trhee mids weights##################################################################################################### 

    ######################################################################################################################################################################################
    ######################################################################################################################################################################################
    #TEMP DEF MERGE#######################################################################################################################################################################
    ######################################################################################################################################################################################
    ######################################################################################################################################################################################

    #def patchLib.resetTransform(trgt):
    #def patchLib.locksSwitch(sel,T=True,R=True,S=True,V=True,lockdo='unlock',keydo=False)
    #def patchLib.getRelatives(side,ctrlBase,digit)
    #orig.orig(objlist=[], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')
    #shapes.create( sel, shape= 'circle', size= 1, scale= [1, 1, 1 ], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= None, colorDegradeTo= None, replace= True, middle= False)

    WORLDGrp = 'WORLD'
    spineTemplateGrp = 'spine_curves_GUIDE'
    CurveGUIDEList = ['botSpine_01_GUIDE','L_botSpine_Tan_GUIDE','L_bot_spine_GUIDE','L_spine_GUIDE','L_top_spine_GUIDE','topSpine_GUIDE',
                'R_top_spine_GUIDE','R_spine_GUIDE','R_bot_spine_GUIDE','R_botSpine_Tan_GUIDE','botSpine_02_GUIDE']

    mainChest = 'chest_ctrl'
    mainHips = 'hips_ctrl'
        
    ### --- centerSpine Generate --- ###
    rigPart = 'spine'
    noXformGrp = 'ctrl_noXformGrp'
    smartJointsGrp = 'SmartJointsGrp'
    deformGrp = 'ctrl_DeformGrp'
    targetList = [mainChest,mainHips]
    rigRoot = 'body_gimbal_ctrl'
    smartParent = None

    midSurfSuffix = 'surfNurbs_ikMiddle'
    endSurfSuffix = 'surfNurbs'
    smartNoXformGrp = '%s_%s' %(rigPart,noXformGrp)
    centerDeformGrp = 'spine_%s' %deformGrp

    rigLvl = midSurfSuffix

    centerMidSurf = 'centerSpine_%s' %midSurfSuffix
    centerEndSurf = 'centerSpine_%s' %endSurfSuffix

    # --- assign values for columeSurf characteristics
    volspans = 4
    volDeg = 3
    volCvs = volspans + volDeg
    # --- spans and degree assign
    spans = 4
    degree = 3
    cvsCount = spans+degree

    # --- creates deform groups for futur use
    mc.group(n=centerDeformGrp,em=True)
    mc.group(n=smartNoXformGrp,em=True)
    mc.parent(smartNoXformGrp,WORLDGrp)
    # ---  cleanup and prepare curvesGuides
    for GUIDE in CurveGUIDEList:
        mc.delete(GUIDE,ch=True)
        GUIDEShapes = mc.listRelatives(GUIDE,s=True)
        for shape in GUIDEShapes:
            mc.delete(shape,ch=True)
    if mc.objExists('composeMatrix_curves_GUIDE') : mc.delete('composeMatrix_curves_GUIDE')
    # --- create volume surface
    duplicatedCurves = mc.duplicate(CurveGUIDEList)
    loftCurves=[]
    mc.parent(duplicatedCurves , w=True)
    for u , curve in enumerate(duplicatedCurves):
        mc.rebuildCurve(curve,d=3,rt=0,s=volspans)
        curveName = str(curve)
        strippedName = curveName.rsplit('_',1)[0]    
        loftCurves.append(mc.rename(curve,'%s_loftCurve' %strippedName))
    loftCurves=loftCurves[::-1]    
    volSurf = mc.loft(loftCurves,ch=False,ar=False,d=3,u=True,n='%s_volume_surfNurbs' %rigPart)[0]

    mc.delete(loftCurves)
    mc.parent(volSurf,smartNoXformGrp)

    # ---  getStart and endPoints for top and bottomCurves
    GUIDECrvSpans = mc.getAttr('%s.spans' %CurveGUIDEList[0])
    GUIDECrvDeg =  mc.getAttr('%s.degree' %CurveGUIDEList[0])
    GUIDECrvCvs = GUIDECrvSpans + GUIDECrvDeg
    #getsubSpine startPoint
    firstPoint = mc.pointPosition('%s.cv[0]' %(CurveGUIDEList[0]) , w=True)
    secPoint = mc.pointPosition('%s.cv[0]' %(CurveGUIDEList[5]) , w=True)
    startPoint = [0 ,(firstPoint[1]+secPoint[1])/2 ,(firstPoint[2]+secPoint[2])/2 ]
    #getsubSpine endPoint        
    firstPoint = mc.pointPosition('%s.cv[%d]' %(CurveGUIDEList[0],GUIDECrvCvs-1) , w=True)
    secPoint = mc.pointPosition('%s.cv[%d]' %(CurveGUIDEList[5],GUIDECrvCvs-1) , w=True)
    endPoint = [0 ,(firstPoint[1]+secPoint[1])/2 ,(firstPoint[2]+secPoint[2])/2 ]

    # ---  create centerSpine baseCurve
    linearCurve = mc.curve(p=[startPoint,endPoint],d=1,n='centerSpine_linearCurve')
    mc.rebuildCurve(linearCurve,d=degree,s = spans , rt = 0 , kep =True, ch=False )
    # --- create centerSpine baseSurf
    topCurve = mc.duplicate(linearCurve,n='centerSpine_topCurve')[0]
    for p in range(0,cvsCount):
        mc.move(0,0.05,0, '%s.cv[%d]' %(topCurve,p), r=True)
    botCurve = mc.duplicate(linearCurve,n='centerSpine_botCurve')[0]
    for p in range(0,cvsCount):
        mc.move(0,-0.05,0, '%s.cv[%d]' %(botCurve,p), r=True)
    centerMidSurf = mc.loft(botCurve,topCurve, ar=False,d=3,u=True,ch=False,n='centerSpine_%s' %midSurfSuffix )[0]
    mc.reverseSurface(centerMidSurf,d=3,ch=False,rpo=True)
    mc.rebuildSurface(centerMidSurf,kc=True,rpo=True,du=3,dv=1,dir=2,rt=0,su=spans,sv=1)
    # --- create centerSpine endSurfSuffix
    centerEndSurf = mc.duplicate(centerMidSurf,n='centerSpine_%s' %endSurfSuffix )[0]
    # --- cleanup
    mc.delete(linearCurve,topCurve,botCurve)
    mc.parent(centerMidSurf,centerEndSurf,smartNoXformGrp)


    ##########################################################################
    # ---  create smarts joints for first lvl and connects to next surf lvl
    smartList = makeMidSmartJoints(targetList,rigRoot,rigLvl,rigPart,noXformGrp,smartJointsGrp,smartParent)
    assignMidSmartToSurf(smartList,centerMidSurf,False,centerEndSurf)
    ##########################################################################

    # --- create centerSpine MidIk_ctrl and both Tan_ik_ctrls
    midCtrlsList = ['spine_mid','chest_tan','hips_tan']
    colorsList = [[0.2,1,0],[1,.5,0],[1,.5,0]]
    sizeList = [1.3,1.4,1.1]

    # --- getting midPoint of centerCurve To get vectorto topCurve
    centerCrvMidPoint = [((startPoint[0]+endPoint[0])/2),((startPoint[1]+endPoint[1])/2),((startPoint[2]+endPoint[2])/2)]
    tempCPOC = mc.createNode('closestPointOnCurve')
    crvShape = mc.listRelatives(CurveGUIDEList[5],s=True)[0]
    mc.connectAttr('%s.worldSpace[0]' %crvShape ,'%s.inCurve' %tempCPOC, f=True)
    mc.setAttr('%s.inPosition' %tempCPOC , centerCrvMidPoint[0],centerCrvMidPoint[1],centerCrvMidPoint[2] )
    pointOnTopCrv = mc.getAttr('%s.position' %tempCPOC)[0]
    mc.delete(tempCPOC)
    ## --- create vector from point positions
    midToTopVector = [0,((pointOnTopCrv[1]-centerCrvMidPoint[1])*0.75),0]

    # --- getting positionLists for all the mid controllers
    spineMidCenterPos = [0,((startPoint[1]+endPoint[1])/2),((startPoint[2]+endPoint[2])/2)]
    spineMidPos = [(spineMidCenterPos[0]+midToTopVector[0]),(spineMidCenterPos[1]+midToTopVector[1]),(spineMidCenterPos[2]+midToTopVector[2])]

    ChestTanPlaceVector = [((endPoint[0]-startPoint[0])/5),((endPoint[1]-startPoint[1])/5),((endPoint[2]-startPoint[2])/5)]
    chestTanCenterPos = [0,(startPoint[1]+ChestTanPlaceVector[1]),(startPoint[2]+ChestTanPlaceVector[2])]
    chestTanPos = [(chestTanCenterPos[0]+midToTopVector[0]),(chestTanCenterPos[1]+midToTopVector[1]),(chestTanCenterPos[2]+midToTopVector[2])]

    hipsTanCenterPos = [0,(endPoint[1]-ChestTanPlaceVector[1]),(endPoint[2]-ChestTanPlaceVector[2])]
    hipsTanPos = [(hipsTanCenterPos[0]+midToTopVector[0]),(hipsTanCenterPos[1]+midToTopVector[1]),(hipsTanCenterPos[2]+midToTopVector[2])]

    placeList = [spineMidPos,chestTanPos,hipsTanPos]
    placeCenterList = [spineMidCenterPos,chestTanCenterPos,hipsTanCenterPos]


    newCtrlList = [] 
    newCenterCtrlsList = []

    for i , ctrl in enumerate(midCtrlsList): 
        
        smartSuffix = '%sSmart' %endSurfSuffix
     
        ## --- create ctrl
        mc.select(cl=True)
        ctrl = mc.joint(n='%s_ik_ctrl' %ctrl)
        mc.setAttr('%s.drawStyle' %ctrl,2)
        shapes.create( ctrl, shape= 'arrowTwoCurve', size= sizeList[i] , scale= [1, 0.8, 0.5 ], axis= 'y', twist= 90, offset= [0, 0.4, 0 ], color= colorsList[i] , colorDegradeTo= None, replace= True, middle= False)
        mc.setAttr('%s.radius' %ctrl,0.1)  
        mc.select(cl=True)
        pivotCtrl = mc.joint(n='%s_ik_pivot_ctrl' %ctrl)
        mc.setAttr('%s.drawStyle' %pivotCtrl,2)
        shapes.create( pivotCtrl, shape= 'crossAxis', size= sizeList[i] , scale= [.75, .75, .75 ], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= None , colorDegradeTo= None, replace= True, middle= False)
        mc.setAttr('%s.radius' %pivotCtrl,0.1)  
        pivotCtrlCounter = mc.group(n='%s_ik_pivot_counter' %ctrl , em=True)    
        ctrlsOrig = orig.orig(objlist=[ctrl,pivotCtrl], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto') 
        #### --- make smartJoints
        smartNodes = []
        for n , node in enumerate((ctrl,ctrlsOrig[0],pivotCtrl,ctrlsOrig[1],pivotCtrlCounter)):
            smartNode = mc.duplicate(node,po=True,n='%s_%s' %(node,smartSuffix))[0]
            smartNodes.append(smartNode)
            smartConnect(node,smartNode)
            if n == 1 or n==3 :
                mc.parent(smartNodes[n-1],smartNode)            
        ### --- place ctrl
        ctrlPos = placeList[i]
        mc.setAttr('%s.translate' %ctrlsOrig[0],ctrlPos[0],ctrlPos[1],ctrlPos[2] )
        mc.setAttr('%s.translate' %ctrlsOrig[1],ctrlPos[0],ctrlPos[1],ctrlPos[2] )
        ### --- connect pivot co counter
        counterDm = mc.createNode('decomposeMatrix',n = '%s_dm' %pivotCtrl )
        mc.connectAttr('%s.inverseMatrix' %pivotCtrl,'%s.inputMatrix' %counterDm)
        mc.connectAttr('%s.outputTranslate' %counterDm , '%s.translate' %pivotCtrlCounter)
        mc.connectAttr('%s.outputRotate' %counterDm , '%s.rotate' %pivotCtrlCounter)    
        mc.connectAttr('%s.outputScale' %counterDm , '%s.scale' %pivotCtrlCounter)  
              
        ## --- create mid ik center ctrl
        mc.select(cl=True)
        centerCtrl = mc.joint(n='%s_center_ik_ctrl' %ctrl)
        mc.setAttr('%s.drawStyle' %centerCtrl,2)
        shapes.create( centerCtrl, shape= 'arrowEatingSnake', size= sizeList[i], scale= [2, 1.6, 1 ], axis= 'z', twist= 0, offset= [0, 0, 0 ], color= colorsList[i], colorDegradeTo= None, replace= True, middle= False)
        mc.setAttr('%s.radius' %centerCtrl,0.1)    
        mc.select(cl=True)
        pivotCenterCtrl = mc.joint(n='%s_center_ik_pivot_ctrl' %ctrl)
        mc.setAttr('%s.drawStyle' %pivotCenterCtrl,2)
        shapes.create( pivotCenterCtrl, shape= 'crossAxis', size= sizeList[i] , scale= [.75, .75, .75], axis= 'y', twist=0, offset= [0, 0, 0 ], color= None , colorDegradeTo= None, replace= True, middle= False)
        mc.setAttr('%s.radius' %pivotCenterCtrl,0.1)  
        pivotCenterCtrlCounter = mc.group(n='%s_center_ik_pivot_counter' %ctrl , em=True)           
        centerCtrlsOrig = orig.orig(objlist=[centerCtrl,pivotCenterCtrl], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto') 
        #### --- make smartJoints
        smartCenterNodes = []
        for n , node in enumerate((centerCtrl,centerCtrlsOrig[0],pivotCenterCtrl,centerCtrlsOrig[1],pivotCenterCtrlCounter)):
            smartNode = mc.duplicate(node,po=True,n='%s_%s' %(node,smartSuffix))[0]
            smartCenterNodes.append(smartNode)
            smartConnect(node,smartNode)
            if n == 1 or n==3 :
                mc.parent(smartNodes[n-1],smartNode)
        ### --- place midIkCenterCtrl
        centerCtrlPos = placeCenterList[i]
        mc.setAttr('%s.translate' %centerCtrlsOrig[0],centerCtrlPos[0],centerCtrlPos[1],centerCtrlPos[2] )
        mc.setAttr('%s.translate' %centerCtrlsOrig[1],centerCtrlPos[0],centerCtrlPos[1],centerCtrlPos[2] )    
        ### --- connect pivot co counter
        counterDm = mc.createNode('decomposeMatrix',n = '%s_dm' %pivotCenterCtrl )
        mc.connectAttr('%s.inverseMatrix' %pivotCenterCtrl,'%s.inputMatrix' %counterDm)
        mc.connectAttr('%s.outputTranslate' %counterDm , '%s.translate' %pivotCenterCtrlCounter)
        mc.connectAttr('%s.outputRotate' %counterDm , '%s.rotate' %pivotCenterCtrlCounter)    
        mc.connectAttr('%s.outputScale' %counterDm , '%s.scale' %pivotCenterCtrlCounter)  
            
        ### --- reparenting
        mc.parent(pivotCtrlCounter,ctrl , r=True)     
        mc.parent(pivotCenterCtrlCounter,centerCtrl , r=True) 
        mc.parent(centerCtrlsOrig[0],pivotCenterCtrl)    
        mc.parent(centerCtrlsOrig[1],pivotCtrlCounter)
        mc.parent(ctrlsOrig[0],pivotCtrl)
        newCtrlList.append([ctrl,pivotCtrl])
        newCenterCtrlsList.append([centerCtrl,pivotCenterCtrl])

        ### --- reparenting smartSuffix   
        mc.parent(smartNodes[0],smartNodes[1])
        mc.parent(smartNodes[2],smartNodes[3])
        mc.parent(smartNodes[4],smartNodes[0])
        mc.parent(smartNodes[1],smartNodes[2])   
        mc.parent(smartCenterNodes[0],smartCenterNodes[1])
        mc.parent(smartCenterNodes[2],smartCenterNodes[3])
        mc.parent(smartCenterNodes[4],smartCenterNodes[0])
        mc.parent(smartCenterNodes[1],smartCenterNodes[2])
        mc.parent(smartCenterNodes[3],smartNodes[4])
        

    # --- create tamponNodes and reparend midIK
    midIkTamp = mc.duplicate(newCenterCtrlsList[0][0],po=True,n='%s_orig_tamp' %newCtrlList[0][0])[0]
    mc.parent(midIkTamp,w=True)
    midIkTampSmart = mc.duplicate(midIkTamp,po=True,n='%s_%s' %(midIkTamp,smartSuffix) )[0]
    mc.parent(mc.listRelatives(newCtrlList[0][1],p=True)[0] , midIkTamp)
    mc.parent('%s_%s' %(mc.listRelatives(newCtrlList[0][1],p=True)[0] , smartSuffix ) , midIkTampSmart)
    ## --- replacing
    mc.parent(midIkTamp,centerDeformGrp)
    mc.parent(centerDeformGrp,rigRoot)
    # --- reparent Tan ctrls
    mc.parent(mc.listRelatives(newCtrlList[1][1],p=True)[0] ,mainChest)
    mc.parent(mc.listRelatives(newCtrlList[2][1],p=True)[0] ,mainHips)

    # ---  attach mid ik on midSurface with Xrivet
    getMidIkTrans = mc.getAttr('%s.translate' %midIkTamp )[0]
    getMidIkRot = mc.getAttr('%s.rotate' %midIkTamp )[0]
    mc.setAttr('%s.translate' %midIkTampSmart ,getMidIkTrans[0],getMidIkTrans[1],getMidIkTrans[2] )
    mc.setAttr('%s.rotate' %midIkTampSmart ,getMidIkRot[0],getMidIkRot[1],getMidIkRot[2] )          
    smartConnect(midIkTampSmart,midIkTamp)

    offsetXrivet = getOffsetFromXrivet('y', '-z')
    xrivetTrOnNurbs(midIkTampSmart, centerMidSurf, mainDirection = 0, out = 'worldSpace[0]', u = None, v = None,
                        offsetOrient = offsetXrivet ,min=False)

    # --- reparent smart Ctrls
    rigLvl = endSurfSuffix
    rigRootSmart = n='%s_%s_%s' %(rigRoot,rigLvl,smartJointsGrp)
    smartNoXformGrp = '%s_%s' %(rigPart,noXformGrp)
    mc.group(n=rigRootSmart , em=True)
    mc.parent(rigRootSmart,rigRoot,r=True)
    mc.parent(rigRootSmart,smartNoXformGrp)
    # --- mid smartJoint group
    midRigRootSmart = n='mid_%s_%s_%s' %(rigRoot,rigLvl,smartJointsGrp)
    mc.group(n=midRigRootSmart , em=True)
    mc.parent(midRigRootSmart,rigRootSmart)
    mc.parent(midIkTampSmart,midRigRootSmart)
    # --- chestTan smartJoint group
    chestRigRootSmart = n='chest_%s_%s_%s' %(rigRoot,rigLvl,smartJointsGrp)
    mc.group(n=chestRigRootSmart , em=True)
    chestRigRootSmartOrig = orig.orig(objlist=[chestRigRootSmart], suffix=['_orig'], origtype='transform', fromsel=False, viz=False, get_ssc=False, rtyp='auto')[0]
    mc.parent(chestRigRootSmartOrig,mainChest,r=True)
    mc.parent(chestRigRootSmartOrig,rigRootSmart)
    smartConnect('%s_orig' %mainChest,chestRigRootSmartOrig)
    smartConnect(mainChest,chestRigRootSmart)
    mc.parent('%s_%sSmart' %(mc.listRelatives(newCtrlList[1][1],p=True)[0],endSurfSuffix) ,chestRigRootSmart)
    # --- hipsTan smartJoint group
    hipsRigRootSmart = n='hips_%s_%s_%s' %(rigRoot,rigLvl,smartJointsGrp)
    mc.group(n=hipsRigRootSmart , em=True)
    hipsRigRootSmartOrig = orig.orig(objlist=[hipsRigRootSmart], suffix=['_orig'], origtype='transform', fromsel=False, viz=False, get_ssc=False, rtyp='auto')[0]
    mc.parent(hipsRigRootSmartOrig,mainChest,r=True)
    mc.parent(hipsRigRootSmartOrig,rigRootSmart)
    smartConnect('%s_orig' %mainHips,hipsRigRootSmartOrig)
    smartConnect(mainHips,hipsRigRootSmart)
    mc.parent('%s_%sSmart' %(mc.listRelatives(newCtrlList[2][1],p=True)[0],endSurfSuffix) ,hipsRigRootSmart)

    # --- add skinJoints, skin and bpm connections on endSurf
    endSurfSmartJoints = []
    endSurfBPMJoints = []
    ## --- create restJoint
    endSurfRestJoint = 'restJoint_%sSmart' %smartSuffix
    mc.select(cl=True)
    mc.joint(n=endSurfRestJoint)
    mc.setAttr('%s.radius' %endSurfRestJoint,0.1)
    mc.setAttr('%s.drawStyle' %endSurfRestJoint,2)
    mc.parent(endSurfRestJoint,rigRootSmart)
    endSurfSmartJoints.append(endSurfRestJoint)
    endSurfBPMJoints.append(endSurfRestJoint)
    ## --- create smartJoints for mid and Tan
    for m , mid in enumerate(midCtrlsList) :
        midSmart = 'center_%s_%s' %(mid,smartSuffix)
        mc.select(cl=True)
        mc.joint(n=midSmart)
        mc.setAttr('%s.radius' %midSmart,0.1)
        endSurfSmartJoints.append(midSmart)
        
        mc.parent(midSmart,newCtrlList[m][0],r=True)    
        parentTrgt = mc.listRelatives('%s_%s' %(newCenterCtrlsList[m][0],smartSuffix) , c=True)[0]
        mc.parent(midSmart,parentTrgt)
        
        bpm = '%s_%s' %(newCtrlList[m][1],smartSuffix)
        endSurfBPMJoints.append(bpm)
    ## --- skinning endSurface
    surfShape = mc.listRelatives(centerEndSurf ,s=True)[0]
    endSKC = mc.skinCluster(endSurfSmartJoints[0:2],surfShape,tsb=True,mi=2)[0]
    #### --- connect to previous surface Orig
    shapeOrig = dag.findShapeOrig(centerEndSurf)
    SKC = mc.listConnections('%s.create' %centerMidSurf , s=True)[0]
    mc.connectAttr('%s.outputGeometry[0]' %SKC , '%s.create' %shapeOrig) 
    #### --- connect bpm on SKC
    sineWeightsOnSurf(centerEndSurf,'v',True)
    convertIkMidToThreeMid(centerEndSurf,'u',endSurfSmartJoints[0],endSurfSmartJoints[2:4])
    for j in range(0,4):
        if j == 0:
            mc.connectAttr('%s.worldInverseMatrix[0]' %endSurfBPMJoints[j], '%s.bindPreMatrix[%d]' %(endSKC, j),f=True)
        else:
            mc.connectAttr('%s.parentInverseMatrix[0]' %endSurfBPMJoints[j], '%s.bindPreMatrix[%d]' %(endSKC, j),f=True)

    ####################################################################
     
    # --- convert center endSurf to sliding
    endSurfIn = mc.listConnections('%s.create' %centerEndSurf , s=True)[0]
    botEndSurfcfsi = mc.createNode('curveFromSurfaceIso' , n='botCrv_%s_cfsi' %centerEndSurf)
    topEndSurfcfsi = mc.createNode('curveFromSurfaceIso' , n='topCrv_%s_cfsi' %centerEndSurf)
    mc.connectAttr('%s.outputGeometry[0]' %endSurfIn , '%s.inputSurface' %botEndSurfcfsi)
    mc.setAttr('%s.isoparmDirection' %botEndSurfcfsi , 0 )
    mc.setAttr('%s.isoparmValue' %botEndSurfcfsi , 1 )
    mc.connectAttr('%s.outputGeometry[0]' %endSurfIn , '%s.inputSurface' %topEndSurfcfsi)
    mc.setAttr('%s.isoparmDirection' %topEndSurfcfsi , 0 )
    mc.setAttr('%s.isoparmValue' %topEndSurfcfsi , 0 )
    botEndSurfRc = mc.createNode('rebuildCurve' , n='botCrv_%s_cr' %centerEndSurf)
    topEndSurfRc = mc.createNode('rebuildCurve' , n='topCrv_%s_cr' %centerEndSurf)
    mc.connectAttr('%s.outputCurve' %botEndSurfcfsi , '%s.inputCurve' %botEndSurfRc)
    mc.setAttr('%s.spans' %botEndSurfRc ,6)
    mc.connectAttr('%s.outputCurve' %topEndSurfcfsi , '%s.inputCurve' %topEndSurfRc)
    mc.setAttr('%s.spans' %topEndSurfRc ,6)
    EndSurfLoft = mc.createNode('loft' , n='%s_loft' %centerEndSurf)
    mc.connectAttr('%s.outputCurve' %botEndSurfRc , '%s.inputCurve[0]' %EndSurfLoft)
    mc.connectAttr('%s.outputCurve' %topEndSurfRc , '%s.inputCurve[1]' %EndSurfLoft)
    mc.setAttr('%s.autoReverse' %EndSurfLoft , False)
    mc.setAttr('%s.uniform' %EndSurfLoft , 1)
    mc.connectAttr('%s.outputSurface' %EndSurfLoft , '%s.create' %centerEndSurf , f=True)

    # --- create and place anchors on centerSurf that will drive the volumeSurf
    averagePointPosList = []
    for row in range(0,volCvs):
        rowPointPosList = []
        for cv in range(0,len(CurveGUIDEList)):
            pointPos = mc.pointPosition('%s.cv[%d][%d]' %(volSurf,cv,row) , w=True)
            rowPointPosList.append(pointPos)
        pointsAdded =[0,0,0]
        for point in rowPointPosList:
            pointsAdded = [(pointsAdded[0]+point[0]),(pointsAdded[1]+point[1]),(pointsAdded[2]+point[2])]
        averagedPoint = [0,(pointsAdded[1])/len(CurveGUIDEList),(pointsAdded[2])/len(CurveGUIDEList)]
        print averagedPoint
        averagePointPosList.append(averagedPoint)          

    tempPOSI = mc.createNode('pointOnSurfaceInfo', n = 'centerSpine_temp_posi')
    tempCPOS = mc.createNode('closestPointOnSurface', n = 'centerSpine_temp_CPOS')
    mc.connectAttr('%s.worldSpace[0]' %centerEndSurf , '%s.inputSurface' %tempPOSI)
    mc.connectAttr('%s.worldSpace[0]' %centerEndSurf , '%s.inputSurface' %tempCPOS)

    centerPointPosList = []    
    for point in averagePointPosList:
        mc.setAttr('%s.inPosition' %tempCPOS , point[0],point[1],point[2])
        vParam = mc.getAttr('%s.parameterV' %tempCPOS )
        mc.setAttr('%s.parameterU' %tempPOSI , 0.5)
        mc.setAttr('%s.parameterV' %tempPOSI , vParam) 
        centerPointPos = mc.getAttr('%s.position' % tempPOSI)[0]
        centerPointPosList.append(centerPointPos) 
          
    mc.delete(tempPOSI,tempCPOS)

    ## --- creates annchors joints, connected to a dual xrivetRig blending between U and V orientation
    ### --- adding blend attribute
    AttrName = 'spineOrientBlend'
    mc.addAttr( mainHips , ln = AttrName , at = 'double' , min = 0 , max = 1 , dv = 0  )
    mc.setAttr('%s.%s' %(mainHips,AttrName) , edit = True , k = True ) 
    ### --- creates anchors
    anchorsUVGrp = mc.group(n='%s_anchors_uv_grp'%rigPart ,em=True)
    mc.parent(anchorsUVGrp,smartNoXformGrp)
    anchorJointsList = []
    for cv in range(0,len(centerPointPosList)):
        #anchroGroups
        anchorUGrp = mc.group(n='%s_anchor_%02d_u_grp'%(rigPart,cv),em=True)
        anchorVGrp = mc.group(n='%s_anchor_%02d_v_grp'%(rigPart,cv),em=True)  
        mc.setAttr('%s.translate' %anchorUGrp, centerPointPosList[cv][0],centerPointPosList[cv][1],centerPointPosList[cv][2])
        mc.setAttr('%s.translate' %anchorVGrp, centerPointPosList[cv][0],centerPointPosList[cv][1],centerPointPosList[cv][2])
        mc.parent(anchorUGrp,anchorVGrp,anchorsUVGrp)      
        offsetXrivet = getOffsetFromXrivet('-z', '-y')
        xrivetTrOnNurbs(anchorUGrp, centerEndSurf, mainDirection = 0, out = 'worldSpace[0]', u = None, v = None,
                            offsetOrient = offsetXrivet ,min=False)    
        xrivetTrOnNurbs(anchorVGrp, centerEndSurf, mainDirection = 1, out = 'worldSpace[0]', u = None, v = None,
                            offsetOrient = offsetXrivet ,min=False)          
        #anchor joint
        mc.select(cl=True)
        anchorJoint = '%s_anchor_%02d_jnt'%(rigPart,cv)
        mc.joint(n=anchorJoint)
        mc.setAttr('%s.radius' %anchorJoint,0.05)
        anchorOrig = orig.orig(objlist=[anchorJoint], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')[0]
        mc.parent(anchorOrig,anchorsUVGrp)
        anchorJointsList.append(anchorJoint)
        #pairBlend et connection
        anchorPB = mc.createNode('pairBlend', n='%s_anchorBlend_%02d_pb' %(rigPart,cv) )
        mc.connectAttr('%s.translate' %anchorUGrp , '%s.inTranslate2' %anchorPB)
        mc.connectAttr('%s.rotate' %anchorUGrp , '%s.inRotate2' %anchorPB)    
        mc.connectAttr('%s.translate' %anchorVGrp , '%s.inTranslate1' %anchorPB)
        mc.connectAttr('%s.rotate' %anchorVGrp , '%s.inRotate1' %anchorPB)  
        mc.connectAttr('%s.%s' %(mainHips,AttrName) , '%s.weight' %anchorPB) 
        mc.connectAttr('%s.outTranslate' %anchorPB , '%s.translate' %anchorOrig )
        mc.connectAttr('%s.outRotate' %anchorPB , '%s.rotate' %anchorOrig )
        mc.setAttr('%s.rotInterpolation' %anchorPB , 1 )
        
    # --- create maxLength rig by centerCurve
    ## --- createCenterCurve, curveInfo and factor node
    endLengthCfsi = mc.createNode('curveFromSurfaceIso' , n='length_%s_cfsi' %centerEndSurf)
    mc.connectAttr('%s.worldSpace[0]' %centerEndSurf , '%s.inputSurface' %endLengthCfsi)
    mc.setAttr('%s.isoparmDirection' %endLengthCfsi , 1 )
    mc.setAttr('%s.isoparmValue' %endLengthCfsi , 0.5 )
    endLengthCi = mc.createNode('curveInfo' , n='length_%s_ci' %centerEndSurf)
    mc.connectAttr('%s.outputCurve' %endLengthCfsi , '%s.inputCurve' %endLengthCi)
    endLengthMD = mc.createNode('multiplyDivide' , n='length_%s_MD' %centerEndSurf)
    mc.setAttr('%s.input1X' %endLengthMD , mc.getAttr('%s.arcLength' %endLengthCi) )
    mc.connectAttr('%s.arcLength' %endLengthCi , '%s.input2X' %endLengthMD)
    mc.setAttr('%s.operation' %endLengthMD , 2 )
    ### --- add blendAttr for maxLength
    AttrName = 'maxLengthBlend'
    mc.addAttr( mainHips , ln = AttrName , at = 'double' , min = 0 , max = 1 , dv = 0  )
    mc.setAttr('%s.%s' %(mainHips,AttrName) , edit = True , k = True ) 
    ###
    blendMaxLengthbta = mc.createNode('blendTwoAttr' , n='length_%s_bta' %centerEndSurf)
    mc.setAttr('%s.input[0]' %blendMaxLengthbta , 1 )
    mc.connectAttr('%s.outputX' %endLengthMD ,'%s.input[1]' %blendMaxLengthbta)
    mc.connectAttr('%s.%s' %(mainHips,AttrName) ,'%s.attributesBlender' %blendMaxLengthbta)

    ## --- create connection to XrivetNodes
    for cv in range(0,(len(centerPointPosList))*2):
        vValue = mc.getAttr('%s_xRivetNurbs.xRivetDatas[%d].vValue' %(centerEndSurf,cv))
        factormdl = mc.createNode('multDoubleLinear' , n='spine_anchor_%02d_mdl'%cv )
        mc.setAttr('%s.input1' %factormdl , vValue)
        mc.connectAttr('%s.output' %blendMaxLengthbta , '%s.input2' %factormdl )
        mc.connectAttr('%s.output' %factormdl , '%s_xRivetNurbs.xRivetDatas[%d].vValue' %(centerEndSurf,cv) )
        
    # --- weights volumeSurf on anchor joints / try finding ok preset for baseSkin
    # --- add second layer with mids volume deform on volumeSurf
    # --- add thirdLayer with sides offsets
    # --- attach joint after that
    # --- check if adding a bellyAim rig would be useful
    # --- check if a more solid ribCage add is possible/useful (second surface aiming but not bending with spine


    ######################################################################################################################################################################################
    ######################################################################################################################################################################################
    #TEASER DIRTY WORK START##############################################################################################################################################################
    ######################################################################################################################################################################################
    ######################################################################################################################################################################################


    # --- create Deformer ctrl/joints around endSurface   //temporary use of firstSurf
    UDeformsCount = 15
    VDeformCount = 7
    endSurf = volSurf

    endSurfDeformGrp = 'spine_endSurf_%s' %deformGrp
    mc.group(n = endSurfDeformGrp , em=True)
    mc.parent(endSurfDeformGrp,centerDeformGrp)

    tempPOSI = tempPOSI = mc.createNode('pointOnSurfaceInfo', n = 'volumeSpine_temp_posi')
    mc.setAttr('%s.turnOnPercentage' %tempPOSI,True)
    mc.connectAttr('%s.worldSpace[0]' %endSurf , '%s.inputSurface' %tempPOSI )
    volumeSpineDeformSKNList = []
    for i in range(0,UDeformsCount-1):
        for j in range(0,VDeformCount):    
            ## --- creates deform ctrl/skin hierarchy
            mc.select(cl=True)
            deformSkn = mc.joint(n='%s_deform_U%02d_V%02d_SKN' %(rigPart,i,j) )
            mc.setAttr('%s.radius' %deformSkn , 0.05)
            mc.select(cl=True)
            deformCtrl = mc.joint(n='%s_deform_U%02d_V%02d_ctrl' %(rigPart,i,j) )
            mc.setAttr('%s.radius' %deformCtrl , 0.05)
            mc.setAttr('%s.drawStyle' %deformCtrl,2)
            smartConnect(deformCtrl,deformSkn)
            shapes.create( deformCtrl, shape= 'pyramidDouble', size= 0.2, scale= [1, 1, 1 ], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= [0.5,0,0.5] , colorDegradeTo= None, replace= True, middle= False)        
            deformOrig = orig.orig(objlist=[deformCtrl], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')[0]
            mc.parent(deformSkn,deformOrig)
            volumeSpineDeformSKNList.append(deformSkn)
            ## --- getWorld Position placement for deform orig from UV
            UValue = ((1.000/(UDeformsCount-1))*i)
            VValue = ((1.000/(VDeformCount-1))*j)                      
            mc.setAttr('%s.parameterU' %tempPOSI , UValue)
            mc.setAttr('%s.parameterV' %tempPOSI , VValue)
            ctrlPos = mc.getAttr('%s.position' %tempPOSI)[0]
            mc.setAttr('%s.translate' %deformOrig , ctrlPos[0],ctrlPos[1],ctrlPos[2] )
            ## --- attach deformer ctrl/joints to endSurface
            xrivetTrOnNurbs(deformOrig, endSurf, mainDirection = 1, out = 'worldSpace[0]', u = None, v = None,
                            offsetOrient = offsetXrivet ,min=False) 
            ## --- reparent deform origs into rig
            mc.parent(deformOrig,endSurfDeformGrp)        
    mc.select(cl=True)
    mc.delete(tempPOSI)

    ## --- TempCleanup of paws sets
    volumeSpineSkinSet = 'volume_spine_skin_set'
    mc.sets(volumeSpineDeformSKNList,n=volumeSpineSkinSet)
    mc.sets(volumeSpineSkinSet,add='skin_set') 
    
    # --- cleanup :
    mc.hide(smartNoXformGrp,spineTemplateGrp)
