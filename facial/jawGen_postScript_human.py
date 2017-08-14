import maya.cmds as mc
import marsCore.shapes.defs as shapes
reload(shapes)
from marsAutoRig_stubby.patch.facial import jawGen_layeredFKTongue as layeredFKTongue
reload(layeredFKTongue)
from marsAutoRig_stubby.patch.facial import teeth_Generate_human as teethGen
reload(teethGen)

#shapes.create( sel, shape= 'circle', size= 1, scale= [1, 1, 1 ], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= None, colorDegradeTo= None, replace= True, middle= False)


def patch():

    facialDrv = 'facialDrivers'

    eyeMaskOrig = 'eyeMask_ctrl_orig'

    JawClenchLOrig = 'Jaw_Clench_l_ctrl_orig'
    JawClenchROrig = 'Jaw_Clench_r_ctrl_orig'

    UpHeadGuide = 'UpHead_ctrl_GUIDE_01'
    UpHeadOrig = 'UpHead_ctrl_01_orig'
    UpHeadCtrl = 'UpHead_ctrl_01'
    LowerHeadGuide = 'LowerHead_ctrl_GUIDE_01'    
    LowerHeadOrig = 'LowerHead_ctrl_01_orig'
    LowerHeadCtrl = 'LowerHead_ctrl_01'
    mouthSquashOrig = 'mouthSquash_jnt_orig'
    foreheadGrp = 'forehead_grp'
    headSKN = 'head_SKN'
    jawctrl = 'jaw_ctrl'
    noseGrp = 'nose_grp'
    noseUpCtrl = 'nose_up_ctrl'
    
    try :
        #reparent halfSkulls 
        mc.parent(eyeMaskOrig,UpHeadOrig,LowerHeadOrig,headSKN)
        #reparent jawClenches
        mc.parent(JawClenchLOrig,JawClenchROrig,jawctrl)
        #reparent foreHead into topSKull
        mc.parent(foreheadGrp,UpHeadCtrl)
        #reparent mouthSquash et nose into lowerSkull
        mc.parent(mouthSquashOrig,LowerHeadCtrl)
        mc.parent(noseGrp,headSKN)
        #deparent halfSkulls guides
        mc.parent(UpHeadGuide,LowerHeadGuide,facialDrv)
        #hide guides
        mc.hide(UpHeadGuide,LowerHeadGuide)

        #change midSkulls ctrlShapes
        shapes.create( UpHeadCtrl, shape= 'circleHalf', size= 2, scale= [1.25, 1, 1.75 ], axis= 'y', twist= -90, offset= [0, 0, 0.5 ], color= [255,255,0] , colorDegradeTo= None, replace= True, middle= False)
        shapes.create( LowerHeadCtrl, shape= 'circleHalf', size= 2, scale= [1.25, 1, 1.75 ], axis= 'y', twist= 90, offset= [0, 0, -0.5 ], color= [255,255,0] , colorDegradeTo= False, replace= True, middle= False)
        
        #add noseFollow
        noseCtrlOrig = mc.listRelatives(noseUpCtrl,p=True)[0]
        noseHold = mc.group(n='%s_hold' %noseCtrlOrig,em=True)
        mc.parent(noseHold,noseCtrlOrig,r=True)
        mc.parent(noseHold,noseGrp)
        noseCns = mc.parentConstraint(LowerHeadCtrl,noseHold,noseCtrlOrig,mo=True)[0]
        noseRv = mc.createNode('reverse', n='%s_rv' %noseCtrlOrig )
        mc.connectAttr('%s.Nose_Follow' %noseUpCtrl , '%s.target[0].targetWeight' %noseCns,f=True )
        mc.connectAttr('%s.Nose_Follow' %noseUpCtrl , '%s.inputX' %noseRv )
        mc.connectAttr('%s.outputX' %noseRv , '%s.target[1].targetWeight' %noseCns,f=True )
        
        # attaches the tongue FK to the mouth inside mesh
        layeredFKTongue.doLayeredFkTongue()
        # upgrades teeth rig
        teethGen.generateTeeth()
        
        
    except :
        print 'template not conform to patchScript'








