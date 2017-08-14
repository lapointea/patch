import maya.cmds as mc

def patch():
	
	import maya.cmds as mc
	
	
	
	
	def pocketGen():
	
	
		PockSurf = ["L_pockDn_surf", "L_pockUp_surf", "R_pockDn_surf", "R_pockUp_surf"]
		sides = ['L','R']
		pockPos = ["pockDn", "pockUp"]
		pockName = ['IK','FKoffset', 'FK', 'mainOffset', 'mainFK', 'global']
		suffix = ['ctrl', 'jnt', 'orig','end','surf','fol', 'Shape', 'mainIKCnct', 'folCnct', 'folZero']
		pos = ['top','mid','bot']



		pTagLoop = []


		def addTag(targets=(),tag='PocketTag'):
			'''
			
			addTag(targets=[],tag='')
			addTag : wil add a string extra attribute, that will allow you to track back the object later
			'''
			taggedList = []
			for each in targets :
				Attr = tag
				if not mc.ls('%s.%s' %(each,Attr)):
					mc.addAttr( each , ln = Attr , dt = 'string')
					mc.setAttr('%s.%s' %(each,Attr) , l=True)
					taggedList.append(each)
			return taggedList





		#### find all pocket IK_ctrl_orig and IK_jnt_orig ####

		allpocketsLoop = mc.ls('*%s*' % pockPos[0],'*%s*' % pockPos[1])

		pocketGrpOrig = []
		pocketGrpjnt = []
		pocketGrpIK = []

		for orig in allpocketsLoop:
			origSplitTmp = orig.rsplit('_' , 1 )[1]
			if origSplitTmp == "orig":
				pocketGrpOrig.append(orig)

		for IK in pocketGrpOrig:
			IKTmp = IK.split('_' , 3 )[2]
			if IKTmp == "IK":
				pocketGrpIK.append(IK)


		for jnt in pocketGrpIK:
				jntTmp = jnt.rsplit('_' , 2 )[1]
				if jntTmp == "jnt":
					pocketGrpjnt.append(jnt)
				if jntTmp == "ctrl":
					pocketGrpjnt.append(jnt)


		#### create folCnct and folZero grp on pocket IK_ctrl_orig and IK_jnt_orig ####


		cnctGrpBtn = []

		LpockUpGrp = []
		RpockUpGrp = []
		LpockDnGrp = []
		RpockDnGrp = []


		for Pocketpos in pocketGrpjnt:
			
			nameSplitTmp = Pocketpos.rsplit('_' , 1 )[0]
			zeroGrp = mc.group(em=True, n='%s_folZero' % nameSplitTmp)
			cnctGrp = mc.group(zeroGrp, n='%s_folCnct' % nameSplitTmp)
			BtnPT = mc.xform(Pocketpos, query=True, t=True, ws=True)
			BtnPR = mc.xform(Pocketpos, query=True, ro=True, ws=True)
			mc.setAttr('%s.rotate' % cnctGrp, BtnPR[0], BtnPR[1], BtnPR[2])
			mc.setAttr('%s.translate' % cnctGrp, BtnPT[0], BtnPT[1], BtnPT[2])
			mc.parent(Pocketpos, zeroGrp)


			sidenameSplit = cnctGrp.split('_' , 1 )[0]    
			if sidenameSplit == "L":
				HightnameSplit = cnctGrp.split('_' , 2 )[1]
				if HightnameSplit == "pockDn":
					LpockDnGrp.append(cnctGrp)
				if HightnameSplit == "pockUp":
					LpockUpGrp.append(cnctGrp)
			
			if sidenameSplit == "R":
				HightnameSplit = cnctGrp.split('_' , 2 )[1]
				if HightnameSplit == "pockDn":
					RpockDnGrp.append(cnctGrp)
				if HightnameSplit == "pockUp":
					RpockUpGrp.append(cnctGrp)

			### create respectives group for pocket position (L or R and UP or Down)

		folClnLs = []
			
		CrtPocketGrp = [LpockUpGrp,RpockUpGrp,LpockDnGrp,RpockDnGrp]

		for allGrp in CrtPocketGrp:
			allGrpSize = len(allGrp)
			if allGrpSize >= 1:
				nameSplit = allGrp[0].rsplit('_' , 4 )[0]
				
				mainGrpAdd = mc.group(allGrp, n='%s_grp' % nameSplit)
				folClnLs.append(mainGrpAdd)
				pTagLoop.append(mainGrpAdd)
				
			



		### create Ik handles on Pockets and parent to ctrl ###


		pockIkCrt = mc.ls('**_%s_%s_**_%s' % (pockPos[0], pockName[0], suffix[1]), '**_%s_%s_**_%s' % (pockPos[1], pockName[0], suffix[1]))

		for crt in pockIkCrt:
			pockIkName = crt.rsplit('_' , 1 )[0]
			IkCrtEnd = crt + "_%s" % (suffix[3])
			IkCrtCtrl = pockIkName + "_%s" %(suffix[0])
			mc.ikHandle( n='%s_ikh' %(pockIkName), sj='%s' %(crt), ee='%s' %(IkCrtEnd))
			ikHdle = mc.ls(sl=True)
			mc.setAttr('%s.visibility' %(ikHdle[0]), 0)
			mc.parent(ikHdle, IkCrtCtrl) 




		### create mainIKCnct group on ik and Fk ctrl Orig ###


		IkconnctCtrlLoop = mc.ls('**_%s_**_**_%s' % ( pockName[2], suffix[0]), '**_%s_**_%s' % ( pockName[0], suffix[0]))
		IkconnctCtrl = []


				### make sure there is only pocket rigs ###
		for pocket in IkconnctCtrlLoop:
			posPocketTmp = pocket.split('_' , 2 )[1]
			if posPocketTmp == "pockDn":
				IkconnctCtrl.append(pocket)
			if posPocketTmp == "pockUp":
				IkconnctCtrl.append(pocket)


		IkconnctOrig = []


		for all in IkconnctCtrl:
			IkCtmp = all + "_%s" % (suffix[2])
			IkconnctOrig.append(IkCtmp)



		for nGrp in IkconnctCtrl:
			SelTrs = mc.xform(nGrp, query=True, t=True, ws=True)
			SelRt = mc.xform(nGrp, query=True, ro=True, ws=True)
			pockIkNameSplit = nGrp.rsplit('_' , 1 )[0]
			mc.group(nGrp, n="%s_mainIKCnct" % pockIkNameSplit, em=True) 
			SelGrp = mc.ls(sl=True)
			mc.setAttr('%s.translate' % SelGrp[0], SelTrs[0], SelTrs[1], SelTrs[2])
			mc.setAttr('%s.rotate' % SelGrp[0], SelRt[0], SelRt[1], SelRt[2])
			
			
			for each in SelGrp:
				mc.parent(SelGrp, IkconnctOrig[0])
				IkconnctOrig.pop(0)
					
				mc.parent(nGrp, SelGrp)



		#### connect mainOffset ctrl to mainIKCnct grp ###

				### mainOffset_ctrl
		LDnmainOff = '%s_%s_%s_%s' % (sides[0], pockPos[0], pockName[3], suffix[0])
		RDnmainOff = '%s_%s_%s_%s' % (sides[1], pockPos[0], pockName[3], suffix[0])
		LUpmainOff = '%s_%s_%s_%s' % (sides[0], pockPos[1], pockName[3], suffix[0])
		RUpmainOff = '%s_%s_%s_%s' % (sides[1], pockPos[1], pockName[3], suffix[0])

				### mainFK_top_ctrl
		LDntpmainFk = '%s_%s_%s_%s_%s' %(sides[0], pockPos[0], pockName[4], pos[0], suffix[0])
		RDntpmainFk = '%s_%s_%s_%s_%s' %(sides[1], pockPos[0], pockName[4], pos[0], suffix[0])
		LUptpmainFk = '%s_%s_%s_%s_%s' %(sides[0], pockPos[1], pockName[4], pos[0], suffix[0])
		RUptpmainFk = '%s_%s_%s_%s_%s' %(sides[1], pockPos[1], pockName[4], pos[0], suffix[0])

				### mainFK_mid_ctrl
		LDnMidmainFk = '%s_%s_%s_%s_%s' %(sides[0], pockPos[0], pockName[4], pos[1], suffix[0])
		RDnMidmainFk = '%s_%s_%s_%s_%s' %(sides[1], pockPos[0], pockName[4], pos[1], suffix[0])
		LUpMidmainFk = '%s_%s_%s_%s_%s' %(sides[0], pockPos[1], pockName[4], pos[1], suffix[0])
		RUpMidmainFk = '%s_%s_%s_%s_%s' %(sides[1], pockPos[1], pockName[4], pos[1], suffix[0])





		########## FK_01_top_mainFKCnct


		if mc.objExists('L_pockDn_global_orig'):
			mc.select('%s_%s_%s_**_%s_%s' % (sides[0], pockPos[0], pockName[2], pos[0], suffix[7]))
			LpockDnTopFKCnct = mc.ls(sl=True)
			for each in LpockDnTopFKCnct:
				mc.connectAttr('%s.rotate' %(LDntpmainFk), '%s.rotate' %(each))
				mc.connectAttr('%s.translate' %(LDntpmainFk), '%s.translate' %(each))
		else:
			print " no L_pockDn exist"


		if mc.objExists('L_pockUp_global_orig'):
			mc.select('%s_%s_%s_**_%s_%s' % (sides[0], pockPos[1], pockName[2], pos[0], suffix[7]))
			LpockUpTopFKCnct = mc.ls(sl=True)
			for each in LpockUpTopFKCnct:
				mc.connectAttr('%s.rotate' %(LUptpmainFk), '%s.rotate' %(each))
				mc.connectAttr('%s.translate' %(LUptpmainFk), '%s.translate' %(each))
		else:
			print " no L_pockUp exist"


		if mc.objExists('R_pockDn_global_orig'):    
			mc.select('%s_%s_%s_**_%s_%s' % (sides[1], pockPos[0], pockName[2], pos[0], suffix[7]))
			RpockDnTopFKCnct = mc.ls(sl=True)
			for each in RpockDnTopFKCnct:
				mc.connectAttr('%s.rotate' %(RDntpmainFk), '%s.rotate' %(each))
				mc.connectAttr('%s.translate' %(RDntpmainFk), '%s.translate' %(each))
		else:
			print " no R_pockDn exist" 
			
			
		if mc.objExists('R_pockUp_global_orig'):
			mc.select('%s_%s_%s_**_%s_%s' % (sides[1], pockPos[1], pockName[2], pos[0], suffix[7]))
			RpockuptopFKCnct = mc.ls(sl=True)
			for each in RpockuptopFKCnct:
				mc.connectAttr('%s.rotate' %(RUptpmainFk), '%s.rotate' %(each))
				mc.connectAttr('%s.translate' %(RUptpmainFk), '%s.translate' %(each))
		else:
			print " no R_pockUp exist"



		########## FK_01_mid_mainFKCnct


		if mc.objExists('L_pockDn_global_orig'):
			mc.select('%s_%s_%s_**_%s_%s' % (sides[0], pockPos[0], pockName[2], pos[1], suffix[7]))
			LpockDnMidFKCnct = mc.ls(sl=True)
			for each in LpockDnMidFKCnct:
				mc.connectAttr('%s.rotate' %(LDnMidmainFk), '%s.rotate' %(each))
				mc.connectAttr('%s.translate' %(LDnMidmainFk), '%s.translate' %(each))
		else:
			print " no L_pockDn exist"
				 
			
		if mc.objExists('L_pockUp_global_orig'):
			mc.select('%s_%s_%s_**_%s_%s' % (sides[0], pockPos[1], pockName[2], pos[1], suffix[7]))
			LpockUpMidFKCnct = mc.ls(sl=True)
			for each in LpockUpMidFKCnct:
				mc.connectAttr('%s.rotate' %(LUpMidmainFk), '%s.rotate' %(each))
				mc.connectAttr('%s.translate' %(LUpMidmainFk), '%s.translate' %(each))
		else:
			print " no L_pockUp exist"
				  
			
		if mc.objExists('R_pockDn_global_orig'):
			mc.select('%s_%s_%s_**_%s_%s' % (sides[1], pockPos[0], pockName[2], pos[1], suffix[7]))
			RpockDnMidFKCnct = mc.ls(sl=True)
			for each in RpockDnMidFKCnct:
				mc.connectAttr('%s.rotate' %(RDnMidmainFk), '%s.rotate' %(each))
				mc.connectAttr('%s.translate' %(RDnMidmainFk), '%s.translate' %(each))
		else:
			print " no R_pockDn exist" 
			

		if mc.objExists('R_pockUp_global_orig'):
			mc.select('%s_%s_%s_**_%s_%s' % (sides[1], pockPos[1], pockName[2], pos[1], suffix[7]))
			RpockUpMidFKCnct = mc.ls(sl=True)
			for each in RpockUpMidFKCnct:
				mc.connectAttr('%s.rotate' %(RUpMidmainFk), '%s.rotate' %(each))
				mc.connectAttr('%s.translate' %(RUpMidmainFk), '%s.translate' %(each))
		else:
			print " no R_pockUp exist"



		########## IK_04_mainIKCnct

		if mc.objExists('L_pockDn_global_orig'):
			mc.select('%s_%s_%s_**_%s' % (sides[0], pockPos[0], pockName[0], suffix[7]))
			LpockDnmainIKCnct = mc.ls(sl=True)
			for each in LpockDnmainIKCnct:
				mc.connectAttr('%s.rotate' %(LDnmainOff), '%s.rotate' %(each))
				mc.connectAttr('%s.translate' %(LDnmainOff), '%s.translate' %(each))
		else:
			print " no L_pockDn exist"
			
		if mc.objExists('L_pockUp_global_orig'):
			mc.select('%s_%s_%s_**_%s' % (sides[0], pockPos[1], pockName[0], suffix[7]))
			LpockUpmainIKCnct = mc.ls(sl=True)
			for each in LpockUpmainIKCnct:
				mc.connectAttr('%s.rotate' %(LUpmainOff), '%s.rotate' %(each))
				mc.connectAttr('%s.translate' %(LUpmainOff), '%s.translate' %(each))
		else:
			print " no L_pockUp exist"
				  
			
		if mc.objExists('R_pockDn_global_orig'):
			mc.select('%s_%s_%s_**_%s' % (sides[1], pockPos[0], pockName[0], suffix[7]))
			RpockDnmainIKCnct = mc.ls(sl=True)
			for each in RpockDnmainIKCnct:
				mc.connectAttr('%s.rotate' %(RDnmainOff), '%s.rotate' %(each))
				mc.connectAttr('%s.translate' %(RDnmainOff), '%s.translate' %(each))
		else:
			print " no R_pockDn exist"
			
		if mc.objExists('R_pockUp_global_orig'):
			mc.select('%s_%s_%s_**_%s' % (sides[1], pockPos[1], pockName[0], suffix[7]))
			RpockUpmainIKCnct = mc.ls(sl=True)
			for each in RpockUpmainIKCnct:
				mc.connectAttr('%s.rotate' %(RUpmainOff), '%s.rotate' %(each))
				mc.connectAttr('%s.translate' %(RUpmainOff), '%s.translate' %(each))
		else:
			print " no R_pockUp exist"


		#### parent mainFK to FolCnct ###



		PaMainFk = mc.ls('**_%s_%s_%s_%s_%s' %(pockPos[0], pockName[4], pos[0], suffix[0], suffix[2]), '**_%s_%s_%s_%s_%s' %(pockPos[1], pockName[4], pos[0], suffix[0], suffix[2]))

		PaMainFkFol = mc.ls('**_%s_%s_03_%s_%s' %(pockPos[0], pockName[0], suffix[1], suffix[9]), '**_%s_%s_03_%s_%s' %(pockPos[1], pockName[0], suffix[1], suffix[9]))

		for each in PaMainFkFol:
			mc.parent(PaMainFk[0], each)
			PaMainFk.pop(0)
			
		#### parent mainOffset to FolCnct ###

		PaMainOff = mc.ls('**_%s_%s_%s_%s' %(pockPos[0], pockName[3], suffix[0], suffix[2]), '**_%s_%s_%s_%s' %(pockPos[1], pockName[3], suffix[0], suffix[2]))

		PaMainOffFol = mc.ls('**_%s_%s_03_%s_%s' %(pockPos[0], pockName[0], suffix[0], suffix[9]), '**_%s_%s_03_%s_%s' %(pockPos[1], pockName[0], suffix[0], suffix[9]))

		for each in PaMainOffFol:
			mc.parent(PaMainOff[0], each)
			PaMainOff.pop(0)


		#### Delete useless Ctrl and cleaner groups ####


		folClnPock = mc.group(folClnLs, n="pocket_grp", em=True)
		mc.parent(folClnLs, folClnPock)
		mc.parent(folClnPock, "root_gimbal_ctrl")

			
		DelGrpGlobal = mc.ls('**_%s_%s_%s' %(pockPos[0], pockName[-1], suffix[2]), '**_%s_%s_%s' %(pockPos[1], pockName[-1], suffix[2]))
		mc.delete(DelGrpGlobal)


		### connect Vis hip_root_ctrl_attrs to pocket_grp 

			### check if attributes exist on hip_root_ctrl and delete them if so
			
		attrDelLoop = []

		AttrChck = mc.listAttr("hip_root_ctrl")
		for allAttr in AttrChck:
			if allAttr == "Pockets_Vis":
				attrDelLoop.append(allAttr)
			if allAttr == "______________":
				attrDelLoop.append(allAttr)

		lenAttrLoop = len(attrDelLoop)
		if lenAttrLoop >= 0:
			for delLoop in range(0,lenAttrLoop):
				mc.setAttr("hip_root_ctrl.%s" % attrDelLoop[delLoop], lock=False)
				mc.deleteAttr("hip_root_ctrl.%s" % attrDelLoop[delLoop])


			### create attributes for vis  

		pocketAttr = mc.ls("hip_root_ctrl")

		mc.addAttr(pocketAttr[0], longName= "______________", at='enum', en="Extra_vis:")

		mc.addAttr(pocketAttr[0], longName= "Pockets_Vis", at='bool', dv=False)

		mc.setAttr("%s.______________" %(pocketAttr[0]),k=False, channelBox=True, lock=True)
		mc.setAttr('%s.Pockets_Vis' %(pocketAttr[0]),k=False, channelBox=True)
		mc.connectAttr('%s.Pockets_Vis' %(pocketAttr[0]), "pocket_grp.visibility")



		####  clean Sets  ####

			
				


		pocketsSetsloop = mc.ls('*pockDn*', '*pockUp*')

		filterpocketsSetsloop = []


		for all in pocketsSetsloop:
			setSplitTmp = all.rsplit('_' , 1 )[1]
			if setSplitTmp == "set":
				reSplitTmp = all.rsplit('_' , 1 )[1]
				if reSplitTmp == "set":
					filterpocketsSetsloop.append(all)




		fkSetsLoop = []
		ZsSetsLoop = []
		skinSetsLoop = []
		ctrlSetsLoop = []
		animSetsLoop = []

		for setLoop in filterpocketsSetsloop:
			animSetsLoop.append(setLoop)
			tagNameSplitTmp = setLoop.rsplit('_' , 1 )[1]
			SetNameSplitTmp = setLoop.rsplit('_' , 2 )[1]
			
			if tagNameSplitTmp == "set":
				pTagLoop.append(setLoop)
		   
			if SetNameSplitTmp == "skin":
				skinSetsLoop.append(setLoop)
				animSetsLoop.remove(setLoop)        
			
			if SetNameSplitTmp == "ZS":
				ZsSetsLoop.append(setLoop)
				animSetsLoop.remove(setLoop)
					  


			if SetNameSplitTmp == "fk":
				fkSetsLoop.append(setLoop)
			if SetNameSplitTmp == "ctrl":
				ctrlSetsLoop.append(setLoop)   
				  

				#### sort anim Set
				
		animSet = mc.sets(animSetsLoop, n="pockets_anim_set")

		mc.sets(animSetsLoop, rm="anim_set")
		mc.sets(animSet, add="anim_set")


				#### sort skin Set
				
		skinSet = mc.sets(skinSetsLoop, n="pockets_skin_set")

		mc.sets(skinSetsLoop, rm="skin_set")
		mc.sets(skinSet, add="skin_set")


				#### sort skin Set
				
		ZSSet = mc.sets(ZsSetsLoop, n="pockets_ZS_set")

		mc.sets(ZsSetsLoop, rm="ALL_ZS_set")
		mc.sets(ZSSet, add="ALL_ZS_set")





		addTag(targets=(pTagLoop),tag='PocketTag')








	if mc.objExists('L_pockDn_global_orig'):
		pocketGen()
	else:
		if mc.objExists('L_pockUp_global_orig'):
			pocketGen()
		else:
			if mc.objExists('R_pockDn_global_orig'):
				pocketGen()
			else:
				if mc.objExists('R_pockDn_global_GUIDE'):
					pocketGen()
				else:
					print "no pocket is in the Scene"



	
