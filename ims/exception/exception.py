import abc


# The base class for all BMI Exceptions
# Made abstract since it is recommended to raise the specific subclass
class BMIException(Exception):
    __metaclass__ = abc.ABCMeta
