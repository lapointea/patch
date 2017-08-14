import maya.cmds as mc
import marsCore.shapes.defs as shapes
reload(shapes)
import marsCore.orig as orig
from marsAutoRig_stubby.patch.customLib import patchLib as patchLib
import marsCore.foundations.curveLib as curveLib
import marsCore.foundations.dagLib as dag

#def patchLib.resetTransform(trgt):
#def patchLib.locksSwitch(sel,T=True,R=True,S=True,V=True,lockdo='unlock',keydo=False)
#def patchLib.getRelatives(side,ctrlBase,digit)
#orig.orig(objlist=[], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')
#shapes.create( sel, shape= 'circle', size= 1, scale= [1, 1, 1 ], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= None, colorDegradeTo= None, replace= True, middle= False)

############################################################################################
def createAnimCurveFromDef(curveDef,curveNodeName):
    #give dictionary definition of curve to function to recreate the animeCurve   
    #dict() # curveDef = {'tangentsVal': [0.0, 0.0, 56.329492519973265, 60.702413199576945], 'keyCount': 4, 'keysValues': [0.0, 0.0, 0.1531658647581936, 1.0], 'keysAtFrame': [0.0, 0.276, 0.5, 1.0]}
    #string # curveNodeName = 'testAnimCurve'

    animCurve = mc.createNode('animCurveTU' , n = curveNodeName )
    for i in range(0,curveDef['keyCount']):
        mc.setKeyframe( curveNodeName , t = curveDef['keysAtFrame'][i] , v = curveDef['keysValues'][i] , itt = 'auto' , ott = 'auto' )
        mc.keyTangent( curveNodeName , edit = True , index = (i,i) , inAngle = curveDef['tangentsVal'][i] , outAngle = curveDef['tangentsVal'][i])
    
    return curveNodeName
############################################################################################
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
# --- fkSection create def ############################################################
############################################################################################
#fromCurveWeightsOnSurf(surf='nurbsPlane1',dir='u',reverseInf=False,animeCurve='locator3_translateY')
def fromCurveWeightsOnSurf(surf,dir,reverseInf,animeCurve):
    # changes weights on a surfaces with 2 influences, uses an animationCurve to go from linear to custom (curve must be from 0 to 1 in every axis )
    #surf = 'nurbsPlane1'
    #dir = 'u'
    #reverseInf = False
    #animeCurve = 'locator3_translateY'

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
############################################################################################
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


def patch():
            
    #vars#########################################################################################
    sides = ['L','R']
    intFixes = ['front','back']
    fullLegDuplicate = ['leg_01','leg_02','foot_01','foot_02']
    ##############################################################################################


    for side in sides :
        if side == 'L' :
            ctrlcolor = 6
        elif side == 'R' :
            ctrlcolor = 13
        #duplicates legs joints to create new fullLeg chain######################################################
        newChain = []
        for i , joint in enumerate(fullLegDuplicate) :
            target = '%s_%s_%s' % (side,intFixes[1],joint)
            if mc.objExists(target):
                newjoint = mc.duplicate(target,po = True)[0]
                patchLib.locksSwitch(newjoint,T=True,R=True,S=True,V=True,lockdo='unlock',keydo=True)
                mc.parent(newjoint,w=True)
                newName = '%s_%s_fullLeg_%02d' % (side,intFixes[1],(i+1))
                mc.rename(newjoint,newName)
                newChain.append(newName)
        if newChain :
            mc.parent(newChain[3],newChain[2])
            mc.parent(newChain[2],newChain[1])
            mc.parent(newChain[1],newChain[0])
        ##parents new fullLeg at the same place as base legs########################################################
        newParent = mc.listRelatives('%s_%s_leg_01_orig' %(side,intFixes[1]) , p = True )[0]
        mc.parent(newChain[0],newParent)
        ############################################################################################################
        #creates new upvector and ik for fullLeg####################################################################
        duplicatedUpVector = mc.duplicate('%s_%s_leg_PV_ctrl' %(side,intFixes[1]))[0]
        fullLegUpV = mc.rename(duplicatedUpVector,'%s_%s_fullLeg_PV_ctrl' %(side,intFixes[1]))
        shapes.create( fullLegUpV, shape= 'pyramid', size= 1, scale= [1, 1, 1 ], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= ctrlcolor, colorDegradeTo= None, replace= True, middle= False)
        fullLegUpVOrig = orig.orig(objlist=[fullLegUpV], suffix=['_orig'], origtype='transform', fromsel=False, viz=False, get_ssc=False, rtyp='auto')[0]
        mc.parent(fullLegUpVOrig,'traj')    
        ###scales newUpvector shape up ##########################################################  
        scalePoints = mc.ls('%s.cv[*]' % fullLegUpV,fl = True)
        mc.scale( 1.25,1.25,1.25, scalePoints , r = True , ocp = True )
        ##creates ik for fullLeg###################################################################################
        fullLegIkName = '%s_%s_fullLeg_ikh' % (side,intFixes[1])
        fullLegIk = mc.ikHandle(sj = newChain[0] , ee = newChain[3] , n = fullLegIkName , sol = 'ikRPsolver' )
        mc.poleVectorConstraint(fullLegUpV,fullLegIk[0])
        ##reparent log upV in FullLeg upV and replace constraint
        upVCnsName = '%s_%s_leg_PV_ctrl_orig_parentConstraint1' % (side,intFixes[1])
        upVCnsTarget = mc.parentConstraint( upVCnsName , q = True , tl = True )[0]
        mc.delete(upVCnsName)
        legUpVOrig = '%s_%s_leg_PV_ctrl_orig' % (side,intFixes[1])
        mc.parent (legUpVOrig,fullLegUpV)
        mc.parentConstraint(upVCnsTarget,fullLegUpVOrig, mo = True )
        
        
        
        ############################################################################################################

        #updating original ball 01 and 02 rigs###################################################################### 
        ball01 = '%s_%s_leg_rvfoot_ball_01_ctrl' %(side,intFixes[1])
        ball02Orig = '%s_%s_leg_rvfoot_ball_02_ctrl_orig' %(side,intFixes[1])
        ball02 = '%s_%s_leg_rvfoot_ball_02_ctrl' %(side,intFixes[1])  
        #updating original ball_01 rig##############################################################################
        ##ads ik offset on ball01###################################################################################
        patchLib.locksSwitch(ball01,T=True,R=True,S=True,V=True,lockdo='unlock',keydo=True)   
        ball01ik = mc.duplicate( ball01 , po = True )
        ball01ikend = mc.duplicate( ball02Orig , po = True )
        ball01ikName = '%s_%s_leg_ik_rvfoot_ball_01_joint' %(side,intFixes[1]) 
        ball01ikEndName = '%s_%s_leg_ik_rvfoot_ball_01_end' %(side,intFixes[1])
        ball01ik=mc.rename(ball01ik,ball01ikName)
        ball01ikend=mc.rename(ball01ikend,ball01ikEndName)
        mc.parent(ball01ikend,ball01ik)
        mc.parent(ball01,ball01ik)
        ###creates ctrl for ball01  ik offset###########################################################################
        ballIKCtrlname = '%s_%s_leg_rvfoot_ik_ball_01_ctrl' % (side,intFixes[1])
        mc.select(cl=True)
        ballIKCtrl = mc.joint(n = ballIKCtrlname )
        mc.setAttr('%s.drawStyle' %ballIKCtrl , 2 )
        ballIKCtrlOrig = orig.orig(objlist=[ballIKCtrl], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')[0]
        shapes.create( ballIKCtrl, shape= 'cube', size= .25, scale= [1, .5, 1 ], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= ctrlcolor, colorDegradeTo= None, replace= True, middle= False)
        mc.parent(ballIKCtrlOrig,ball01ikend)
        mc.setAttr('%s.translate'%ballIKCtrlOrig,0,0,0)
        mc.parent(ballIKCtrlOrig,(mc.listRelatives(ball01ik,p=True)))     
        ###creates ikSCsolver for ball 01 ik ##################################################################### 
        ball01ikhName = '%s_%s_leg_rvfoot_ik_ball_01_ikh' % (side,intFixes[1])
        ball01ikh =  mc.ikHandle(sj = ball01ik , ee = ball01ikend , n = ball01ikhName , sol = 'ikSCsolver' )  
        mc.parent(ball01ikh[0],ballIKCtrl)

        
        patchLib.locksSwitch(ball01,T=True,R=False,S=True,V=True,lockdo='lock',keydo=False)   
        #updating original ball_02 rig##############################################################################  
        ##remove original aim constraint############################################################################  
        ball02AimCns = mc.listConnections( '%s.rotateX' % ball02Orig )[0]
        mc.delete(ball02AimCns)
        ##ads ik offset on ball02###################################################################################
        ballDublicate = [ ball02Orig, '%s_%s_leg_rvfoot_ball_02_ctrl' %(side,intFixes[1]) , '%s_%s_leg_rvfoot_ankle_ctrl' %(side,intFixes[1] ) ]
        newBall = []
        for j , ballJnt in enumerate(ballDublicate) :
            newJnt = mc.duplicate( ballJnt , po = True )       
            newJntName = ballDublicate[j].replace('rvfoot','rvfoot_ik')
            newJntName = newJntName.replace('ctrl','jnt')
            mc.rename(newJnt,newJntName)
            newBall.append(newJntName)
        mc.parent(newBall[2],newBall[1])
        mc.parent(newBall[1],newBall[0])
        mc.parent(newBall[0],ball02Orig)
        mc.parent(ball02,newBall[1])
        ###creates ikSCsolver for ball ik offset##################################################################### 
        ball02ikhName = '%s_%s_leg_rvfoot_ik_ball_02_ikh' % (side,intFixes[1])
        ball02ikh =  mc.ikHandle(sj = newBall[1] , ee = newBall[2] , n = ball02ikhName , sol = 'ikSCsolver' )
        ###creates ctrl for ball ik offset###########################################################################
        ballIKCtrlname = '%s_%s_leg_rvfoot_ik_ball_02_ctrl' % (side,intFixes[1])
        mc.select(cl=True)
        ballIKCtrl = mc.joint(n = ballIKCtrlname )
        mc.setAttr('%s.drawStyle' %ballIKCtrl , 2 )
        ballIKCtrlOrig = orig.orig(objlist=[ballIKCtrl], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')[0]
        if side == 'L' :
            ctrlcolor = 6
        elif side == 'R' :
            ctrlcolor = 13
        shapes.create( ballIKCtrl, shape= 'locator', size= 1, scale= [1, 1, 1 ], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= ctrlcolor, colorDegradeTo= None, replace= True, middle= False)
        mc.parent(ballIKCtrlOrig,newBall[2],r =True)
        mc.parent(ballIKCtrlOrig,newBall[0])
        ####adjusts ctrl position####################################################################################
        mc.setAttr('%s.translateY' %ballIKCtrlOrig, (mc.getAttr('%s.translateY' %ballIKCtrlOrig))*2)
        mc.xform(ballIKCtrlOrig, ws = True , r = True, a = True , ro = (0,0,0))
        if side == 'L':
            mc.setAttr('%s.jointOrientX' % ballIKCtrl , 180-(mc.getAttr('%s.rotateX' % ballIKCtrlOrig)) )  
        if side == 'R':
            mc.setAttr('%s.jointOrientX' % ballIKCtrl , -(mc.getAttr('%s.rotateX' % ballIKCtrlOrig)) )
        ##parents ball 02 ikh into ctrl##############################################################################
        mc.parent(ball02ikh[0],ballIKCtrl)
        mc.setAttr('%s.translate' % ball02ikh[0] , 0,0,0 )
        ##constraints updated ball02 to fullLeg######################################################################
        mc.parentConstraint(newChain[3],newBall[0],st=["x","y","z"],mo=True) 
        ##connects translate of fullLegs first joint to base legs first joint#######################################
        mc.connectAttr('%s.translate'%newChain[0],'%s_%s_leg_01_orig.translate'%(side,intFixes[1]),f=True)
        ##parent new ikh############################################################################################
        fullLegParent = '%s_%s_leg_rvfoot_ball_01_ctrl' %(side,intFixes[1])
        mc.parent(fullLegIk[0],fullLegParent)        
        ##############################################################################################################
        #temp remove front aim cns on ball_02
        mc.delete('%s_%s_leg_rvfoot_ball_02_ctrl_orig_aimConstraint1'%(side,intFixes[0]))    
        ##############################################################################################################
   
        
        
        
    '''
    #create global Mid groups
    ########################################################
    finalFactor = len(hips)
    posValues = [0,0,0]
    for ctrl in hips :
        wPos = mc.xform(ctrl, ws = True, q=True, t=True)
        posValues[0] = posValues[0] + wPos[0]
        posValues[1] = posValues[1] + wPos[1]
        posValues[2] = posValues[2] + wPos[2]
    finalPosValue = [posValues[0]/finalFactor,posValues[1]/finalFactor,posValues[2]/finalFactor]
    #create actual cnsGroup
    cnsGroup = mc.group(n='hips_spine_cns_grp' , em=True)
    mc.setAttr('%s.translate' %cnsGroup , finalPosValue[0],finalPosValue[1],finalPosValue[2] )
    mc.parent(cnsGroup,mainHips)
    mainCnsGroupsList.append(cnsGroup)
    for ctrl in hips:
        mc.parentConstraint(cnsGroup,'%s_%s_orig' %(ctrl,overGroups[0]) , mo=True)                                      
    ########################################################   
    finalFactor = len(chests)
    posValues = [0,0,0]
    for ctrl in chests :
        wPos = mc.xform(ctrl, ws = True, q=True, t=True)
        posValues[0] = posValues[0] + wPos[0]
        posValues[1] = posValues[1] + wPos[1]
        posValues[2] = posValues[2] + wPos[2]
    finalPosValue = [posValues[0]/finalFactor,posValues[1]/finalFactor,posValues[2]/finalFactor]
    #create actual cnsGroupq
    cnsGroup = mc.group(n='chest_spine_cns_grp' , em=True)
    mc.setAttr('%s.translate' %cnsGroup , finalPosValue[0],finalPosValue[1],finalPosValue[2] ) 
    mc.parent(cnsGroup,mainChest)
    mainCnsGroupsList.append(cnsGroup)
    for ctrl in chests:
        mc.parentConstraint(cnsGroup,'%s_%s_orig' %(ctrl,overGroups[0]) , mo=True) 
    ######################################################## 
    finalFactor = len(mids)
    posValues = [0,0,0]
    for ctrl in mids :
        wPos = mc.xform(ctrl, ws = True, q=True, t=True)
        posValues[0] = posValues[0] + wPos[0]
        posValues[1] = posValues[1] + wPos[1]
        posValues[2] = posValues[2] + wPos[2]
    finalPosValue = [posValues[0]/finalFactor,posValues[1]/finalFactor,posValues[2]/finalFactor]
    #create actual cnsGroup
    cnsGroup = mc.group(n='mids_spine_cns_grp' , em=True)
    mc.setAttr('%s.translate' %cnsGroup , finalPosValue[0],finalPosValue[1],finalPosValue[2] )
    mc.parent(cnsGroup,mainChest)
    mainCnsGroupsList.append(cnsGroup)
    ########################################################
    finalFactor = len(mids)
    posValues = [0,0,0]
    for ctrl in chestTans :
        wPos = mc.xform(ctrl, ws = True, q=True, t=True)
        posValues[0] = posValues[0] + wPos[0]
        posValues[1] = posValues[1] + wPos[1]
        posValues[2] = posValues[2] + wPos[2]
    finalPosValue = [posValues[0]/finalFactor,posValues[1]/finalFactor,posValues[2]/finalFactor]
    #create actual cnsGroup
    cnsGroup = mc.group(n='chestTan_spine_ctrl' , em=True)
    mc.setAttr('%s.translate' %cnsGroup , finalPosValue[0],finalPosValue[1],finalPosValue[2] )
    mc.parent(cnsGroup,mainCnsGroupsList[1])
    mainCnsGroupsList.append(cnsGroup)
    ########################################################
    finalFactor = len(mids)
    posValues = [0,0,0]
    for ctrl in hipsTans :
        wPos = mc.xform(ctrl, ws = True, q=True, t=True)
        posValues[0] = posValues[0] + wPos[0]
        posValues[1] = posValues[1] + wPos[1]
        posValues[2] = posValues[2] + wPos[2]
    finalPosValue = [posValues[0]/finalFactor,posValues[1]/finalFactor,posValues[2]/finalFactor]
    #create actual cnsGroup
    cnsGroup = mc.group(n='hipsTan_spine_ctrl' , em=True)
    mc.setAttr('%s.translate' %cnsGroup , finalPosValue[0],finalPosValue[1],finalPosValue[2] )
    mc.parent(cnsGroup,mainCnsGroupsList[0])
    mainCnsGroupsList.append(cnsGroup)
    ########################################################
    # --- adds cns on mid_cns group to keep it at mid distance between hip and chest cns groups
    mc.parentConstraint(mainCnsGroupsList[0],mainCnsGroupsList[1],mainCnsGroupsList[2],mo=True)
    ##################################################################################################
    # --- adding variablePivot global spine controls

    # --- adding variable pivots to TAN controls
    bothTanList =zip([chestTans,hipsTans],[mainCnsGroupsList[3],mainCnsGroupsList[4]])
    for list in bothTanList :
        tanList = list[0]
        cnsGroup = list[1]
        # --- create control layer on cnsGroup
        orig.orig(objlist=[cnsGroup], suffix=['_orig'], origtype='transform', fromsel=False, viz=False, get_ssc=False, rtyp='auto')
        shapes.create( cnsGroup, shape= 'arrowEatingSnake', size= 1.3, scale= [2, 1.5, 1 ], axis= 'z', twist= 0, offset= [0, 0, 0 ], color= [0.75,1,0], colorDegradeTo= None, replace= True, middle= False)
        # --- create variable pivot cns rig
        # --- variable pivot rig for Tan ctrls
        for tanCtrl in tanList :
            ## --- create matrixOffset group
            matOffGrp = mc.group(n = '%s_matOffset_grp' % tanCtrl , em=True)
            mc.parent(matOffGrp,mc.listRelatives(tanCtrl,p=True)[0],r=True)
            mc.parentConstraint(cnsGroup,matOffGrp,mo=False)
            mc.scaleConstraint(cnsGroup,matOffGrp,mo=False)
            ## --- create matrixNodes ton constraint
            cnsGroupName = '%s_cns_orig' %tanCtrl
            decMat = mc.createNode('decomposeMatrix' , n = '%s_dm' %cnsGroupName)
            multMat = mc.createNode('multMatrix' , n =  '%s_mm' %cnsGroupName)
            mc.connectAttr('%s.matrixSum' %multMat , '%s.inputMatrix' %decMat)
            
            mc.connectAttr('%s.inverseMatrix' %matOffGrp , '%s.matrixIn[0]' %multMat)
            mc.connectAttr('%s.matrix' %cnsGroup , '%s.matrixIn[1]' %multMat)
            mc.connectAttr('%s.matrix' %matOffGrp , '%s.matrixIn[2]' %multMat)        
            
            mc.connectAttr('%s.outputTranslate' %decMat , '%s.translate' %cnsGroupName )  
            mc.connectAttr('%s.outputRotate' %decMat , '%s.rotate' %cnsGroupName )      
            mc.connectAttr('%s.outputScale' %decMat , '%s.scale' %cnsGroupName ) 
    # --- variable pivot rig for midSpine rig
    ## create midSpine global controls
    spineMidTop = 'spine_mid_top_ctrl'
    spineMidTopPvt = 'spine_mid_top_pivotCtrl'
    spineMidCenter = 'spine_mid_center_ctrl'
    spineMidCenterPvt = 'spine_mid_center_pivotCtrl'
    spineCtrlsList = [spineMidTop,spineMidTopPvt,spineMidCenter,spineMidCenterPvt]
    mc.group(n=spineMidTop,em=True)
    mc.group(n=spineMidTopPvt,em=True)            
    mc.group(n=spineMidCenter,em=True)            
    mc.group(n=spineMidCenterPvt,em=True)
    shapes.create( spineMidTop, shape= 'arrowTwoCurve', size= 1 , scale= [2, 1.5, 1 ], axis= 'y', twist= 90, offset= [0,0,0], color= [0.25,1,0.25], colorDegradeTo= None, replace= True, middle= False)
    shapes.create( spineMidTopPvt, shape= 'crossAxis', size= 1, scale= [1, 1, 1 ], axis= 'y', twist= 0, offset= [0,0,0], color= None, colorDegradeTo= None, replace= True, middle= False)
    shapes.create( spineMidCenter, shape= 'arrowEatingSnake', size= 1.4, scale= [2, 1.5, 1 ], axis= 'z', twist= 0, offset= [0,0.05,0], color= [0.25,1,0.25], colorDegradeTo= None, replace= True, middle= False)
    shapes.create( spineMidCenterPvt, shape= 'crossAxis', size= 1, scale= [2.5, 1,1 ], axis= 'y', twist= 0, offset= [0,0,0], color= None, colorDegradeTo= None, replace= True, middle= False)
    ### parent ctrl into hierarchy
    mc.parent(spineMidTop,spineMidTopPvt)
    mc.parent(spineMidCenter,spineMidCenterPvt)
    ### offset top pivot to spine mid ctrl
    spineMidWPos = mc.xform(mids[0],ws = True, q=True,t=True)
    mc.xform(spineMidTopPvt , ws=True, t=spineMidWPos)        
    ### reparent stuff to correct hierarchy and creates origs
    mc.parent(spineMidCenterPvt,mainCnsGroupsList[2],r=True)
    mc.parent(spineMidTopPvt,mainCnsGroupsList[2])
    mc.parent(spineMidCenterPvt,spineMidTop) 
    orig.orig(objlist=spineCtrlsList, suffix=['_orig'], origtype='transform', fromsel=False, viz=False, get_ssc=False, rtyp='auto')
    # --- creates offsets groups and matrix nodes
    for midCtrl in mids:
        ## --- create matrixOffset group
        matOffGrp = mc.group(n = '%s_matOffset_grp' % midCtrl , em=True)
        mc.parent(matOffGrp,mc.listRelatives(midCtrl,p=True)[0],r=True)
        mc.parentConstraint(spineMidTop,matOffGrp,mo=False)
        mc.scaleConstraint(spineMidTop,matOffGrp,mo=False)
        ## --- create matrixNodes ton constraint
        cnsGroupName = '%s_cns_orig' %midCtrl
        decMat = mc.createNode('decomposeMatrix' , n = '%s_dm' %cnsGroupName)
        multMat = mc.createNode('multMatrix' , n =  '%s_mm' %cnsGroupName)
        mc.connectAttr('%s.matrixSum' %multMat , '%s.inputMatrix' %decMat)
        
        mc.connectAttr('%s.inverseMatrix' %matOffGrp , '%s.matrixIn[0]' %multMat)
        mc.connectAttr('%s.matrix' %spineMidTop , '%s.matrixIn[1]' %multMat)
        mc.connectAttr('%s_orig.inverseMatrix' %spineMidCenterPvt , '%s.matrixIn[2]' %multMat)
        mc.connectAttr('%s.inverseMatrix' %spineMidCenterPvt , '%s.matrixIn[3]' %multMat)        
        mc.connectAttr('%s.matrix' %spineMidCenter , '%s.matrixIn[4]' %multMat)
        mc.connectAttr('%s.matrix' %spineMidCenterPvt , '%s.matrixIn[5]' %multMat)
        mc.connectAttr('%s_orig.matrix' %spineMidCenterPvt , '%s.matrixIn[6]' %multMat)        
        mc.connectAttr('%s.matrix' %matOffGrp , '%s.matrixIn[7]' %multMat)        
        
        mc.connectAttr('%s.outputTranslate' %decMat , '%s.translate' %cnsGroupName )  
        mc.connectAttr('%s.outputRotate' %decMat , '%s.rotate' %cnsGroupName )      
        mc.connectAttr('%s.outputScale' %decMat , '%s.scale' %cnsGroupName )         
      
    # --- adding aimRig for belly and sides spines
    attrNode = spineMidTop
    AttrName = 'straightBelly'
    botAimNodes = [chests[3],hips[3]]
    LAimNodes = [chests[1],hips[1]]
    RAimNodes = [chests[2],hips[2]]
    sidesAimNodes = [LAimNodes,RAimNodes]
    #overGroups[1]

    ## --- adding straightBelly attribute
    mc.addAttr( attrNode , ln = AttrName , at = 'double' , min = 0 , max = 1 , dv = 0.5  )
    mc.setAttr('%s.%s' %(attrNode,AttrName) , edit = True , k = True ) 
    ## --- adding main AimCns and node on bottom Belly
    aimNewNodes = []
    for aimNode in botAimNodes:
        aimTrgt =  '%s_%s_orig' %(aimNode,overGroups[1])
        aimParent = mc.listRelatives(aimTrgt,p=True)[0]
        aimFullNode = '%s_%s_full' %(aimNode,overGroups[1])
        aimHoldNode = '%s_%s_hold' %(aimNode,overGroups[1])
        mc.group(n=aimFullNode , em=True)
        mc.group(n=aimHoldNode , em=True)  
        mc.parent(aimFullNode,aimHoldNode,aimParent,r=True)
        aimNodes = [aimFullNode,aimHoldNode,aimParent]
        aimNewNodes.append(aimNodes)
        mc.setAttr('%s.rotateOrder' %aimTrgt , 1)
        mc.setAttr('%s.rotateOrder' %aimFullNode , 1)    
        mc.setAttr('%s.rotateOrder' %aimHoldNode , 1)
        #create parentConstraints with blends
        aimPairBlend = mc.createNode('pairBlend',n='%s_pb' %aimTrgt)
        mc.connectAttr('%s.translate' %aimHoldNode,'%s.inTranslate1' %aimPairBlend)
        mc.connectAttr('%s.rotate' %aimHoldNode,'%s.inRotate1' %aimPairBlend)   
        mc.connectAttr('%s.translate' %aimFullNode,'%s.inTranslate2' %aimPairBlend)
        mc.connectAttr('%s.rotate' %aimFullNode,'%s.inRotate2' %aimPairBlend)
        mc.connectAttr('%s.outTranslate' %aimPairBlend  ,'%s.translate' %aimTrgt)
        mc.connectAttr('%s.outRotate' %aimPairBlend  ,'%s.rotate' %aimTrgt)
        mc.connectAttr('%s.%s' %(attrNode,AttrName) , '%s.weight' %aimPairBlend )   
    ### creates aim constraints for bottom
    botChestAimCns = mc.aimConstraint(aimNewNodes[1][0],aimNewNodes[0][0],aim=[0,0,-1],u=[1,0,0],wu=[1,0,0],wut='object',wuo=aimNewNodes[0][2],mo=True  )
    botHipstAimCns = mc.aimConstraint(aimNewNodes[0][0],aimNewNodes[1][0],aim=[0,0,1],u=[1,0,0],wu=[1,0,0],wut='object',wuo=aimNewNodes[1][2],mo=True  ) 

    ## --- adding main AimCns and node on sides
    for sideAimNodes in sidesAimNodes:
        aimNewNodes = []
        for aimNode in sideAimNodes:
            aimTrgt =  '%s_%s_orig' %(aimNode,overGroups[1])
            aimParent = mc.listRelatives(aimTrgt,p=True)[0]
            aimFullNode = '%s_%s_full' %(aimNode,overGroups[1])
            aimHoldNode = '%s_%s_hold' %(aimNode,overGroups[1])
            mc.group(n=aimFullNode , em=True)
            mc.group(n=aimHoldNode , em=True)  
            mc.parent(aimFullNode,aimHoldNode,aimParent,r=True)
            aimNodes = [aimFullNode,aimHoldNode,aimParent]
            aimNewNodes.append(aimNodes)
            mc.setAttr('%s.rotateOrder' %aimTrgt , 1)
            mc.setAttr('%s.rotateOrder' %aimFullNode , 1)    
            mc.setAttr('%s.rotateOrder' %aimHoldNode , 1)
            #create parentConstraints with blends
            aimPairBlend = mc.createNode('pairBlend',n='%s_pb' %aimTrgt)
            halfAimMdl = mc.createNode('multDoubleLinear',n='%s_mdl' %aimTrgt)
            mc.setAttr('%s.input2' %halfAimMdl , 0.5)
            mc.connectAttr('%s.%s' %(attrNode,AttrName),'%s.input1' %halfAimMdl )
            
            mc.connectAttr('%s.translate' %aimHoldNode,'%s.inTranslate1' %aimPairBlend)
            mc.connectAttr('%s.rotate' %aimHoldNode,'%s.inRotate1' %aimPairBlend)   
            mc.connectAttr('%s.translate' %aimFullNode,'%s.inTranslate2' %aimPairBlend)
            mc.connectAttr('%s.rotate' %aimFullNode,'%s.inRotate2' %aimPairBlend)
            mc.connectAttr('%s.outTranslate' %aimPairBlend  ,'%s.translate' %aimTrgt)
            mc.connectAttr('%s.outRotate' %aimPairBlend  ,'%s.rotate' %aimTrgt)
            mc.connectAttr('%s.output' %halfAimMdl , '%s.weight' %aimPairBlend )   
        ### creates aim constraints for bottom
        botChestAimCns = mc.aimConstraint(aimNewNodes[1][0],aimNewNodes[0][0],aim=[0,0,-1],u=[1,0,0],wu=[1,0,0],wut='object',wuo=aimNewNodes[0][2],mo=True  )
        botHipstAimCns = mc.aimConstraint(aimNewNodes[0][0],aimNewNodes[1][0],aim=[0,0,1],u=[1,0,0],wu=[1,0,0],wut='object',wuo=aimNewNodes[1][2],mo=True  )     
    '''



    #create aimRig for sides and bottom spines
    # add visibility switches and change shape for easier manipulation




    ######################################################################################################################################################################################
    ######################################################################################################################################################################################
    #TEASER DIRTY WORK START##############################################################################################################################################################
    ######################################################################################################################################################################################
    ######################################################################################################################################################################################

    # --- fix ik offsets symmetries and parentings

    hipIkOffset = 'hip_ik_offset_ctrl'
    sideHips = 'hip_ctrl_01'
    pelvis = 'pelvis_ctrl'

    scapIkOffset = 'scapula_ik_offset_ctrl'
    scap = 'scapula_ctrl_01'
    scapOffset = 'scapula_offset_ctrl'

    scapRootIkOffset = 'scapula_root_ik_offset_ctrl'
    scapRoot = 'scapula_root_ctrl_01'
    chestAdjust = 'chest_adjust_ctrl'

    ikCtrlList = [hipIkOffset,scapIkOffset,scapRootIkOffset]
    fkCtrlList =[sideHips,scap,scapRoot]
    rootList = [pelvis,scapOffset,chestAdjust]


    for side in sides :
        for i,ik in enumerate(ikCtrlList):
            hipIkOffsetParent = mc.listRelatives('%s_%s' %(side,ik),p=True)[0]    
            ### --- create autogroup for later use
            autoGrp = orig.orig(objlist=['%s_%s' %(side,ik)], suffix=['_orig'], origtype='transform', fromsel=False, viz=False, get_ssc=False, rtyp='auto')[0]
            mc.rename(autoGrp,'%s_%s_auto' %(side,ik))
            ### --- reparent ik offsets controllers
            if side == 'R':
                mc.parent(hipIkOffsetParent,w=True)
                mc.setAttr('%s.rotate' %hipIkOffsetParent , 0,0,0 )         
                mc.setAttr('%s.scaleX' %hipIkOffsetParent , -1 )  
            root = rootList[i]
            if i == 1:
                root = '%s_%s' %(side,rootList[i])
            mc.parent(hipIkOffsetParent , root )
            ### --- generate ik offset joints hierarchy
            fk = '%s_%s' %(side,fkCtrlList[i])
            rootJoint = mc.duplicate(fk , po=True , n = fk.replace('ctrl','ik_jnt') )[0]
            endJoint = mc.duplicate(mc.listRelatives(fk,c=True)[0],po=True,n= '%s_end' %rootJoint )[0]
            mc.parent(endJoint,rootJoint)
            mc.parent(rootJoint,root)
            ### --- add ikHandle to IkOffsets
            ikHandle = mc.ikHandle(sj=rootJoint , ee=endJoint , sol='ikSCsolver',n='%s_ikh' %rootJoint)[0]
            mc.parent(ikHandle,'%s_%s' %(side,ik))
            mc.hide(ikHandle)   
            ### --- reparent fk hips inside ikHandle
            mc.parent(mc.listRelatives('%s_%s' %(side,fkCtrlList[i]),p=True)[0],rootJoint)
            ### --- quickCleanup
            patchLib.locksSwitch('%s_%s' %(side,ik),T=False,R=True,S=True,V=True,lockdo='lock',keydo=False)   

                          
    # --- make cheap paws/toes with shitty repose of sections

    toesReplaceDict = {u'L_front_04_paw_tipSquash_repose': [(0.001985158689634128, 0.021460092886801757, -0.01891139085751101), (-16.10338128982276, 0.0, 0.0)], u'L_front_02_paw_repose_02': [(1.1102230246251565e-16, -4.440892098500626e-16, -1.1102230246251565e-16), (36.53542590439221, 0.0, 0.0)], u'R_front_02_paw_tip_repose_02': [(1.1102230246251565e-16, -4.440892098500626e-16, 8.326672684688674e-17), (0.0, 0.0, 0.0)], u'L_front_02_paw_repose_01': [(0.0001724089493585802, -0.018163882042368948, -0.06309008515807871), (-9.214024116352087, -3.5671655121773083, -0.2472910389020807)], u'R_back_03_paw_tipSquash_repose': [(2.2204460492502963e-16, -0.0069115976941169326, -0.007629144349090558), (-16.14110731208447, 0.0, 0.0)], u'R_back_02_paw_tip_repose_02': [(5.551115123125783e-17, -0.0, -1.1102230246251565e-16), (0.0, 0.0, 0.0)], u'R_back_02_paw_tip_repose_01': [(5.551115123125783e-17, 2.220446049250313e-16, 1.1102230246251565e-16), (5.413616972292173, 0.0, 0.0)], u'L_back_paw_repose_01': [(0.0, 0.0, 0.0), (-13.180430584612095, 0.0, 0.0)], u'L_back_04_paw_tip_repose_02': [(0.0, 0.0, 5.551115123125783e-17), (0.0, 0.0, 0.0)], u'L_back_04_paw_tip_repose_01': [(0.002740842211619208, -0.005928469615408057, -0.004919555039966667), (13.544535774603828, 0.0, 0.0)], u'L_back_paw_repose_02': [(0.0, 0.0, 0.0), (-11.564794598410202, 0.0, 0.0)], u'L_back_04_paw_tipSquash_repose': [(-0.0023507730452710417, 0.03130494589651657, -0.0058242886700340755), (-21.247061143788052, 0.0, 0.0)], u'R_front_04_paw_tip_repose_01': [(0.0, -0.0, -0.0), (-7.245890310999545, 0.0, 0.0)], u'R_front_04_paw_tip_repose_02': [(1.1102230246251565e-16, -4.440892098500626e-16, -2.7755575615628914e-17), (0.0, 0.0, 0.0)], u'L_back_03_paw_tip_repose_01': [(-1.1102230246251565e-16, -2.220446049250313e-16, -2.220446049250313e-16), (6.386990832935119, 0.0, 0.0)], u'L_back_03_paw_tip_repose_02': [(-2.220446049250313e-16, 2.220446049250313e-16, -5.551115123125783e-17), (0.0, 0.0, 0.0)], u'L_back_02_paw_tip_repose_01': [(-5.551115123125783e-17, -2.220446049250313e-16, -1.1102230246251565e-16), (5.413616972292173, 0.0, 0.0)], u'R_back_01_paw_repose_02': [(-1.6653345369377304e-16, 0.012399452616682426, 0.023916066303957116), (8.745268706370622, 1.1490569381298708, 0.25559880120479817)], u'R_back_01_paw_repose_01': [(0.000793608305974121, 0.006126476687389892, 0.0673991702646063), (5.45307172675213, 2.455999905616432, -2.459398427155876)], u'R_back_04_paw_repose_02': [(-0.0, 2.220446049250313e-16, -0.0), (26.920798934191204, 0.18912781367453496, -9.991722081319375)], u'R_back_04_paw_repose_01': [(0.005781990701103826, 0.013297104705131796, 0.0472245465865173), (-4.6630998160922035, 0.58708644005176, -0.05107964967437411)], u'L_back_02_paw_tip_repose_02': [(-5.551115123125783e-17, 0.0, 1.1102230246251565e-16), (0.0, 0.0, 0.0)], u'L_back_04_paw_m_repose': [(0.0, -0.015671412661798403, -0.005049239035192867), (-11.111213810795794, 0.0, 0.0)], u'R_front_04_paw_repose_02': [(-1.1102230246251565e-16, 0.0, 0.0), (31.45003165815669, 0.0, 0.0)], u'R_front_03_paw_m_repose': [(-0.0, 0.015754025153279227, 0.013877062563831762), (-2.352798620518732, 1.9709621577935823, -0.08096525195247659)], u'R_front_04_paw_repose_01': [(0.0005048565778918252, -9.85836147931714e-06, -2.8960382337339208e-05), (-8.587930893575717, 2.6118366104548096, -2.0515204714445963)], u'L_back_01_paw_tip_repose_02': [(-8.326672684688674e-17, -2.220446049250313e-16, -5.551115123125783e-17), (0.0, 0.0, 0.0)], u'L_back_01_paw_tip_repose_01': [(8.326672684688674e-17, -2.220446049250313e-16, 1.1102230246251565e-16), (-0.971080037388014, 0.0, 0.0)], u'L_back_02_paw_tipSquash_repose': [(1.6653345369377526e-16, 0.023413521535050122, 0.008166820421889131), (-26.490158716849727, 0.0, 0.0)], u'R_back_02_paw_repose_01': [(0.00110746753419564, 0.0038072266376041374, 0.06831369111377282), (-3.223725632231791, -8.27448189384617, 1.2415597936629674)], u'R_back_02_paw_repose_02': [(2.7755575615628914e-17, 0.0, -2.7755575615628914e-17), (32.07478411561574, 0.0, 0.0)], u'R_front_01_paw_tipSquash_repose': [(1.1102230246251565e-16, 4.440892098500626e-16, -1.1102230246251565e-16), (0.0, 0.0, 0.0)], u'R_back_paw_repose_02': [(0.0, -0.0, -0.0), (-11.564794598410202, 0.0, 0.0)], u'R_back_paw_repose_01': [(0.0, -0.0, 0.0), (-13.180430584612095, 0.0, 0.0)], u'R_back_03_paw_tip_repose_02': [(2.220446049250313e-16, -2.220446049250313e-16, 5.551115123125783e-17), (0.0, 0.0, 0.0)], u'R_back_03_paw_tip_repose_01': [(1.1102230246251565e-16, 2.220446049250313e-16, 2.220446049250313e-16), (6.386990832935119, 0.0, 0.0)], u'R_front_01_paw_repose_02': [(0.00020415197743304972, 0.028066102810541334, 0.027426002642314175), (23.43353853635219, -6.578519078604302, 7.46874755571482)], u'R_front_01_paw_repose_01': [(-1.1102230246251686e-16, 0.0006147371539897535, 0.03355249641687895), (-8.963353430009663, 4.441780518975857, -1.0994633412575412)], u'R_front_01_paw_repose_m': [(-0.0, 0.04624060573919369, 0.031520311272999424), (0.0, 0.0, 0.0)], u'R_back_01_paw_repose_m': [(-5.551115123125783e-17, 0.015671412661798403, 0.005049239035192867), (-4.015031041666677, -9.135294558149344, 6.35156873650335)], u'R_front_02_paw_tip_repose_01': [(-0.0, 0.0, 0.0), (6.030337709215453, 0.0, 0.0)], u'R_front_03_paw_repose_01': [(-0.0, -0.0, 1.1102230246251565e-16), (-17.014593594320697, -1.074637086603781, -0.9285021158909341)], u'R_front_03_paw_repose_02': [(1.1102230246251565e-16, 0.0, 5.551115123125783e-17), (46.854034614596415, 0.0, 0.0)], u'R_back_04_paw_tipSquash_repose': [(0.0023507730452710417, -0.03130494589651657, 0.0058242886700340755), (-21.247061143788052, 0.0, 0.0)], u'L_back_03_paw_m_repose': [(0.0, -0.015671412588362105, -0.005049239263118436), (-11.111213810795794, 0.0, 0.0)], u'L_front_03_paw_repose_02': [(-1.1102230246251565e-16, 0.0, -5.551115123125783e-17), (46.854034614596415, 0.0, 0.0)], u'L_front_03_paw_repose_01': [(0.0, 0.0, -1.1102230246251565e-16), (-17.014593594320697, -1.074637086603781, -0.9285021158909341)], u'L_back_02_paw_repose_m': [(5.551115123125783e-17, -0.015671412661798403, -0.005049239035192867), (-11.111213810795794, 0.0, 0.0)], u'L_front_01_paw_repose_m': [(0.0, -0.04624060573919369, -0.031520311272999424), (0.0, 0.0, 0.0)], u'R_front_paw_repose_fk_03': [(1.1102230246251565e-16, 0.0, 6.938893903907228e-17), (-6.025506727442577, 0.0, 0.0)], u'R_front_paw_repose_fk_02': [(0.0, 2.220446049250313e-16, 5.551115123125783e-17), (-21.061298671120845, 0.0, 0.0)], u'R_front_paw_repose_fk_01': [(0.0, 0.0, 6.938893903907228e-18), (-0.6123583465156592, 0.0, 0.0)], u'L_front_02_paw_repose_m': [(0.0, -0.014350830767579127, -0.0008593638855518191), (-6.1522312073544505, 0.0, 0.0)], u'R_back_01_paw_tipSquash_repose': [(-0.0009450860539016194, -0.004826007127952428, -0.001377176521489428), (-13.928368134120422, 0.0, 0.0)], u'L_front_01_paw_tip_repose_02': [(0.0, -2.220446049250313e-16, -1.6653345369377348e-16), (0.0, 0.0, 0.0)], u'L_front_01_paw_tip_repose_01': [(0.0, 0.0, 0.0), (0.006490063098034895, 0.0, 0.0)], u'L_back_01_paw_tipSquash_repose': [(0.0009450860539016194, 0.004826007127952428, 0.001377176521489428), (-13.928368134120422, 0.0, 0.0)], u'L_back_01_paw_repose_01': [(-0.000793608305974121, -0.006126476687389892, -0.0673991702646063), (5.45307172675213, 2.4559999056164314, -2.459398427155876)], u'L_back_01_paw_repose_02': [(1.6653345369377304e-16, -0.012399452616682426, -0.023916066303957116), (8.745268706370622, 1.1490569381298708, 0.25559880120479817)], u'L_back_01_paw_repose_m': [(5.551115123125783e-17, -0.015671412661798403, -0.005049239035192867), (-4.015031041666677, -9.135294558149344, 6.35156873650335)], u'L_front_02_paw_tip_repose_01': [(0.0, 0.0, 0.0), (6.030337709215453, 0.0, 0.0)], u'R_back_02_paw_tipSquash_repose': [(-1.6653345369377526e-16, -0.023413521535050122, -0.008166820421889131), (-26.490158716849727, 0.0, 0.0)], u'R_back_04_paw_m_repose': [(0.0, 0.015671412661798403, 0.005049239035192867), (-11.111213810795794, 0.0, 0.0)], u'L_front_04_paw_tip_repose_02': [(-1.1102230246251565e-16, 4.440892098500626e-16, 2.7755575615628914e-17), (0.0, 0.0, 0.0)], u'L_front_04_paw_tip_repose_01': [(0.0, 0.0, 0.0), (-7.245890310999545, 0.0, 0.0)], u'R_front_04_paw_m_repose': [(-0.0, 0.015754025153279227, 0.013877062563831762), (0.0, 0.0, 0.0)], u'R_front_01_paw_tip_repose_01': [(0.0, -0.0, -0.0), (0.006490063098034895, 0.0, 0.0)], u'R_front_01_paw_tip_repose_02': [(-0.0, 2.220446049250313e-16, 1.6653345369377348e-16), (0.0, 0.0, 0.0)], u'R_front_02_paw_repose_m': [(-0.0, 0.014350830767579127, 0.0008593638855518191), (-6.1522312073544505, 0.0, 0.0)], u'L_front_03_paw_tip_repose_01': [(0.0, 0.0, -1.1102230246251565e-16), (-9.774782276411518, 0.0, 0.0)], u'L_front_02_paw_tip_repose_02': [(-1.1102230246251565e-16, 4.440892098500626e-16, -8.326672684688674e-17), (0.0, 0.0, 0.0)], u'L_front_03_paw_tip_repose_02': [(-1.1102230246251565e-16, -4.440892098500626e-16, -2.7755575615628914e-17), (0.0, 0.0, 0.0)], u'L_front_paw_repose_fk_01': [(0.0, 0.0, -6.938893903907228e-18), (-0.6123583465156592, 0.0, 0.0)], u'L_front_paw_repose_fk_03': [(-1.1102230246251565e-16, 0.0, -6.938893903907228e-17), (-6.025506727442577, 0.0, 0.0)], u'L_front_paw_repose_fk_02': [(0.0, -2.220446049250313e-16, -5.551115123125783e-17), (-21.061298671120845, 0.0, 0.0)], u'L_back_03_paw_tipSquash_repose': [(-2.2204460492502963e-16, 0.0069115976941169326, 0.007629144349090558), (-16.14110731208447, 0.0, 0.0)], u'R_front_02_paw_repose_01': [(-0.0001724089493585802, 0.018163882042368948, 0.06309008515807871), (-9.214024116352087, -3.5671655121773083, -0.2472910389020807)], u'R_front_02_paw_repose_02': [(-1.1102230246251565e-16, 4.440892098500626e-16, 1.1102230246251565e-16), (36.53542590439221, 0.0, 0.0)], u'R_back_03_paw_m_repose': [(0.0, 0.015671412588362105, 0.005049239263118436), (-11.111213810795794, 0.0, 0.0)], u'R_front_03_paw_tipSquash_repose': [(2.775557561562895e-16, -0.0011210918601354102, -0.005450498382932557), (-11.622847415353977, 0.0, 0.0)], u'L_front_03_paw_m_repose': [(0.0, -0.015754025153279227, -0.013877062563831762), (-2.352798620518732, 1.9709621577935823, -0.08096525195247659)], u'L_back_02_paw_repose_02': [(-2.7755575615628914e-17, 0.0, 2.7755575615628914e-17), (32.07478411561574, 0.0, 0.0)], u'L_front_02_paw_tipSquash_repose': [(3.3306690738754647e-16, 0.012063212324592062, 0.010632426472427785), (-28.494168907825543, 0.0, 0.0)], u'L_front_03_paw_tipSquash_repose': [(-2.775557561562895e-16, 0.0011210918601354102, 0.005450498382932557), (-11.622847415353977, 0.0, 0.0)], u'L_front_04_paw_repose_02': [(1.1102230246251565e-16, 0.0, 0.0), (31.45003165815669, 0.0, 0.0)], u'R_front_04_paw_tipSquash_repose': [(-0.001985158689634128, -0.021460092886801757, 0.01891139085751101), (-16.10338128982276, 0.0, 0.0)], u'R_front_02_paw_tipSquash_repose': [(-3.3306690738754647e-16, -0.012063212324592062, -0.010632426472427785), (-28.494168907825543, 0.0, 0.0)], u'L_back_04_paw_repose_01': [(-0.005781990701103826, -0.013297104705131796, -0.0472245465865173), (-4.6630998160922035, 0.58708644005176, -0.05107964967437411)], u'L_back_04_paw_repose_02': [(0.0, -2.220446049250313e-16, 0.0), (26.920798934191204, 0.18912781367453496, -9.991722081319375)], u'L_front_01_paw_tipSquash_repose': [(-1.1102230246251565e-16, -4.440892098500626e-16, 1.1102230246251565e-16), (0.0, 0.0, 0.0)], u'L_front_01_paw_repose_01': [(1.1102230246251686e-16, -0.0006147371539897535, -0.03355249641687895), (-8.963353430009663, 4.441780518975857, -1.0994633412575412)], u'L_front_01_paw_repose_02': [(-0.00020415197743304972, -0.028066102810541334, -0.027426002642314175), (23.43353853635219, -6.578519078604302, 7.46874755571482)], u'R_front_03_paw_tip_repose_02': [(1.1102230246251565e-16, 4.440892098500626e-16, 2.7755575615628914e-17), (0.0, 0.0, 0.0)], u'R_back_02_paw_repose_m': [(-5.551115123125783e-17, 0.015671412661798403, 0.005049239035192867), (-11.111213810795794, 0.0, 0.0)], u'R_front_03_paw_tip_repose_01': [(0.0, -0.0, 1.1102230246251565e-16), (-9.774782276411518, 0.0, 0.0)], u'R_back_01_paw_tip_repose_01': [(-8.326672684688674e-17, 2.220446049250313e-16, -1.1102230246251565e-16), (-0.971080037388014, 0.0, 0.0)], u'R_back_01_paw_tip_repose_02': [(8.326672684688674e-17, 2.220446049250313e-16, 5.551115123125783e-17), (0.0, 0.0, 0.0)], u'L_front_04_paw_repose_01': [(-0.0005048565778918252, 9.85836147931714e-06, 2.8960382337339208e-05), (-8.587930893575717, 2.6118366104548096, -2.0515204714445963)], u'L_back_02_paw_repose_01': [(-0.00110746753419564, -0.0038072266376041374, -0.06831369111377282), (-3.223725632231791, -8.27448189384617, 1.2415597936629674)], u'R_back_04_paw_tip_repose_01': [(-0.002740842211619208, 0.005928469615408057, 0.004919555039966667), (13.544535774603828, 0.0, 0.0)], u'L_front_04_paw_m_repose': [(0.0, -0.015754025153279227, -0.013877062563831762), (0.0, 0.0, 0.0)], u'R_back_04_paw_tip_repose_02': [(0.0, -0.0, -5.551115123125783e-17), (0.0, 0.0, 0.0)], u'L_back_03_paw_repose_02': [(-1.1102230246251565e-16, 2.220446049250313e-16, -2.220446049250313e-16), (28.705303401929662, 0.0, 0.0)], u'R_back_03_paw_repose_01': [(2.220446049250332e-16, 0.004284659806534137, 0.049720728806938605), (-4.25885451949169, -1.5069810901318477, 0.8842790743638299)], u'R_back_03_paw_repose_02': [(1.1102230246251565e-16, -2.220446049250313e-16, 2.220446049250313e-16), (28.705303401929662, 0.0, 0.0)], u'L_back_03_paw_repose_01': [(-2.220446049250332e-16, -0.004284659806534137, -0.049720728806938605), (-4.25885451949169, -1.5069810901318477, 0.8842790743638299)]}
    toesList =toesReplaceDict.keys()

    toesPlaceNode = 'traj'
    toesPlaceAttr = 'toesPlace'

    mc.addAttr( toesPlaceNode , ln = toesPlaceAttr , at = 'double' , min = 0 , max = 1 , dv = 0  )
    mc.setAttr('%s.%s' %(toesPlaceNode,toesPlaceAttr) , edit = True , k = True )  

    for toe in toesList:
        shapes.create( toe, shape= 'cube', size= 0.1, scale= [1, 1, 1 ], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= [0,1,0] , colorDegradeTo= None, replace= True, middle= False)    
        placeNode = orig.orig(objlist=[toe], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')[0]
        placeNode = mc.rename(placeNode,'%s_place' %toe )   
        
        toePB = mc.createNode('pairBlend' , n='%s_place_pb' %toe) 
        mc.connectAttr('%s.%s' %(toesPlaceNode,toesPlaceAttr),'%s.weight' %toePB )
        mc.setAttr('%s.rotInterpolation' %toePB , 1 )    
        
        transformValues = toesReplaceDict[toe]
        mc.setAttr('%s.inTranslate2' %toePB , transformValues[0][0],transformValues[0][1],transformValues[0][2] )
        mc.setAttr('%s.inRotate2' %toePB , transformValues[1][0],transformValues[1][1],transformValues[1][2] )
        mc.connectAttr('%s.outTranslate' %toePB , '%s.translate' %placeNode)
        mc.connectAttr('%s.outRotate' %toePB , '%s.rotate' %placeNode)        

    mc.setAttr('%s.%s' %(toesPlaceNode,toesPlaceAttr),1)
    ## --- constraint temporary toes to leg foot joints

    targetList = ['back_paw_repose_01_orig','back_paw_repose_02_orig','front_paw_repose_fk_01_orig','front_paw_repose_fk_02_orig','front_paw_repose_fk_03_orig']
    SKNList = ['back_foot_02_SKN','back_foot_03_SKN','front_foot_01','front_foot_02_SKN','front_foot_03_SKN']
    for side in sides:
        for k,each in enumerate(SKNList):
            cns = mc.parentConstraint('%s_%s' %(side,each) ,'%s_%s' %(side,targetList[k] ),mo=True)[0]
            print cns       
            mc.connectAttr('%s.%s' %(toesPlaceNode,toesPlaceAttr)  , '%s.target[0].targetWeight' %cns , force=True)
            
    mc.setAttr('%s.%s' %(toesPlaceNode,toesPlaceAttr),0)       

    

    # --- fix right fuckedUp tumbles
    bankSource = mc.listConnections('L_front_leg_rvfoot_heel_ctrl.rotateAxisX' , p = True , s = True )[0]
    mc.keyframe((bankSource.split('.',1)[0]), index = (0,0) ,absolute = True , valueChange = 1 )
    bankSource = mc.listConnections('L_front_leg_rvfoot_tip_ctrl.rotateAxisX' , p = True , s = True )[0]
    mc.keyframe((bankSource.split('.',1)[0]), index = (1,1) ,absolute = True , valueChange = -1 )
    bankSource = mc.listConnections('R_front_leg_rvfoot_heel_ctrl.rotateAxisX' , p = True , s = True )[0]
    mc.keyframe((bankSource.split('.',1)[0]), index = (0,0) ,absolute = True , valueChange = 1 )
    bankSource = mc.listConnections('R_front_leg_rvfoot_tip_ctrl.rotateAxisX' , p = True , s = True )[0]
    mc.keyframe((bankSource.split('.',1)[0]), index = (1,1) ,absolute = True , valueChange = -1 )


    Rbank01Source = mc.listConnections('R_front_leg_rvfoot_bank_01_ctrl.rotateAxisZ' , p = True , s = True )[0]
    Rbank02Source = mc.listConnections('R_front_leg_rvfoot_bank_02_ctrl.rotateAxisZ' , p = True , s = True )[0]   
    mc.connectAttr(Rbank02Source,'R_front_leg_rvfoot_bank_01_ctrl.rotateAxisZ' , f = True )
    mc.connectAttr(Rbank01Source,'R_front_leg_rvfoot_bank_02_ctrl.rotateAxisZ' , f = True )
    mc.keyframe((Rbank01Source.split('.',1)[0]), index = (1,1) ,absolute = True , valueChange = -1 )
    mc.keyframe((Rbank02Source.split('.',1)[0]), index = (0,0) ,absolute = True , valueChange = 1 )

    Rbank01Source = mc.listConnections('R_back_leg_rvfoot_bank_01_ctrl.rotateAxisZ' , p = True , s = True )[0]
    Rbank02Source = mc.listConnections('R_back_leg_rvfoot_bank_02_ctrl.rotateAxisZ' , p = True , s = True )[0]   
    mc.connectAttr(Rbank02Source,'R_back_leg_rvfoot_bank_01_ctrl.rotateAxisZ' , f = True )
    mc.connectAttr(Rbank01Source,'R_back_leg_rvfoot_bank_02_ctrl.rotateAxisZ' , f = True )
    mc.keyframe((Rbank01Source.split('.',1)[0]), index = (1,1) ,absolute = True , valueChange = -1 )
    mc.keyframe((Rbank02Source.split('.',1)[0]), index = (0,0) ,absolute = True , valueChange = 1 )

    ###############################################################################################################################################3
    # --- ears smart Rig
    smartParentTarget = 'head_gimbal_ctrl'
    smartDupTargets = ['L_ear_fk_ctrl_01_orig','R_ear_fk_ctrl_01_orig']
    earsNoXformGrp = 'ears_ctrl_noXformGrp'        
    ## --- create noXform Grp for ears
    mc.group(n=earsNoXformGrp,em=True)
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






    #------------------------------------------------------------------------------------------------------------------- add group inside hips, pointConstrained to centerSpine end anchorJoint  (make that inside smart groups and connect to actual group in rig
    #--------------------------------------------------------------------------------------------------------------------add ik offset to L/R_hip_ctrl_01
    
    #--------------------------------------------------------------------------------------------------------------------add L/R_scapula_ctrl_01 IK offset   
    #--------------------------------------------------------------------------------------------------------------------add L/R_scapula_root_ctrl_01  
    
    #---------------------------------------------------------------------------------------------------------------------readjust legs guides (back misoriented for optimal behavior)  
    
    #--------------------------------------------------------------------------------------------------------------------- add toes parented inside legs joints
    #--------------------------------------------------------------------------------------------------------------------- give them a TposeOffset group with a switch to go to toes TPose to paws pose
    #---------------------------------------------------------------------------------------------------------------------fixs ALL feets tumble -_-' again
    
    #--------------------------------------------------------------------------------------------------------------------adjuste neck rig Position
    #--------------------------------------------------------------------------------------------------------------------add volumeSurface to neck
    # make NECK volumeDeform RIG --MANUAL--
    # check xrivets settings on neck
    
    #--------------------------------------------------------------------------------------------------------------------- adjust ears FKRig
    #---------------------------------------------------------------------------------------------------------------------- add orientation currentSpace on ears joint 2, to have them follow head instead of joint 01
    #-------------------------------------------------------------------------------------------------------------------- add volumeSurface on ears
    #----------------------------------------------------------------------------------------------------------------------check first ear orientation
    # add localRig for ears
    # make EARS volumeDeform RIG --MANUAL--
    #--------------------------------------------------------------------------------------------------------------------- add ears ik offsets


    #---HELPERS---#
    # add earsRoot Helper, parented inside head, pointConstrained on ears joint2 base
    # add scapula offset helper, same as earsRoot
    # add scapulaTip Helper, same as earsRoot
    # add backLegs root helpers, same as earsRoot
    # same on foot_02 , for paw push/pull
    
    # add compressor helpers :
    #       on legs flaps
    #       on backLegs , from mid of each leg segment    
    #---HELPERS---#

    # add collar Rig --MANUAL--
    
    
    # shapes and visClean Pass

    
    
    
















    # rough cleanup
    hideList = ['leg_rvfoot_ik_ball_02_ikh','fullLeg_ikh','leg_rvfoot_ik_ball_01_ikh','fullLeg_01']
    for toHide in hideList :
        mc.hide('%s_%s_%s' %(side,intFixes[1],toHide))

