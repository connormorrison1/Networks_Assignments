'''
Created on Oct 12, 2016

@author: mwittie
'''
import queue
import threading


## wrapper class for a queue of packets
class Interface:
    ## @param maxsize - the maximum size of the queue storing packets
    def __init__(self, maxsize=0):
        self.queue = queue.Queue(maxsize);
        self.mtu = None
    
    ##get packet from the queue interface
    def get(self):
        try:
            return self.queue.get(False)
        except queue.Empty:
            return None
        
    ##put the packet into the interface queue
    # @param pkt - Packet to be inserted into the queue
    # @param block - if True, block until room in queue, if False may throw queue.Full exception
    def put(self, pkt, block=False):
        self.queue.put(pkt, block)
        
        
## Implements a network layer packet (different from the RDT packet 
# from programming assignment 2).
# NOTE: This class will need to be extended to for the packet to include
# the fields necessary for the completion of this assignment.
class NetworkPacket:
    ## packet encoding lengths 
    dst_addr_S_length = 5
    packet_ID_Length = 7
    packet_Flag_Length = 8
    
    ##@param dst_addr: address of the destination host
    # @param data_S: packet payload
    def __init__(self, dst_addr, data_S, ID, flag):
        self.dst_addr = dst_addr
        self.data_S = data_S
        self.packet_ID = ID
        self.packet_Flag = flag
        
    ## called when printing the object
    def __str__(self):
        return self.to_byte_S()
        
    ## convert packet to a byte string for transmission over links
    def to_byte_S(self):
        byte_S = str(self.dst_addr).zfill(self.dst_addr_S_length)
        byte_S += str(self.packet_ID)
        byte_S += str(self.packet_Flag)
        byte_S += self.data_S
        return byte_S
    
    ## extract a packet object from a byte string
    # @param byte_S: byte string representation of the packet
    @classmethod
    def from_byte_S(self, byte_S):
        dst_addr = int(byte_S[0 : NetworkPacket.dst_addr_S_length])
        packet_ID = int(byte_S[NetworkPacket.dst_addr_S_length : NetworkPacket.packet_ID_Length])
        packet_Flag = int(byte_S[NetworkPacket.packet_ID_Length : NetworkPacket.packet_Flag_Length])
        data_S = byte_S[NetworkPacket.packet_Flag_Length : ]
        return self(dst_addr, data_S, packet_ID, packet_Flag)
    

    

## Implements a network host for receiving and transmitting data
class Host:
    
    ##@param addr: address of this node represented as an integer
    def __init__(self, addr):
        self.addr = addr
        self.in_intf_L = [Interface()]
        self.out_intf_L = [Interface()]
        self.stop = False #for thread termination
        self.packet_ID = 10
        self.partial_packet = {}
    
    ## called when printing the object
    def __str__(self):
        return 'Host_%s' % (self.addr)
       
    ## create a packet and enqueue for transmission
    # @param dst_addr: destination address for the packet
    # @param data_S: data being transmitted to the network layer
    def udt_send(self, dst_addr, data_S):
        self.packet_ID +=1
        mtu_Length = self.out_intf_L[0].mtu - NetworkPacket.packet_Flag_Length
        num_Packets = 1
        if mtu_Length < len(data_S):
            num_Packets = int(len(data_S) / mtu_Length) + 1

        packet_begin_index = 0
        packet_end_index = mtu_Length
        packet_flag = 0
        for i in range(num_Packets):
            if packet_end_index > len(data_S):
                packet_end_index = len(data_S)
                packet_flag = 1
            p = NetworkPacket(dst_addr, data_S[packet_begin_index:packet_end_index], self.packet_ID, packet_flag)
            self.out_intf_L[0].put(p.to_byte_S())  # send packets always enqueued successfully
            print('%s: sending packet "%s" on the out interface with mtu=%d' % (self, p, self.out_intf_L[0].mtu))
            packet_begin_index += mtu_Length
            packet_end_index += mtu_Length

        
    ## receive packet from the network layer
    def udt_receive(self):
        pkt_S = self.in_intf_L[0].get()
        if pkt_S is not None:
            index = pkt_S[NetworkPacket.dst_addr_S_length: NetworkPacket.packet_ID_Length]
            if int(pkt_S[NetworkPacket.packet_ID_Length: NetworkPacket.packet_Flag_Length]) == 0:
                if index in self.partial_packet:
                    self.partial_packet[index] = self.partial_packet[index]+pkt_S[NetworkPacket.packet_Flag_Length : ]
                else:
                    self.partial_packet[index] = pkt_S[NetworkPacket.packet_Flag_Length:]
            else:
                self.partial_packet[index] = self.partial_packet[index]+pkt_S[NetworkPacket.packet_Flag_Length : ]
                print('%s: received packet "%s" on the in interface' % (self, self.partial_packet[index]))
       
    ## thread target for the host to keep receiving data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            #receive data arriving to the in interface
            self.udt_receive()
            #terminate
            if(self.stop):
                print (threading.currentThread().getName() + ': Ending')
                return
        


## Implements a multi-interface router described in class
class Router:
    
    ##@param name: friendly router name for debugging
    # @param intf_count: the number of input and output interfaces 
    # @param max_queue_size: max queue length (passed to Interface)
    def __init__(self, name, intf_count, max_queue_size):
        self.stop = False #for thread termination
        self.name = name
        #create a list of interfaces
        self.in_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]
        self.out_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]

    ## called when printing the object
    def __str__(self):
        return 'Router_%s' % (self.name)

    ## look through the content of incoming interfaces and forward to
    # appropriate outgoing interfaces
    def forward(self):
        for i in range(len(self.in_intf_L)):
            pkt_S = None
            try:
                #get packet from interface i
                pkt_S = self.in_intf_L[i].get()
                #if packet exists make a forwarding decision
                if pkt_S is not None:
                    p = NetworkPacket.from_byte_S(pkt_S) #parse a packet out
                    # HERE you will need to implement a lookup into the 
                    # forwarding table to find the appropriate outgoing interface
                    # for now we assume the outgoing interface is also i

                    data = p.data_S
                    full_packet_flag = p.packet_Flag
                    packet_ID = p.packet_ID
                    dst_address = p.dst_addr

                    mtu_Length = self.out_intf_L[0].mtu - NetworkPacket.packet_Flag_Length
                    num_Packets = 1
                    if mtu_Length < len(data):
                        num_Packets = int(len(data) / mtu_Length) + 1
                    packet_begin_index = 0
                    packet_end_index = mtu_Length
                    packet_flag = 0

                    for j in range(num_Packets):
                        if packet_end_index > len(data):
                            packet_end_index = len(data)
                            if full_packet_flag == 1:
                                packet_flag = 1
                        p = NetworkPacket(dst_address, data[packet_begin_index:packet_end_index], packet_ID,
                                          packet_flag)
                        self.out_intf_L[i].put(p.to_byte_S(), True)
                        print('%s: forwarding packet "%s" from interface %d to %d with mtu %d' \
                              % (self, p, i, i, self.out_intf_L[i].mtu))
                        packet_begin_index += mtu_Length
                        packet_end_index += mtu_Length


            except queue.Full:
                print('%s: packet "%s" lost on interface %d' % (self, p, i))
                pass
                
    ## thread target for the host to keep forwarding data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            self.forward()
            if self.stop:
                print (threading.currentThread().getName() + ': Ending')
                return 