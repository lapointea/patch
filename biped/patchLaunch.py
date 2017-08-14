# --- biped patchScripts launching sequence

#preBe
from marsAutoRig_stubby.patch.biped import preBe_biped_patchScript as preBeBipPatch
reload(preBeBipPatch)
preBeBipPatch.patch()
#postBe
from marsAutoRig_stubby.patch.biped import postBe_biped_patchScript as postBeBipPatch
reload(postBeBipPatch)
postBeBipPatch.patch()

