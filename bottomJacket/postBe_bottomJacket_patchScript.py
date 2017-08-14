def patch():
    # --- Bottom Jacket script --- #

    # --- Import / establish what's needed
    import maya.cmds as mc
    import marsCore.orig as orig
    reload(orig)
    import marsCore.shapes.defs as shapes
    reload(shapes)
    from marsAutoRig_stubby.patch.customLib import patchLib as patchLib
    reload(patchLib)
    #
    # --- check if rigTemplate is loaded before doing anything else
    botShirt = 'bottomJacket'
    rigTmplt = 'rigTemplate'
    if not mc.objExists('{0}_{1}'.format(botShirt, rigTmplt)):
        mc.warning('{0}_{1} did not exist, skipping {0} extra rig creation'.format(botShirt, rigTmplt))
    else:
        # --- sourcing any needed defs
        # --- v ----------------------------------------------- ADD  TAG ----------------------------------------------- v --- #
        def addTag(targets=[],tag=''):
            '''
            addTag(targets=[],tag='')
            addTag : wil add a string extra attribute, that will allow you to track back the object later
            '''
            taggedList = []
            for each in targets :
                Attr = tag
                if not mc.attributeQuery('%s.%s' %(each,Attr)):
                    mc.addAttr( each , ln = Attr , dt = 'string')
                    mc.setAttr('%s.%s' %(each,Attr) , l=True)
                    taggedList.append(each)
                else:
                    mc.warning('{0} already has attribute {1}'.format(rigSetMember, botShirt_tag))
            return taggedList
        # --- ^ ----------------------------------------------- ADD  TAG ----------------------------------------------- ^ --- #
        # --- v -------------------------------------------- xRIVETS SOURCE -------------------------------------------- v --- #
        #
        def xrivetTrOnNurbs(tr, surface, mainDirection=1, out='worldSpace[0]', u=None, v=None, offsetOrient=[0, 0, 0],
                            min=False):
            """
        
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
            """
            attrsFrom = ['outTranslation', 'outRotation', 'outScale', 'outShear']
            attrsTo = ['translate', 'rotate', 'scale', 'shear']
            require_plugin = ['xRivet']
            for plugin in require_plugin:
                if not mc.pluginInfo(plugin, q=True, l=True):
                    try:
                        mc.loadPlugin(plugin, quiet=True)
                    except:
                        print 'warning : {0} plugin could not load'.format(plugin)
                        return
            xRivet = '{0}_xRivetNurbs'.format(surface)
            if not mc.objExists(xRivet):
                xRivet = mc.createNode('xRivetNurbs', n=xRivet)
                mc.connectAttr('{0}.{1}'.format(surface, out), '{0}.inNurbsSurface'.format(xRivet))
            indexLast = getXrivetEntryAvailable(xRivet)
            if u != None and v != None:
                valU, valV = u, v
            else:
                valU, valV = getUvOnSurfaceFromeTr(tr, surface, out)
        
            # if min:
            #     valV/=2
            # print valV,'***********---------------'
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
        
            addRot = mc.createNode('animBlendNodeAdditiveRotation', n=tr + 'AdditiveRotation')
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
            if mc.objectType(xrivet, i='xRivetNurbs'):
                norm = 8
            index = 0
            attrDatas = mc.listAttr(xrivet + '.xRivetDatas', m=True)
            if attrDatas:
                index = len(attrDatas) / norm
            return index
        
        
        def getUvOnSurfaceFromeTr(tr, surface, out):
            """
        
            :param tr:
            :type tr:
            :param surface:
            :type surface:
            :param out:
            :type out:
            :return:
            :rtype:
            """
            closestTmp = mc.createNode('closestPointOnSurface', n='closestPointUVGetTmp')
            mc.connectAttr(surface + '.' + out, closestTmp + '.is')
            posi = mc.xform(tr, q=True, ws=True, t=True)
            mc.setAttr(closestTmp + '.ip', *posi)
            u, v = mc.getAttr(closestTmp + '.u'), mc.getAttr(closestTmp + '.v')
            mc.delete(closestTmp)
            # print '----------', v,'*******'
            return u, v
        
        
        def getOffsetFromXrivet(aim, upv):
            """
        
            :param aim:
            :type aim:
            :param upv:
            :type upv:
            :return:
            :rtype:
            """
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
        #
        # --- ^ -------------------------------------------- xRIVETS SOURCE -------------------------------------------- ^ --- #
        #
    
        # --- PRE RIG --- #
        # --- creating creation set for easy clearing or managing, on creation, add everything here as you build
        rigSet = 'RIG_created_set'
        
        if not mc.objExists(rigSet):
            mc.sets(n=rigSet)
        else:
            mc.warning('skipping, {0} already exists'.format(rigSet))
        #
        # --- creating rig trash and rig world groups
        rigGroups = ['{0}_RIG_HELP'.format(botShirt), '{0}_noXformGrp'.format(botShirt)]
        for rigGroup in rigGroups:
            if not mc.objExists('{0}'.format(rigGroup)):
                mc.group(empty=True, n='{0}'.format(rigGroup))
                mc.sets('{0}'.format(rigGroup), e=True, fe=rigSet)
            else:
                mc.warning('skipping, {0} already exists'.format(rigGroup))
        
        # --- creating rig world groups
        rigWorldGroups = ['{0}_rig_world_jnts_grp'.format(botShirt), '{0}_rig_world_FKL_locs_grp'.format(botShirt),
                          '{0}_rig_world_crvs_grp'.format(botShirt), '{0}_rig_world_surfs_grp'.format(botShirt),
                          '{0}_rig_world_rivets_grp'.format(botShirt)]
        for rigWorldGroup in rigWorldGroups:
            if not mc.objExists('{0}'.format(rigWorldGroup)):
                mc.group(empty=True, n='{0}'.format(rigWorldGroup))
                mc.parent('{0}'.format(rigWorldGroup), '{0}'.format(rigGroups[1]))
                mc.sets('{0}'.format(rigWorldGroup), e=True, fe=rigSet)
            else:
                mc.warning('skipping, {0} already exists'.format(rigWorldGroup))
        
        # --- creating rig trash groups and rig help grps
        rigTrashGroups = ['{0}_temp_locs_grp'.format(botShirt), '{0}_rig_proxy_skin_help_grp'.format(botShirt)]
        for rigTrashGroup in rigTrashGroups:
            if not mc.objExists('{0}'.format(rigTrashGroup)):
                mc.group(empty=True, n='{0}'.format(rigTrashGroup))
                mc.parent('{0}'.format(rigTrashGroup), '{0}'.format(rigGroups[0]))
                mc.sets('{0}'.format(rigTrashGroup), e=True, fe=rigSet)
            else:
                mc.warning('skipping, {0} already exists'.format(rigTrashGroup))
        # -------------------------------------------------------------------------------------------------------------------- #
        # - v - VARIABLES ############################################################################################## - v - #
        # -------------------------------------------------------------------------------------------------------------------- #
        #
        LRsides = ['L', 'R']
        letters = ['A', 'B', 'C', 'D']
        #
        xyzAttrs = ['x', 'y', 'z']
        XYZattrs = ['X', 'Y', 'Z']
        RGBattrs = ['R', 'G', 'B']
        #
        translates = ['tx', 'ty', 'tz']
        rots = ['rx', 'ry', 'rz']
        transforms = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
        allTransforms = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
        #
        # --- prefixes ------------------------------------------------------------------------------------------------------- #
        #
        center = 'C'
        centerLetter = 'E'
        #
        ctrl = 'ctrl'
        botShirt = 'bottomJacket'
        rigTmplt = 'rigTemplate'
        tag = 'tag'
        botShirt_tag = '{0}_{1}'.format(botShirt, tag)
        fkDynChain = 'fkDynChain'
        guide = 'GUIDE'
        FKlay = 'FKL'
        fk = 'FK'
        ik = 'IK'
        grp = 'grp'
        loc = 'loc'
        rivet = 'riv'
        origGrp = 'orig'
        poseGrp = 'pose'
        offsGrp = 'offset'
        hookGrp = 'hook'
        cnsGrp = 'cns'
        main = 'main'
        world = 'world'
        surf = 'surf'
        patch = 'patch'
        crv = 'crv'
        shape = 'Shape'
        shpOrig = 'Orig'
        mesh = 'mesh'
        geo = 'geo'
        sknJnt = 'SKN'
        hldSkn = 'holdSKN'
        proxySkn = 'proxySkn'
        rsltSkn = 'resultSKN'
        tweakJnt = 'tweakJnt'
        jointNode = 'jnt'
        target = 'tgt'
        ikHdl = 'ikh'
        eff = 'e'
        endJnt = 'end'
        poleVec = 'PV'
        cv = 'cv'
        sknSet = 'skin_set'
        animSet = 'anim_set'
        set = 'set'
        slidingSM = 'sliding_sm'
        dynChainAnimSet = '{0}_fkDynChain_ctrl_fk_set'.format(botShirt)
        botShirtSet = '{0}_{1}'.format(botShirt, set)
        L_botShirtSMset = '{0}_{1}_{2}_{3}'.format(LRsides[0], botShirt, slidingSM, set)
        R_botShirtSMset = '{0}_{1}_{2}_{3}'.format(LRsides[1], botShirt, slidingSM, set)
        #
        # --- nodes suffixes from rigging guidelines ------------------------------------------------------------------------- #
        #
        cfsi = 'cfsi'# - curveFromSurfaceIso
        multiplyDivideNode = 'md'
        plusMinusAverageNode = 'pma'
        reverseNode = 'rv'
        conditionNode = 'cond'
        blendTwoAttributesNode = 'bta'
        pairBlendNode = 'pb'
        decomposeMatrixNode = 'dm'
        composeMatrixNode = 'cm'
        multmatrixNode = 'mm'
        transformGeometryNode = 'tg'
        skinClusterNode = 'sc'
        addDoubleLinearNode = 'adl'
        multDoubleLinearNode = 'mdl'
        avgCurveNode = 'ac'
        blendColorsNode = 'bc'
        clampNode = 'cl'
        distanceBetweenNode = 'db'
        loftNode = 'loft'
        frameCacheNode = 'fc'
        choiceNode = 'ch'
        tweakNode = 'tweak'
        # -------------------------------------------------------------------------------------------------------------------- #
        
        # -------------------------------------------------------------------------------------------------------------------- #
        
        
        # - dynamic list for indexes to help with parenting from reverse or jntsNumbers list --------------------------------- #
        indexes = []
        
        # - dynamic list for jnts numbering / naming inside chains ----------------------------------------------------------- #
        rigJointsList = mc.listRelatives('{0}_{1}_{2}_{3}_01'.format(botShirt, fkDynChain, ctrl, guide), ad=True, type='joint')
        rigJointsList.reverse()
        rigJointsList.insert(0, '{0}_{1}_{2}_{3}_01'.format(botShirt, fkDynChain, ctrl, guide))
        rigJointsAmount = len(rigJointsList)
        
        
        
        # - dynamic list for jnts numbering / naming inside chains ----------------------------------------------------------- #
        # --- will give 01, 02, 03, [...] /// for rivetsHooks not to use the last end joint
        bonesNumbers = []
        bonesIndexes = []
        # --- will give 01, 02, 03 [...], end /// for hierarchy naming
        jntsNumbers = []
        # --- will give 01, 02, 03, 04, 05, 06, 07 (01 to rigJntsAmout +2)
        rsltBonesNumbers = []
        #
        for numbering in range(rigJointsAmount):
            # print numbering+1
            jntsNumbers.append('{:02d}'.format(numbering + 1))
            bonesNumbers.append('{:02d}'.format(numbering + 1))
            bonesIndexes.append('{0}'.format(numbering + 1))
            indexes.append('{0}'.format(numbering + 1))
            #
        # --- new to create more result skin joints adding one at each 1st and last 1/3rds
        for numbering in range(rigJointsAmount+2):
            #print numbering+1
            rsltBonesNumbers.append('{:02d}'.format(numbering))
        #
        # --- converting the bones index list from string to integers
        list(map(int, bonesIndexes))
        # - replacing last item of list from ## to end and making bones number count until before last
        jntsNumbers[-1] = 'end'
        # /// bonesNumbers = bonesNumbers[:-1] /// maybe I need to do for boneNumber in bonesNumbers[:-1]
        # creating the hierarchy into world ---------------------------------------------------------------------------------- #
        rigJnts = []
        rigBones = []
        dynPoseJnts = []
        dynChainJnts = []
        dynChainCtrls = []
        #
        # --- used to remove inverseScale connections -- #
        marsJnts = list(rigJnts+dynChainCtrls)
        marsInvSclConns = []
        # ---------------------------------------------- #
        #
        dynSknJntOffsets = []
        dynSknJnts = []
        dynSknTweaks = []
        dynTweaks = []
        for boneNumber in bonesNumbers:
            dynSknJnts.append('{0}_{1}_{2}_{3}_{4}'.format(botShirt, fkDynChain, sknJnt, boneNumber, world))
            dynChainCtrls.append('{0}_{1}_{2}_{3}'.format(botShirt, fkDynChain, ctrl, boneNumber))
            dynPoseJnts.append('{0}_{1}_{2}_{3}'.format(botShirt, fkDynChain, poseGrp, boneNumber))
            dynSknJntOffsets.append('{0}_{1}_{2}_{3}_{4}'.format(botShirt, fkDynChain, sknJnt, boneNumber, offsGrp))
            dynSknTweaks.append('{0}_{1}_{2}_{3}_{4}_{5}'.format(botShirt, fkDynChain, sknJnt, boneNumber, world, tweakJnt))
            dynTweaks.append('{0}_{1}_{2}_{3}_{4}'.format(botShirt, fkDynChain, sknJnt, boneNumber, tweakJnt))
            # --- adding what were previously lines 494+497 here to make sure calls are ealy enough
            rigBones.append('{0}_{1}_{2}_{3}_{4}_{5}'.format(center, botShirt, fk, centerLetter, ctrl, boneNumber))
            dynChainJnts.append('{0}_{1}_{2}_{3}'.format(botShirt, fkDynChain, sknJnt, boneNumber))
        #
        sknTweaks = dynChainJnts+dynSknJnts
        # /// TO CONFIRM if you want to remove the last one or use it /// dynSknJnts = dynSknJnts[:-1]
        vertsToSkin = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        # creating the list for rivets --------------------------------------------------------------------------------------- #
        rigRvts = []
        rsltJntsXrvts = []
        allRsltJntsXrvts = []
        # appending all for all final skn resulting joint
        allRsltSknJnts = []
        # indexCounters ------------------------------------------------------------------------------------------------------ #
        indexCounter = 0
        previousIndex = -1
        
        # iteration counter -------------------------------------------------------------------------------------------------- #
        iterationCounter = 0
        
        # varaibles for the auto generation of curves ------------------------------------------------------------------------ #
        jointsStarts = []
        jointsChains = []
        jointsPositions = []
        #
        jointsMarsStart = []
        #
        # create nurbs surface with skin joints to take into account for how many joints would be used for the rig ----------- #
        spansForJoints = rigJointsAmount - 1
        #
        botShirtMainWorldSurf = '{0}_{1}_{2}'.format(botShirt, main, surf)
        # --------------------------------------------------------------------------- #
        botShirtWorldPatchSurf = '{0}_{1}'.format(botShirt, patch)
        proxySknMesh = '{0}_{1}_{2}'.format(botShirt, proxySkn, mesh)
        nurbsPatches = []
        # -------------------------------------------------------------------------------------------------------------------- #
        #
        iToPop = [7, 5, 3, 1]
        # lofting around curves to create the main surface, list them in the proper order though
        #
        loftCrvs = []
        poppedOddIndexes = []
        reorderedLoftCrvs = []
        # --- same for proxy
        loftProxyCrvs = []
        # -------------------------------------------------------------------------------------------------------------------- #
        #
        # --- lists for hooks, locs and poseGrpJnts to parent the locs to the hooks and then connect the jnts to the locs
        hooksList = []
        locsList = []
        poseGrpsList = []
        worldPoseGrpsList = []
        # -------------------------------------------------------------------------------------------------------------------- #
        # --- required variables manipulations for auto positioning sknRsltJnts on patches
        # --------------------------------------------------------------------------- #
        uIndexes = list(map(int, indexes))
        uIndexes.insert(0, 0)
        # --- new to add extra joints at 1st and last 1/3rds
        uIndexes.append(uIndexes[-1]+1)
        vIndexes = [0, 1, 2, 3]# original was [0, 2] for 1st and mid, adding 1 and 3
        # --------------------------------------------------------------------------- #
        abcdLetters = ['A', 'B', 'C', 'D']
        dcbaLetters = ['D', 'C', 'B', 'A']
        # --------------------------------------------------------------------------- #
        nurbsPatches = []
        # --------------------------------------------------------------------------- #
        botShirtRsltSknJnts = []
        botShirtRsltSknGrps = []
        # --------------------------------------------------------------------------- #
        st4Index = 0
        st8Index = 0
        loftingIndex = 0
        # --------------------------------------------------------------------------- #
        uDfltValueCfsi = 0.5
        uValuesCfsi = []
        # --------------------------------------------------------------------------- #
        valueOf1 = -1
        idxToInsert = []
        #
        # --- transform to parent the grp containing all the xRivets into the rig /// this could be "hard coded" for simplicity
        resultRivetsGrpParent = '{0}_{1}_{2}'.format(botShirt, main, ctrl)
        #
        # ---------------------------------------- #
        vPoints = [0, 1, 2, 3, 4]
        uPoints = list(map(int, indexes))
        uPoints.insert(0, 0)
        uPoints.append(rigJointsAmount+1)
        uJoints = list(uPoints[:-2])
        # ---------------------------------------- #
        uJntIndexes = list(map(int, indexes))
        uJntIndexes = list(uJntIndexes[:-1])
        uJntIndexes.insert(0, 0)
        # ---------------------------------------- #
        rigWorldSknJnts = []
        for LRside in LRsides:
            #
            for letter in letters:
                rigWorldSknJnts.append('{0}_{1}_{2}_{3}_{4}'.format(LRside, botShirt, fk, letter, ctrl))
                #
        rigWorldSknJnts.append('{0}_{1}_{2}_{3}_{4}'.format(center, botShirt, fk, centerLetter, ctrl))
        # ---
        tempPops = []
        iToPop = [7, 6, 5, 4]
        # ---
        for i in iToPop:
            tempPops.append(rigWorldSknJnts.pop(i))
        # ---
        for pop in tempPops:
            rigWorldSknJnts.append(pop)
        # ---------------------------------------- #
        rigBotShirtParent = 'spine_ctrl_deform_SKN_00'
        # ---------------------------------------- #
        # --- inverse scaling for the FK chains ----------------------------- #
        # ----------------------------------- #
        ctrlsScl = []
        jntsInvScl = []
        # ----------------------------------- #
        for jntNumber in jntsNumbers[:-1]:
            ctrlsScl.append(jntNumber)
        for jntNumber in jntsNumbers[1:]:
            jntsInvScl.append(jntNumber)
        # ----------------------------------- #
        # ------------------------------------------------------------------- #
        # --------------------------------------------------------------------------------- #
        def pkOrig():
            #
            transforms = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
            items = mc.ls(sl=True)
            for item in items:
                mc.group(empty=True, n='{0}_orig'.format(item))
                mc.parent('{0}_orig'.format(item),
                          '{0}'.format(item))
                for transform in transforms:
                    mc.setAttr('{0}_orig.{1}'.format(item, transform), 0)
                mc.parent('{0}_orig'.format(item), w=True)
                itemDad = mc.listRelatives('{0}'.format(item), parent=True) or []
                mc.parent('{0}'.format(item),
                          '{0}_orig'.format(item))
                if not itemDad == []:
                    mc.parent('{0}_orig'.format(item), itemDad)
                else:
                    mc.warning('{0} had no parents, skipping orig reparenting'.format(item))
        # --------------------------------------------------------------------------------- #
        hipCtrl = 'hip_root_ctrl'
        #
        # ================================================================================= #
        # -------------------------------------------------------------------------------------------------------------------- #
        # - ^ - VARIABLES ############################################################################################## - ^ - #
        # -------------------------------------------------------------------------------------------------------------------- #
        
        #####################
        # --- RIG START --- #
        #####################
        
        # --- hide rigWorld group
        mc.hide('{0}_noXformGrp'.format(botShirt))
        # -------------------------------------------------------------------------------------------------------------------- #
        # establishing/appending into established variables / empty Lists
        #
        for LRside in LRsides:
            #
            for letter in letters:
                #
                for jntNumber in jntsNumbers:
                    #
                    rigJnts.append('{0}_{1}_{2}_{3}_{4}_{5}'.format(LRside, botShirt, fk, letter, ctrl, jntNumber))
                    #
                for boneNumber in bonesNumbers:
                    rigBones.append('{0}_{1}_{2}_{3}_{4}_{5}'.format(LRside, botShirt, fk, letter, ctrl, boneNumber))
                    #
        for jntNumber in jntsNumbers:
            #
            rigJnts.append('{0}_{1}_{2}_{3}_{4}_{5}'.format(center, botShirt, fk, centerLetter, ctrl, jntNumber))
        #
        # -------------------------------------------------------------------------------------------------------------------- #
        #
        # --- adding orig to end joint of mars chains
        for count, rigWorldSknJnt in enumerate(rigWorldSknJnts):
            if not mc.objExists('{0}_{1}_{2}'.format(rigWorldSknJnts[count], jntsNumbers[-1], origGrp)):
                mc.select('{0}_{1}'.format(rigWorldSknJnts[count], jntsNumbers[-1]))
                orig.orig(suffix=['_{0}'.format(origGrp)], origtype='transform', fromsel=True, viz=False, get_ssc=False, rtyp='auto')
                mc.select(deselect=True)
                if not mc.attributeQuery('uiRigGenereted', node='{0}_{1}_{2}'.format(rigWorldSknJnts[count], jntsNumbers[-1], origGrp), ex=True):
                    mc.addAttr('{0}_{1}_{2}'.format(rigWorldSknJnts[count], jntsNumbers[-1], origGrp), ln='uiRigGenereted', dt='string')
            else:
                mc.warning('orig already exists for {0}_{1}, skipping'.format(rigWorldSknJnts[count], jntsNumbers[-1]))
                if not mc.attributeQuery('uiRigGenereted', node='{0}_{1}_{2}'.format(rigWorldSknJnts[count], jntsNumbers[-1], origGrp), ex=True):
                    mc.addAttr('{0}_{1}_{2}'.format(rigWorldSknJnts[count], jntsNumbers[-1], origGrp), ln='uiRigGenereted', dt='string')
                else:
                    mc.warning('attribute uiRigGenereted already exists on {0}_{1}_{2}, skipping'.format(rigWorldSknJnts[count], jntsNumbers[-1], origGrp))
        #
        # creating the hierarchy into world
        #
        for count, rigJnt in enumerate(rigJnts):
            #
            mc.select('{0}'.format(rigJnts[count]))
            #
            # --- adding poseGrps to local rig
            orig.orig(objlist='{0}'.format(rigJnts[count]), suffix=['_{0}'.format(poseGrp)], origtype='transform', fromsel=True, viz=False, get_ssc=False, rtyp='auto')
            #
            # --- getting positionning infos
            ori = mc.xform('{0}'.format(rigJnts[count]), q=True, ra=True, ws=True)
            pos = mc.xform('{0}'.format(rigJnts[count]), q=True, t=True, ws=True)
            #
            # --- creating items at joints positions
            #
            mc.joint(n='{0}_{1}'.format(rigJnts[count], world), position=pos, orientation=ori, rad=0.2)
            #
            # --- doing origs
            orig.orig(suffix=['_{0}'.format(origGrp)], origtype='transform', fromsel=True, viz=False, get_ssc=False,
                      rtyp='auto')
            orig.orig(objlist='{0}_{1}'.format(rigJnts[count], world), suffix=['_{0}'.format(poseGrp)], origtype='transform',
                      fromsel=True, viz=False, get_ssc=False, rtyp='auto')
            #
            # --- adding creations to sets for later
            mc.sets(e=True, fe=rigSet)
            mc.select(deselect=True)
            #
            # --- adding in FK_layer locators creation ----------------------------------------------------------------------- #
            mc.spaceLocator(n='{0}_{1}_{2}'.format(rigJnts[count], FKlay, loc))
            for xyzAttr in xyzAttrs:
                mc.setAttr('{0}_{1}_{2}{3}.ls{4}'.format(rigJnts[count], FKlay, loc, shape, xyzAttr), 0.2)
            #
            # --- doing origs
            orig.orig(objlist='{0}_{1}_{2}'.format(rigJnts[count], FKlay, loc), suffix=['_{0}'.format(origGrp)],
                      origtype='transform', fromsel=True, viz=False, get_ssc=False, rtyp='auto')
            #
            # --- creating transforms hooks with their origs
            mc.createNode('transform', n='{0}_{1}_{2}'.format(rigJnts[count], FKlay, hookGrp))
            # --- doing origs
            orig.orig(objlist='{0}_{1}_{2}'.format(rigJnts[count], FKlay, hookGrp), suffix=['_{0}'.format(cnsGrp)],
                      origtype='transform', fromsel=True, viz=False, get_ssc=False, rtyp='auto')
            #
            # --- parenting into joints, zeroing-out and unparenting to have locators have the same orientation as the joints
            mc.parent('{0}_{1}_{2}_{3}'.format(rigJnts[count], FKlay, loc, origGrp), '{0}_{1}'.format(rigJnts[count], world))
            mc.parent('{0}_{1}_{2}_{3}'.format(rigJnts[count], FKlay, hookGrp, cnsGrp), '{0}_{1}'.format(rigJnts[count], world))
            #
            for transform in transforms:
                #
                # --- resetting FKlayer locators
                mc.setAttr('{0}_{1}_{2}_{3}.{4}'.format(rigJnts[count], FKlay, loc, origGrp, transform), 0)
                #
                # --- resetting hooks
                mc.setAttr('{0}_{1}_{2}_{3}.{4}'.format(rigJnts[count], FKlay, hookGrp, cnsGrp, transform), 0)
            #
            # --- unparenting FKlayer locators
            mc.parent('{0}_{1}_{2}_{3}'.format(rigJnts[count], FKlay, loc, origGrp), w=True)
            #
            # --- unparenting hooks rivets
            mc.parent('{0}_{1}_{2}_{3}'.format(rigJnts[count], FKlay, hookGrp, cnsGrp), w=True)
            #
            # --- adding shapes to transforms for rivets
            shapes.create('{0}_{1}_{2}'.format(rigJnts[count], FKlay, hookGrp), shape='circle', size=0.25, scale=[1, 1, 1],
                          axis='z', twist=0, offset=[0, 0, 0], color=18, colorDegradeTo=None, replace=True, middle=False)
            # ---------------------------------------------------------------------------------------------------------------- #
            #
            # --- creating transforms hooks with their origs # --- appending to list on seperate line to avoid [u'{0}]
            #
            rigRvts.append('{0}_{1}_{2}_{3}'.format(rigJnts[count], FKlay, hookGrp, cnsGrp))
            #
            hooksList.append('{0}_{1}_{2}'.format(rigJnts[count], FKlay, hookGrp))
            locsList.append('{0}_{1}_{2}'.format(rigJnts[count], FKlay, loc))
            poseGrpsList.append('{0}_{1}'.format(rigJnts[count], poseGrp))
            worldPoseGrpsList.append('{0}_{1}_{2}'.format(rigJnts[count], world, poseGrp))
            #
            # --- parenting under appropriate group in rig world
            #
            mc.parent('{0}_{1}_{2}'.format(rigJnts[count], world, origGrp), rigWorldGroups[0])
            mc.parent('{0}_{1}_{2}_{3}'.format(rigJnts[count], FKlay, loc, origGrp), rigWorldGroups[1])
            mc.parent('{0}_{1}_{2}_{3}'.format(rigJnts[count], FKlay, hookGrp, cnsGrp), rigWorldGroups[4])
            # --- adding to rig_created_set
            #
            mc.sets('{0}_{1}_{2}'.format(rigJnts[count], world, origGrp), e=True, fe=rigSet)
            mc.sets('{0}_{1}_{2}_{3}'.format(rigJnts[count], FKlay, loc, origGrp), e=True, fe=rigSet)
            mc.sets('{0}_{1}_{2}_{3}'.format(rigJnts[count], FKlay, hookGrp, cnsGrp), e=True, fe=rigSet)
            #
            # --- clearing selection
            mc.select(deselect=True)
        #
        # -------------------------------------------------------------------------------------------------------------------- #
        # --- same little bit of hierarchy of code for dynChain, this could go in the hierarchy from above once you clean
        #
        for count, dynChainJnt in enumerate(dynChainJnts):
            #
            # --- getting information for positioning
            mc.select('{0}'.format(dynChainJnts[count]))
            ori = mc.xform('{0}'.format(dynChainJnts[count]), q=True, ra=True, ws=True)
            pos = mc.xform('{0}'.format(dynChainJnts[count]), q=True, t=True, ws=True)
            #
            # --- creating items at joints positions
            #
            mc.joint(n='{0}_{1}'.format(dynChainJnts[count], world), position=pos, orientation=ori, rad=0.2)
            #
            # --- doing origs
            #
            orig.orig(suffix=['_{0}'.format(origGrp)], origtype='transform', fromsel=True, viz=False, get_ssc=False,
                      rtyp='auto')
            orig.orig(objlist='{0}_{1}'.format(dynChainJnts[count], world), suffix=['_{0}'.format(poseGrp)], origtype='transform',
                      fromsel=True, viz=False, get_ssc=False, rtyp='auto')
            #
            # --- adding creations to sets for later
            #
            mc.sets(e=True, fe=rigSet)
            mc.select(deselect=True)
            #
            # --- parenting under appropriate group in rig world
            #
            mc.parent('{0}_{1}_{2}'.format(dynChainJnts[count], world, origGrp), rigWorldGroups[0])
            #
            # --- adding to rig_created_set
            #
            mc.sets('{0}_{1}_{2}'.format(dynChainJnts[count], world, origGrp), e=True, fe=rigSet)
            #
            # --- clearing selection
            mc.select(deselect=True)
        # -------------------------------------------------------------------------------------------------------------------- #
        # -------------------------------------------------------------------------------------------------------------------- #
        # --- adding the offsetable sknJnts within the dynSkn chains for localised offsets locally and world
        #
        for count, sknTweak in enumerate(sknTweaks):
            #
            #print count
            #print sknTweak
            # --- getting information for positioning
            mc.select('{0}'.format(sknTweaks[count]))
            ori = mc.xform('{0}'.format(sknTweaks[count]), q=True, ra=True, ws=True)
            pos = mc.xform('{0}'.format(sknTweaks[count]), q=True, t=True, ws=True)
            #
            # --- creating items at joints positions
            mc.joint(n='{0}_{1}'.format(sknTweaks[count], tweakJnt), position=pos, orientation=ori, rad=0.2)
            #
            # --- doing origs
            orig.orig(suffix=['_{0}'.format(offsGrp)], origtype='transform', fromsel=True, viz=False, get_ssc=False,
                      rtyp='auto')
            # --- adding creations to sets for later
            #
            mc.sets(e=True, fe=rigSet)
            mc.sets('{0}_{1}_{2}'.format(sknTweaks[count], tweakJnt, offsGrp), e=True, fe=rigSet)
            #
            mc.select(deselect=True)
            #
        # -------------------------------------------------------------------------------------------------------------------- #
        # -------------------------------------------------------------------------------------------------------------------- #
        # parenting them all together
        #
        # this placement of iteration number is needed to make sure it starts at the right number
        iterationCounter = 0
        #
        for LRside in LRsides:
            #
            for letter in letters:
                #
                iterationCounter += 1
                #
                if iterationCounter < 9:
                    #print iterationCounter
                    for jntNumber in jntsNumbers:
                        #
                        indexCounter -= 1
                        previousIndex -= 1
                        #
                        if not previousIndex < -rigJointsAmount:
                            mc.parent('{0}_{1}_{2}_{3}_{4}_{5}_{6}_{7}'.format(LRsides[0], botShirt, fk, letter, ctrl,
                                                                               jntsNumbers[indexCounter], world, origGrp),
                                      '{0}_{1}_{2}_{3}_{4}_{5}_{6}'.format(LRsides[0], botShirt, fk, letter, ctrl,
                                                                           jntsNumbers[previousIndex], world))
                            mc.parent('{0}_{1}_{2}_{3}_{4}_{5}_{6}_{7}'.format(LRsides[1], botShirt, fk, letter, ctrl,
                                                                               jntsNumbers[indexCounter], world, origGrp),
                                      '{0}_{1}_{2}_{3}_{4}_{5}_{6}'.format(LRsides[1], botShirt, fk, letter, ctrl,
                                                                           jntsNumbers[previousIndex], world))
                            #
                            # --- locators same hierarchy
                            mc.parent('{0}_{1}_{2}_{3}_{4}_{5}_{6}_{7}_{8}'.format(LRsides[0], botShirt, fk, letter, ctrl,
                                                                                   jntsNumbers[indexCounter], FKlay, loc, origGrp),
                                      '{0}_{1}_{2}_{3}_{4}_{5}_{6}_{7}'.format(LRsides[0], botShirt, fk, letter, ctrl,
                                                                               jntsNumbers[previousIndex], FKlay, loc))
                            mc.parent('{0}_{1}_{2}_{3}_{4}_{5}_{6}_{7}_{8}'.format(LRsides[1], botShirt, fk, letter, ctrl,
                                                                                   jntsNumbers[indexCounter], FKlay, loc, origGrp),
                                      '{0}_{1}_{2}_{3}_{4}_{5}_{6}_{7}'.format(LRsides[1], botShirt, fk, letter, ctrl,
                                                                               jntsNumbers[previousIndex], FKlay, loc))
                            #
                        else:
                            mc.warning('previous index is outside range from negative jointsCount, passing to next loop and '
                                       'resetting indexCounter')
                            #
                            indexCounter = 0
                            previousIndex = -1
                            #
                    iterationCounter += 1
                elif iterationCounter == 9:
                    for jntNumber in jntsNumbers:
                        #
                        indexCounter -= 1
                        previousIndex -= 1
                        #
                        if not previousIndex < -rigJointsAmount:
                            mc.parent('{0}_{1}_{2}_{3}_{4}_{5}_{6}_{7}'.format(center, botShirt, fk, centerLetter, ctrl,
                                                                               jntsNumbers[indexCounter], world, origGrp),
                                      '{0}_{1}_{2}_{3}_{4}_{5}_{6}'.format(center, botShirt, fk, centerLetter, ctrl,
                                                                           jntsNumbers[previousIndex], world))
                            #
                            # --- locators same hierarchy
                            mc.parent('{0}_{1}_{2}_{3}_{4}_{5}_{6}_{7}_{8}'.format(center, botShirt, fk, centerLetter, ctrl,
                                                                                   jntsNumbers[indexCounter], FKlay, loc, origGrp),
                                      '{0}_{1}_{2}_{3}_{4}_{5}_{6}_{7}'.format(center, botShirt, fk, centerLetter, ctrl,
                                                                               jntsNumbers[previousIndex], FKlay, loc))
                        else:
                            mc.warning('previous index is outside range from negative jointsCount, passing to next loop and '
                                       'resetting indexCounter')
                            #
                            indexCounter = 0
                            previousIndex = -1
        # --- had to remove dynFkChain parenting from hierarchy above so its not withing letters loop
        # --- dynChain same hierarchy
        #
        for boneNumber in bonesNumbers:
            #
            indexCounter -= 1
            previousIndex -= 1
            #
            if not previousIndex < -rigJointsAmount:
                mc.parent('{0}_{1}_{2}_{3}_{4}_{5}'.format(botShirt, fkDynChain, sknJnt, bonesNumbers[indexCounter], world, origGrp),
                          '{0}_{1}_{2}_{3}_{4}'.format(botShirt, fkDynChain, sknJnt, bonesNumbers[previousIndex], world))
                    #
            else:
                mc.warning('previous index is outside range from negative jointsCount, passing to next loop and '
                           'resetting indexCounter')
                #
                indexCounter = 0
                previousIndex = -1
                #
        # -------------------------------------------------------------------------------------------------------------------- #
        # auto creating curves from joint chains to then loft around in proper order though for main surf creation from guide
        # using my world joints, because RIG: runs with origs as joints instead of transforms which wont work for me
        #
        # this placement of iteration number is needed to make sure it starts at the right number
        iterationCounter = 0
        #
        for LRside in LRsides:
            #
            for letter in letters:
                #
                if iterationCounter < 8:
                    #
                    iterationCounter += 1
                    #
                    jointsStarts.append('{0}_{1}_{2}_{3}_{4}_01_{5}'.format(LRsides[0], botShirt, fk, letter, ctrl, world))
                    jointsMarsStart.append('{0}_{1}_{2}_{3}_{4}_01_{5}'.format(LRsides[0], botShirt, fk, letter, ctrl, origGrp))
                    iterationCounter += 1
                    #
                    jointsStarts.append('{0}_{1}_{2}_{3}_{4}_01_{5}'.format(LRsides[1], botShirt, fk, letter, ctrl, world))
                    jointsMarsStart.append('{0}_{1}_{2}_{3}_{4}_01_{5}'.format(LRsides[1], botShirt, fk, letter, ctrl, origGrp))
                    #
                elif iterationCounter == 8:
                    iterationCounter += 1
                    jointsStarts.append('{0}_{1}_{2}_{3}_{4}_01_{5}'.format(center, botShirt, fk, centerLetter, ctrl, world))
                    jointsMarsStart.append('{0}_{1}_{2}_{3}_{4}_01_{5}'.format(center, botShirt, fk, centerLetter, ctrl, origGrp))
                    #
        # -------------------------------------------------------------------------------------------------------------------- #
        #
        for jointStart in jointsStarts:
            #
            jointsPositions = [mc.xform(jointStart, q=True, t=True, ws=True)]
            kids = mc.listRelatives(jointStart, ad=True, type='joint') or []
            #
            # reversing to have proper chain order
            kids.reverse()
            #
            for kid in kids:
                #
                jointsChains.append('{0}'.format(kid))
                #
                jointsPositions.append(mc.xform(kid, q=True, t=True, ws=True))
                #
            #
            #
            # ---------------------------------------------------------------------------------------------------------------- #
            # -- v -- inserting tangeant holding knots in curves ------ kind of dirty code here, but it's helper stuff -- v -- #
            # ---------------------------------------------------------------------------------------------------------------- #
            #
            currentChainItems = []
            currentChainItems.append(jointStart)
            for kid in kids:
                currentChainItems.append('{0}'.format(kid))
            #
            mc.spaceLocator(n='{0}_top'.format(jointStart))
            mc.spaceLocator(n='{0}_bot'.format(jointStart))
            #
            mc.pointConstraint([currentChainItems[0], currentChainItems[1]], '{0}_top'.format(jointStart), mo=False, n='top_ptCstr')
            mc.pointConstraint([currentChainItems[-1], currentChainItems[-2]], '{0}_bot'.format(jointStart), mo=False, n='bot_ptCstr')
            #
            mc.setAttr('top_ptCstr.w1', 0.333)
            mc.setAttr('bot_ptCstr.w1', 0.333)
            #
            mc.delete('top_ptCstr')
            mc.delete('bot_ptCstr')
            #
            jointsPositions.insert(1, mc.xform('{0}_top'.format(jointStart), q=True, t=True, ws=True))
            jointsPositions.insert(-1, mc.xform('{0}_bot'.format(jointStart), q=True, t=True, ws=True))
            #
            mc.parent('{0}_top'.format(jointStart), rigTrashGroups[0])
            mc.parent('{0}_bot'.format(jointStart), rigTrashGroups[0])
            #
            mc.sets('{0}_top'.format(jointStart), e=True, fe=rigSet)
            mc.sets('{0}_bot'.format(jointStart), e=True, fe=rigSet)
            #
            # ---------------------------------------------------------------------------------------------------------------- #
            # -- ^ -- inserting tangeant holding knots in curves ------ kind of dirty code here, but it's helper stuff -- ^ -- #
            # ---------------------------------------------------------------------------------------------------------------- #
            #
            #
            mc.curve(n='{0}_{1}'.format(jointStart, crv), d=3, p=jointsPositions)
            mc.parent('{0}_{1}'.format(jointStart, crv), rigWorldGroups[2])
            mc.sets('{0}_{1}'.format(jointStart, crv), e=True, fe=rigSet)
            #
            mc.select(deselect=True)
        # -------------------------------------------------------------------------------------------------------------------- #
        
        # -------------------------------------------------------------------------------------------------------------------- #
        # lofting around curves to create the main surface, list them in the proper order though
        #
        for jointStart in jointsStarts:
            loftCrvs.append('{0}_{1}'.format(jointStart, crv))
        #
        # this should be cleaner in one go. kept this way until I learn how to pop everything at once, or simply do proper loop
        #
        poppedOddIndexes.append(loftCrvs.pop(7))
        poppedOddIndexes.append(loftCrvs.pop(5))
        poppedOddIndexes.append(loftCrvs.pop(3))
        poppedOddIndexes.append(loftCrvs.pop(1))
        #
        reorderedLoftCrvs = loftCrvs + poppedOddIndexes
        #
        # --- lofting without keeping construction history
        mc.loft(reorderedLoftCrvs, n=botShirtMainWorldSurf, ch=1, u=1, c=0, ar=0, d=3, ss=1, rn=0, po=0, rsn=True)
        # -------------------------------------------------------------------------------------------------------------------- #
        #
        # --- renaming loft node and curve shapes
        #
        mc.rename(mc.listConnections('{0}_{1}_{2}{3}.create'.format(botShirt, main, surf, shape), d=False, s=True),
                  '{0}_{1}_{2}_{3}'.format(botShirt, main, surf, loftNode))
        #
        for reorderedLoftCrv in reorderedLoftCrvs:
            mc.rename(mc.listRelatives('{0}'.format(reorderedLoftCrv), c=True), '{0}{1}'.format(reorderedLoftCrv, shape))
        #
        mc.parent(botShirtMainWorldSurf, rigWorldGroups[3])
        mc.sets(botShirtMainWorldSurf, e=True, fe=rigSet)
        #
        # -------------------------------------------------------------------------------------------------------------------- #
        # --- auto skinning surface /// confirm with Julien if he wants the last jnt to skin --------------------------------- #
        # -------------------------------------------------------------------------------------------------------------------- #
        # --- adding in the skin holding joint and his world counterpart
        mc.select(deselect=True)
        mc.joint(n='{0}_{1}_{2}_{3}'.format(botShirt, main, ctrl, hldSkn), rad=0.2)
        orig.orig(suffix=['_{0}'.format(origGrp)], origtype='transform', fromsel=True, viz=False, get_ssc=False, rtyp='auto')
        mc.parent('{0}_{1}_{2}_{3}_{4}'.format(botShirt, main, ctrl, hldSkn, origGrp),
                  '{0}_{1}_{2}_01_{3}'.format(botShirt, fkDynChain, ctrl, origGrp))
        for step, transform in enumerate(transforms):
            mc.setAttr('{0}_{1}_{2}_{3}_{4}.{5}'.format(botShirt, main, ctrl, hldSkn, origGrp, transforms[step]), 0)
        #
        mc.select(deselect=True)
        mc.joint(n='{0}_{1}_{2}_{3}_{4}'.format(botShirt, main, ctrl, hldSkn, world), rad=0.2)
        orig.orig(suffix=['_{0}'.format(origGrp)], origtype='transform', fromsel=True, viz=False, get_ssc=False, rtyp='auto')
        mc.parent('{0}_{1}_{2}_{3}_{4}_{5}'.format(botShirt, main, ctrl, hldSkn, world, origGrp),
                  '{0}_{1}_{2}_01_{3}_{4}'.format(botShirt, fkDynChain, sknJnt, world, origGrp))
        for step, transform in enumerate(transforms):
            mc.setAttr('{0}_{1}_{2}_{3}_{4}_{5}.{6}'.format(botShirt, main, ctrl, hldSkn, world, origGrp, transforms[step]), 0)
        #
        # --- connecting them
        for step, allTransform in enumerate(allTransforms):
            mc.connectAttr('{0}_{1}_{2}_{3}.{4}'.format(botShirt, main, ctrl, hldSkn, allTransforms[step]),
                           '{0}_{1}_{2}_{3}_{4}.{5}'.format(botShirt, main, ctrl, hldSkn, world, allTransforms[step]))
        # --- appending to variables
        dynSknTweaks.append('{0}_{1}_{2}_{3}_{4}'.format(botShirt, main, ctrl, hldSkn, world))
        mc.sets('{0}_{1}_{2}_{3}'.format(botShirt, main, ctrl, hldSkn), e=True, fe=rigSet)
        mc.sets('{0}_{1}_{2}_{3}_{4}'.format(botShirt, main, ctrl, hldSkn, origGrp), e=True, fe=rigSet)
        mc.sets('{0}_{1}_{2}_{3}_{4}'.format(botShirt, main, ctrl, hldSkn, world), e=True, fe=rigSet)
        mc.sets('{0}_{1}_{2}_{3}_{4}_{5}'.format(botShirt, main, ctrl, hldSkn, world, origGrp), e=True, fe=rigSet)
        # -------------------------------------------------------------------------------------------------------------------- #
        # -------------------------------------------------------------------------------------------------------------------- #
        # --- deleting history before skinning
        mc.delete(botShirtMainWorldSurf, ch=True)
        # -------------------------------------------------------------------------------------------------------------------- #
        # -------------------------------------------------------------------------------------------------------------------- #
        # --- previously after skinning, moving before skinning to avoid having to do reset skin after direction change
        # --- from surf with hooks, running xRivets -------------------------------------------------------------------------- #
        #
        # --- ok, better to unparent the hooks, run the xRivets, and bring back the hooks so that they remain clean
        # --- unparenting hooks
        mc.parent(hooksList, w=True)
        #
        # --- running the xRivets
        for rigRvt in rigRvts:
        #    # print rigRvt
            xrivetTrOnNurbs(rigRvt, botShirtMainWorldSurf, mainDirection=1, out='worldSpace[0]', u=None, v=None,
                            offsetOrient=[0, 0, 0], min=False)
        #
        # --- parenting hooks back to get proper local offsets to remain as clean as generated, corresponding with the rig
        for count, hookList in enumerate(hooksList):
            #mc.parent('{0}'.format(hooksList[count]), w=True)
            mc.parent('{0}'.format(hooksList[count]), '{0}'.format(rigRvts[count]))
        # -------------------------------------------------------------------------------------------------------------------- #
        
        # --- from xRivets, parenting locators to hooks, and then connecting locs to jnts_poseGrps --------------------------- #
        #
        for count, hookList in enumerate(hooksList):
            # --- parent constraints
            mc.parentConstraint('{0}'.format(hooksList[count]),
                                '{0}'.format(locsList[count]))
            #
            # --- direct connection from fkLay locs to rig poseGrps
            for step, allTransform in enumerate(allTransforms):
                mc.connectAttr('{0}.{1}'.format(locsList[count], allTransforms[step]),
                               '{0}.{1}'.format(poseGrpsList[count], allTransforms[step]))
            #
            # --- direct connection from fkLay locs to world poseGrps
            for step, allTransform in enumerate(allTransforms):
                mc.connectAttr('{0}.{1}'.format(locsList[count], allTransforms[step]),
                               '{0}.{1}'.format(worldPoseGrpsList[count], allTransforms[step]))
        #
        # -------------------------------------------------------------------------------------------------------------------- #
        # --------------------------------------------------------------------------------------------------------- #
        # --- main surf --- setting direction U/V /// 0 = U /// 1 = V /// patches are better in V main U
        for r in range(len(mc.listRelatives('{0}_rig_world_rivets_grp'.format(botShirt), children=True))):
            mc.setAttr('{0}_main_surf_xRivetNurbs.xRivetDatas[{1}].mainDirection'.format(botShirt, r), 0)
        # --------------------------------------------------------------------------------------------------------- #
        # --- skinning lofted surface /// changed dynSknJnts to dynSknTweaks since request for offsetable ctrl
        mc.skinCluster(dynSknTweaks, botShirtMainWorldSurf, tsb=True, n='{0}_{1}'.format(botShirtMainWorldSurf, skinClusterNode))
        mc.rename(mc.listConnections('{0}{1}.tweakLocation'.format(botShirtMainWorldSurf, shape)),
                                     '{0}_{1}'.format(botShirtMainWorldSurf, tweakNode))
        
        # --- auto skinning surface /// confirm with Julien if he wants the last jnt to skin --------------------------------- #
        # /// adding in the 'tv' flag , _{5} tweakJnt since request for offsetable ctrl
        indexCounter = 0
        for count, boneNumber in enumerate(bonesNumbers):
            #
            if count == 0:
                # skin first two rows to first sknJnt
                for vertToSkin in vertsToSkin:
                    #
                    mc.skinPercent('{0}_{1}'.format(botShirtMainWorldSurf, skinClusterNode),
                                   '{0}.cv[0][{1}]'.format(botShirtMainWorldSurf, vertToSkin),
                                   tv=('{0}_{1}_{2}_{3}_{4}_{5}'.format(botShirt, fkDynChain, sknJnt, bonesNumbers[0],
                                                                        world, tweakJnt), 1))
                    #
                    mc.skinPercent('{0}_{1}'.format(botShirtMainWorldSurf, skinClusterNode),
                                   '{0}.cv[1][{1}]'.format(botShirtMainWorldSurf, vertToSkin),
                                   tv=('{0}_{1}_{2}_{3}_{4}_{5}'.format(botShirt, fkDynChain, sknJnt, bonesNumbers[0],
                                                                        world, tweakJnt), 1))
                    #
            if count <rigJointsAmount-1:
                # skin rows 2 to before 2 lasts to their respective joints
                #
                indexCounter = indexCounter+1
                #
                for vertToSkin in vertsToSkin:
                    #
                    mc.skinPercent('{0}_{1}'.format(botShirtMainWorldSurf, skinClusterNode),
                                   '{0}.cv[{1}][{2}]'.format(botShirtMainWorldSurf, bonesIndexes[indexCounter], vertToSkin),
                                   tv=('{0}_{1}_{2}_{3}_{4}_{5}'.format(botShirt, fkDynChain, sknJnt, bonesNumbers[indexCounter],
                                   world, tweakJnt), 1))
                    #
            elif count == rigJointsAmount-1:
                # skin last 2 rows to last jnts
                #
                for vertToSkin in vertsToSkin:
                    mc.skinPercent('{0}_{1}'.format(botShirtMainWorldSurf, skinClusterNode),
                                   '{0}.cv[{1}][{2}]'.format(botShirtMainWorldSurf, rigJointsAmount, vertToSkin),
                                   tv=('{0}_{1}_{2}_{3}_{4}_{5}'.format(botShirt, fkDynChain, sknJnt, bonesNumbers[-1],
                                   world, tweakJnt), 1))
                    #
                    mc.skinPercent('{0}_{1}'.format(botShirtMainWorldSurf, skinClusterNode),
                                   '{0}.cv[{1}][{2}]'.format(botShirtMainWorldSurf, rigJointsAmount+1, vertToSkin),
                                   tv=('{0}_{1}_{2}_{3}_{4}_{5}'.format(botShirt, fkDynChain, sknJnt, bonesNumbers[-1],
                                   world, tweakJnt), 1))
                    # --------------------------------------------------------------------------------------------------------- #
                    # --- replace onto holding joints
                    mc.skinPercent('{0}_{1}'.format(botShirtMainWorldSurf, skinClusterNode),
                                   '{0}.cv[0][{1}]'.format(botShirtMainWorldSurf, vertToSkin),
                                   tv=('{0}_{1}_{2}_{3}_{4}'.format(botShirt, main, ctrl, hldSkn, world), 1))
                    #
                    mc.skinPercent('{0}_{1}'.format(botShirtMainWorldSurf, skinClusterNode),
                                   '{0}.cv[1][{1}]'.format(botShirtMainWorldSurf, vertToSkin),
                                   tv=('{0}_{1}_{2}_{3}_{4}'.format(botShirt, main, ctrl, hldSkn, world), .85))
                    #
                    mc.skinPercent('{0}_{1}'.format(botShirtMainWorldSurf, skinClusterNode),
                                   '{0}.cv[2][{1}]'.format(botShirtMainWorldSurf, vertToSkin),
                                   tv=('{0}_{1}_{2}_{3}_{4}'.format(botShirt, main, ctrl, hldSkn, world), .15))
                    #
        
        
        # -------------------------------------------------------------------------------------------------------------------- #
        #
        # --- direct connect the rig ctrls to the world jnts
        #
        for count, rigJnt in enumerate(rigJnts):
            for step, allTransform in enumerate(allTransforms):
                # --- ctrls to world jnts
                mc.connectAttr('{0}.{1}'.format(rigJnts[count], allTransforms[step]),
                               '{0}_{1}.{2}'.format(rigJnts[count], world, allTransforms[step]))
        #
        # -------------------------------------------------------------------------------------------------------------------- #
        
        # --- direct connect fkDynChains from rig to world ------------------------------------------------------------------- #
        #
        for count, dynSknJnt in enumerate(dynSknJnts):
            for step, allTransform in enumerate(allTransforms):# --- replacing transforms by allTransforms
                mc.connectAttr('{0}.{1}'.format(dynPoseJnts[count], allTransforms[step]),
                               '{0}_{1}.{2}'.format(dynSknJnts[count], poseGrp, allTransforms[step]), f=True)
                # --- replacing dynChainCtrls by dyn actual SKN jnts to obtain dynamic dynChainCtrls->dynChainJnts
                mc.connectAttr('{0}.{1}'.format(dynChainJnts[count], allTransforms[step]),
                               '{0}.{1}'.format(dynSknJnts[count], allTransforms[step]), f=True)
        #
        # -------------------------------------------------------------------------------------------------------------------- #
        
        # --- kind of "patching" adding offsets grps to rig ctrls and their world equivalent --------------------------------- #
        for count, rigJnt in enumerate(rigJnts):
            mc.select(rigJnts[count])
            orig.orig(suffix=['_{0}'.format(offsGrp)], origtype='transform', fromsel=True, viz=False, get_ssc=False, rtyp='auto')
            mc.select('{0}_{1}'.format(rigJnts[count], world))
            orig.orig(suffix=['_{0}'.format(offsGrp)], origtype='transform', fromsel=True, viz=False, get_ssc=False, rtyp='auto')
            mc.select(deselect=True)
            #
            for step, allTransform in enumerate(allTransforms):# --- replacing trransforms by allTransforms
                mc.connectAttr('{0}_{1}.{2}'.format(rigJnts[count], offsGrp, allTransforms[step]),
                               '{0}_{1}_{2}.{3}'.format(rigJnts[count], world, offsGrp, allTransforms[step]), f=True)
        #
        # -------------------------------------------------------------------------------------------------------------------- #
        # --- direct connecting dynChain tweaks to their world equivalent
        for count, dynChainJnt in enumerate(dynChainJnts):
            for step, allTransform in enumerate(allTransforms):
                #
                mc.connectAttr('{0}_{1}.{2}'.format(dynChainJnts[count], tweakJnt, allTransforms[step]),
                               '{0}_{1}_{2}.{3}'.format(dynChainJnts[count], world, tweakJnt, allTransforms[step]))
                #
                mc.connectAttr('{0}_{1}_{2}.{3}'.format(dynChainJnts[count], tweakJnt, offsGrp, allTransforms[step]),
                               '{0}_{1}_{2}_{3}.{4}'.format(dynChainJnts[count], world, tweakJnt, offsGrp, allTransforms[step]))
        # -------------------------------------------------------------------------------------------------------------------- #
        # --- auto lofing as well as
        # --- auto positionning all results skn jnts with point positions to then xRivet and then skin ----------------------- #
        # --------------------------------------------------------------------------- #
        # --------------------------------------------------------------------------- #
        for count, reorderedLoftCrv in enumerate(reorderedLoftCrvs[:-1]):
            uValuesCfsi.append(uDfltValueCfsi+count)
            idxToInsert.append(valueOf1+2)
            valueOf1 = valueOf1+2
        # --------------------------------------------------------------------------- #
        crvsToLoft = list(reorderedLoftCrvs)
        # --------------------------------------------------------------------------- #
        rsltsOrigsGrps = []
        for count, rigWorldSknJnt in enumerate(rigWorldSknJnts):
            mc.select(deselect=True)
            mc.group(empty=True, n='{0}_{1}_{2}'.format(rigWorldSknJnts[count], rsltSkn, grp))
            mc.sets('{0}_{1}_{2}'.format(rigWorldSknJnts[count], rsltSkn, grp), e=True, fe=rigSet)
            rsltsOrigsGrps.append('{0}_{1}_{2}'.format(rigWorldSknJnts[count], rsltSkn, grp))
            mc.select(deselect=True)
        rsltsOrigsGrps.remove('{0}_{1}_{2}_{3}_{4}_{5}_{6}'.format(center, botShirt, fk, centerLetter, ctrl, rsltSkn, grp))
        if mc.objExists('{0}_{1}_{2}_{3}_{4}_{5}_{6}'.format(center, botShirt, fk, centerLetter, ctrl, rsltSkn, grp)):
            mc.delete('{0}_{1}_{2}_{3}_{4}_{5}_{6}'.format(center, botShirt, fk, centerLetter, ctrl, rsltSkn, grp))
        else:
            mc.warning('{0}_{1}_{2}_{3}_{4}_{5}_{6} did not exist, pass'.format(center, botShirt, fk, centerLetter, ctrl, rsltSkn, grp))
        # ============ #
        # ============ #
        # ============ #
        firstRowSknJnts = []
        
        for LRside in LRsides:
            #
            for letter in letters:
                for step, vIndex in enumerate(vIndexes):
                    firstRowSknJnts.append('{0}_{1}_{2}_{3}{4}_00_{5}'.format(LRside, botShirt, rsltSkn, letter, vIndexes[step], jointNode))
        # --------------------------------------------------------------------------- #
        #
        for count, reorderedLoftCrv in enumerate(reorderedLoftCrvs):
            if count<8:
                nextIndex = count+1
                # ------------------------------------------------------------------------------------------------------------------------- #
                if count<4:
                    #
                    # --- resetting variable to nothing, for loop specific dynamic listing
                    rsltJntsXrvts = []
                    # --- create curves from surface iso from main surf to get inbetweens curves for patches to have curvature
                    mc.sets(mc.createNode('curveFromSurfaceIso', n='{0}_{1}_{2}_{3}_{4}'.format(LRsides[0], botShirtWorldPatchSurf, abcdLetters[st4Index], surf, cfsi)), fe=rigSet)
                    mc.connectAttr('{0}{1}{2}.worldSpace[0]'.format(botShirtMainWorldSurf, shape, shpOrig),
                                   '{0}_{1}_{2}_{3}_{4}.inputSurface'.format(LRsides[0], botShirtWorldPatchSurf, abcdLetters[st4Index], surf, cfsi))# replaced <botShirtMainWorldSurf> by <botShirtMainWorldSurfCfsi> // removed {2} (shpOrig)
                    mc.setAttr('{0}_{1}_{2}_{3}_{4}.isoparmDirection'.format(LRsides[0], botShirtWorldPatchSurf, abcdLetters[st4Index], surf, cfsi), 0)
                    mc.setAttr('{0}_{1}_{2}_{3}_{4}.isoparmValue'.format(LRsides[0], botShirtWorldPatchSurf, abcdLetters[st4Index], surf, cfsi), uValuesCfsi[count])
                    mc.sets(mc.parent(mc.createNode('nurbsCurve', n='{0}_{1}_{2}_{3}_{4}_{5}{6}'.format(LRsides[0], botShirtWorldPatchSurf, abcdLetters[st4Index], surf, cfsi, crv, shape)), rigWorldGroups[2]), e=True, fe=rigSet)
                    mc.connectAttr('{0}_{1}_{2}_{3}_{4}.outputCurve'.format(LRsides[0], botShirtWorldPatchSurf, abcdLetters[st4Index], surf, cfsi),
                                   '{0}_{1}_{2}_{3}_{4}_{5}{6}.create'.format(LRsides[0], botShirtWorldPatchSurf, abcdLetters[st4Index], surf, cfsi, crv, shape))
                    crvsToLoft.insert(idxToInsert[count], '{0}_{1}_{2}_{3}_{4}_{5}'.format(LRsides[0], botShirtWorldPatchSurf, abcdLetters[st4Index], surf, cfsi, crv))
                    mc.loft([crvsToLoft[loftingIndex], crvsToLoft[loftingIndex+1], crvsToLoft[loftingIndex+2]],
                            n='{0}_{1}_{2}_{3}'.format(LRsides[0], botShirtWorldPatchSurf, abcdLetters[st4Index], surf),
                            ch=1, u=1, c=0, ar=0, d=3, ss=1, rn=0, po=0, rsn=True)
                    mc.rebuildSurface('{0}_{1}_{2}_{3}'.format(LRsides[0], botShirtWorldPatchSurf, abcdLetters[st4Index], surf), ch=1, rpo=1, rt=0, end=1, kr=0, kcp=1, kc=1, su=0, du=2, sv=0, dv=2, tol=0.01, fr=0, dir=2)
                    mc.delete('{0}_{1}_{2}_{3}'.format(LRsides[0], botShirtWorldPatchSurf, abcdLetters[st4Index], surf), ch=True)
                    #
                    rsltSurfXrvts='{0}_{1}_{2}_{3}'.format(LRsides[0], botShirtWorldPatchSurf, abcdLetters[st4Index], surf)
                    #
                    mc.sets('{0}_{1}_{2}_{3}'.format(LRsides[0], botShirtWorldPatchSurf, abcdLetters[st4Index], surf), e=True, fe=rigSet)
                    mc.parent('{0}_{1}_{2}_{3}'.format(LRsides[0], botShirtWorldPatchSurf, abcdLetters[st4Index], surf), rigWorldGroups[3])
                    nurbsPatches.append('{0}_{1}_{2}_{3}'.format(LRsides[0], botShirtWorldPatchSurf, abcdLetters[st4Index], surf))
                    # --------------------------------------------------------------------------------------------------------------------- #
                    for jumpst4, vIndex in enumerate(vIndexes):
                        rsltSknJnts = []
                        for stepst4, uIndex in enumerate(uIndexes):
                            #
                            # --- surface points coordinates
                            cvPP = mc.pointPosition('{0}_{1}_{2}_{3}.{4}[{5}][{6}]'.format(LRsides[0], botShirtWorldPatchSurf, abcdLetters[st4Index], surf, cv, uIndexes[stepst4], vIndexes[jumpst4]), w=True)
                            # --- joints from above's result
                            mc.select(deselect=True)
                            mc.joint(n='{0}_{1}_{2}_{3}{4}_{5}_{6}'.format(LRsides[0], botShirt, rsltSkn, abcdLetters[st4Index], vIndexes[jumpst4], rsltBonesNumbers[stepst4], jointNode), position= cvPP, rad=0.2)
                            orig.orig(suffix=['_{0}'.format(origGrp)], origtype='transform', fromsel=True, viz=False, get_ssc=False, rtyp='auto')
                            rsltJntsXrvts.append('{0}_{1}_{2}_{3}{4}_{5}_{6}_{7}'.format(LRsides[0], botShirt, rsltSkn, abcdLetters[st4Index], vIndexes[jumpst4], rsltBonesNumbers[stepst4], jointNode, origGrp))
                            rsltSknJnts.append('{0}_{1}_{2}_{3}{4}_{5}_{6}'.format(LRsides[0], botShirt, rsltSkn, abcdLetters[st4Index], vIndexes[jumpst4], rsltBonesNumbers[stepst4], jointNode))
                            allRsltJntsXrvts.append('{0}_{1}_{2}_{3}{4}_{5}_{6}_{7}'.format(LRsides[0], botShirt, rsltSkn, abcdLetters[st4Index], vIndexes[jumpst4], rsltBonesNumbers[stepst4], jointNode, origGrp))
                            allRsltSknJnts.append('{0}_{1}_{2}_{3}{4}_{5}_{6}'.format(LRsides[0], botShirt, rsltSkn, abcdLetters[st4Index], vIndexes[jumpst4], rsltBonesNumbers[stepst4], jointNode))
                            #
                            mc.parent(rsltJntsXrvts, '{0}'.format(rsltsOrigsGrps[count]))
                            #
                            mc.sets('{0}_{1}_{2}_{3}{4}_{5}_{6}_{7}'.format(LRsides[0], botShirt, rsltSkn, abcdLetters[st4Index], vIndexes[jumpst4], rsltBonesNumbers[stepst4], jointNode, origGrp), e=True, fe=rigSet)
                            mc.select(deselect=True)
                        #
                        # !!! -v- creating curves for proxy help mesh -v- !!! #
                        # insert loop here
                        #
                        jointsPositions = []
                        for rsltSknJnt in rsltSknJnts:
                            jointsPositions.append(mc.xform(rsltSknJnt, q=True, t=True, ws=True))
                        #
                        mc.curve(n='{0}_{1}'.format(rsltSknJnts[0], crv), d=3, p=jointsPositions)
                        #
                        mc.select(deselect=True)
                        mc.parent('{0}_{1}'.format(rsltSknJnts[0], crv), rigTrashGroups[1])
                        mc.sets('{0}_{1}'.format(rsltSknJnts[0], crv), e=True, fe=rigSet)
                        loftProxyCrvs.append('{0}_{1}'.format(rsltSknJnts[0], crv))
                        #
                        mc.select(deselect=True)
                        #
                        #
                        # !!! -^- creating curves for proxy help mesh -^- !!! #
                    #
                    st4Index +=1
                    loftingIndex +=2
                    #
                    # -------------------------------------------------------------------------------------------------------------------- #
                    # --- running the xRivets
                    for rsltJntXrvt in rsltJntsXrvts:
                        # print rigRvt
                        xrivetTrOnNurbs(rsltJntXrvt, '{0}'.format(rsltSurfXrvts), mainDirection=1, out='worldSpace[0]', u=None, v=None, offsetOrient=[0, 0, 0], min=False)
                    # -------------------------------------------------------------------------------------------------------------------- #
                # ------------------------------------------------------------------------------------------------------------------------- #
                else:
                    #
                    # --- resetting variable to nothing, for loop specific dynamic listing
                    rsltJntsXrvts = []
                    # --- create curves from surface iso from main surf to get inbetweens curves for patches to have curvature
                    mc.sets(mc.createNode('curveFromSurfaceIso', n='{0}_{1}_{2}_{3}_{4}'.format(LRsides[1], botShirtWorldPatchSurf, dcbaLetters[st8Index], surf, cfsi)), fe=rigSet)
                    mc.connectAttr('{0}{1}{2}.worldSpace[0]'.format(botShirtMainWorldSurf, shape, shpOrig),
                                   '{0}_{1}_{2}_{3}_{4}.inputSurface'.format(LRsides[1], botShirtWorldPatchSurf, dcbaLetters[st8Index], surf, cfsi))# replaced <botShirtMainWorldSurf> by <botShirtMainWorldSurfCfsi> // removed {2} (shpOrig)
                    mc.setAttr('{0}_{1}_{2}_{3}_{4}.isoparmDirection'.format(LRsides[1], botShirtWorldPatchSurf, dcbaLetters[st8Index], surf, cfsi), 0)
                    mc.setAttr('{0}_{1}_{2}_{3}_{4}.isoparmValue'.format(LRsides[1], botShirtWorldPatchSurf, dcbaLetters[st8Index], surf, cfsi), uValuesCfsi[count])
                    mc.sets(mc.parent(mc.createNode('nurbsCurve', n='{0}_{1}_{2}_{3}_{4}_{5}{6}'.format(LRsides[1], botShirtWorldPatchSurf, dcbaLetters[st8Index], surf, cfsi, crv, shape)), rigWorldGroups[2]), e=True, fe=rigSet)
                    mc.connectAttr('{0}_{1}_{2}_{3}_{4}.outputCurve'.format(LRsides[1], botShirtWorldPatchSurf, dcbaLetters[st8Index], surf, cfsi),
                                   '{0}_{1}_{2}_{3}_{4}_{5}{6}.create'.format(LRsides[1], botShirtWorldPatchSurf, dcbaLetters[st8Index], surf, cfsi, crv, shape))
                    crvsToLoft.insert(idxToInsert[count], '{0}_{1}_{2}_{3}_{4}_{5}'.format(LRsides[1], botShirtWorldPatchSurf, dcbaLetters[st8Index], surf, cfsi, crv))
                    mc.loft([crvsToLoft[loftingIndex], crvsToLoft[loftingIndex+1], crvsToLoft[loftingIndex+2]],
                            n='{0}_{1}_{2}_{3}'.format(LRsides[1], botShirtWorldPatchSurf, dcbaLetters[st8Index], surf),
                            ch=1, u=1, c=0, ar=0, d=3, ss=1, rn=0, po=0, rsn=True)
                    mc.rebuildSurface('{0}_{1}_{2}_{3}'.format(LRsides[1], botShirtWorldPatchSurf, dcbaLetters[st8Index], surf), ch=1, rpo=1, rt=0, end=1, kr=0, kcp=1, kc=1, su=0, du=2, sv=0, dv=2, tol=0.01, fr=0, dir=2)
                    mc.delete('{0}_{1}_{2}_{3}'.format(LRsides[1], botShirtWorldPatchSurf, dcbaLetters[st8Index], surf), ch=True)
                    #
                    rsltSurfXrvts='{0}_{1}_{2}_{3}'.format(LRsides[1], botShirtWorldPatchSurf, dcbaLetters[st8Index], surf)
                    #
                    mc.sets('{0}_{1}_{2}_{3}'.format(LRsides[1], botShirtWorldPatchSurf, dcbaLetters[st8Index], surf), e=True, fe=rigSet)
                    mc.parent('{0}_{1}_{2}_{3}'.format(LRsides[1], botShirtWorldPatchSurf, dcbaLetters[st8Index], surf), rigWorldGroups[3])
                    nurbsPatches.append('{0}_{1}_{2}_{3}'.format(LRsides[1], botShirtWorldPatchSurf, dcbaLetters[st8Index], surf))
                    # --------------------------------------------------------------------------------------------------------------------- #
                    for jumpst8, vIndex in enumerate(vIndexes):
                        rsltSknJnts = []
                        for stepst8, uIndex in enumerate(uIndexes):
                            #
                            # --- surface points coordinates
                            cvPP = mc.pointPosition('{0}_{1}_{2}_{3}.{4}[{5}][{6}]'.format(LRsides[1], botShirtWorldPatchSurf, dcbaLetters[st8Index], surf, cv, uIndexes[stepst8], vIndexes[jumpst8]), w=True)
                            # --- joints from above's result
                            mc.select(deselect=True)
                            mc.joint(n='{0}_{1}_{2}_{3}{4}_{5}_{6}'.format(LRsides[1], botShirt, rsltSkn, dcbaLetters[st8Index], vIndexes[jumpst8], rsltBonesNumbers[stepst8], jointNode), position= cvPP, rad=0.2)
                            orig.orig(suffix=['_{0}'.format(origGrp)], origtype='transform', fromsel=True, viz=False, get_ssc=False, rtyp='auto')
                            rsltJntsXrvts.append('{0}_{1}_{2}_{3}{4}_{5}_{6}_{7}'.format(LRsides[1], botShirt, rsltSkn, dcbaLetters[st8Index], vIndexes[jumpst8], rsltBonesNumbers[stepst8], jointNode, origGrp))
                            rsltSknJnts.append('{0}_{1}_{2}_{3}{4}_{5}_{6}'.format(LRsides[1], botShirt, rsltSkn, dcbaLetters[st8Index], vIndexes[jumpst8], rsltBonesNumbers[stepst8], jointNode))
                            allRsltJntsXrvts.append('{0}_{1}_{2}_{3}{4}_{5}_{6}_{7}'.format(LRsides[1], botShirt, rsltSkn, dcbaLetters[st8Index], vIndexes[jumpst8], rsltBonesNumbers[stepst8], jointNode, origGrp))
                            allRsltSknJnts.append('{0}_{1}_{2}_{3}{4}_{5}_{6}'.format(LRsides[1], botShirt, rsltSkn, dcbaLetters[st8Index], vIndexes[jumpst8], rsltBonesNumbers[stepst8], jointNode))
                            #
                            mc.parent(rsltJntsXrvts, '{0}'.format(rsltsOrigsGrps[count]))
                            #
                            mc.sets('{0}_{1}_{2}_{3}{4}_{5}_{6}_{7}'.format(LRsides[1], botShirt, rsltSkn, dcbaLetters[st8Index], vIndexes[jumpst8], rsltBonesNumbers[stepst8], jointNode, origGrp), e=True, fe=rigSet)
                            mc.select(deselect=True)
                        #
                        #
                        # !!! -v- creating curves for proxy help mesh -v- !!! #
                        # insert loop here
                        #
                        jointsPositions = []
                        for rsltSknJnt in rsltSknJnts:
                            jointsPositions.append(mc.xform(rsltSknJnt, q=True, t=True, ws=True))
                        #
                        mc.curve(n='{0}_{1}'.format(rsltSknJnts[0], crv), d=3, p=jointsPositions)
                        #
                        #mc.select(deselect=True)
                        mc.parent('{0}_{1}'.format(rsltSknJnts[0], crv), rigTrashGroups[1])
                        mc.sets('{0}_{1}'.format(rsltSknJnts[0], crv), e=True, fe=rigSet)
                        loftProxyCrvs.append('{0}_{1}'.format(rsltSknJnts[0], crv))
                        #
                        mc.select(deselect=True)
                        #
                        #
                        # !!! -^- creating curves for proxy help mesh -^- !!! #
                    st8Index +=1
                    loftingIndex +=2
                    #
                    # -------------------------------------------------------------------------------------------------------------------- #
                    # --- running the xRivets
                    for rsltJntXrvt in rsltJntsXrvts:
                        # print rigRvt
                        xrivetTrOnNurbs(rsltJntXrvt, '{0}'.format(rsltSurfXrvts), mainDirection=1, out='worldSpace[0]', u=None, v=None, offsetOrient=[0, 0, 0], min=False)
                    # -------------------------------------------------------------------------------------------------------------------- #
                #
            # ----------------------------------------------------------------------------------------------------------------------------- #
            if count==8:
                #
                # --- resetting variable to nothing, for loop specific dynamic listing
                rsltJntsXrvts = []
                rsltSknJnts = []
                # /// remove /// rsltSurfXrvts = []
                #
                for step8, uIndex in enumerate(uIndexes):
                    # --- surface points coordinates
                    cvPP = mc.pointPosition('{0}_{1}_A_{2}.{3}[{4}][4]'.format(LRsides[1], botShirtWorldPatchSurf, surf, cv, uIndexes[step8]), w=True)
                    # --- joints from above's result
                    mc.select(deselect=True)
                    mc.joint(n='{0}_{1}_{2}_A4_{3}_{4}'.format(LRsides[1], botShirt, rsltSkn, rsltBonesNumbers[step8], jointNode), position= cvPP, rad=0.2)
                    orig.orig(suffix=['_{0}'.format(origGrp)], origtype='transform', fromsel=True, viz=False, get_ssc=False, rtyp='auto')
                    rsltJntsXrvts.append('{0}_{1}_{2}_A4_{3}_{4}_{5}'.format(LRsides[1], botShirt, rsltSkn, rsltBonesNumbers[step8], jointNode, origGrp))
                    rsltSknJnts.append('{0}_{1}_{2}_A4_{3}_{4}'.format(LRsides[1], botShirt, rsltSkn, rsltBonesNumbers[step8], jointNode))
                    allRsltJntsXrvts.append('{0}_{1}_{2}_A4_{3}_{4}_{5}'.format(LRsides[1], botShirt, rsltSkn, rsltBonesNumbers[step8], jointNode, origGrp))
                    allRsltSknJnts.append('{0}_{1}_{2}_A4_{3}_{4}'.format(LRsides[1], botShirt, rsltSkn, rsltBonesNumbers[step8], jointNode))
                    #
                    mc.parent(rsltJntsXrvts, '{0}_{1}_{2}_{3}_{4}_{5}_{6}'.format(LRsides[1], botShirt, fk, letters[0], ctrl, rsltSkn, grp))
                    #
                    mc.sets('{0}_{1}_{2}_A4_{3}_{4}_{5}'.format(LRsides[1], botShirt, rsltSkn, rsltBonesNumbers[step8], jointNode, origGrp), e=True, fe=rigSet)
                    mc.select(deselect=True)
                #
                # !!! -v- creating curves for proxy help mesh -v- !!! #
                # insert loop here
                #
                jointsPositions = []
                for rsltSknJnt in rsltSknJnts:
                    jointsPositions.append(mc.xform(rsltSknJnt, q=True, t=True, ws=True))
                #
                mc.curve(n='{0}_{1}'.format(rsltSknJnts[0], crv), d=3, p=jointsPositions)
                #
                #mc.select(deselect=True)
                mc.parent('{0}_{1}'.format(rsltSknJnts[0], crv), rigTrashGroups[1])
                mc.sets('{0}_{1}'.format(rsltSknJnts[0], crv), e=True, fe=rigSet)
                loftProxyCrvs.append('{0}_{1}'.format(rsltSknJnts[0], crv))
                #
                mc.select(deselect=True)
                #
                #
                # !!! -^- creating curves for proxy help mesh -^- !!! #
                # -------------------------------------------------------------------------------------------------------------------- #
                # --- running the xRivets --------- R_botShirt_patch_A_surf
                for rsltJntXrvt in rsltJntsXrvts:
                    # print rigRvt
                    xrivetTrOnNurbs(rsltJntXrvt, '{0}_{1}_A_{2}'.format(LRsides[1], botShirtWorldPatchSurf, surf), mainDirection=1, out='worldSpace[0]', u=None, v=None, offsetOrient=[0, 0, 0], min=False)
                # -------------------------------------------------------------------------------------------------------------------- #
        #
        # -------------------------------------------------------------------------------------------------------------------- #
        # --- parenting rivets grp inside actual rig
        mc.group(rsltsOrigsGrps, n='{0}_{1}_{2}_{3}_{4}'.format(botShirt, rsltSkn, rivet, grp, origGrp))#replaced -- allRsltJntsXrvts
        mc.parent('{0}_{1}_{2}_{3}_{4}'.format(botShirt, rsltSkn, rivet, grp, origGrp), resultRivetsGrpParent)
        mc.hide('{0}_{1}_{2}_{3}_{4}'.format(botShirt, rsltSkn, rivet, grp, origGrp))
        #
        # --- adding grp to rigSet for deletion
        mc.sets('{0}_{1}_{2}_{3}_{4}'.format(botShirt, rsltSkn, rivet, grp, origGrp), e=True, fe=rigSet)
        # --- adding all skn jnts to rig creation set
        mc.sets(allRsltSknJnts, e=True, fe=rigSet)
        # -------------------------------------------------------------------------------------------------------------------- #
        # --------------------------------------------------------------------------------------------------------- #
        # --- for each patch surfs --- setting direction U/V /// 0 = U /// 1 = V /// patches are better in V main U
        for count, rsltOrigsGrp in enumerate(rsltsOrigsGrps):
            for r in range(len(mc.listRelatives('{0}'.format(rsltsOrigsGrps[count]), children=True))):
                #print r
                mc.setAttr('{0}_xRivetNurbs.xRivetDatas[{1}].mainDirection'.format(nurbsPatches[count], r), 1)
        # --------------------------------------------------------------------------------------------------------- #
        rigJntsTweaks = []
        rigJntsTweaksWorld = []
        
        # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx #
        # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx #
        
        # --- kind of "patching" adding offsets grps to rig ctrls and their world equivalent --------------------------------- #
        for count, rigJnt in enumerate(rigJnts):
            rigJntsTweaks.append('{0}_{1}'.format(rigJnts[count], tweakJnt))
            rigJntsTweaksWorld.append('{0}_{1}_{2}'.format(rigJnts[count], world, tweakJnt))
            #
            pos = mc.xform('{0}_{1}'.format(rigJnts[count], world), q=True, t=True, ws=True)
            #
            # --- creating items at joints positions
            mc.joint(n='{0}'.format(rigJntsTweaks[count]), rad=0.2)
            #
            # --- setting position through set attr in translate channels iterating within the xForm query (more legit)
            for step, translate in enumerate(translates):
                mc.setAttr('{0}.{1}'.format(rigJntsTweaks[count], translates[step]), pos[step])
            #
            # --- do Origs
            orig.orig(suffix=['_{0}'.format(offsGrp)], origtype='transform', fromsel=True, viz=False, get_ssc=False, rtyp='auto')
            #
            mc.sets('{0}'.format(rigJntsTweaks[count]), e=True, fe=rigSet)
            mc.sets('{0}_{1}'.format(rigJntsTweaks[count], offsGrp), e=True, fe=rigSet)
            #
            shapes.create('{0}'.format(rigJntsTweaks[count]), shape='sphere', size=0.25, scale=[1, 1, 1],
                          axis='y', twist=0, offset=[0, 0, 0], color=18, colorDegradeTo=None, replace=True, middle=False)
            #
            mc.select(deselect=True)
            #
        #
        # --- adding tweak 00 to hold very 1st row of CVs to preserve "hips" line through deformation (not getting S shapes at waist lvl)
        for count, rigWorldSknJnt in enumerate(rigWorldSknJnts):
            #
            pos = mc.xform('{0}_{1}_{2}_{3}'.format(rigWorldSknJnts[count], jntsNumbers[0], tweakJnt, offsGrp), q=True, t=True, ws=True)
            #
            mc.select(deselect=True)
            mc.joint(n='{0}_00_{1}'.format(rigWorldSknJnts[count], tweakJnt), rad=0.2)
            #
            for jump, translate in enumerate(translates):
                mc.setAttr('{0}_00_{1}.{2}'.format(rigWorldSknJnts[count], tweakJnt, translates[jump]), pos[jump])
            # --- do Origs
            orig.orig(suffix=['_{0}'.format(offsGrp)], origtype='transform', fromsel=True, viz=False, get_ssc=False, rtyp='auto')
            #
            mc.parent('{0}_00_{1}_{2}'.format(rigWorldSknJnts[count], tweakJnt, offsGrp),
                      '{0}_{1}_{2}'.format(rigWorldSknJnts[count], jntsNumbers[0], origGrp))#replacing offsGrp by origGrp
            #
            for rot in rots:
                mc.setAttr('{0}_00_{1}_{2}.{3}'.format(rigWorldSknJnts[count], tweakJnt, offsGrp, rot), 0)
            #
            mc.sets('{0}_00_{1}'.format(rigWorldSknJnts[count], tweakJnt), e=True, fe=rigSet)
            mc.sets('{0}_00_{1}_{2}'.format(rigWorldSknJnts[count], tweakJnt, offsGrp), e=True, fe=rigSet)
            #
            shapes.create('{0}_00_{1}'.format(rigWorldSknJnts[count], tweakJnt), shape='sphere', size=0.25, scale=[1, 1, 1],
                          axis='y', twist=0, offset=[0, 0, 0], color=18, colorDegradeTo=None, replace=True, middle=False)
            #
            mc.select(deselect=True)
        #
        # --- actually parentResetting them in their next joint in line, but parenting back in their respective parent for offset
        for count, rigWorldSknJnt in enumerate(rigWorldSknJnts):
            nextStep = 0
            for step, jntNumber in enumerate(jntsNumbers):
                nextStep +=1 
                if nextStep < rigJointsAmount:
                    #
                    mc.parent('{0}_{1}_{2}_{3}'.format(rigWorldSknJnts[count], jntsNumbers[step], tweakJnt, offsGrp),
                              '{0}_{1}_{2}'.format(rigWorldSknJnts[count], jntsNumbers[nextStep], offsGrp))# adding _{2} (offsGrp) to get pos from riv on surf
                    #
                    for transform in transforms:
                        #
                        mc.setAttr('{0}_{1}_{2}_{3}.{4}'.format(rigWorldSknJnts[count], jntsNumbers[step], tweakJnt, offsGrp, transform), 0)
                    #
                else:
                    mc.parent('{0}_{1}_{2}_{3}'.format(rigWorldSknJnts[count], jntsNumbers[step], tweakJnt, offsGrp),
                              '{0}_{1}_{2}'.format(rigWorldSknJnts[count], jntsNumbers[step], offsGrp))# adding _{2} (offsGrp) to get pos from riv on surf
                              #
                    for transform in transforms:
                        #
                        mc.setAttr('{0}_{1}_{2}_{3}.{4}'.format(rigWorldSknJnts[count], jntsNumbers[step], tweakJnt, offsGrp, transform), 0)
                    #
                #
            #
        #
        for count, rigWorldSknJnt in enumerate(rigWorldSknJnts):
            for step, jntNumber in enumerate(jntsNumbers):
                #
                mc.select('{0}_{1}_{2}_{3}'.format(rigWorldSknJnts[count], jntsNumbers[step], tweakJnt, offsGrp))
                orig.orig(suffix=['_{0}'.format(origGrp)], origtype='transform', fromsel=True, viz=False, get_ssc=False, rtyp='auto')
                mc.sets('{0}_{1}_{2}_{3}_{4}'.format(rigWorldSknJnts[count], jntsNumbers[step], tweakJnt, offsGrp, origGrp), e=True, fe=rigSet)
                mc.select(deselect=True)
        
        # --- cheap way of making before to last joints (jntsNumbers[-2] position be on the before last rows of CVs)
        for count, rigWorldSknJnt in enumerate(rigWorldSknJnts):
            #
            for step, jntNumber in enumerate(jntsNumbers[-3:]):
                #
                mc.parentConstraint(['{0}_{1}_{2}_{3}_{4}'.format(rigWorldSknJnts[count], jntsNumbers[-3:][0], tweakJnt, offsGrp, origGrp),
                                     '{0}_{1}_{2}_{3}_{4}'.format(rigWorldSknJnts[count], jntsNumbers[-3:][-1], tweakJnt, offsGrp, origGrp)], 
                                    '{0}_{1}_{2}_{3}_{4}'.format(rigWorldSknJnts[count], jntsNumbers[-3:][1], tweakJnt, offsGrp, origGrp), mo=False, n='tempConstraint')
                mc.setAttr('tempConstraint.w0', 0.333)
                mc.delete('tempConstraint')
        # -------------------------------------------------------------------------------------------------------------------- #
        
        
        # --- second loop for world equivalent --- technically this could be tastefully integrated in a better loop, but ok 4 now
        #
        for count, rigJnt in enumerate(rigJnts):
            #
            pos = mc.xform('{0}_{1}'.format(rigJnts[count], world), q=True, t=True, ws=True)
            #
            # --- creating items at joints positions
            mc.joint(n='{0}'.format(rigJntsTweaksWorld[count]), rad=0.2)
            #
            # --- setting position through set attr in translate channels iterating within the xForm query (more legit)
            for step, translate in enumerate(translates):
                mc.setAttr('{0}.{1}'.format(rigJntsTweaksWorld[count], translates[step]), pos[step])
            #
            # --- do Origs
            orig.orig(suffix=['_{0}'.format(offsGrp)], origtype='transform', fromsel=True, viz=False, get_ssc=False, rtyp='auto')
            #
            mc.sets('{0}'.format(rigJntsTweaksWorld[count]), e=True, fe=rigSet)
            mc.sets('{0}_{1}'.format(rigJntsTweaksWorld[count], offsGrp), e=True, fe=rigSet)
            #
            mc.select(deselect=True)
            #
        #
        # --- adding tweak 00 to hold very 1st row of CVs to preserve "hips" line through deformation (not getting S shapes at waist lvl)
        for count, rigWorldSknJnt in enumerate(rigWorldSknJnts):
            #
            pos = mc.xform('{0}_{1}_{2}_{3}_{4}'.format(rigWorldSknJnts[count], jntsNumbers[0], world, tweakJnt, offsGrp), q=True, t=True, ws=True)
            #
            mc.select(deselect=True)
            mc.joint(n='{0}_00_{1}_{2}'.format(rigWorldSknJnts[count], world, tweakJnt), rad=0.2)
            #
            for jump, translate in enumerate(translates):
                mc.setAttr('{0}_00_{1}_{2}.{3}'.format(rigWorldSknJnts[count], world, tweakJnt, translates[jump]), pos[jump])
            # --- do Origs
            orig.orig(suffix=['_{0}'.format(offsGrp)], origtype='transform', fromsel=True, viz=False, get_ssc=False, rtyp='auto')
            #
            mc.parent('{0}_00_{1}_{2}_{3}'.format(rigWorldSknJnts[count], world, tweakJnt, offsGrp),
                      '{0}_{1}_{2}_{3}'.format(rigWorldSknJnts[count], jntsNumbers[0], world, origGrp))#replacing offsGrp by origGrp
            #
            for rot in rots:
                mc.setAttr('{0}_00_{1}_{2}_{3}.{4}'.format(rigWorldSknJnts[count], world, tweakJnt, offsGrp, rot), 0)
            #
            mc.sets('{0}_00_{1}_{2}'.format(rigWorldSknJnts[count], world, tweakJnt), e=True, fe=rigSet)
            mc.sets('{0}_00_{1}_{2}_{3}'.format(rigWorldSknJnts[count], world, tweakJnt, offsGrp), e=True, fe=rigSet)
            #
            mc.select(deselect=True)
        #
        # --- actually parentResetting them in their next joint in line, but parenting back in their respective parent for offset
        for count, rigWorldSknJnt in enumerate(rigWorldSknJnts):
            nextStep = 0
            for step, jntNumber in enumerate(jntsNumbers):
                nextStep +=1 
                if nextStep < rigJointsAmount:
                    #
                    mc.parent('{0}_{1}_{2}_{3}_{4}'.format(rigWorldSknJnts[count], jntsNumbers[step], world, tweakJnt, offsGrp),
                              '{0}_{1}_{2}_{3}'.format(rigWorldSknJnts[count], jntsNumbers[nextStep], world, offsGrp))# --- adding {3} (offsGrp) to get riv on surf pos
                    #
                    for transform in transforms:
                        mc.setAttr('{0}_{1}_{2}_{3}_{4}.{5}'.format(rigWorldSknJnts[count], jntsNumbers[step], world, tweakJnt, offsGrp, transform), 0)
                    #
                else:
                    mc.parent('{0}_{1}_{2}_{3}_{4}'.format(rigWorldSknJnts[count], jntsNumbers[step], world, tweakJnt, offsGrp),
                              '{0}_{1}_{2}_{3}'.format(rigWorldSknJnts[count], jntsNumbers[step], world, offsGrp))# --- adding {3} (offsGrp) to get riv on surf pos
                              #
                    for transform in transforms:
                        mc.setAttr('{0}_{1}_{2}_{3}_{4}.{5}'.format(rigWorldSknJnts[count], jntsNumbers[step], world, tweakJnt, offsGrp, transform), 0)
                    #
                #
            #
        #
        for count, rigWorldSknJnt in enumerate(rigWorldSknJnts):
            for step, jntNumber in enumerate(jntsNumbers):
                mc.select('{0}_{1}_{2}_{3}_{4}'.format(rigWorldSknJnts[count], jntsNumbers[step], world, tweakJnt, offsGrp))
                orig.orig(suffix=['_{0}'.format(origGrp)], origtype='transform', fromsel=True, viz=False, get_ssc=False, rtyp='auto')
                mc.select(deselect=True)
        
        # --- cheap way of making before to last joints (jntsNumbers[-2] position be on the before last rows of CVs)
        for count, rigWorldSknJnt in enumerate(rigWorldSknJnts):
            #
            for step, jntNumber in enumerate(jntsNumbers[-3:]):
                #
                mc.parentConstraint(['{0}_{1}_{2}_{3}_{4}_{5}'.format(rigWorldSknJnts[count], jntsNumbers[-3:][0], world, tweakJnt, offsGrp, origGrp),
                                     '{0}_{1}_{2}_{3}_{4}_{5}'.format(rigWorldSknJnts[count], jntsNumbers[-3:][-1], world, tweakJnt, offsGrp, origGrp)],
                                    '{0}_{1}_{2}_{3}_{4}_{5}'.format(rigWorldSknJnts[count], jntsNumbers[-3:][1], world, tweakJnt, offsGrp, origGrp), mo=False, n='tempConstraint')
                mc.setAttr('tempConstraint.w0', 0.333)
                mc.delete('tempConstraint')
        # -------------------------------------------------------------------------------------------------------------------- #
        
        
        
        # -------------------------------------------------------------------------------------------------------------------- #
        # --- direct connecting the rig fk tweaks to their world equivalent
        for count, rigJnt in enumerate(rigJnts):
            for step, allTransform in enumerate(allTransforms):
                mc.connectAttr('{0}.{1}'.format(rigJntsTweaks[count], allTransforms[step]),
                               '{0}.{1}'.format(rigJntsTweaksWorld[count], allTransforms[step]))
                #
                mc.connectAttr('{0}_{1}.{2}'.format(rigJntsTweaks[count], offsGrp, allTransforms[step]),
                               '{0}_{1}.{2}'.format(rigJntsTweaksWorld[count], offsGrp, allTransforms[step]))
        #
        for count, rigWorldSknJnt in enumerate(rigWorldSknJnts):
            for step, allTransform in enumerate(allTransforms):
                mc.connectAttr('{0}_00_{1}.{2}'.format(rigWorldSknJnts[count], tweakJnt, allTransforms[step]),
                               '{0}_00_{1}_{2}.{3}'.format(rigWorldSknJnts[count], world, tweakJnt, allTransforms[step]))
                #
                mc.connectAttr('{0}_00_{1}_{2}.{3}'.format(rigWorldSknJnts[count], tweakJnt, offsGrp, allTransforms[step]),
                               '{0}_00_{1}_{2}_{3}.{4}'.format(rigWorldSknJnts[count], world, tweakJnt, offsGrp, allTransforms[step]))
        # -------------------------------------------------------------------------------------------------------------------- #
        # --- adding to anim sets the fk tweaks
        for LRside in LRsides:
            for letter in letters:
                for jntNumber in jntsNumbers:
                    mc.sets('{0}_{1}_{2}_{3}_{4}_{5}_{6}'.format(LRside, botShirt, fk, letter, ctrl, jntNumber, tweakJnt),
                            e=True, fe='{0}_{1}_{2}_{3}_{4}_fk_set'.format(LRside, botShirt, fk, letter, ctrl))
                #
                mc.sets('{0}_{1}_{2}_{3}_{4}_00_{5}'.format(LRside, botShirt, fk, letter, ctrl, tweakJnt),
                        e=True, fe='{0}_{1}_{2}_{3}_{4}_fk_set'.format(LRside, botShirt, fk, letter, ctrl))
                #
        for jntNumber in jntsNumbers:
            mc.sets('{0}_{1}_{2}_{3}_{4}_{5}_{6}'.format(center, botShirt, fk, centerLetter, ctrl, jntNumber, tweakJnt),
                    e=True, fe='{0}_{1}_{2}_{3}_{4}_fk_set'.format(center, botShirt, fk, centerLetter, ctrl))
        #
        mc.sets('{0}_{1}_{2}_{3}_{4}_00_{5}'.format(center, botShirt, fk, centerLetter, ctrl, tweakJnt),
                e=True, fe='{0}_{1}_{2}_{3}_{4}_fk_set'.format(center, botShirt, fk, centerLetter, ctrl))
        # -------------------------------------------------------------------------------------------------------------------- #
        # -------------------------------------------------------------------------------------------------------------------- #
        
        for count, nurbPatch in enumerate(nurbsPatches):
            #
            # --- deleting history, creatingSkinClusters, dynamically renaming tweaks - #
            #
            mc.delete(nurbsPatches[count], ch=True)
            #
            # --- small loop appending joints to add to skin
            patchesJntsInfluences = []
            for jntNumber in jntsNumbers:
                patchesJntsInfluences.append('{0}_00_{1}_{2}'.format(rigWorldSknJnts[count], world, tweakJnt))
                patchesJntsInfluences.append('{0}_{1}_{2}_{3}'.format(rigWorldSknJnts[count], jntNumber, world, tweakJnt))
            for jntNumber in jntsNumbers:
                patchesJntsInfluences.append('{0}_00_{1}_{2}'.format(rigWorldSknJnts[count+1], world, tweakJnt))
                patchesJntsInfluences.append('{0}_{1}_{2}_{3}'.format(rigWorldSknJnts[count+1], jntNumber, world, tweakJnt))
            #
            mc.skinCluster(patchesJntsInfluences, nurbsPatches[count], tsb=True, n='{0}_{1}'.format(nurbsPatches[count], skinClusterNode), mi=2, omi=True, bm=1, sm=1, nw=1)
            mc.setAttr('{0}_{1}.dqsSupportNonRigid'.format(nurbsPatches[count], skinClusterNode), 1)
            #
            mc.rename(mc.listConnections('{0}{1}.tweakLocation'.format(nurbsPatches[count], shape)),
                                         '{0}_{1}'.format(nurbsPatches[count], tweakNode))
        # -------------------------------------------------------------------------------------------------------------------------------------------- #    
        # --- auto skinning everything
        #
        # --- just making sure count gets properly reset
        # --- just making sure to have values at expected values
        count = 0
        nextCount = 1
        #
        for count, nurbPatch in enumerate(nurbsPatches):
            # --- Auto Skinning all the patches --------------------------------------- #
            #
            indexOffset = 1
            #
            for uPtCount, uPoint in enumerate(uPoints):
                #
                if uPtCount < 3:
                    #
                    if uPtCount < 2:
                        for vPtCount, vPoint in enumerate(vPoints):
                            #
                            for uJntCount, jntNumber in enumerate(jntsNumbers):
                                #
                                #
                                if vPtCount < 2:
                                    #
                                    mc.skinPercent('{0}_{1}'.format(nurbsPatches[count], skinClusterNode),
                                                   '{0}.{1}[{2}][{3}]'.format(nurbsPatches[count], cv, uPoints[uPtCount], vPoints[vPtCount]),
                                                   tv=('{0}_00_{1}_{2}'.format(rigWorldSknJnts[count], world, tweakJnt), 1))
                                    #
                                elif vPtCount == 2:
                                    #
                                    mc.skinPercent('{0}_{1}'.format(nurbsPatches[count], skinClusterNode),
                                                   '{0}.{1}[{2}][{3}]'.format(nurbsPatches[count], cv, uPoints[uPtCount], vPoints[vPtCount]),
                                                   tv=('{0}_00_{1}_{2}'.format(rigWorldSknJnts[count], world, tweakJnt), 1))
                                    mc.skinPercent('{0}_{1}'.format(nurbsPatches[count], skinClusterNode),
                                                   '{0}.{1}[{2}][{3}]'.format(nurbsPatches[count], cv, uPoints[uPtCount], vPoints[vPtCount]),
                                                   tv=('{0}_00_{1}_{2}'.format(rigWorldSknJnts[nextCount], world, tweakJnt), 0.5))
                                    #
                                elif vPtCount > 2:
                                    #
                                    mc.skinPercent('{0}_{1}'.format(nurbsPatches[count], skinClusterNode),
                                                   '{0}.{1}[{2}][{3}]'.format(nurbsPatches[count], cv, uPoints[uPtCount], vPoints[vPtCount]),
                                                   tv=('{0}_00_{1}_{2}'.format(rigWorldSknJnts[nextCount], world, tweakJnt), 1))
                    #
                    else:
                        for vPtCount, vPoint in enumerate(vPoints):
                            #
                            for uJntCount, jntNumber in enumerate(jntsNumbers):
                                #
                                #
                                if vPtCount < 2:
                                    #
                                    mc.skinPercent('{0}_{1}'.format(nurbsPatches[count], skinClusterNode),
                                                   '{0}.{1}[{2}][{3}]'.format(nurbsPatches[count], cv, uPoints[uPtCount], vPoints[vPtCount]),
                                                   tv=('{0}_{1}_{2}_{3}'.format(rigWorldSknJnts[count], jntsNumbers[0], world, tweakJnt), 1))
                                    #
                                elif vPtCount == 2:
                                    #
                                    mc.skinPercent('{0}_{1}'.format(nurbsPatches[count], skinClusterNode),
                                                   '{0}.{1}[{2}][{3}]'.format(nurbsPatches[count], cv, uPoints[uPtCount], vPoints[vPtCount]),
                                                   tv=('{0}_{1}_{2}_{3}'.format(rigWorldSknJnts[count], jntsNumbers[0], world, tweakJnt), 1))
                                    mc.skinPercent('{0}_{1}'.format(nurbsPatches[count], skinClusterNode),
                                                   '{0}.{1}[{2}][{3}]'.format(nurbsPatches[count], cv, uPoints[uPtCount], vPoints[vPtCount]),
                                                   tv=('{0}_{1}_{2}_{3}'.format(rigWorldSknJnts[nextCount], jntsNumbers[0], world, tweakJnt), 0.5))
                                    #
                                elif vPtCount > 2:
                                    #
                                    mc.skinPercent('{0}_{1}'.format(nurbsPatches[count], skinClusterNode),
                                                   '{0}.{1}[{2}][{3}]'.format(nurbsPatches[count], cv, uPoints[uPtCount], vPoints[vPtCount]),
                                                   tv=('{0}_{1}_{2}_{3}'.format(rigWorldSknJnts[nextCount], jntsNumbers[0], world, tweakJnt), 1))
                                #
                            #
                        #
                    #
                #
                else:
                    # uPtCount =>3
                    #
                    for vPtCount, vPoint in enumerate(vPoints):
                        #
                        if vPtCount < 2:
                            #
                            mc.skinPercent('{0}_{1}'.format(nurbsPatches[count], skinClusterNode),
                                           '{0}.{1}[{2}][{3}]'.format(nurbsPatches[count], cv, uPoints[uPtCount], vPoints[vPtCount]),
                                           tv=('{0}_{1}_{2}_{3}'.format(rigWorldSknJnts[count], jntsNumbers[indexOffset], world, tweakJnt), 1))
                            #
                        elif vPtCount == 2:
                            #
                            mc.skinPercent('{0}_{1}'.format(nurbsPatches[count], skinClusterNode),
                                           '{0}.{1}[{2}][{3}]'.format(nurbsPatches[count], cv, uPoints[uPtCount], vPoints[vPtCount]),
                                           tv=('{0}_{1}_{2}_{3}'.format(rigWorldSknJnts[count], jntsNumbers[indexOffset], world, tweakJnt), 1))
                            mc.skinPercent('{0}_{1}'.format(nurbsPatches[count], skinClusterNode),
                                           '{0}.{1}[{2}][{3}]'.format(nurbsPatches[count], cv, uPoints[uPtCount], vPoints[vPtCount]),
                                           tv=('{0}_{1}_{2}_{3}'.format(rigWorldSknJnts[nextCount], jntsNumbers[indexOffset], world, tweakJnt), 0.5))
                            #
                        elif vPtCount > 2:
                            #
                            mc.skinPercent('{0}_{1}'.format(nurbsPatches[count], skinClusterNode),
                                           '{0}.{1}[{2}][{3}]'.format(nurbsPatches[count], cv, uPoints[uPtCount], vPoints[vPtCount]),
                                           tv=('{0}_{1}_{2}_{3}'.format(rigWorldSknJnts[nextCount], jntsNumbers[indexOffset], world, tweakJnt), 1))
                            #
                        #
                    #
                    indexOffset +=1
                    #
                #
            #
            nextCount +=1
            #
        #
        # ================================================================================= #
        # --- adding sliding softMod :)
        cnt=0
        for cnt, LRside in enumerate(LRsides):
            #
            if cnt == 0:
                mainColor = 6
                subColor = 18
            else:
                mainColor = 13
                subColor = 20
            # --- clearing selection
            mc.select(deselect=True)
            # --- creating required joints and origs for softmods
            mc.joint(n='{0}_{1}_{2}_{3}'.format(LRside, slidingSM, offsGrp, ctrl), rad=0.2)
            pkOrig()
            mc.joint(n='{0}_{1}_{2}'.format(LRside, slidingSM, ctrl), rad=0.2)
            pkOrig()
            #
            # --- adding in locator
            fallofCenterLoc = mc.spaceLocator(n='{0}_{1}_{2}_{3}'.format(LRside, slidingSM, offsGrp, loc))
            mc.setAttr('{0}_{1}_{2}_{3}.visibility'.format(LRside, slidingSM, offsGrp, loc), 0)
            mc.parent(fallofCenterLoc, '{0}_{1}_{2}_{3}'.format(LRside, slidingSM, offsGrp, ctrl))
            #
            # --- clearing selection
            mc.select(deselect=True)
            #
            # --- adding to rigSet, animSet
            #
            mc.sets('{0}_{1}_{2}_{3}'.format(LRside, slidingSM, offsGrp, ctrl), e=True, fe=rigSet)
            mc.sets('{0}_{1}_{2}'.format(LRside, slidingSM, ctrl), e=True, fe=rigSet)
            mc.sets('{0}_{1}_{2}_{3}_{4}'.format(LRside, slidingSM, offsGrp, ctrl, origGrp), e=True, fe=rigSet)
            mc.sets('{0}_{1}_{2}_{3}'.format(LRside, slidingSM, ctrl, origGrp), e=True, fe=rigSet)
            mc.sets('{0}_{1}_{2}_{3}'.format(LRside, slidingSM, offsGrp, loc), e=True, fe=rigSet)
            #
            mc.sets('{0}_{1}_{2}_{3}'.format(LRside, slidingSM, offsGrp, ctrl), e=True, fe=rigSet)
            mc.sets('{0}_{1}_{2}'.format(LRside, slidingSM, ctrl), e=True, fe=rigSet)
            #
            # --- creating SM deformers on surface
            mc.softMod(botShirtMainWorldSurf, n='{0}_{1}'.format(LRside, slidingSM))
            #
            # --- clearing selection
            mc.select(deselect=True)
            #
            # --- adding controling attributes on ctrls
            mc.addAttr('{0}_{1}_{2}'.format(LRside, slidingSM, ctrl), ln='smRadius', at='double', min=0, dv=2)
            mc.setAttr('{0}_{1}_{2}.smRadius'.format(LRside, slidingSM, ctrl), e=True, k=True, cb=True)
            mc.addAttr('{0}_{1}_{2}'.format(LRside, slidingSM, ctrl), ln='smMode', at='enum', en='volume:surface')
            mc.setAttr('{0}_{1}_{2}.smMode'.format(LRside, slidingSM, ctrl), e=True, k=True, cb=True)
            #
            # --- establishing sm graph connections
            mc.connectAttr('{0}_{1}_{2}.worldMatrix[0]'.format(LRside, slidingSM, ctrl),
                           '{0}_{1}.matrix'.format(LRside, slidingSM), f=True)
            mc.connectAttr('{0}_{1}_{2}_{3}Shape.worldPosition[0]'.format(LRside, slidingSM, offsGrp, loc),
                           '{0}_{1}.falloffCenter'.format(LRside, slidingSM), f=True)
            mc.connectAttr('{0}_{1}_{2}_{3}.worldInverseMatrix[0]'.format(LRside, slidingSM, offsGrp, ctrl),
                           '{0}_{1}.bindPreMatrix'.format(LRside, slidingSM), f=True)
            mc.connectAttr('{0}_{1}_{2}.smRadius'.format(LRside, slidingSM, ctrl),
                           '{0}_{1}.falloffRadius'.format(LRside, slidingSM), f=True)
            mc.connectAttr('{0}_{1}_{2}.smMode'.format(LRside, slidingSM, ctrl),
                           '{0}_{1}.falloffMode'.format(LRside, slidingSM), f=True)
            #
            # --- clearing selection
            mc.select(deselect=True)
            #
            mc.parent('{0}_{1}HandleShape'.format(LRside, slidingSM),
                      '{0}_{1}_{2}'.format(LRside, slidingSM, ctrl), r=True, s=True)
            #
            # --- clearing selection
            mc.select(deselect=True)
            #
            if mc.objExists('{0}_{1}Handle'.format(LRside, slidingSM)):
                mc.delete('{0}_{1}Handle'.format(LRside, slidingSM))
            else:
                pass
            #
            # --- adding controller shapes
            shapes.create('{0}_{1}_{2}_{3}'.format(LRsides[cnt], slidingSM, offsGrp, ctrl),
                          shape='cube', size=1, scale=[1, 1, 1], axis='z', twist=0, offset=[0, 0, 0],
                          color=mainColor, colorDegradeTo=None, replace=True, middle=False)
            shapes.create('{0}_{1}_{2}'.format(LRsides[cnt], slidingSM, ctrl), shape='sphere', size=1,
                          scale=[1, 1, 1], axis='z', twist=0, offset=[0, 0, 0], color=subColor,
                          colorDegradeTo=None, replace=True, middle=False)
            #
            # --- clearing selection
            mc.select(deselect=True)
            #
            # --- parent inside thighs and set attr at 0.5* the value of the next joint in line
            mc.parent('{0}_{1}_{2}_{3}_{4}'.format(LRside, slidingSM, offsGrp, ctrl, origGrp),
                      '{0}_leg_01'.format(LRside))
            for transform in transforms:
                mc.setAttr('{0}_{1}_{2}_{3}_{4}.{5}'.format(LRside, slidingSM, offsGrp, ctrl, origGrp, transform), 0)
            mc.setAttr('{0}_{1}_{2}_{3}_{4}.ty'.format(LRside, slidingSM, offsGrp, ctrl, origGrp),
                       0.5*mc.getAttr('{0}_leg_02.ty'.format(LRside)))
            #
            # --- hiding SM shape
            mc.hide('{0}_{1}HandleShape'.format(LRside, slidingSM))
        # -------------------------------------------------------------------------------------------------------------------- #
        # --- REMAINING CLEANING UP TO DO, TO DO
        #
        # -------------------------------------------------------------------------------------------------------------------- #
        # - [OK] - auto create/skin proxy geo of 1 vert per joints skinned at 1, max inf 1. Copy skin by proximity and booya!- #
        # --- lofting without keeping construction history
        mc.loft(loftProxyCrvs, n='{0}_{1}'.format(proxySkn, surf), ch=1, u=1, c=0, ar=0, d=1, ss=1, rn=0, po=0, rsn=True)
        mc.nurbsToPoly('{0}_{1}'.format(proxySkn, surf), mnd=1, ch=0, f=3, pt=1, pc=200, chr=0.1, ft=0.01, mel=0.001,
                                        d=0.1, ut=1, un=3, vt=1, vn=3, uch=0, ucr=0, cht=0.2, es=0, ntr=0, mrt=0, uss=1,
                                        n=proxySknMesh)
        #
        # --- adding to help grps and rigSet
        mc.parent(proxySknMesh, rigTrashGroups[1])
        mc.sets(proxySknMesh, e=True, fe=rigSet)
        #
        # --- deleting temp loft surf
        if mc.objExists('{0}_{1}'.format(proxySkn, surf)):
            mc.delete('{0}_{1}'.format(proxySkn, surf))
        else:
            mc.warning('skipping, {0}_{1} didnt exist or was already removed'.format(proxySkn, surf))
        #
        mc.skinCluster(allRsltSknJnts, proxySknMesh, tsb=True, n='{0}_{1}'.format(proxySknMesh, skinClusterNode),
                       mi=1, omi=True, bm=1, sm=0, nw=1)
        mc.rename(mc.listConnections('{0}{1}.tweakLocation'.format(proxySknMesh, shape)),
                                     '{0}_{1}'.format(proxySknMesh, tweakNode))
        # -------------------------------------------------------------------------------------------------------------------- #
        #
        # - [OK] - add padding to format so that if bone cnt exceeds 9 padding is ## 09, 10 ---------------------------------- #
        #
        # - [OK] - add missing items to rigSet (locators, groups etc., botShirt_resultSKN_riv_grp_orig!) --------------------- #
        #
        # - [OK] - clear any unecessary things to keep rig skin clean, parent botShirt world in world ------------------------ #
        if mc.objExists(rigTrashGroups[0]):
            mc.delete(rigTrashGroups[0])
        else:
            mc.warning('{0} did not exist, could not delete, moving on'.format(rigTrashGroups[0]))
        #
        for loftProxyCrv in loftProxyCrvs:
            if mc.objExists(loftProxyCrv):
                mc.delete(loftProxyCrv)
            else:
                mc.warning('{0} did not exit, could not delete, moving on'.format(loftProxyCrv))
        #
        if mc.objExists('WORLD'):
            mc.parent(rigGroups[1], 'WORLD')
        #
        # - [OK] - maybe skin top joints of patchSurfs to an orig so it doesn't affect the top line -------------------------- #
        #
        # - [OK] - add result joints to skin sets ---------------------------------------------------------------------------- #
        if mc.objExists('skin_set'):
            # --- creating a sub set for skin_set specific to bottom jacket
            mc.sets(n='{0}_{1}'.format(botShirt, sknSet))
            mc.select(deselect=True)
            mc.sets('{0}_{1}'.format(botShirt, sknSet), e=True, fe=sknSet)
            mc.select(deselect=True)
            mc.sets(allRsltSknJnts, e=True, fe='{0}_{1}'.format(botShirt, sknSet))
        else:
            mc.warning('skin_set doesnt exists, which means something screwed up before, report this issue')
        #
        # -------------------------------------------------------------------------------------------------------------- #
        # --- adding jnt under 1st tweak to only take translate /// will need to transfer half up weight to it
        
        for cnt, firstRowSknJnt in enumerate(firstRowSknJnts):
            #
            # --- creating the required joints and placing them at the right spot -------------------------------------- #
            mc.select(deselect=True)
            mc.joint(n='{0}_noRot'.format(firstRowSknJnt), rad=0.1)
            pkOrig()
            #
            mc.parent('{0}_noRot_{1}'.format(firstRowSknJnt, origGrp),
                      '{0}'.format(firstRowSknJnt))
            mc.select(deselect=True)
            #
            for transform in transforms:
                mc.setAttr('{0}_noRot_{1}.{2}'.format(firstRowSknJnt, origGrp, transform), 0)
            #
            # --- connecting only translates
            for step, trans in enumerate(translates):
                mc.connectAttr('{0}_{1}.{2}'.format(firstRowSknJnt, origGrp, trans),
                               '{0}_noRot_{1}.{2}'.format(firstRowSknJnt, origGrp, trans), f=True)
            #
            # --- parenting in their groups to be clean (yeah I know this could have been cleaner) --------------------- #
            if cnt < 4:
                mc.parent('{0}_noRot_{1}'.format(firstRowSknJnts[cnt], origGrp), '{0}'.format(rsltsOrigsGrps[0]))
            
            if cnt < 8 :
                if cnt > 3:
                    mc.parent('{0}_noRot_{1}'.format(firstRowSknJnts[cnt], origGrp), '{0}'.format(rsltsOrigsGrps[1]))
        
            if cnt < 12:
                if cnt > 7:
                    mc.parent('{0}_noRot_{1}'.format(firstRowSknJnts[cnt], origGrp), '{0}'.format(rsltsOrigsGrps[2]))
        
            if cnt < 16:
                if cnt > 11:
                    mc.parent('{0}_noRot_{1}'.format(firstRowSknJnts[cnt], origGrp), '{0}'.format(rsltsOrigsGrps[3]))
        
            if cnt < 20:
                if cnt > 15:
                    mc.parent('{0}_noRot_{1}'.format(firstRowSknJnts[cnt], origGrp), '{0}'.format(rsltsOrigsGrps[7]))
        
            if cnt < 24:
                if cnt > 19:
                    mc.parent('{0}_noRot_{1}'.format(firstRowSknJnts[cnt], origGrp), '{0}'.format(rsltsOrigsGrps[6]))
        
            if cnt < 28:
                if cnt > 23:
                    mc.parent('{0}_noRot_{1}'.format(firstRowSknJnts[cnt], origGrp), '{0}'.format(rsltsOrigsGrps[5]))
        
            if cnt < 32:
                if cnt > 27:
                    mc.parent('{0}_noRot_{1}'.format(firstRowSknJnts[cnt], origGrp), '{0}'.format(rsltsOrigsGrps[4]))
                    #
                #
            #
            # --- adding to sets
            mc.sets('{0}_noRot'.format(firstRowSknJnt), e=True, fe=rigSet)
            mc.sets('{0}_noRot'.format(firstRowSknJnt), e=True, fe='{0}_{1}'.format(botShirt, sknSet))
            #
            mc.sets('{0}_noRot_{1}'.format(firstRowSknJnt, origGrp), e=True, fe=rigSet)
        # -------------------------------------------------------------------------------------------------------------- #
        # --- clean botShirt skin set from trasnform grp
        if mc.sets('{0}_noXformGrp'.format(botShirt), im='{0}_{1}'.format(botShirt, sknSet)):
            mc.sets('{0}_noXformGrp'.format(botShirt), e=True, rm='{0}_{1}'.format(botShirt, sknSet))
        else:
            mc.warning('{0} was not part of the set --- skipping removal'.format())
        # - [--] - add ctrls / missing ctrls to anim sets -------------------------------------------------------------------- #
        mc.sets('{0}_{1}_{2}_{3}'.format(botShirt, fkDynChain, ctrl, bonesNumbers[-1]), e=True, fe=dynChainAnimSet)#{:02d}
        mc.sets(dynTweaks, e=True, fe=dynChainAnimSet)
        
        
        if not mc.objExists(botShirtSet):
            mc.sets(n=botShirtSet)
            mc.sets(botShirtSet, e=True, fe=animSet)
        else:
            mc.warning('skipping, {0} already exists'.format(botShirtSet))
        
        for rigWorldSknJnt in rigWorldSknJnts:
            mc.sets('{0}_fk_{1}'.format(rigWorldSknJnt, set), e=True, fe=botShirtSet)
            mc.sets('{0}_{1}_{2}_fk_{3}'.format(botShirt, main, ctrl, set), e=True, fe=botShirtSet)
            mc.sets('{0}_{1}_{2}_fk_{3}'.format(botShirt, fkDynChain, ctrl, set), e=True, fe=botShirtSet)
        
        #
        # - [OK] - adjust shapes --------------------------------------------------------------------------------------------- #
        for cnt, dynChainCtrl in enumerate(dynChainCtrls):
            # --- dyn ctrls
            shapes.create('{0}'.format(dynChainCtrls[cnt]), shape='circle', size=3+(cnt*.2), scale=[1.2, 1, 1 ], axis='y',
                          twist=0, offset=[0, 0, 0 ], color=22, colorDegradeTo=None, replace=True, middle=False)
            # --- dyn tweaks ctrls
            shapes.create('{0}'.format(dynTweaks[cnt]), shape='circle', size=3.25+(cnt*.2), scale=[1.2, 1, 1 ], axis='y',
                          twist=0, offset=[0, 0, 0 ], color=18, colorDegradeTo=None, replace=True, middle=False)
        #
        shapes.create('{0}_{1}_{2}'.format(botShirt, main, ctrl), shape='circle', size=3.5, scale=[1.2, 1, 1 ], axis='y',
                      twist=0, offset=[0, 0, 0 ], color=22, colorDegradeTo=None, replace=True, middle=False)
        #
        # --- auto resizing shapes
        for letter in letters:
            #
            cnt = 0
            #
            for jntNumber in jntsNumbers[:-1]:
                #
                cnt +=1
                #
                if cnt == rigJointsAmount-1:
                    #
                    shapeSize = abs(mc.getAttr('{0}_{1}_{2}_{3}_{4}_{5}_{6}.ty'.format(LRsides[0], botShirt, fk, letter, ctrl, jntsNumbers[-2], origGrp)))
                    shapes.create('{0}_{1}_{2}_{3}_{4}_{5}'.format(LRsides[0], botShirt, fk, letter, ctrl, jntNumber), shape='circleHalf',
                                  size=shapeSize, scale=[1, 1, 1], axis='x', twist=0, offset=[0, -0.5*shapeSize, 0], color=6,
                                  colorDegradeTo=None, replace=True, middle=False)
                    #
                    shapeSize = abs(mc.getAttr('{0}_{1}_{2}_{3}_{4}_{5}_{6}.ty'.format(LRsides[1], botShirt, fk, letter,
                                    ctrl, jntsNumbers[-2], origGrp)))
                    shapes.create('{0}_{1}_{2}_{3}_{4}_{5}'.format(LRsides[1], botShirt, fk, letter, ctrl, jntNumber), shape='circleHalf',
                                  size=-shapeSize, scale=[1, 1, 1], axis='x', twist=0, offset=[0, 0.5*shapeSize, 0], color=13,
                                  colorDegradeTo=None, replace=True, middle=False)
                    #
                    shapeSize = abs(mc.getAttr('{0}_{1}_{2}_A_{3}_{4}_{5}.ty'.format(LRsides[1], botShirt, fk,
                                                                                     ctrl, jntsNumbers[-2], origGrp)))
                    shapes.create('{0}_{1}_{2}_A_{3}_{4}'.format(LRsides[1], botShirt, fk, ctrl, jntNumber), shape='circleHalf',
                                  size=shapeSize, scale=[1, 1, 1], axis='x', twist=0, offset=[0, -0.5*shapeSize, 0], color=13,
                                  colorDegradeTo=None, replace=True, middle=False)
                    #
                elif cnt < rigJointsAmount-1:
                    #
                    shapeSize = abs(mc.getAttr('{0}_{1}_{2}_{3}_{4}_{5}_{6}.ty'.format(LRsides[0], botShirt, fk, letter,
                                                                                       ctrl, jntsNumbers[cnt], origGrp)))
                    shapes.create('{0}_{1}_{2}_{3}_{4}_{5}'.format(LRsides[0], botShirt, fk, letter, ctrl, jntNumber), shape='circleHalf',
                                  size=shapeSize, scale=[1, 1, 1], axis='x', twist=0, offset=[0, 0, 0], color=6,
                                  colorDegradeTo=None, replace=True, middle=True)
                    #
                    shapeSize = abs(mc.getAttr('{0}_{1}_{2}_{3}_{4}_{5}_{6}.ty'.format(LRsides[1], botShirt, fk, letter,
                                                                                       ctrl, jntsNumbers[cnt], origGrp)))
                    shapes.create('{0}_{1}_{2}_{3}_{4}_{5}'.format(LRsides[1], botShirt, fk, letter, ctrl, jntNumber), shape='circleHalf',
                                  size=-shapeSize, scale=[1, 1, 1], axis='x', twist=0, offset=[0, 0, 0], color=13,
                                  colorDegradeTo=None, replace=True, middle=True)
                    #
                    shapeSize = abs(mc.getAttr('{0}_{1}_{2}_A_{3}_{4}_{5}.ty'.format(LRsides[1], botShirt, fk,
                                                                                     ctrl, jntsNumbers[cnt], origGrp)))
                    shapes.create('{0}_{1}_{2}_A_{3}_{4}'.format(LRsides[1], botShirt, fk, ctrl, jntNumber), shape='circleHalf',
                                  size=shapeSize, scale=[1, 1, 1], axis='x', twist=0, offset=[0, 0, 0], color=13,
                                  colorDegradeTo=None, replace=True, middle=True)
                    #
                else:
                    mc.warning('exiting loop')
                    #
                #
            #
        #
        #
        cnt = 0
        #
        for jntNumber in jntsNumbers:
            #
            cnt +=1
            #
            if cnt == rigJointsAmount-1:
                #
                shapeSize = abs(mc.getAttr('{0}_{1}_{2}_{3}_{4}_{5}_{6}.ty'.format(center, botShirt, fk, centerLetter,
                                                                                   ctrl, jntsNumbers[-2], origGrp)))
                shapes.create('{0}_{1}_{2}_{3}_{4}_{5}'.format(center, botShirt, fk, centerLetter, ctrl, jntNumber),
                              shape='circleHalf', size=shapeSize, scale=[1, 1, 1], axis='x', twist=0,
                              offset=[0, -0.5*shapeSize, 0], color=23, colorDegradeTo=None, replace=True, middle=False)
            #
            elif cnt < rigJointsAmount-1:
                shapeSize = abs(mc.getAttr('{0}_{1}_{2}_{3}_{4}_{5}_{6}.ty'.format(center, botShirt, fk, centerLetter,
                                                                                   ctrl, jntsNumbers[cnt], origGrp)))
                shapes.create('{0}_{1}_{2}_{3}_{4}_{5}'.format(center, botShirt, fk, centerLetter, ctrl, jntNumber),
                              shape='circleHalf', size=shapeSize, scale=[1, 1, 1], axis='x', twist=0, offset=[0, 0, 0],
                              color=23, colorDegradeTo=None, replace=True, middle=True)
            else:
                mc.warning('exiting loop')
        #
        # --- adding follow attribute first tweaks - taking only the fk into account for stability and for anticipated results
        # --- adding controling attributes on ctrls
        
        attrExists = mc.attributeQuery('_________', node=hipCtrl, ex=True)
        if attrExists == False:
            mc.addAttr('{0}'.format(hipCtrl), ln='_________', at='enum', en='{0}_ctrl'.format(botShirt))
            mc.setAttr('{0}._________'.format(hipCtrl), e=True, k=False, cb=True)
        else:
            mc.warning('adding {0}._________ attribute was skipped as it already exists.'.format(hipCtrl))
            #
        attrExists = mc.attributeQuery('rotFollow', node=hipCtrl, ex=True)
        if attrExists == False:
            mc.addAttr('{0}'.format(hipCtrl), ln='rotFollow', at='float', min=0, max=1, dv=1)
            mc.setAttr('{0}.rotFollow'.format(hipCtrl), e=True, k=True, cb=True)
        else:
            mc.warning('adding {0}.rotFollow attribute was skipped as it already exists.'.format(hipCtrl))
            #
        #
        for rigWorldSknJnt in rigWorldSknJnts:
            # --- create orient constraints
            mc.orientConstraint('{0}_01'.format(rigWorldSknJnt),
                                '{0}_00_{1}_{2}'.format(rigWorldSknJnt, tweakJnt, offsGrp), mo=True, skip=['y', 'z'])
            #
            # --- shortcut for pairBlend creation
            mc.setKeyframe('{0}_00_{1}_{2}.rx'.format(rigWorldSknJnt, tweakJnt, offsGrp))
            #
            # --- list connection and rename the pairBlend properly and rename lines under
            mc.rename(mc.listConnections('{0}_00_{1}_{2}.rx'.format(rigWorldSknJnt, tweakJnt, offsGrp), d=False, s=True),
                                         '{0}_00_{1}_{2}_pb'.format(rigWorldSknJnt, tweakJnt, offsGrp))
            #
            mc.rename(mc.listConnections('{0}_00_{1}_{2}_pb.inRotateX1'.format(rigWorldSknJnt, tweakJnt, offsGrp), d=False, s=True),
                                         '{0}_00_{1}_{2}_pb_animCrv_rx1'.format(rigWorldSknJnt, tweakJnt, offsGrp))
            #
            mc.disconnectAttr('{0}_00_{1}_{2}_pb_animCrv_rx1.output'.format(rigWorldSknJnt, tweakJnt, offsGrp),
                              '{0}_00_{1}_{2}_pb.inRotateX1'.format(rigWorldSknJnt, tweakJnt, offsGrp))
            #
            # - ! - technically I should do an, if attribute is free delete anim curves but I know it works so I'll do it right away
            mc.delete('{0}_00_{1}_{2}_pb_animCrv_rx1'.format(rigWorldSknJnt, tweakJnt, offsGrp))
            # --- forcing in translate 1 (original position to be 0-0-0)
            mc.setAttr('{0}_00_{1}_{2}_pb.inRotateX1'.format(rigWorldSknJnt, tweakJnt, offsGrp), 0)
            #
            # --- changing interpoation
            mc.setAttr('{0}_00_{1}_{2}_pb.rotInterpolation'.format(rigWorldSknJnt, tweakJnt, offsGrp), 1)
            
            # --- connecting follow to pairBlends
            mc.connectAttr('{0}.rotFollow'.format(hipCtrl), '{0}_00_{1}_{2}_pb.weight'.format(rigWorldSknJnt, tweakJnt, offsGrp), f=True)
        # -------------------------------------------------------------------------------------------------------------------- #
        # - [OK] - Do Julien's tagging (see mail) ---------------------------------------------------------------------------- #
        #
        # --- making list from rigSet selection, appending into clean list to remove u' -------------------------------------- #
        #
        marsRigMembers = []
        #
        marsRigMembers.append('{0}_{1}_{2}_{3}'.format(botShirt, main, ctrl, origGrp))
        marsRigMembers.append('{0}_{1}_{2}'.format(botShirt, main, ctrl))
        marsRigMembers.append('{0}_{1}_{2}_01_{3}'.format(botShirt, fkDynChain, ctrl, origGrp))
        #
        for marsRigMember in marsRigMembers:
            if not mc.sets('{0}'.format(marsRigMember), im=rigSet):
                mc.sets('{0}'.format(marsRigMember), e=True, fe=rigSet)
            else:
                mc.warning('{0} is already a member of {1}, skipping'.format(marsRigMember, rigSet))
        #
        # --- adding tag to all bottomShirt rig created set
        mc.select(rigSet)
        rigSetMembers = []
        rigSetSel = mc.ls(sl=True)
        for rigSetItem in rigSetSel:
            rigSetMembers.append('{0}'.format(rigSetItem))
        #
        # -------------------------------------------------------------------------------------------------------------------- #
        #
        patchLib.addTag(targets=rigSetMembers, tag=botShirt_tag)
        mc.select(deselect=True)
        # -------------------------------------------------------------------------------------------------------------------- #
        #
        # ------------------------------------------------------------------------------------------- #
        # --- [OK] --- actually adding inverseScales
        for rigWorldSknJnt in rigWorldSknJnts:
            for cnt, ctrlScl in enumerate(ctrlsScl):
                #
                mc.connectAttr('{0}_{1}.scale'.format(rigWorldSknJnt, ctrlsScl[cnt]),
                               '{0}_{1}_{2}.inverseScale'.format(rigWorldSknJnt, jntsInvScl[cnt], world))
        # --- removing inverse scale from botShirt_main_ctrl to fk chains first origs
        marsInvSclConns = []
        invScaleConns = mc.listConnections('{0}_{1}_{2}.scale'.format(botShirt, main, ctrl), p=True)
        for invScaleConn in invScaleConns:
            marsInvSclConns.append('{0}'.format(invScaleConn))
        for marsInvSclConn in marsInvSclConns:
            mc.disconnectAttr('{0}_{1}_{2}.scale'.format(botShirt, main, ctrl),
                              '{0}'.format(marsInvSclConn))
        # ------------------------------------------------------------------------------------------- #
        # - [OK] - Do Julien's visibility sets
        #
        from marsAutoRig_stubby.visSets import templateBiped_visSets as bipedVisSets
        reload(bipedVisSets)
        visSetsDict = bipedVisSets.createVisSets()
        #
        mc.select(deselect=True)
        #
        from marsAutoRig_stubby.patch.customLib import massConnectVis as massVis
        reload(massVis)
        massVis.massCreateVisSets(visSetsDict)
        #
        mc.select(deselect=True)
        #
        # --- if rig exists, parent the botShirt_main_ctrl_orig /// good place to put if parented to rig : build succesfull
        if mc.objExists(rigBotShirtParent):
            mc.parent('{0}_{1}_{2}_{3}'.format(botShirt, main, ctrl, origGrp),
                      '{0}'.format(rigBotShirtParent))
        else:
            mc.warning('{0} did not exist. Could not parent. Make sure you have a character rig'.format(rigBotShirtParent))
        # --- completion message
        checkParent = mc.listRelatives('{0}_{1}_{2}_{3}'.format(botShirt, main, ctrl, origGrp), parent=True)
        if checkParent == [u'{0}'.format(rigBotShirtParent)]:
            mc.warning('{0} build was successful'.format(botShirt))
        else:
            mc.error('{0} build was not successful. See script editor for details'.format(botShirt))
            print('Could not parent {0}_{1}_{2}_{3} to {4}.'
                  ' The rest of the build could execute normally so you could'
                  ' do this part manually if you wish'.format(botShirt, main, ctrl, origGrp, rigBotShirtParent))
        #
        # -------------------------------------------------------------------------------------------------------------------- #