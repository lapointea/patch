import maya.cmds as mc

def patch():

    def buttonPreSkin() :
        
    
		def addTag(targets=(),tag='ButtonTag'):
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


		bTagLoop = []

		allButtonLoop = mc.ls('*button*')

		ButtonGrpOrig = []
		for orig in allButtonLoop:
			origSplitTmp = orig.rsplit('_' , 1 )[1]
			if origSplitTmp == "orig":
				ButtonGrpOrig.append(orig)

		cnctGrpBtn = []
		for pos in ButtonGrpOrig:
			nameSplitTmp = pos.rsplit('_' , 1 )[0]
			zeroGrp = mc.group(em=True, n='%s_zero' % nameSplitTmp)
			cnctGrp = mc.group(zeroGrp, n='%s_Cnct' % nameSplitTmp)
			BtnPT = mc.xform(pos, query=True, t=True, ws=True)
			BtnPR = mc.xform(pos, query=True, ro=True, ws=True)
			mc.setAttr('%s.rotate' % cnctGrp, BtnPR[0], BtnPR[1], BtnPR[2])
			mc.setAttr('%s.translate' % cnctGrp, BtnPT[0], BtnPT[1], BtnPT[2])
			mc.parent(pos, zeroGrp)
			cnctGrpBtn.append(cnctGrp)
			bTagLoop.append(zeroGrp)
			bTagLoop.append(cnctGrp)    


		buttonGrp = mc.group(cnctGrpBtn, n="button_grp")
		mc.parent(buttonGrp, "*root_gimbal_ctrl")
		bTagLoop.append(buttonGrp)


		#### create button Sets and sort them #####


		buttonSetsloop = mc.ls('*button*')

		fkSetsLoop = []
		ZsSetsLoop = []
		skinSetsLoop = []

		for setLoop in buttonSetsloop:
			tagNameSplitTmp = setLoop.rsplit('_' , 1 )[1]
			SetNameSplitTmp = setLoop.rsplit('_' , 2 )[1]
			
			if tagNameSplitTmp == "set":
				bTagLoop.append(setLoop)
			if SetNameSplitTmp == "fk":
				fkSetsLoop.append(setLoop)   
			if SetNameSplitTmp == "ZS":
				ZsSetsLoop.append(setLoop)      
			if SetNameSplitTmp == "skin":
				skinSetsLoop.append(setLoop)  

				#### sort anim Set
				
		animSetButton = mc.sets(fkSetsLoop, n="button_anim_set")

		mc.sets(fkSetsLoop, rm="anim_set")
		mc.sets(animSetButton, add="anim_set")


				#### sort skin Set
				
		skinSetButton = mc.sets(skinSetsLoop, n="buttons_skin_set")

		mc.sets(skinSetsLoop, rm="skin_set")
		mc.sets(skinSetButton, add="skin_set")


				#### sort skin Set
				
		ZSSetButton = mc.sets(ZsSetsLoop, n="buttons_ZS_set")

		mc.sets(ZsSetsLoop, rm="ALL_ZS_set")
		mc.sets(ZSSetButton, add="ALL_ZS_set")

		setGrp = (animSetButton, skinSetButton, ZSSetButton)

		bTagLoop.extend(setGrp)


		##### Create Tag for all #####




		addTag(targets=(bTagLoop),tag='ButtonTag')



	#### if there is a button jnt execute def 
	
    BListLoop = mc.ls('*_button_*_orig')

    if len(BListLoop) >= 0:
        buttonPreSkin()
		




