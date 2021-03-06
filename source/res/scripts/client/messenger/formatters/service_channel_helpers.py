# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/formatters/service_channel_helpers.py
import typing
import logging
from collections import namedtuple
from items import makeIntCompactDescrByID
from optional_bonuses import BONUS_MERGERS
from skeletons.gui.shared import IItemsCache
from items.components.c11n_constants import CustomizationNamesToTypes
from helpers import dependency
from messenger import g_settings
_logger = logging.getLogger(__name__)
EOL = '\n'
DEFAULT_MESSAGE = 'defaultMessage'
if typing.TYPE_CHECKING:
    from messenger.proto.bw.wrappers import ServiceChannelMessage
MessageData = namedtuple('MessageData', 'data, settings')

def getRewardsForQuests(message, questIDs):
    data = message.data or {}
    detailRewards = data.get('detailedRewards', {})
    resultRewards = {}
    for questID, rewards in detailRewards.items():
        if questID in questIDs:
            _mergeRewards(resultRewards, rewards)

    return resultRewards


def _mergeRewards(resultRewards, rewards):
    for bonusName, bonusValue in rewards.items():
        if bonusName in BONUS_MERGERS:
            BONUS_MERGERS[bonusName](resultRewards, bonusName, bonusValue, False, 1, None)
        _logger.warning('BONUS_MERGERS has not bonus %s', bonusName)

    return


def getCustomizationItemData(itemId, customizationName):
    itemsCache = dependency.instance(IItemsCache)
    customizationType = CustomizationNamesToTypes.get(customizationName.upper())
    if customizationType is None:
        _logger.warning('Wrong customization name: %s', customizationName)
    compactDescr = makeIntCompactDescrByID('customizationItem', customizationType, itemId)
    item = itemsCache.items.getItemByCD(compactDescr)
    itemName = item.userName
    itemTypeName = item.itemFullTypeName
    return _CustomizationItemData(itemTypeName, itemName)


_CustomizationItemData = namedtuple('_CustomizationItemData', ('guiItemType', 'userName'))

def getDefaultMessage(normal='', bold=''):
    return g_settings.msgTemplates.format(DEFAULT_MESSAGE, {'normal': normal,
     'bold': bold})
