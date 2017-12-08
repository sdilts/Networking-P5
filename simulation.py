from network import Router, Host
from link import Link, LinkLayer
import threading
from time import sleep
import sys
from copy import deepcopy

##configuration parameters
router_queue_size = 0 #0 means unlimited
simulation_time = 10 #give the network sufficient time to execute transfers

if __name__ == '__main__':
    object_L = [] #keeps track of objects, so we can kill their threads at the end
    
    #create network hosts
    host_1 = Host('H1')
    object_L.append(host_1)
    host_2 = Host('H2')
    object_L.append(host_2)
    
    #create routers and routing tables for connected clients (subnets)
    # {in-label : dest and {in_label : outlabel}
    frwd_tbl_D = {'H2' : {'dest' : 'H2', 'outlabel': '3', 'intf' : '1'}, '2': {'dest' : 'H1', 'intf' : '0', 'outlabel':'H1'}}     # table used to forward MPLS frames
	
	# format of {current_router : {dest1, dest2} }
    encap_tbl_D = {'H1' : {'RA'}, 'H2' : {'RB'} }     # table used to encapsulate network packets into MPLS frames
    decap_tbl_D = {'RA' : {'H1'}, 'RB' : {'H2'} }    # table used to decapsulate network packets from MPLS frames
    router_a = Router(name='RA', 
                              intf_capacity_L=[('H1',500),('RB', 500)],
                              encap_tbl_D = encap_tbl_D,
                              frwd_tbl_D = frwd_tbl_D,
                              decap_tbl_D = decap_tbl_D, 
                              max_queue_size=router_queue_size)
    object_L.append(router_a)
    frwd_tbl_D = {'3': {'dest' :'H2','outlabel' :'H2', "intf" : '1'} , 'H1' : {"intf" : '0', 'dest' : 'H1', 'outlabel':'2'}}   
    router_b = Router(name='RB', 
                              intf_capacity_L=[('RA', 500),('H2', 100)],
                              encap_tbl_D = encap_tbl_D,
                              frwd_tbl_D = frwd_tbl_D,
                              decap_tbl_D = decap_tbl_D,
                              max_queue_size=router_queue_size)
    object_L.append(router_b)
    
    #create a Link Layer to keep track of links between network nodes
    link_layer = LinkLayer()
    object_L.append(link_layer)
    
    #add all the links - need to reflect the connectivity in cost_D tables above
    link_layer.add_link(Link(host_1, 0, router_a, 0))
    link_layer.add_link(Link(router_a, 1, router_b, 0))
    link_layer.add_link(Link(router_b, 1, host_2, 0))
    
    
    #start all the objects
    thread_L = []
    for obj in object_L:
        thread_L.append(threading.Thread(name=obj.__str__(), target=obj.run)) 
    
    for t in thread_L:
        t.start()
    
    #create some send events    
    for i in range(5):
        priority = i%2
        host_1.udt_send('H2', 'MESSAGE_%d_FROM_H1' % i, priority)
        
    #give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)

    
    #join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()
        
    print("All simulation threads joined")