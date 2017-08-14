# --- quadruped patchScripts launching sequence

#preBe
from marsAutoRig_stubby.patch.quadruped import preBe_quad_patchScript as preBeQuadPatch
reload(preBeQuadPatch)
preBeQuadPatch.patch()
#postBe
from marsAutoRig_stubby.patch.quadruped import postBe_quad_patchScript as postBeQuadPatch
reload(postBeQuadPatch)
postBeQuadPatch.patch()