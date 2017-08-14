
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