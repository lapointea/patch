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
#shapes.create( sel, shape= 'circle', size= 1, scale= [1, 1, 1 ], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= None, colorDegradeTo= None, replace= True, middle= False)
 

autoSourceBaseName = 'leg_foot_ball_01_ctrl_orig'

'''
sides = ['L','R']
intFixes = ['front','back']

# COPY THIS IN PATCHSCRIPT
# create Auto locators for source of legs automation
for side in sides:
    for fix in intFixes:

        autoSourceName = '{}_{}_{}'.format(side,fix,autoSourceBaseName)
        sourcePos = mc.xform(autoSourceName, q=True, ws=True, t=True)
        autoLoc = mc.spaceLocator(n=autoSourceName.replace('orig','autoLoc') )[0]
        mc.xform(autoLoc, ws=True, t=sourcePos)
        mc.parent(autoLoc,autoSourceName)
        mc.hide(autoLoc)
'''        


def buildLegsAutomation(sides,intFixes):
    for side in sides:
        for fix in intFixes:

            # --- generate front Legs Automation
            nodeSource = '{}_{}_leg_foot_ball_01_ctrl_autoLoc'.format(side,fix)
            nodeTarget = '{}_{}_leg_root_offset_ctrl_auto'.format(side,fix)
            attrNode = '{}_{}_leg_SW_ctrl'.format(side,fix)
            attrBaseName = 'legAutomation'

            softLimitAutoMationGenerate(side,fix,nodeSource,nodeTarget,attrNode,attrBaseName)
            
            # --- generate front scapula automation
            if fix == 'front':
                    
                nodeSource = '{}_{}_leg_root_offset_ctrl'.format(side,fix)
                nodeTarget = '{}_reverse_scapula_ikh_auto'.format(side)
                attrNode = '{}_{}_leg_SW_ctrl'.format(side,fix)
                attrBaseName = 'scapulaAutomation'
                
                simpleFollowGenerate(side,fix,nodeSource,nodeTarget,attrNode,attrBaseName)
                
         


def buildLegsTopIks(sides,intFixes,chestAdjust):

    #sides = ['L','R']
    #intFixes = ['front','back']
    #chestAdjust = 'chest_adjust_ctrl'
    baseRgb = [[0,0,1],[1,0,0]]
    darkRgb = [[0,0,.8],[.8,0,0]]
    lightRgb = [[.5,.5,1],[1,.5,.5]]

    for s, side in enumerate(sides) :
        fix = intFixes[0]
        #### front leg 
        # add of Auto node + orig on top of leg root offset orig
        nodeRoot = '{}_{}_leg_root_offset_ctrl'.format(side,fix)

        makeAutoNode(nodeRoot)

        # --- recreate reverse scapula joint with Ik and scaleBlend
        nodeEnd = '{}_scapula_ctrl'.format(side)
        baseName = nodeEnd.replace('scapula_ctrl', 'reverse_scapula' )
        attrNode = '{}_{}_leg_SW_ctrl'.format(side,fix)
        attrName = '{}ScapulaStretch'.format(side)

        revIK = makeRevIk(nodeRoot,nodeEnd,baseName,attrNode,attrName)   
        
        # --- add auto group on reverse ikh orig
        revIkAuto = makeAutoNode(revIK[2])
        print 'ikAuto Target = %s' % revIK[3]
        print revIkAuto

        # --- recrate base scapula chain and pointConstraint scapula_orig to it
        baseScapRoot = chestAdjust
        baseScapName = nodeEnd.replace('scapula_ctrl','scapula_base_jnt')

        scapulaBaseChain = makeChainFromObj(baseScapRoot,nodeEnd,baseScapName)
        mc.parent(scapulaBaseChain[2],chestAdjust)
        mc.pointConstraint(scapulaBaseChain[1], mc.listRelatives(nodeEnd,p=True), mo=False )   

        # --- recreate base scapula  secondary chain + ik  fullScale
        baseScapSecName = nodeEnd.replace('scapula_ctrl','scapula_base_sec_jnt')
        baseScapAttrName = 'baseScapeScale'
        baseScapSecEnd = mc.listRelatives(nodeEnd,p=True)
        basScapSecChain = makeRevIk(scapulaBaseChain[0],baseScapSecEnd,baseScapSecName,scapulaBaseChain[0],baseScapAttrName)
        mc.setAttr('{}.{}'.format(scapulaBaseChain[0],baseScapAttrName), 1 )
        mc.setAttr('{}.{}'.format(scapulaBaseChain[0],baseScapAttrName), l=True )
        
        # --- make scapula base ctrl
        mc.select(cl=True)
        scapulaBaseCtrl = mc.joint(n= nodeEnd.replace('scapula','scapula_base'))
        mc.setAttr('{}.drawStyle'.format(scapulaBaseCtrl), 2)
        mc.setAttr('{}.radius'.format(scapulaBaseCtrl), k=False)
        mc.parent(scapulaBaseCtrl,nodeEnd,r=True)    
        
        shapes.create( scapulaBaseCtrl, shape= 'root', size= .6, scale= [1, 1, 1 ], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= lightRgb[s] , colorDegradeTo= None, replace= True, middle= False) 
        scapulaBaseCtrlOrig = orig.orig(objlist=[scapulaBaseCtrl], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')[0]
        scapulaBaseCtrlAuto = orig.orig(objlist=[scapulaBaseCtrlOrig], suffix=['_auto'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')[0]
        patchLib.locksSwitch(scapulaBaseCtrl,T=False,R=True,S=True,V=True,lockdo='lock',keydo=False)
             
        mc.pointConstraint(revIK[1],scapulaBaseCtrlAuto,mo=True)

        # --- make reverse scapula secondary chain and full ik stretch
        baseSecName = nodeEnd.replace('scapula_ctrl', 'reverse_scapula_sec' )    
        revSecIK = makeRevIk(revIK[0],scapulaBaseCtrl,baseSecName,revIK[0],baseScapAttrName)   
        mc.setAttr('{}.{}'.format(revIK[0],baseScapAttrName), 1 )
        mc.setAttr('{}.{}'.format(revIK[0],baseScapAttrName), l=True )  
           
        mc.pointConstraint(revSecIK[1],basScapSecChain[3],mo=True)
        
        # constraint reverse chain Orig to base leg ctrl
        revChainOrig = mc.listRelatives(revIK[0], p=True)
        legBaseCtrl = '{}_{}_leg_01_base_ctrl'.format(side,fix)  
          
        mc.pointConstraint(legBaseCtrl,revChainOrig,mo=True)
        
        # connect base scapula ctrl to advance attr
        mc.connectAttr('{}.advanced'.format(attrNode), '{}.visibility'.format(scapulaBaseCtrlOrig) )

       
        #### back leg ####   
        fix = intFixes[1]
        
        sideHipRoot = '{}_hip_ctrl'.format(side)
        sideHipEnd = '{}_{}_leg_root_offset_ctrl'.format(side,fix)
        
        # --- make side hip auto
        sideHipAuto = makeAutoNode(sideHipEnd)
        
        # --- add end joint on side hips control
        sideHipBaseName = sideHipRoot.replace('ctrl','chain')
        
        siddeHipChain = makeChainFromObj(sideHipRoot,sideHipEnd,sideHipBaseName)
        mc.parent(siddeHipChain[2],sideHipRoot)
        
        # --- re PointConstraint
        mc.pointConstraint(siddeHipChain[1], sideHipAuto[1]  )
        
        # --- double side hip chain in IK fullStretch controlled by back leg offset
        sideHipSecRoot = mc.listRelatives(sideHipEnd, p=True)
        sideHipSecBaseName = sideHipBaseName.replace('chain','sec')
        sideHipSecattrName = 'sideHipScale'
        
        sideHipSecChain = makeRevIk(siddeHipChain[0],sideHipSecRoot,sideHipSecBaseName,siddeHipChain[0],sideHipSecattrName)
        mc.setAttr('{}.{}'.format(siddeHipChain[0],sideHipSecattrName), 1 )
        mc.setAttr('{}.{}'.format(siddeHipChain[0],sideHipSecattrName), l=True )  
        
        # --- constraint side hip ik to back leg base Ctrl
        backLegBaseCtrl = '{}_{}_leg_01_base_ctrl'.format(side,fix)
        mc.pointConstraint(backLegBaseCtrl,sideHipSecChain[3], mo=True)
    
    
def makeChainFromObj(nodeRoot,nodeEnd,baseName):
    rootName = '{}_root'.format(baseName)
    endName = '{}_end'.format(baseName)    
    rootPos = mc.xform(nodeRoot, q=True, ws=True, t=True)
    endPos = mc.xform(nodeEnd, q=True, ws=True, t=True)
    # create joint chain
    mc.select(cl=True)
    rootJoint = mc.joint(n=rootName)
    mc.setAttr('{}.radius'.format(rootJoint), 0.02)
    mc.xform(rootJoint, ws=True, t=rootPos )    
    mc.select(cl=True)
    endJoint = mc.joint(n=endName)
    mc.setAttr('{}.radius'.format(endJoint), 0.02)
    mc.xform(endJoint, ws=True, t=endPos )    
    mc.parent(endJoint,rootJoint)
    mc.joint( rootJoint, e=True, oj = 'zxy', secondaryAxisOrient = 'yup', ch = True, zso = True )
    chainOrig = orig.orig(objlist=[rootJoint], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')[0]
    
    return(rootJoint,endJoint,chainOrig,rootPos,endPos)
    
    
def makeRevIk(nodeRoot,nodeEnd,baseName,attrNode,attrName):
    #create new chain
    newChain = makeChainFromObj(nodeRoot,nodeEnd,baseName)
    rootPos = newChain[3]
    endPos = newChain[4]
    # create ikh orig and ikh
    ikhOrig = mc.group(n= '{}_ikh_orig'.format(baseName), em=True)
    mc.xform(ikhOrig, ws=True, t=endPos )
    ikh = mc.ikHandle(sj = newChain[0] , ee = newChain[1] , n = '{}_ikh'.format(baseName) , sol = 'ikSCsolver' )[0]
    mc.hide(ikh)
    mc.parent(ikh,ikhOrig)
    # add attr for ikStretch Blend
    mc.addAttr( attrNode , ln = attrName , at = 'double' , min = 0, max = 1, dv = 0  )
    mc.setAttr('{}.{}'.format(attrNode,attrName) , edit = True , k = True )
    # create ikScale rig
    rvChainDB = mc.createNode('distanceBetween', n='{}_scale_db'.format(baseName) )
    rvChainRefDB = mc.createNode('distanceBetween', n='{}_scale_ref_db'.format(baseName) )
    rvChainMD = mc.createNode('multiplyDivide', n='{}_scale_md'.format(baseName) )
    rvChainBTA = mc.createNode('blendTwoAttr', n='{}_scale_bta'.format(baseName) )
    #create reference position nodes for scale_ref_distanceBetween
    rootRefNode = mc.group(n='{}_refPose'.format(nodeRoot) , em=True)
    endRefNode = mc.group(n='{}_refPose'.format(nodeEnd) , em=True)
    mc.parent(rootRefNode,nodeRoot, r=True)
    mc.parent(endRefNode,nodeEnd, r=True)    
    mc.parent(rootRefNode,endRefNode, mc.listRelatives(nodeRoot, p=True))  
    ## connect distance between node
    mc.connectAttr('{}.worldMatrix[0]'.format(newChain[2]), '{}.inMatrix1'.format(rvChainDB) )
    mc.connectAttr('{}.worldMatrix[0]'.format(ikhOrig), '{}.inMatrix2'.format(rvChainDB) )
    ## connect distance between ref node
    mc.connectAttr('{}.worldMatrix[0]'.format(rootRefNode), '{}.inMatrix1'.format(rvChainRefDB) )
    mc.connectAttr('{}.worldMatrix[0]'.format(endRefNode), '{}.inMatrix2'.format(rvChainRefDB) )
    ## connect multiplyDivide
    mc.connectAttr('{}.distance'.format(rvChainDB), '{}.input1X'.format(rvChainMD) )
    mc.connectAttr('{}.distance'.format(rvChainRefDB), '{}.input2X'.format(rvChainMD) )
    mc.setAttr('{}.operation'.format(rvChainMD), 2)
    ## connect blendTwoAttributes
    mc.connectAttr('{}.{}'.format(attrNode,attrName), '{}.attributesBlender'.format(rvChainBTA) )
    mc.setAttr('{}.input[0]'.format(rvChainBTA), 1 )
    mc.connectAttr('{}.outputX'.format(rvChainMD), '{}.input[1]'.format(rvChainBTA) )
    mc.connectAttr('{}.output'.format(rvChainBTA), '{}.scaleZ'.format(newChain[0]))
    # reparent chain and ikh_orig
    mc.parent(ikhOrig,nodeEnd)
    mc.parent(newChain[2],nodeRoot)  
    
    return(newChain[0],newChain[1],ikh,ikhOrig)   
    

def makeAutoNode(nodeRoot):
    legRootOrig = mc.listRelatives(nodeRoot, p=True)[0]
    rootParent = mc.listRelatives(legRootOrig, p=True)[0]
    # create Auto node
    legRootAuto = '{}_auto'.format(nodeRoot)
    mc.group(n= legRootAuto, em=True)
    legRootAutoOrig = orig.orig(objlist=[legRootAuto], suffix=['_orig'], origtype='transform', fromsel=False, viz=False, get_ssc=False, rtyp='auto')[0]
    # reparent hierarchy
    mc.parent(legRootAutoOrig, legRootOrig )
    mc.setAttr('{}.translate'.format(legRootAutoOrig) , 0,0,0 )
    mc.parent(legRootAutoOrig, rootParent)
    mc.parent(legRootOrig, legRootAuto)
    return (legRootAuto,legRootAutoOrig)
    
##### simple Hard follow
def simpleFollowGenerate(side,fix,nodeSource,nodeTarget,attrNode,attrBaseName):
    #nodeSource = '{}_{}_leg_root_offset_ctrl'.format(side,fix)
    #nodeTarget = '{}_reverse_scapula_ikh_auto'.format(side)
    #attrNode = '{}_{}_leg_SW_ctrl'.format(side,fix)
    #attrBaseName = 'scapulaAutomation'
           
    ## --- create autoGetLoc in at same level as target Hierarchy   and pointConstrain it to autoLocq
    targetParent = mc.listRelatives(nodeTarget, p=True)
    autoGetLoc = mc.spaceLocator(n= '{}_autoGetLoc'.format(nodeTarget))[0]
    mc.parent(autoGetLoc,nodeTarget, r=True)
    mc.parent(autoGetLoc, targetParent)
    mc.hide(autoGetLoc)
    mc.pointConstraint(nodeSource,autoGetLoc,mo=True)
    
    ## --- create attributes on SW ctrl for soft limit tweaking
    axisList = ['x','y','z']
    
    separatorAttr = '{}'.format(attrBaseName)        
    mc.addAttr( attrNode , ln = separatorAttr , at = 'enum' , en = attrBaseName )
    mc.setAttr('{}.{}'.format(attrNode,separatorAttr) , edit = True , cb = True , l=True) 
    
    ## FollowBlend Attributes
    for axis in axisList :
        attrName = '{}ScapulaFollow'.format(axis)
        mc.addAttr( attrNode , ln = attrName , at = 'double' , min = 0, max = 1, dv = .25  )
        mc.setAttr('{}.{}'.format(attrNode,attrName) , edit = True , k = True )  
    
    ## --- create nodes system for soft limit rig
    blendMD = mc.createNode('multiplyDivide', n='{}_{}_{}_blend_md'.format(side,fix,attrBaseName) )
    ikFkBlend = mc.createNode('multiplyDivide', n='{}_{}_{}_ikFkBlend_md'.format(side,fix,attrBaseName) )
    
    ### connect follow Attributse to blendMD
    for axis in axisList :
        if axis == 'x':                    
            attrName = '{}ScapulaFollow'.format(axis)
            mc.connectAttr('{}.{}'.format(attrNode,attrName), '{}.input2X'.format(blendMD) )
            
        if axis == 'y':
            attrName = '{}ScapulaFollow'.format(axis)
            mc.connectAttr('{}.{}'.format(attrNode,attrName), '{}.input2Y'.format(blendMD) )
            
        if axis == 'z':
            attrName = '{}ScapulaFollow'.format(axis)
            mc.connectAttr('{}.{}'.format(attrNode,attrName), '{}.input2Z'.format(blendMD) )

    ### connect source to blendMD
    mc.connectAttr('{}.translate'.format(autoGetLoc),'{}.input1'.format(blendMD) ) 
    ### connect blendMD to target
    mc.connectAttr('{}.output'.format(blendMD), '{}.input1'.format(ikFkBlend) ) 
    mc.connectAttr('{}.fkIk'.format(attrNode), '{}.input2X'.format(ikFkBlend) )
    mc.connectAttr('{}.fkIk'.format(attrNode), '{}.input2Y'.format(ikFkBlend) )
    mc.connectAttr('{}.fkIk'.format(attrNode), '{}.input2Z'.format(ikFkBlend) )
    
    mc.connectAttr('{}.output'.format(ikFkBlend), '{}.translate'.format(nodeTarget) ) 


##### soft Limit follow
def softLimitAutoMationGenerate(side,fix,nodeSource,nodeTarget,attrNode,attrBaseName):
    # --- generate front Legs Automation

    #nodeSource = '{}_{}_leg_foot_ball_01_ctrl_autoLoc'.format(side,fix)
    #nodeTarget = '{}_{}_leg_root_offset_ctrl_auto'.format(side,fix)
    #attrNode = '{}_{}_leg_SW_ctrl'.format(side,fix)
    #attrBaseName = 'legAutomation'
           
    ## --- create autoGetLoc in at same level as target Hierarchy   and pointConstrain it to autoLocq
    targetParent = mc.listRelatives(nodeTarget, p=True)
    autoGetLoc = mc.spaceLocator(n= '{}_autoGetLoc'.format(nodeTarget))[0]
    mc.parent(autoGetLoc,nodeTarget, r=True)
    mc.parent(autoGetLoc, targetParent)
    mc.hide(autoGetLoc)
    mc.pointConstraint(nodeSource,autoGetLoc,mo=True)
    
    ## --- create attributes on SW ctrl for soft limit tweaking
    axisList = ['x','y','z']
    dirList = ['Pos','Neg']
    
    attrName = 'LegFollowAll'
    mc.addAttr( attrNode , ln = attrName , at = 'double' , min = 0, max = 1, dv = 1  )
    mc.setAttr('{}.{}'.format(attrNode,attrName) , edit = True , k = True )
    
    separatorAttr = '{}'.format(attrBaseName)        
    mc.addAttr( attrNode , ln = separatorAttr , at = 'enum' , en = attrBaseName )
    mc.setAttr('{}.{}'.format(attrNode,separatorAttr) , edit = True , cb = True , l=True)
       
    ## FollowBlend Attributes
    for axis in axisList :
        attrName = '{}LegFollow'.format(axis)
        mc.addAttr( attrNode , ln = attrName , at = 'double' , min = 0, max = 1, dv = .25  )
        mc.setAttr('{}.{}'.format(attrNode,attrName) , edit = True , k = True )
    ## axises limits attributes
    for axis in axisList :
        for dir in dirList:
            attrName = '{}{}LegLimit'.format(axis,dir)
            mc.addAttr( attrNode , ln = attrName , at = 'double' , min = 0, max = 100, dv = 1  )
            mc.setAttr('{}.{}'.format(attrNode,attrName) , edit = True , k = True )        
    
    ## --- create nodes system for soft limit rig
    ### create nodes
    xCond = mc.createNode('condition', n='{}_{}_{}_xdir_cond'.format(side,fix,attrBaseName) )
    mc.setAttr('{}.operation'.format(xCond), 2 )
    yCond = mc.createNode('condition', n='{}_{}_{}_ydir_cond'.format(side,fix,attrBaseName) )
    mc.setAttr('{}.operation'.format(yCond), 2 )
    zCond = mc.createNode('condition', n='{}_{}_{}_zdir_cond'.format(side,fix,attrBaseName) )
    mc.setAttr('{}.operation'.format(zCond), 2 )
    
    squareMD = mc.createNode('multiplyDivide', n='{}_{}_{}_square_md'.format(side,fix,attrBaseName) )
    mc.setAttr('{}.operation'.format(squareMD), 3 )
    mc.setAttr('{}.input2'.format(squareMD), 2,2,2 )
    firstFactorMD = mc.createNode('multiplyDivide', n='{}_{}_{}_firstFactor_md'.format(side,fix,attrBaseName) )
    secFactorMD = mc.createNode('multiplyDivide', n='{}_{}_{}_sectFactor_md'.format(side,fix,attrBaseName) )
    mc.setAttr('{}.operation'.format(secFactorMD), 2 )
    squareRootMD = mc.createNode('multiplyDivide', n='{}_{}_{}_squareRoot_md'.format(side,fix,attrBaseName) )
    mc.setAttr('{}.operation'.format(squareRootMD), 3 )
    mc.setAttr('{}.input2'.format(squareRootMD), 0.5,0.5,0.5 )
    blendMD = mc.createNode('multiplyDivide', n='{}_{}_{}_blend_md'.format(side,fix,attrBaseName) )    
    ikFkBlendMD = mc.createNode('multiplyDivide', n='{}_{}_{}_ikFkBlend_md'.format(side,fix,attrBaseName) )  
    allBlendMD = mc.createNode('multiplyDivide', n='{}_{}_{}_allBlend_md'.format(side,fix,attrBaseName) )  
    
    noZeroPMA = mc.createNode('plusMinusAverage', n='{}_{}_{}_noZero_pma'.format(side,fix,attrBaseName) )
    mc.setAttr('{}.input3D[1]'.format(noZeroPMA), 1,1,1 )
   
    ### connect source to conditions
    for axis in axisList :
        if axis == 'x':                    
            mc.connectAttr('{}.outputX'.format(blendMD) , '{}.firstTerm'.format(xCond) ) 
            ### connect followBlend to blendMD
            attrName = '{}LegFollow'.format(axis)
            mc.connectAttr('{}.{}'.format(attrNode,attrName), '{}.input2X'.format(blendMD) )
            
        if axis == 'y':
            mc.connectAttr('{}.outputY'.format(blendMD) , '{}.firstTerm'.format(yCond) )
            ### connect followBlend to blendMD
            attrName = '{}LegFollow'.format(axis)
            mc.connectAttr('{}.{}'.format(attrNode,attrName), '{}.input2Y'.format(blendMD) )
            
        if axis == 'z':
            mc.connectAttr('{}.outputZ'.format(blendMD) , '{}.firstTerm'.format(zCond) )
            ### connect followBlend to blendMD
            attrName = '{}LegFollow'.format(axis)
            mc.connectAttr('{}.{}'.format(attrNode,attrName), '{}.input2Z'.format(blendMD) )
        
        for dir in dirList:                
            attrName = '{}{}LegLimit'.format(axis,dir)
            
            if axis == 'x':     
                if dir == 'Pos':               
                    mc.connectAttr('{}.{}'.format(attrNode,attrName), '{}.colorIfTrueR'.format(xCond) )   
                if dir == 'Neg':               
                    mc.connectAttr('{}.{}'.format(attrNode,attrName), '{}.colorIfFalseR'.format(xCond) )                    
            if axis == 'y':
                if dir == 'Pos':               
                    mc.connectAttr('{}.{}'.format(attrNode,attrName), '{}.colorIfTrueR'.format(yCond) )   
                if dir == 'Neg':               
                    mc.connectAttr('{}.{}'.format(attrNode,attrName), '{}.colorIfFalseR'.format(yCond) )                  
            if axis == 'z':
                if dir == 'Pos':               
                    mc.connectAttr('{}.{}'.format(attrNode,attrName), '{}.colorIfTrueR'.format(zCond) )   
                if dir == 'Neg':               
                    mc.connectAttr('{}.{}'.format(attrNode,attrName), '{}.colorIfFalseR'.format(zCond) )




    ### connect source to blendMD
    mc.connectAttr('{}.translate'.format(autoGetLoc),'{}.input1'.format(blendMD) )
    mc.connectAttr('{}.fkIk'.format(attrNode),'{}.input2X'.format(ikFkBlendMD) )
    mc.connectAttr('{}.fkIk'.format(attrNode),'{}.input2Y'.format(ikFkBlendMD) )
    mc.connectAttr('{}.fkIk'.format(attrNode),'{}.input2Z'.format(ikFkBlendMD) )
    mc.connectAttr('{}.LegFollowAll'.format(attrNode),'{}.input2X'.format(allBlendMD) )
    mc.connectAttr('{}.LegFollowAll'.format(attrNode),'{}.input2Y'.format(allBlendMD) )
    mc.connectAttr('{}.LegFollowAll'.format(attrNode),'{}.input2Z'.format(allBlendMD) ) 
    ### connect source to square MD
    mc.connectAttr('{}.output'.format(blendMD), '{}.input1'.format(squareMD) )
    ### connect square MD to firstFactorMD
    mc.connectAttr('{}.output'.format(squareMD),'{}.input1'.format(firstFactorMD)  )
    ### connect conds to firstFactorMD                    
    mc.connectAttr('{}.outColor.outColorR'.format(xCond), '{}.input2X'.format(firstFactorMD) )
    mc.connectAttr('{}.outColor.outColorR'.format(yCond), '{}.input2Y'.format(firstFactorMD) )
    mc.connectAttr('{}.outColor.outColorR'.format(zCond), '{}.input2Z'.format(firstFactorMD) )
    ### connect firstFactorMD to noZeroPMA
    mc.connectAttr('{}.output'.format(firstFactorMD), '{}.input3D[0]'.format(noZeroPMA) )
    ### connect noZeroPMA to squareRootMD
    mc.connectAttr('{}.output3D'.format(noZeroPMA), '{}.input1'.format(squareRootMD) )
    ### connectSource to secFactorMD
    mc.connectAttr('{}.output'.format(blendMD), '{}.input1'.format(secFactorMD) )
    ### connect squareRootMD to secFactorMD
    mc.connectAttr('{}.output'.format(squareRootMD), '{}.input2'.format(secFactorMD) ) 
    ### connect secFactorMD to target
    mc.connectAttr('{}.output'.format(secFactorMD), '{}.input1'.format(ikFkBlendMD) )
    mc.connectAttr('{}.output'.format(secFactorMD), '{}.input1'.format(allBlendMD) )
    mc.connectAttr('{}.output'.format(allBlendMD),'{}.translate'.format(nodeTarget) )

