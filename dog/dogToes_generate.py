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


def buildToes(sides,intFixes,baseName,branches):

    #sides = ['L','R']
    #intFixes = ['front','back']
    #baseName = 'toes'
    #branches = ['pinkyToe','ringToe','middleToe','bigToe']
    baseRgb = [[0,0,1],[1,0,0]]
    darkRgb = [[0,0,.8],[.8,0,0]]
    lightRgb = [[.5,.5,1],[1,.5,.5]]

    for fix in intFixes:
        for s, side in enumerate(sides) :
            # toes All control
            ## get average toes world pos
            worldPosList = []
            for branch in branches :
                tipPos = mc.xform('{}_{}_{}_IK_ctrl'.format(side,fix,branch), q=True, ws= True, t=True)
                worldPosList.append(tipPos)
            worldPosListLen = len(worldPosList)
            worldPosSum = [0,0,0]
            for i in range (0,worldPosListLen):
                worldPosSum[0] += worldPosList[i][0]
                worldPosSum[1] += worldPosList[i][1]
                worldPosSum[2] += worldPosList[i][2]  
            worldPosAverage = [ worldPosSum[0]/worldPosListLen , worldPosSum[1]/worldPosListLen , worldPosSum[2]/worldPosListLen ]
            ## create toes All Ctrl
            toesAllCtrl = mc.group(n='{}_{}_toes_all_IK_ctrl'.format(side,fix), em=True)
            mc.setAttr('{}.translate'.format(toesAllCtrl), worldPosAverage[0], worldPosAverage[1], worldPosAverage[2] )
            mc.parent(toesAllCtrl, '{}_{}_foot_03_SKN'.format(side,fix) )
            mc.setAttr('{}.translateX'.format(toesAllCtrl), 0 )
            shapes.create( toesAllCtrl, shape= 'square', size= 1, scale= [.55, .2, .4], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= lightRgb[s], colorDegradeTo= None, replace= True, middle= False)
            orig.orig(objlist=[toesAllCtrl], suffix=['_orig'], origtype='transform', fromsel=False, viz=False, get_ssc=False, rtyp='auto')

            # reparent and constraint main toes grp
            mc.parent('{}_{}_toes'.format(side,fix), '{}_{}_leg_scl'.format(side,fix))
            mc.parentConstraint('{}_{}_foot_02_SKN'.format(side,fix), '{}_{}_toes'.format(side,fix), mo=True )   
                 
            # reparent cushion joint
            mc.parent('{}_{}_cushion_ctrl_orig'.format(side,fix), '{}_{}_leg_scl'.format(side,fix))
            mc.disconnectAttr('{}_{}_leg_scl.scale'.format(side,fix), '{}_{}_cushion_ctrl_orig.inverseScale'.format(side,fix) )

            for branch in branches :
                # reparent toes hierarchy
                mc.parent('{}_{}_{}_IK_ctrl_orig'.format(side,fix,branch), toesAllCtrl)   
                      
                # reparent toes tips in toes end joints
                mc.parent('{}_{}_{}_tip_ctrl_orig'.format(side,fix,branch), '{}_{}_{}_end'.format(side,fix,branch) )
                
                # reparent ik poleVectors in ik ctrl origs
                mc.parent('{}_{}_{}_PV_ctrl_orig'.format(side,fix,branch), '{}_{}_{}_IK_ctrl_orig'.format(side,fix,branch) )

                # add upVectors visSwitch
                attrNode = '{}_{}_{}_IK_ctrl'.format(side,fix,branch)
                AttrName = 'showUpV'
                mc.addAttr( attrNode , ln = AttrName , at = 'bool' , dv = 0  )
                mc.setAttr('{}.{}'.format(attrNode,AttrName) , edit = True , k = True )              
                mc.connectAttr('{}.{}'.format(attrNode,AttrName) , '{}_{}_{}_PV_ctrl_orig.visibility'.format(side,fix,branch), f=True )
                
                # make blens orient rig for toes tips
                tipOrigParent = mc.listRelatives('{}_{}_{}_tip_ctrl_orig'.format(side,fix,branch) , p=True)[0]
                ## create hold grp
                holdGrp = mc.group(n='{}_{}_{}_tip_hold'.format(side,fix,branch) , em=True)
                mc.parent(holdGrp,'{}_{}_{}_tip_ctrl_orig'.format(side,fix,branch), r=True)
                mc.parent(holdGrp,tipOrigParent)
                ## create orient constraint and blend
                ### create orient Attr
                attrNode = '{}_{}_{}_IK_ctrl'.format(side,fix,branch)
                AttrName = 'toeTipOrient'
                mc.addAttr( attrNode , ln = AttrName , at = 'double' , min = 0 , max = 1 , dv = 0  )
                mc.setAttr('{}.{}'.format(attrNode,AttrName) , edit = True , k = True )
                ### multipliy Attr and ikFK blend
                toeTipOrientMDL = mc.createNode('multDoubleLinear', n= '{}_{}_{}_tipOrient_mdl'.format(side,fix,branch) )
                mc.connectAttr('{}.{}'.format(attrNode,AttrName), '{}.input1'.format(toeTipOrientMDL) )
                mc.connectAttr('{}_{}_{}_SW_ctrl.fkIk'.format(side,fix,branch), '{}.input2'.format(toeTipOrientMDL) )
                ### orientConstraint toes tip orig
                tipOrientCns = mc.orientConstraint('{}_{}_{}_IK_ctrl'.format(side,fix,branch),holdGrp,'{}_{}_{}_tip_ctrl_orig'.format(side,fix,branch), mo=True)[0]
                ### add reverse node and connect blend on orient constraint
                toeTipOrientRv = mc.createNode('reverse', n= '{}_{}_{}_tipOrient_rv'.format(side,fix,branch) )
                mc.connectAttr('{}.output'.format(toeTipOrientMDL), '{}.inputX'.format(toeTipOrientRv) )
                mc.connectAttr('{}.output'.format(toeTipOrientMDL), '{}.target[0].targetWeight'.format(tipOrientCns), f=True )
                mc.connectAttr('{}.outputX'.format(toeTipOrientRv), '{}.target[1].targetWeight'.format(tipOrientCns), f=True )      
                
                # change shapes
                
                shapes.create( '{}_{}_{}_nail_ctrl'.format(side,fix,branch), shape= 'cube', size= .1, scale= [.5, 1, .5], axis= 'z', twist= 0, offset= [0, 0, 0 ], color= lightRgb[s], colorDegradeTo= None, replace= True, middle= False)
                shapes.create( '{}_{}_{}_tip_ctrl'.format(side,fix,branch), shape= 'square', size= .25, scale= [.4, .5, .75], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= darkRgb[s], colorDegradeTo= None, replace= True, middle= False)
                shapes.create( '{}_{}_{}_squash_ctrl'.format(side,fix,branch), shape= 'cube', size= .15, scale= [.6, .1, 1], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= lightRgb[s], colorDegradeTo= None, replace= True, middle= False)
                shapes.create( '{}_{}_{}_IK_ctrl'.format(side,fix,branch), shape= 'square', size= .25, scale= [.5, .5, 1], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= baseRgb[s], colorDegradeTo= None, replace= True, middle= False)
                
            shapes.create( '{}_{}_cushion_ctrl'.format(side,fix), shape= 'square', size= .3, scale= [1, 1, 1], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= baseRgb[s], colorDegradeTo= None, replace= True, middle= False)  
            shapes.create( '{}_{}_leg_scl_ctrl'.format(side,fix), shape= 'cube', size= .22, scale= [1, .3, 1], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= lightRgb[s], colorDegradeTo= None, replace= True, middle= False)




