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
        # rough cleanup
        hideList = ['leg_rvfoot_ik_ball_02_ikh','fullLeg_ikh','leg_rvfoot_ik_ball_01_ikh','fullLeg_01']
        for toHide in hideList :
            mc.hide('%s_%s_%s' %(side,intFixes[1],toHide))

