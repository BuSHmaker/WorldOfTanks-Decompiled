# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/block.py
from typing import List, Any

class ASPECT(object):
    SERVER = 'SERVER'
    CLIENT = 'CLIENT'


class SLOT_TYPE(object):
    BOOL = 'Bool'
    STR = 'String'
    INT = 'Int'
    FLOAT = 'Float'
    VECTOR2 = 'Vector2'
    VECTOR3 = 'Vector3'
    VECTOR4 = 'Vector4'
    MATRIX4 = 'Matrix4'
    ANGLE = 'Angle'
    INT_ARRAY = 'IntArray'
    FLOAT_ARRAY = 'FloatArray'
    STR_ARRAY = 'StringArray'
    BOOL_ARRAY = 'BoolArray'
    VECTOR2_ARRAY = 'Vector2Array'
    VECTOR3_ARRAY = 'Vector3Array'
    VECTOR4_ARRAY = 'Vector4Array'
    MATRIX4_ARRAY = 'Matrix4Array'
    ANGLE_ARRAY = 'AngleArray'


class EDITOR_TYPE(object):
    STR_KEY_SELECTOR = 1


def buildStrKeysValue(*args):
    return ';'.join(args)


class InitParam(object):

    def __init__(self, name, slotType, defaultValue, editorType=None):
        self.name = name
        self.slotType = slotType
        self.defaultValue = defaultValue
        self.editorType = editorType


class DataInputSlot(object):

    @staticmethod
    def getValue():
        pass


class DataOutputSlot(object):

    @staticmethod
    def setValue(value):
        pass


class EventInputSlot(object):
    pass


class EventOutputSlot(object):

    @staticmethod
    def call():
        pass


class Meta(object):

    @classmethod
    def blockName(cls):
        return cls.__name__

    @classmethod
    def blockModule(cls):
        return cls.__module__

    @classmethod
    def blockAspects(cls):
        return [ASPECT.SERVER, ASPECT.CLIENT]

    @classmethod
    def blockIcon(cls):
        pass

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def initParams(cls):
        return []


class Block(Meta):

    def __init__(self, agent):
        self.__agent = agent
        self._onFinishScriptCallRequired = False

    def _getInitParams(self):
        return self.__agent.getInitParams()

    def _makeDataInputSlot(self, name, slotType, editorType=-1):
        return self.__agent.makeDataInputSlot(name, slotType, editorType)

    def _makeDataOutputSlot(self, name, slotType, fun):
        return self.__agent.makeDataOutputSlot(name, slotType, fun)

    def _makeEventInputSlot(self, name, fun):
        return self.__agent.makeEventInputSlot(name, fun)

    def _makeEventOutputSlot(self, name):
        return self.__agent.makeEventOutputSlot(name)

    def _writeLog(self, msg):
        self.__agent.writeLog(msg)

    def captionText(self):
        pass

    def onFinishScript(self):
        pass
