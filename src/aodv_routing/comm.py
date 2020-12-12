import sys, listener, aodv
import sensor
import argparse


class comm():

    def __init__(self):
        self.aodv_handler=0

    # Main routine
    def main(self, n, node_id):
        
        self.node_id = node_id
        
        # Initialize and start the listener thread
        listener_thread = listener.listener()
        listener_thread.set_node_id(node_id)
        listener_thread.set_node_count(n)
        listener_thread.start()
        
        # Initialize and start the protocol handler thread
        aodv_thread = aodv.aodv()
        aodv_thread.set_node_id(node_id)
        aodv_thread.set_node_count(n)
        aodv_thread.start()

        # Initialize and start the vehicle simulation thread
        sensor_thread = sensor.sensor()
        sensor_thread.set_node_id(node_id)
        sensor_thread.daemon = True
        sensor_thread.start()         

# Get the arguments passed by the driver program 
n = 7
node_id = sys.argv[2]

node = node()
node.main(n, node_id)