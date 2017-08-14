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
    intFixes = ['front','back']
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
    headToNeckOrientCns = mc.orientConstraint(headGimbalCtrl,holdGrp,neckTipAdjust , mo = True , sk = ['x','y'] )[0]
    mc.createNode('reverse' , n = neckFollowRev )

    mc.connectAttr('%s.%s' %(headCtrl,AttrName), '%s.target[0].targetWeight' % headToNeckOrientCns , f = True )
    mc.connectAttr('%s.%s' %(headCtrl,AttrName), '%s.input.inputX' %  neckFollowRev , f = True )
    mc.connectAttr('%s.outputX' %  neckFollowRev, '%s.target[1].targetWeight' % headToNeckOrientCns , f = True )


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
    #cleanup ################################################################################################################################
    
    # --- remove unwanted nodes from sets  
    remSetList = ['head_gimbal_ctrl_smart','neck_01','neck_tip_adjust_ik_ctrl','neck_tip_ik_ctrl','neck_end','L_back_leg_rvfoot_spin_ctrl','L_front_leg_rvfoot_spin_ctrl',
                  'R_back_leg_rvfoot_spin_ctrl','R_front_leg_rvfoot_spin_ctrl','L_reverse_scapula_root']

    for obj in remSetList:
        if mc.objExists(obj) == True:
            getSets = mc.listSets(object = obj)
            if getSets:
                for set in getSets:
                    mc.sets(obj , rm = set)   

    # --- make main toes sets for a less messy main set
    for side in sides:
        for fix in intFixes:
            tips = mc.ls('{}_{}_*Toe_tip_ctrl'.format(side,fix), type = 'joint' )
            squashs = mc.ls('{}_{}_*Toe_squash_ctrl'.format(side,fix), type = 'joint' )
            nails = mc.ls('{}_{}_*Toe_nail_ctrl'.format(side,fix), type = 'joint' )
            cushion = '{}_{}_cushion_ctrl'.format(side,fix)
            
            mc.sets(cushion , add = '{}_{}_toes_anim_set'.format(side,fix) )
            mc.sets(cushion , add = '{}_{}_toes_ZS_set'.format(side,fix) )
            mc.sets(cushion , add = '{}_{}_toes_skin_set'.format(side,fix) )
            for each in tips:
                mc.sets(each , add = '{}_{}_toes_anim_set'.format(side,fix) )
                mc.sets(each , add = '{}_{}_toes_ZS_set'.format(side,fix) )
                mc.sets(each , add = '{}_{}_toes_skin_set'.format(side,fix) )
            for each in squashs:
                mc.sets(each , add = '{}_{}_toes_anim_set'.format(side,fix) )
                mc.sets(each , add = '{}_{}_toes_ZS_set'.format(side,fix) )
                mc.sets(each , add = '{}_{}_toes_skin_set'.format(side,fix) )
            for each in nails:
                mc.sets(each , add = '{}_{}_toes_anim_set'.format(side,fix) )
                mc.sets(each , add = '{}_{}_toes_ZS_set'.format(side,fix) )
                mc.sets(each , add = '{}_{}_toes_skin_set'.format(side,fix) ) 
        scapBase = '{}_scapula_base_sec_jnt_root'.format(side)
        revScap = '{}_reverse_scapula_sec_root'.format(side)
        sideHip = '{}_hip_sec_root'.format(side)
        mc.sets(scapBase , add = '{}_front_leg_skin_set'.format(side) )
        mc.sets(revScap , add = '{}_front_leg_skin_set'.format(side) )
        mc.sets(sideHip , add = '{}_back_leg_skin_set'.format(side) )

            
    
    neckIkRoot = 'neck_ik_root'
    # Attributes set
    mc.setAttr('%s.stretch' % neckIkRoot , 0 )
    mc.setAttr('%s.squash' % neckIkRoot , 0 )
    mc.setAttr('%s.tweakVis' % neckIkRoot , 0 )

    # hide ctrls and shapes - temp Hardcoded
    hideList = ['neck_tip_ik_ctrlShape','neck_tip_adjust_ik_ctrlShape','neck_01Shape']
    for each in hideList : mc.hide(each)
    
    ## --- set animation default values on legs automation
    
    '''
    frontLegFollowX = .25
    frontLegFollowY = .25
    frontLegFollowZ = .25
    frontLegPosXLimit = 1
    frontLegNegXLimit = 1
    frontLegPosYLimit = 1
    frontLegNegYLimit = 1
    frontLegPosZLimit = 1
    frontLegNegZLimit = 1
    scapulaFollowX = .25
    scapulaFollowY = .25
    scapulaFollowZ = .25
    frontAutoValuesList = [frontLegFollowX,frontLegFollowY,frontLegFollowZ,frontLegPosXLimit,frontLegNegXLimit,frontLegPosYLimit,frontLegNegYLimit,
                           frontLegPosZLimit,frontLegNegZLimit,scapulaFollowX,scapulaFollowY,scapulaFollowZ]
    frontAutoAttrList = ['xLegFollow','yLegFollow','zLegFollow','xPosLegLimit','xNegLegLimit','yPosLegLimit','yNegLegLimit','zPosLegLimit','zNegLegLimit',
                        'xScapulaFollow','yScapulaFollow','zScapulaFollow']
      
    backLegFollowX = .25
    backLegFollowY = .25
    backLegFollowZ = .25
    backLegPosXLimit = 1
    backLegNegXLimit = 1
    backLegPosYLimit = 1
    backLegNegYLimit = 1
    backLegPosZLimit = 1
    backLegNegZLimit = 1
    backAutoValuesList = [backLegFollowX,backLegFollowY,backLegFollowZ,backLegPosXLimit,backLegNegXLimit,backLegPosYLimit,backLegNegYLimit,backLegPosZLimit,backLegNegZLimit]
    backAutoAttrList = ['xLegFollow','yLegFollow','zLegFollow','xPosLegLimit','xNegLegLimit','yPosLegLimit','yNegLegLimit','zPosLegLimit','zNegLegLimit']
    
    swName = 'SW_ctrl'
    
    for side in sides:
        for f, fix in intFixes:
            if fix == 'front':
                for i, each in frontAutoValuesList:
                    mc.addAttr('{}_{}_leg_{}.{}'.format(side,fix,swName,frontAutoAttrList[i]), e=True, dv= frontAutoValuesList )
            if fix == 'back':
                for i, each in backAutoValuesList:
                    mc.addAttr('{}_{}_leg_{}.{}'.format(side,fix,swName,backAutoAttrList[i]), e=True, dv= backAutoValuesList )
    
    '''
    
    
    
    
    
    

    # lock/hide channels

