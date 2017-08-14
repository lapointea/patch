import maya.cmds as mc
import marsCore.shapes.defs as shapes
reload(shapes)
import marsCore.orig as orig
from marsAutoRig_stubby.patch.customLib import patchLib as patchLib
reload(patchLib)
from marsAutoRig_stubby.patch.customLib import rotateOrderLib as roLib
reload(roLib)

#def patchLib.resetTransform(trgt):
#def patchLib.locksSwitch(sel,T=True,R=True,S=True,V=True,lockdo='unlock',keydo=False)
#def patchLib.getRelatives(side,ctrlBase,digit)
#orig.orig(objlist=[], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')
#shapes.create( sel, shape= 'circle', size= 1, scale= [1, 1, 1 ], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= None, colorDegradeTo= None, replace= True, middle= False)
#updateRotateOrder(xyz=[], yzx=[], zxy=[], xzy=[], yxz=[], zyx=[] )

def patch():
        
    pelvName = 'pelvis'
    clavName= 'clavicle'
    armRootOff = 'arm_root_offset'
    legRootOffName = 'leg_root_offset'
    armIK = 'arm_IK'
    legIK = 'leg_IK'
    armFK = 'arm'
    legFK = 'leg'  
    footFK = 'foot'      
    wristFK = 'wrist'
    root = 'root'
    rootGimbal = 'root_gimbal'
    head = 'head'
    headGimbal = 'head_gimbal'
    ikFKSwitchTgt = 'arm_ik_tgt'
    neckIKTipAdjust = 'neck_ik_tip_adjust'
    headRotProxyOrig = 'headRotProxy_orig'
    headProxyRot = 'headRotProxy'
    ribCage2 = 'ribCage_bend_ctrl_02'
    
    palmCtrlName = 'hand_palm_ctrl'
    middleCtrlName = 'middle_01'

    sides = ['L','R']

    ###Fix Axises and rotate Orders############################################################

    #reorient translate R clavicle
    rClavRelatives = patchLib.getRelatives(sides[1],clavName,1)
    mc.parent(rClavRelatives[3] , w = True )
    mc.setAttr('%s.scale' % rClavRelatives[1] , -1,-1,-1 )
    mc.parent(rClavRelatives[3] , rClavRelatives[2] )
    #reorient R arm root offset
    rArmRootOfftRelatives = patchLib.getRelatives(sides[1],armRootOff,'')
    mc.parent(rArmRootOfftRelatives[3] , w = True )
    mc.setAttr('%s.scale' % rArmRootOfftRelatives[1] , -1,-1,-1 )
    mc.setAttr('%s.jointOrientX' % rArmRootOfftRelatives[1] , 0 )
    mc.parent(rArmRootOfftRelatives[3] , rArmRootOfftRelatives[2] )
    #reorient R ik Hand
    rArmIKRelatives = patchLib.getRelatives(sides[1],armIK,'')
    for rel in rArmIKRelatives[3] :
        patchLib.locksSwitch(rel,T=True,R=True,S=True,V=False,lockdo='unlock',keydo=False)
    mc.parent(rArmIKRelatives[3] , w = True )
    mc.setAttr('%s.jointOrientX' % rArmIKRelatives[0] , 90 )
    mc.setAttr('%s.jointOrientY' % rArmIKRelatives[0] , -90 )    
    mc.parent(rArmIKRelatives[3] , rArmIKRelatives[2] )
    for rel in rArmIKRelatives[3] :
        patchLib.locksSwitch(rel,T=True,R=True,S=True,V=False,lockdo='lock',keydo=False)
    ##reorient IKFK switch target
    mc.setAttr('%s_%s.rotate' %(sides[1],ikFKSwitchTgt) , l=False )
    mc.setAttr('%s_%s.rotateY' %(sides[1],ikFKSwitchTgt) , -180 )
    mc.setAttr('%s_%s.rotate' %(sides[1],ikFKSwitchTgt) , l=True )
    
    #reorient et hide Attr legs root offset
    llegRootOffRelatives = patchLib.getRelatives(sides[0],legRootOffName,'')
    mc.parent( llegRootOffRelatives[3] , w = True )
    mc.setAttr('%s.rotateX' % llegRootOffRelatives[1] , 0 )
    mc.parent( llegRootOffRelatives[3] , llegRootOffRelatives[2])

    rlegRootOffRelatives = patchLib.getRelatives(sides[1],legRootOffName,'')
    RLegProxyScaleGrp = '%s_%s_scaleProxy' % (sides[1],legRootOffName)
    mc.group( n = RLegProxyScaleGrp , em = True )
    mc.parent( RLegProxyScaleGrp , rlegRootOffRelatives[0] , r = True )
    mc.parent( rlegRootOffRelatives[3] , RLegProxyScaleGrp )    
    mc.parent( RLegProxyScaleGrp , w = True )
    mc.setAttr('%s.scale' % rlegRootOffRelatives[1] , -1,-1,-1 )
    mc.parent( RLegProxyScaleGrp , rlegRootOffRelatives[2] )

    
    mc.setAttr('L_leg_root_offset_ctrl.scaleX' , k = False , l = True )
    mc.setAttr('L_leg_root_offset_ctrl.scaleY' , k = False , l = True )
    mc.setAttr('L_leg_root_offset_ctrl.scaleZ' , k = False , l = True )
    mc.setAttr('R_leg_root_offset_ctrl.scaleX' , k = False , l = True )
    mc.setAttr('R_leg_root_offset_ctrl.scaleY' , k = False , l = True )
    mc.setAttr('R_leg_root_offset_ctrl.scaleZ' , k = False , l = True )
    
    #connects feets rotateOrder to feets_SKN rotateORders
    for side in sides:
        for i in range(1,3):
            mc.connectAttr('%s_%s_%02d.rotateOrder' %(side,footFK,i),'%s_%s_%02d_SKN.rotateOrder' %(side,footFK,i),f=True)
    #################################################################################################
    # --- add leg ground IK ctrls on top of actual leg Iks
    for side in sides :
        
        if side == 'L' :
            ctrlcolor = 6
        elif side == 'R' :
            ctrlcolor = 13  
        mc.select(cl=True)                  
        newCtrl = mc.joint(n = '%s_%s_ground_ctrl' % (side,legIK) )
        mc.setAttr('%s.drawStyle' % newCtrl , 2 )
        shapes.create( newCtrl, shape= 'square', size= 2, scale= [1, 1, 2 ], axis= 'y', twist= 0, offset= [0, 0, 1 ], color= ctrlcolor, colorDegradeTo= None, replace= True, middle= False)
        newCtrlOrig = orig.orig(objlist=[newCtrl], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')[0]
        mc.parent(newCtrlOrig,'%s_%s_rvfoot_heel_ctrl' % (side,legFK) )
        mc.setAttr('%s.translate' % newCtrlOrig , 0,0,0)
        mc.parent(newCtrlOrig,'traj')
        mc.parent('%s_%s_ctrl_orig' % (side,legIK),newCtrl)   
        mc.sets( newCtrl , add = '%s_%s_anim_set' % (side,legFK) )
        mc.sets( newCtrl , add = '%s_%s_ZS_set' % (side,legFK) )
        mc.connectAttr('%s_leg_SW_ctrl.fkIk' %side,'%s.visibility' %newCtrl)

    # --- fix right fuckedUp bank
    Rbank01Source = mc.listConnections('%s_%s_rvfoot_bank_01_ctrl.rotateAxisZ' %(sides[1],legFK) , p = True , s = True )[0]
    Rbank02Source = mc.listConnections('%s_%s_rvfoot_bank_02_ctrl.rotateAxisZ' %(sides[1],legFK) , p = True , s = True )[0]   
    mc.connectAttr(Rbank02Source,'%s_%s_rvfoot_bank_01_ctrl.rotateAxisZ' %(sides[1],legFK) , f = True )
    mc.connectAttr(Rbank01Source,'%s_%s_rvfoot_bank_02_ctrl.rotateAxisZ' %(sides[1],legFK) , f = True )
    mc.keyframe((Rbank01Source.split('.',1)[0]), index = (1,1) ,absolute = True , valueChange = -1 )
    mc.keyframe((Rbank02Source.split('.',1)[0]), index = (0,0) ,absolute = True , valueChange = 1 )

     
    #################################################################################################
    
    #reparent armTwist reader rig to avoid flips when FKarm currentSpace not in restPose
    twistTrgtList = ['twist','twist_aimdir']
    for side in sides :
        parentTrgt = mc.listRelatives('%s_%s_01_orig' % (side,armFK) , p = True)
        for twist in twistTrgtList:
            twistname = '%s_%s_01_%s' % (side,armFK,twist)
            patchLib.locksSwitch(twistname,T=True,R=True,S=True,V=True,lockdo='unlock',keydo=False)
            mc.parent(twistname,parentTrgt)
            patchLib.locksSwitch(twistname,T=True,R=False,S=True,V=True,lockdo='lock',keydo=False)
    ##################################################################################################

    # --- readjust Palm Controls
    JOSettings = [(-180,0,90),(0,0,-90)]

    for side in sides:
        palmCtrl = '%s_%s' %(side,palmCtrlName)
        palmOrig = mc.listRelatives(palmCtrl,p=True)[0]

        # get constraints from palmCtrl, its targets and the blend settings, then remove constraints
        outCns = mc.listConnections('%s.parentMatrix[0]' %palmCtrl )    
        cnsTargets = []
        for cns in outCns:
            target = mc.listConnections('%s.constraintTranslateX' %cns)[0]
            blend0 = mc.getAttr('%s.target[0].targetWeight' %cns )
            blend1 = mc.getAttr('%s.target[1].targetWeight' %cns )
            cnsTargets.append((target,(blend0,blend1)))
            mc.delete(cns)

        # realigns the palm ctrl orig
        palmOrigParent = mc.listRelatives(palmOrig,p=True)[0]
        mc.parent(palmOrig,w=True)
        mc.setAttr('%s.jointOrient' %palmOrig , JOSettings[0][0],JOSettings[0][1],JOSettings[0][2] )
        
        alignPos = mc.xform('%s_%s' %(side,middleCtrlName) ,q=True, t=True, ws=True )
        mc.setAttr('%s.translateY' %palmOrig , alignPos[1])
        mc.setAttr('%s.translateZ' %palmOrig , alignPos[2])
        mc.parent(palmOrig,palmOrigParent)
        
        #reconstraint Targets to palmCtrl   
        for each in cnsTargets:
            target = each[0]
            blends = each[1]
            newCns = mc.parentConstraint(palmOrig,palmCtrl,target,mo=True)[0]
            
            blend0 = mc.listConnections('%s.target[0].targetWeight' %newCns , p=True)[0]
            blend1 = mc.listConnections('%s.target[1].targetWeight' %newCns , p=True)[0]
            mc.setAttr(blend0,blends[0])
            mc.setAttr(blend1,blends[1]) 


    #neckTwist#######################################   
    attrName = 'neckTwistFollow'
    neckFollowMdl = '%s_mdl' % attrName
    
    mc.group( n = headRotProxyOrig , em = True )
    mc.group( n = headProxyRot , em = True )
    mc.parent( headProxyRot , headRotProxyOrig )
    mc.parent( headRotProxyOrig , '%s_orig' % neckIKTipAdjust , r = True )
    getRO = mc.getAttr('%s.jointOrient' % neckIKTipAdjust)[0]
    mc.setAttr( '%s.rotateAxis' % headRotProxyOrig , getRO[0] , getRO[1] , getRO[2])
    mc.setAttr('%s.rotateOrder' % neckIKTipAdjust , 2 )
    mc.setAttr('%s.rotateOrder' % headProxyRot , 2 )
    mc.orientConstraint( 'head_gimbal_ctrl' , headProxyRot , mo =True )
    # --- adds blendattribute for neckTwist on head   
    mc.addAttr( '%s_ctrl' % head , ln = attrName , at = 'double' , min = 0 , max = 1 , dv = 1  )
    mc.setAttr('%s_ctrl.%s' %(head,attrName) , edit = True , k = True )
    mc.createNode('multDoubleLinear' ,n = neckFollowMdl )
    mc.connectAttr( '%s.rotateY' % headProxyRot , '%s.input1' % neckFollowMdl , f = True)
    mc.connectAttr( '%s_ctrl.%s' %(head,attrName)  , '%s.input2' % neckFollowMdl , f = True)     
    
    mc.connectAttr( '%s.output' % neckFollowMdl , '%s.rotateY' % neckIKTipAdjust )
    #neckTwist#######################################
    
    #reparent last neck deform#######################
    lastNeckDeform = mc.ls('neck_ctrl_deform_*_orig')[-1]
    mc.parent( lastNeckDeform , neckIKTipAdjust )
    
    # ---  add head_hook for later facial parenting
    headHook = 'head_hook'
    mc.group(n=headHook , em=True)
    mc.parent(headHook , '%s_ctrl' %headGimbal , r=True)

    # --- add breathCtrl
    breathingCtrl = 'breathing_ctrl'
    mc.select(cl=True)
    mc.joint(n=breathingCtrl)
    shapes.create( breathingCtrl, shape= 'arrowTwo',  size= 0.5, scale= [1, 1, 1 ], axis= 'z', twist= 0, offset= [0, 0, 0 ], color= [1,0.5,0.3], colorDegradeTo= None, replace= True, middle= False)
    mc.setAttr('%s.drawStyle' %breathingCtrl , 2 )
    breathingOrig = orig.orig(objlist=[breathingCtrl], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')[0]
    mc.parent(breathingOrig,ribCage2,r=True)
    mc.setAttr('%s.jointOrient' %breathingOrig , 0,0,0)
    mc.setAttr('%s.translate' %breathingOrig , 0,0,1)
    mc.sets(breathingCtrl, add = 'spine_ctrl_anim_set')
    mc.sets(breathingCtrl, add = 'spine_ctrl_ZS_set')
    ## set locks and limits
    mc.setAttr('%s.translateX' %breathingCtrl , l=True , k=False)
    mc.setAttr('%s.translateY' %breathingCtrl , l=True, k=False) 
    mc.setAttr('%s.rotateX' %breathingCtrl , l=True, k=False) 
    mc.setAttr('%s.rotateY' %breathingCtrl , l=True, k=False)    
    mc.setAttr('%s.rotateZ' %breathingCtrl , l=True, k=False)    
    mc.setAttr('%s.scaleX' %breathingCtrl , l=True, k=False) 
    mc.setAttr('%s.scaleY' %breathingCtrl , l=True, k=False)    
    mc.setAttr('%s.scaleZ' %breathingCtrl , l=True, k=False)
    mc.transformLimits(breathingCtrl , etz = (True,True), tz=(-1.5,1.5))
                         
    # --- expose and tweak missing rotate Orders ---
    ctrlList = mc.listConnections('?_hand_fk_set.dagSetMembers')
    ctrlList.append(mc.listConnections('L_hand_anim_set.dagSetMembers')[0])
    ctrlList.append(mc.listConnections('R_hand_anim_set.dagSetMembers')[0])
    ctrlList.append('L_leg_01')
    ctrlList.append('R_leg_01')
    
    xyzRoList = []
    yzxRoList = []
    zxyRoList = ctrlList
    xzyRoList = ['head_ctrl','head_gimbal_ctrl','root_ctrl','root_gimbal_ctrl','pelvis_ctrl','spine_mid_ctrl','spine_tip_ctrl','spine_tip_adjust_ctrl',
                 'L_arm_IK_ctrl','R_arm_IK_ctrl','L_wrist','R_wrist','L_wrist_offset','R_wrist_offset',
                 'L_leg_IK_ctrl','R_leg_IK_ctrl','L_leg_IK_ground_ctrl','R_leg_IK_ground_ctrl','L_leg_root_offset_ctrl','R_leg_root_offset_ctrl']
    yxzRoList = ['L_leg_02','R_leg_02','L_arm_02','R_arm_02']
    zyxRoList = ['L_foot_01','R_foot_01','L_foot_02','R_foot_02','L_arm_01','R_arm_01']
        
    roLib.updateRotateOrder(xyz=xyzRoList, yzx=yzxRoList, zxy=zxyRoList, xzy=xzyRoList, yxz=yxzRoList, zyx=zyxRoList )          
   
   
   
test = mc.listConnections('?_hand_anim_set.dagSetMembers')