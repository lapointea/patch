import maya.cmds as mc
import marsCore.shapes.defs as shapes
reload(shapes)
import marsCore.orig as orig
from marsAutoRig_stubby.patch.customLib import patchLib as patchLib
import marsCore.foundations.curveLib as curveLib
import marsCore.foundations.dagLib as dag

from marsAutoRig_stubby.patch.dog import dogLegsTopIKs_generate as dogLegsTopIKs
reload(dogLegsTopIKs)
from marsAutoRig_stubby.patch.dog import dogToes_generate as dogToes
reload(dogToes)
from marsAutoRig_stubby.patch.dog import quad_volumeSpine_generate as volumeSpine
reload(volumeSpine)
from marsAutoRig_stubby.patch.dog import quad_volumeEars_generate as volumeEars
reload(volumeEars)
from marsAutoRig_stubby.patch.customLib import rotateOrderLib as roLib


#def patchLib.resetTransform(trgt):
#def patchLib.locksSwitch(sel,T=True,R=True,S=True,V=True,lockdo='unlock',keydo=False)
#def patchLib.getRelatives(side,ctrlBase,digit)
#orig.orig(objlist=[], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')
#shapes.create( sel, shape= 'circle', size= 1, scale= [1, 1, 1 ], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= None, colorDegradeTo= None, replace= True, middle= False)

def scaleOpositCtrl(name):
    objOrig = mc.listRelatives(name , p=True)[0]
    origParent = mc.listRelatives(objOrig , p=True)[0]
    childs = mc.listRelatives(name , c=True)
    unparentedChilds = []
    if childs:
        for child in childs:
            if not mc.objectType(child) == 'nurbsCurve' :
                mc.parent(child,w=True)
                unparentedChilds.append(child)
    mc.parent(objOrig,w=True)
    mc.setAttr('{}.rotate'.format(objOrig), 0,0,0 )
    mc.setAttr('{}.scaleX'.format(objOrig), -1 )
    mc.parent(objOrig, origParent)
    if unparentedChilds:
        for child in unparentedChilds:
            scaleTampon = orig.orig(objlist=[child], suffix=['_scale'], origtype='transform', fromsel=False, viz=False, get_ssc=False, rtyp='auto')
            mc.parent( scaleTampon, name )


def patch():
            
    #vars#########################################################################################
    sides = ['L','R']
    intFixes = ['front','back']
    fullLegDuplicate = ['leg_01','leg_02','foot_01','foot_02']
    headGimbal = 'head_gimbal'
    chestAdjust = 'chest_adjust_ctrl'
    autoSourceBaseName = 'leg_foot_ball_01_ctrl_orig'
    ##############################################################################################
        
    # --- reorient legs offsets for better symmetrical behavior
    for side in sides[1]:
        baseName = 'leg_root_offset_ctrl'
        for fix in intFixes:
            name = '{}_{}_{}'.format(side,fix,baseName)
            scaleOpositCtrl(name)              
    for side in sides[1]:
        baseNameList = ['scapula_ctrl', 'hip_ctrl' ]
        for baseName in baseNameList:
            name = '{}_{}'.format(side,baseName)
            scaleOpositCtrl(name)

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
 

    # --- change parenting of scapulas and leg_root_offsets to avoid unwanted scale and reconstraint to maintain behavior
    bodyGimball = 'body_gimbal_ctrl'
    hips = 'hips_ctrl'
    chest = 'chest_ctrl'
    chestOffset = 'chest_offset_ctrl'
    pelvisOrig = 'pelvis_ctrl_orig'
    chestTangentOrig = 'chest_tan_ik_ctrl_ik_pivot_ctrl_orig'
    neckBaseIk = 'neck_base_ik_ctrl'
    legRootOffset = 'back_leg_root_offset_ctrl'
    
    scapulasJointsOrig = ['L_scapula_ctrl_orig','R_scapula_ctrl_orig']
    legOffsetsOrig = ['L_back_leg_root_offset_ctrl_orig','R_back_leg_root_offset_ctrl_orig']
    
    scapulasOrig = 'scapulas_orig'
    legsOffsetsOrig = 'back_legs_offsets_orig'
    mc.group(n=scapulasOrig , em=True)
    mc.group(n=legsOffsetsOrig , em=True)
    mc.parent(scapulasOrig,chest,r=True)
    mc.parent(legsOffsetsOrig,hips,r=True)
    mc.parent(scapulasOrig,legsOffsetsOrig,bodyGimball)
    mc.parentConstraint(chest,scapulasOrig,mo=True)
    mc.parentConstraint(hips,legsOffsetsOrig,mo=True)
    mc.parent(scapulasJointsOrig,scapulasOrig)
    mc.parent(legOffsetsOrig,legsOffsetsOrig)
    
    # --- reparent all leg joints in lag back offsets
    for side in sides :
        mc.parent('{}_back_leg_01_fullLeg_orig'.format(side), '{}_{}'.format(side,legRootOffset) )
        
    
    # --- disconnect inversScale from perlvis orig
    mc.disconnectAttr('{}.scale'.format(hips), '{}.inverseScale'.format(pelvisOrig) )   
    
    # --- create Auto locators for source of legs automation
    for side in sides:
        for fix in intFixes:

            autoSourceName = '{}_{}_{}'.format(side,fix,autoSourceBaseName)
            sourcePos = mc.xform(autoSourceName, q=True, ws=True, t=True)
            autoLoc = mc.spaceLocator(n=autoSourceName.replace('orig','autoLoc') )[0]
            mc.xform(autoLoc, ws=True, t=sourcePos)
            mc.parent(autoLoc,autoSourceName)
            mc.hide(autoLoc)
            
    # --- build top legs iks and leg automation Rigs
    dogLegsTopIKs.buildLegsTopIks(sides,intFixes,chestAdjust)
    dogLegsTopIKs.buildLegsAutomation(sides,intFixes)
    
    # --- build toes additional rigs
    baseNameToes = 'toes'
    branchesToes = ['pinkyToe','ringToe','middleToe','bigToe']
    
    dogToes.buildToes(sides,intFixes,baseNameToes,branchesToes)
    
    # --- build volumeSpine
    volumeSpine.makeSpine(chest,hips,bodyGimball)
    
    # --- build ears
    smartParentTarget = 'head_gimbal_ctrl'
    smartDupTargets = ['L_ear_fk_ctrl_01_orig','R_ear_fk_ctrl_01_orig']
       
    volumeEars.makeVolumeEars(smartParentTarget,smartDupTargets,side,sides)
    
    # --- reparent toes in toesBase
    for side in sides:
        for fix in intFixes:
            toesBase = '{}_{}_toes_base_ctrl'.format(side,fix)
            toesJnt = '{}_{}_toes'.format(side,fix)
            toesChilds = mc.listRelatives(toesJnt, c=True, type = 'joint')
            mc.parent(toesBase,toesJnt)
            for child in toesChilds:                
                mc.parent(child,toesBase)
                mc.disconnectAttr('{}.scale'.format(toesBase), '{}.inverseScale'.format(child) )
    
    # --- patch spine to add chest_offset_ctrl
    ## reparent chest tangent control
    mc.parent(chestTangentOrig,chestOffset)
    mc.disconnectAttr('{}.scale'.format(chest), '{}.inverseScale'.format(mc.listRelatives(chestOffset,p=True)[0]))
    ## add chestOffset transforms to chest smart joint
    chestSmartJoint = '{}_surfNurbs_ikMiddleSmart'.format(chest)
    ### create pma nodes and connest transforms from chest and chest offset to it
    chestSmartSumTra = mc.createNode('plusMinusAverage', n= '{}_tra_sum_pma'.format(chestSmartJoint) )
    chestSmartSumRot = mc.createNode('plusMinusAverage', n= '{}_rot_sum_pma'.format(chestSmartJoint) )
    chestSmartSumSca = mc.createNode('plusMinusAverage', n= '{}_sca_sum_pma'.format(chestSmartJoint) )
    chestSmartNormSca = mc.createNode('multiplyDivide', n= '{}_sca)norm_md'.format(chestSmartJoint) )
    
    mc.connectAttr('{}.translate'.format(chest), '{}.input3D[0]'.format(chestSmartSumTra) )
    mc.connectAttr('{}.translate'.format(chestOffset), '{}.input3D[1]'.format(chestSmartSumTra) )
    mc.connectAttr('{}.rotate'.format(chest), '{}.input3D[0]'.format(chestSmartSumRot) )
    mc.connectAttr('{}.rotate'.format(chestOffset), '{}.input3D[1]'.format(chestSmartSumRot) )
    mc.connectAttr('{}.scale'.format(chest), '{}.input3D[0]'.format(chestSmartSumSca) )
    mc.connectAttr('{}.scale'.format(chestOffset), '{}.input3D[1]'.format(chestSmartSumSca) )
    mc.connectAttr('{}.output3D'.format(chestSmartSumSca), '{}.input1'.format(chestSmartNormSca) )
    mc.setAttr('{}.input2'.format(chestSmartNormSca) , 0.5,0.5,0.5 )
    
    ### for connection of pmas to chest smart
    mc.connectAttr('{}.output3D'.format(chestSmartSumTra), '{}.translate'.format(chestSmartJoint), f=True )
    mc.connectAttr('{}.output3D'.format(chestSmartSumRot), '{}.rotate'.format(chestSmartJoint), f=True )
    mc.connectAttr('{}.output'.format(chestSmartNormSca), '{}.scale'.format(chestSmartJoint), f=True )   
    
    # --- patch neck rig to add autoOffset on neck_base_ik_ctrl and its smart ctrls
    addParentList = [neckBaseIk, '{}_necksurfNurbsSmart'.format(neckBaseIk), '{}_necksurfNurbs_ikMiddleSmart'.format(neckBaseIk) ]
    newParents = orig.orig(objlist=addParentList, suffix=['_auto'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')
    patchLib.smartConnect(newParents[0],newParents[1])
    patchLib.smartConnect(newParents[0],newParents[2])
    # --- make new nodes and connections to connect chestOffset to neckRig
    ## create matrixOffset node, place it and constrain it to chestOffset
    neckBaseIkMatrixOffset = mc.group(n= '{}_matrixOffset'.format(neckBaseIk), em=True)
    mc.parent(neckBaseIkMatrixOffset, mc.listRelatives(mc.listRelatives(neckBaseIk,p=True),p=True), r=True)
    chestOffsetPos = mc.xform(chestOffset, q=True, ws=True, t=True)
    mc.xform(neckBaseIkMatrixOffset, ws=True, t=chestOffsetPos)
    mc.parentConstraint(chestOffset, neckBaseIkMatrixOffset, mo=True)
    ## create matrix nodes and do connections to chestOffset
    chestOffsetMM = mc.createNode('multMatrix', n= '{}_toNeck_mm'.format(chestOffset) )
    chestOffsetDM = mc.createNode('decomposeMatrix', n= '{}_toNeck_dm'.format(chestOffset) )
    mc.connectAttr('{}.matrixSum'.format(chestOffsetMM), '{}.inputMatrix'.format(chestOffsetDM) )
    
    mc.connectAttr('{}.inverseMatrix'.format(neckBaseIkMatrixOffset), '{}.matrixIn[0]'.format(chestOffsetMM) )
    mc.connectAttr('{}.matrix'.format(chestOffset), '{}.matrixIn[1]'.format(chestOffsetMM) )
    mc.connectAttr('{}.matrix'.format(neckBaseIkMatrixOffset), '{}.matrixIn[2]'.format(chestOffsetMM) )
    mc.connectAttr('{}.outputTranslate'.format(chestOffsetDM), '{}.translate'.format(newParents[0]) )
    
    # --- reparent roots of Neck compressors into neckMid ctrl
    neckCompressorList = ['C_bottomNeck_base_orig','L_bottomNeck_base_orig','R_bottomNeck_base_orig',
                          'C_topNeck_base_orig','L_topNeck_base_orig','R_topNeck_base_orig']
    neckMidIk = 'neck_mid_ik_ctrl'
    mc.parent(neckCompressorList ,neckMidIk )
    # --- reparent tip of top neck compressors
    tipTopNeckCompBaseName = 'topNeck_tip'
    tipTopNeckTargetBaseName = 'reverse_scapula_root'
    for side in sides:
        mc.parent('{}_{}'.format(side,tipTopNeckCompBaseName), '{}_{}'.format(side,tipTopNeckTargetBaseName) )
    # --- flip neck compressors ctrl_origs to fix ctrl orientation
    for each in neckCompressorList:
        splitName = each.split('_',1)[0]
        if not splitName == 'R':
            origName = each.replace('base','ctrl')
            mc.setAttr('{}.jointOrientX'.format(origName), 180)
            
    # --- unlock translate on leg_mid_ctrls
    for side in sides:
        for fix in intFixes:
            node = '{}_{}_leg_mid_orig'.format(side,fix)
            newNodeName = mc.rename(node, node.replace('orig','ctrl_orig'))
            patchLib.locksSwitch(newNodeName,T=True,R=True,S=False,V=False,lockdo='unlock',keydo=False)

    # --- expose and tweak missing rotate Orders ---
    
    xyzRoList = []
    yzxRoList = []
    zxyRoList = []
    xzyRoList = ['head_ctrl','head_gimbal_ctrl','body_ctrl','body_gimbal_ctrl','chest_ctrl','chest_offset_ctrl','hips_ctrl','pelvis_ctrl',
                 'R_front_leg_IK_ctrl','R_front_leg_rvfoot_tip_ctrl','R_front_leg_rvfoot_heel_ctrl','L_front_leg_IK_ctrl','L_front_leg_rvfoot_tip_ctrl',
                 'L_front_leg_rvfoot_heel_ctrl','R_back_leg_IK_ctrl','R_back_leg_rvfoot_heel_ctrl','R_back_leg_rvfoot_tip_ctrl','L_back_leg_IK_ctrl',
                 'L_back_leg_rvfoot_tip_ctrl','L_back_leg_rvfoot_heel_ctrl','neck_mid_ik_ctrl','neck_base_ik_ctrl','neck_end', 'neck_02','neck_ik_root',
                 'chest_tan_ik_ctrl','chest_tan_ik_ctrl_center_ik_ctrl','spine_mid_ik_ctrl','spine_mid_ik_ctrl_center_ik_ctrl','hips_tan_ik_ctrl',
                 'hips_tan_ik_ctrl_center_ik_ctrl']
    yxzRoList = []
    zyxRoList = ['tail_root_fk_ctrl_01','tail_root_fk_ctrl_02','tail_fk_ctrl_01','tail_fk_ctrl_02','tail_fk_ctrl_03','Tail_offset_ctrl','tail_tip_ctrl']
        
    roLib.updateRotateOrder(xyz=xyzRoList, yzx=yzxRoList, zxy=zxyRoList, xzy=xzyRoList, yxz=yxzRoList, zyx=zyxRoList )
            
                       
    # ---  add head_hook for later facial parenting
    headHook = 'head_hook'
    mc.group(n=headHook , em=True)
    mc.parent(headHook , '%s_ctrl' %headGimbal , r=True)

    ####################################################################################################################################################
    
