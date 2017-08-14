# --- biped patchScripts launching sequence

#postBe
from marsAutoRig_stubby.patch.attrPanel import attributeManipulators as postBeAttrPanel
reload(postBeAttrPanel)
postBeAttrPanel.patch()