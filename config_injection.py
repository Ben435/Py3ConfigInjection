import logging
from configparser import ConfigParser
from typing import Callable, Iterable


global_config = ConfigParser()
debug = False

logger = logging.getLogger(__name__)
injector_config_section = 'INJECTOR'


def setInjectorConfig(config: ConfigParser):
    """
    Set config parser for injector.
    :param config: Config to pull from. Must be pre-loaded.
    :return: None
    """
    global global_config, debug
    global_config = config
    debug = config.get(injector_config_section, 'debug', fallback=False)
    if isinstance(debug, str):
        try:
            debug = to_bool(debug)
        except ValueError:
            debug = False
    if debug:
        level = logging.INFO
        try:
            level = config.getint(injector_config_section, 'level', fallback=None)
        except ValueError:
            level = config.get(injector_config_section, 'level', fallback='DEBUG')
        finally:
            logger.setLevel(level)


def to_bool(string: str) -> bool:
    if string.lower() in ['true', 't', 'y', 'yes']:
        return True
    elif string.lower() in ['false', 'f', 'n', 'no']:
        return False
    else:
        raise ValueError("Failed to recognise: '{}'.".format(string))


def _log(msg):
    if debug:
        logger.log(logger.getEffectiveLevel(), msg)


def get_and_cast(section: str, target: str, preferred=None):
    """
    Get 'target' from config 'section' and cast to 'preferred' or one of inside 'preferred' if iterable.
    By default, attempts: [float, int, bool], with a custom to_bool cast function.
    :param section: Section to find 'target' configuration.
    :param target: Target configuration name in 'section'.
    :param preferred: Class or list of classes it will attempt to cast too. Overrides defaults.
    :return: Either one of preferred, or one of [float, int, to_bool], or str if all casts failed.
    """

    if preferred:
        if isinstance(preferred, Iterable):
            allowed_types = preferred
        # Special case
        elif preferred == bool:
            allowed_types = [to_bool]
        else:
            allowed_types = [preferred]
    else:
        allowed_types = [float, int, to_bool]

    to_cast = global_config.get(section, target)
    if to_cast is None:
        return None
    for i in range(len(allowed_types)):
        cast = allowed_types[i]
        try:
            result = cast(to_cast)
            break
        except ValueError:
            pass
    else:
        return to_cast
    return result


def inject_config(section: str):
    """
    Decorator for config injection into kwargs of functions.
    Takes config, and injects all values in specified section into function before call.
    :param section: Section to pull values from.
    :return: Decorator to inject configs.
    """
    def decorator(func: Callable):
        def new_func(*args, **kwargs):
            if global_config and global_config.has_section(section):
                set_options = global_config.options(section)
                # Let direct options override config.
                for option in filter(lambda x: x not in kwargs, set_options):
                    kwargs[option] = get_and_cast(section, option)
                    _log("Injected from section {} and option {}, val {} of type {}".format(section, option, str(kwargs[option]), type(kwargs[option])))

            else:
                logger.warning("No section found: {}".format(section))
            return func(*args, **kwargs)
        return new_func
    return decorator

