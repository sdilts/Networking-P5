from network import Router, Host
from link import Link, LinkLayer
import threading
from time import sleep
import sys
from copy import deepcopy

##configuration parameters
router_queue_size = 0 #0 means unlimited
simulation_time = 15 #give the network sufficient time to execute transfers

if __name__ == '__main__':
    object_L = [] #keeps track of objects, so we can kill their threads at the end
    
    #create network hosts
    host_1 = Host('H1')
    object_L.append(host_1)
    host_2 = Host('H2')
    object_L.append(host_2)
    host_3 = Host('H3')
    object_L.append(host_3)
    
    
    #create routers and routing tables for connected clients (subnets)
    # {in-label : 
    #frwd_tbl_D =  {'H2' : {'dest' : 'H2', 'outlabel': '3', 'intf' : '1'}, '2': {'dest' : 'H1', 'intf' : '0', 'outlabel':'H1'}}     # table used to forward MPLS frames
    frwd_tbl_D = {'6' : {'dest' : 'H3', 'outlabel': '1', 'intf' : '1'}, '5' :{'dest':'H3', 'outlabel':'3', 'intf': '3'}, '1': {'dest' : 'H1', 'intf' : '0', 'outlabel':'H1'}, '3':{'dest':'H2', 'outlabel':'H2', 'intf':'2'}}
	# format of {current_router : {dest1, dest2} }
    encap_tbl_D = {'H1' : {'RA'}, 'H2' : {'RA'}, 'H3': {'RD'} }     # table used to encapsulate network packets into MPLS frames
    decap_tbl_D = {'RA' : {'H1', 'H2'}, 'RD' : {'H3'} }    # table used to decapsulate network packets from MPLS frames
    router_a = Router(name='RA', 
                              intf_capacity_L=[('H1',500),('RB', 500), ('H2', 500), ('RC', 500)],
                              encap_tbl_D = encap_tbl_D,
                              frwd_tbl_D = frwd_tbl_D,
                              decap_tbl_D = decap_tbl_D, 
                              max_queue_size=router_queue_size)
    object_L.append(router_a)
    frwd_tbl_D = {'1' : {'dest' : '1', 'outlabel': '2', 'intf' : '1'}, '2': {'dest' : '2', 'intf' : '0', 'outlabel':'1'}}
    router_b = Router(name='RB', 
                              intf_capacity_L=[('RA', 500),('RD', 100)],
                              encap_tbl_D = encap_tbl_D,
                              frwd_tbl_D = frwd_tbl_D,
                              decap_tbl_D = decap_tbl_D,
                              max_queue_size=router_queue_size)
    object_L.append(router_b)
    
    frwd_tbl_D = {'3' : {'dest' : '3', 'outlabel': '4', 'intf' : '1'}, '4': {'dest' : '4', 'intf' : '0', 'outlabel':'3'}}
    router_c = Router(name='RC', 
                              intf_capacity_L=[('RA', 500),('RD', 100)],
                              encap_tbl_D = encap_tbl_D,
                              frwd_tbl_D = frwd_tbl_D,
                              decap_tbl_D = decap_tbl_D,
                              max_queue_size=router_queue_size)
    object_L.append(router_c)
    
    frwd_tbl_D = {'2' : {'dest' : 'H3', 'outlabel': 'H3', 'intf' : '1'}, '4': {'dest' : 'H3', 'intf' : '1', 'outlabel':'H3'},'H1': {'dest' : 'H1', 'intf' : '0', 'outlabel':'2'}, 'H1P' : {'dest' : 'H1', 'intf' : '2', 'outlabel':'4'},'H2': {'dest' : 'H2', 'intf' : '0', 'outlabel':'2'}, 'H2P' : {'dest' : 'H2', 'intf' : '2', 'outlabel':'4'}}
    router_d = Router(name='RD', 
                              intf_capacity_L=[('RB', 500),('RC', 100), ('H3', 500)],
                              encap_tbl_D = encap_tbl_D,
                              frwd_tbl_D = frwd_tbl_D,
                              decap_tbl_D = decap_tbl_D,
                              max_queue_size=router_queue_size)
    object_L.append(router_d)
    
    #create a Link Layer to keep track of links between network nodes
    link_layer = LinkLayer()
    object_L.append(link_layer)
    
    #add all the links - need to reflect the connectivity in cost_D tables above
    #link_layer.add_link(Link(host_1, 0, router_a, 0))
    #ink_layer.add_link(Link(router_a, 1, router_b, 0))
    #link_layer.add_link(Link(router_b, 1, host_2, 0))
    link_layer.add_link(Link(host_1, 0, router_a, 0))
    link_layer.add_link(Link(router_a, 1, router_b, 0))
    link_layer.add_link(Link(router_b, 1, router_d, 0))

    link_layer.add_link(Link(host_2, 0, router_a, 2))
    link_layer.add_link(Link(router_a, 3, router_c, 0))
    link_layer.add_link(Link(router_c, 1, router_d, 2))
    link_layer.add_link(Link(router_d, 1, host_3, 0))
    
    #start all the objects
    thread_L = []
    for obj in object_L:
        thread_L.append(threading.Thread(name=obj.__str__(), target=obj.run)) 
    
    for t in thread_L:
        t.start()
    
    #create some send events    
    # for i in range(2):
    # priority = i%2
    host_1.udt_send('H3', 'MESSAGE_%d_FROM_H1' % 1, 0)
    host_2.udt_send('H3', 'MESSAGE_%d_FROM_H2' % 2, 1)
    
        
    #give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)

    
    #join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()
        
    print("All simulation threads joined")