
# Serial Labware module for Python
This repository contains a general parent class for communication with any kind of laboratory equipment via serial interfaces (USB or RS232/RS485). It also contains a growing collection of ready-to-use child classes for a number of commonly used devices. All classes provided here have been extensively tested in various platforms and should be bug free, however, as always, _caveat emptor_. 

## Required modules
This project has been developed in Python 3.6, and the only non-standard package used is pyserial (version 3.3 or later).

## Installation and usage
To perform an installation, clone/download the source code into directory of choice (e.g. *source_dir*) and run:
<code>pip3 install <i>source_dir</i></code>
After that you can remove the *source_dir* with all the files downloaded.

## Development

To perform an installation for development, clone the source code into directory of choice (e.g. *source_dir*) and run:
<code>pip3 install -e <i>source_dir</i></code>

## How it works in a nutshell
Any device object spawns a separate thread upon instantiation which in turn opens a serial connection to the device. 
When a method is called or a property set or queried, the necessary command is sent to the command thread via a queue.
The command thread encodes the string according to the `self.standard_encoding` property and sends it down the serial line. If a reply is expected, the command thread receives and decodes the reply, checks it against a regular expression pattern (if supplied), and returns the digested reply back to the main thread through another queue. 

Additionally, the user can specify a `self.keepalive()` method. This is a method that is continuously called while there are no commands in the queue. Some devices (especially those of the heating variety) require some kind of recurring call from the PC in order to stay operational. **NOTA BENE**: in the keepalive, never use `time.sleep()`! That would block the entire operation and break the class. Always use a non-blocking wait similar to the infamous Arduino "Blink Without Delay" example:

```python
if time() >= (self.last_time + 2):
    self.last_time = time()
    return self.temperature_pv
else:
    return None
```

## The @command decorator
One feature that often confuses user is the `@command` decorator preceding all commands in the device classes. However, the purpose and behaviour of that cryptic line is quickly explained. In a nutshell, a decorator is just a shorthand notation for a wrapper function:

```python
@spam
def foo(bar):
    # do stuff
```

Means every time `foo(bar)` is called, you actually call `spam(foo(bar))`. `spam` "wraps" around `foo` in a sense that the entire `foo` function call including the argument given for `bar` is passed as an argument to `spam`. For a detailed explanation of how decorators work and how to write and use them I suggest reading through [this great guide to decorators](https://www.thecodeship.com/patterns/guide-to-python-function-decorators/).

Now what the `@command` decorator specifically does is check whether a method is called in the main thread or the command handler thread. If it finds the method is called in the command handler thread, it just executes the method with the supplied arguments. If, however, the method was called anywhere else, it packs both the method call and the supplied arguments into the command queue and ships it off to the command thread where it will be executed.

In practical terms this only means that any class method sending commands has to be preceded by an `@command` wrapper. In fact, as a simple user, you need not concern yourself with this wrapper at all, just use the provided methods as shown in the [examples](/SerialLabware/example). If you want to make a new class for another piece of equipment, type `@command` in the line above every method definition, as exemplified in the classes that already exist. No magic involved!

## The @property decorator
Python comes with a few inbuilt decorators. One of them is `@property`. A property is (broadly speaking) a value associated with an object. A property can be set, and it can be read and used ("get"). In our case this is terribly useful for things like setpoints, which in most devices can, you guessed it, be get (well, gotten) and set.

Have a look at the following example from [IKA_RET_Control_Visc.py](/SerialLabware/IKA_RET_Stirrer/IKA_RET_Control_Visc.py):

```python
@property
@command
def stir_rate_sp(self):
    """
    Reads the set point (target) for the stir rate
    :return: call back to send_message with a request to return and check a value
    """
    return self.send_message(self.GET_STIR_RATE_SP, True, self.valueanswer)

@stir_rate_sp.setter
@command
def stir_rate_sp(self, stir_rate=None):
    """
    Sets the stirrer rate and return the set point from the hot plate so the user can verify that it was successful
    :param stir_rate: (integer) the target stir rate of the hot plate
    :return: call back to get_stirrer_rate_set_point()
    """
    try:
        # type checking of the stir rate that the user provided
        stir_rate = int(stir_rate)
    except ValueError:
        raise(ValueError("Error setting stir rate. Rate was not a valid integer \"{0}\"".format(stir_rate)))

    self.logger.debug("Setting stir rate to {0} RPM...".format(stir_rate))

    # actually sending the command
    self.send_message("{0} {1}".format(self.SET_STIR_RATE_SP, stir_rate))
```

We know the `@command` decorator just sorts out the technicalities of sending the message in the right thread, so we can ignore it for now. We further see two identically named methods `stir_rate_sp`, but one decorated with `@property`, and the other one with `@stir_rate_sp.setter`. You will also see that the `@property` one seems to read the stir rate setpoint, while the `@stir_rate_sp.setter` one seems to send the supplied stir rate to the hotplate. This is exactly how it works:

```python
stirrer.stir_rate_sp = 100  # this sets the stir rate to 100rpm and sends all the required magic
print(stirrer.stir_rate_sp)  # this asks the stirrer for the current setpoint and prints it
```

Some properties don't have a setter, like `stir_rate_pv` which queries the current actual stir rate. No point in setting that, but reading is useful.

## The Regular Expressions check patterns
You will notice some modules have gibberish-ish properties like this one here:

```python
self.valueanswer = re.compile("(\d+\.\d+) (\d)\r\n")
```

You will also notice those patterns being passed to `self.send_message()` for the `return_pattern` argument. Again, no 
magic involved, those things are called Regular Expressions or RegEx. 

The internet is full of explanations, tutorials, cheat sheets and evaluators for RegEx, so I'll refer you to Google for that one. In short RegEx is a fancy (and powerful) tool for search and replace. This project utilises them to check answers given by devices. For example, IKA RET Visc control hotplate stirrers reply to queries for numeric values (temperature, stir rate etc.) with strings like `"10.0 1\r\n"`. Those answers always consist of one or more numbers, a decimal point, more numbers, a space, one more digit, and then carriage return and newline characters. This translates into the RegEx "\d+\.\d+ \d\r\n". 

The additional parentheses in the example code above are what's called capture groups.
Mostly we are not interested in the entire string the device blurts back, but just in the actual value. By putting parentheses around the bit that is the value, we can pick out the part we are interested in. In the example above I also capture the second number, as the second number indicates which value has been returned, and I can check if I got the answer to the right question.

Again, as a mere user, don't worry about any of that. As a developer, you can choose to supply `None` as return pattern, in which case `send_message(get_return=True)` returns the raw answer string, stripped of newline characters. Or you can choose to supply a RegEx pattern, in which case the method instead returns a list of the captured groups. In the above example, the return looks like this:

```python
self.valueanswer = re.compile("(\d+\.\d+) (\d)\r\n")

print(self.send_message(self.get_temperature, get_return=True, return_pattern=None))
>>> "21.0 1\r\n"

print(self.send_message(self.get_temperature, get_return=True, return_pattern=self.valueanswer))
>>> ["21.0", "1"]
```

I hope you can see the utility of that little exercise. If you don't, or can't be bothered, you don't have to supply a pattern.
