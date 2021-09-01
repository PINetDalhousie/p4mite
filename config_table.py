table1 = bfrt.hesam_switch.pipe.SwitchIngress.ipv4_lpm
entry = table1.entry_with_ipv4_forward(dst_addr=0x0A320005 , port="132").push()
entry = table1.entry_with_ipv4_forward(dst_addr=0x0A32000b , port="48").push()
entry = table1.entry_with_ipv4_forward(dst_addr=0x0A320010 , port="48").push()



table2 = bfrt.hesam_switch.pipe.SwitchIngress.LB
entry = table2.entry_with_LB_forward(dst_addr=0x0A320064).push()
table2.dump(from_hw=True)

bfrt.hesam_switch.pipe.bloom_filter.dump(from_hw=True)

#entry = table2.entry_with_LB_forward(dst_addr=0x0A320064 , dst_mac=0xb8599fdf07cb , dst_ip=0x0A32000b, port="48").push()


table3 = bfrt.hesam_switch.pipe.SwitchIngress.server
entry = table3.entry_with_select_server(dst_addr=0x0A320065 , dst_mac=0xb8599fdf07d1 , dst_ip=0x0A320010, port="48").push()
entry = table3.entry_with_select_server(dst_addr=0x0A320066 , dst_mac=0xb8599fdf07cb , dst_ip=0x0A32000B, port="48").push()
table3.dump(from_hw=True)



ip neighbor add 10.50.0.100 lladdr b8:59:9f:df:07:cb dev enp1s0np0 nud permanent
ip neighbor add 10.50.0.11 lladdr b8:59:9f:df:07:cb dev enp1s0np0 nud permanent
ip neighbor add 10.50.0.16 lladdr b8:59:9f:df:07:d1 dev enp1s0np0 nud permanent


ip neighbor add 10.50.0.5 lladdr 00:15:4d:12:11:a8 dev enp101s0f1 nud permanent
ip neighbor add 10.50.0.101 lladdr b8:59:9f:df:07:cb dev enp101s0f1 nud permanent
ip neighbor add 10.50.0.102 lladdr b8:59:9f:df:07:cb dev enp101s0f1 nud permanent


ip neighbor add 10.50.0.5 lladdr 00:15:4d:12:11:a8 dev p1 nud permanent
