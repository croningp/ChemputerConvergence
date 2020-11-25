# Chemputer Pumps and Valves API

This repo contains the software suite required to control chemputer pumps and valves.

## Getting Started

This API is self-contained and has no external dependencies. The API itself makes no assumptions about the subnet used, however, the default network config in config.py uses 192.168.1.255.

### Prerequisites

* Python 3.6

## Project structure

This repository contains the following subfolders and files in the root folder:

```
.
├── Chemputer_device_API            # Contains the API and config file
|   └── examples                    # Contains files exemplifying the configuration of new devices and use of the API
├── docs                            # Documentation files
├── tests                           # Test and exercise files for the devices
├── LICENSE.txt
└── README.md
```

## API operation

Detailed examples for how to use the API can be found in the `examples` subfolder. The API offers one public function and two public classes:

### initialise_udp_keepalive()

The devices require a regular UDP package containing a keepalive cookie, otherwise they reset themselves. This is a safety mechanism as well as a necessity, because the dumb fuck who designed the boards did not include a reset button.

Thus, the function `initialise_udp_keepalive()` has to be called exactly once at the beginning of your script, before instantiating any devices. If the firmware on the devices is in the stock configuration, no arguments have to be passed to `initialise_udp_keepalive()`, else a tuple containing the subnet and port has to be provided.

**Nota bene** make sure only one keepalive thread is running at any time, otherwise the increased load may cause the firmware to crash! I recognise this as a huge problem and it should be solved at some point, but right now I don't have the time.

### ChemputerPump(address, name="")

This class controls a Chemputer pump. It is instantiated with an IP address as string, and an optional name. The name is used for legible debug prints only. It establishes a TCP connection with the device, and then offers the user a range of methods covering all everyday needs. An exhaustive documentation of all provided methods should be compiled at some point, yet right now I don't really have the time, either.

### ChemputerValve(address, name="")

This class controls a Chemputer valve. It is instantiated with an IP address as string, and an optional name. The name is used for legible debug prints only. It establishes a TCP connection with the device, and then offers the user a range of methods covering all everyday needs. An exhaustive documentation of all provided methods should be compiled at some point, yet right now I don't really have the time, either.

## Authors

* **Cronin Group**
