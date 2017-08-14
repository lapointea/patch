import maya.cmds as mc

#updateRotateOrder(xyz=[], yzx=[], zxy=[], xzy=[], yxz=[], zyx=[] )
def updateRotateOrder(xyz=[], yzx=[], zxy=[], xzy=[], yxz=[], zyx=[] ):
    updateRoList = [xyz,yzx,zxy,xzy,yxz,zyx]

    for ro , RoList in enumerate(updateRoList):
            for each in RoList:
                mc.setAttr('%s.rotateOrder' %each , k=True)
                mc.setAttr('%s.rotateOrder' %each , ro)
                
def makeAllRoKeyable(setName):
    mc.select(setName)
    setSel = mc.ls(sl=True)
    mc.select(cl=True)
    animCtrls = []
    for sel in setSel :
        if not mc.objectType(sel) == 'objectSet':
            animCtrls.append(sel)
    for ctrl in animCtrls:
        mc.setAttr('{}.rotateOrder'.format(ctrl), k=True)
        # get actual rotateORder balue and set it as default
        RoValue = mc.getAttr('{}.rotateOrder'.format(ctrl))
        mc.addAttr(ctrl, ln='reset_rotateOrder' , at = 'long', min = 0, max = 5, dv = 0 )
        mc.setAttr('{}.reset_rotateOrder'.format(ctrl), RoValue )
        mc.setAttr('{}.reset_rotateOrder'.format(ctrl), l=True )
        
    









