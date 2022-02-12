table1 = bfrt.ecmp_switch.pipe.SwitchIngress.ipv4_lpm
entry = table1.entry_with_ipv4_forward(dst_addr=0x0A320001 , dst_mac=0x00154d1211a8, port="132").push()


entry = table1.entry_with_ipv4_forward(dst_addr=0x0A320005 , dst_mac=0xb8599fdf07fa, port="189").push()
entry = table1.entry_with_ipv4_forward(dst_addr=0x0A32000F , dst_mac=0xb8599fdf0800, port="189").push()


entry = table1.entry_with_ipv4_forward(dst_addr=0x0A320006 , dst_mac=0xb8599fdf07ca, port="188").push()
entry = table1.entry_with_ipv4_forward(dst_addr=0x0A320010 , dst_mac=0xb8599fdf07d0, port="188").push()




lag_ecmp = bfrt.ecmp_switch.pipe.SwitchIngress.lag_ecmp


mbr_base = 200000
dest_1 = mbr_base + 1; lag_ecmp.entry_with_send(dest_1, dest=0x0a320006).push() #Should set IP1


dest_2 = mbr_base + 2; lag_ecmp.entry_with_send(dest_2, dest=0x0a320010).push() #Should set IP2


lag_ecmp_sel = bfrt.ecmp_switch.pipe.SwitchIngress.lag_ecmp_sel






lag_1 = 2000;
lag_ecmp_sel.entry(SELECTOR_GROUP_ID=lag_1
                       ACTION_MEMBER_ID=[dest_1, dest_2],
                       ACTION_MEMBER_STATUS=[True, True]).push()




nexthop = bfrt.ecmp_switch.pipe.SwitchIngress.nexthop
nexthop.entry(dst_addr=0x0A320064, SELECTOR_GROUP_ID=lag_1).push()