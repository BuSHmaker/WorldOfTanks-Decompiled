# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/common.py
import logging
import BigWorld
from constants import EMPTY_GEOMETRY_ID
from skeletons.gui.shared import IItemsCache
from gui import SystemMessages
from gui.impl.gen import R
from gui.impl import backport
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.SystemMessages import SM_TYPE, CURRENCY_TO_SM_TYPE
from gui.shared.formatters import formatPrice, formatGoldPrice, text_styles, icons
from gui.shared.gui_items.processors import Processor, makeError, makeSuccess, makeI18nError, makeI18nSuccess, plugins
from gui.shared.money import Money, Currency
from helpers import dependency
from skeletons.gui.game_control import IVehicleComparisonBasket
from gui.Scaleform.Waiting import Waiting
_logger = logging.getLogger(__name__)

class TankmanBerthsBuyer(Processor):

    def __init__(self, berthsPrice, berthsCount):
        super(TankmanBerthsBuyer, self).__init__((plugins.MessageInformator('barracksExpandNotEnoughMoney', activeHandler=lambda : not plugins.MoneyValidator(berthsPrice).validate().success), plugins.MessageConfirmator('barracksExpand', ctx={'price': text_styles.concatStylesWithSpace(text_styles.gold(str(berthsPrice.gold)), icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_2)),
          'count': text_styles.stats(berthsCount)}), plugins.MoneyValidator(berthsPrice)))
        self.berthsPrice = berthsPrice

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='buy_tankmen_berths/{}'.format(errStr), defaultSysMsgKey='buy_tankmen_berths/server_error')

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='buy_tankmen_berths/success', money=formatPrice(self.berthsPrice), type=SM_TYPE.PurchaseForGold)

    def _request(self, callback):
        _logger.debug('Make server request to buy tankman berths')
        BigWorld.player().stats.buyBerths(lambda code: self._response(code, callback))


class PremiumAccountBuyer(Processor):

    def __init__(self, period, price, arenaUniqueID=0, withoutBenefits=False, requireConfirm=True):
        self.wasPremium = self.itemsCache.items.stats.isPremium
        plugList = [plugins.MoneyValidator(Money(gold=price))]
        if requireConfirm:
            plugList.insert(0, self.__getConfirmator(withoutBenefits, period, price))
        super(PremiumAccountBuyer, self).__init__(plugList)
        self.premiumPrice = price
        self.period = period
        self.arenaUniqueID = arenaUniqueID

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='premium/{}'.format(errStr), defaultSysMsgKey='premium/server_error', auxData={'errStr': errStr}, period=self.period)

    def _successHandler(self, code, ctx=None):
        localKey = 'premium/continueSuccess' if self.wasPremium else 'premium/buyingSuccess'
        return makeI18nSuccess(sysMsgKey=localKey, period=self.period, money=formatGoldPrice(self.premiumPrice), type=SM_TYPE.PurchaseForGold)

    def _request(self, callback):
        _logger.debug('Make server request to buy premium account, %s, %s', self.period, self.premiumPrice)
        BigWorld.player().stats.upgradeToPremium(self.period, self.arenaUniqueID, lambda code, errStr: self._response(code, callback, errStr=errStr))

    def __getConfirmator(self, withoutBenefits, period, price):
        if withoutBenefits:
            return plugins.HtmlMessageConfirmator('buyPremWithoutBenefitsConfirmation', 'html_templates:lobby/dialogs', 'confirmBuyPremWithoutBenefeits', {'days': text_styles.stats(period),
             Currency.GOLD: text_styles.concatStylesWithSpace(text_styles.gold(backport.getGoldFormat(price)), icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_2))})
        localKey = 'premiumContinueConfirmation' if self.wasPremium else 'premiumBuyConfirmation'
        return plugins.MessageConfirmator(localKey, ctx={'days': text_styles.stats(period),
         Currency.GOLD: text_styles.concatStylesWithSpace(text_styles.gold(backport.getGoldFormat(price)), icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_2))})


class GoldToCreditsExchanger(Processor):

    def __init__(self, gold):
        self.gold = gold
        self.credits = int(gold) * self.itemsCache.items.shop.exchangeRate
        super(GoldToCreditsExchanger, self).__init__(plugins=(plugins.HtmlMessageConfirmator('exchangeGoldConfirmation', 'html_templates:lobby/dialogs', 'confirmExchange', {'primaryCurrencyAmount': backport.getGoldFormat(self.gold),
          'resultCurrencyAmount': backport.getIntegralFormat(self.credits)}), plugins.MoneyValidator(Money(gold=self.gold))))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='exchange/{}'.format(errStr), defaultSysMsgKey='exchange/server_error', gold=self.gold)

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='exchange/success', gold=backport.getGoldFormat(self.gold), credits=formatPrice(Money(credits=self.credits)), type=SM_TYPE.FinancialTransactionWithGold)

    def _request(self, callback):
        _logger.debug('Make server request to exchange gold to credits')
        BigWorld.player().stats.exchange(self.gold, lambda code: self._response(code, callback))


class FreeXPExchanger(Processor):

    def __init__(self, xp, vehiclesCD, freeConversion=False):
        rate = self.itemsCache.items.shop.freeXPConversion
        self.xp = xp
        self.__freeConversion = bool(freeConversion)
        self.gold = round(rate[1] * xp / rate[0]) if not freeConversion else 0
        self.vehiclesCD = vehiclesCD
        super(FreeXPExchanger, self).__init__(plugins=(self.__makeConfirmator(), plugins.MoneyValidator(Money(gold=self.gold)), plugins.EliteVehiclesValidator(self.vehiclesCD)))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='exchangeXP/{}'.format(errStr), defaultSysMsgKey='exchangeXP/server_error', xp=backport.getIntegralFormat(self.xp))

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='exchangeXP/success', gold=backport.getGoldFormat(self.gold), xp=backport.getIntegralFormat(self.xp), type=SM_TYPE.FinancialTransactionWithGold)

    def _request(self, callback):
        _logger.debug('Make server request to exchange xp for credits')
        BigWorld.player().stats.convertToFreeXP(self.vehiclesCD, self.xp, lambda code: self._response(code, callback), int(self.__freeConversion))

    def __makeConfirmator(self):
        xpLimit = self.itemsCache.items.shop.freeXPConversionLimit
        extra = {'resultCurrencyAmount': backport.getIntegralFormat(self.xp),
         'primaryCurrencyAmount': backport.getGoldFormat(self.gold)}
        if self.__freeConversion:
            sourceKey = 'XP_EXCHANGE_FOR_FREE'
            extra['freeXPLimit'] = backport.getIntegralFormat(xpLimit)
        else:
            sourceKey = 'XP_EXCHANGE_FOR_GOLD'
        return plugins.HtmlMessageConfirmator('exchangeXPConfirmation', 'html_templates:lobby/dialogs', 'confirmExchangeXP', extra, sourceKey=sourceKey)


class BattleResultsGetter(Processor):

    def __init__(self, arenaUniqueID):
        super(BattleResultsGetter, self).__init__()
        self.__arenaUniqueID = arenaUniqueID

    def _errorHandler(self, code, errStr='', ctx=None):
        _logger.warning('Error on server request to get battle results: %s, %s, %s, %s', self.__arenaUniqueID, code, errStr, ctx)
        return makeError()

    def _successHandler(self, code, ctx=None):
        return makeSuccess(auxData=ctx)

    def _request(self, callback):
        _logger.debug('Make server request to get battle results')
        BigWorld.player().battleResultsCache.get(self.__arenaUniqueID, lambda code, battleResults: self._response(code, callback, ctx=battleResults))


class OutfitApplier(Processor):

    def __init__(self, vehicle, outfit, season):
        super(OutfitApplier, self).__init__()
        self.vehicle = vehicle
        self.outfit = outfit
        self.season = season

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('customization/{}'.format(errStr or 'server_error'))

    def _request(self, callback):
        _logger.debug('Make server request to put on outfit on vehicle %s, season %s', self.vehicle.invID, self.season)
        BigWorld.player().shop.buyAndEquipOutfit(self.vehicle.invID, self.season, self.outfit.pack().makeCompDescr(), lambda code: self._response(code, callback))


class StyleApplier(Processor):

    def __init__(self, vehicle, style=None):
        super(StyleApplier, self).__init__()
        self.vehicle = vehicle
        self.style = style

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('customization/{}'.format(errStr or 'server_error'))

    def _request(self, callback):
        _logger.debug('Make server request to put on style on vehicle %s', self.vehicle.invID)
        BigWorld.player().shop.buyAndEquipStyle(self.vehicle.invID, self.style.id if self.style else 0, lambda code: self._response(code, callback))


class CustomizationsBuyer(Processor):

    def __init__(self, vehicle, item, count):
        super(CustomizationsBuyer, self).__init__()
        self.vehicle = vehicle
        self.item = item
        self.count = count

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('customization/{}'.format(errStr or 'server_error'))

    def _request(self, callback):
        invID = self.vehicle.invID if self.vehicle else 0
        _logger.debug('Make server request to buy customizations on vehicle %s: %s count %s', invID, self.item, self.count)
        BigWorld.player().shop.buyCustomizations(invID, {self.item.intCD: self.count}, lambda code: self._response(code, callback))

    def _getTotalPrice(self):
        buyPrice = self.item.buyPrices.itemPrice.price
        if not buyPrice:
            _logger.error('Incorrect attempt to buy item %s', self.item)
        return buyPrice * self.count

    def _getMsgCtx(self):
        return {'itemType': self.item.userType,
         'itemName': self.item.userName,
         'count': backport.getIntegralFormat(int(self.count)),
         'money': formatPrice(self._getTotalPrice())}

    def _successHandler(self, code, ctx=None):
        currency = self.item.buyPrices.itemPrice.price.getCurrency(byWeight=True)
        messageType = MESSENGER.SERVICECHANNELMESSAGES_SYSMSG_CUSTOMIZATIONS_BUY
        sysMsgType = CURRENCY_TO_SM_TYPE.get(currency, SM_TYPE.PurchaseForGold)
        SystemMessages.pushI18nMessage(messageType, type=sysMsgType, **self._getMsgCtx())
        return makeSuccess(auxData=ctx)


class CustomizationsSeller(Processor):

    def __init__(self, vehicle, item, count=1):
        super(CustomizationsSeller, self).__init__()
        self.vehicle = vehicle
        self.item = item
        self.count = count

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('customization/{}'.format(errStr or 'server_error'))

    def _getTotalPrice(self):
        sellPrice = self.item.sellPrices.itemPrice.price
        if not sellPrice:
            _logger.error('Attempt to sell item %s that is not sold.', self.item)
        return sellPrice * self.count

    def _getMsgCtx(self):
        return {'itemType': self.item.userType,
         'itemName': self.item.userName,
         'count': backport.getIntegralFormat(int(self.count)),
         'money': formatPrice(self._getTotalPrice())}

    def _successHandler(self, code, ctx=None):
        messageType = MESSENGER.SERVICECHANNELMESSAGES_SYSMSG_CUSTOMIZATIONS_SELL
        SystemMessages.pushI18nMessage(messageType, type=SM_TYPE.Selling, **self._getMsgCtx())
        return makeSuccess(auxData=ctx)

    def _request(self, callback):
        invID = self.vehicle.invID if self.vehicle else 0
        _logger.debug('Make server request to sell customizations on vehicle %s, item %s, count %s', invID, self.item, self.count)
        BigWorld.player().shop.sellCustomizations(invID, self.item.intCD, self.count, lambda code: self._response(code, callback))


class BadgesSelector(Processor):

    def __init__(self, badges=None):
        if badges is None:
            plugs = ()
            badges = ()
        else:
            plugs = (plugins.BadgesValidator(badges),)
        super(BadgesSelector, self).__init__(plugs)
        self.__badges = badges
        return

    def _getMessagePrefix(self):
        pass

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='{}/server_error/{}'.format(self._getMessagePrefix(), errStr), defaultSysMsgKey='{}/server_error'.format(self._getMessagePrefix()))

    def _request(self, callback):
        _logger.debug('Make server request to select badges %s', self.__badges)
        BigWorld.player().badges.selectBadges(self.__badges, lambda resID, code, errStr: self._response(code, callback, errStr))


class EpicPrestigeTrigger(Processor):

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('epicBattles/prestigeTrigger/error')

    def _request(self, callback):
        _logger.debug('Make server request to trigger prestige')
        BigWorld.player().epicMetaGame.triggerEpicMetaGamePrestige(lambda code, errStr: self._response(code, callback, errStr=errStr))


class EpicPrestigePointsExchange(Processor):

    def _request(self, callback):
        _logger.debug('Make server request to exchange prestige points')
        BigWorld.player().epicMetaGame.exchangePrestigePoints(lambda code, errStr: self._response(code, callback, errStr=errStr))


class BobRewardClaimer(Processor):

    def __init__(self, token):
        super(BobRewardClaimer, self).__init__()
        self.__token = token

    def _errorHandler(self, code, errStr='', ctx=None):
        Waiting.hide('bob/claimReward')
        return super(BobRewardClaimer, self)._errorHandler(code, errStr, ctx)

    def _request(self, callback):
        _logger.debug('Make server request to claim BoB2 reward')
        BigWorld.player().bob.claimReward(self.__token, lambda code, errStr: self._response(code, callback, errStr=errStr))


class EpicRewardsClaimer(Processor):

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('epicBattles/claimReward/error')

    def _request(self, callback):
        _logger.debug('Make server request to claim final reward')
        BigWorld.player().epicMetaGame.claimEpicMetaGameMaxPrestigeReward(lambda code, errStr: self._response(code, callback, errStr=errStr))


class ConvertBlueprintFragmentProcessor(Processor):

    def __init__(self, vehicleCD, count, fragmentPosition):
        super(ConvertBlueprintFragmentProcessor, self).__init__()
        self.__vehicleCD = vehicleCD
        self.__position = fragmentPosition
        self.__count = count

    def _request(self, callback):
        BigWorld.player().blueprints.convertBlueprintFragment(self.__vehicleCD, self.__position, self.__count, lambda code: self._response(code, callback))


class _MapsBlackListSelector(Processor):

    def __init__(self, selectedMaps=None):
        super(_MapsBlackListSelector, self).__init__()
        if selectedMaps is None:
            selectedMaps = ()
        self.__selectedMaps = selectedMaps
        return

    def _getMessagePrefix(self):
        pass

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='{}/server_error/{}'.format(self._getMessagePrefix(), errStr), defaultSysMsgKey='{}/server_error'.format(self._getMessagePrefix()))

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='{}/success'.format(self._getMessagePrefix()))

    def _request(self, callback):
        _logger.debug('Make server request to select black maps %r', self.__selectedMaps)
        BigWorld.player().stats.setMapsBlackList(self.__selectedMaps, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))

    def _getLayout(self):
        return [ mapID for mapID, _ in self.itemsCache.items.stats.getMapsBlackList() ]


class MapsBlackListSetter(_MapsBlackListSelector):

    def __init__(self, selectedMapID):
        layout = self._getLayout()
        wasInserted = False
        for idx, mapID in enumerate(layout):
            if mapID == EMPTY_GEOMETRY_ID:
                layout[idx] = selectedMapID
                wasInserted = True
                break

        if not wasInserted:
            layout.append(selectedMapID)
        super(MapsBlackListSetter, self).__init__(layout)


class MapsBlackListRemover(_MapsBlackListSelector):

    def __init__(self, removeMapID):
        layout = self._getLayout()
        if removeMapID in layout:
            layout[layout.index(removeMapID)] = EMPTY_GEOMETRY_ID
        else:
            _logger.error('Cannot remove mapID %d from layout %r', removeMapID, layout)
        super(MapsBlackListRemover, self).__init__(layout)


class MapsBlackListChanger(_MapsBlackListSelector):

    def __init__(self, srcMapID, destMapID):
        layout = self._getLayout()
        if srcMapID in layout:
            layout[layout.index(srcMapID)] = destMapID
        else:
            _logger.error('Cannot change srcMapID %d from layout %r', srcMapID, layout)
        super(MapsBlackListChanger, self).__init__(layout)


class PremiumBonusApplier(Processor):

    def __init__(self, arenaUniqueID=None, vehTypeCompDescr=None):
        super(PremiumBonusApplier, self).__init__()
        self.__arenaUniqueID = arenaUniqueID
        self.__vehTypeCompDescr = vehTypeCompDescr

    def _getMessagePrefix(self):
        pass

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='{}/server_error/{}'.format(self._getMessagePrefix(), errStr), defaultSysMsgKey='{}/server_error'.format(self._getMessagePrefix()))

    def _request(self, callback):
        _logger.debug('Make server request to apply premium XP bonus %d', self.__arenaUniqueID)
        BigWorld.player().shop.applyPremiumXPBonus(self.__arenaUniqueID, self.__vehTypeCompDescr, lambda resID, code, errStr: self._response(code, callback, errStr))


class UseCrewBookProcessor(Processor):

    def __init__(self, crewBookCD, vehInvID, tmanInvID):
        super(UseCrewBookProcessor, self).__init__()
        self.__crewBookCD = crewBookCD
        self.__vehInvID = vehInvID
        self.__tmanInvID = tmanInvID

    def _successHandler(self, code, ctx=None):
        itemsCache = dependency.instance(IItemsCache)
        return makeI18nSuccess(sysMsgKey='crewBooksNotification/bookUsed', name=itemsCache.items.getItemByCD(self.__crewBookCD).userName)

    def _request(self, callback):
        BigWorld.player().inventory.useCrewBook(self.__crewBookCD, self.__vehInvID, self.__tmanInvID, lambda code: self._response(code, callback))


class VehicleChangeNation(Processor):
    _comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    def __init__(self, cvh, nvh):
        super(VehicleChangeNation, self).__init__()
        self._cvh = cvh
        self._nvh = nvh

    def _request(self, callback):
        BigWorld.player().inventory.switchNation(self._cvh.name, self._nvh.name, lambda code: self._response(code, callback))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey=backport.text(R.strings.system_messages.nation_change.dyn(errStr)()), defaultSysMsgKey=backport.text(R.strings.system_messages.nation_change.error()))

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey=backport.text(R.strings.system_messages.nation_change.success()), veh_name=self._cvh.userName)
