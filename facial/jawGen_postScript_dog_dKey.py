import maya.cmds as mc
import marsCore.shapes.defs as shapes
reload(shapes)
import marsCore.orig as orig
reload(orig)
from marsAutoRig_stubby.patch.customLib import patchLib as patchLib


#    sneer_tip_ctrl -->    nose_up_ctrl_dKey






#shapes.create( sel, shape= 'circle', size= 1, scale= [1, 1, 1 ], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= None, colorDegradeTo= None, replace= True, middle= False)
#orig.orig(objlist=[], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')
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
    noseUp = 'nose_up_ctrl'
    sneerTip = 'sneer_tip_ctrl'
    
    CUpperLip = 'C_upper_lip_ctrl'
    CUpperLipSideDkey = 'C_lipFlap_ctrl_01_dKeyAll_side'

    sides = ['L','R','C']
    lipFlapOrig = 'lipFlap_ctrl_01_orig'
    lipflapAll = 'lipFlap_all_ctrl'
    lipflapTip = 'lipFlap_tip_ctrl'
    lipflapCup = 'lipFlap_cup_ctrl'
    lipFlapList = [lipflapAll,lipflapTip,lipflapCup]

    allFlapsWeigts = ['lipFlap_all_inOut','lipFlap_all_UpDn','lipFlap_all_bwFw', 'lipFlap_all_rotX', 'lipFlap_all_rotY' , 'lipFlap_all_rotZ' ]
    tipFlapsWeigts = ['lipFlap_tip_inOut','lipFlap_tip_UpDn','lipFlap_tip_bwFw', 'lipFlap_tip_rotX', 'lipFlap_tip_rotY' , 'lipFlap_tip_rotZ' ]
    flapWeightsList = [allFlapsWeigts,tipFlapsWeigts]
    transformListBcs = ['translateX','translateY','translateZ', 'outValueX','outValueY','outValueZ']

    bcsNode = mc.ls('*_bcs' , type = 'DPK_bcs' )[0]


    #reparent cups inside flaps All
    for side in sides:
        mc.parent('%s_%s_orig' %(side,lipflapCup) , '%s_%s' %(side,lipflapAll) )


    # create drivenKeys on all dKeys nodes
    dKeyTrVals = [-2,0,2]
    dKeyRoVals = [-180,0,180]
    dKeyValsList = [dKeyTrVals,dKeyRoVals]

    axisList = ['X','Y','Z']
    transformList = ['translate','rotate']

    if mc.objExists('tempSaveGrp'):
        dKeyAllNodesList = eval(mc.getAttr('tempSaveGrp.dKeyAllNodesList'))
        dKeyTipNodesList = eval(mc.getAttr('tempSaveGrp.dKeyTipNodesList'))
            
        ## create dKeys on dKeyAll nodes
        for s , side in enumerate(sides):
            slaveNum = len(dKeyAllNodesList[s])
            ctrlName = '%s_%s' %(side,lipflapAll)
            targetList = dKeyAllNodesList[s]    
            
            for t , transform in enumerate(transformList):
                for a, axis in enumerate(axisList):  
                    for r , target in enumerate(targetList) :
                        valuesDivider = len(targetList)  
                        
                        if transform == 'rotate':                       
                            mc.setAttr('%s.%s%s' %(ctrlName,transform,axis) , 0 )
                            for value in dKeyValsList[t]:
                                mc.setAttr('%s.%s%s' %(ctrlName,transform,axis) , value )
                                mc.setAttr('%s.%s%s' %(target,transform,axis) , value/(valuesDivider/2) )
                                mc.setDrivenKeyframe( target , at='%s%s' %(transform,axis) , cd='%s.%s%s' %(ctrlName,transform,axis))
                            mc.setAttr('%s.%s' %(ctrlName,transform) ,0,0,0 )
                        elif transform == 'translate':
                            trFactor = mc.getAttr('%s_orig.scale' %ctrlName)[0]
                            
                            if not axis == 'Y':
                                if r>0:
                                    pass
                                else:
                                    mc.setAttr('%s.%s%s' %(ctrlName,transform,axis) , 0 )
                                    for value in dKeyValsList[t]:
                                        mc.setAttr('%s.%s%s' %(ctrlName,transform,axis) , value )
                                        mc.setAttr('%s.%s%s' %(target,transform,axis) , value*abs(trFactor[a]) )
                                        mc.setDrivenKeyframe( target , at='%s%s' %(transform,axis) , cd='%s.%s%s' %(ctrlName,transform,axis))
                                    mc.setAttr('%s.%s' %(ctrlName,transform) ,0,0,0 )
                            else:
                                mc.setAttr('%s.%s%s' %(ctrlName,transform,axis) , 0 )
                                for value in dKeyValsList[t]:
                                    mc.setAttr('%s.%s%s' %(ctrlName,transform,axis) , value )
                                    mc.setAttr('%s.%s%s' %(target,transform,axis) , value*abs(trFactor[a]) )
                                    mc.setDrivenKeyframe( target , at='%s%s' %(transform,axis) , cd='%s.%s%s' %(ctrlName,transform,axis))
                                mc.setAttr('%s.%s' %(ctrlName,transform) ,0,0,0 )
                        
                        mc.keyTangent(target,itt='linear',ott='linear')
                        
        ## create dKeys on dKeytip nodes
        for s , side in enumerate(sides):
            slaveNum = len(dKeyAllNodesList[s])
            ctrlName = '%s_%s' %(side,lipflapTip)
            targetList = dKeyTipNodesList[s]    
            
            for t , transform in enumerate(transformList):
                for a, axis in enumerate(axisList):  
                    for r , target in enumerate(targetList) :
                        valuesDivider = len(targetList)  
                        
                        if transform == 'rotate':                       
                            mc.setAttr('%s.%s%s' %(ctrlName,transform,axis) , 0 )
                            for value in dKeyValsList[t]:
                                mc.setAttr('%s.%s%s' %(ctrlName,transform,axis) , value )
                                mc.setAttr('%s.%s%s' %(target,transform,axis) , value/(valuesDivider/2) )
                                mc.setDrivenKeyframe( target , at='%s%s' %(transform,axis) , cd='%s.%s%s' %(ctrlName,transform,axis))
                            mc.setAttr('%s.%s' %(ctrlName,transform) ,0,0,0 )
                        elif transform == 'translate':
                            trFactor = mc.getAttr('%s_orig.scale' %ctrlName)[0]
                            
                            if not axis == 'Y':
                                if r>0:
                                    pass
                                else:
                                    mc.setAttr('%s.%s%s' %(ctrlName,transform,axis) , 0 )
                                    for value in dKeyValsList[t]:
                                        mc.setAttr('%s.%s%s' %(ctrlName,transform,axis) , value )
                                        mc.setAttr('%s.%s%s' %(target,transform,axis) , value*abs(trFactor[a]) )
                                        mc.setDrivenKeyframe( target , at='%s%s' %(transform,axis) , cd='%s.%s%s' %(ctrlName,transform,axis))
                                    mc.setAttr('%s.%s' %(ctrlName,transform) ,0,0,0 )
                            else:
                                mc.setAttr('%s.%s%s' %(ctrlName,transform,axis) , 0 )
                                for value in dKeyValsList[t]:
                                    mc.setAttr('%s.%s%s' %(ctrlName,transform,axis) , value )
                                    mc.setAttr('%s.%s%s' %(target,transform,axis) , value*abs(trFactor[a]) )
                                    mc.setDrivenKeyframe( target , at='%s%s' %(transform,axis) , cd='%s.%s%s' %(ctrlName,transform,axis))
                                mc.setAttr('%s.%s' %(ctrlName,transform) ,0,0,0 )
                        
                        mc.keyTangent(target,itt='linear',ott='linear')

        ## create additionnal Dkeys
        ### create nose up dKeyAllNodesList
        noseDkeyVals = [-2,0,2]
        mc.setAttr('{}_dKey.rotateY'.format(noseUp), 0)
        mc.setAttr('{}.translateX'.format(sneerTip), 0)
        for val in noseDkeyVals:
            mc.setAttr('{}.translateX'.format(sneerTip), val )
            mc.setAttr('{}_dKey.rotateY'.format(noseUp), val*1.5 )
            mc.setDrivenKeyframe( '{}_dKey'.format(noseUp) , at='rotateY' , cd='{}.translateX'.format(sneerTip))
        mc.setAttr('{}.translateX'.format(sneerTip), 0)
        ### create C_upperLip_side_dkey
        lipDkeyVals = [-1.5,0,1.5]
        axisList = ['X','Z']
        for axis in axisList:
            mc.setAttr('{}.translate{}'.format(CUpperLip,axis), 0)
            mc.setAttr('{}.translate{}'.format(CUpperLipSideDkey,axis), 0)
            for val in lipDkeyVals:
                mc.setAttr('{}.translate{}'.format(CUpperLip,axis), val)
                mc.setAttr('{}.translate{}'.format(CUpperLipSideDkey,axis), val*0.1)
                mc.setDrivenKeyframe( CUpperLipSideDkey , at='translate{}'.format(axis) , cd='{}.translate{}'.format(CUpperLip,axis) )
            mc.setAttr('{}.translate{}'.format(CUpperLip,axis), 0)
     
        mc.delete('tempSaveGrp')
        
            # add locks and translate limits to controls
        for side in sides:
            for lipFlap in (lipFlapList[0],lipFlapList[1]):
                patchLib.locksSwitch('%s_%s' %(side,lipFlap) ,T=False,R=False,S=True,V=False,lockdo='lock',keydo=False)
                mc.transformLimits( '%s_%s' %(side,lipFlap), tx=(-1, 1), ty=(-1, 1), tz=(-1, 1) )
                mc.transformLimits( '%s_%s' %(side,lipFlap), rx=(-180, 180), ry=(-180, 180), rz=(-180, 180) )
                mc.transformLimits( '%s_%s' %(side,lipFlap),etx=(True, True), ety=(True, True), etz=(True, True ) )
                mc.transformLimits( '%s_%s' %(side,lipFlap),erx=(True, True), ery=(True, True), erz=(True, True ) )
                createOvershootAttrLimit(['%s_%s' %(side,lipFlap)],['tx', 'ty', 'tz'])

        #connect flaps controls to bcs weights
        if bcsNode:
            for side in sides:
                for f , flap in enumerate(lipFlapList[0:2]):
                    flapCtrl = '%s_%s' %(side,flap)
                    
                    flapSR = mc.createNode('setRange' , n='%s_sr' %flapCtrl)
                    mc.connectAttr('%s.rotate' %flapCtrl , '%s.value' %flapSR)
                    mc.setAttr('%s.min' %flapSR , -2,-2,-2 )
                    mc.setAttr('%s.max' %flapSR , 2,2,2 )
                    mc.setAttr('%s.oldMin' %flapSR , -180,-180,-180 )
                    mc.setAttr('%s.oldMax' %flapSR , 180,180,180 )
                    
                    for w , weight in enumerate(flapWeightsList[f]):
                        if w < 3:
                            mc.connectAttr('%s.%s' %(flapCtrl,transformListBcs[w]) , '%s.%s_%s' %(bcsNode,weight,side) )
                        else :
                            mc.connectAttr('%s.%s' %(flapSR,transformListBcs[w]) , '%s.%s_%s' %(bcsNode,weight,side) )   
        
    else:
        print 'saveGrp missing, do jawGen dog befor creating dKeys'                

                