# Py3ConfigInjection
To use, import <code>setInjectorConfig</code> from <code>config_injection</code> and give it an opened config file.

Then, <code>@inject_config('\<SECTION\>')</code> on methods to inject into <code>**kwargs</code> any variables found.
Config will only be injected when kwargs haven't been set in the base method call, else will override the default variables in the method declaration.
Uses the variable's name to identify the variable to load from config.

```ini
# filename: config.ini
[FUNC]
world = True
```
```python
config = ConfigParser()
config.read('config.ini')

# Set config
setInjectorConfig(config)

#Annotated with section.
@inject_config('FUNC')
def func(hello, world=False):
    if world:
        print(hello)
    else:
        print("No hello for you")

func("shoop de woop")                   # Will print "shoop de woop"
func("shoop de woop", world=False)      # Will pring "No hello for you"
```
Will attempt casting on variables found, defaulting to <code>str</code> if all options fail. has a custom bool parser to deal with <code>'false'</code> and <code>'no'</code> as <code>False</code> values.


For classes, <code>@inject_statics_from_config('\<SECTION\>')</code>.
Similar to <code>@inject_config('\<SECTION\>')</code>, it will inject into the static variables.

```ini
# filename: config.ini
[TEST]
DEFAULT_TMP = "world"
```
```python
config = ConfigParser()
config.read('config.ini')

# Set config
setInjectorConfig(config)

#Annotated with section.
@inject_statics_from_config('TEST')
    class Test(ParentTest):
        DEFAULT_TMP = "Nope"
        def __init__(self, tmp):
            self.tmp = tmp
        def __str__(self):
            return str(self.tmp) + " " + str(Test.DEFAULT_TMP)

a = Test("hello")
print(a)        # Will print "hello world"
```

If you need injection into the actual instances, the easiest method is to <code>@inject_config</code> on the <code>\_\_init\_\_</code> method of the class, and then define the <coded>**kwargs</code> there.
