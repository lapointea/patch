# --- pocket patchScripts launching sequence

#preBe
from marsAutoRig_stubby.patch.pocket import preBe_pocket_patchScript as preBepocketPatch
reload(preBepocketPatch)
preBepocketPatch.patch()

#postBe
from marsAutoRig_stubby.patch.pocket import postBe_pocket_patchScript as postBepocketPatch
reload(postBepocketPatch)
postBepocketPatch.patch()

