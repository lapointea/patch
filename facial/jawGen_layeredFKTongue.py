import maya.cmds as mc
import maya.mel as mel
import marsCore.orig as orig
import marsCore.shapes.defs as shapes
reload(shapes)
from marsAutoRig_stubby.patch.customLib import patchLib as patchLib
reload(patchLib)

#orig.orig(objlist=[], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')
#shapes.create( sel, shape= 'circle', size= 1, scale= [1, 1, 1 ], axis= 'y', twist= 0, offset= [0, 0, 0 ], color= None, colorDegradeTo= None, replace= True, middle= False)
###################################
def massConnect(source,trgt):
    mc.connectAttr('%s.translate' %source , '%s.translate' %trgt )
    mc.connectAttr('%s.rotate' %source , '%s.rotate' %trgt )
    mc.connectAttr('%s.scale' %source , '%s.scale' %trgt )
    if mc.objectType(source) == 'joint' :
        if mc.objectType(trgt) == 'joint' :
            mc.connectAttr('%s.jointOrient' %source , '%s.jointOrient' %trgt )


def xrivetTrOnNurbs(tr, surface, mainDirection = 1, out = 'worldSpace[0]', u = None, v = None,offsetOrient = [0, 0, 0],min=False):
    '''

    :param tr:
    :type tr: 
    :param surface:
    :type surface:
    :param mainDirection:
    :type mainDirection:
    :param out:
    :type out:
    :param u:
    :type u:
    :param v:
    :type v:
    :param offsetOrient:
    :type offsetOrient:
    :return:
    :rtype:
    '''
    attrsFrom = ['outTranslation', 'outRotation', 'outScale', 'outShear']
    attrsTo = ['translate', 'rotate', 'scale', 'shear']
    require_plugin = ['xRivet']
    for plugin in require_plugin:
        if not mc.pluginInfo(plugin, q = True, l = True):
            try:
                mc.loadPlugin(plugin, quiet = True)
            except:
                print 'warning : {0} plugin could not load'.format(plugin)
            return
    xRivet = '{0}_xRivetNurbs'.format(surface)
    if not mc.objExists(xRivet):
        xRivet = mc.createNode('xRivetNurbs', n = xRivet)
        mc.connectAttr('{0}.{1}'.format(surface, out), '{0}.inNurbsSurface'.format(xRivet))
    indexLast = getXrivetEntryAvailable(xRivet)
    if u != None and v != None:
        valU, valV = u, v
    else:
        valU, valV = getUvOnSurfaceFromeTr(tr, surface, out)

    # if min:
    #     valV/=2
    #print valV,'***********---------------'
    # xrivetTrans = mc.createNode('transform', n = tr + 'Xrivet')
    mc.setAttr('{0}.xRivetDatas[{1}].uValue'.format(xRivet, indexLast), valU)
    mc.setAttr('{0}.xRivetDatas[{1}].vValue'.format(xRivet, indexLast), valV)
    mc.setAttr('{0}.xRivetDatas[{1}].mainDirection'.format(xRivet, indexLast), mainDirection)
    mc.setAttr('{0}.xRivetDatas[{1}].stretchSquash'.format(xRivet, indexLast), 0)

    # for attrFrom, attrTo in zip(attrsFrom, attrsTo):
    #     mc.connectAttr('{0}.outputTransforms[{1}].{2}'.format(xRivet, indexLast, attrFrom),
    #                    '{0}.{1}'.format(xrivetTrans, attrTo))


    # mc.parentConstraint(xrivetTrans, tr, mo = True)
    mc.connectAttr('{0}.outputTransforms[{1}].{2}'.format(xRivet, indexLast, 'outTranslation'),
                   '{0}.{1}'.format(tr, 'translate'))

    addRot = mc.createNode('animBlendNodeAdditiveRotation', n = tr + 'AdditiveRotation')
    mc.setAttr(addRot + '.accumulationMode', 1)
    mc.connectAttr('{0}.outputTransforms[{1}].{2}'.format(xRivet, indexLast, 'outRotation'),
                   '{0}.{1}'.format(addRot, 'inputA'))
    mc.setAttr(addRot + '.inputB', *offsetOrient)
    mc.connectAttr(addRot + '.output', tr + '.rotate')
    # mc.pointConstraint(xrivetTrans, tr, mo = True)
    # mc.orientConstraint(xrivetTrans, tr, mo = True)

    return xRivet, indexLast
    
    
    
def getXrivetEntryAvailable(xrivet):
    """

    :param xrivet:
    :type xrivet:
    :return:
    :rtype:
    """
    norm = 17
    if mc.objectType(xrivet, i = 'xRivetNurbs'):
        norm = 8
    index = 0
    attrDatas = mc.listAttr(xrivet + '.xRivetDatas', m = True)
    if attrDatas:
        index = len(attrDatas) / norm
    return index
    
def getUvOnSurfaceFromeTr(tr, surface, out):
    '''

    :param tr:
    :type tr:
    :param surface:
    :type surface:
    :param out:
    :type out:
    :return:
    :rtype:
    '''
    closestTmp = mc.createNode('closestPointOnSurface', n = 'closestPointUVGetTmp')
    mc.connectAttr(surface + '.' + out, closestTmp + '.is')
    posi = mc.xform(tr, q = True, ws = True, t = True)
    mc.setAttr(closestTmp + '.ip', *posi)
    u, v = mc.getAttr(closestTmp + '.u'), mc.getAttr(closestTmp + '.v')
    mc.delete(closestTmp)
    #print '----------', v,'*******'
    return u, v
    
    
def getOffsetFromXrivet(aim, upv):
    '''

    :param aim:
    :type aim:
    :param upv:
    :type upv:
    :return:
    :rtype:
    '''
    offset = [0, 0, 0]
    if aim == 'x':
        if upv == 'y':
            offset[0:1] = [90]
        if upv == '-y':
            offset[0:1] = [-90]
        if upv == '-z':
            offset[0:1] = [-180]

    if aim == '-x':
        offset[2:3] = [-180]
        if upv == 'y':
            offset[0:1] = [-90]
        if upv == '-y':
            offset[0:1] = [90]
        if upv == 'z':
            offset[0:1] = [-180]

    if aim == 'y':
        offset[2:3] = [-90]
        if upv == 'x':
            offset[1:2] = [-90]
        if upv == '-x':
            offset[1:2] = [90]
        if upv == '-z':
            offset[1:2] = [-180]

    if aim == '-y':
        offset[2:3] = [90]
        if upv == 'x':
            offset[1:2] = [-90]
        if upv == '-x':
            offset[1:2] = [90]
        if upv == '-z':
            offset[1:2] = [-180]

    if aim == 'z':
        offset = [90, 90, 90]
        if upv == 'x':
            offset[1:2] = [-90]
        if upv == 'y':
            offset[1:2] = [0]
        if upv == '-y':
            offset[1:2] = [-180]

    if aim == '-z':
        offset = [90, 90, -90]
        if upv == 'x':
            offset[1:2] = [-180]
        if upv == 'y':
            offset[1:2] = [0]
        if upv == '-y':
            offset[1:2] = [-180]
    return offset


###################################

def doLayeredFkTongue():
    sides = ['L','R']
    facialFGrp = 'facial_fGrp'
    facialDriversGrp = 'facialDrivers'
    tongueRoot = 'tongue_jnt_1_orig'
    storeGroup = 'tongue_noXformGrp'
    headSKN = 'head_SKN'

    bcsNode = mc.ls(type= 'DPK_bcs')[0]
    headMeshShape = mel.eval('DPK_bcs -q -g %s' %bcsNode)[0]


    '''
    #get edges Manually
    getEdges = mc.ls(sl=True,fl=True)
    Edges = []
    for edge in getEdges:
        asciiName = edge.encode('ascii','ignore')
        Edges.append(asciiName)
    print Edges
    '''

    # get list of edges to generate base tongue surf
    lVertices = [u'head_hi_bcsObj.vtx[5677]', u'head_hi_bcsObj.vtx[5678]', u'head_hi_bcsObj.vtx[5683]', u'head_hi_bcsObj.vtx[5686]', u'head_hi_bcsObj.vtx[5689]', u'head_hi_bcsObj.vtx[5692]', u'head_hi_bcsObj.vtx[5693]', u'head_hi_bcsObj.vtx[5697]', u'head_hi_bcsObj.vtx[5699]', u'head_hi_bcsObj.vtx[5700]', u'head_hi_bcsObj.vtx[5710]', u'head_hi_bcsObj.vtx[5714]', u'head_hi_bcsObj.vtx[5715]', u'head_hi_bcsObj.vtx[5775]', u'head_hi_bcsObj.vtx[7369]', u'head_hi_bcsObj.vtx[7558]', u'head_hi_bcsObj.vtx[7561]', u'head_hi_bcsObj.vtx[7564]', u'head_hi_bcsObj.vtx[7567]', u'head_hi_bcsObj.vtx[7570]', u'head_hi_bcsObj.vtx[7572]', u'head_hi_bcsObj.vtx[7574]', u'head_hi_bcsObj.vtx[7576]', u'head_hi_bcsObj.vtx[7582]', u'head_hi_bcsObj.vtx[7586]', u'head_hi_bcsObj.vtx[7590]', u'head_hi_bcsObj.vtx[7600]', u'head_hi_bcsObj.vtx[8259]', u'head_hi_bcsObj.vtx[8291]', u'head_hi_bcsObj.vtx[8303]']
    rVertices = [u'head_hi_bcsObj.vtx[1274]', u'head_hi_bcsObj.vtx[1275]', u'head_hi_bcsObj.vtx[1280]', u'head_hi_bcsObj.vtx[1283]', u'head_hi_bcsObj.vtx[1286]', u'head_hi_bcsObj.vtx[1289]', u'head_hi_bcsObj.vtx[1290]', u'head_hi_bcsObj.vtx[1294]', u'head_hi_bcsObj.vtx[1296]', u'head_hi_bcsObj.vtx[1297]', u'head_hi_bcsObj.vtx[1307]', u'head_hi_bcsObj.vtx[1311]', u'head_hi_bcsObj.vtx[1312]', u'head_hi_bcsObj.vtx[1372]', u'head_hi_bcsObj.vtx[2966]', u'head_hi_bcsObj.vtx[3155]', u'head_hi_bcsObj.vtx[3158]', u'head_hi_bcsObj.vtx[3161]', u'head_hi_bcsObj.vtx[3164]', u'head_hi_bcsObj.vtx[3167]', u'head_hi_bcsObj.vtx[3169]', u'head_hi_bcsObj.vtx[3171]', u'head_hi_bcsObj.vtx[3173]', u'head_hi_bcsObj.vtx[3179]', u'head_hi_bcsObj.vtx[3183]', u'head_hi_bcsObj.vtx[3187]', u'head_hi_bcsObj.vtx[3197]', u'head_hi_bcsObj.vtx[3856]', u'head_hi_bcsObj.vtx[3888]', u'head_hi_bcsObj.vtx[3900]']
    lEdges = mc.polyListComponentConversion( lVertices , fv=True, te=True , internal = True)
    rEdges = mc.polyListComponentConversion( rVertices , fv=True, te=True , internal = True)
    edgesLists = [lEdges,rEdges]

    #creates store group for futur cleanup
    mc.group(n=storeGroup,em=True)
    mc.setAttr('%s.inheritsTransform' %storeGroup , False)
    mc.hide(storeGroup)
    mc.parent(storeGroup,facialFGrp)
    #create head_SKN decomposeMatrix for later use
    headSKMDM = mc.createNode('decomposeMatrix' , n='%s_dm' %headSKN )
    mc.connectAttr('%s.worldMatrix[0]' %headSKN , '%s.inputMatrix' %headSKMDM )


    #creates nodeBased surf from edges selection
    baseTongueLoft = mc.createNode('loft',n='tongueBase_loft')
    mc.setAttr('%s.autoReverse' %baseTongueLoft , False)
    tongueBaseSurf = mc.createNode('nurbsSurface',n='tongueBase_surfShape')
    mc.connectAttr('%s.outputSurface' %baseTongueLoft , '%s.create' %tongueBaseSurf)
    mc.parent(mc.listRelatives(tongueBaseSurf,p=True)[0],facialDriversGrp)

    petcList = []
    for i,list in enumerate(edgesLists):
        mc.select(list)
        baseTongueCrv = mc.polyToCurve(ch=True,degree=3,form=0,n='%s_tongueBase_crv' %sides[i] )
        baseTonguePetc = mc.rename(baseTongueCrv[1],'%s_tongueBase_petc' %sides[i])
        petcList.append(baseTonguePetc)
        curveShape = mc.listRelatives(baseTongueCrv[0],s=True)[0]
        mc.connectAttr('%s.outputcurve' %baseTonguePetc , '%s.inputCurve[%d]' %(baseTongueLoft,i) )
        mc.delete(baseTongueCrv[0])
        
    #Generate FK proxy hierarchy from template tongue
    ## get all tongue Pose nodes
    allTongueObj = mc.listRelatives(tongueRoot ,ad=True,type='transform')
    tonguePose = []
    for obj in allTongueObj:
        splitName = obj.rsplit('_',2)
        if splitName[1] == 'pose':
            tonguePose.append(obj)
    ## create FK proxy  hyerarchy
    ###creates proxy Nodes
    tonguePoseProxy = []
    for pose in tonguePose:
        mc.select(cl=True)
        newPose = mc.joint(n='%s_proxy' %pose)
        tonguePoseProxy.append(newPose)
        mc.setAttr('%s.radius' %newPose , 0.02)    
        newSkin = mc.duplicate(newPose,n=newPose.replace('pose','SKN'))
        mc.parent(newSkin,newPose)
        mewOrig = orig.orig(objlist=[newPose], suffix=['_orig'], origtype='joint', fromsel=False, viz=False, get_ssc=False, rtyp='auto')[0]
        mc.rename(mewOrig,mewOrig.replace('pose','jnt'))
        
    ### recreates parenting
    firstProxyNode = ''
    for pose in tonguePose:
        poseOrig = mc.listRelatives(pose,p=True)[0]
        poseProxy = '%s_proxy' %pose
        poseOrigProxy = mc.listRelatives(poseProxy,p=True)[0]
        
        poseOrigParent = mc.listRelatives(poseOrig,p=True)[0]
        poseOrigProxyParent = '%s_proxy' %poseOrigParent
        
        if not poseOrigParent  == 'jaw_SKN':
            mc.parent(poseOrigProxy,poseOrigProxyParent)
        elif poseOrigParent  == 'jaw_SKN':
            firstProxyNode = poseOrigProxy
            
    ### match proxy nodes on local nodes
    mc.parent(firstProxyNode,'jaw_SKN')
    firstNode = firstProxyNode.replace('_proxy', '')
    patchLib.smartcopyAttr(firstNode,firstProxyNode)

    allProxyNodes = mc.listRelatives(firstProxyNode,ad=True)
    for node in allProxyNodes:
        rigNode = node.replace('_proxy', '')
        patchLib.smartcopyAttr(rigNode,node)
        
    # create cns nodes
    tongueCns = []
    for pose in tonguePoseProxy:
        ### create cns and hooks hierarchy
        poseTest = int(pose.rsplit('_',2)[1])
        cnsNode = mc.group(n=pose.replace('proxy','cns') , em=True)
        mc.parent(cnsNode,pose,r=True)
        mc.parent(cnsNode,w=True)
        cnsHookNode = mc.duplicate(cnsNode,n=cnsNode.replace('cns','hook'))
        tongueCns.append(cnsNode)
        
        ### connect cns nodes to surface with Xrivet, then constraint proxy nodes to cns nodes
        surf = mc.listRelatives(tongueBaseSurf,p=True)[0]

        if poseTest <= (len(tonguePoseProxy)-3) :
            xRivet = xrivetTrOnNurbs(cnsNode, surf, mainDirection = 1, out = 'worldSpace[0]', u = None, v = None,offsetOrient = [0, 0, 0],min=False)
            mc.parentConstraint(cnsHookNode,pose,mo=True)
            massConnect(pose,pose.replace('_proxy' , ''))
            mc.connectAttr('%s.outputScale' %headSKMDM , '%s.scale' %cnsNode )
        else:
            mc.parentConstraint('jaw_SKN',cnsNode,mo=True)
            mc.parentConstraint(cnsHookNode,pose,mo=True)
            massConnect(pose,pose.replace('_proxy' , ''))
        mc.parent(cnsHookNode,cnsNode)
        
        ### connect local poseNodes rotate ORders to proxy rotate ORders
        source = pose.replace('_proxy','')
        mc.connectAttr('%s.rotateOrder' %source , '%s.rotateOrder' %pose) 
        
        #### cleanup
        mc.parent(cnsNode,storeGroup)
        