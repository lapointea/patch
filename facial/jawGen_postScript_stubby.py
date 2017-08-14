import maya.cmds as mc
import marsCore.shapes.defs as shapes
reload(shapes)

#shapes.create( sel, shape= 'circle', size= 1, scale= [1, 1, 1 ], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= None, colorDegradeTo= None, replace= True, middle= False)


def postJawGenHuman():

    eyeMaskOrig = 'eyeMask_ctrl_orig'

    JawClenchLOrig = 'Jaw_Clench_l_ctrl_orig'
    JawClenchROrig = 'Jaw_Clench_r_ctrl_orig'

    UpHeadOrig = 'UpHead_ctrl_01_orig'
    UpHeadCtrl = 'UpHead_ctrl_01'
    LowerHeadOrig = 'LowerHead_ctrl_01_orig'
    LowerHeadCtrl = 'LowerHead_ctrl_01'
    mouthSquashOrig = 'mouthSquash_jnt_orig'
    foreheadGrp = 'forehead_grp'
    headSKN = 'head_SKN'
    jawctrl = 'jaw_ctrl'
    noseGrp = 'nose_grp'

    #reparent halfSkulls and nose
    mc.parent(noseGrp,eyeMaskOrig,UpHeadOrig,LowerHeadOrig,headSKN)
    #reparent jawClenches
    mc.parent(JawClenchLOrig,JawClenchROrig,jawctrl)

    #change midSkulls ctrlShapes

    shapes.create( UpHeadCtrl, shape= 'circleHalf', size= 2, scale= [1.25, 1, 1.75 ], axis= 'y', twist= -90, offset= [0, 0, 0.5 ], color= [255,255,0] , colorDegradeTo= None, replace= True, middle= False)
    shapes.create( LowerHeadCtrl, shape= 'circleHalf', size= 2, scale= [1.25, 1, 1.75 ], axis= 'y', twist= 90, offset= [0, 0, -0.5 ], color= [255,255,0] , colorDegradeTo= False, replace= True, middle= False)









