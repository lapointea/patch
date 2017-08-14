import maya.cmds as mc
import marsCore.shapes.defs as shapes
reload(shapes)
import marsCore.orig as orig
from marsAutoRig_stubby.patch.customLib import patchLib as patchLib

#def patchLib.resetTransform(trgt):
#def patchLib.locksSwitch(sel,T=True,R=True,S=True,V=True,lockdo='unlock',keydo=False)
#def patchLib.getRelatives(side,ctrlBase,digit)
#orig.orig(objlist=[], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')
#shapes.create( sel, shape= 'circle', size= 1, scale= [1, 1, 1 ], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= None, colorDegradeTo= None, replace= True, middle= False)

def patch():

    sides = ['L','R']
    pelvisCtrl = 'pelvis_ctrl'
    hipIkAdjustCtrl = 'hips_adjust_ik_ctrl_orig'
    chestAddjustCtrl = 'chest_adjust_ctrl'
    chestAdjustIKCtrlOrig = 'chest_adjust_ik_ctrl_orig'
    neckIkbase = 'neck_base_ik_ctrl'
    neckFk = 'neck_01'
    neckTipAdjust = 'neck_tip_adjust_ik_ctrl'
    neckTip = 'neck_tip_ik_ctrl'
    headCtrl = 'head_ctrl'
    headGimbalCtrl = 'head_gimbal_ctrl'

    #constraints neck_tip_adjust_ik_ctrl rotZ to headGimbalCtrl rot Z and adds blend
    AttrName = 'neckFollow'
    neckFollowRev = '%s_Rev' % AttrName
    holdGrp ='neck_tip_adjust_ik_ctrl_hold' 
    holdGrpOrig ='neck_tip_adjust_ik_ctrl_hold_orig' 

    mc.group( n = holdGrp , em = True )
    holdGrpOrig = orig.orig(objlist=[holdGrp], suffix=['_orig'], origtype='transform', fromsel=False, viz=False, get_ssc=False, rtyp='auto')[0]
    mc.parent(holdGrpOrig,(mc.listRelatives(neckTipAdjust , p= True )) , r = True )

    mc.addAttr( headCtrl , ln = AttrName , at = 'double' , min = 0 , max = 1 , dv = 0  )
    mc.setAttr('%s.%s' %(headCtrl,AttrName) , edit = True , k = True )
    headToNeckOrientCns = mc.orientConstraint(headGimbalCtrl,holdGrp,neckTipAdjust , mo = True , sk = ['x','z'] )[0]
    mc.createNode('reverse' , n = neckFollowRev )

    mc.connectAttr('%s.%s' %(headCtrl,AttrName), '%s.target[0].targetWeight' % headToNeckOrientCns , f = True )
    mc.connectAttr('%s.%s' %(headCtrl,AttrName), '%s.input.inputX' %  neckFollowRev , f = True )
    mc.connectAttr('%s.outputX' %  neckFollowRev, '%s.target[1].targetWeight' % headToNeckOrientCns , f = True )

    ######################################################################################################################################################################################
    ######################################################################################################################################################################################
    #TEASER DIRTY WORK START##############################################################################################################################################################
    ######################################################################################################################################################################################
    ######################################################################################################################################################################################

    # --- anchor pelvisPosition to last centerSpine anchor position

    mainHips = 'hips_ctrl'
    pelvisCtrl = 'pelvis_ctrl'
    maxLengthAttr = 'maxLengthBlend'

    hipsSmart = 'hips_body_gimbal_ctrl_surfNurbs_SmartJointsGrp'
    lastAnchor = 'spine_anchor_06_jnt'
    pelvisAnchorGrpSmart = 'pelvis_spineAnchor_grp_smart'
    pelvisAnchorGrp = 'pelvis_spineAnchor_grp'
    
    pelvisAnchorJnt = 'pelvis_spineAnchor_jnt_smart'

    mc.group(n=pelvisAnchorGrpSmart,em=True)
    mc.parent(pelvisAnchorGrpSmart,hipsSmart)
    mc.parentConstraint(lastAnchor,pelvisAnchorGrpSmart)

    mc.group(n=pelvisAnchorGrp,em=True)
    mc.parent(pelvisAnchorGrp,pelvisAnchorGrpSmart,r=True)
    mc.parent(pelvisAnchorGrp,mainHips)
    orig.orig(objlist=[pelvisAnchorGrp,pelvisAnchorGrpSmart], suffix=['_orig'], origtype='transform', fromsel=False, viz=False, get_ssc=False, rtyp='auto')
    mc.select(clear=True)
    
    pelvisAnchorPB = mc.createNode('pairBlend' , n='%s_pb' %pelvisAnchorGrp )
    mc.setAttr('%s.rotInterpolation' %pelvisAnchorPB , 1 )
    mc.connectAttr('%s.translate' %pelvisAnchorGrpSmart , '%s.inTranslate2' %pelvisAnchorPB)
    mc.connectAttr('%s.rotate' %pelvisAnchorGrpSmart , '%s.inRotate2' %pelvisAnchorPB)
    mc.connectAttr('%s.%s' %(mainHips,maxLengthAttr) , '%s.weight' %pelvisAnchorPB )
    mc.connectAttr('%s.outTranslate' %pelvisAnchorPB , '%s.translate' %pelvisAnchorGrp)
    mc.connectAttr('%s.outRotate' %pelvisAnchorPB , '%s.rotate' %pelvisAnchorGrp)

    mc.parent(mc.listRelatives(pelvisCtrl,p=True)[0],pelvisAnchorGrp)

    # --- add smart pelvisJoint parented into maxLenghts stuff
    mc.joint(n=pelvisAnchorJnt)
    mc.parent(pelvisAnchorJnt,pelvisAnchorGrpSmart,r=True)
    mc.setAttr('%s.radius' %pelvisAnchorJnt , 0.5 )
    mc.hide(pelvisAnchorJnt)

    # --- constraint sides helpers
    HelpFrontTrgt = ['spine_deform_U10_V02_ctrl','spine_deform_U04_V02_ctrl']   
    HelpBackTrgt = ['spine_deform_U10_V04_ctrl','spine_deform_U04_V04_ctrl']  

    frontHelperName = 'HELPER_frontLeg_sides_SKN_tip'
    backHelperName = 'HELPER_backLeg_flap_SKN_tip'

    for s , side in enumerate(sides):
        mc.pointConstraint( HelpFrontTrgt[s], '%s_%s' %(side,frontHelperName) )
        mc.pointConstraint( HelpBackTrgt[s], '%s_%s' %(side,backHelperName) )



    ################################################################################################################################################
    # adds missing ctrl to animSet,rempve unwanted ones, temp Hardcoded
    adCtrlList = ['mouthSquash_ctrl','lipsUp_ctrl']

    mc.sets([u'R_front_leg_rvfoot_toes_end_ctrl'] , rm = 'R_front_leg_ik_set' )
    mc.sets([u'R_front_leg_rvfoot_toes_end_ctrl'] , rm = 'R_front_leg_ZS_set' )

    mc.sets([u'R_back_leg_rvfoot_ik_ball_02_jnt', u'R_back_leg_ik_rvfoot_ball_01_joint', u'R_back_leg_rvfoot_toes_end_ctrl'] , rm = 'R_back_leg_ik_set' )
    mc.sets([u'R_back_leg_rvfoot_ik_ball_02_jnt', u'R_back_leg_ik_rvfoot_ball_01_joint', u'R_back_leg_rvfoot_toes_end_ctrl'] , rm = 'R_back_leg_ZS_set' )

    mc.sets([u'R_back_fullLeg_01', u'R_back_fullLeg_02', u'R_back_fullLeg_03', u'R_back_fullLeg_04'] , rm = 'R_back_leg_fk_set' )
    mc.sets([u'R_back_fullLeg_01', u'R_back_fullLeg_02', u'R_back_fullLeg_03', u'R_back_fullLeg_04'] , rm = 'R_back_leg_ZS_set' )

    mc.sets([u'L_front_leg_rvfoot_toes_end_ctrl'] , rm = 'L_front_leg_ik_set' )
    mc.sets([u'L_front_leg_rvfoot_toes_end_ctrl'] , rm = 'L_front_leg_ZS_set' )

    mc.sets([u'L_back_leg_rvfoot_toes_end_ctrl', u'L_back_leg_ik_rvfoot_ball_01_joint', u'L_back_leg_rvfoot_ik_ball_02_jnt'] , rm = 'L_back_leg_ik_set' )
    mc.sets([u'L_back_leg_rvfoot_toes_end_ctrl', u'L_back_leg_ik_rvfoot_ball_01_joint', u'L_back_leg_rvfoot_ik_ball_02_jnt'] , rm = 'L_back_leg_ZS_set' )

    mc.sets([u'L_back_fullLeg_01', u'L_back_fullLeg_02', u'L_back_fullLeg_03', u'L_back_fullLeg_04'] , rm = 'L_back_leg_fk_set' )
    mc.sets([u'L_back_fullLeg_01', u'L_back_fullLeg_02', u'L_back_fullLeg_03', u'L_back_fullLeg_04'] , rm = 'L_back_leg_ZS_set' )

    ################################################################################################################################################
    #previz cleanup ################################################################################################################################
    
    ##############################################################################################     
    remSetList = ['L_scapula_ik_jnt_01','L_scapula_root_ik_jnt_01','R_hip_ik_jnt_01','R_scapula_ik_jnt_01','R_scapula_root_ik_jnt_01','L_hip_ik_jnt_01','head_gimbal_ctrl_smart',]

    for obj in remSetList:
        getSets = mc.listSets(object = obj)
        if getSets:
            for set in getSets:
                mc.sets(obj , rm = set)   
    ##############################################################################################  

    # temp previz cleanup
    neckIkRoot = 'neck_ik_root'

    # temp Attributes set
    mc.setAttr('%s.stretch' % neckIkRoot , 0 )
    mc.setAttr('%s.squash' % neckIkRoot , 0 )
    mc.setAttr('%s.tweakVis' % neckIkRoot , 0 )

    # hide ctrls and shapes - temp Hardcoded
    hideList = ['neck_tip_ik_ctrlShape','neck_base_ik_ctrlShape']
    for each in hideList : mc.hide(each)

    # lock/hide channels
    #mc.setAttr( '%s.rotateY' % neckTipAdjustCtrl , l = True , k = False )
