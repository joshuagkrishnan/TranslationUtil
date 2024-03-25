from abc import ABCMeta, abstractmethod, abstractproperty, abstractstaticmethod

class Serializer(metaclass=ABCMeta):
    @abstractmethod
    def serialize(self):
        pass

    @abstractmethod
    def deserialize(self):
        pass

    @abstractmethod
    def content_dump(self):
        pass

    @abstractstaticmethod
    def remove_pirate_holder(m):
        pass

    @abstractproperty
    def content(self):
        pass
