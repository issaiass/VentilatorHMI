# Ventilator HMI

This is an example of a possible ventilator HMI done in python with Qt and is supplied as simple as it is for you to understand the code.

The implementation has a limitaton of the server polling capacity, a better server will provide more responses in les time.

The HMI acts as a client and is independant of the main controller.  Recall that this is the way all the RTUs (Remote Terminal Units) work with an HMI, the server in the controller is always active and the client will poll the server for parameters.

A list of parameters is detailed below sections and cand be expandable.  If the final client wants to support the project i will be replacing the Modbus TCP part to a SQLite client but still maintain the modbus project.

### Installation

Instructions below for creating the environment using conda and install all dependencies

```sh
$ conda create -n qtenv python=3.6
$ activate qtenv
$ pip install PyQt5 pyqtgraph pyModbusTCP
$ deactivate qtenv
```

Finally go to the root and excecute the main application...

```sh
$ python main.py
```

### Testing

You can test the application using pyModSlave

We assume this things from the client and the server

> localhost as the ip address (127.0.0.1)
> 502 as the default port
> Unit ID as 1 but it doesnt matter

This text you see here is *actually* written in Markdown! To get a feel for Markdown's syntax, type some text into the left window and watch the result


### Modbus Map and Mode of Functioning

Below is the modbus map for the server, that will need to make the graph for the client

* Coils
* [Stop / Start] - Coil 0 - 1 bit:  0 = Core processor did not started the ventilator, 1 = Core processor started the ventilator function


* Holding Registers
* [Graph Variable 1] - Holding Register 0 - 16 bits:  A variable for the first graph
* [Graph Variable 2] - Holding Register 1 - 16 bits:  A variable for the first graph
* [Graph Variable 3] - Holding Register 2 - 16 bits:  A variable for the first graph
* [Inspiration Time] - Holding Register 3 - 16 bits:  Inspiration time x 10, raw variable will have 1 decimal
* [Expiration Time] - Holding Register 4 - 16 bits:  Expiration time x 10, raw variable will have 1 decimal
* [Pressure] - Holding Register 5 - 16 bits:  Pressupre x 10, raw variable will have 1 decimal.


The mode of functioning is simple, when the HMI is up and running it will start a modbustcp client that will request data from the server, if the server is down the hmi will work forever until the application quits.

If the server is active the HMI will hold those variables and will graph it.  The client also has the capability of store the variables in a json file that will hold the actual settings of the core processor and will be available even if the client dies and is restarted.

It has also two buttons, one to confirm the settings and one to send the signal for start and stop the HMI.

Finally, there are two task, a task for the variable graphing and another task for the modbustcp requests.

You can view the video at https://youtu.be/H7ZD4PTJD5o
