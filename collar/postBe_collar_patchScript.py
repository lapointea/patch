import maya.cmds as mc

def patch():

    
    if mc.objExists("collar_mainOffset"):


		
		### sets of name use ###

		CNames = ['neckCollar','neckCollarDrv','getRoll','collar','collarIK','collarOffset', 'collarFK', 'collarAtt']
		sides = ['L','B','R']
		numb =  ['V0','V1','V2','V3','V4']
		FkHieNm = ['bot','mid','top']
		suffix = ['ctrl', 'jnt', 'orig','end', 'Cns']
		IkCrt = ['B_collarIK_01','L_collarIK_01','L_collarIK_02','L_collarIK_03','L_collarIK_04','R_collarIK_01','R_collarIK_02','R_collarIK_03','R_collarIK_04']
		maDrv = ['V0_neckCollarDrv','V1_neckCollarDrv','V2_neckCollarDrv','V3_neckCollarDrv','V4_neckCollarDrv']

		paLsEnd = []
		parentGrpLp = []

		def addTag(targets=(paLsEnd),tag='collarTag'):
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

		### rename same naming issue generation issues ####

		RnmSuffix = ['jnt','end', 'neckCollarDrv']

		collSlgrp = mc.listRelatives("collar_mainOffset", ad=True)



		RnameEndSel = []

		for jntendloop in collSlgrp:
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
				mc.rename("%s_%s_%s" % (RnameEndList,RnmSuffix[0], RnmSuffix[1]))

			
			
		RnameDrvEndSel = mc.ls("**_neckCollarDrvend")

		if RnameDrvEndSel == 0:
			print "no Drvend to rename"
			
			
		else:	
			for all in RnameDrvEndSel:
				mc.select("**_neckCollarDrvend")
				RnameEnd = mc.ls(sl=True)

				RnameEndList = RnameEnd[0].rsplit('_' , 1 )[0]
				mc.rename("%s_%s_%s" % (RnameEndList,RnmSuffix[2], RnmSuffix[1]))

		####




		v0CollarDrvLs = []
		if mc.objExists("L_getRoll_03_jnt_orig"):
			v0CollarDrvLs.append("L_getRoll_03_jnt_orig")
		if mc.objExists("R_getRoll_03_jnt_orig"):
			v0CollarDrvLs.append("R_getRoll_03_jnt_orig")
		if mc.objExists("B_getRoll_01_jnt_orig"):
			v0CollarDrvLs.append("B_getRoll_01_jnt_orig")

		v1CollarDrvLs = []
		if mc.objExists("L_getRoll_02_jnt_orig"):
			v1CollarDrvLs.append("L_getRoll_02_jnt_orig")
		if mc.objExists("R_getRoll_04_jnt_orig"):
			v1CollarDrvLs.append("R_getRoll_04_jnt_orig")

		v2CollarDrvLs = []
		if mc.objExists("L_getRoll_04_jnt_orig"):
			v2CollarDrvLs.append("L_getRoll_04_jnt_orig")
		if mc.objExists("R_getRoll_02_jnt_orig"):
			v2CollarDrvLs.append("R_getRoll_02_jnt_orig")

		if mc.objExists("R_getRoll_01_jnt_orig"):
			v3CollarDrvLs = mc.ls("R_getRoll_01_jnt_orig")

		if mc.objExists("L_getRoll_01_jnt_orig"):
			v4CollarDrvLs = mc.ls("L_getRoll_01_jnt_orig")


		SnpGetRollSel = (v0CollarDrvLs, v1CollarDrvLs, v2CollarDrvLs, v3CollarDrvLs, v4CollarDrvLs)


		collDrv = len(numb)
		for b in range(0,collDrv):

			SnpGetRollSelCn = mc.pointConstraint("neck_ctrl_deform_SKN_03", "%s_orig" % maDrv[b], mo=False)
			mc.delete(SnpGetRollSelCn)    





		### pointConstraint Cns to neck_ctrl_deform_SKN_* ####

		nCollOrig = 'neckCollar_Cns_orig'
		vDrvTmp = []

		if mc.objExists("neck_ctrl_deform_SKN_05"):
			neckSKNjntCn = mc.ls("neck_ctrl_deform_SKN_05")
		else:
			neckSKNjntCn = mc.ls("neck_ctrl_deform_SKN_04")    

		mc.parentConstraint(neckSKNjntCn, nCollOrig, mo=False)
		mc.select(nCollOrig)
		mc.delete(cn=True)

			
		for b in numb:
			mc.select('%s_%s_%s' % (b, CNames[1], suffix[3]))
			Sel = mc.ls(sl=True)
			vDrvTmp.extend(Sel) 


		for pCns in vDrvTmp:
			mc.pointConstraint(nCollOrig, pCns, mo=False)
			mc.select(pCns)
			mc.delete(cn=True)

		poCns = mc.pointConstraint("neck_ctrl_deform_SKN_07", "neckCollar_Cns", mo=True)



		### aimConstraint rotation drivers ###
		for allAim in maDrv:
			
			allAimCnctGrp = mc.group(n="%s_cnct" % allAim, em=True)
			allAimCnctGrpZero = mc.group(allAimCnctGrp,n="%s_cnct_zero" % allAim)
			PCnsTmp = mc.parentConstraint('%s_orig' % allAim ,allAimCnctGrpZero, mo=False)
			mc.delete(PCnsTmp)
			aimAttTmp = mc.aimConstraint("neckCollar_Cns", allAimCnctGrp, mo=True, w=1, aim=(0.0, 1.0, 0.0), u=(0.0, 0.0, 1.0), wut="none", sk=["y"])
			mc.parent(allAimCnctGrpZero, '%s_orig' % allAim)
			mc.connectAttr('%s.rotateX' % allAimCnctGrp, '%s.rotateX' % allAim)
			mc.connectAttr('%s.rotateZ' % allAimCnctGrp, '%s.rotateZ' % allAim)
			
			
		### Scale -X FK and IK ctrl on Right side to match Left behaviour ###

		sclIKTrns = mc.ls('%s_%s_**_%s_%s' %(sides[2],CNames[4],suffix[0],suffix[2]))
		sclFKTrns = mc.ls('%s_%s_**_%s_%s' %(sides[2],CNames[6],suffix[0],suffix[2]))


		for sEach in sclIKTrns:
			mc.setAttr('%s.scaleX' % (sEach), -1)

		for sEach in sclFKTrns:
			FrLoc = mc.spaceLocator()
			lisAllFkOffset = mc.listRelatives(sEach, ad=True)
			DelLocParent = []
			for allOrig in lisAllFkOffset:
				lisAllFkOffsetOrig = allOrig.rsplit('_', 1)[1]
				if lisAllFkOffsetOrig == 'orig':
					parentTemp = mc.parentConstraint(FrLoc, allOrig, mo=True)
					DelLocParent.extend(parentTemp)
					
					
			mc.setAttr('%s.scaleX' % (sEach), -1)
			mc.delete(FrLoc,DelLocParent)
			
		### create Ik handles on collarIk and parent to ctrl ###


		for Crt in IkCrt:
			IkCrtjnt = Crt + "_%s" % (suffix[1])
			IkCrtEnd = IkCrtjnt + "_%s" % (suffix[3])
			IkCrtCtrl = Crt + "_%s" %(suffix[0])
			mc.ikHandle( n='%s_ikh' %(Crt), sj='%s' %(IkCrtjnt), ee='%s' %(IkCrtEnd))
			ikHdle = mc.ls(sl=True)
			mc.setAttr('%s.visibility' %(ikHdle[0]), 0)
			mc.parent(ikHdle, IkCrtCtrl)      



					   
		### set collarAtt_ctrl create attribute for intensity and offset ###

		if mc.objExists("collarAtt_ctrl"):
			
			
			if mc.objExists("neck_ik_root_orig"):
				### snap AttrCtrl to rootCtrl
				NeckAttr = "neck_ik_root_orig"
				collarAttr = "collarAtt_ctrl_orig"
				collarAttrCtrl = "collarAtt_ctrl"
			   
				Seltf = mc.xform(NeckAttr, query=True, t=True, ws=True)
				Selrf = mc.xform(NeckAttr, query=True, ro=True, ws=True)
				mc.setAttr('%s.translate' % collarAttr, Seltf[0], Seltf[1], Seltf[2])
				mc.setAttr('%s.rotate' % collarAttr, Selrf[0], Selrf[1], Selrf[2])
				
				
				mc.setAttr('%s.translate' % collarAttrCtrl, 0,1.647,-1.040)
				mc.setAttr('%s.rotate' % collarAttrCtrl, 90,0,0)
				mc.makeIdentity('collarAtt_ctrl', apply=True, t=True, r=True)

			else:
				print "no root to snap to"
				
			
			### add Attributes to att_ctrl and connect them to all get rolls
			
			mc.select('**_%s_**_%s' %(CNames[2],suffix[1]))
			attNameLoop = mc.ls(sl=True)

			mc.select("%s_%s" %(CNames[7], suffix[0]))
			collarAttRmv = mc.ls(sl=True)
			
			
			mc.addAttr(longName= "Collar_Blends", at='enum', en="_____:")
			mc.setAttr("%s.Collar_Blends" %(collarAttRmv[0]),k=False, channelBox=True)
			
			
			mc.addAttr(longName= "Follow_translate", at='float', min=0, max=1 , dv=.2)
			mc.setAttr("%s.Follow_translate" %(collarAttRmv[0]),k=True)

			mc.addAttr(longName= "Follow_all", at='float', min=0, max=1 , dv=1)
			mc.setAttr("%s.Follow_all" %(collarAttRmv[0]),k=True)


			mc.addAttr(longName= "intensity", at='enum', en="__:")
			mc.setAttr("%s.intensity" %(collarAttRmv[0]),k=False, channelBox=True)
			
			
			for name in attNameLoop:

				baseName = name.split('_' , 1 )[0]
				endName = name.rsplit('_' , 2 )[1]
				fullName = '%s_%s_%s' %(baseName, CNames[3], endName)
				mc.select(collarAttRmv[0])
				mc.addAttr(longName= "%s_intensity" % fullName, k=True, at='float',  dv=.5)
				
			mc.select(collarAttRmv[0])  
			mc.addAttr(longName= "Offset", at='enum', en="__:")
			mc.setAttr("%s.Offset" %(collarAttRmv[0]),k=False, channelBox=True)

			for name in attNameLoop:

				baseName = name.split('_' , 1 )[0]
				endName = name.rsplit('_' , 2 )[1]
				fullName = '%s_%s_%s' %(baseName, CNames[3], endName)
				mc.select("%s_%s" %(CNames[7], suffix[0]))
				mc.addAttr(longName= "%s_offset" % fullName, k=True, at='float',  dv=10)
			  
			  
			mc.select(collarAttRmv[0])  
			mc.addAttr(longName= "Collar_Vis", at='enum', en="_____:")
			mc.setAttr("%s.Collar_Vis" %(collarAttRmv[0]),k=False, channelBox=True)
		  
			mc.addAttr(longName= "Advanced", at='bool', dv=1)
			mc.setAttr("%s.Advanced" %(collarAttRmv[0]),k=False, channelBox=True)
			
			mc.addAttr(longName= "Tweak_Vis", at='bool', dv=1)
			mc.setAttr("%s.Tweak_Vis" %(collarAttRmv[0]),k=False, channelBox=True)
				




			for all in collarAttRmv:
			   
				mc.setAttr("%s.tx" %(all),k=False, channelBox=False, lock=True)
				mc.setAttr("%s.ty" %(all),k=False, channelBox=False, lock=True)
				mc.setAttr("%s.tz" %(all),k=False, channelBox=False, lock=True)
				mc.setAttr("%s.rx" %(all),k=False, channelBox=False, lock=True)
				mc.setAttr("%s.ry" %(all),k=False, channelBox=False, lock=True)
				mc.setAttr("%s.rz" %(all),k=False, channelBox=False, lock=True)
				mc.setAttr("%s.sx" %(all),k=False, channelBox=False, lock=True)
				mc.setAttr("%s.sy" %(all),k=False, channelBox=False, lock=True)
				mc.setAttr("%s.sz" %(all),k=False, channelBox=False, lock=True)
				mc.setAttr("%s.sz" %(all),k=False, channelBox=False, lock=True)
				mc.setAttr("%s.visibility" %(all),k=False, channelBox=False, lock=True)
				mc.setAttr("%s.rotateOrder" %(all),k=False, channelBox=False, lock=True)

		else:
			print " no collar Attr ctrl exist "

		### set the translate Follow part


		grpOffset = mc.group(em=True, n="collar_mainOffset_followTrans")
		grpOffsetZero = mc.group(grpOffset, n="collar_mainOffset_followTrans_zero")
		parentGrpLp.append(grpOffsetZero)
		paLsEnd.append(grpOffsetZero)

		if mc.objExists("neck_ctrl_deform_SKN_07"):
			mc.parentConstraint("neck_ctrl_deform_SKN_07", grpOffsetZero, mo=False)
		mc.select(grpOffsetZero)
		mc.delete(cn=True)
		mc.pointConstraint("collar_mainOffset_orig", grpOffsetZero, mo=False)
		mc.select(grpOffsetZero)
		mc.delete(cn=True)

		mc.parentConstraint("neck_ctrl_deform_SKN_07", "collar_neck_drv_orig", mo=False)
		mc.select("collar_neck_drv_orig")
		mc.delete(cn=True)

		mc.parent("collar_mainOffset_orig", grpOffset)

		mc.parent("collar_neck_drv_orig", grpOffsetZero)

		tmpNameAddList = "collar_neck_drv_orig"
		parentGrpLp.append(tmpNameAddList)

		mc.parentConstraint("neck_ctrl_deform_SKN_07", "collar_neck_drv", mo=False)
		txFollowNode = mc.createNode('multDoubleLinear', n='collar_neck_drv_tx_Follow')
		tzFollowNode = mc.createNode('multDoubleLinear', n='collar_neck_drv_tz_Follow')
		mc.connectAttr('collar_neck_drv.translateX', '%s.input1' % txFollowNode)
		mc.connectAttr('collar_neck_drv.translateZ', '%s.input1' % tzFollowNode)
		mc.connectAttr('%s.output' % txFollowNode, '%s.translateX' % grpOffset)
		mc.connectAttr('%s.output' % tzFollowNode, '%s.translateZ' % grpOffset)

		mc.connectAttr("%s_%s.Follow_translate" %(CNames[7], suffix[0]), '%s.input2' % txFollowNode)
		mc.connectAttr("%s_%s.Follow_translate" %(CNames[7], suffix[0]), '%s.input2' % tzFollowNode)



		paLsEnd.append(txFollowNode)
		paLsEnd.append(tzFollowNode)

		### connect Visibility to collarAtt_ctrl ####

			### Advanced vis to FK and IK ctrl ###

		if mc.objExists("collarAtt_ctrl"):    
			
			
			mc.select("**_%s_**_%s_%s" %(CNames[6], suffix[0],suffix[2]), "**_%s_**_%s_%s" %(CNames[4], suffix[0],suffix[2]), '**_baseOffset_**_%s_%s' % (suffix[0], suffix[2]))
			TmpVis = mc.ls(sl=True)

			for allVis in TmpVis:
				mc.setAttr("%s.visibility" %(allVis),k=True, channelBox=True, lock=False)
				mc.connectAttr("%s_%s.Advanced" %(CNames[7], suffix[0]), "%s.visibility" % (allVis))

		else:
			print " no collar Attr ctrl exist "
			
			### tweak_vis to FK_offset ctrl ###

		if mc.objExists("collarAtt_ctrl"):

			mc.select("**_%s_**_**_%s_%s" %(CNames[5],suffix[0],suffix[2]))
			TmpVis = mc.ls(sl=True)

			for allVis in TmpVis:
				mc.setAttr("%s.visibility" %(allVis),k=True, channelBox=True, lock=False)
				mc.connectAttr("%s_%s.Tweak_Vis" %(CNames[7], suffix[0]), "%s.visibility" % (allVis))

		else:
			print " no collar Attr ctrl exist "


		### create nodes and connect them to getRoll ###


		mc.select('**_%s_**_%s' %(CNames[2],suffix[1]))
		nodCnc = mc.ls(sl=True)
		AVGCncPl = []
		multAttCn = []
		MultRev = []

		for each in nodCnc:

			baseName = each.split('_' , 1 )[0]
			endName = each.rsplit('_' , 2 )[1]
			fullName = '%s_%s_%s' %(baseName, CNames[3], endName)
			

			mc.createNode('multDoubleLinear', n='%s_Follow' %(each))
			fllwNd = mc.ls(sl=True)
			paLsEnd.extend(fllwNd)
			AVGCncPl.append(fllwNd[0])
			mc.connectAttr("%s_%s.Follow_all" %(CNames[7], suffix[0]),'%s.input2' % fllwNd[0])    
			
			mc.createNode('multDoubleLinear', n='%s_reverse' %(each))
			MultRevloop = mc.ls(sl=True)
			paLsEnd.extend(MultRevloop)
			mc.setAttr("%s.input2" %(MultRevloop[0]), 1)
			MultRev.append(MultRevloop[0])
			mc.connectAttr("%s.output" %(fllwNd[0]),'%s.input1' % (MultRevloop[0]))
			
			for cnct in MultRevloop:
				mc.createNode('plusMinusAverage', n='%s_offset_AVG' %(each))
				plMiAvNd = mc.ls(sl=True)
				paLsEnd.extend(plMiAvNd)
				mc.connectAttr("%s.output" %(cnct),'%s.input3D[0].input3Dx' % plMiAvNd[0])
				SwitchClmpND = mc.createNode('clamp', n='%s_onSwitch_clamp' %(each))
				paLsEnd.append(SwitchClmpND)
				mc.setAttr('%s.maxR' % SwitchClmpND,1)
				mc.connectAttr("%s.output" %(cnct),'%s.inputR' % SwitchClmpND)  
				
			for e in plMiAvNd:
				mc.connectAttr('collarAtt_ctrl.%s_offset' % fullName, '%s.input3D[1].input3Dx' % (e))  
				mc.createNode('clamp', n='%s_clamp' %(each))
				clNd = mc.ls(sl=True)
				paLsEnd.extend(clNd)
				
			for i in clNd:
				mc.connectAttr('%s.output3Dx' % (e), '%s.inputR' % (i))
				mc.setAttr('%s.maxR' % (i), 90)
				mc.createNode('multiplyDivide', n='%s_intensity_mult' %(each))
				multNd = mc.ls(sl=True)
				multAttCn.append(multNd[0])
				paLsEnd.extend(multNd)
				
			for mu in multNd:
				mc.connectAttr('%s.outputR' % (i), '%s.input1X' % (mu))
				mc.connectAttr('collarAtt_ctrl.%s_intensity' % fullName, '%s.input2X' % (mu))
				multDZero = mc.createNode('multDoubleLinear', n='%s_multD_zero' %(each))
			   
				paLsEnd.append(multDZero)
				
			mc.connectAttr('%s.outputX' % (mu),'%s.input1' % (multDZero))
			mc.connectAttr('%s.outputR' % (SwitchClmpND),'%s.input2' % (multDZero))
			mc.connectAttr('%s.output' % (multDZero),'%s.rotateX' % (each))
			
			
		## connect Drivers to positive axes joints##
			
		mc.connectAttr('%s.rotateX' % (maDrv[4]),'%s.input1' % (AVGCncPl[1]))      
		mc.connectAttr('%s.rotateZ' % (maDrv[1]),'%s.input1' % (AVGCncPl[2])) 
		mc.connectAttr('%s.rotateX' % (maDrv[3]),'%s.input1' % (AVGCncPl[5]))
		mc.connectAttr('%s.rotateZ' % (maDrv[2]),'%s.input1' % (AVGCncPl[6]))
		mc.connectAttr('%s.rotateZ' % (maDrv[0]),'%s.input1' % (AVGCncPl[7]))


		mc.connectAttr('%s.rotateX' % (maDrv[0]),'%s.input1' % (AVGCncPl[0]))
		mc.connectAttr('%s.rotateZ' % (maDrv[0]),'%s.input1' % (AVGCncPl[3]))
		mc.connectAttr('%s.rotateZ' % (maDrv[2]),'%s.input1' % (AVGCncPl[4]))
		mc.connectAttr('%s.rotateZ' % (maDrv[1]),'%s.input1' % (AVGCncPl[8]))   

		RevSetAttr = [MultRev[0], MultRev[3], MultRev[4], MultRev[8]]
		for negative in RevSetAttr:
			
			mc.setAttr('%s.input2' % (negative), -1)



		### change baseOffset Ctrl shape ##

		baseoffGuideLoop = mc.ls('*_baseOffset_**_ctrl_GUIDE')
		baseoffLoop = mc.ls('*_baseOffset_**_ctrl')

		baseofflen = len(baseoffGuideLoop)


		for swtCrv in range(0, baseofflen):
			swtCrvShpGuide = mc.listRelatives(baseoffGuideLoop[swtCrv], s=True)
			swtCrvShp = mc.listRelatives(baseoffLoop[swtCrv], s=True)
			
			mc.parent(swtCrvShpGuide,baseoffLoop[swtCrv], r=True, s=True)
			mc.delete(swtCrvShp)
			mc.rename(swtCrvShpGuide, "%s" % swtCrvShp[0])
			


		collarmainGuide = mc.listRelatives("collar_mainOffset_GUIDE", s=True)
		collarmain = mc.listRelatives("collar_mainOffset", s=True)
		mc.parent(collarmainGuide[3],"collar_mainOffset", r=True, s=True)
		mc.delete(collarmain)
		mc.rename(collarmainGuide[3], "%s" % collarmain[0])


		### clean up the rig ###


		mc.select("collar_mainOffset_SKN_orig", '**_%s_%s' % (CNames[1], suffix[2]), '%s_%s_%s' % (CNames[0], suffix[4], suffix[2]), '%s_neck_drv_%s' % (CNames[3],suffix[2]))
		jntVisLoop = mc.ls(sl=True)

		for vis in jntVisLoop:
			
			mc.setAttr('%s.visibility' % vis, k=False, channelBox=False, lock=False )
			mc.setAttr('%s.visibility' % vis, 0, lock=True)
		if mc.objExists("neck_ik_root"):
			if mc.objExists("neck_ik_root"):
				mc.parent(parentGrpLp, "neck_ik_root")
			else:
				print " no neck_ik_root to parent to "
		else:
			if mc.objExists("neck_ctrl_deform_00"):
				mc.parent(parentGrpLp, "neck_ctrl_deform_00")
			else:
				print " no neck_ctrl_deform_00 to parent to "


			###create collar Sets and sort them
			
		baseOffSets = mc.ls('*_baseOffset_**_fk_set')

		collarOffSets = mc.ls('*_%s_*_ctrl_fk_set' % CNames[5])

		collarFKSets = mc.ls('*_%s_**_ctrl_set' % CNames[6])

		collarIKSets = mc.ls('*_%s_**_ctrl_set' % CNames[4])

		mainOffsetSets = mc.ls('collar_mainOffset_set')

		allSets = (baseOffSets + collarOffSets + collarFKSets + collarIKSets + mainOffsetSets)

		paLsEnd.extend(allSets)

				#### sort anim Set
		animSetCollar = mc.sets(allSets, n="collar")

		mc.sets(allSets, rm="anim_set")
		mc.sets(animSetCollar, add="anim_set")

		paLsEnd.append(animSetCollar)

				#### sort ZS_set
		allSetsZSTmp = []
		for all in allSets:
			ZsSetsNm = all.split('_' , 2 )[1]
			allSetsZSTmp.append(ZsSetsNm)

		allSetsNM = []
		for i in allSetsZSTmp:
		  if i not in allSetsNM:
			  allSetsNM.append(i)

		collarZsSel = []      
		for each in allSetsNM:
			collarZsSelTmp = mc.ls('*_%s_*_ZS_set' % each)
			collarZsSel.extend(collarZsSelTmp) 


		ZSSetCollar = mc.sets(collarZsSel,'collar_mainOffset_ZS_set' , n="collar_ZS_set") 
				  
		mc.sets(collarZsSel,'collar_mainOffset_ZS_set' , rm="ALL_ZS_set")
		mc.sets(ZSSetCollar, add="ALL_ZS_set")

		paLsEnd.append(ZSSetCollar)

				#### sort skin_set

		collarSKNSel = []      
		for each in allSetsNM:
			collarSKNSelTmp = mc.ls('*_%s_*_skin_set' % each)
			collarSKNSel.extend(collarSKNSelTmp) 

		SKNSetCollar = mc.sets(collarSKNSel, n="collar_skin_set") 
				  
		mc.sets(collarSKNSel, rm="skin_set")
		mc.sets(SKNSetCollar, add="skin_set")


		paLsEnd.append(SKNSetCollar)

		##### Create Tag for all #####
		paLsEnd.append("collarAtt_ctrl_orig")

		addTag(targets=(paLsEnd),tag='collarTag')



    else:
        print "no collar template is in the Scene"
    
	
