import maya.cmds as mc
import marsCore.shapes.defs as shapes
reload(shapes)
import marsCore.orig as orig
from marsAutoRig_stubby.patch.customLib import patchLib as patchLib
reload(patchLib)
from marsAutoRig_stubby.patch.customLib import removeFromSets as remSet
reload(remSet)
from marsAutoRig_stubby.patch.customLib import massConnectVis as massVis
reload(massVis)
from marsAutoRig_stubby.visSets import templateBiped_visSets as bipedVisSets
reload(bipedVisSets)

#def patchLib.resetTransform(trgt):
#def patchLib.locksSwitch(sel,T=True,R=True,S=True,V=True,lockdo='unlock',keydo=False)
#def patchLib.getRelatives(side,ctrlBase,digit)
#orig.orig(objlist=[], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')
#shapes.create( sel, shape= 'circle', size= 1, scale= [1, 1, 1 ], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= None, colorDegradeTo= None, replace= True, middle= False)

def patch():

    ############################################################################################## 
    #BEHAVIORS
    ############################################################################################## 
       
    spineTipAdjustCtrl = 'spine_tip_adjust_ctrl'    
    spineTipCtrl = 'spine_tip_ctrl'  
    spineMidCtrl = 'spine_mid_ctrl'  
    spineBaseCtrl = 'spine_base_ctrl'

    hipRootCtrl = 'hip_root_ctrl'
    rootGimbal = 'root_gimbal_ctrl'

    headGimbal = 'head_gimbal_ctrl'
    headSquash = 'head_squasher_ctrl'
      
    ribCageBendOrigName = 'ribCage_bend_ctrl_01_orig'
    ribCageOrigName = 'ribCage_01_orig'
    breathCtrl = 'breathing_ctrl'

    neckIkRoot = 'neck_ik_root'
    neckIkBase = 'neck_ik_base'
    neckTipAdjust = 'neck_ik_tip_adjust'
    neckTip = 'neck_ik_tip'
    neckEnd = 'neck_ctrl_end'
    neckIkMid = 'neck_ik_mid'

    helpersList = mc.ls('?_pectoral_ctrl','?_dorsal_ctrl','?_clavicleBone_ctrl','?_trapezius_ctrl','?_mastoid_ctrl')

    LarmRootOffset = 'L_arm_root_offset_ctrl'
    RarmRootOffset = 'R_arm_root_offset_ctrl'
    LwristOffset = 'L_wrist_offset'
    RwristOffset = 'R_wrist_offset'

    LLegRootOffset = 'L_leg_root_offset_ctrl'
    RLegRootOffset = 'R_leg_root_offset_ctrl'
    LankleIk = 'L_leg_IK_ctrl'
    RankleIk = 'R_leg_IK_ctrl'
    LgroundIk = 'L_leg_IK_ground_ctrl'
    RgroundIk = 'R_leg_IK_ground_ctrl'
    LStompCtrl = 'L_leg_scl_ctrl'
    RStompCtrl = 'R_leg_scl_ctrl'
    LtumbleCtrl = 'L_leg_tumble_ctrl'
    RtumbleCtrl = 'R_leg_tumble_ctrl'
    LfootTipCtrl = 'L_leg_rvfoot_tip_ctrl'
    RfootTipCtrl = 'R_leg_rvfoot_tip_ctrl'
    LfootHeelCtrl = 'L_leg_rvfoot_heel_ctrl'
    RfootHeelCtrl = 'R_leg_rvfoot_heel_ctrl'
    LfootSpinCtrl = 'L_leg_rvfoot_spin_ctrl'
    RfootSpinCtrl = 'R_leg_rvfoot_spin_ctrl'
    LToesCtrl = 'L_leg_rvfoot_toes_ctrl'
    RToesCtrl = 'R_leg_rvfoot_toes_ctrl'
    LBallCtrl = 'L_leg_rvfoot_ball_ctrl'
    RBallCtrl = 'R_leg_rvfoot_ball_ctrl'

    jawRoot='jawRoot_ctrl'
    LFootScale = 'L_leg_scl_ctrl'
    RFootScale = 'R_leg_scl_ctrl'
    hand = 'hand'
    palm = 'palm'
    lookat = 'aim_lookat'
    lookatMinor = 'lookat'
    sides = ['L','R']

    ############################################################################################## 
    #Alter top Ik behavior to give scale tangent control
   
    SpineDeformOrigs = mc.ls('spine_ctrl_deform_*_orig')
    lastSpineDeformOrig = 'spine_ctrl_deform_%02d_orig' % (len(SpineDeformOrigs)-1)
    
    ribCageOrig = mc.duplicate(spineTipAdjustCtrl, po = True )[0]
    mc.rename( ribCageOrig , ribCageOrigName )
    
    mc.parent(ribCageBendOrigName,ribCageOrigName)
    
    mc.connectAttr( '%s.translate' % spineTipAdjustCtrl, '%s.translate' % ribCageOrigName )
    mc.connectAttr( '%s.rotate' % spineTipAdjustCtrl, '%s.rotate' % ribCageOrigName )
    
    #adds connection to last spine deform
    mc.connectAttr( '%s.translate' % spineTipAdjustCtrl, '%s.translate' % lastSpineDeformOrig )
    mc.connectAttr( '%s.rotate' % spineTipAdjustCtrl, '%s.rotate' % lastSpineDeformOrig )
    mc.connectAttr( '%s.rotateOrder' % spineTipAdjustCtrl, '%s.rotateOrder' % lastSpineDeformOrig )    
    mc.sets(ribCageOrigName , rm = 'spine_ctrl_skin_set')
    # --- add transform blend on spine tip adjust connection to smartJoints
    ikRotateAttrName = 'IK_RotateBlend'
    ikTipAdjustRotateMD = 'spine_tip_adjust_rotate_MD'    
    smartJntTgt = ['spine_tip_adjust_ctrl_spine_ctrlsurfNurbsSmart','spine_tip_adjust_ctrl_spine_ctrlsurfNurbs_ikMiddleSmart']
    
    mc.addAttr( spineTipAdjustCtrl , ln = ikRotateAttrName , at = 'double' , min = 0 , max = 1 , dv = 1 )
    mc.setAttr('%s.%s' %(spineTipAdjustCtrl,ikRotateAttrName) , edit = True , k = True )
    mc.createNode('multiplyDivide' , n = ikTipAdjustRotateMD)
    mc.connectAttr('%s.rotate' % spineTipAdjustCtrl , '%s.input1' % ikTipAdjustRotateMD )
    mc.connectAttr('%s.%s' %(spineTipAdjustCtrl,ikRotateAttrName) , '%s.input2X' % ikTipAdjustRotateMD )    
    mc.connectAttr('%s.%s' %(spineTipAdjustCtrl,ikRotateAttrName) , '%s.input2Y' % ikTipAdjustRotateMD )    
    mc.connectAttr('%s.%s' %(spineTipAdjustCtrl,ikRotateAttrName) , '%s.input2Z' % ikTipAdjustRotateMD )
    
    for jnt in smartJntTgt:
        mc.connectAttr('%s.output' % ikTipAdjustRotateMD , '%s.rotate' % jnt , force = True )
    ############################################################################################## 
    #add base spine follow Rig and Switch
    ##add switch on pelvis
    pelvisCtrl = 'pelvis_ctrl'
    AttrName = 'baseSpineFollow'
    mc.addAttr( pelvisCtrl , ln = AttrName , at = 'double' ,  min = 0 , max = 1 , dv = 1 )
    mc.setAttr('%s.%s' %(pelvisCtrl,AttrName) , edit = True , k = True )
    ## add orient constraints and hold groups
    IKOrig = 'spine_base_ctrl'
    IKHold = '%s_holdGrp' % IKOrig
    mc.group(n = IKHold , em = True )
    mc.parent(IKHold , pelvisCtrl , r = True )
    mc.parent(IKHold , (mc.listRelatives(IKOrig,p = True)) )
    IKOrientCns = mc.orientConstraint(pelvisCtrl,IKHold,IKOrig,mo=True)[0]
    IKPointCns = mc.pointConstraint(pelvisCtrl,IKOrig,mo=True)
    ## add nodes rig and connects to constraints
    baseSpaineFolloeRv = mc.createNode('reverse',n='%s_rv' %AttrName )
    mc.connectAttr('%s.%s' %(pelvisCtrl,AttrName) , '%s.target[0].targetWeight' %IKOrientCns,f=True)   
    mc.connectAttr('%s.%s' %(pelvisCtrl,AttrName) , '%s.inputX' %baseSpaineFolloeRv)   
    mc.connectAttr('%s.outputX' %baseSpaineFolloeRv , '%s.target[1].targetWeight' %IKOrientCns,f=True) 

    ############################################################################################## 

    ############################################################################################## 
    #neck mid surf reweight to linear#############################################################
    partName = 'neck'
    patchLib.linearWeightsOnSurf('%s_ctrlsurfNurbs_ikMiddle' % partName ,'v',False)
    #spine mid surf reweight to linear#############################################################
    partName = 'spine'
    patchLib.linearWeightsOnSurf('%s_ctrlsurfNurbs_ikMiddle' % partName ,'v',False)
    #switch spine XRivets to V as the main direction
    midXrivetName = 'spine_ctrlsurfNurbs_ikMiddle_xRivetNurbs'
    lastXrivetName = 'spine_ctrl_surface_xRivetNurbs'
    deformList = mc.ls('spine_ctrl_deform_*_orig')   
    mc.setAttr('%s.xRivetDatas[0].mainDirection' % midXrivetName , 0 )
    for i in range(0,len(deformList)):
        mc.setAttr('%s.xRivetDatas[%d].mainDirection' %(lastXrivetName,i) , 1 )
    ############################################################################################## 
   
    #cleanup###############################################################################


        
    ##############################################################################################     
    remSetCtrlList = ['L_leg_rvfoot_toes_end_ctrl','R_leg_rvfoot_toes_end_ctrl',ribCageOrigName,spineBaseCtrl,neckIkBase,neckTip,neckTipAdjust,neckEnd]
                
    remSet.removeFromAllSets(remSetList=remSetCtrlList)
    
    ##############################################################################################     

    #lookat
    lookatoffsetOrig = '%s_ctrlOffset_orig' % lookat
    lookatSubOrig = '%s_ctrlSub_orig' % lookat
    subCns = mc.listConnections('%s.translateX' % lookatoffsetOrig, s=True)[0]
    if subCns:mc.delete(subCns,lookatSubOrig)
    mc.deleteAttr('%s_ctrl.subCtrlSwitch' % lookat )
    
    for side in sides:
        eyeLookAt = '%s_%s_ctrl' %(side,lookatMinor)
        eyeLookatShape = mc.listRelatives(eyeLookAt,s=True)
        for shape in eyeLookatShape:
              mc.connectAttr('%s_ctrl.subCtrlVis' % lookat , '%s.visibility' %shape , f=True)

    lookatOrient = '%s_ctrlOrient' % lookat    
    patchLib.locksSwitch(lookatOrient,T=True,R=False,S=True,V=False,lockdo='lock',keydo=False)
     
     
    #metacarpus
    for side in sides:
        mc.setAttr('%s_%s_%s_ctrl.metaViz' %(side,hand,palm) , 1 )
        mc.setAttr('%s_%s_%s_ctrl.metaViz' %(side,hand,palm) , l = True , k = False ,cb = False )
        
    #spine
    patchLib.locksSwitch(hipRootCtrl,T=True,R=True,S=True,V=True,lockdo='lock',keydo=False)
    mc.setAttr('%s.rotateOrder' %hipRootCtrl , k=False,cb=False)
    mc.setAttr('%s.stretch' % hipRootCtrl , 0 )
    mc.setAttr('%s.squash' % hipRootCtrl , 0 )
    mc.setAttr('%s.tweakVis' % hipRootCtrl , 0 )
    spineBaseShape = mc.listRelatives(spineBaseCtrl,s=True)[0]
    mc.setAttr('%s.visibility' % spineBaseShape , 0 )
    #neck
    patchLib.locksSwitch(neckIkRoot,T=True,R=True,S=True,V=True,lockdo='lock',keydo=False)
    mc.setAttr('%s.rotateOrder' %neckIkRoot , k=False,cb=False)
    mc.setAttr('%s.stretch' % neckIkRoot , 0 )
    mc.setAttr('%s.squash' % neckIkRoot , 0 )
    mc.setAttr('%s.tweakVis' % neckIkRoot , 0 )
    neckBaseShape = mc.listRelatives(neckIkBase,s=True)[0]
    mc.setAttr('%s.visibility' % neckBaseShape , 0 )
    
    patchLib.locksSwitch(neckTip,T=False,R=False,S=False,V=True,lockdo='unlock',keydo=False)
    mc.disconnectAttr('%s.ikCtrlVis' %neckIkRoot ,'%s.visibility' %neckTip )
    mc.setAttr('%s.visibility' %neckTip , 0 )
    patchLib.locksSwitch(neckTip,T=False,R=False,S=False,V=True,lockdo='lock',keydo=False)   

    mc.setAttr('%s.rotateY' %neckTipAdjust , k=False,cb=False,l=True)
    
    mc.setAttr('%s.visibility' % neckEnd , 0 )
    patchLib.locksSwitch(neckEnd,T=False,R=False,S=False,V=True,lockdo='lock',keydo=False)
    
    # --- visibility switches --------------------------------------------------------------------

    #cleanup base vis connections
    massVis.disconnectVisAttr(ctrl=neckIkRoot,attr='ikCtrlVis')
    massVis.disconnectVisAttr(ctrl=hipRootCtrl,attr='ikCtrlVis')
    
    # create visibility Sets
    visSetsDict = bipedVisSets.createVisSets()
    massVis.massCreateVisSets(visSetsDict)
     
    
