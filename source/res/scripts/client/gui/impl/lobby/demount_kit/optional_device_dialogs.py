# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/demount_kit/optional_device_dialogs.py
from frameworks.wulf import ViewSettings, ViewFlags
from gui.goodies.goodie_items import DemountKit
from gui.impl.gen.view_models.views.lobby.demount_kit.optional_device_dialog_model import OptionalDeviceDialogModel
from gui.impl.gen import R
from gui.impl.lobby.demount_kit.item_price_dialog import ItemPriceDialog
from gui.impl.lobby.dialogs.full_screen_dialog_view import DIALOG_TYPES
from gui.shared import events
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.money import MONEY_UNDEFINED
from helpers import dependency
from skeletons.gui.goodies import IGoodiesCache

class OpDevBaseDialog(ItemPriceDialog):

    def __init__(self, typeCompDescr):
        settings = ViewSettings(layoutID=R.views.lobby.demountkit.CommonWindow(), flags=ViewFlags.TOP_WINDOW_VIEW, model=OptionalDeviceDialogModel())
        super(OpDevBaseDialog, self).__init__(settings, typeCompDescr)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _setBaseParams(self, model):
        super(OpDevBaseDialog, self)._setBaseParams(model)
        self._setTitleArgs(model.getTitleArgs(), (('equipment', R.strings.artefacts.dyn(self._item.name).name()),))
        if model.getDialogType() == DIALOG_TYPES.SIMPLE:
            model.setSpecialType(self._item.getOverlayType())
            model.setImage(R.images.gui.maps.shop.artefacts.c_180x135.dyn(self._item.descriptor.iconName)())
        model.setCancelButtonText(R.strings.dialogs.confirmBuyAndInstall.cancel())


class DestroyOpDevDialog(OpDevBaseDialog):

    @property
    def _price(self):
        return ItemPrice(MONEY_UNDEFINED, MONEY_UNDEFINED)

    def _setBaseParams(self, model):
        model.setDialogType(DIALOG_TYPES.WARNING)
        super(DestroyOpDevDialog, self)._setBaseParams(model)
        model.setTitleBody(R.strings.dialogs.equipmentDestroy.conformation())
        model.setAcceptButtonText(R.strings.dialogs.removeConfirmationNotRemovable.submit())

    def getEventType(self):
        return events.ShowDialogEvent.SHOW_CONFIRM_ORDER_DIALOG


class DemountOpDevSinglePriceDialog(OpDevBaseDialog):
    _goodiesCache = dependency.descriptor(IGoodiesCache)

    def _onInventoryResync(self, *args, **kwargs):
        dk = self._goodiesCache.getDemountKit()
        if self.isPriceInGold() and dk.enabled:
            self._onCancelClicked()
            return
        super(DemountOpDevSinglePriceDialog, self)._onInventoryResync(args, kwargs)

    def _getAdditionalData(self):
        dk = self._goodiesCache.getDemountKit()
        return {'openDemountSelectorWindow': self.isPriceInGold() and dk.enabled}

    @property
    def _price(self):
        return self._item.getRemovalPrice(self._itemsCache.items)

    def _setBaseParams(self, model):
        super(DemountOpDevSinglePriceDialog, self)._setBaseParams(model)
        model.setTitleBody(R.strings.demount_kit.equipmentDemount.confirmation())
        model.setDescription(R.strings.demount_kit.equipmentDemount.confirmation.description())
        model.setPriceDescription(R.strings.demount_kit.equipmentDemountPrice())
        model.setAcceptButtonText(R.strings.demount_kit.demountConfirmation.submit())


class InstallOpDevDialog(OpDevBaseDialog):

    @property
    def _price(self):
        return ItemPrice(MONEY_UNDEFINED, MONEY_UNDEFINED)

    def _setBaseParams(self, model):
        super(InstallOpDevDialog, self)._setBaseParams(model)
        self._setDescription(model)
        model.setTitleBody(R.strings.dialogs.equipmentPurcase.conformation.all())
        model.setAcceptButtonText(R.strings.dialogs.confirmEquipmentInstall.submit())

    def _setDescription(self, model):
        if self._item.isRemovable:
            return
        if self._item.isDeluxe:
            description = R.strings.dialogs.equipmentDestroy.DemountOptions.bonds()
        else:
            description = R.strings.dialogs.equipmentDestroy.DemountOptions.goldOrDemoKit()
        model.setDescription(description)


class BuyAndInstallOpDevDialog(InstallOpDevDialog):

    @property
    def _price(self):
        return self._item.getBuyPrice(preferred=False)

    def _setBaseParams(self, model):
        super(BuyAndInstallOpDevDialog, self)._setBaseParams(model)
        model.setTitleBody(R.strings.dialogs.confirmEquipmentBuyInstall.submit())
        model.setPriceDescription(R.strings.dialogs.equipmentBuyInstall.price())
        model.setAcceptButtonText(R.strings.menu.contextMenu.buyAndEquip())


class BuyAndStorageOpDevDialog(OpDevBaseDialog):

    @property
    def _price(self):
        return self._item.getBuyPrice(preferred=False)

    def _setBaseParams(self, model):
        super(BuyAndStorageOpDevDialog, self)._setBaseParams(model)
        model.setTitleBody(R.strings.dialogs.buyConfirmation.stringEquipment.submit())
        model.setDescription(R.strings.dialogs.buyInstallConfirmation.notEnoughWeight())
        model.setPriceDescription(R.strings.dialogs.equipmentBuyInstall.price())
        model.setAcceptButtonText(R.strings.dialogs.buyConfirmation.submit())
