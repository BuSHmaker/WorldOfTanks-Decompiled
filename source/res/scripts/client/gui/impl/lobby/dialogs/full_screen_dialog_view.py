# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/full_screen_dialog_view.py
import logging
from abc import abstractproperty
from PlayerEvents import g_playerEvents
from async import AsyncScope, AsyncEvent, await, async, BrokenPromiseError, AsyncReturn
from frameworks.wulf import WindowSettings, Window
from gui.Scaleform.genConsts.APP_CONTAINERS_NAMES import APP_CONTAINERS_NAMES
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.dialog_window import DialogResult, DialogButtons, DialogLayer
from gui.impl.wrappers.background_blur import WGUIBackgroundBlurSupportImpl
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class DIALOG_TYPES(object):
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    SIMPLE = 'simple'


class FullScreenDialogView(ViewImpl):
    __slots__ = ('__blur', '__scope', '__event', '__result', '_stats')
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, settings):
        super(FullScreenDialogView, self).__init__(settings)
        self.__blur = WGUIBackgroundBlurSupportImpl()
        self.__scope = AsyncScope()
        self.__event = AsyncEvent(scope=self.__scope)
        self.__result = DialogButtons.CANCEL
        self._stats = self._itemsCache.items.stats

    @abstractproperty
    def viewModel(self):
        pass

    def _getAdditionalData(self):
        return None

    @async
    def wait(self):
        try:
            yield await(self.__event.wait())
        except BrokenPromiseError:
            _logger.debug('%s has been destroyed without user decision', self)

        raise AsyncReturn(DialogResult(self.__result, self._getAdditionalData()))

    def _initialize(self):
        super(FullScreenDialogView, self)._initialize()
        self._addListeners()

    def _onInventoryResync(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            self.__setStats(model)

    def _setBaseParams(self, model):
        self.__setStats(model)

    def _onLoading(self, *args, **kwargs):
        super(FullScreenDialogView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self._setBaseParams(model)

    def _onLoaded(self, *args, **kwargs):
        super(FullScreenDialogView, self)._onLoaded()
        self._blurBackGround()

    def _finalize(self):
        super(FullScreenDialogView, self)._finalize()
        self._removeListeners()
        self.__scope.destroy()
        if self.__blur:
            self.__blur.disable()

    def _addListeners(self):
        self.viewModel.onAcceptClicked += self._onAcceptClicked
        self.viewModel.onCancelClicked += self._onCancelClicked
        self._itemsCache.onSyncCompleted += self._onInventoryResync
        g_playerEvents.onAccountBecomeNonPlayer += self.destroyWindow

    def _removeListeners(self):
        self.viewModel.onAcceptClicked -= self._onAcceptClicked
        self.viewModel.onCancelClicked -= self._onCancelClicked
        self._itemsCache.onSyncCompleted -= self._onInventoryResync
        g_playerEvents.onAccountBecomeNonPlayer -= self.destroyWindow

    def _blurBackGround(self):
        if self.__blur:
            blurLayers = [APP_CONTAINERS_NAMES.VIEWS,
             APP_CONTAINERS_NAMES.SUBVIEW,
             APP_CONTAINERS_NAMES.BROWSER,
             APP_CONTAINERS_NAMES.WINDOWS,
             APP_CONTAINERS_NAMES.MARKER]
            self.__blur.enable(APP_CONTAINERS_NAMES.WINDOWS, blurLayers)

    def _onAcceptClicked(self):
        self.__result = DialogButtons.SUBMIT
        self.__event.set()

    def _onCancelClicked(self):
        self.__result = DialogButtons.CANCEL
        self.__event.set()

    def __setStats(self, model):
        model.setCredits(int(self._stats.money.getSignValue(Currency.CREDITS)))
        model.setGolds(int(self._stats.money.getSignValue(Currency.GOLD)))
        model.setCrystals(int(self._stats.money.getSignValue(Currency.CRYSTAL)))
        model.setFreexp(self._stats.freeXP)


class FullScreenDialogWindowWrapper(Window):
    __slots__ = ('__wrappedView',)

    def __init__(self, wrappedView, parent=None):
        self.__wrappedView = wrappedView
        settings = WindowSettings()
        settings.flags = DialogLayer.TOP_WINDOW
        settings.content = wrappedView
        if parent is not None:
            settings.parent = parent
        super(FullScreenDialogWindowWrapper, self).__init__(settings)
        return

    def wait(self):
        return self.__wrappedView.wait()
