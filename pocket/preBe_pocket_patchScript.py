import maya.cmds as mc

def patch():
	
	def pocketRnm():

		PockSurf = ("L_pockDn_surf", "L_pockUp_surf", "R_pockDn_surf", "R_pockUp_surf")
		sides = ['L','R']
		pockPos = ["pockDn", "pockUp"]
		pockName = ['IK','FKoffset', 'FK', 'mainOffset', 'mainFK', 'global']
		suffix = ['ctrl', 'jnt', 'orig','end','surf','fol', 'Shape', 'mainIKCnct', 'folCnct', 'folZero']
		pos = ['top','mid','bot']

		#### rename jntend to jnt_end


		pocketSlgrp = mc.ls("*_IK_*_jntend")


		RnameEndSel = []


		for jntendloop in pocketSlgrp:
			testBind = jntendloop.rsplit('_' , 1 )[1]
			if testBind == "jntend" :
				RnameEndSel.append(jntendloop)


		if RnameEndSel == 0:
			print "no jntend to rename"
			
			
		else:
			for all in RnameEndSel:
				mc.select(all)
				RnameEnd = mc.ls(sl=True)

				RnameEndList = RnameEnd[0].rsplit('_' , 1 )[0]
				mc.rename("%s_%s_%s" % (RnameEndList, suffix[1], suffix[3]))


	if mc.objExists('L_pockDn_global_GUIDE'):
		pocketRnm()
	else:
		if mc.objExists('L_pockUp_global_GUIDE'):
			pocketRnm()
		else:
			if mc.objExists('R_pockDn_global_GUIDE'):
				pocketRnm()
			else:
				if mc.objExists('R_pockUp_global_GUIDE'):
					pocketRnm()
				else:
					print "pockets are not in the Scene"
