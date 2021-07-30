import sys
import os

sys.path.append(os.path.expandvars('$SDE/install/lib/python2.7/site-packages/tofino/'))

from bfrt_grpc import client
from ipaddress import ip_address


def setup_ports():
    for t in bfrt_info.table_dict.keys():
        print(t)

    t=bfrt_info.table_dict['$PORT']
    keys = ['132', '140', '48', '49', '50', '51']

    KeyTuple_list = []

    tkey = []
    for key in keys:
        KeyTuple_list.append(client.KeyTuple(name='DEV_PORT', value=key))
        tkey.append(t.make_key(KeyTuple_list))

    tdata = []
    for i in range(2):
        DataTuple_List = []
        DataTuple_List.append(client.DataTuple(name='SPEED', val='BF_SPEED_40G'))
        DataTuple_List.append(client.DataTuple(name='FEC', val='BF_FEC_TYP_NONE'))
        DataTuple_List.append(client.DataTuple(name='PORT_ENABLE', val=True))
        t.make_data(DataTuple_List)
        tdata.append(DataTuple_List)

    for i in range(4):
        DataTuple_List = []
        DataTuple_List.append(client.DataTuple(name='SPEED', val='BF_SPEED_25G'))
        DataTuple_List.append(client.DataTuple(name='FEC', val='BF_FEC_TYP_NONE'))
        DataTuple_List.append(client.DataTuple(name='PORT_ENABLE', val=True))
        t.make_data(DataTuple_List)
        tdata.append(DataTuple_List)

    return t.entry_add(target=client.Target(), key_list = [tkey], data_list=[tdata])



def add_entries(table, keyname, keys, action_values):
    t=bfrt_info.table_dict[table]

    KeyTuple_list = []

    for key in keys:
        KeyTuple_list.append(client.KeyTuple(name=keyname, value=key))
    tkey=t.make_key(KeyTuple_list)

    DataTuple_List = []
    DataTuple_List.append(client.DataTuple(name='dstAddr', val=action_values[0]))
    DataTuple_List.append(client.DataTuple(name='port', val=int(action_values[1])))
    tdata=t.make_data(DataTuple_List, action_name='ipv4_forward')

    return t.entry_add(target=client.Target(), key_list = [tkey], data_list=[tdata])

def reset():
    GRPC_CLIENT.clear_all_tables()

def close():
    GRPC_CLIENT.__del__()


if __name__ == "__main__":
    GRPC_CLIENT=client.ClientInterface(grpc_addr="localhost:50052", client_id=0,device_id=0)
    bfrt_info=GRPC_CLIENT.bfrt_info_get(p4_name=None)
    GRPC_CLIENT.bind_pipeline_config(p4_name=bfrt_info.p4_name)

    print(bfrt_info.p4_name)

    table = 'SwitchIngress.ipv4_lpm'
    keyname = 'hdr.ipv4.dst_addr'
    addr = ip_address('10.50.0.5')
    keys = [0x00154d1211a8, "132"]
    add_entries(table, keyname, addr, keys)


    addr = ip_address('10.50.0.11')
    keys = [0xb8599fdf07cb, "48"]
    add_entries(table, keyname, addr, keys)
    
    # if (sys.argv[1] == 'hesam'):
    #     dstAddr = [[132], [48]]
    #     dstPort = [['48'], ['132']]
    # elif (sys.argv[1] == 'carson'):
    #     dstAddr = [[132], [140]]
    #     dstPort = [[140], [132]]
    # else:
    #     dstAddr = [['00:15:4d:12:11:a8'], ['00:15:4d:12:12:bf'], ['b8:59:9f:df:07:ca'], ['b8:59:9f:df:07:fb'], ['b8:59:9f:df:07:d0']]
    #     dstPort = [['132'], ['140'], ['48'], ['49'], ['50']]
    #     table = 'SwitchIngress.L2_forward'
    #     keyname = 'hdr.ethernet.dstAddr'


    #setup_ports()
    # for addr, port in zip(dstAddr, dstPort):
    #     add_entries(table, keyname, addr, port)



    close()
