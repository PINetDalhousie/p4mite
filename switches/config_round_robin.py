table1 = bfrt.round_robin.pipe.SwitchIngress.ipv4_lpm
entry = table1.entry_with_ipv4_forward(dst_addr=0x0A320001 , dst_mac=0x00154d1211a8, port="132").push()


entry = table1.entry_with_ipv4_forward(dst_addr=0x0A320005 , dst_mac=0xb8599fdf07fa, port="189").push()
entry = table1.entry_with_ipv4_forward(dst_addr=0x0A32000F , dst_mac=0xb8599fdf0800, port="189").push()


entry = table1.entry_with_ipv4_forward(dst_addr=0x0A320006 , dst_mac=0xb8599fdf07ca, port="188").push()
entry = table1.entry_with_ipv4_forward(dst_addr=0x0A320010 , dst_mac=0xb8599fdf07d0, port="188").push()




table2 = bfrt.round_robin.pipe.SwitchIngress.LB
entry = table2.entry_with_LB_forward(dst_addr=0x0A320064).push()


bfrt.round_robin.pipe.circular_queue.add(0, 1)  
bfrt.round_robin.pipe.circular_queue.add(1, 1) 
bfrt.round_robin.pipe.circular_queue.add(2, 1)
bfrt.round_robin.pipe.circular_queue.add(3, 1)
bfrt.round_robin.pipe.circular_queue.add(4, 1)
bfrt.round_robin.pipe.circular_queue.add(5, 0) 


bfrt.round_robin.pipe.queue_iterator.add(0,0)                                                
	