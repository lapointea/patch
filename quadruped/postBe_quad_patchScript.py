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

    #fix jaw skinSet Temp
    mc.sets( ['jaw_SKN','lipsUp_SKN'] , add = 'jaw_root_jnt_skin_set' )

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


    #connects pelvis_ctrl translate to hips_adjust_ik_ctrl_orig
    mc.connectAttr('%s.translate' % pelvisCtrl , '%s.translate' % hipIkAdjustCtrl , f = True )
    #connects  and blend pelvis_ctrl rotate to hips_adjust_ik_ctrl_orig
    AttrName = 'hipAdjustRotateFollow'
    hipFollowMD = '%s_MD' % AttrName

    mc.addAttr( pelvisCtrl , ln = AttrName , at = 'double' , min = 0 , max = 1 , dv = 0  )
    mc.setAttr('%s.%s' %(pelvisCtrl,AttrName) , edit = True , k = True )

    mc.createNode('multiplyDivide' , n = hipFollowMD )
    mc.connectAttr( '%s.rotateX' % pelvisCtrl , '%s.input1X' % hipFollowMD , f = True )
    mc.connectAttr( '%s.rotateY' % pelvisCtrl , '%s.input1Y' % hipFollowMD , f = True )
    mc.connectAttr( '%s.rotateZ' % pelvisCtrl , '%s.input1Z' % hipFollowMD , f = True )
    mc.connectAttr('%s.%s' %(pelvisCtrl,AttrName) , '%s.input2X' % hipFollowMD , f = True )
    mc.connectAttr('%s.%s' %(pelvisCtrl,AttrName) , '%s.input2Y' % hipFollowMD , f = True )
    mc.connectAttr('%s.%s' %(pelvisCtrl,AttrName) , '%s.input2Z' % hipFollowMD , f = True )
    mc.connectAttr( '%s.outputX' % hipFollowMD , '%s.rotateX' % hipIkAdjustCtrl , f = True )
    mc.connectAttr( '%s.outputY' % hipFollowMD , '%s.rotateY' % hipIkAdjustCtrl , f = True )
    mc.connectAttr( '%s.outputZ' % hipFollowMD , '%s.rotateZ' % hipIkAdjustCtrl , f = True )

    #constraints chest_adjust_ctrl to 'neck_ik_root' while ommiting rotation first then add rotation blend
    mc.parentConstraint( chestAddjustCtrl , neckIkbase , mo = True , sr = ['x','y','z'] )
    #constraints chest_adjust_ctrl to chest_adjust_ik_ctrl while ommiting rotation first then add rotation blend
    mc.parentConstraint( chestAddjustCtrl , chestAdjustIKCtrlOrig , mo = True , sr = ['x','y','z'] )

    chestAdjustOrigHold = '%s_hold' % chestAdjustIKCtrlOrig
    chestAdjustFollowREV = '%s_follow_REV' % chestAdjustIKCtrlOrig
    chestAdjustOrigParent = mc.listRelatives( chestAdjustIKCtrlOrig , p=True)[0]

    mc.group(n = chestAdjustOrigHold , em = True )
    mc.parent( chestAdjustOrigHold , chestAdjustOrigParent , r =True )
    chestAdjustOrigOrientCns = mc.orientConstraint( chestAddjustCtrl , chestAdjustOrigHold , chestAdjustIKCtrlOrig , mo = True )[0]

    AttrName = '%sFollow' % chestAddjustCtrl
    mc.addAttr( chestAddjustCtrl , ln = AttrName , at = 'double' , min = 0 , max = 1 , dv = 1  )
    mc.setAttr('%s.%s' %(chestAddjustCtrl,AttrName) , edit = True , k = True )

    mc.createNode('reverse' , n = chestAdjustFollowREV )
    mc.connectAttr( '%s.%s' %(chestAddjustCtrl,AttrName), '%s.inputX' % chestAdjustFollowREV , f = True )
    mc.connectAttr('%s.%s' %(chestAddjustCtrl,AttrName) ,  '%s.target[0].targetWeight' % chestAdjustOrigOrientCns , f = True )
    mc.connectAttr('%s.outputX' % chestAdjustFollowREV ,  '%s.target[1].targetWeight' % chestAdjustOrigOrientCns , f = True )

    #####TEMP fix spine deform ORientation -- HARDCODED
    adRotList = ['spine_ctrl_deform_01_origAdditiveRotation','spine_ctrl_deform_02_origAdditiveRotation','spine_ctrl_deform_03_origAdditiveRotation']
    for adRot in adRotList :
        mc.setAttr('%s.inputBZ' % adRot , -90 )

    ################################################################################################################################################
    # adds missing ctrl to animSet,rempve unwanted ones, temp Hardcoded
    adCtrlList = ['jaw_ctrl','mouthSquash_ctrl','lipsUp_ctrl']

    mc.sets(adCtrlList , add = 'jaw_root_jnt_fk_set' )
    mc.sets(adCtrlList , add = 'jaw_root_jnt_ZS_set' )

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

    # temp previz cleanup
    neckIkRoot = 'neck_ik_root'
    chestRootCtrl = 'chest_root_ctrl'
    neckTipAdjustCtrl = 'neck_tip_adjust_ik_ctrl'

    # temp Attributes set
    mc.setAttr('%s.stretch' % neckIkRoot , 0 )
    mc.setAttr('%s.squash' % neckIkRoot , 0 )
    mc.setAttr('%s.tweakVis' % neckIkRoot , 0 )
    mc.setAttr('%s.stretch' % chestRootCtrl , 0 )
    mc.setAttr('%s.squash' % chestRootCtrl , 0 )
    mc.setAttr('%s.tweakVis' % chestRootCtrl , 0 )

    # hide ctrls and shapes - temp Hardcoded
    hideList = ['neck_tip_ik_ctrlShape','jaw_root_ctrlShape','neck_base_ik_ctrlShape','chest_adjust_ik_ctrlShape',
                'chest_root_ctrlShape','hips_adjust_ik_ctrlShape','spine_ctrl_01Shape','spine_ctrl_02Shape','spine_ctrl_03Shape']
    for each in hideList : mc.hide(each)

    # lock/hide channels
    mc.setAttr( '%s.rotateY' % neckTipAdjustCtrl , l = True , k = False )
