# P4Mite

P4mite - resource aware load balancer

## Overview

There are multiple folders in the project:
```bash
ls
```
1. [The switches](https://github.com/PINetDalhousie/in-network-dispatcher#Switches)
2. [The application](https://github.com/PINetDalhousie/in-network-dispatcher#Applications)
3. [SmartNIC-LB](https://github.com/PINetDalhousie/in-network-dispatcher#SmartNIC-LB)



# Switches
There are three switches implemented:

```bash
cd switches
```

#### To bring P4Mite switch up
```bash
./setup_switch.sh p4mite_switch.p4
```
#### To bring ECMP switch up
```bash
./setup_switch.sh ecmp_switch.p4
```
#### To bring round robin switch up
```bash
./setup_switch.sh round_robin.p4
```
For each switch, there is a Python script containing the configurations. The configuration files should be updated based on the physical connections and IP addresses in the testbed. In our case:

- The client: 10.50.0.1
- The server: 10.50.0.6
- The SmartNIC: 10.50.0.16


# Applications
There are 5 ones in the applications folder:


1. p4mite_agent.py:
The agent monitoring server and measure latency using tcpdump
```bash
cd applications
sudo tcpdump --immediate-mode -n -i <INTERFACE_NAME> | sudo python3 p4mite_agent.py <SERVER_ADDR> <ACCELERATE_ADDR> <THRESHOLD>
```

2. Microbenchmark: a synthetic workload

To run the microbenchmark's server
```bash
cd applications/microbenchmark/server

# To see the options
python3 server_bite_report.py -h

# An example:
python3 server_bite_report.py -H <HOST_ADDR> -P <PORT>

# Run multiple instances:
./run.sh
```

To run the client:
```bash
cd applications/microbenchmark/client

# To see the options
python3 client_multi_port.py -h

#By defaults the client sends the request to ports [10001,10020] of the server.
# An example:
python3 client_multi_port.py -H <HOST_ADDR> -N <NUMBER_OF_REQUESTS> -R <SENDING_RATE>
```



3. VGG16: 

there are two version of the server for VGG16. One version uses TensorFlow (```server_udp_reporting.py```), and the other version uses TensorFlow lite (```server_udp_arm.py```).

```bash
cd applications/vgg16/server

# To run TensorFlow version
python3 server_udp_reporting.py -H <HOST_ADDR> -P <PORT>

# To run TensorFlow lite version
python3 server_udp_arm.py -H <HOST_ADDR> -P <PORT>

# To see help
python3 server_udp_reporting.py -h
python3 server_udp_arm.py -h
```

VGG16's client

```bash
cd applications/vgg16/client

#By defaults the client sends the request to ports [10001,10020] of the server.
python3 client_udp_multi_ports.py -H <HOST_ADDR> -N <NUMBER_OF_REQUESTS> -R <SENDING_RATE>

# To see help:
python3 client_udp_multi_ports.py -h
```



4. KNN:

KNN's Server:

```bash
cd applications/knn/server

python3 server_knn_reporting.py <HOST_ADDR> -P <PORT>
# To see help:
python3 server_knn_reporting.py -h
```

KNN's Client:
```bash
cd applications/knn/client

#By defaults the client sends the request to ports [10001,10020] of the server.
python3 client_udp_multi_ports.py -H <HOST_ADDR> -N <NUMBER_OF_REQUESTS> -R <SENDING_RATE>

# To see help:
python3 client_udp_multi_ports.py -h
```


5. DNS

DSN's Server:
```bash
cd applications/dns/server
python3 dns.py
```

DNS's client:
```bash
cd applications/dns/client
python dnsclient.py --server <SERVER_ADDR>:5053 -R <RATE> 'example.com'
```


```python
import foobar

# returns 'words'
foobar.pluralize('word')

# returns 'geese'
foobar.pluralize('goose')

# returns 'phenomenon'
foobar.singularize('phenomena')
```

#SmartNIC-LB

```bash
cd SmartNIC-LB

sudo python3 lb.py -H <LB_ADDR or SmartNIC_ADDR> -P <PORT>

# To see the help:
python3 lb.py -h
```
<!-- ## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/) -->
