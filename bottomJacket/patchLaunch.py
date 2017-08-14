# --- BottomJacket patchScripts launching sequence

#postBe
from marsAutoRig_stubby.patch.bottomJacket import postBe_bottomJacket_patchScript as postBeBottomJacketPatch
reload(postBeBottomJacketPatch)
postBeBottomJacketPatch.patch()
