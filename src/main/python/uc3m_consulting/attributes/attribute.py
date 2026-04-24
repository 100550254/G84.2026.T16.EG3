from uc3m_consulting.exception.enterprise_management_exception import EnterpriseManagementException

class Attribute:
    def __init__(self, value):
        self._value = self._validate(value)

    @property
    def value(self):
        return self._value

    @value.setter
    def __set__(self, new_value):
        self._value = self._validate(new_value)

    def _validate(self, value):
        raise EnterpriseManagementException


