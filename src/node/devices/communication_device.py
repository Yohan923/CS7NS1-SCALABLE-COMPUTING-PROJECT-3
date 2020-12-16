import threading, logging, socket, os, select, re
from threading import Timer
import json

# Defines
AODV_HELLO_INTERVAL         =   0.2
AODV_HELLO_TIMEOUT          =   600
AODV_PATH_DISCOVERY_TIME    =   30
AODV_ACTIVE_ROUTE_TIMEOUT   =   300

VEHICLE_PORT=33100
AODV_PORT = 33880
AODV_THREAD_PORT = 33980
SPEED_PORT=33881
SPEED_THREAD_PORT = 33981
HEADWAY_PORT=33882
HEADWAY_THREAD_PORT=33982
WIPER_PORT=33883
WIPER_THREAD_PORT=33983
LIGHT_PORT=33884
LIGHT_THREAD_PORT=33984
AODV_NETWORK_PORT = 33300 
AODV_SPEED_PORT=33500


class CommunicationDevice(threading.Thread):

    # Constructor
    def __init__(self,nid,neighbors=[]):
        threading.Thread.__init__(self)
        self.node_id = str(nid)
        self.seq_no = 0
        self.rreq_id = 0
        self.aodv_port = 0
        self.listener_sock = 0
        self.aodv_sock = 0
        self.tester_sock = 0
        self.log_file = ""
        self.command = ""
        self.neighbors = dict()
        self.routing_table = dict()
        self.message_box = dict()
        self.rreq_id_list = dict()
        self.pending_msg_q = []
        self.status = "Active"
        self.hello_timer = 0
        self.location_sensor_data=""
        self.photo_sensor_data=""
        self.rainfall_sensor_data=""
        self.aodv_add_neighbor(neighbors)

    def get_aodv_port(self, node):
        return AODV_NETWORK_PORT

    def get_aodv_ip(self, node):
        ip = {'n1':  '10.35.70.38',
                'n2':  '10.35.70.6',
                'n3':  '10.35.70.26',
                'n4': '10.35.70.16',
                'n5': '10.35.70.13'}['n'+str(node)]
                
        return ip       

    def aodv_restart_route_timer(self, route, create):
        if (create == False):
            pass

    def aodv_send(self, destination, destination_port, message):
        try:
            message_bytes = bytes(message, 'utf-8')
            destination_ip = self.get_aodv_ip(destination)
            self.aodv_sock.sendto(message_bytes, 0, 
                                  (destination_ip, destination_port))
        except:
            pass    
 
    def broadcast_photo_sensor_data(self):
        try:
            for n in self.neighbors.keys():
                if n!= self.node_id:
                    message_type = "BROADCAST_MESSAGE_PHOTO"
                    sender = self.node_id
                    message = message_type + ":" + sender + ":" + str(self.photo_sensor_data)
                    port = AODV_NETWORK_PORT
                    self.aodv_send(n, int(port), message)
                    logging.debug("['" + message_type + "', '" + sender + "', " + 
                                  "Sending photo_sensor_data message to " + str(n) + "']")

        except:
            pass   



    def broadcast_rainfall_sensor_data(self):
        
        try:
            for n in self.neighbors.keys():
                if n!= self.node_id:
                    message_type = "BROADCAST_MESSAGE_RAINFALL"
                    sender = self.node_id
                    message = message_type + ":" + sender + ":" + str(self.rainfall_sensor_data)
                    port = AODV_NETWORK_PORT
                    self.aodv_send(n, int(port), message)
                    logging.debug("['" + message_type + "', '" + sender + "', " + 
                                  "Sending rainfall_sensor_data message to " + str(n) + "']")

        except:
            pass        

    def aodv_process_broadcast_rainfall(self,message):
        sender = message[1]
        try:
            message=json.dumps(message[2])
            message_bytes = bytes(message, 'utf-8')
            self.aodv_sock.sendto(message_bytes, 0, 
                                      ('localhost', AODV_PORT))
        except:
            pass

        # try:
        #     for n in self.neighbors.keys():
        #         if n !=sender and n!= self.node_id:
        #             message_type = "BROADCAST_MESSAGE_RAINFALL"
        #             sender = self.node_id
        #             message = message_type + ":" + sender + ":" + str(self.rainfall_sensor_data)
        #             port = AODV_NETWORK_PORT
        #             self.aodv_send(n, int(port), message)

        # except:
        #     pass     

    def aodv_process_broadcast_photo(self,message):
        sender = message[1]

        try:
            message=json.dumps(message[2])
            message_bytes = bytes(message, 'utf-8')
            self.aodv_sock.sendto(message_bytes, 0, 
                                      ('localhost', AODV_PORT))
        except:
            pass

        # try:
        #     for n in self.neighbors.keys():
        #         if n !=sender and n!= self.node_id:
        #             message_type = "BROADCAST_MESSAGE_PHOTO"
        #             sender = self.node_id
        #             message = message_type + ":" + sender + ":" + str(self.photo_sensor_data)
        #             port = AODV_NETWORK_PORT
        #             self.aodv_send(n, int(port), message)
        #             logging.debug("['" + message_type + "', '" + sender + "', " + 
        #                           "Sending photo_sensor_data message to " + str(n) + "']")

        # except:
        #     pass  


    # Send the hello message to all the neighbors
    def aodv_send_hello_message(self):
        try:

            message={'neighbors':list(self.neighbors.keys())}
            # message=json.dumps(message)
            # # message_bytes = bytes(message, 'utf-8')
            # # self.aodv_sock.sendto(message_bytes, 0, 
            # #                           ('localhost', AODV_PORT))
        except:
            pass
            
        try:
            # Send message to each neighbor
            for n in self.neighbors.keys():
                message_type = "HELLO_MESSAGE"
                sender = self.node_id
                message_data = "Hello message from " + self.node_id
                message = message_type + ":" + sender + ":" + message_data+ ":" +str(self.location_sensor_data)
                port = AODV_NETWORK_PORT
                
                self.aodv_send(n, int(port), message)
                logging.debug("['" + message_type + "', '" + sender + "', " + 
                              "Sending hello message to " + str(n) + "']")
        
            # Restart the timer
            self.hello_timer.cancel()
            self.hello_timer = Timer(AODV_HELLO_INTERVAL, self.aodv_send_hello_message, ())
            self.hello_timer.start()
            
        except:
            pass
        
   # Process incoming hello messages
    def aodv_process_hello_message(self, message):
        logging.debug(message)
        sender = message[1]
        message[3]=message[3].replace('\'','\"')
        command_type = "RECEIVE"
        msg = command_type+":"+sender+":"+message[3]
        # print("Received data from node "+sender+": "+message[3])
        # TODO: maybe delete this node from neighbors if it is too far away
        message_bytes = bytes(msg, 'utf-8')
        self.aodv_sock.sendto(message_bytes, 0, 
                    ('localhost', SPEED_THREAD_PORT))

           

        try:
            if (sender in self.neighbors.keys()):
                neighbor = self.neighbors[sender]
                route = self.routing_table[sender]
                self.aodv_restart_route_timer(route, False)

            else:
                if (sender in self.routing_table.keys()):
                    route = self.routing_table[sender]
                    self.aodv_restart_route_timer(route, False)
                else:
                    self.routing_table[sender] = {'Destination': sender, 
                                                  'Destination-Port': AODV_NETWORK_PORT, 
                                                  'Next-Hop': sender, 
                                                  'Next-Hop-Port': AODV_NETWORK_PORT, 
                                                  'Seq-No': '1', 
                                                  'Hop-Count': '1', 
                                                  'Status': 'Active'}
                    self.aodv_restart_route_timer(self.routing_table[sender], True)

        except KeyError:
            pass

    # Process incoming application message
    def aodv_process_user_message(self, message):
        
        # Get the message contents, sender and receiver
        sender = message[1]
        receiver = message[2]
        msg = message[3]
        
        # Check if the message is for us
        if (receiver == self.node_id):

            # Add the message to the message box
            self.message_box[msg] = {'Sender': sender, 'Message': msg}
        
            # Log the message and notify the user
            logging.debug(message)
            print("New message arrived. Issue 'view_messages' to see the contents")
        
        else:
            route = self.routing_table[receiver]
            next_hop = route['Next-Hop']
            next_hop_port = int(route['Next-Hop-Port'])
            self.aodv_restart_route_timer(route, False)
            message = message[0] + ":" + message[1] + ":" + message[2] + ":" + message[3]
            self.aodv_send(next_hop, next_hop_port, message)
            logging.debug("['USER_MESSAGE', '" + sender + " to " + receiver + "', " + msg + "']")

    # Process an incoming RREQ message
    def aodv_process_rreq_message(self, message):
        
        # Extract the relevant parameters from the message
        message_type = message[0]
        sender = message[1]
        hop_count = int(message[2]) + 1
        message[2] = str(hop_count)
        rreq_id = int(message[3])
        dest = message[4]
        dest_seq_no = int(message[5])
        orig = message[6]
        orig_seq_no = int(message[7])
        orig_port = self.get_aodv_port(orig)
        sender_port = self.get_aodv_port(sender)

        # Ignore the message if we are not active
        if (self.status == "Inactive"):
            return

        logging.debug("['" + message[0] + "', 'Received RREQ to " + message[4] + " from " + sender + "']")

        # Discard this RREQ if we have already received this before
        if (orig in self.rreq_id_list.keys()):
            node_list = self.rreq_id_list[orig]
            per_node_rreq_id_list = node_list['RREQ_ID_List']
            if rreq_id in per_node_rreq_id_list.keys():
                logging.debug("['RREQ_MESSAGE', 'Ignoring duplicate RREQ (" + orig + ", " + str(rreq_id) + ") from " + sender + "']")
                return

        # This is a new RREQ message. Buffer it first
        if (orig in self.rreq_id_list.keys()):
            per_node_list = self.rreq_id_list[orig]
        else:
            per_node_list = dict()
        path_discovery_timer = Timer(AODV_PATH_DISCOVERY_TIME, 
                                     self.aodv_process_path_discovery_timeout, 
                                     [orig, rreq_id])
        per_node_list[rreq_id] = {'RREQ_ID': rreq_id, 
                                  'Timer-Callback': path_discovery_timer}
        self.rreq_id_list[orig] = {'Node': self.node_id, 
                                   'RREQ_ID_List': per_node_list}
        path_discovery_timer.start()

        if orig in self.routing_table.keys():
            # TODO update lifetime timer for this route
            route = self.routing_table[orig]
            if (int(route['Seq-No']) < orig_seq_no):
                route['Seq-No'] = orig_seq_no
                self.aodv_restart_route_timer(route, False)
            elif (int(route['Seq-No']) == orig_seq_no):
                if (int(route['Hop-Count']) > hop_count):
                    route['Hop-Count'] = hop_count
                    route['Next-Hop'] = sender
                    route['Next-Hop-Port'] = sender_port
                    self.aodv_restart_route_timer(route, False)
            elif (int(route['Seq-No']) == -1):
                route['Seq-No'] = orig_seq_no
                self.aodv_restart_route_timer(route, False)

        else:
            # TODO update lifetime timer for this route
            self.routing_table[orig] = {'Destination': str(orig), 
                                        'Destination-Port': str(orig_port),
                                        'Next-Hop': str(sender),
                                        'Next-Hop-Port': str(sender_port),
                                        'Seq-No': str(orig_seq_no),
                                        'Hop-Count': str(hop_count),
                                        'Status': 'Active'}
            self.aodv_restart_route_timer(self.routing_table[orig], True)

        if (self.node_id == dest):
            self.aodv_send_rrep(orig, sender, dest, dest, 0, 0)
            return

        if (dest in self.routing_table.keys()):
            # Verify that the route is valid and has a higher seq number
            route = self.routing_table[dest]
            status = route['Status']
            route_dest_seq_no = int(route['Seq-No'])
            if (status == "Active" and route_dest_seq_no >= dest_seq_no):
                self.aodv_send_rrep(orig, sender, self.node_id, dest, route_dest_seq_no, int(route['Hop-Count']))
                return
        else:
            self.aodv_forward_rreq(message)

    # Process an incoming RREP message
    def aodv_process_rrep_message(self, message):
        # Extract the relevant fields from the message
        message_type = message[0]
        sender = message[1]
        hop_count = int(message[2]) + 1
        message[2] = str(hop_count)
        dest = message[3]
        dest_seq_no = int(message[4])
        orig = message[5]

        logging.debug("['" + message_type + "', 'Received RREP for " + dest + " from " + sender + "']")

        # Check if we originated the RREQ. If so, consume the RREP.
        if (self.node_id == orig):
            if (dest in self.routing_table.keys()):
                route = self.routing_table[dest]
                route_hop_count = int(route['Hop-Count'])
                if (route_hop_count > hop_count):
                    route['Hop-Count'] = str(hop_count)
                    self.aodv_restart_route_timer(self.routing_table[dest], False)
            else:
                self.routing_table[dest] = {'Destination': dest,
                                            'Destination-Port': self.get_aodv_port(dest),
                                            'Next-Hop': sender,
                                            'Next-Hop-Port': self.get_aodv_port(sender),
                                            'Seq-No': str(dest_seq_no),
                                            'Hop-Count': str(hop_count),
                                            'Status': 'Active'}
                self.aodv_restart_route_timer(self.routing_table[dest], True)

            # Check if we have any pending messages to this destination
            for m in self.pending_msg_q:
                msg = re.split(':', m)
                d = msg[2]
                if (d == dest):
                    # Send the pending message and remove it from the buffer
                    next_hop = sender
                    next_hop_port = self.get_aodv_port(next_hop)
                    self.aodv_send(next_hop, int(next_hop_port), m)
                    logging.debug("['USER_MESSAGE', '" + msg[1] + " to " + msg[2] + " via " + next_hop + "', '" + msg[3] + "']")
                    print("Message sent")
           
                    self.pending_msg_q.remove(m)

        else:
            if (dest in self.routing_table.keys()):
                route = self.routing_table[dest]
                route['Status'] = 'Active'
                route['Seq-No'] = str(dest_seq_no)
                self.aodv_restart_route_timer(route, False)
            else:
                self.routing_table[dest] = {'Destination': dest,
                                            'Destination-Port': self.get_aodv_port(dest),
                                            'Next-Hop': sender,
                                            'Next-Hop-Port': self.get_aodv_port(sender),
                                            'Seq-No': str(dest_seq_no),
                                            'Hop-Count': str(hop_count),
                                            'Status': 'Active'}
                self.aodv_restart_route_timer(self.routing_table[dest], True)
                # TODO update/add a lifetime timer for the route

            # Now lookup the next-hop for the source and forward it
            route = self.routing_table[orig]
            next_hop = route['Next-Hop']
            next_hop_port = int(route['Next-Hop-Port'])
            self.aodv_forward_rrep(message, next_hop, next_hop_port)

    # Process an incoming RERR message
    def aodv_process_rerr_message(self, message):
        # Extract the relevant fields from the message
        message_type = message[0]
        sender = message[1]
        dest = message[3]
        dest_seq_no = int(message[4])

        if (self.node_id == dest):
            return

        logging.debug("['" + message_type + "', 'Received RERR for " + dest + " from " + sender + "']")

        if (dest in self.routing_table.keys()):
            route = self.routing_table[dest]
            if (route['Status'] == 'Active' and route['Next-Hop'] == sender):
                # Mark the destination as inactive
                route['Status'] = "Inactive"

                # Forward the RERR to all the neighbors
                self.aodv_forward_rerr(message)
            else:
                logging.debug("['" + message_type + "', 'Ignoring RERR for " + dest + " from " + sender + "']")

    # Broadcast an RREQ message for the given destination
    def aodv_send_rreq(self, destination, destination_seq_no):
        
        # Increment our sequence number
        self.seq_no = self.seq_no + 1
        
        # Increment the RREQ_ID
        self.rreq_id = self.rreq_id + 1
        
        # Construct the RREQ packet
        message_type = "RREQ_MESSAGE"
        sender = self.node_id
        hop_count = 0
        rreq_id = self.rreq_id
        dest = destination
        dest_seq_no = destination_seq_no
        orig = self.node_id
        orig_seq_no = self.seq_no
        message = message_type + ":" + sender + ":" + str(hop_count) + ":" + str(rreq_id) + ":" + str(dest) + ":" + str(dest_seq_no) + ":" + str(orig) + ":" + str(orig_seq_no)
        
        # Broadcast the RREQ packet to all the neighbors
        for n in self.neighbors:
            port = self.get_aodv_port(n)
            self.aodv_send(n, int(port), message)
            logging.debug("['" + message_type + "', 'Broadcasting RREQ to " + dest + "']")
            
        # Buffer the RREQ_ID for PATH_DISCOVERY_TIME. This is used to discard duplicate RREQ messages
        if (self.node_id in self.rreq_id_list.keys()):
            per_node_list = self.rreq_id_list[self.node_id]
        else:
            per_node_list = dict()
        path_discovery_timer = Timer(AODV_PATH_DISCOVERY_TIME, 
                                     self.aodv_process_path_discovery_timeout, 
                                     [self.node_id, rreq_id])
        per_node_list[rreq_id] = {'RREQ_ID': rreq_id, 
                                  'Timer-Callback': path_discovery_timer}
        self.rreq_id_list[self.node_id] = {'Node': self.node_id, 
                                           'RREQ_ID_List': per_node_list}
        path_discovery_timer.start()

    # 
    # Rebroadcast an RREQ request (Called when RREQ is received by an
    # intermediate node)
    #
    def aodv_forward_rreq(self, message):
        msg = message[0] + ":" + self.node_id + ":" + message[2] + ":" + message[3] + ":" + message[4] + ":" + message[5] + ":" + message[6] + ":" + message[7]
        for n in self.neighbors:
            port = self.get_aodv_port(n)
            self.aodv_send(n, int(port), msg)
            logging.debug("['" + message[0] + "', 'Rebroadcasting RREQ to " + message[4] + "']")

    # Send an RREP message back to the RREQ originator
    def aodv_send_rrep(self, rrep_dest, rrep_nh, rrep_src, rrep_int_node, dest_seq_no, hop_count):

        if (rrep_src == rrep_int_node):
            # Increment the sequence number and reset the hop count
            self.seq_no = self.seq_no + 1
            dest_seq_no = self.seq_no
            hop_count = 0

        # Construct the RREP message
        message_type = "RREP_MESSAGE"
        sender = self.node_id
        dest = rrep_int_node
        orig = rrep_dest
        message = message_type + ":" + sender + ":" + str(hop_count) + ":" + str(dest) + ":" + str(dest_seq_no) + ":" + str(orig)

        # Now send the RREP to the RREQ originator along the next-hop
        port = self.get_aodv_port(rrep_nh)
        self.aodv_send(rrep_nh, int(port), message)
        logging.debug("['" + message_type + "', 'Sending RREP for " + rrep_int_node + " to " + rrep_dest + " via " + rrep_nh + "']")


    def aodv_forward_rrep(self, message, next_hop, next_hop_port):
        msg = message[0] + ":" + self.node_id + ":" + message[2] + ":" + message[3] + ":" + message[4] + ":" + message[5]
        self.aodv_send(next_hop, next_hop_port, msg)
        logging.debug("['" + message[0] + "', 'Forwarding RREP for " + message[5] + " to " + next_hop + "']")

    # Generate and send a Route Error message
    def aodv_send_rerr(self, dest, dest_seq_no):
        # Construct the RERR message
        message_type = "RERR_MESSAGE"
        sender = self.node_id
        dest_count = '1'
        dest_seq_no = dest_seq_no + 1
        message = message_type + ":" + sender + ":" + dest_count + ":" + dest + ":" + str(dest_seq_no)

        # Now broadcast the RREQ message
        for n in self.neighbors.keys():
            port = self.get_aodv_port(n)
            self.aodv_send(n, int(port), message)

        logging.debug("['" + message_type + "', 'Sending RERR for " + dest + "']")

    # Forward a Route Error message
    def aodv_forward_rerr(self, message):
        msg = message[0] + ":" + self.node_id + ":" + message[2] + ":" + message[3] + ":" + message[4]
        for n in self.neighbors.keys():
            port = self.get_aodv_port(n)
            self.aodv_send(n, int(port), msg)

        logging.debug("['" + message[0] + "', 'Forwarding RERR for " + message[3] + "']")

    # Handle neighbor timeouts
    def aodv_process_neighbor_timeout(self, neighbor):
        pass
        
    def aodv_process_path_discovery_timeout(self, node, rreq_id):
        
        # Remove the buffered RREQ_ID for the given node
        if node in self.rreq_id_list.keys():
            node_list =  self.rreq_id_list[node]
            per_node_rreq_id_list = node_list['RREQ_ID_List']
            if rreq_id in per_node_rreq_id_list.keys():
                per_node_rreq_id_list.pop(rreq_id)
    
    # Handle route timeouts
    def aodv_process_route_timeout(self, route):

        # Remove the route from the routing table
        key = route['Destination']
        self.routing_table.pop(key)

        if (key in self.neighbors):
            self.neighbors.pop(key)

        logging.debug("aodv_process_route_timeout: removing " + key + " from the routing table.")

    # Simulate a link-up event for the current node
    def aodv_simulate_link_up(self, from_tester):
        if (self.status == "Active"):
            print("Node is already active!")
            return

        # Start the hello timer again
        self.hello_timer = Timer(AODV_HELLO_INTERVAL, self.aodv_send_hello_message, ())
        self.hello_timer.start()

        # Restart all the lifetime timers in the routing table
        for r in self.routing_table.keys():
            route = self.routing_table[r]

        self.status = "Active"

        logging.debug("Activating node " + self.node_id)
        print("Activated node " + self.node_id + ". This node will resume sending hello messages.")

    def aodv_command_stop(self, from_tester):
        if (from_tester == False):
            message_type = "COMMAND_STOP"
            message = message_type + ":" + ""
            message_bytes = bytes(message, 'utf-8')
            port = SPEED_THREAD_PORT
            self.tester_sock.sendto(message_bytes, 0,('localhost', int(port)))
        print("Sent ["+message+"] to vehicle thread")


    
    # Take the neighbor set for the current node from the user
    def aodv_add_neighbor(self,neighbors):
        for n in neighbors:
            timer = Timer(AODV_HELLO_TIMEOUT, 
                          self.aodv_process_neighbor_timeout, [n])
            self.neighbors[n] = {'Neighbor': n, 'Timer-Callback': timer}
            # timer.start()

        print("Neighbors added successfully: ", self.neighbors.keys())
        
        # Update the routing table. Setup direct routes for each added neighbor.
        for n in neighbors:
            # TODO: Add lifetime timer
            dest = str(n)
            dest_port = str(self.get_aodv_port(n))
            nh = str(n)
            nh_port = str(self.get_aodv_port(n))
            seq = '1'
            hop_count = '1'
            status = 'Active'
            
            self.routing_table[dest] = {'Destination': dest, 
                                        'Destination-Port': dest_port, 
                                        'Next-Hop': nh, 
                                        'Next-Hop-Port': nh_port, 
                                        'Seq-No': seq, 
                                        'Hop-Count': hop_count, 
                                        'Status': status}
            self.aodv_restart_route_timer(self.routing_table[dest], True)
            
        # Start a timer to start sending hello messages periodically
        
        self.hello_timer = Timer(AODV_HELLO_INTERVAL, self.aodv_send_hello_message, ())
        self.hello_timer.start()
        
    # Simulate a link-down event for the current node
    def aodv_simulate_link_down(self, from_tester):
        if (self.status == "Inactive"):
            print("Node is already down!")
            return

        # Cancel the hello timer
        self.hello_timer.cancel()

        # Stop all the lifetime timers in the routing table
        for r in self.routing_table.keys():
            route = self.routing_table[r]
            timer = route['Lifetime']
            timer.cancel()

        self.status = "Inactive"

        logging.debug("Deactivating node " + self.node_id)
        print("Deactivated node " + self.node_id + ". This node will stop sending hello messages.")
        
    # Delete the messages buffered for the given node
    def aodv_delete_messages(self, from_tester):
        # Remove all the messages from the message box
        self.message_box.clear()
        print("Message box has been cleared")
                    
    # Send a message to a peer
    def aodv_send_message(self, from_tester):
        # Get the command sent by the listener thread / tester process
        command = self.command
        if (from_tester == False):
            source = command[1]
            dest = command[2]
            message_data = command[3]
        else:
            source = command[1]
            dest = command[2]
            message_data = command[3]
        
        # Format the message
        message_type = "USER_MESSAGE"
        message = message_type + ":" + source + ":" + dest + ":" + message_data
        
        if dest in self.routing_table.keys():
            destination = self.routing_table[dest]
            
            if (destination['Status'] == 'Inactive'):
                self.aodv_send_rreq(dest, destination['Seq-No'])
            else:
                next_hop = destination['Next-Hop']
                next_hop_port = destination['Next-Hop-Port']
                self.aodv_send(next_hop, int(next_hop_port), message)
                # TODO: update lifetime here as the route was used
                self.aodv_restart_route_timer(destination, False)
                logging.debug("['USER_MESSAGE', '" + source + " to " + dest + " via " + next_hop + "', '" + message_data + "']")
                print("Message sent")
        else:
            # Initiate a route discovery message to the destination
            self.aodv_send_rreq(dest, -1)

            # Buffer the message and resend it once RREP is received
            self.pending_msg_q.append(message)

    # Display the routing table for the current node
    def aodv_show_routing_table(self, from_tester):
        print("")
        print("There are " + str(len(self.routing_table)) + " active route(s) in the routing-table")
        print("")
        
        print("Destination     Next-Hop     Seq-No     Hop-Count     Status")
        print("------------------------------------------------------------")
        for r in self.routing_table.values():
            print(r['Destination'] + "              " + r['Next-Hop'] + "           " + r['Seq-No'] + "          " + r['Hop-Count'] + "             " + r['Status'])
        print("")
        
        self.status = "Success"

    # Dump the log file to the console
    def aodv_show_log(self, from_tester):
        for line in open(self.log_file, 'r'):
            print(line)
            
    # Return the buffered messages back to the node
    def aodv_show_messages(self, from_tester):
        print("")
        print("There are " + str(len(self.message_box)) + " message(s) in the message-box")
        print("")
        
        print("Sender     Message")
        print("------------------")
        for m in self.message_box.values():
            print(m['Sender'] + "         " + m['Message'])
        print("")
        
        self.status = "Success"
        
    # Default action handler
    def aodv_default(self):
        pass
    
    # Thread start routine
    def run(self):
        
        # Setup logging
        self.log_file = "aodv_log_" + str(self.node_id)
        FORMAT = "%(asctime)s - %(message)s"
        logging.basicConfig(filename=self.log_file, 
                            level=logging.DEBUG, 
                            format=FORMAT)
        
        self.aodv_port = self.get_aodv_port(self.node_id)
        
        self.tester_thread_port = SPEED_THREAD_PORT

        self.listener_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.listener_sock.bind(('localhost', AODV_THREAD_PORT))
        self.listener_sock.setblocking(0)
        self.listener_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # tester_sock is responsible for communication to the speed sensor thread
        self.tester_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tester_sock.bind(('localhost', AODV_SPEED_PORT))
        self.tester_sock.setblocking(0)
        self.tester_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.aodv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.aodv_sock.bind(('', AODV_NETWORK_PORT))
        self.aodv_sock.setblocking(0)
        self.aodv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        logging.debug("node " + self.node_id + " started on port " + str(self.aodv_port) + " with pid " + str(os.getpid()))
        self.status = "Active"

        # self.hello_timer = Timer(AODV_HELLO_INTERVAL, self.aodv_send_hello_message, ())
        # self.hello_timer.start()


        inputs = [self.listener_sock, self.tester_sock, self.aodv_sock]
        outputs = []

        while inputs:
            readable, _, _ = select.select(inputs, outputs, inputs)
            for r in readable:
                if r is self.listener_sock:

                    # We got a message from the listener thread. Process it.
                    command, _ = self.listener_sock.recvfrom(100)
                    command = command.decode('utf-8')
                    command = re.split(':', command)
                    command_type = command[0]
                    self.command = command

                    if command_type == "NODE_ACTIVATE":
                        self.aodv_simulate_link_up(False)
                    elif command_type == "ADD_NEIGHBOR":
                        pass
                    elif command_type == "NODE_DEACTIVATE":
                        self.aodv_simulate_link_down(False)
                    elif command_type == "DELETE_MESSAGES":
                        self.aodv_delete_messages(False)
                    elif command_type == "SEND_MESSAGE":
                        self.aodv_send_message(False)
                    elif command_type == "SHOW_ROUTE":
                        self.aodv_show_routing_table(False)
                    elif command_type == "VIEW_LOG":
                        self.aodv_show_log(False)
                    elif command_type == "VIEW_MESSAGES":
                        self.aodv_show_messages(False)
                    elif command_type == "COMMAND_STOP":
                        self.aodv_command_stop(False)                        
                    else:
                        self.aodv_default()
                     
                    # Send the status back to the listener thread
                    message = bytes(self.status, 'utf-8')
                    self.listener_sock.sendto(message, 0, 
                                              ('localhost', AODV_PORT))
                    
                elif r is self.tester_sock:
                    command, _ = self.tester_sock.recvfrom(1000)
                    command = command.decode('utf-8')
                    
                    sensor_data = json.loads(command)
                    if 'light_intensity' in sensor_data.keys():
                        # print("test->aodv"+command)
                        self.photo_sensor_data = sensor_data
                        self.broadcast_photo_sensor_data();
                    elif 'humidity' in sensor_data.keys():
                        # print("test->aodv"+command)
                        self.rainfall_sensor_data = sensor_data
                        self.broadcast_rainfall_sensor_data();
                    elif 'location' in sensor_data.keys():
                        self.location_sensor_data = sensor_data




                elif r is self.aodv_sock:
                    # We got a message from the network
                    message, _ = self.aodv_sock.recvfrom(2000)
                    message = message.decode('utf-8')
                    message_type = message.split(':',1)[0]
                    
                    if (message_type == "HELLO_MESSAGE"):
                        message = message.split(':',3)
                        self.aodv_process_hello_message(message)
                    elif (message_type == "USER_MESSAGE"):
                        message = re.split(':', message)
                        self.aodv_process_user_message(message)
                    elif (message_type == "RREQ_MESSAGE"):
                        message = re.split(':', message)
                        self.aodv_process_rreq_message(message)
                    elif (message_type == "RREP_MESSAGE"):
                        message = re.split(':', message)
                        self.aodv_process_rrep_message(message)
                    elif (message_type == "RERR_MESSAGE"):
                        message = re.split(':', message)
                        self.aodv_process_rerr_message(message)
                    elif (message_type == "BROADCAST_MESSAGE_RAINFALL"):
                        print("aodv->aodv "+message)
                        message = message.split(':', 2)
                        self.aodv_process_broadcast_rainfall(message)                       
                    elif (message_type == "BROADCAST_MESSAGE_PHOTO"):
                        print("aodv->aodv "+message)
                        message = message.split(':', 2)
                        self.aodv_process_broadcast_photo(message)             
# End of File
