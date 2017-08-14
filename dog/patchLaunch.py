# --- quadruped patchScripts launching sequence

#preBe
from marsAutoRig_stubby.patch.dog import preBe_dog_PROD_patchScript as preBeDogPatch
reload(preBeDogPatch)
preBeDogPatch.patch()
#postBe
from marsAutoRig_stubby.patch.dog import postBe_dog_PROD_patchScript as postBeDogPatch
reload(postBeDogPatch)
postBeDogPatch.patch()

'''
#volumeSpine
from marsAutoRig_stubby.patch.dog import quad_volumeSpine_generate as volumeSpine
reload(volumeSpine)
volumeSpine.makeSpine()
'''



