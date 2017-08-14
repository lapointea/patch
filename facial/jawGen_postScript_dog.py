import maya.cmds as mc
import marsCore.shapes.defs as shapes
reload(shapes)
import marsCore.orig as orig
reload(orig)
from marsAutoRig_stubby.patch.customLib import patchLib as patchLib
from marsAutoRig_stubby.patch.facial import teeth_Generate_human as teethGen
reload(teethGen)

#shapes.create( sel, shape= 'circle', size= 1, scale= [1, 1, 1 ], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= None, colorDegradeTo= None, replace= True, middle= False)
#orig.orig(objlist=[], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')
#patchLib.locksSwitch(sel,T=True,R=True,S=True,V=True,lockdo='unlock',keydo=False)

#################################################################################################
def smartConnect(trgt,smart):
    mc.connectAttr('%s.translate' %trgt , '%s.translate' %smart )
    mc.connectAttr('%s.rotate' %trgt , '%s.rotate' %smart )
    mc.connectAttr('%s.scale' %trgt , '%s.scale' %smart )
    mc.connectAttr('%s.rotateOrder' %trgt , '%s.rotateOrder' %smart )
    if mc.objectType(trgt) == 'joint' :
        if mc.objectType(smart) == 'joint' :
            mc.connectAttr('%s.jointOrient' %trgt , '%s.jointOrient' %smart )
#################################################################################################
#########################################################################################
def createOvershootAttrLimit(sel,channels):

    if sel:
        if channels:       
            for each in sel :
                choiceNodeMin = mc.createNode('choice' , n = '%s_overshootLimit_min_ch' % each)
                mc.setAttr('%s.input[0]' % choiceNodeMin , -1 )
                mc.setAttr('%s.input[1]' % choiceNodeMin , -1.5 )
                mc.setAttr('%s.input[0]' % choiceNodeMin , l=True )
                mc.setAttr('%s.input[1]' % choiceNodeMin , l=True )   
                choiceNodeMax = mc.createNode('choice' , n = '%s_overshootLimit_max_ch' % each)
                mc.setAttr('%s.input[0]' % choiceNodeMax , 1 )
                mc.setAttr('%s.input[1]' % choiceNodeMax , 1.5 )
                mc.setAttr('%s.input[0]' % choiceNodeMax , l=True )
                mc.setAttr('%s.input[1]' % choiceNodeMax , l=True ) 
                
                mc.addAttr(each , ln = 'overShootLimits' , at = 'bool')
                mc.setAttr('%s.overShootLimits' % each , cb = True)
                mc.connectAttr('%s.overShootLimits' % each , '%s.selector' %choiceNodeMin , f=True)
                mc.connectAttr('%s.overShootLimits' % each , '%s.selector' %choiceNodeMax , f=True)            
                
                for channel in channels:
                    
                    axis = (channel.replace('t','')).upper()

                    minLimToggle = mc.getAttr('%s.minTransLimitEnable.minTrans%sLimitEnable' %(each,axis) )
                    maxLimToggle = mc.getAttr('%s.maxTransLimitEnable.maxTrans%sLimitEnable' %(each,axis) )                                         
                    minLim = mc.getAttr('%s.minTransLimit.minTrans%sLimit' %(each,axis) )
                    maxLim = mc.getAttr('%s.maxTransLimit.maxTrans%sLimit' %(each,axis) )
                    
                    if minLimToggle == True:
                        if minLim == -1 :
                            mc.connectAttr('%s.output' %choiceNodeMin , '%s.minTransLimit.minTrans%sLimit' %(each,axis), f=True)
                    if maxLimToggle == True:
                        if maxLim == 1 :
                            mc.connectAttr('%s.output' %choiceNodeMax , '%s.maxTransLimit.maxTrans%sLimit' %(each,axis) , f=True)                            
######################################################################################### 

def patch():
        
    facialDrv = 'facialDrivers'

    eyeMaskOrig = 'eyeMask_ctrl_orig'

    JawClenchLOrig = 'Jaw_Clench_l_ctrl_orig'
    JawClenchROrig = 'Jaw_Clench_r_ctrl_orig'
    jawChinOrig = 'jawChin_ctrl_orig'

    UpHeadGuide = 'UpHead_ctrl_GUIDE_01'
    UpHeadOrig = 'UpHead_ctrl_01_orig'
    UpHeadCtrl = 'UpHead_ctrl_01'
    LowerHeadGuide = 'LowerHead_ctrl_GUIDE_01'    
    LowerHeadOrig = 'LowerHead_ctrl_01_orig'
    LowerHeadCtrl = 'LowerHead_ctrl_01'
    mouthSquashOrig = 'mouthSquash_jnt_orig'
    mouthSquashSKN = 'mouthSquash_SKN'
    mouthGlobal = 'mouthGlobal_ctrl_orig'
    foreheadGrp = 'forehead_grp'
    headSKN = 'head_SKN'
    jawctrl = 'jaw_ctrl'
    jawJntOrig = 'jaw_jnt_orig'
    jawShapeGrp = 'jaw_SHAPE_grp'
    jawMidSkin = 'jaw_02_SKN'
    noseGrp = 'nose_grp'
    noseUp = 'nose_up_ctrl'
    noseUpOrig = 'nose_up_ctr_orig'
    neckTrash = 'neck_grpTRASH'
    earGrp = 'ear_grp'
    eyeGrp = 'eye_grp'
    eyeMaskGrp = 'eyeMask_ctrl_orig'

    sides = ['L','R','C']
    lipFlapOrig = 'lipFlap_ctrl_01_orig'
    lipflapAll = 'lipFlap_all_ctrl'
    lipflapTip = 'lipFlap_tip_ctrl'
    lipflapCup = 'lipFlap_cup_ctrl'
    lipFlapList = [lipflapAll,lipflapTip,lipflapCup]


    #try :

    #reparent halfSkulls 
    mc.parent(eyeMaskOrig,UpHeadOrig,LowerHeadOrig,headSKN)
    #reparent jawClenches
    mc.parent(JawClenchLOrig,JawClenchROrig,jawctrl)
    #reparent foreHead into topSKull
    mc.parent(foreheadGrp,UpHeadCtrl)
    #reparent mouthSquash et nose into lowerSkull
    mc.parent(noseGrp,mouthSquashOrig,LowerHeadCtrl)
    #deparent halfSkulls guides
    mc.parent(UpHeadGuide,LowerHeadGuide,facialDrv)
    # reparent jawChin in MidHJaw
    mc.parent(jawChinOrig,jawMidSkin)

    #change midSkulls ctrlShapes
    shapes.create( UpHeadCtrl, shape= 'circleHalf', size= 2, scale= [1.25, 1, 1.75 ], axis= 'y', twist= -90, offset= [0, 0, 0.5 ], color= [255,255,0] , colorDegradeTo= None, replace= True, middle= False)
    shapes.create( LowerHeadCtrl, shape= 'circleHalf', size= 2, scale= [1.25, 1, 1.75 ], axis= 'y', twist= 90, offset= [0, 0, -0.5 ], color= [255,255,0] , colorDegradeTo= False, replace= True, middle= False)

    # --- add upjaw ctrl
    ## create jawUp and jawUp proxies
    mc.select(cl=True)
    upJaw = mc.joint( n= 'upJaw_ctrl' )
    mc.setAttr('{}.radius'.format(upJaw), 0.01 )
    mc.select(cl=True)
    upJawLoHeadProxy = mc.joint( n= 'upJaw_loHead_proxy' )
    mc.setAttr('{}.radius'.format(upJawLoHeadProxy), 0.01 )
    mc.select(cl=True)
    upJawMSquashProxy = mc.joint( n= 'upJaw_mSquash_proxy' )
    mc.setAttr('{}.radius'.format(upJawMSquashProxy), 0.01 )

    jawpPos = mc.xform(jawctrl, q=True, ws=True, t=True)
    mc.xform(upJaw, ws=True, t= jawpPos )
    mc.xform(upJawLoHeadProxy, ws=True, t= jawpPos )
    mc.xform(upJawMSquashProxy, ws=True, t= jawpPos )
    jawPosOrigs = orig.orig(objlist=[upJaw,upJawLoHeadProxy,upJawMSquashProxy], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')

    ## reparent nodes in jawUp nodes
    mc.parent(eyeGrp,eyeMaskGrp,UpHeadOrig,upJaw)
    mc.parent(noseGrp,upJawLoHeadProxy)
    mSquashSKNChilds = mc.listRelatives(mouthSquashSKN, c=True)
    for child in mSquashSKNChilds:
        if not ( child == jawJntOrig or child == jawShapeGrp) :
            print child
            mc.parent(child,upJawMSquashProxy)
    ## reparent jawUp nodes
    mc.parent(jawPosOrigs[0],headSKN)
    mc.parent(jawPosOrigs[1],LowerHeadCtrl)
    mc.parent(jawPosOrigs[2],mouthSquashSKN)
    ## connectJawUps
    smartConnect(upJaw,upJawLoHeadProxy)
    smartConnect(upJaw,upJawMSquashProxy)
    # --- add shape to UpJaw
    shapes.create( upJaw, shape= 'pinSphere', size= 0.75, scale= [1, 1, 1 ], axis= 'y', twist= 0, offset= [0, .75, 0 ], color= [1,1,0] , colorDegradeTo= None, replace= True, middle= False)
    # --- change mouthGlobal parentConstraint targets
    mouthGlobalCns = mc.listConnections('{}.translateX'.format(mouthGlobal), s=True)[0]
    mc.delete(mouthGlobalCns)
    mc.parentConstraint(upJaw,jawctrl,mouthGlobal, mo=True)
    # --- add upJaw to skinSet
    mc.sets(upJaw, add='head_jnt_skin_set' )


    # --- reparent and adjust Shapes for flaps ctrls
    mainColList = [[0.0,0.0,1.0],[1.0,0.0,0.0],[1.0,1.0,0.0]]
    secColList = [[0.5,0.5,1.0],[1.0,0.5,0.5],[1.0,1.0,0.65]]
    sizeList = [0.07,0.07,0.04]

    for s , side in enumerate(sides):
        ## --- reparent dKey ctrls to world
        allCtrl = '%s_%s' %(side,lipflapAll)
        tipCtrl = '%s_%s' %(side,lipflapTip)
            
        allCtrlOrig = mc.listRelatives('%s_%s' %(side,lipflapAll) , p=True )[0]    
        mc.parent(allCtrlOrig , w=True)

        if side == 'L':
            shapes.create( allCtrl, shape= 'pyramid', size= sizeList[s] , scale= [1.5, -1.5, 1.5 ], axis= 'y', twist= 0 , offset= [0, -0.5 , 0 ], color= mainColList[s] , colorDegradeTo= None, replace= True, middle= False)    
            shapes.create( tipCtrl, shape= 'arrowFourCurve', size= sizeList[s] , scale= [0.8, -0.8, 0.8 ], axis= 'y', twist= 0 , offset= [0, -0.28 , 0 ], color= secColList[s] , colorDegradeTo= None, replace= True, middle= False)    

        elif side == 'R':
            shapes.create( allCtrl, shape= 'pyramid', size= sizeList[s] , scale= [1.5, 1.5, 1.5 ], axis= 'y', twist= 0 , offset= [0, 0.5 , 0 ], color= mainColList[s] , colorDegradeTo= None, replace= True, middle= False)    
            shapes.create( tipCtrl, shape= 'arrowFourCurve', size= sizeList[s] , scale= [0.8, 0.8, 0.8 ], axis= 'y', twist= 0 , offset= [0, 0.28 , 0 ], color= secColList[s] , colorDegradeTo= None, replace= True, middle= False)    

        elif side == 'C':
            shapes.create( allCtrl, shape= 'pyramid', size= sizeList[s] , scale= [1.5, -1.5, 1.5 ], axis= 'y', twist= 0 , offset= [0, -0.2 , 0 ], color= mainColList[s] , colorDegradeTo= None, replace= True, middle= False)    
            shapes.create( tipCtrl, shape= 'arrowFourCurve', size= sizeList[s] , scale= [0.8, -0.8, 0.8 ], axis= 'y', twist= 0 , offset= [0, -0.12 , 0 ], color= secColList[s] , colorDegradeTo= None, replace= True, middle= False)    

    # add hierarchy for drivenKeys on lipFlaps fk joints
    dKeyAllNodesList = []
    dKeyTipNodesList = []
    for side in sides:
        sideDKeyNodesList = []
        firstOrig = '%s_%s' %(side,lipFlapOrig)
        flapRoot = orig.orig(objlist=[firstOrig], suffix=['_root'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')[0]   
        allChilds = mc.listRelatives(flapRoot,c=True,typ='transform',ad=True)
        allChilds.reverse()
        for child in allChilds:
            stripName = child.rsplit('_',1)[-1]   
            if not stripName == 'orig' and not stripName == 'end':
                dkeyNode = orig.orig(objlist=[child], suffix=['_dKeyAll'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')[0]  
                sideDKeyNodesList.append(dkeyNode)
        dKeyAllNodesList.append(sideDKeyNodesList)
        
    for list in dKeyAllNodesList:
        sideDKeyNodesList = []
        listLen = len(list)
        for i in range((listLen/2),listLen):
            ctrl = mc.listRelatives(list[i],c=True,typ='transform')[0]
            dkeyNode = orig.orig(objlist=[ctrl], suffix=['_dKeyTip'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')[0]  
            sideDKeyNodesList.append(dkeyNode)
        dKeyTipNodesList.append(sideDKeyNodesList)
    # change controls shapes on lipFlaps FKs
    attrName = 'showLipFlapsFK'
    for s , side in enumerate(sides):
        mainFlapCtrl = '%s_%s' %(side,lipflapAll)
        mc.addAttr( mainFlapCtrl , ln = attrName , at = 'bool' )
        mc.setAttr('%s.%s' %(mainFlapCtrl,attrName) , edit = True , k = True )
            
        flapRoot = '%s_%s_root' %(side,lipFlapOrig)
        allChilds = mc.listRelatives(flapRoot,c=True,typ='transform',ad=True)
        allChilds.reverse()
        for child in allChilds:
            stripName = child.rsplit('_',1)[-1]   
            if not stripName == 'orig' and not stripName == 'end' and not stripName == 'dKeyAll' and not stripName == 'dKeyTip':
                if not side == 'R':
                    shapes.create( child, shape= 'pinPyramid', size= sizeList[s] , scale= [4, 5, 5 ], axis= '-X', twist= 0 , offset= [0, 0, 0 ], color= mainColList[s] , colorDegradeTo= None, replace= True, middle= False)
                else:
                    shapes.create( child, shape= 'pinPyramid', size= sizeList[s] , scale= [-4, 5, 5 ], axis= '-X', twist= 0 , offset= [0, 0, 0 ], color= mainColList[s] , colorDegradeTo= None, replace= True, middle= False)

            childShapes = mc.listRelatives(child,s=True)
            if childShapes:
                for childShape in childShapes:
                    mc.connectAttr('%s.%s' %(mainFlapCtrl,attrName),'%s.visibility' %childShape)

    # scale R side -1 to get propper symmetrical behavior
    for each in (lipFlapList[0],lipFlapList[1]):
        if each == 'lipFlap_cup_ctrl':
            mc.setAttr('%s_%s.jointOrientY' %(sides[1],each) ,180 )
        else:
            mc.setAttr('%s_%s_orig.scale' %(sides[1],each) ,-1,-1,-1)

    for side in sides[1]:
        root = '%s_%s_root' %(side,lipFlapOrig)
        allChilds = mc.listRelatives(root,c=True,typ='transform',ad=True)
        allChilds.reverse()
        for child in allChilds:
            stripName = child.rsplit('_',1)[-1]   
            if stripName == 'orig' or  stripName == 'dKeyAll' or stripName == 'dKeyTip' :
                mc.setAttr('%s.scale' %child , -1,-1,-1)
                
    #reparent all flaps inside mouthSquash
    for side in sides:
        mc.parent('%s_%s_root' %(side,lipFlapOrig) ,'%s_%s_orig' %(side,lipflapAll) ,  mouthSquashSKN)
        mc.parent('%s_%s_orig' %(side,lipflapCup) , mouthSquashSKN )
        
    # --- create smart_flaps joints
    smartFlapsGrp = mc.group(n='flaps_smart_grp' , em=True)
    mc.parent(smartFlapsGrp ,'facial_fGrp')
    mc.setAttr('%s.inheritsTransform' %smartFlapsGrp , False)
    mc.select(cl=True)
    smartFlapsHoldJnt = mc.joint(n='flaps_smart_hold_jnt')
    mc.parent(smartFlapsHoldJnt,smartFlapsGrp)

    smartTrgt = ['%s_%s_root' %(sides[0],lipFlapOrig) ,'%s_%s_root' %(sides[1],lipFlapOrig),'%s_%s_root' %(sides[2],lipFlapOrig)]
    smartDupTargets = []
    for each in smartTrgt:
        newTrgt = mc.duplicate(each, n ='%s_smart' %each )[0]
        smartDupTargets.append(newTrgt)
    mc.parent(smartDupTargets,smartFlapsGrp)
    
    # --- add dkNode on top of nose_upCtrl
    noseUpDkey = mc.group( n = '{}_dKey'.format(noseUp), em=True)
    mc.parent(noseUpDkey,mouthSquashSKN)
    mc.setAttr('{}.translate'.format(noseUpDkey), 0,0,0)
    mc.parent(noseUpDkey,noseGrp)
    mc.parent(noseUpOrig, noseUpDkey)
     
    # --- goes into the hierarchy of duplicated Fks and counts the depth of the hierarchy. stops when arrived at end of hierarchy
    for i,each in enumerate(smartDupTargets): 
        nexChild = ''
        stopLoop = False
        for j in range(0,30):
            if j == 0:
                nexChild = each
            getChild = mc.listRelatives(nexChild,c=True,f=True)   
            if getChild:
                for child in getChild:
                    if mc.objectType(child) == 'nurbsCurve':
                        mc.delete(child)
               
                    else:
                        if mc.objectType(child) == 'joint':
                            splittedName1 = child.rsplit('|')[-1]                       
                            checkEnd = splittedName1.rsplit('_',1)[-1]

                            newName = mc.rename(child,'%s_smart' %splittedName1)
                            smartConnect(splittedName1,newName)                       

                            if not checkEnd == 'end':
                                nexChild = newName
                            else:
                                stopLoop = True
            if stopLoop == True:
                break
                
    # --- add dkNode on top of C_lipFlap_dKey
    CNoseSideDKeyAll = orig.orig(objlist=['C_lipFlap_ctrl_01_dKeyAll'], suffix=['_side'], origtype='transform', fromsel=False, viz=False, get_ssc=False, rtyp='auto')[0]
    CNoseSideDKeyAllSmart = orig.orig(objlist=['C_lipFlap_ctrl_01_dKeyAll_smart'], suffix=['_side'], origtype='transform', fromsel=False, viz=False, get_ssc=False, rtyp='auto')[0] 
    smartConnect(CNoseSideDKeyAll,CNoseSideDKeyAllSmart)
               
    #save lists in tempNode
    tempSaveGrp = mc.group(n='tempSaveGrp',em=True)
    mc.hide(tempSaveGrp)
    mc.addAttr(tempSaveGrp , ln='dKeyAllNodesList',dt='string')
    mc.addAttr(tempSaveGrp , ln='dKeyTipNodesList',dt='string')
    mc.setAttr('%s.dKeyAllNodesList' %tempSaveGrp , dKeyAllNodesList , type='string')
    mc.setAttr('%s.dKeyTipNodesList' %tempSaveGrp , dKeyTipNodesList , type='string')
    
    # --- do teeth generate
    teethGen.generateTeeth()


