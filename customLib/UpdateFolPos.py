import maya.cmds as mc

#select follicles then run to create repositionLocators
#createRepLocs()

#when locators position is ok,selectFollicles and run command
#updateFolFromRepLoc()

# --- def create replace locators ---#
def createRepLocs():
    sel = mc.ls(sl=True)
    repLocList = []
    for fol in sel:
        folPos = mc.xform(fol,ws=True,t=True,q=True)
        repLoc = mc.spaceLocator(n='%s_repLoc' %fol)[0]
        mc.setAttr('%s.localScale' %repLoc , 0.1,0.1,0.1)
        mc.xform(repLoc,ws=True,t=folPos)
        repLocList.append(repLoc)
    return repLocList
# --- def create replace locators ---#

# --- def replace follicles ---#
def updateFolFromRepLoc():
    sel = mc.ls(sl=True)
    CPOS = mc.createNode('closestPointOnSurface' , n='tempFolCPOS')
    RBDSurf = mc.createNode('rebuildSurface' , n ='tempFolRBDSurf')
    mc.setAttr('%s.keepControlPoints' %RBDSurf , True)
    mc.setAttr('%s.keepRange' %RBDSurf , 0)
    mc.setAttr('%s.rebuildType' %RBDSurf , 0)
    mc.connectAttr('%s.outputSurface' %RBDSurf , '%s.inputSurface' %CPOS , f=True)
                            
    for fol in sel :
        if mc.objExists('%s_repLoc' %fol):
            folShape = mc.listRelatives(fol , s=True,type='follicle')[0]
            folSurfPlug = mc.listConnections('%s.inputSurface' %folShape , p=True)[0]
            mc.connectAttr(folSurfPlug,'%s.inputSurface' % RBDSurf , force=True)
            
            repLocPos = mc.xform('%s_repLoc' %fol,ws=True,t=True,q=True)
            mc.setAttr('%s.inPosition' % CPOS , repLocPos[0],repLocPos[1],repLocPos[2])
            newU = mc.getAttr('%s.parameterU' % CPOS)
            newV = mc.getAttr('%s.parameterV' % CPOS)
            
            print newU
            print newV        
            
            mc.setAttr('%s.parameterU' % folShape , newU)
            mc.setAttr('%s.parameterV' % folShape , newV)
            
            bpmName = folShape.replace('rivet','bpmRvt')
            if mc.objExists(bpmName):
                mc.setAttr('%s.parameterU' % bpmName , newU)
                mc.setAttr('%s.parameterV' % bpmName , newV)
            
            mc.disconnectAttr(folSurfPlug,'%s.inputSurface' %RBDSurf)
        mc.delete('%s_repLoc' %fol) 
    mc.delete(CPOS,RBDSurf)
    
        
        


    

        




