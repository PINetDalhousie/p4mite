

/* -*- P4_16 -*- */

/*******************************************************************************
 * BAREFOOT NETWORKS CONFIDENTIAL & PROPRIETARY
 *
 * Copyright (c) Intel Corporation
 * SPDX-License-Identifier: CC-BY-ND-4.0
 */


#include <core.p4>
#if __TARGET_TOFINO__ == 2
#include <t2na.p4>
#else
#include <tna.p4>
#endif

#include "headers.p4"
#include "util.p4"

struct metadata_t {
    bit<16> checksum_udp_tmp;
	ipv4_addr_t available_server_meta;
    bit<32> random_number;
}

const bit<16> TYPE_IPV4 = 0x800;


// bit<32> smartnic = 0x0A32000B;

// ---------------------------------------------------------------------------
// Ingress parser
// ---------------------------------------------------------------------------
parser SwitchIngressParser(
    packet_in pkt,
    out header_t hdr,
    out metadata_t ig_md,
    out ingress_intrinsic_metadata_t ig_intr_md) {

        TofinoIngressParser() tofino_parser;
        Checksum() ipv4_checksum;
        Checksum() udp_checksum;
        state start {
            tofino_parser.apply(pkt, ig_intr_md);
            ig_md.checksum_udp_tmp = 0;
            ig_md.available_server_meta = 0;
            transition parse_ethernet;
        }

        state parse_ethernet {
            pkt.extract(hdr.ethernet);
            transition select(hdr.ethernet.ether_type) {
                TYPE_IPV4: parse_ipv4;
                default: accept;
            }
        }

        state parse_ipv4 {
            pkt.extract(hdr.ipv4);
            ipv4_checksum.add(hdr.ipv4);

            udp_checksum.subtract({hdr.ipv4.dst_addr});
            transition select(hdr.ipv4.protocol) {
                IP_PROTOCOLS_UDP : parse_udp;
                default : accept;
            }
        }
        state parse_udp {
            // The tcp checksum cannot be verified, since we cannot compute
            // the payload's checksum.
            pkt.extract(hdr.udp);
            udp_checksum.subtract({hdr.udp.checksum});
            ig_md.checksum_udp_tmp = udp_checksum.get();
            transition accept;
        }
}

// ---------------------------------------------------------------------------
// Ingress
// ---------------------------------------------------------------------------
// Here is the bloom filter

struct pair {
	bit<32> is_valid;
	bit<32> server_address;
}

Register<pair, bit<16>>(65536) bloom_filter;
Register<bit<32>, _>(1) available_server;

control SwitchIngress(
        inout header_t hdr,
        inout metadata_t ig_md,
        in ingress_intrinsic_metadata_t ig_intr_md,
        in ingress_intrinsic_metadata_from_parser_t ig_intr_prsr_md,
        inout ingress_intrinsic_metadata_for_deparser_t ig_intr_dprsr_md,
        inout ingress_intrinsic_metadata_for_tm_t ig_intr_tm_md) {
	
    bit<32> vip = 0x0A320064;
    bit<32> vip2 = 0x0A320065;

    Hash<bit<16>>(HashAlgorithm_t.CRC16) hash;

    action send(ipv4_addr_t dest){
        hdr.ipv4.dst_addr = dest;
    }
 
    Random<bit<32>>() rng;
   
    action get_random() {
       ig_md.random_number = rng.get();
    }
    
    ActionProfile(size = 10) lag_ecmp;
    
    ActionSelector(
       action_profile = lag_ecmp,
        hash           = hash, //this is identity hash -> uses whatever is passed to the selector
        mode           = SelectorMode_t.FAIR,
        max_group_size = 2,
        num_groups     = 1) lag_ecmp_sel;

    table nexthop {
          key = {
              hdr.ipv4.dst_addr      :exact;
              hdr.ipv4.src_addr      : selector;
              hdr.udp.src_port       :selector;}
          actions = { send;}
          size = 16384;
          implementation = lag_ecmp_sel;
      }


    action drop_() {
        ig_intr_dprsr_md.drop_ctl = 0;
    }
    action ipv4_forward(PortId_t port, mac_addr_t dst_mac) {
        ig_intr_tm_md.ucast_egress_port = port;
        hdr.ethernet.dst_addr = dst_mac;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    table ipv4_lpm {
        key = {
            hdr.ipv4.dst_addr: exact;
        }
        actions = { 
            ipv4_forward;
            drop_;
        }
        size = 1024;
        default_action = drop_();
    }

    apply {
        if (hdr.ipv4.isValid()) {
            get_random();
            nexthop.apply(); 
            ipv4_lpm.apply();
        ig_intr_tm_md.bypass_egress = 1w1;
        }
    } 
}

// ---------------------------------------------------------------------------
// Ingress Deparser
// ---------------------------------------------------------------------------
control SwitchIngressDeparser(
        packet_out pkt,
        inout header_t hdr,
        in metadata_t ig_md,
        in ingress_intrinsic_metadata_for_deparser_t ig_intr_dprsr_md) {

    Checksum() ipv4_checksum;
    Checksum() udp_checksum;
    apply {
        hdr.ipv4.hdr_checksum = ipv4_checksum.update(
            {hdr.ipv4.version,
            hdr.ipv4.ihl,
            hdr.ipv4.diffserv,
            hdr.ipv4.total_len,
            hdr.ipv4.identification,
            hdr.ipv4.flags,
            hdr.ipv4.frag_offset,
            hdr.ipv4.ttl,
            hdr.ipv4.protocol,
            hdr.ipv4.src_addr,
            hdr.ipv4.dst_addr});

        hdr.udp.checksum = udp_checksum.update(data = {
            hdr.ipv4.dst_addr,
            ig_md.checksum_udp_tmp
            }, zeros_as_ones = true);
        // UDP specific checksum handling
         
        pkt.emit(hdr.ethernet);
        pkt.emit(hdr.ipv4);
        pkt.emit(hdr.udp);
    }
}

Pipeline(SwitchIngressParser(),
         SwitchIngress(),
         SwitchIngressDeparser(),
         EmptyEgressParser(),
         EmptyEgress(),
         EmptyEgressDeparser()) pipe;

Switch(pipe) main;



