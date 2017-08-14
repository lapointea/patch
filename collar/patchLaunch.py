# --- collar patchScripts launching sequence

#postBe
from marsAutoRig_stubby.patch.collar import postBe_collar_patchScript as postBecollarPatch
reload(postBecollarPatch)
postBecollarPatch.patch()
