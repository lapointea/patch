# --- sleeves patchScripts launching sequence

#preBe
from marsAutoRig_stubby.patch.noRollSleeves import sleevesPrebehaveIfCondition as preBeSleevesPatch
reload(preBeSleevesPatch)
preBeSleevesPatch.patch()
#postBe
from marsAutoRig_stubby.patch.noRollSleeves import postBehavLightWeight as postBeSleevesPatch
reload(postBeSleevesPatch)
postBeSleevesPatch.patch()