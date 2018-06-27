from typing import Iterable
import logging
from config_injection import get_and_cast, global_config, _log

logger = logging.getLogger(__name__)


def inject_statics_from_config(section: str):
    """
    Inject config options into static variables of class.
    If you want injection into actual instance variables, use inject_config on __init__ instead.
    :param section: Section for variables.
    :return: Decorator.
    """
    def decorator(OldClass: type):
        class MetaInjected(type):
            def __getattribute__(cls, item):
                config_var = global_config.get(section, item, fallback=None)
                if config_var is not None:
                    config_ops = global_config.options(section)
                else:
                    config_ops = []
                # Go through mro...
                x = None
                for classOp in OldClass.mro():
                    # Check if can override with config.
                    if config_var and classOp == OldClass and config_var and item in config_ops:
                        x = get_and_cast(section, item)
                    # Else keep iterating through mro
                    try:
                        x = classOp.__getattribute__(classOp, item)
                        break
                    except AttributeError as e:
                        pass
                if x is None:
                    raise AttributeError("'{}' object has no attribute '{}'".format(OldClass, item))
                _log("{}.__getattribute__({}) = {}".format(OldClass, item, x))
                try:
                    # Get function for given class.
                    a = x.__get__(cls)
                    return a
                except AttributeError as e:
                    return x
                except TypeError as e:
                    return x

        class InjectedClass(object, metaclass=MetaInjected):
            def __init__(self, *args, **kwargs):
                self.oInstance = OldClass(*args, **kwargs)

            def __instancecheck__(self, instance):
                #print("THERE LOOKING!!!")
                return type(instance) == OldClass

            def __getattribute__(self, item):
                try:
                    # If in the wrapper class, return that
                    x = super(InjectedClass, self).__getattribute__(item)
                except AttributeError:
                    pass
                else:
                    return x

                x = self.oInstance.__getattribute__(item)
                # If its a method...
                if isinstance(type(x), type(self.__init__)):
                    return x
                else:
                    # Its a variable. Attempt config injection.
                    # if config.get(section, x, fallback=False):
                    return x

            def __str__(self):
                return str(self.oInstance)

            def __eq__(self, o: object) -> bool:
                return self.oInstance == o

            def __ne__(self, o: object) -> bool:
                return self.oInstance != o

            def __repr__(self) -> str:
                return repr(self.oInstance)

            def __hash__(self) -> int:
                return hash(self.oInstance)

            def __format__(self, format_spec: str) -> str:
                return format(self.oInstance, format_spec)

            def __sizeof__(self) -> int:
                return self.oInstance.__sizeof__()

            def __reduce__(self) -> tuple:
                return self.oInstance.__reduce__()

            def __reduce_ex__(self, protocol: int) -> tuple:
                return self.oInstance.__reduce_ex__(protocol)

            def __dir__(self) -> Iterable[str]:
                return self.oInstance.__dir__()

        return InjectedClass

    return decorator


if __name__ == "__main__":
    from time import sleep

    class ParentTest:
        PARENT_VAR = "Hello world!"


    @inject_statics_from_config('TEST')
    class Test(ParentTest):
        DEFAULT_TMP = "Nope"

        def __init__(self, tmp, def_tmp=DEFAULT_TMP):
            self.tmp = tmp
            self.def_tmp = def_tmp

        def a(self):
            print("Running a")
            sleep(1)
            print("Ending a")
            return self.tmp

        @staticmethod
        def static_default_tmp():
            return Test.DEFAULT_TMP

        @classmethod
        def default_tmp(cls):
            cls.DEFAULT_TMP = "Reset"

        @staticmethod
        def static_set_tmp(new_tmp):
            Test.DEFAULT_TMP = new_tmp
            return Test.DEFAULT_TMP

        @classmethod
        def default_set_tmp(cls, new_tmp):
            Test.DEFAULT_TMP = new_tmp
            return Test.DEFAULT_TMP

        @property
        def get_tmp(self):
            return self.tmp

        def __str__(self):
            return str(self.tmp) + str(self.def_tmp)

    a = Test("hello")
    a.a()
    print(Test.DEFAULT_TMP)
    # Run static methods.
    Test.static_default_tmp()
    Test.default_tmp()
    Test.default_set_tmp("Bub Bye")
    Test.static_set_tmp("Hello World!")
    print(Test.PARENT_VAR)
    print(a.get_tmp)
    b = Test("Bye")
    print(a, b)
    print(repr(a), repr(b), Test.DEFAULT_TMP, a.tmp, b.tmp)
