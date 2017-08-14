# Alejandro Munoz Medina
# Attribute template connecting post behavior script

import maya.cmds as mc

def patch():

    # Alejandro Munoz Medina
    # Attribute template connecting post behavior script

    import maya.cmds as mc

    def main():

        import maya.cmds as mc

        ## Functions

        # transfer attributes from control to control

        # repurpose SW controls

        def repurposeCtrls(ctrl):

            import maya.cmds as mc

            shapes = mc.listRelatives("%s_attrs" % ctrl, s=True)

            for shape in shapes:
                mc.parent(shape, ctrl, r=True, s=True)

            mc.delete("%s_attrs_orig" % ctrl)
            mc.hide("%sShape" % ctrl)

        # hardcoding
        def hardcode():

            import maya.cmds as mc

            attr1 = "baseSpineFollow"
            attr2 = "neckTwistFollow"

            hip = "hip_root_ctrl"
            neck = "neck_ik_root"

            ##lower back
            mc.addAttr(hip, at="enum", sn="sep9", ln="____________", en="pelvis_ctrl", k=True, h=False)
            mc.setAttr("%s.sep9" % hip, k=False, l=True, cb=True)
            mc.addAttr(hip, at="double", ln=attr1, min=0, max=1, dv=1, k=True, h=False)
            mc.connectAttr("%s.%s" % (hip, attr1), "pelvis_ctrl.%s" % attr1)
            mc.setAttr("pelvis_ctrl.%s" % attr1, k=False, cb=False)

            ##neck
            mc.addAttr(neck, at="enum", sn="sep9", ln="____________", en="head_ctrl", k=True, h=False)
            mc.setAttr("%s.sep9" % neck, k=False, l=True, cb=True)
            mc.addAttr(neck, at="float", ln=attr2, min=0, max=1, dv=1, k=True, h=False)
            mc.setAttr("%s.%s" % (neck, attr2), k=False, cb=True)
            mc.connectAttr("%s.%s" % (neck, attr2), "head_ctrl.%s" % attr2)
            mc.setAttr("head_ctrl.%s" % attr2, k=False, cb=False)

        ### End

        # Variables

        ctrlList = ["hip_root_ctrl",
                    "neck_ik_root",
                    "L_arm_SW_ctrl",
                    "R_arm_SW_ctrl",
                    "L_leg_SW_ctrl",
                    "R_leg_SW_ctrl"]

        ## Execute functions

        for ctrl in ctrlList:
            repurposeCtrls(ctrl)

        hardcode()

    ### End

    if mc.objExists("attrs_ctrls_frame_orig"):
        main()
    else:
        print "There is no attribute panel in the scene"
        pass