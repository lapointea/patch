#Alejandro Munoz Medina
#post behavior for short_sleeve templates

import maya.cmds as mc

def patch():

    import maya.cmds as mc

    def main():

        ##################################################################
        #### Post Behavior short_sleeve Controllers' follow function #####
        ##################################################################

        # short_sleeve follow mechanism for top pivots

        def followMechanismtopPivot(side):

            import maya.cmds as mc

            attributeCtrl = ("%s_short_sleeve_top_pivot_attr_ctrl" % side)

            mc.setAttr("%s.rx" % attributeCtrl, l=True, k=False, cb=False)
            mc.setAttr("%s.ry" % attributeCtrl, l=True, k=False, cb=False)
            mc.setAttr("%s.rz" % attributeCtrl, l=True, k=False, cb=False)
            mc.setAttr("%s.sx" % attributeCtrl, l=True, k=False, cb=False)
            mc.setAttr("%s.sy" % attributeCtrl, l=True, k=False, cb=False)
            mc.setAttr("%s.sz" % attributeCtrl, l=True, k=False, cb=False)

            chauffeur = ("%s_short_sleeve_01_pivot_top_ctrl" % (side))

            passengers = ["%s_short_sleeve_05_pivot_top_ctrl" % (side), ]

            controller = mc.addAttr(attributeCtrl,
                                    at="float",
                                    sn="%s_fp" % chauffeur,
                                    ln="%s_followPercentage" % chauffeur,
                                    max=1.0, min=0.0, dv=1.0, k=True, h=False)
            # create nodes that control the translation, rotation, and scale of the follow:
            deformations = ["t", "r", "s"]
            for deformation in deformations:
                switches = mc.createNode("multiplyDivide", n="%s_%s_follow_perCent_md" % (chauffeur, deformation))
                mc.connectAttr("%s.%s" % (chauffeur, deformation), "%s.input1" % switches)
                mc.connectAttr("%s.%s_fp" % (attributeCtrl, chauffeur), "%s.input2X" % switches)
                mc.connectAttr("%s.%s_fp" % (attributeCtrl, chauffeur), "%s.input2Y" % switches)
                mc.connectAttr("%s.%s_fp" % (attributeCtrl, chauffeur), "%s.input2Z" % switches)

            # create a plusMinus for scale correction for later use
            pmaSubstract = mc.createNode("plusMinusAverage", n="%s_scale_substract_pma" % chauffeur)
            mc.setAttr("%s.op" % pmaSubstract, 2)
            mc.setAttr("%s.i3[0]" % pmaSubstract, 0, 0, 0)
            mc.setAttr("%s.i3[1]" % pmaSubstract, 1, 1, 1)
            mc.connectAttr("%s.s" % chauffeur, "%s.i3[0]" % pmaSubstract, f=True)

            for passenger in passengers:
                targets = mc.listRelatives(passenger, p=True)
                grandDad = mc.listRelatives(targets, p=True)
                for target in targets:
                    # create attribute on the slave controls that changes their follow fall off
                    mc.addAttr(attributeCtrl, at="float", sn="%s_fa" % passenger, ln="%s_followAmount" % passenger,
                               max=1.0, min=0.0, dv=1.0, k=True, h=False)
                # create a group on top of the ORIG of each slave control meant to follow the driver control
                phonyFollowGRP = [mc.group(em=True, n="%s_phoney_follow_group" % passenger)]
                mc.parent(phonyFollowGRP, grandDad, a=True)
                tempConst = mc.parentConstraint(targets, phonyFollowGRP, n="tempCnst")
                mc.delete(tempConst)
                if "R_" in "%s" % phonyFollowGRP:
                    mc.scale(-1, -1, -1, phonyFollowGRP)
                followGRP = mc.group(em=True, n="%s_follow_group" % passenger)
                mc.parent(followGRP, phonyFollowGRP, r=True)
                mc.parent(target, followGRP)
                # connect everything
                for deformation2 in deformations:
                    followAmountNode = mc.createNode("multiplyDivide",
                                                     n="%s_%s_followAmount_md" % (passenger, deformation2))
                    mc.setAttr("%s.input2" % followAmountNode, 1, 1, 1)
                    mc.connectAttr("%s.%s_fa" % (attributeCtrl, passenger), "%s.input1X" % followAmountNode)
                    mc.connectAttr("%s.%s_fa" % (attributeCtrl, passenger), "%s.input1Y" % followAmountNode)
                    mc.connectAttr("%s.%s_fa" % (attributeCtrl, passenger), "%s.input1Z" % followAmountNode)
                    mc.connectAttr("%s_%s_follow_perCent_md.output" % (chauffeur, deformation2),
                                   "%s.input2" % followAmountNode)
                    mc.connectAttr("%s.output" % followAmountNode, followGRP + ".%s" % deformation2)
                    # redefine the connections for the scale attribute
                    if deformation2 == "s":
                        followScale = mc.createNode("multiplyDivide", n="%s_s_followScale_md" % passenger)
                        mc.connectAttr("%s.o3" % pmaSubstract, "%s.i1" % followScale, f=True)
                        mc.connectAttr("%s.o" % followAmountNode, "%s.i2" % followScale, f=True)
                        pmaAdd = mc.createNode("plusMinusAverage", n="%s_scale_correct_pma" % passenger)
                        mc.setAttr("%s.i3[0]" % pmaAdd, 1, 1, 1)
                        mc.setAttr("%s.i3[1]" % pmaAdd, 0, 0, 0)
                        mc.connectAttr("%s.o" % followScale, "%s.i3[1]" % pmaAdd, f=True)
                        mc.connectAttr("%s.o3" % pmaAdd, "%s.s" % followGRP, f=True)
            mc.disconnectAttr("%s.s" % chauffeur, "%s_s_follow_perCent_md.i1" % chauffeur)
            mc.setAttr("%s_s_follow_perCent_md.i1" % chauffeur, 1, 1, 1)

            # rename short_sleeve 5 attribute to "shirt"
            if passenger == "%s_short_sleeve_05_pivot_top_ctrl" % side:
                mc.renameAttr("%s.%s_short_sleeve_05_pivot_top_ctrl_followAmount" % (attributeCtrl, side),
                              "%s_shirt_pivot_top_followAmount" % side)

        ###############

        # short_sleeve follow mechanism for main controls

        def followMechanismMains(side):

            import maya.cmds as mc

            attributeCtrl = ("%s_main_short_sleeve_attr_ctrl" % side)

            mc.setAttr("%s.rx" % attributeCtrl, l=True, k=False, cb=False)
            mc.setAttr("%s.ry" % attributeCtrl, l=True, k=False, cb=False)
            mc.setAttr("%s.rz" % attributeCtrl, l=True, k=False, cb=False)
            mc.setAttr("%s.sx" % attributeCtrl, l=True, k=False, cb=False)
            mc.setAttr("%s.sy" % attributeCtrl, l=True, k=False, cb=False)
            mc.setAttr("%s.sz" % attributeCtrl, l=True, k=False, cb=False)

            chauffeur = ("%s_short_sleeve_01_ctrl" % (side))

            passengers = ["%s_short_sleeve_05_ctrl" % (side)]

            controller = mc.addAttr(attributeCtrl,
                                    at="float",
                                    sn="%s_fp" % chauffeur,
                                    ln="%s_followPercentage" % chauffeur,
                                    max=1.0, min=0.0, dv=1.0, k=True, h=False)
            # create nodes that control the translation, rotation, and scale of the follow:
            deformations = ["t", "r", "s"]
            for deformation in deformations:
                switches = mc.createNode("multiplyDivide", n="%s_%s_follow_perCent_md" % (chauffeur, deformation))
                mc.connectAttr("%s.%s" % (chauffeur, deformation), "%s.input1" % switches)
                mc.connectAttr("%s.%s_fp" % (attributeCtrl, chauffeur), "%s.input2X" % switches)
                mc.connectAttr("%s.%s_fp" % (attributeCtrl, chauffeur), "%s.input2Y" % switches)
                mc.connectAttr("%s.%s_fp" % (attributeCtrl, chauffeur), "%s.input2Z" % switches)

            # create a plusMinus for scale correction for later use
            pmaSubstract = mc.createNode("plusMinusAverage", n="%s_scale_substract_pma" % chauffeur)
            mc.setAttr("%s.op" % pmaSubstract, 2)
            mc.setAttr("%s.i3[0]" % pmaSubstract, 0, 0, 0)
            mc.setAttr("%s.i3[1]" % pmaSubstract, 1, 1, 1)
            mc.connectAttr("%s.s" % chauffeur, "%s.i3[0]" % pmaSubstract, f=True)

            for passenger in passengers:
                targets = mc.listRelatives(passenger, p=True)
                grandDad = mc.listRelatives(targets, p=True)
                for target in targets:
                    # create attribute on the slave controls that changes their follow fall off
                    mc.addAttr(attributeCtrl, at="float", sn="%s_fa" % passenger, ln="%s_followAmount" % passenger,
                               max=1.0, min=0.0, dv=1.0, k=True, h=False)
                # create a group on top of the ORIG of each slave control meant to follow the driver control
                phonyFollowGRP = [mc.group(em=True, n="%s_phoney_follow_group" % passenger)]
                mc.parent(phonyFollowGRP, grandDad, a=True)
                tempConst = mc.parentConstraint(targets, phonyFollowGRP, n="tempCnst")
                mc.delete(tempConst)
                if "R_" in "%s" % phonyFollowGRP:
                    mc.scale(-1, -1, 1, phonyFollowGRP)
                followGRP = mc.group(em=True, n="%s_follow_group" % passenger)
                mc.parent(followGRP, phonyFollowGRP, r=True)
                mc.parent(target, followGRP)
                # connect everything
                for deformation2 in deformations:
                    followAmountNode = mc.createNode("multiplyDivide",
                                                     n="%s_%s_followAmount_md" % (passenger, deformation2))
                    mc.setAttr("%s.input2" % followAmountNode, 1, 1, 1)
                    mc.connectAttr("%s.%s_fa" % (attributeCtrl, passenger), "%s.input1X" % followAmountNode)
                    mc.connectAttr("%s.%s_fa" % (attributeCtrl, passenger), "%s.input1Y" % followAmountNode)
                    mc.connectAttr("%s.%s_fa" % (attributeCtrl, passenger), "%s.input1Z" % followAmountNode)
                    mc.connectAttr("%s_%s_follow_perCent_md.output" % (chauffeur, deformation2),
                                   "%s.input2" % followAmountNode)
                    mc.connectAttr("%s.output" % followAmountNode, followGRP + ".%s" % deformation2)
                    # redefine the connections for the scale attribute
                    if deformation2 == "s":
                        followScale = mc.createNode("multiplyDivide", n="%s_s_followScale_md" % passenger)
                        mc.connectAttr("%s.o3" % pmaSubstract, "%s.i1" % followScale, f=True)
                        mc.connectAttr("%s.o" % followAmountNode, "%s.i2" % followScale, f=True)
                        pmaAdd = mc.createNode("plusMinusAverage", n="%s_scale_correct_pma" % passenger)
                        mc.setAttr("%s.i3[0]" % pmaAdd, 1, 1, 1)
                        mc.setAttr("%s.i3[1]" % pmaAdd, 0, 0, 0)
                        mc.connectAttr("%s.o" % followScale, "%s.i3[1]" % pmaAdd, f=True)
                        mc.connectAttr("%s.o3" % pmaAdd, "%s.s" % followGRP, f=True)
            mc.disconnectAttr("%s.s" % chauffeur, "%s_s_follow_perCent_md.i1" % chauffeur)
            mc.setAttr("%s_s_follow_perCent_md.i1" % chauffeur, 1, 1, 1)

            # rename short_sleeve 5 attribute to "shirt"
            if passenger == "%s_short_sleeve_05_ctrl" % side:
                mc.renameAttr("%s.%s_short_sleeve_05_ctrl_followAmount" % (attributeCtrl, side),
                              "%s_shirt_followAmount" % side)

        ###############

        # short_sleeve follow mechanism for conrner controls

        def followMechanismCorners(side, position):

            import maya.cmds as mc

            attributeCtrl = ("%s_%s_short_sleeve_attr_ctrl" % (side, position))

            mc.setAttr("%s.rx" % attributeCtrl, l=True, k=False, cb=False)
            mc.setAttr("%s.ry" % attributeCtrl, l=True, k=False, cb=False)
            mc.setAttr("%s.rz" % attributeCtrl, l=True, k=False, cb=False)
            mc.setAttr("%s.sx" % attributeCtrl, l=True, k=False, cb=False)
            mc.setAttr("%s.sy" % attributeCtrl, l=True, k=False, cb=False)
            mc.setAttr("%s.sz" % attributeCtrl, l=True, k=False, cb=False)

            chauffeur = ("%s_%s_short_sleeve_01_ctrl" % (side, position))

            passengers = ["%s_%s_short_sleeve_05_ctrl" % (side, position)]

            controller = mc.addAttr(attributeCtrl,
                                    at="float",
                                    sn="%s_fp" % chauffeur,
                                    ln="%s_followPercentage" % chauffeur,
                                    max=1.0, min=0.0, dv=1.0, k=True, h=False)
            # create nodes that control the translation, rotation, and scale of the follow:
            deformations = ["t", "r", "s"]
            for deformation in deformations:
                switches = mc.createNode("multiplyDivide", n="%s_%s_follow_perCent_md" % (chauffeur, deformation))
                mc.connectAttr("%s.%s" % (chauffeur, deformation), "%s.input1" % switches)
                mc.connectAttr("%s.%s_fp" % (attributeCtrl, chauffeur), "%s.input2X" % switches)
                mc.connectAttr("%s.%s_fp" % (attributeCtrl, chauffeur), "%s.input2Y" % switches)
                mc.connectAttr("%s.%s_fp" % (attributeCtrl, chauffeur), "%s.input2Z" % switches)

            # create a plusMinus for scale correction for later use
            pmaSubstract = mc.createNode("plusMinusAverage", n="%s_scale_substract_pma" % chauffeur)
            mc.setAttr("%s.op" % pmaSubstract, 2)
            mc.setAttr("%s.i3[0]" % pmaSubstract, 0, 0, 0)
            mc.setAttr("%s.i3[1]" % pmaSubstract, 1, 1, 1)
            mc.connectAttr("%s.s" % chauffeur, "%s.i3[0]" % pmaSubstract, f=True)

            for passenger in passengers:
                targets = mc.listRelatives(passenger, p=True)
                grandDad = mc.listRelatives(targets, p=True)
                for target in targets:
                    # create attribute on the slave controls that changes their follow fall off
                    mc.addAttr(attributeCtrl, at="float", sn="%s_fa" % passenger, ln="%s_followAmount" % passenger,
                               max=1.0, min=0.0, dv=1.0, k=True, h=False)
                # create a group on top of the ORIG of each slave control meant to follow the driver control
                phonyFollowGRP = [mc.group(em=True, n="%s_phoney_follow_group" % passenger)]
                mc.parent(phonyFollowGRP, grandDad, a=True)
                tempConst = mc.parentConstraint(targets, phonyFollowGRP, n="tempCnst")
                mc.delete(tempConst)
                if "R_" in "%s" % phonyFollowGRP:
                    mc.scale(-1, -1, 1, phonyFollowGRP)
                followGRP = mc.group(em=True, n="%s_follow_group" % passenger)
                mc.parent(followGRP, phonyFollowGRP, r=True)
                mc.parent(target, followGRP)
                # connect everything
                for deformation2 in deformations:
                    followAmountNode = mc.createNode("multiplyDivide",
                                                     n="%s_%s_followAmount_md" % (passenger, deformation2))
                    mc.setAttr("%s.input2" % followAmountNode, 1, 1, 1)
                    mc.connectAttr("%s.%s_fa" % (attributeCtrl, passenger), "%s.input1X" % followAmountNode)
                    mc.connectAttr("%s.%s_fa" % (attributeCtrl, passenger), "%s.input1Y" % followAmountNode)
                    mc.connectAttr("%s.%s_fa" % (attributeCtrl, passenger), "%s.input1Z" % followAmountNode)
                    mc.connectAttr("%s_%s_follow_perCent_md.output" % (chauffeur, deformation2),
                                   "%s.input2" % followAmountNode)
                    mc.connectAttr("%s.output" % followAmountNode, followGRP + ".%s" % deformation2)
                    # redefine the connections for the scale attribute
                    if deformation2 == "s":
                        pmaSubstract = mc.createNode("plusMinusAverage", n="%s_scale_substract_pma" % passenger)
                        mc.setAttr("%s.op" % pmaSubstract, 2)
                        mc.setAttr("%s.i3[0]" % pmaSubstract, 0, 0, 0)
                        mc.setAttr("%s.i3[1]" % pmaSubstract, 1, 1, 1)
                        mc.connectAttr("%s.s" % chauffeur, "%s.i3[0]" % pmaSubstract, f=True)
                        followScale = mc.createNode("multiplyDivide", n="%s_s_followScale_md" % passenger)
                        mc.connectAttr("%s.o3" % pmaSubstract, "%s.i1" % followScale, f=True)
                        mc.connectAttr("%s.o" % followAmountNode, "%s.i2" % followScale, f=True)
                        pmaAdd = mc.createNode("plusMinusAverage", n="%s_scale_correct_pma" % passenger)
                        mc.setAttr("%s.i3[0]" % pmaAdd, 1, 1, 1)
                        mc.setAttr("%s.i3[1]" % pmaAdd, 0, 0, 0)
                        mc.connectAttr("%s.o" % followScale, "%s.i3[1]" % pmaAdd, f=True)
                        mc.connectAttr("%s.o3" % pmaAdd, "%s.s" % followGRP, f=True)
            mc.disconnectAttr("%s.s" % chauffeur, "%s_s_follow_perCent_md.i1" % chauffeur)
            mc.setAttr("%s_s_follow_perCent_md.i1" % chauffeur, 1, 1, 1)

            # rename short_sleeve 6 attribute to "shirt"
            if passenger == "%s_%s_short_sleeve_05_ctrl" % (side, position):
                mc.renameAttr("%s.%s_%s_short_sleeve_05_ctrl_followAmount" % (attributeCtrl, side, position),
                              "%s_%s_shirt_followAmount" % (side, position))

        ###############

        def followMechanismInterms(side, intPosition):

            import maya.cmds as mc

            attributeCtrl = ("%s_%s_short_sleeve_attr_ctrl" % (side, intPosition))

            mc.setAttr("%s.rx" % attributeCtrl, l=True, k=False, cb=False)
            mc.setAttr("%s.ry" % attributeCtrl, l=True, k=False, cb=False)
            mc.setAttr("%s.rz" % attributeCtrl, l=True, k=False, cb=False)
            mc.setAttr("%s.sx" % attributeCtrl, l=True, k=False, cb=False)
            mc.setAttr("%s.sy" % attributeCtrl, l=True, k=False, cb=False)
            mc.setAttr("%s.sz" % attributeCtrl, l=True, k=False, cb=False)

            chauffeur = ("%s_%s_short_sleeve_01_interm_02_ctrl" % (side, intPosition))

            passengers = ["%s_%s_short_sleeve_05_interm_02_ctrl" % (side, intPosition)]

            controller = mc.addAttr(attributeCtrl,
                                    at="float",
                                    sn="%s_fp" % chauffeur,
                                    ln="%s_followPercentage" % chauffeur,
                                    max=1.0, min=0.0, dv=1.0, k=True, h=False)
            # create nodes that control the translation, rotation, and scale of the follow:
            deformations = ["t", "r", "s"]
            for deformation in deformations:
                switches = mc.createNode("multiplyDivide", n="%s_%s_follow_perCent_md" % (chauffeur, deformation))
                mc.connectAttr("%s.%s" % (chauffeur, deformation), "%s.input1" % switches)
                mc.connectAttr("%s.%s_fp" % (attributeCtrl, chauffeur), "%s.input2X" % switches)
                mc.connectAttr("%s.%s_fp" % (attributeCtrl, chauffeur), "%s.input2Y" % switches)
                mc.connectAttr("%s.%s_fp" % (attributeCtrl, chauffeur), "%s.input2Z" % switches)

            # create a plusMinus for scale correction for later use
            pmaSubstract = mc.createNode("plusMinusAverage", n="%s_scale_substract_pma" % chauffeur)
            mc.setAttr("%s.op" % pmaSubstract, 2)
            mc.setAttr("%s.i3[0]" % pmaSubstract, 0, 0, 0)
            mc.setAttr("%s.i3[1]" % pmaSubstract, 1, 1, 1)
            mc.connectAttr("%s.s" % chauffeur, "%s.i3[0]" % pmaSubstract, f=True)

            for passenger in passengers:
                targets = mc.listRelatives(passenger, p=True)
                grandDad = mc.listRelatives(targets, p=True)
                for target in targets:
                    # create attribute on the slave controls that changes their follow fall off
                    mc.addAttr(attributeCtrl, at="float", sn="%s_fa" % passenger, ln="%s_followAmount" % passenger,
                               max=1.0, min=0.0, dv=1.0, k=True, h=False)
                # create a group on top of the ORIG of each slave control meant to follow the driver control
                phonyFollowGRP = [mc.group(em=True, n="%s_phoney_follow_group" % passenger)]
                mc.parent(phonyFollowGRP, grandDad, a=True)
                tempConst = mc.parentConstraint(targets, phonyFollowGRP, n="tempCnst")
                mc.delete(tempConst)
                if "R_" in "%s" % phonyFollowGRP:
                    mc.scale(-1, 1, 1, phonyFollowGRP)
                followGRP = mc.group(em=True, n="%s_follow_group" % passenger)
                mc.parent(followGRP, phonyFollowGRP, r=True)
                mc.parent(target, followGRP)
                # connect everything
                for deformation2 in deformations:
                    followAmountNode = mc.createNode("multiplyDivide",
                                                     n="%s_%s_followAmount_md" % (passenger, deformation2))
                    mc.setAttr("%s.input2" % followAmountNode, 1, 1, 1)
                    mc.connectAttr("%s.%s_fa" % (attributeCtrl, passenger), "%s.input1X" % followAmountNode)
                    mc.connectAttr("%s.%s_fa" % (attributeCtrl, passenger), "%s.input1Y" % followAmountNode)
                    mc.connectAttr("%s.%s_fa" % (attributeCtrl, passenger), "%s.input1Z" % followAmountNode)
                    mc.connectAttr("%s_%s_follow_perCent_md.output" % (chauffeur, deformation2),
                                   "%s.input2" % followAmountNode)
                    mc.connectAttr("%s.output" % followAmountNode, followGRP + ".%s" % deformation2)
                    # redefine the connections for the scale attribute
                    if deformation2 == "s":
                        pmaSubstract = mc.createNode("plusMinusAverage", n="%s_scale_substract_pma" % passenger)
                        mc.setAttr("%s.op" % pmaSubstract, 2)
                        mc.setAttr("%s.i3[0]" % pmaSubstract, 0, 0, 0)
                        mc.setAttr("%s.i3[1]" % pmaSubstract, 1, 1, 1)
                        mc.connectAttr("%s.s" % chauffeur, "%s.i3[0]" % pmaSubstract, f=True)
                        followScale = mc.createNode("multiplyDivide", n="%s_s_followScale_md" % passenger)
                        mc.connectAttr("%s.o3" % pmaSubstract, "%s.i1" % followScale, f=True)
                        mc.connectAttr("%s.o" % followAmountNode, "%s.i2" % followScale, f=True)
                        pmaAdd = mc.createNode("plusMinusAverage", n="%s_scale_correct_pma" % passenger)
                        mc.setAttr("%s.i3[0]" % pmaAdd, 1, 1, 1)
                        mc.setAttr("%s.i3[1]" % pmaAdd, 0, 0, 0)
                        mc.connectAttr("%s.o" % followScale, "%s.i3[1]" % pmaAdd, f=True)
                        mc.connectAttr("%s.o3" % pmaAdd, "%s.s" % followGRP, f=True)
            mc.disconnectAttr("%s.s" % chauffeur, "%s_s_follow_perCent_md.i1" % chauffeur)
            mc.setAttr("%s_s_follow_perCent_md.i1" % chauffeur, 1, 1, 1)

            # rename short_sleeve 6 attribute to "shirt"
            if passenger == "%s_%s_short_sleeve_05_interm_02_ctrl" % (side, intPosition):
                mc.renameAttr(
                    "%s.%s_%s_short_sleeve_05_interm_02_ctrl_followAmount" % (attributeCtrl, side, intPosition),
                    "%s_%s_shirt_interm_followAmount" % (side, intPosition))

        ###############

        def unwantedControls():

            import marsAutoRig_stubby.patch.customLib.removeFromSets as rfs

            remSetList = ['R_back_short_sleeve_01_jnt',
                          'R_back_short_sleeve_01_jnt_orig',
                          'L_front_short_sleeve_01_jnt',
                          'L_front_short_sleeve_01_jnt_orig',
                          'L_bot_short_sleeve_01_jnt',
                          'L_bot_short_sleeve_01_jnt_orig',
                          'L_back_short_sleeve_01_jnt',
                          'L_back_short_sleeve_01_jnt_orig',
                          'R_top_short_sleeve_01_jnt',
                          'R_top_short_sleeve_01_jnt_orig',
                          'R_front_short_sleeve_01_jnt',
                          'R_front_short_sleeve_01_jnt_orig',
                          'L_front_short_sleeve_05_jnt',
                          'L_front_short_sleeve_05_jnt_orig',
                          'L_top_short_sleeve_05_jnt',
                          'L_top_short_sleeve_05_jnt_orig',
                          'L_bot_short_sleeve_05_jnt',
                          'L_bot_short_sleeve_05_jnt_orig',
                          'L_back_short_sleeve_05_jnt',
                          'L_back_short_sleeve_05_jnt_orig',
                          'R_bot_short_sleeve_01_jnt',
                          'R_bot_short_sleeve_01_jnt_orig',
                          'R_back_short_sleeve_05_jnt',
                          'R_back_short_sleeve_05_jnt_orig',
                          'R_bot_short_sleeve_05_jnt',
                          'R_bot_short_sleeve_05_jnt_orig',
                          'R_front_short_sleeve_05_jnt',
                          'R_front_short_sleeve_05_jnt_orig',
                          'R_top_short_sleeve_05_jnt',
                          'R_top_short_sleeve_05_jnt_orig']

            rfs.removeFromSet(remSetList=[], remSet='anim_set')

            ###############

        sides = ["L", "R"]
        positions = ["top", "front", "bot", "back"]
        intPositions = ["topToFront", "frontToBot", "botToBack", "backToTop"]
        for side in sides:
            followMechanismtopPivot(side)
            followMechanismMains(side)
            for position in positions:
                followMechanismCorners(side, position)
            for intPosition in intPositions:
                followMechanismInterms(side, intPosition)

        unwantedControls()

        ############################################################
        # Post Behavior short_sleeve Controllers' visibility
        ############################################################

        def visibilityTopPivot(side):

            import maya.cmds as mc

            attributeCtrl = ("%s_arm_SW_ctrl" % side)

            mc.addAttr(attributeCtrl, at="enum", en='sleevesVis',
                       sn="sep20",
                       ln="____________",
                       k=False, h=False)
            mc.setAttr("%s.sep20" % attributeCtrl, cb=True)

            mc.addAttr(attributeCtrl, at="bool", dv=0,
                       sn="slvviz",
                       ln="shortSleevesViz",
                       k=False, h=False)
            mc.setAttr("%s.slvviz" % attributeCtrl, cb=True)

            mc.addAttr(attributeCtrl, at="bool", dv=0,
                       sn="advslv",
                       ln="advancedShortSleeve",
                       k=False, h=False)
            mc.setAttr("%s.advslv" % attributeCtrl, cb=True)

            mc.addAttr(attributeCtrl, at="bool", dv=0,
                       sn="twkslvviz",
                       ln="tweakShortSleeveViz",
                       k=False, h=False)
            mc.setAttr("%s.twkslvviz" % attributeCtrl, cb=True)

            topPivotVizGRPs = ("%s_short_sleeve_01_pivot_top_ctrl" % side,
                               "%s_short_sleeve_05_pivot_top_ctrl" % side,)

            for topPivotVizGRP in topPivotVizGRPs:
                mc.connectAttr("%s.slvviz" % attributeCtrl, "%s_orig.v" % topPivotVizGRP)

            mc.connectAttr("%s.advslv" % attributeCtrl, "%s.v" % topPivotVizGRPs[1])

        ##################

        def visibilityMain(side):

            import maya.cmds as mc

            attributeCtrl = ("%s_arm_SW_ctrl" % side)

            mainVizGRPs = ("%s_short_sleeve_01_ctrl" % side,
                           "%s_short_sleeve_05_ctrl" % side,)

            for mainVizGRP in mainVizGRPs:
                mc.connectAttr("%s.slvviz" % attributeCtrl, "%s_orig.v" % mainVizGRP)

            mc.connectAttr("%s.advslv" % attributeCtrl, "%s.v" % mainVizGRPs[1])

        ##################

        def visibilityCorners(side, position):

            import maya.cmds as mc

            attributeCtrl = ("%s_arm_SW_ctrl" % side)

            cornerVizGRPs = ("%s_%s_short_sleeve_01_ctrl" % (side, position),
                             "%s_%s_short_sleeve_05_ctrl" % (side, position))

            for cornerVizGRP in cornerVizGRPs:
                mc.setAttr("%s_orig.v" % cornerVizGRP, l=False)
                mc.connectAttr("%s.twkslvviz" % attributeCtrl, "%s_orig.v" % cornerVizGRP)
                mc.setAttr("%s_orig.v" % cornerVizGRP, l=True)

        ##################

        def visibilityInterm(side, intPosition):

            import maya.cmds as mc

            attributeCtrl = ("%s_arm_SW_ctrl" % side)

            intermVizGRPs = ("%s_%s_short_sleeve_01_interm_02_ctrl" % (side, intPosition),
                             "%s_%s_short_sleeve_05_interm_02_ctrl" % (side, intPosition))

            for intermVizGRP in intermVizGRPs:
                vizGRP = mc.group("%s_orig" % intermVizGRP, n="%s_viz_group" % intermVizGRP)
                mc.connectAttr("%s.twkslvviz" % attributeCtrl, "%s.v" % vizGRP)

        ##################

        sides = ["L", "R"]
        positions = ["top", "front", "bot", "back"]
        intPositions = ["topToFront", "frontToBot", "botToBack", "backToTop"]

        for side in sides:
            visibilityTopPivot(side)
            visibilityMain(side)
            for position in positions:
                visibilityCorners(side, position)
            for intPosition in intPositions:
                visibilityInterm(side, intPosition)

                ######################## End

    short_sleeveTemplate = ("short_sleeve_ctrls_template")

    if mc.objExists(short_sleeveTemplate):

        main()

    else:

        pass