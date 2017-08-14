# --- buttons patchScripts launching sequence

#postBe
from marsAutoRig_stubby.patch.buttons import postBe_buttons_patchScript as postBebuttonsPatch
reload(postBebuttonsPatch)
postBebuttonsPatch.patch()
