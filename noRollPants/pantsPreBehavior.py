#Alejandro Munoz Medina

#Complete prebehavior script for pants' pantss with no roll and manipulators

import maya.cmds as mc

def patch():

    import maya.cmds as mc

    def main():

        import maya.cmds as mc

        #######################################
        ############### No Roll ###############
        #######################################

        # no twist joints

        # ankle

        def ankleNoTwist(side):

            import maya.cmds as mc

            # joint in question
            frLegTip = ("%s_leg_02_tip_twist" % side)

            # create control for the attibutes and prep it
            attrControl = "%s_leg_SW_ctrl" % side

            # add attribute(s) to the new control:

            mc.addAttr(attrControl, at="enum", en='sleeveRoll',
                       sn="sep21",
                       ln="__________________",
                       k=False, h=False)
            mc.setAttr('%s.sep21' % attrControl, cb=True)

            # add attribute(s) to the new control:
            mc.addAttr(attrControl, at="bool", sn="%s_nr" % side, ln="%s_no_roll" % side,
                       max=1.0, min=0.0, dv=1.0, k=True, h=False)

            # create the no twist joint
            frLegNtTip = mc.duplicate(frLegTip, n="%s_leg_02_tip_no_twist" % side)

            # refer to hip
            hip = ("%s_leg_01_twist" % side)

            # create blender
            blender = mc.createNode("blendTwoAttr", n="%s_ankle_twist_choice_bta" % side)

            # connect them
            mc.connectAttr("%s.twistZ" % hip, "%s.rz" % frLegNtTip[0])
            mc.connectAttr("%s.rz" % frLegTip, "%s.input[0]" % blender)
            mc.connectAttr("%s.rz" % frLegNtTip[0], "%s.input[1]" % blender)
            mc.connectAttr("%s.%s_nr" % (attrControl, side), "%s.ab" % blender, f=True)

        # foreleg

        def forelegNoTwist(side):

            import maya.cmds as mc

            # joint in question
            frLeg = ("%s_leg_02_bend_twist" % side)

            # refer to attribute control
            attrControl1 = ("%s_leg_SW_ctrl" % side)

            # create the no twist joint
            frLegNt = mc.duplicate(frLeg, n="%s_leg_02_bend_no_twist" % side)

            # refer to hip
            hip1 = ("%s_leg_01_twist" % side)

            # create blender
            blender1 = mc.createNode("blendTwoAttr", n="%s_foreleg_twist_choice_bta" % side)

            # connect them
            mc.connectAttr("%s.twistZ" % hip1, "%s.rz" % frLegNt[0])
            mc.connectAttr("%s.rz" % frLeg, "%s.input[0]" % blender1)
            mc.connectAttr("%s.rz" % frLegNt[0], "%s.input[1]" % blender1)
            mc.connectAttr("%s.%s_nr" % (attrControl1, side), "%s.ab" % blender1, f=True)

        # knee (front)

        def kneeFrontNoTwist(side):

            import maya.cmds as mc

            # joint in question
            kneeFrnt = ("%s_leg_02_base_twist" % side)

            # refer to attribute control
            attrControl2 = ("%s_leg_SW_ctrl" % side)

            # create the no twist joint
            kneeFrntNt = mc.duplicate(kneeFrnt, n="%s_leg_02_base_no_twist" % side)

            # refer to hip
            hip2 = ("%s_leg_01_twist" % side)

            # create blender
            blender2 = mc.createNode("blendTwoAttr", n="%s_kneeBack_twist_choice_bta" % side)

            # connect them
            mc.connectAttr("%s.twistZ" % hip2, "%s.rz" % kneeFrntNt[0])
            mc.connectAttr("%s.rz" % kneeFrnt, "%s.input[0]" % blender2)
            mc.connectAttr("%s.rz" % kneeFrntNt[0], "%s.input[1]" % blender2)
            mc.connectAttr("%s.%s_nr" % (attrControl2, side), "%s.ab" % blender2, f=True)

        # knee (back)

        def kneeBackNoTwist(side):

            import maya.cmds as mc

            # joint in question
            kneebck = ("%s_leg_01_tip_twist" % side)

            # refer to attribute control
            attrControl3 = ("%s_leg_SW_ctrl" % side)

            # create the no twist joint
            kneebckNt = mc.duplicate(kneebck, n="%s_leg_01_tip_no_twist" % side)

            # refer to hip
            hip3 = ("%s_leg_01_twist" % side)

            # create blender
            blender3 = mc.createNode("blendTwoAttr", n="%s_kneeFrnt_twist_choice_bta" % side)

            # connect them
            mc.connectAttr("%s.twistZ" % hip3, "%s.rz" % kneebckNt[0])
            mc.connectAttr("%s.rz" % kneebck, "%s.input[0]" % blender3)
            mc.connectAttr("%s.rz" % kneebckNt[0], "%s.input[1]" % blender3)
            mc.connectAttr("%s.%s_nr" % (attrControl3, side), "%s.ab" % blender3, f=True)

        # upperleg

        def upperlegNoTwist(side):

            import maya.cmds as mc

            # joint in question
            upperleg = ("%s_leg_01_bend_twist" % side)

            # refer to attribute control
            attrControl4 = ("%s_leg_SW_ctrl" % side)

            # create the no twist joint
            upperlegNt = mc.duplicate(upperleg, n="%s_leg_01_bend_no_twist" % side)

            # refer to hip
            hip4 = ("%s_leg_01_twist" % side)

            # create blender
            blender4 = mc.createNode("blendTwoAttr", n="%s_upperleg_twist_choice_bta" % side)

            # connect them
            mc.connectAttr("%s.twistZ" % hip4, "%s.rz" % upperlegNt[0])
            mc.connectAttr("%s.rz" % upperleg, "%s.input[0]" % blender4)
            mc.connectAttr("%s.rz" % upperlegNt[0], "%s.input[1]" % blender4)
            mc.connectAttr("%s.%s_nr" % (attrControl4, side), "%s.ab" % blender4, f=True)

        # hip

        def hipNoTwist(side):

            import maya.cmds as mc

            # joint in question
            hp = ("%s_leg_01_base_twist" % side)

            # refer to attribute control
            attrControl5 = ("%s_leg_SW_ctrl" % side)

            # create the no twist joint
            hpNt = mc.duplicate(hp, n="%s_leg_01_base_no_twist" % side)

            # refer to hip
            hip5 = ("%s_leg_01_twist" % side)

            # create blender
            blender5 = mc.createNode("blendTwoAttr", n="%s_hip_twist_choice_bta" % side)

            # connect them
            mc.connectAttr("%s.twistZ" % hip5, "%s.rz" % hpNt[0])
            mc.connectAttr("%s.rz" % hp, "%s.input[0]" % blender5)
            mc.connectAttr("%s.rz" % hpNt[0], "%s.input[1]" % blender5)
            mc.connectAttr("%s.%s_nr" % (attrControl5, side), "%s.ab" % blender5, f=True)

        #######################################

        # duplicate NURBS surfaces

        def surfaceDuplicate(side, section):

            import maya.cmds as mc

            surface = ("%s_leg_%s_deform_ns" % (side, section))

            noTwistJnts = ["%s_leg_%s_base_no_twist" % (side, section),
                           "%s_leg_%s_bend_no_twist" % (side, section),
                           "%s_leg_%s_tip_no_twist" % (side, section)]

            surfaceNt = mc.duplicate(surface, n="%s_no_twist" % surface)

            mc.skinCluster(noTwistJnts[0],
                           noTwistJnts[1],
                           noTwistJnts[2],
                           surfaceNt[0], n="%s_sc" % surfaceNt[0], tsb=True)

            skinClusterSource = mc.ls(mc.listHistory(surface, pdo=True), type='skinCluster')
            newSkincluster = mc.ls(mc.listHistory(surfaceNt[0], pdo=True), type='skinCluster')
            cvs = mc.ls('%s.cv[*][*]' % surface, fl=True)
            for cv in cvs:
                skinWeights = mc.skinPercent(skinClusterSource[0], cv, query=True, value=True)
                newCv = cv.replace(surface, surfaceNt[0])
                mc.skinPercent(newSkincluster[0], newCv, transformValue=[(noTwistJnts[0], skinWeights[0]),
                                                                         (noTwistJnts[1], skinWeights[1]),
                                                                         (noTwistJnts[2], skinWeights[2])])

        #######################################

        # follicle maker

        def legsfollicles(side, section):

            import maya.cmds as mc

            # list important objects
            constantName = ("%s_leg_%s_deform" % (side, section))
            legSwitch = ("%s_leg_SW_ctrl" % side)
            deformGRP = ("%s_leg_%s_deform_grp" % (side, section))
            surface = ("%s_ns_no_twist" % constantName)

            # first transformGeometry
            tg0 = mc.createNode("transformGeometry", n="%s_tg0" % surface)
            mc.connectAttr("%sShape.local" % surface, "%s.ig" % tg0, )
            mc.connectAttr("%s.wim" % deformGRP, "%s.txf" % tg0)

            # first curveFromSurfaceIso
            cfsi0 = mc.createNode("curveFromSurfaceIso", n="%s_cfsi0" % surface)
            mc.connectAttr("%s.og" % tg0, "%s.is" % cfsi0)
            mc.setAttr("%s.minValue" % cfsi0, 0)
            mc.setAttr("%s.maxValue" % cfsi0, 1)

            # second curveFromSurfaceIso
            cfsi1 = mc.createNode("curveFromSurfaceIso", n="%s_cfsi1" % surface)
            mc.connectAttr("%s.og" % tg0, "%s.is" % cfsi1)
            mc.setAttr("%s.minValue" % cfsi1, 0)
            mc.setAttr("%s.maxValue" % cfsi1, 1)
            mc.setAttr("%s.iv" % cfsi1, 1)

            # first rebuildCurve
            rc0 = mc.createNode("rebuildCurve", n="%s_rc0" % surface)
            mc.connectAttr("%s.oc" % cfsi0, "%s.ic" % rc0)
            mc.setAttr("%s.keepRange" % rc0, 0)

            # second rebuildCurve
            rc1 = mc.createNode("rebuildCurve", n="%s_rc1" % surface)
            mc.connectAttr("%s.oc" % cfsi1, "%s.ic" % rc1)
            mc.setAttr("%s.keepRange" % rc1, 0)

            # evenspread switch
            essw = mc.createNode("blendTwoAttr", n="%s_essw" % surface)
            mc.connectAttr("%s.evenspread" % deformGRP, "%s.ab" % essw)
            mc.setAttr("%s.i[0]" % essw, 1)

            # first avgCurves
            ac0 = mc.createNode("avgCurves", n="%s_ac0" % surface)
            mc.connectAttr("%s.oc" % cfsi0, "%s.ic1" % ac0)
            mc.connectAttr("%s.oc" % rc0, "%s.ic2" % ac0)
            mc.connectAttr("%s.o" % essw, "%s.w1" % ac0)
            mc.connectAttr("%s.evenspread" % deformGRP, "%s.w2" % ac0)
            mc.setAttr("%s.automaticWeight" % ac0, 0)

            # second avgCurves
            ac1 = mc.createNode("avgCurves", n="%s_ac1" % surface)
            mc.connectAttr("%s.oc" % cfsi1, "%s.ic1" % ac1)
            mc.connectAttr("%s.oc" % rc1, "%s.ic2" % ac1)
            mc.connectAttr("%s.o" % essw, "%s.w1" % ac1)
            mc.connectAttr("%s.evenspread" % deformGRP, "%s.w2" % ac1)
            mc.setAttr("%s.automaticWeight" % ac1, 0)

            # loft
            loft = mc.createNode("loft", n="%s_loft" % surface)
            mc.connectAttr("%s.oc" % ac0, "%s.ic[0]" % loft)
            mc.connectAttr("%s.oc" % ac1, "%s.ic[1]" % loft)
            mc.setAttr("%s.uniform" % loft, 1)
            mc.setAttr("%s.autoReverse" % loft, 0)
            mc.setAttr("%s.reverseSurfaceNormals" % loft, 1)

            # second transformGeometry
            tg1 = mc.createNode("transformGeometry", n="%s_tg1" % surface)
            mc.connectAttr("%s.os" % loft, "%s.ig" % tg1, )
            mc.connectAttr("%s.wm[0]" % deformGRP, "%s.txf" % tg1)

            # --------------------------

            # follicles

            # first follicle
            fol1 = mc.createNode("follicle", n="%s_att_01Shape" % surface)
            mc.connectAttr("%s.og" % tg1, "%s.is" % fol1)
            mc.connectAttr("%s.outRotate" % fol1, "%s_att_01.r" % surface)
            mc.connectAttr("%s.outTranslate" % fol1, "%s_att_01.t" % surface)
            mc.parent("%s_att_01" % surface, deformGRP)
            mc.setAttr("%s.parameterU" % fol1, 0.125)
            mc.setAttr("%s.parameterV" % fol1, 0.5)
            mc.setAttr("%s_att_01.inheritsTransform" % surface, 0)

            # second follicle
            fol2 = mc.createNode("follicle", n="%s_att_02Shape" % surface)
            mc.connectAttr("%s.og" % tg1, "%s.is" % fol2)
            mc.connectAttr("%s.outRotate" % fol2, "%s_att_02.r" % surface)
            mc.connectAttr("%s.outTranslate" % fol2, "%s_att_02.t" % surface)
            mc.parent("%s_att_02" % surface, deformGRP)
            mc.setAttr("%s.parameterU" % fol2, 0.375)
            mc.setAttr("%s.parameterV" % fol2, 0.5)
            mc.setAttr("%s_att_02.inheritsTransform" % surface, 0)

            # third follicle
            fol3 = mc.createNode("follicle", n="%s_att_03Shape" % surface)
            mc.connectAttr("%s.og" % tg1, "%s.is" % fol3)
            mc.connectAttr("%s.outRotate" % fol3, "%s_att_03.r" % surface)
            mc.connectAttr("%s.outTranslate" % fol3, "%s_att_03.t" % surface)
            mc.parent("%s_att_03" % surface, deformGRP)
            mc.setAttr("%s.parameterU" % fol3, 0.625)
            mc.setAttr("%s.parameterV" % fol3, 0.5)
            mc.setAttr("%s_att_03.inheritsTransform" % surface, 0)

            # fourth follicle
            fol4 = mc.createNode("follicle", n="%s_att_04Shape" % surface)
            mc.connectAttr("%s.og" % tg1, "%s.is" % fol4)
            mc.connectAttr("%s.outRotate" % fol4, "%s_att_04.r" % surface)
            mc.connectAttr("%s.outTranslate" % fol4, "%s_att_04.t" % surface)
            mc.parent("%s_att_04" % surface, deformGRP)
            mc.setAttr("%s.parameterU" % fol4, 0.875)
            mc.setAttr("%s.parameterV" % fol4, 0.5)
            mc.setAttr("%s_att_04.inheritsTransform" % surface, 0)

            # --------------------------

            # post follicle actions

            # first orig joint
            jntOrig1 = mc.duplicate("%s_leg_%s_deform_SKN_01_orig" % (side, section), po=True,
                                    n="%s_leg_%s_no_twist_SKN_01_orig" % (side, section), ic=False)
            mc.setAttr("%s.v" % jntOrig1[0], k=True, cb=True, l=False)
            mc.setAttr("%s.v" % jntOrig1[0], 1)
            mc.setAttr("%s.ds" % jntOrig1[0], 0)
            jnt1 = mc.joint(n="%s_leg_%s_no_twist_SKN_01" % (side, section))
            mc.parent(jnt1, jntOrig1[0], r=True)
            mc.select(cl=True)
            jntCtrl1 = mc.joint(n="%s_leg_%s_no_twist_ctrl_01" % (side, section))
            mc.parent(jntCtrl1, jntOrig1[0], r=True)
            mc.parent(jntOrig1[0], "%s_att_01" % surface, r=True)
            mc.parent(jntOrig1[0], deformGRP)
            mc.setAttr("%s.drawStyle" % jntOrig1[0], 2)
            mc.setAttr("%s.drawStyle" % jnt1, 2)
            mc.setAttr("%s.drawStyle" % jntCtrl1, 2)

            # first multMatrix
            mm1 = mc.createNode("multMatrix", n="%s_leg_%s_no_twist_SKN_01_mm" % (side, section))
            mc.connectAttr("%s_att_01.m" % surface, "%s.i[0]" % mm1)
            mc.connectAttr("%s.pim" % jntOrig1[0], "%s.i[1]" % mm1)

            # first decomposeMatrix
            dm1 = mc.createNode("decomposeMatrix", n="%s_leg_%s_no_twist_SKN_01_dm" % (side, section))
            mc.connectAttr("%s.o" % mm1, "%s.inputMatrix" % dm1)
            mc.connectAttr("%s.outputRotate" % dm1, "%s.r" % jntOrig1[0])
            mc.connectAttr("%s.outputTranslate" % dm1, "%s.t" % jntOrig1[0])
            mc.setAttr("%s.jo" % jntOrig1[0], 0, 0, 0)

            # connect joints accordingly
            mc.connectAttr("%s.t" % jntCtrl1, "%s.t" % jnt1)
            mc.connectAttr("%s.r" % jntCtrl1, "%s.r" % jnt1)
            mc.connectAttr("%s.s" % jntCtrl1, "%s.s" % jnt1)
            mc.connectAttr("%s.ro" % jntCtrl1, "%s.ro" % jnt1)

            # second orig joint
            jntOrig2 = mc.duplicate("%s_leg_%s_deform_SKN_02_orig" % (side, section), po=True,
                                    n="%s_leg_%s_no_twist_SKN_02_orig" % (side, section), ic=False)
            mc.setAttr("%s.v" % jntOrig2[0], k=True, cb=True, l=False)
            mc.setAttr("%s.v" % jntOrig2[0], 1)
            mc.setAttr("%s.ds" % jntOrig2[0], 0)
            jnt2 = mc.joint(n="%s_leg_%s_no_twist_SKN_02" % (side, section))
            mc.parent(jnt2, jntOrig2[0], r=True)
            mc.select(cl=True)
            jntCtrl2 = mc.joint(n="%s_leg_%s_no_twist_ctrl_02" % (side, section))
            mc.parent(jntCtrl2, jntOrig2[0], r=True)
            mc.parent(jntOrig2[0], "%s_att_02" % surface, r=True)
            mc.parent(jntOrig2[0], deformGRP)
            mc.setAttr("%s.drawStyle" % jntOrig2[0], 2)
            mc.setAttr("%s.drawStyle" % jnt2, 2)
            mc.setAttr("%s.drawStyle" % jntCtrl2, 2)

            # second multMatrix
            mm2 = mc.createNode("multMatrix", n="%s_leg_%s_no_twist_SKN_02_mm" % (side, section))
            mc.connectAttr("%s_att_02.m" % surface, "%s.i[0]" % mm2)
            mc.connectAttr("%s.pim" % jntOrig2[0], "%s.i[1]" % mm2)

            # second decomposeMatrix
            dm2 = mc.createNode("decomposeMatrix", n="%s_leg_%s_no_twist_SKN_02_dm" % (side, section))
            mc.connectAttr("%s.o" % mm2, "%s.inputMatrix" % dm2)
            mc.connectAttr("%s.outputRotate" % dm2, "%s.r" % jntOrig2[0])
            mc.connectAttr("%s.outputTranslate" % dm2, "%s.t" % jntOrig2[0])
            mc.setAttr("%s.jo" % jntOrig2[0], 0, 0, 0)

            # connect joints accordingly
            mc.connectAttr("%s.t" % jntCtrl2, "%s.t" % jnt2)
            mc.connectAttr("%s.r" % jntCtrl2, "%s.r" % jnt2)
            mc.connectAttr("%s.s" % jntCtrl2, "%s.s" % jnt2)
            mc.connectAttr("%s.ro" % jntCtrl2, "%s.ro" % jnt2)

            # third orig joint
            jntOrig3 = mc.duplicate("%s_leg_%s_deform_SKN_03_orig" % (side, section), po=True,
                                    n="%s_leg_%s_no_twist_SKN_03_orig" % (side, section), ic=False)
            mc.setAttr("%s.v" % jntOrig3[0], k=True, cb=True, l=False)
            mc.setAttr("%s.v" % jntOrig3[0], 1)
            mc.setAttr("%s.ds" % jntOrig3[0], 0)
            jnt3 = mc.joint(n="%s_leg_%s_no_twist_SKN_03" % (side, section))
            mc.parent(jnt3, jntOrig3[0], r=True)
            mc.select(cl=True)
            jntCtrl3 = mc.joint(n="%s_leg_%s_no_twist_ctrl_03" % (side, section))
            mc.parent(jntCtrl3, jntOrig3[0], r=True)
            mc.parent(jntOrig3[0], "%s_att_03" % surface, r=True)
            mc.parent(jntOrig3[0], deformGRP)
            mc.setAttr("%s.drawStyle" % jntOrig3[0], 2)
            mc.setAttr("%s.drawStyle" % jnt3, 2)
            mc.setAttr("%s.drawStyle" % jntCtrl3, 2)

            # third multMatrix
            mm3 = mc.createNode("multMatrix", n="%s_leg_%s_no_twist_SKN_03_mm" % (side, section))
            mc.connectAttr("%s_att_03.m" % surface, "%s.i[0]" % mm3)
            mc.connectAttr("%s.pim" % jntOrig3[0], "%s.i[1]" % mm3)

            # third decomposeMatrix
            dm3 = mc.createNode("decomposeMatrix", n="%s_leg_%s_no_twist_SKN_03_dm" % (side, section))
            mc.connectAttr("%s.o" % mm3, "%s.inputMatrix" % dm3)
            mc.connectAttr("%s.outputRotate" % dm3, "%s.r" % jntOrig3[0])
            mc.connectAttr("%s.outputTranslate" % dm3, "%s.t" % jntOrig3[0])
            mc.setAttr("%s.jo" % jntOrig3[0], 0, 0, 0)

            # connect joints accordingly
            mc.connectAttr("%s.t" % jntCtrl3, "%s.t" % jnt3)
            mc.connectAttr("%s.r" % jntCtrl3, "%s.r" % jnt3)
            mc.connectAttr("%s.s" % jntCtrl3, "%s.s" % jnt3)
            mc.connectAttr("%s.ro" % jntCtrl3, "%s.ro" % jnt3)

            # fourth orig joint
            jntOrig4 = mc.duplicate("%s_leg_%s_deform_SKN_04_orig" % (side, section), po=True,
                                    n="%s_leg_%s_no_twist_SKN_04_orig" % (side, section), ic=False)
            mc.setAttr("%s.v" % jntOrig4[0], k=True, cb=True, l=False)
            mc.setAttr("%s.v" % jntOrig4[0], 1)
            mc.setAttr("%s.ds" % jntOrig4[0], 0)
            jnt4 = mc.joint(n="%s_leg_%s_no_twist_SKN_04" % (side, section))
            mc.parent(jnt4, jntOrig4[0], r=True)
            mc.select(cl=True)
            jntCtrl4 = mc.joint(n="%s_leg_%s_no_twist_ctrl_04" % (side, section))
            mc.parent(jntCtrl4, jntOrig4[0], r=True)
            mc.parent(jntOrig4[0], "%s_att_04" % surface, r=True)
            mc.parent(jntOrig4[0], deformGRP)
            mc.setAttr("%s.drawStyle" % jntOrig4[0], 2)
            mc.setAttr("%s.drawStyle" % jnt4, 2)
            mc.setAttr("%s.drawStyle" % jntCtrl4, 2)

            # fourth multMatrix
            mm4 = mc.createNode("multMatrix", n="%s_leg_%s_no_twist_SKN_04_mm" % (side, section))
            mc.connectAttr("%s_att_04.m" % surface, "%s.i[0]" % mm4)
            mc.connectAttr("%s.pim" % jntOrig4[0], "%s.i[1]" % mm4)

            # fourth decomposeMatrix
            dm4 = mc.createNode("decomposeMatrix", n="%s_leg_%s_no_twist_SKN_04_dm" % (side, section))
            mc.connectAttr("%s.o" % mm4, "%s.inputMatrix" % dm4)
            mc.connectAttr("%s.outputRotate" % dm4, "%s.r" % jntOrig4[0])
            mc.connectAttr("%s.outputTranslate" % dm4, "%s.t" % jntOrig4[0])
            mc.setAttr("%s.jo" % jntOrig4[0], 0, 0, 0)

            # connect joints accordingly
            mc.connectAttr("%s.t" % jntCtrl4, "%s.t" % jnt4)
            mc.connectAttr("%s.r" % jntCtrl4, "%s.r" % jnt4)
            mc.connectAttr("%s.s" % jntCtrl4, "%s.s" % jnt4)
            mc.connectAttr("%s.ro" % jntCtrl4, "%s.ro" % jnt4)

        # no twist thight joints

        def thighJnts(side):

            import maya.cmds as mc

            # refer to the no roll attribute control
            attrCtrl = "%s_leg_SW_ctrl" % side
            rev = mc.createNode("reverse", n="%s_leg_01_no_twist_rev" % side)
            mc.connectAttr("%s.%s_nr" % (attrCtrl, side), "%s.ix" % rev)

            # refer to thigh joints
            jnt1 = ("%s_leg_01_deform_ctrl_01" % side)
            jnt2 = ("%s_leg_01_deform_ctrl_02" % side)
            jnt3 = ("%s_leg_01_deform_ctrl_03" % side)
            jnt4 = ("%s_leg_01_deform_ctrl_04" % side)

            # refer to thigh nt joints
            ntjnt1 = ("%s_leg_01_no_twist_ctrl_01" % side)
            ntjnt2 = ("%s_leg_01_no_twist_ctrl_02" % side)
            ntjnt3 = ("%s_leg_01_no_twist_ctrl_03" % side)
            ntjnt4 = ("%s_leg_01_no_twist_ctrl_04" % side)

            # controls
            tempCrcl1 = mc.circle(n="%s_tempCircle1" % side)
            mc.delete(tempCrcl1, ch=True)
            mc.rotate(90, 0, 0, "%s.cv[0:9]" % tempCrcl1[0], r=1)
            mc.scale(1.2, .6, .3, "%s.cv[0:9]" % tempCrcl1[0], r=1)
            mc.parent("%sShape" % tempCrcl1[0], ntjnt1, s=True, r=True)
            mc.select(cl=True)
            mc.delete(tempCrcl1[0])

            oriConst1 = mc.orientConstraint(jnt1, ntjnt1, mo=True)
            mc.connectAttr("%s.ox" % rev, "%s.w0" % oriConst1[0])

            tempCrcl2 = mc.circle(n="%s_tempCircle2" % side)
            mc.delete(tempCrcl2, ch=True)
            mc.rotate(90, 0, 0, "%s.cv[0:9]" % tempCrcl2[0], r=1)
            mc.scale(1.2, .6, .3, "%s.cv[0:9]" % tempCrcl2[0], r=1)
            mc.parent("%sShape" % tempCrcl2[0], ntjnt2, s=True, r=True)
            mc.select(cl=True)
            mc.delete(tempCrcl2[0])

            oriConst2 = mc.orientConstraint(jnt2, ntjnt2, mo=True)
            mc.connectAttr("%s.ox" % rev, "%s.w0" % oriConst2[0])

            tempCrcl3 = mc.circle(n="%s_tempCircle3" % side)
            mc.delete(tempCrcl3, ch=True)
            mc.rotate(90, 0, 0, "%s.cv[0:9]" % tempCrcl3[0], r=1)
            mc.scale(1.2, .6, .3, "%s.cv[0:9]" % tempCrcl3[0], r=1)
            mc.parent("%sShape" % tempCrcl3[0], ntjnt3, s=True, r=True)
            mc.select(cl=True)
            mc.delete(tempCrcl3[0])

            oriConst3 = mc.orientConstraint(jnt3, ntjnt3, mo=True)
            mc.connectAttr("%s.ox" % rev, "%s.w0" % oriConst3[0])

            tempCrcl4 = mc.circle(n="%s_tempCircle4" % side)
            mc.delete(tempCrcl4, ch=True)
            mc.rotate(90, 0, 0, "%s.cv[0:9]" % tempCrcl4[0], r=1)
            mc.scale(1.2, .6, .3, "%s.cv[0:9]" % tempCrcl4[0], r=1)
            mc.parent("%sShape" % tempCrcl4[0], ntjnt4, s=True, r=True)
            mc.select(cl=True)
            mc.delete(tempCrcl4[0])

            oriConst4 = mc.orientConstraint(jnt4, ntjnt4, mo=True)
            mc.connectAttr("%s.ox" % rev, "%s.w0" % oriConst4[0])

            theSet = mc.sets(ntjnt1, ntjnt2, ntjnt3, ntjnt4, n="%s_thigh_NoTwistJoints_skin_set" % side)
            mc.sets(theSet, add="skin_set")

        #######################################
        ############ Manipulators #############
        #######################################

        # right side top pivots' proper orientation

        def topPivotOrient(number):

            import maya.cmds as mc

            pivotControl = ("R_pants_0%s_pivot_top_ctrl" % number)
            pantsControl = mc.listRelatives(pivotControl, c=True, type="transform")
            pivotControlTopGrp = mc.listRelatives("%s_orig" % pivotControl, p=True, )

            mc.parent(pantsControl[0], w=True)

            mc.parent("%s_orig" % pivotControl, w=True)

            mc.setAttr("%s_orig.scale" % pivotControl, -1, -1, -1)

            mc.parent(pantsControl, pivotControl)
            mc.parent("%s_orig" % pivotControl, "%s" % pivotControlTopGrp[0])

        # right side main controls' proper orientation

        def rightSideOrient(number):

            import maya.cmds as mc

            controller = ("R_pants_0%s_ctrl" % number)

            kids = mc.listRelatives(controller, c=True, type='transform')
            mc.parent(kids, w=True)
            mc.setAttr('%s_orig.scale' % controller, -1, -1, 1)
            mc.parent(kids, controller)
            for kid in kids:
                mc.setAttr('%s.scale' % kid, -1, -1, 1)

        # fix size of fifth ring

        def fix5thRing(side):

            import maya.cmds as mc

            ring = ("%s_pants_05_ctrl" % side)

            mc.scale(.75, .75, .75, "%s.cv[0:9]" % ring)

        # reparent viz controls for the pantss

        def vcReparent(side):

            import maya.cmds as mc

            ctrl = ("%s_pants_top_pivot_attr_ctrl_orig" % side)

            mc.parent(ctrl, "%s_leg_02_no_twist_SKN_04_orig" % side)

        # Connect Manips to the follicles

        def parentManips(side):

            import maya.cmds as mc

            blendelbFrnt = "%s_kneeFrnt_twist_choice_bta" % side
            blendfrleg = "%s_foreleg_twist_choice_bta" % side
            blendankle = "%s_ankle_twist_choice_bta" % side

            attrControl = "%s_leg_SW_ctrl" % side
            rev = mc.createNode("reverse", n="%s_leg_02_no_twist_rev" % side)
            mc.connectAttr("%s.%s_nr" % (attrControl, side), "%s.ix" % rev)

            ntJnt1 = "%s_leg_02_no_twist_ctrl_01" % side
            ntJnt2 = "%s_leg_02_no_twist_ctrl_02" % side
            ntJnt3 = "%s_leg_02_no_twist_ctrl_03" % side
            ntJnt4 = "%s_leg_02_no_twist_ctrl_04" % side

            Jnt1 = "%s_leg_02_deform_ctrl_01" % side
            Jnt2 = "%s_leg_02_deform_ctrl_02" % side
            Jnt3 = "%s_leg_02_deform_ctrl_03" % side
            Jnt4 = "%s_leg_02_deform_ctrl_04" % side

            svl1 = "%s_pants_01_pivot_top_ctrl" % side
            svl2 = "%s_pants_02_pivot_top_ctrl" % side
            svl3 = "%s_pants_03_pivot_top_ctrl" % side
            svl4 = "%s_pants_04_pivot_top_ctrl" % side
            svl5 = "%s_pants_05_pivot_top_ctrl" % side

            knee = mc.duplicate("%s_leg_02" % side, n="%s_leg_02_no_twist" % side, po=True)
            mc.parent(knee[0], "%s_leg_02" % side)
            tempOriConst = mc.orientConstraint(ntJnt4, knee[0])
            mc.delete(tempOriConst)

            tempConst1 = mc.pointConstraint(ntJnt4, "%s_orig" % svl1, sk=("y", "z"))
            mc.delete(tempConst1)
            tempConst2 = mc.pointConstraint(ntJnt3, "%s_orig" % svl2, sk=("y", "z"))
            mc.delete(tempConst2)
            tempConst3 = mc.pointConstraint(ntJnt2, "%s_orig" % svl3, sk=("y", "z"))
            mc.delete(tempConst3)
            tempConst4 = mc.pointConstraint(ntJnt1, "%s_orig" % svl4, sk=("y", "z"))
            mc.delete(tempConst4)

            grp1 = mc.group(em=True, n="%s_transform" % svl1, p=ntJnt4)
            tempConst5 = mc.pointConstraint(ntJnt4, grp1)
            mc.delete(tempConst5)
            oriCnst1 = mc.orientConstraint(ntJnt4, knee[0], grp1, mo=True)
            mc.connectAttr("%s.%s_nr" % (attrControl, side), "%s.w0" % oriCnst1[0])
            mc.connectAttr("%s.ox" % rev, "%s.w1" % oriCnst1[0])
            mc.parent("%s_orig" % svl1, grp1)

            grp5 = mc.group(em=True, n="%s_transform" % svl5, p=ntJnt4)
            tempConst6 = mc.pointConstraint(ntJnt4, grp5, sk="x")
            mc.delete(tempConst6)
            oriCnst2 = mc.orientConstraint(ntJnt4, knee[0], grp5, mo=True)
            mc.connectAttr("%s.%s_nr" % (attrControl, side), "%s.w0" % oriCnst2[0])
            mc.connectAttr("%s.ox" % rev, "%s.w1" % oriCnst2[0])
            mc.parent("%s_orig" % svl5, grp5)

            grp2 = mc.group(em=True, n="%s_transform" % svl2, p=ntJnt3)
            tempConst7 = mc.pointConstraint(ntJnt3, grp2)
            mc.delete(tempConst7)
            oriCnst3 = mc.orientConstraint(ntJnt3, knee[0], grp2, mo=True)
            mc.connectAttr("%s.%s_nr" % (attrControl, side), "%s.w0" % oriCnst3[0])
            mc.connectAttr("%s.ox" % rev, "%s.w1" % oriCnst3[0])
            mc.parent("%s_orig" % svl2, grp2)

            grp3 = mc.group(em=True, n="%s_transform" % svl3, p=ntJnt2)
            tempConst8 = mc.pointConstraint(ntJnt2, grp3)
            mc.delete(tempConst8)
            oriCnst4 = mc.orientConstraint(ntJnt2, knee[0], grp3, mo=True)
            mc.connectAttr("%s.%s_nr" % (attrControl, side), "%s.w0" % oriCnst4[0])
            mc.connectAttr("%s.ox" % rev, "%s.w1" % oriCnst4[0])
            mc.parent("%s_orig" % svl3, grp3)

            grp4 = mc.group(em=True, n="%s_transform" % svl4, p=ntJnt1)
            tempConst9 = mc.pointConstraint(ntJnt1, grp4)
            mc.delete(tempConst9)
            oriCnst5 = mc.orientConstraint(ntJnt1, knee[0], grp4, mo=True)
            mc.connectAttr("%s.%s_nr" % (attrControl, side), "%s.w0" % oriCnst5[0])
            mc.connectAttr("%s.ox" % rev, "%s.w1" % oriCnst5[0])
            mc.parent("%s_orig" % svl4, grp4)

        #######################################
        ########## execute functions ##########
        #######################################

        # variables

        sides = ["L", "R"]
        sections = ["01", "02"]
        numbers = ["1", "2", "3", "4", "5"]

        ###No Roll

        # no twist joints
        for side in sides:
            ankleNoTwist(side)
            forelegNoTwist(side)
            kneeFrontNoTwist(side)
            kneeBackNoTwist(side)
            upperlegNoTwist(side)
            hipNoTwist(side)

        # duplicate NURBS surfaces
        for side in sides:
            for section in sections:
                surfaceDuplicate(side, section)

        # follicle maker
        for side in sides:
            for section in sections:
                legsfollicles(side, section)

        # thighs' controls
        for side in sides:
            thighJnts(side)

        ###Manipulators

        # right side proper orientation
        for number in numbers:
            topPivotOrient(number)
            rightSideOrient(number)

        # connect no roll to manipulators
        for side in sides:
            parentManips(side)
            vcReparent(side)

        # correction of the first ring on the right side
        mc.parent("R_pants_01_ctrl_orig", w=True)
        mc.setAttr("R_pants_01_pivot_top_ctrl_orig.scale", -1, -1, -1)
        mc.parent("R_pants_01_ctrl_orig", "R_pants_01_pivot_top_ctrl")
        mc.move(0, -1.351013, 0, "R_pants_01_pivot_top_ctrlShape.cv[0]", os=True, r=True)
        mc.move(0, -1.351013, 0, "R_pants_01_pivot_top_ctrlShape.cv[2:3]", os=True, r=True)
        mc.move(0, -1.351013, 0, "R_pants_01_pivot_top_ctrlShape.cv[5:9]", os=True, r=True)

        # intermediate joints' proper orientation
        interms = mc.ls("R*interm*ctrl_orig")

        for interm in interms:
            trnsfrms = mc.listRelatives(interm, p=True)
            for trnsfrm in trnsfrms:
                mc.setAttr('%s.rotate' % interm, 0, 180, 180)
                mc.setAttr('%s.scale' % interm, -1, 1, 1)

        # fix size of fifth ring
        for side in sides:
            fix5thRing(side)

    ######################## End

    pantsTemplate = ("pants_ctrls_template")

    if mc.objExists(pantsTemplate):

        main()

    else:

        pass