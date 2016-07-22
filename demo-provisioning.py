#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python

import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
import cobra.model.fv
import cobra.model.pol

# define alias
fv = cobra.model.fv

# user input (APIC credentials + variables)
apic_ip_addr =  raw_input("IP address of APIC ? ")
apic_login =  raw_input("APIC login ? ")
apic_mdp =  raw_input(apic_login + " password ? ")
my_tenant =  raw_input(" Tenant name ? ")
vlan_start = raw_input(" VLAN start from ? ")
vlan_stop = raw_input(" VLAN stop at ? ")

# log into an APIC and create an object directory
my_session = cobra.mit.session.LoginSession('http://' + apic_ip_addr, apic_login, apic_mdp)
my_dir = cobra.mit.access.MoDirectory(my_session)
my_dir.login()

# the top level object on which operations will be made
topMo = cobra.model.pol.Uni('')

# creation of a new tenant
fvTenant = fv.Tenant(topMo, my_tenant)

# creation of the APN
fvAp = fv.Ap(fvTenant, name='Production-Vlans')

# for each new VLAN
for i in range[int(vlan_start),int(vlan_stop)+1]:
	# creation of the BD's
	fvBD = fv.BD(fvTenant, name='Production-SVI-' + str(i))
	fvRsCtx = fv.RsCtx(fvBD, tnFvCtxName='Production')
	fvSubnet = fv.Subnet(fvBD, ip='10.' + str(i) + '.0.254/24')

	# creation of the EPG's
	fvAEPg = fv.AEPg(fvAp, name='Production-Vlan-' + str(i))
	fvRsDomAtt = fv.RsDomAtt(fvAEPg, tDn='uni/vmmp-VMware/dom-VMware_Domain', primaryEncap='unknown', classPref='encap', instrImedcy='lazy', encap='unknown', resImedcy='immediate')
	fvRsBd = fv.RsBd(fvAEPg, tnFvBDName='Production-SVI-' + str(i))

# commit the generated config to the APIC object directory
config = cobra.mit.request.ConfigRequest()
config.addMo(fvTenant)
my_dir.commit(config)