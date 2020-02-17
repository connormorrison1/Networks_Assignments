'''
Created on Oct 12, 2016

@author: mwittie
'''
import network_3 as network
import link_3 as link
import threading
from time import sleep

##configuration parameters
router_queue_size = 0 #0 means unlimited
simulation_time = 1 #give the network sufficient time to transfer all packets before quitting

if __name__ == '__main__':
    object_L = [] #keeps track of objects, so we can kill their threads
    
    #create network nodes
    
    #we need two clients, so we will create the hosts for both of them
    firstClient = network.Host(1)
    object_L.append(firstClient)
    secondClient = network.Host(2)
    object_L.append(secondClient)
    
    #we need two servers, we will create the hosts for both of them
    firstServer = network.Host(3)
    object_L.append(firstServer)
    secondServer = network.Host(4)
    object_L.append(secondServer)
    
    #create the routing tables for the relation shown in the picture.
    #A routes to B and C
    routing_table_A = ['B', 'C']
    #B routes to D
    routing_table_B = ['D']
    #C routes to D
    routing_table_C = ['D']
    #D routes to both the servers
    routing_table_D = ['s_1', 's_2']
    
    #we need four routers
    #A has two interfaces it can route to, so we set the intf_count to be two. Also set the routing options for A to be B and C
    router_A = network.Router(name='A', intf_count=2, max_queue_size=router_queue_size, routing_table = routing_table_A)
    object_L.append(router_A)
    #B has one interface (D) it can route to.
    router_B = network.Router(name='B', intf_count=1, max_queue_size=router_queue_size, routing_table = routing_table_B)
    object_L.append(router_B)
    #C has one interface (D) it can route to.
    router_C = network.Router(name='C', intf_count=1, max_queue_size=router_queue_size, routing_table = routing_table_C)
    object_L.append(router_C)
    #D has two interfaces (server 1 and server 2) it routes to.
    router_D = network.Router(name='D', intf_count=2, max_queue_size=router_queue_size, routing_table = routing_table_D)
    object_L.append(router_D)
    
    #create a Link Layer to keep track of links between network nodes
    link_layer = link.LinkLayer()
    object_L.append(link_layer)
    
    #add all the links
    #link parameters: from_node, from_intf_num, to_node, to_intf_num, mtu
    link_layer.add_link(link.Link(firstClient, 0, router_A, 0, 80))
    #join host2 with router C, and host1 with router B by changing the intf numbers. Changed intf in and out numbers to reflect this.
    #Here we are linking each of the routers and hosts and servers according to the picture show.
    link_layer.add_link(link.Link(secondClient, 0, router_A, 1, 80))
    link_layer.add_link(link.Link(router_A, 0, router_B, 0, 80))
    link_layer.add_link(link.Link(router_A, 1, router_C, 0, 80))
    link_layer.add_link(link.Link(router_C, 0, router_D, 0, 80))
    link_layer.add_link(link.Link(router_B, 0, router_D, 0, 80))
    link_layer.add_link(link.Link(router_D, 0, firstServer, 0, 80))
    link_layer.add_link(link.Link(router_D, 0, secondServer, 0, 80))
    
    #start all the objects
    thread_L = []
    thread_L.append(threading.Thread(name=firstClient.__str__(), target=firstClient.run))
    thread_L.append(threading.Thread(name=secondClient.__str__(), target=secondClient.run))    
    thread_L.append(threading.Thread(name=firstServer.__str__(), target=firstServer.run))
    thread_L.append(threading.Thread(name=secondServer.__str__(), target=secondServer.run))
    thread_L.append(threading.Thread(name=router_A.__str__(), target=router_A.run))
    thread_L.append(threading.Thread(name=router_B.__str__(), target=router_B.run))
    thread_L.append(threading.Thread(name=router_C.__str__(), target=router_C.run))
    thread_L.append(threading.Thread(name=router_D.__str__(), target=router_D.run))

    thread_L.append(threading.Thread(name="Network", target=link_layer.run))
    
    for t in thread_L:
        t.start()
    
    #send the packet
    firstClient.udt_send(4, 'Sample data MORE CHARACTERS')
    
    #give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)
    
    #join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()
        
    print("All simulation threads joined")



# writes to host periodically