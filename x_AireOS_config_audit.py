import os
import yaml
import xlsxwriter
import copy
import pprint
from pprint import pprint
import re
import logging
from logging.handlers import RotatingFileHandler
import argparse
import zipfile

# Declare global variables
#Configure Logging and add file handler
#check if Logs directory exists... if not add it
if not os.path.exists("Logs"):
    os.makedirs("Logs")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logFileHandler=RotatingFileHandler('Logs/runlog.log', mode='a', maxBytes=10*1024*1024,
                                   backupCount=2, encoding=None, delay=0)
logFileHandler.setLevel(logging.DEBUG)
consoleLogHandler=logging.StreamHandler()
consoleLogHandler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logFileHandler.setFormatter(formatter)
consoleLogHandler.setFormatter(formatter)
logger.addHandler(logFileHandler)
logger.addHandler(consoleLogHandler)

def warning(msg):
    logger.warning(msg)


def error(msg):
    logger.error(msg)


def fatal(msg):
    logger.fatal(msg)
    exit(1)

#########################################################################
# Build WLAN List
#
#
#########################################################################

def buildWlanList(input, sysName):
    wlanConfig =[]
    wlanList=[]
    wlanDict={}
    wlanAuthList = []
    wlanAcctList = []
    wlanCompleteDict={}
    wlanConfigStartStop="WLAN Configuration", "Policy Configuration"
    mobilityConfigStartStop="Mobility Anchor List", "802.11u"
    wlanMobDict={}
    wlanMobList=[]
    gatherConfig=False
    wlanConfig=collectConfigSection(input, wlanConfigStartStop)
            # Build WLAN List from WLAN Config output
    logger.info("Building WLAN Config for %s"%sysName)
    for line in wlanConfig:
        if "WLAN Identifier.................................." in line:
            if 'wlanId' in wlanDict:
                if wlanDict['wlanId'] != "":
                    wlanDict['wlanRadiusAcct'] = wlanAcctList
                    wlanDict['wlanRadiusAuth'] = wlanAuthList
                    wlanAcctList = []
                    wlanAuthList = []
                    wlanList.append(copy.copy(wlanDict))
                    wlanDict = {}
            wlanDict['wlanId'] = configLineSplit(line)
        elif "Guest LAN Identifier............................." in line:
            if 'guestLanID' in wlanDict:
                if wlanDict['guestLanID'] != "":
                    wlanDict['wlanRadiusAcct'] = wlanAcctList
                    wlanDict['wlanRadiusAuth'] = wlanAuthList
                    wlanAcctList = []
                    wlanAuthList = []
                    wlanList.append(copy.copy(wlanDict))
                    wlanDict = {}
            wlanDict['guestLanID'] = configLineSplit(line)
            wlanDict['ssid'] = "NA"
        elif "Profile Name....................................." in line:
            wlanDict['profileName'] = configLineSplit(line)
            wlanDict['keyId']=configLineSplit(line)
        elif "Network Name (SSID).............................." in line:
            wlanDict['ssid'] = configLineSplit(line)
        elif "Status..........................................." in line:
            wlanDict['wlanStatus'] = configLineSplit(line)
        elif "MAC Filtering...................................." in line:
            wlanDict['macFilter'] = configLineSplit(line)
        elif "Broadcast SSID..................................." in line:
            wlanDict['broadcastSSID'] = configLineSplit(line)
        elif "AAA Policy Override.............................." in line:
            wlanDict['aaaOverride'] = configLineSplit(line)
        elif "Radius Profiling ............................" in line:
            wlanDict['radiusProfile'] = configLineSplit(line)
        elif "Local Profiling ............................." in line:
            wlanDict['localProfile'] = configLineSplit(line)
        elif "DHCP ......................................." in line:
            if "dhcpProfile" in wlanDict:
                wlanDict['localDhcpProfile'] = configLineSplit(line)
            else:
                wlanDict['radiusDhcpProfile'] = configLineSplit(line)
        elif "HTTP ......................................." in line:
            if "radiusHttpProfile" in wlanDict:
                wlanDict['localHttpProfile'] = configLineSplit(line)
            else:
                wlanDict['radiusHttpProfile'] = configLineSplit(line)
        elif "Average Data Rate................................" in line:
            if "ssidAvgDataRate" in wlanDict:
                wlanDict['clientAvgDataRate'] = configLineSplit(line)
            else:
                wlanDict['ssidAvgDataRate'] = configLineSplit(line)
        elif "Average Realtime Data Rate......................." in line:
            if "ssidRealDataRate" in wlanDict:
                wlanDict['clientRealDataRate'] = configLineSplit(line)
            else:
                wlanDict['ssidRealDataRate'] = configLineSplit(line)
        elif "Burst Data Rate.................................." in line:
            if "ssidBurstDataRate" in wlanDict:
                wlanDict['clientBurstDataRate'] = configLineSplit(line)
            else:
                wlanDict['ssidBurstDataRate'] = configLineSplit(line)
        elif "Burst Realtime Data Rate........................." in line:
            if "ssidBurstRealDataRate" in wlanDict:
                wlanDict['clientBurstRealDataRate'] = configLineSplit(line)
            else:
                wlanDict['ssidBurstRealDataRate'] = configLineSplit(line)
        elif "Radius-NAC State..............................." in line:
            wlanDict['radiusNacState'] = configLineSplit(line)
        elif "SNMP-NAC State................................." in line:
            wlanDict['snmpNacState'] = configLineSplit(line)
        elif "Quarantine VLAN................................" in line:
            wlanDict['quarantineVlan'] = configLineSplit(line)
        elif "Maximum number of Associated Clients............." in line:
            wlanDict['maxAssociated'] = configLineSplit(line)
        elif "Maximum number of Clients per AP Radio..........." in line:
            wlanDict['maxClientsPerRadio'] = configLineSplit(line)
        elif "Number of Active Clients........................." in line:
            wlanDict['maxActiveClients'] = configLineSplit(line)
        elif "Exclusionlist Timeout............................" in line:
            wlanDict['exclusionTimeout'] = configLineSplit(line)
        elif "Session Timeout.................................." in line:
            wlanDict['sessionTimeout'] = configLineSplit(line)
        elif "User Idle Timeout................................" in line:
            wlanDict['userIdleTimeout'] = configLineSplit(line)
        elif "Sleep Client....................................." in line:
            wlanDict['sleepClient'] = configLineSplit(line)
        elif "Sleep Client Timeout............................." in line:
            wlanDict['sleepClientTimeout'] = configLineSplit(line)
        elif "User Idle Threshold.............................." in line:
            wlanDict['userIdleThreshold'] = configLineSplit(line)
        elif "NAS-identifier..................................." in line:
            wlanDict['nasID'] = configLineSplit(line)
        elif "CHD per WLAN....................................." in line:
            wlanDict['wlanChd'] = configLineSplit(line)
        elif "Webauth DHCP exclusion..........................." in line:
            wlanDict['webauthDhcpEx'] = configLineSplit(line)
        elif "Interface........................................" in line:
            wlanDict['wlanInterface'] = configLineSplit(line)
        elif "Multicast Interface.............................." in line:
            wlanDict['wlanMulticastInterface'] = configLineSplit(line)
        elif "WLAN IPv4 ACL...................................." in line:
            wlanDict['wlanIpv4Acl'] = configLineSplit(line)
        elif "WLAN IPv6 ACL...................................." in line:
            wlanDict['wlanIpv6Acl'] = configLineSplit(line)
        elif "WLAN Layer2 ACL.................................." in line:
            wlanDict['wlanL2Acl'] = configLineSplit(line)
        elif "mDNS Status......................................" in line:
            wlanDict['mdnsStatus'] = configLineSplit(line)
        elif "mDNS Profile Name................................" in line:
            wlanDict['mdnsProfileName'] = configLineSplit(line)
        elif "DHCP Server......................................" in line:
            wlanDict['dhcpServer'] = configLineSplit(line)
        elif "DHCP Address Assignment Required................." in line:
            wlanDict['dhcpRequired'] = configLineSplit(line)
        elif "Static IP client tunneling......................." in line:
            wlanDict['staticTunnel'] = configLineSplit(line)
        elif "PMIPv6 Mobility Type............................." in line:
            wlanDict['pmipv6Mobility'] = configLineSplit(line)
        elif "PMIPv6 MAG Profile..........................." in line:
            wlanDict['pmipv6MagProf'] = configLineSplit(line)
        elif "PMIPv6 Default Realm........................." in line:
            wlanDict['pmipv6DefaultRealm'] = configLineSplit(line)
        elif "PMIPv6 NAI Type.............................." in line:
            wlanDict['pmipv6Nai'] = configLineSplit(line)
        elif "PMIPv6 MAG location.........................." in line:
            wlanDict['pmipv6MagLocation'] = configLineSplit(line)
        elif "Quality of Service..............................." in line:
            wlanDict['wlanQos'] = configLineSplit(line)
        elif "Scan Defer Priority.............................." in line:
            wlanDict['scanDeferPriority'] = configLineSplit(line)
        elif "Scan Defer Time.................................." in line:
            wlanDict['scanDeferTime'] = configLineSplit(line)
        elif "WMM.............................................." in line:
            wlanDict['wmm'] = configLineSplit(line)
        elif "WMM UAPSD Compliant Client Support..............." in line:
            wlanDict['wmmUapsd'] = configLineSplit(line)
        elif "Media Stream Multicast-direct...................." in line:
            wlanDict['mediaStreamMulticastDirect'] = configLineSplit(line)
        elif "CCX - AironetIe Support.........................." in line:
            wlanDict['ccxAironetie'] = configLineSplit(line)
        elif "CCX - Gratuitous ProbeResponse (GPR)............." in line:
            wlanDict['ccxGPR'] = configLineSplit(line)
        elif "CCX - Diagnostics Channel Capability............." in line:
            wlanDict['ccxDiag'] = configLineSplit(line)
        elif "Dot11-Phone Mode (7920).........................." in line:
            wlanDict['dot11Phone'] = configLineSplit(line)
        elif "Wired Protocol..................................." in line:
            wlanDict['wiredProtocol'] = configLineSplit(line)
        elif "Passive Client Feature..........................." in line:
            wlanDict['passiveClient'] = configLineSplit(line)
        elif "Peer-to-Peer Blocking Action....................." in line:
            wlanDict['p2pBlock'] = configLineSplit(line)
        elif "Radio Policy....................................." in line:
            wlanDict['radioPolicy'] = configLineSplit(line)
        elif "DTIM period for 802.11a radio...................." in line:
            wlanDict['dtim80211b'] = configLineSplit(line)
        elif "DTIM period for 802.11b radio...................." in line:
            wlanDict['dtim80211b'] = configLineSplit(line)
        elif "Authentication................................" in line:
            wlanAuthList.append(configLineSplit(line))
        elif "Accounting...................................." in line:
            wlanAcctList.append(configLineSplit(line))
        elif "Interim Update............................." in line:
            wlanDict['wlanInterimUpdate'] = configLineSplit(line)
        elif "Interim Update Interval...................." in line:
            wlanDict['wlanInternalUpdateInt'] = configLineSplit(line)
        elif "Framed IPv6 Acct AVP ......................" in line:
            wlanDict['wlanFramedIpv6Acct'] = configLineSplit(line)
        elif "Dynamic Interface............................." in line:
            wlanDict['dynamicInterface'] = configLineSplit(line)
        elif "Dynamic Interface Priority...................." in line:
            wlanDict['dynamicInterfacePriority'] = configLineSplit(line)
        elif "Local EAP Authentication........................." in line:
            wlanDict['wlanLocalEapAuth'] = configLineSplit(line)
        elif "Radius NAI-Realm................................." in line:
            wlanDict['radiusNai'] = configLineSplit(line)
        elif "802.11 Authentication:........................" in line:
            wlanDict['80211buth'] = configLineSplit(line)
        elif "FT Support...................................." in line:
            wlanDict['ftSupport'] = configLineSplit(line)
        elif "Static WEP Keys..............................." in line:
            wlanDict['staticWep'] = configLineSplit(line)
        elif "802.1X...." in line:
            if "wlan8021x" in wlanDict:
                wlanDict['akm8021x'] = configLineSplit(line)
            else:
                wlanDict['wlan8021x']=configLineSplit(line)
        elif "Wi-Fi Protected Access (WPA/WPA2)............." in line:
            wlanDict['wpa'] = configLineSplit(line)
        elif "WPA (SSN IE)..............................." in line:
            wlanDict['wpav1'] = configLineSplit(line)
        elif "WPA2 (RSN IE).............................." in line:
            wlanDict['wpav2'] = configLineSplit(line)
        elif "TKIP Cipher............................." in line:
            wlanDict['tkip'] = configLineSplit(line)
        elif "AES Cipher.............................." in line:
            wlanDict['aes'] = configLineSplit(line)
        elif "FT Reassociation Timeout..................." in line:
            wlanDict['ftReassTimeout'] = configLineSplit(line)
        elif "FT Over-The-DS mode........................" in line:
            wlanDict['ftOverDs'] = configLineSplit(line)
        elif "GTK Randomization.........................." in line:
            wlanDict['gtkRandom'] = configLineSplit(line)
        elif "SKC Cache Support.........................." in line:
            wlanDict['skcCache'] = configLineSplit(line)
        elif "CCKM TSF Tolerance........................." in line:
            wlanDict['cckmTsfTolerance'] = configLineSplit(line)
        elif "WAPI.........................................." in line:
            wlanDict['wapi'] = configLineSplit(line)
        elif "Wi-Fi Direct policy configured................" in line:
            wlanDict['wifiDirect'] = configLineSplit(line)
        elif "EAP-Passthrough..............................." in line:
            wlanDict['eapPassthrough'] = configLineSplit(line)
        elif "CKIP ........................................." in line:
            wlanDict['ckip'] = configLineSplit(line)
        elif "Web Based Authentication......................" in line:
            wlanDict['webAuth'] = configLineSplit(line)
        elif "Web Authentication Timeout...................." in line:
            wlanDict['webAuthTimeout'] = configLineSplit(line)
        elif "Web-Passthrough..............................." in line:
            wlanDict['webPassthrough'] = configLineSplit(line)
        elif "Mac-auth-server..............................." in line:
            wlanDict['macAuthServer'] = configLineSplit(line)
        elif "Web-portal-server............................." in line:
            wlanDict['webPortalServer'] = configLineSplit(line)
        elif "Conditional Web Redirect......................" in line:
            wlanDict['condWebRedirect'] = configLineSplit(line)
        elif "Splash-Page Web Redirect......................" in line:
            wlanDict['splashWebRedirect'] = configLineSplit(line)
        elif "Auto Anchor..................................." in line:
            wlanDict['autoAnchor'] = configLineSplit(line)
        elif "FlexConnect Local Switching..................." in line:
            wlanDict['flexLocalSwitch'] = configLineSplit(line)
        elif "FlexConnect Central Association..............." in line:
            wlanDict['flexCentralAssociation'] = configLineSplit(line)
        elif "flexconnect Central Dhcp Flag................." in line:
            wlanDict['flexCentralDhcp'] = configLineSplit(line)
        elif "flexconnect nat-pat Flag......................" in line:
            wlanDict['flexNatPat'] = configLineSplit(line)
        elif "flexconnect Dns Override Flag................." in line:
            wlanDict['flexDnsOverride'] = configLineSplit(line)
        elif "flexconnect PPPoE pass-through................" in line:
            wlanDict['flexPpoe'] = configLineSplit(line)
        elif "flexconnect local-switching IP-source-guar...." in line:
            wlanDict['flexLocalSwSourceGuard'] = configLineSplit(line)
        elif "FlexConnect Vlan based Central Switching ....." in line:
            wlanDict['flexVlanCentralSwitch'] = configLineSplit(line)
        elif "FlexConnect Local Authentication.............." in line:
            wlanDict['flexLocalAuth'] = configLineSplit(line)
        elif "FlexConnect Learn IP Address.................." in line:
            wlanDict['flexLearnIp'] = configLineSplit(line)
        elif "Client MFP...................................." in line:
            wlanDict['clientMfp'] = configLineSplit(line)
        elif "PMF..........................................." in line:
            wlanDict['pmf'] = configLineSplit(line)
        elif "PMF Association Comeback Time................." in line:
            wlanDict['pmfAssocComebackTime'] = configLineSplit(line)
        elif "PMF SA Query RetryTimeout....................." in line:
            wlanDict['pmfSaQuery'] = configLineSplit(line)
        elif "Tkip MIC Countermeasure Hold-down Timer......." in line:
            wlanDict['tkipHoldDown'] = configLineSplit(line)
        elif "Eap-params...................................." in line:
            wlanDict['eapParams'] = configLineSplit(line)
        elif "AVC Visibilty...................................." in line:
            wlanDict['avcVisibiilty'] = configLineSplit(line)
        elif "AVC Profile Name................................." in line:
            wlanDict['avcProfileName'] = configLineSplit(line)
        elif "Flow Monitor Name................................" in line:
            wlanDict['flowMonitor'] = configLineSplit(line)
        elif "Split Tunnel................................." in line:
            wlanDict['splitTunnel'] = configLineSplit(line)
        elif "Call Snooping...................................." in line:
            wlanDict['callSnoop'] = configLineSplit(line)
        elif "Roamed Call Re-Anchor Policy....................." in line:
            wlanDict['roamCallReanchor'] = configLineSplit(line)
        elif "SIP CAC Fail Send-486-Busy Policy................" in line:
            wlanDict['sipCacFailBusy'] = configLineSplit(line)
        elif "SIP CAC Fail Send Dis-Association Policy........." in line:
            wlanDict['sipCacFailDisass'] = configLineSplit(line)
        elif "KTS based CAC Policy............................." in line:
            wlanDict['cacKts'] = configLineSplit(line)
        elif "Assisted Roaming Prediction Optimization........." in line:
            wlanDict['assistRoam'] = configLineSplit(line)
        elif "802.11k Neighbor List............................" in line:
            wlanDict['80211kNeighbor'] = configLineSplit(line)
        elif "802.11k Neighbor List Dual Band.................." in line:
            wlanDict['80211kNeighborDual'] = configLineSplit(line)
        elif "802.11v Directed Multicast Service..............." in line:
            wlanDict['80211vDirectMulticast'] = configLineSplit(line)
        elif "802.11v BSS Max Idle Service....................." in line:
            wlanDict['80211vBssMax'] = configLineSplit(line)
        elif "DMS" in line:
            wlanDict['dms']=configLineSplit(line)
        elif "Band Select......................................" in line:
            wlanDict['bandSelect'] = configLineSplit(line)
        elif "Load Balancing..................................." in line:
            wlanDict['wlanLoadBalance'] = configLineSplit(line)
        elif "Multicast Buffer................................." in line:
            wlanDict['multicastBuffer'] = configLineSplit(line)
        elif "Universal Ap Admin..............................." in line:
            wlanDict['unversalApAdmin'] = configLineSplit(line)
    wlanDict['wlanRadiusAcct'] = wlanAcctList
    wlanDict['wlanRadiusAuth'] = wlanAuthList
    wlanList.append(copy.copy(wlanDict))
    wlanCompleteDict['wlans']=wlanList
    return wlanCompleteDict

#########################################################################
#########################################################################
# Build System Inventory
#
#
#########################################################################
def buildSysInventory(input,sysName):
    inventoryDict={}
    inventoryDetailDict={}
    #set start stop point for config sections
    inventoryConfigStartStop="System Inventory", "System Information"
    #add System Inventory section to list
    inventoryConfig=collectConfigSection(input,inventoryConfigStartStop)
    # Build Inventory from Input
    logger.info("Building System Inventory for %s" % sysName)
    for line in inventoryConfig:
        # Populate values in System Inventory Section of Config
        if 'NAME: ' in line:
            inventoryDetailDict['name']=line.strip().split()[1]
            inventoryDetailDict['descrip']=" ".join(line.strip().split()[4:])
        elif 'PID: ' in line:
            inventoryDetailDict['pid'] = line.strip().split()[1]
            inventoryDetailDict['vid'] = (line.strip().split()[3]).replace(",", "")
            inventoryDetailDict['sn'] = (line.strip().split()[5])
        elif "Burned-in MAC Address............................" in line:
            inventoryDetailDict['burnMac'] = line.strip().split()[3]
        elif "Power Supply 1..................................." in line:
            inventoryDetailDict['ps1Avail'] = line.strip().split()[3]
            inventoryDetailDict['ps1Status'] = line.strip().split()[4]
        elif "Power Supply 2..................................." in line:
            inventoryDetailDict['ps2Avail'] = line.strip().split()[3]
            inventoryDetailDict['ps2Status'] = line.strip().split()[4]
        elif "Maximum number of APs supported.................." in line:
            inventoryDetailDict['maxAp'] = line.strip().split()[5]
    inventoryDict['sysInventory']=inventoryDetailDict
    return inventoryDict
#########################################################################
# Build NTP Server List
#
#
#########################################################################
def buildNtpServer(input, sysName):
    ntpDict={}
    ntpFinal={}
    ntpList=[]
    ntpServerDetailDict={}
    # set start stop point for config sections
    ntpConfigStartStop="NTP Servers", "Redundancy Information"
    # add NTP info to List
    ntpConfig = (collectConfigSection(input, ntpConfigStartStop))
    # Build Inventory from Input
    logger.info("Building NTP Config for %s" % sysName)
    for line in ntpConfig:
        if "NTP Polling Interval" in line:
           ntpDict['ntpPollingInt']=configLineSplit(line)
        if "NTP Polling Interval....." not in line:
            if "NTP Servers" not in line:
                if "Index" not in line:
                    if "---" not in line:
                        if len(line.split()) > 4:
                            ntpServerDetailDict['ntpIndex']=line.strip().split()[0]
                            ntpServerDetailDict['ntpKeyIndex'] = line.strip().split()[1]
                            ntpServerDetailDict['ntpServerIp'] = line.strip().split()[2]
                            ntpServerDetailDict['ntpStatus'] = line.strip().split()[3]
                            #ntpServerDetailDict['ntpAuthStatus'] = line.strip().split()[5]
                            ntpList.append(copy.copy(ntpServerDetailDict))
                            ntpServerDetailDict={}
    ntpDict['ntpServers']=ntpList
    ntpFinal['ntpConfig']=ntpDict
    return ntpFinal


#########################################################################
# Build System Information
#
#
#########################################################################
def buildSysInfo(input):
    infoDict={}
    infoDetailDict={}
    # set start stop point for config sections
    infoConfigStartStop="System Information", "Redundancy Information"
    # add System Information section to list
    infoConfig=(collectConfigSection(input,infoConfigStartStop))
    # Build System Information from Input
    for line in infoConfig:
        if "Manufacturer's Name.............................. " in line:
            infoDetailDict['manufacturer']=configLineSplit(line)
        elif "Product Name....................................." in line:
            infoDetailDict['productName']=configLineSplit(line)
        elif "Product Version.................................." in line:
            infoDetailDict['prodVer'] = configLineSplit(line)
        elif "Bootloader Version..............................." in line:
            infoDetailDict['bootLoad'] = configLineSplit(line)
        elif "Field Recovery Image Version....................." in line:
            infoDetailDict['fieldRecovery'] = configLineSplit(line)
        elif "Firmware Version................................." in line:
            infoDetailDict['firmware'] = configLineSplit(line)
        elif "Build Type......................................." in line:
            infoDetailDict['buildType'] = configLineSplit(line)
        elif "System Name......................................" in line:
            infoDetailDict['sysName'] = configLineSplit(line)
        elif "System Location.................................. " in line:
            infoDetailDict['sysLocation'] = configLineSplit(line)
        elif "System Contact..................................." in line:
            infoDetailDict['sysContact'] = configLineSplit(line)
        elif "System ObjectID.................................." in line:
            infoDetailDict['sysOid'] = configLineSplit(line)
        elif "Redundancy Mode.................................." in line:
            infoDetailDict['redundModeStatus'] = configLineSplit(line)
        elif "IP Address......................................." in line:
            infoDetailDict['ipAddress'] = configLineSplit(line)
        elif "IPv6 Address....................................." in line:
            infoDetailDict['ipv6Address'] = configLineSplit(line)
        elif "Last Reset......................................." in line:
            infoDetailDict['lastReset'] = configLineSplit(line)
        elif "System Up Time..................................." in line:
            infoDetailDict['sysUp'] = configLineSplit(line)
        elif "System Timezone Location........................." in line:
            infoDetailDict['sysTimezone'] = configLineSplit(line)
        elif "System Stats Realtime Interval..................." in line:
            infoDetailDict['sysStatsReal'] = configLineSplit(line)
        elif "System Stats Normal Interval....................." in line:
            infoDetailDict['sysStatsNorm'] = configLineSplit(line)
        elif "Configured Country..............................." in line:
            infoDetailDict['country'] = configLineSplit(line)
        elif "Operating Environment............................" in line:
            infoDetailDict['operEnviron'] = configLineSplit(line)
        elif "Internal Temp Alarm Limits......................." in line:
            infoDetailDict['internalTempAlarm'] = configLineSplit(line)
        elif "Internal Temperature............................." in line:
            infoDetailDict['internalTemp'] = configLineSplit(line)
        elif "External Temperature............................." in line:
            infoDetailDict['externalTemp'] = configLineSplit(line)
        elif "Fan Status......................................." in line:
            infoDetailDict['fanStatus'] = configLineSplit(line)
        elif "State of 802.11b Network........................." in line:
            infoDetailDict['network80211bStatus'] = configLineSplit(line)
        elif "State of 802.11a Network........................." in line:
            infoDetailDict['network80211aStatus'] = configLineSplit(line)
        elif "Number of WLANs.................................." in line:
            infoDetailDict['wlanCount'] = configLineSplit(line)
        elif "Number of Active Clients........................." in line:
            infoDetailDict['clientCount'] = configLineSplit(line)
        elif "Burned-in MAC Address............................ " in line:
            infoDetailDict['macAddress'] = configLineSplit(line)
        elif "Power Supply 1..................................." in line:
            infoDetailDict['ps1'] = configLineSplit(line)
        elif "Power Supply 2..................................." in line:
            infoDetailDict['ps2'] =configLineSplit(line)
        elif "Maximum number of APs supported.................." in line:
            infoDetailDict['maxAps'] = configLineSplit(line)
        elif "System Nas-Id...................................." in line:
            infoDetailDict['sysNasid'] = configLineSplit(line)
        elif "WLC MIC Certificate Types........................" in line:
            infoDetailDict['wlcMic'] = configLineSplit(line)
    infoDict['sysInfo']=infoDetailDict
    return infoDict
#########################################################################
# Build Redundancy Config
#
#
#########################################################################
def buildRedundancyInfo(input,sysName):
    redundantDict={}
    redundantDetailDict={}
    # set start stop point for config sections
    redundantConfigStartStop="Redundancy Information", "AP Bundle Information"
    # add System Information section to list
    redundantConfig=collectConfigSection(input,redundantConfigStartStop)
    # Build System Information from Input
    logger.info("Building Redundancy Info for %s" % sysName)
    for line in redundantConfig:
        if "Redundancy Mode ................................." in line:
            redundantDetailDict['redundMode'] = configLineSplit(line)
        elif "Local State......................................" in line:
            redundantDetailDict['localState'] = configLineSplit(line)
        elif "Peer State......................................." in line:
            redundantDetailDict['peerState'] = configLineSplit(line)
        elif "Unit............................................." in line:
            redundantDetailDict['unit'] = configLineSplit(line)
        elif "Unit ID.........................................." in line:
            redundantDetailDict['unitId'] = configLineSplit(line)
        elif "Redunadancy State................................" in line:
            redundantDetailDict['redundState'] = configLineSplit(line)
        elif "Mobility MAC....................................." in line:
            redundantDetailDict['mobilityMac'] = configLineSplit(line)
        elif "Redundancy Management IP Address................." in line:
            redundantDetailDict['redundManageIp'] = configLineSplit(line)
        elif "Peer Redundancy Management IP Address............" in line:
            redundantDetailDict['peerRedundManageIp'] = configLineSplit(line)
        elif "Redundancy Port IP Address......................." in line:
            redundantDetailDict['redundPortIp'] = configLineSplit(line)
        elif "Peer Redundancy Port IP Address.................." in line:
            redundantDetailDict['peerRedundPortIp'] = configLineSplit(line)
    redundantDict['redundancyConfig']=redundantDetailDict
    return redundantDict
#########################################################################
# Build AP Image Version Info
#
#
#########################################################################
def buildApBundleInfo(input,sysName):
    apBundleDictPri={}
    apBundleDictSec = {}
    apBundleDict={}
    # set start stop point for config sections
    apBundleConfigPriStartStop="Primary AP Image", "Secondary AP Image"
    apBundleConfigSecStartStop="Secondary AP Image", "Switch Configuration"
    # add Ap Bundle section to list
    apBundleConfigPri = collectConfigSection(input,apBundleConfigPriStartStop)
    apBundleConfigSec=collectConfigSection(input,apBundleConfigSecStartStop)
    apBundlePriList=[]
    apBundleSecList = []
    # Build System Information from Input
    logger.info("Building Ap Bundle Info for %s" % sysName)
    for line in apBundleConfigPri:
        if "Primary AP Image" not in line:
            if len(line.split()) > 1:
                if "version.info" not in line:
                    if "---" not in line:
                        apBundleDictPri['apImageName']=line.split()[0]
                        apBundleDictPri['apImageSize']=line.split()[1]
                        apBundlePriList.append(copy.copy(apBundleDictPri))
    apBundleDict['primaryApImages']=apBundlePriList
    for line in apBundleConfigSec:
        if "Secondary AP Image" not in line:
            if "---" not in line:
                if "version.info" not in line:
                    if len(line.split()) > 1:
                        apBundleDictSec['apImageName']=line.split()[0]
                        apBundleDictSec['apImageSize']=line.split()[1]
                        apBundleSecList.append(copy.copy(apBundleDictSec))
    apBundleDict['secondaryApImages'] = apBundleSecList
    apBundleDict['apImageBundle']=apBundleDict
    return apBundleDict

#########################################################################
# Build Switch Config
#
#
#########################################################################
def buildSwitchConfig(input,sysName):
    switchConfig=[]
    switchDict={}
    switchDetailDict={}
    # set start stop point for Switch Config
    switchConfigStartStop="Switch Configuration", "Network Information"
    # add Switch Config
    switchConfig = collectConfigSection(input,switchConfigStartStop)
    # Build System Configuration from Input
    logger.info("Building Switch Configuration for %s" % sysName)
    for line in switchConfig:
        if "802.3x Flow Control Mode......................... " in line:
            switchDetailDict['flowControl'] = configLineSplit(line)
        elif "FIPS prerequisite features....................... " in line:
            switchDetailDict['fips'] = configLineSplit(line)
        elif "WLANCC prerequisite features..................... " in line:
            switchDetailDict['wlancc'] = configLineSplit(line)
        elif "UCAPL prerequisite features...................... " in line:
            switchDetailDict['ucapl'] = configLineSplit(line)
        elif "DTLS WLC MIC .................................... " in line:
            switchDetailDict['dtlsMic'] = configLineSplit(line)
        elif "secret obfuscation............................... " in line:
            switchDetailDict['secretOb'] = configLineSplit(line)
        elif "   case-check.................................... " in line:
            switchDetailDict['caseCheck'] = configLineSplit(line)
        elif "   consecutive-check............................. " in line:
            switchDetailDict['consecCheck'] = configLineSplit(line)
        elif "   default-check................................. " in line:
            switchDetailDict['defaultCheck'] = configLineSplit(line)
        elif "   username-check................................ " in line:
            switchDetailDict['usernameCheck'] = configLineSplit(line)
        elif "   position-check................................ " in line:
            switchDetailDict['postionCheck'] = configLineSplit(line)
        elif "   case-digit-check.............................. " in line:
            switchDetailDict['caseDigitCheck'] = configLineSplit(line)
        elif "   Min. Password length.......................... " in line:
            switchDetailDict['minPass'] = configLineSplit(line)
        elif "   Min. Upper case chars......................... " in line:
            switchDetailDict['minUpper'] = configLineSplit(line)
        elif "   Min. Lower case chars......................... " in line:
            switchDetailDict['minLower'] = configLineSplit(line)
        elif "   Min. Digits chars............................. " in line:
            switchDetailDict['minDigits'] = configLineSplit(line)
        elif "   Min. Special chars............................ " in line:
            switchDetailDict['minSpecial'] = configLineSplit(line)
        elif "   Password Lifetime [days]...................... " in line:
            if "passwordLifetime" in switchDetailDict:
                switchDetailDict['snmpPassLifetime'] = configLineSplit(line)
            else:
                switchDetailDict['passwordLifetime'] = configLineSplit(line)
        elif "   Password Lockout.............................. " in line:
            if "passwordLock" in switchDetailDict:
                switchDetailDict['snmpPasswordLock'] = configLineSplit(line)
            else:
                switchDetailDict['passwordLock'] = configLineSplit(line)

        elif "   Lockout Attempts.............................. " in line:
            if "passLockAttempts" in switchDetailDict:
                switchDetailDict['snmpPassLockAttempts'] = configLineSplit(line)
            else:
                switchDetailDict['passLockAttempts'] = configLineSplit(line)
        elif "   Lockout Timeout [mins]........................ " in line:
            if "passwordLockTimeout" in switchDetailDict:
                switchDetailDict['snmpLockTimeout'] = configLineSplit(line)
            else:
                switchDetailDict['passwordLockTimeout'] = configLineSplit(line)
    switchDict['switchDetail']=switchDetailDict
    return switchDict

#########################################################################
# Build Network Info
#
#
#########################################################################
def buildNetworkInfo(input, sysName):
    networkDict={}
    networkDetailDict={}
    # set start stop point for config sections
    networkConfigStartStop="Network Information", "Port Summary"
    # Build Network Information from Input
    networkConfig=collectConfigSection(input,networkConfigStartStop)
    logger.info("Building Network Information for %s" % sysName)
    for line in networkConfig:
        if "RF-Network Name............................." in line:
            networkDetailDict['rfNetwork'] = configLineSplit(line)
        elif "Web Mode...................................." in line:
            networkDetailDict['webMode'] = configLineSplit(line)
        elif "Secure Web Mode............................." in line:
            networkDetailDict['secureWebMode'] = configLineSplit(line)
        elif "Secure Web Mode Cipher-Option High.........." in line:
            networkDetailDict['secureWebModeHigh'] = configLineSplit(line)
        elif "Secure Web Mode Cipher-Option SSLv2........." in line:
            networkDetailDict['secureWebModeSslv2'] = configLineSplit(line)
        elif "Secure Web Mode RC4 Cipher Preference......." in line:
            networkDetailDict['secureWebModeRc4'] = configLineSplit(line)
        elif "Secure Web Mode SSL Protocol................" in line:
            networkDetailDict['secureWebModeSecProt'] = configLineSplit(line)
        elif "OCSP........................................" in line:
            networkDetailDict['oscp'] = configLineSplit(line)
        elif "OCSP responder URL.........................." in line:
        	networkDetailDict['oscpResponderUrl'] = configLineSplit(line)
        elif "Secure Shell (ssh).........................." in line:
            networkDetailDict['ssh'] = configLineSplit(line)
        elif "Telnet......................................" in line:
            networkDetailDict['telnet'] = configLineSplit(line)
        elif "Ethernet Multicast Forwarding..............." in line:
            networkDetailDict['ethernetMulticast'] = configLineSplit(line)
        elif "Ethernet Broadcast Forwarding..............." in line:
            networkDetailDict['ethernetBroadcast'] = configLineSplit(line)
        elif "IPv4 AP Multicast/Broadcast Mode............" in line:
            networkDetailDict['ipv4ApFowardMode'] = line.strip().split()[4]
            if networkDetailDict['ipv4ApFowardMode']== "Multicast":
                    networkDetailDict['ipv4multicastIp']= line.strip().split()[7]
        elif "IPv6 AP Multicast/Broadcast Mode............" in line:
            networkDetailDict['ipv6ApFowardMode'] = line.strip().split()[4]
            if networkDetailDict['ipv6ApFowardMode']== "Multicast":
                    networkDetailDict['ipv6multicastIp']= line.strip().split()[7]
        elif "IGMP snooping..............................." in line:
            networkDetailDict['igmpSnoop'] = configLineSplit(line)
        elif "IGMP timeout................................" in line:
            networkDetailDict['igmpTimeout'] = configLineSplit(line)
        elif "IGMP Query Interval........................." in line:
            networkDetailDict['igmpQuery'] = configLineSplit(line)
        elif "MLD snooping................................" in line:
            networkDetailDict['mldSnoop'] = configLineSplit(line)
        elif "MLD timeout................................." in line:
            networkDetailDict['mldTimeout'] = configLineSplit(line)
        elif "MLD query interval.........................." in line:
            networkDetailDict['mldQuery'] = configLineSplit(line)
        elif "User Idle Timeout..........................." in line:
            networkDetailDict['userIdleTimeout'] = configLineSplit(line)
        elif "ARP Idle Timeout............................" in line:
            networkDetailDict['arpIdleTimeout'] = configLineSplit(line)
        elif "Cisco AP Default Master....................." in line:
            networkDetailDict['apDefaultMaster'] = configLineSplit(line)
        elif "AP Join Priority............................" in line:
            networkDetailDict['apJoinPriority'] = configLineSplit(line)
        elif "Mgmt Via Wireless Interface................." in line:
            networkDetailDict['mgmtViaWireless'] = configLineSplit(line)
        elif "Mgmt Via Dynamic Interface.................." in line:
            networkDetailDict['mgmtViaDynamic'] = configLineSplit(line)
        elif "Bridge MAC filter Config...................." in line:
            networkDetailDict['bridgeMacFilter'] = configLineSplit(line)
        elif "Bridge Security Mode........................" in line:
            networkDetailDict['bridgeSecMode'] = configLineSplit(line)
        elif "Mesh Full Sector DFS........................" in line:
            networkDetailDict['meshFullSector'] = configLineSplit(line)
        elif "AP Fallback ................................" in line:
            networkDetailDict['apFallback'] = configLineSplit(line)
        elif "Web Auth CMCC Support ......................" in line:
            networkDetailDict['webAuthCmcc'] = configLineSplit(line)
        elif "Web Auth Redirect Ports ...................." in line:
            networkDetailDict['webAuthRedirectPort'] = configLineSplit(line)
        elif "Web Auth Proxy Redirect  ..................." in line:
            networkDetailDict['webAuthProxyRedirect'] = configLineSplit(line)
        elif "Web Auth Captive-Bypass   .................." in line:
            networkDetailDict['webAuthCaptiveBypass'] = configLineSplit(line)
        elif "Web Auth Secure Web  ......................." in line:
            networkDetailDict['webAuthSecureWeb'] = configLineSplit(line)
        elif "Web Auth Secure Redirection  ..............." in line:
            networkDetailDict['webAuthSecureWebRedir'] = configLineSplit(line)
        elif "Fast SSID Change ..........................." in line:
            networkDetailDict['fastSSID'] = configLineSplit(line)
        elif "AP Discovery - NAT IP Only ................." in line:
            networkDetailDict['apDiscoveryNat'] = configLineSplit(line)
        elif "IP/MAC Addr Binding Check .................." in line:
            networkDetailDict['ipMacBindingCheck'] = configLineSplit(line)
        elif "Link Local Bridging Status ................." in line:
            networkDetailDict['linkLocalBridge'] = configLineSplit(line)
        elif "CCX-lite status ............................" in line:
            networkDetailDict['ccxLiteStatus'] = configLineSplit(line)
        elif "oeap-600 dual-rlan-ports ..................." in line:
            networkDetailDict['oeapDualRlanPorts'] = configLineSplit(line)
        elif "oeap-600 local-network ....................." in line:
            networkDetailDict['oeapLocalNetwork'] = configLineSplit(line)
        elif "oeap-600 Split Tunneling (Printers)........." in line:
            networkDetailDict['oeapSplitTunnel'] = configLineSplit(line)
        elif "WebPortal Online Client ...................." in line:
            networkDetailDict['webPortalOnlineClient'] = configLineSplit(line)
        elif "WebPortal NTF_LOGOUT Client ................" in line:
            networkDetailDict['webPortalNtfLogout'] = configLineSplit(line)
        elif "mDNS snooping..............................." in line:
            networkDetailDict['mdnsSnoop'] = configLineSplit(line)
        elif "mDNS Query Interval........................." in line:
            networkDetailDict['mdnsQueryInterval'] = configLineSplit(line)
        elif "Web Color Theme............................." in line:
            networkDetailDict['webColor'] = configLineSplit(line)
        elif "Capwap Prefer Mode.........................." in line:
            networkDetailDict['capwapPreferMode'] = configLineSplit(line)
        elif "Client ip conflict detection (DHCP) ........" in line:
            networkDetailDict['clientIpConflictDetect'] = configLineSplit(line)
    networkDict['networkInfo']=networkDetailDict
    return networkDict
#########################################################################
# Build Port Summary
#
#
#########################################################################
def buildPortSummary(input,sysName):
    portList=[]
    portDict={}
    portDetailDict={}
    wlcPortStartStop="Port Summary","AP Summary"
    wlcPort = collectConfigSection(input, wlcPortStartStop)
    logger.info("Building Physical Port Summary for %s" % sysName)
    for line in wlcPort:
        if "Port Summary" not in line:
            if "SFPType" not in line:
                if "Physical" not in line:
                    if "---" not in line:
                        if len(line.split()) > 10:
                            portDetailDict['portNumber']=line.strip().split()[0]
                            portDetailDict['portType'] = line.strip().split()[1]
                            portDetailDict['portStpState'] = line.strip().split()[2]
                            portDetailDict['portAdminMode'] = line.strip().split()[3]
                            portDetailDict['physicalMode'] = line.strip().split()[4]
                            portDetailDict['portPhysicalStatus'] = line.strip().split()[5]
                            portDetailDict['portLinkStatus'] = line.strip().split()[6]
                            portDetailDict['portLinkTrap'] = line.strip().split()[7]
                            portDetailDict['portPoe'] = line.strip().split()[8]
                            portDetailDict['portSfpType'] = " ".join(line.strip().split()[9:])
                            portDetailDict['keyId']=portDetailDict['portNumber']
                            portList.append(copy.copy(portDetailDict))
                            portDetailDict={}
    portDict['portSummary']=portList
    return portDict

#########################################################################
# Build Interfaces
#
#
#########################################################################
def buildInterfaces(input,sysName):
    interfaceList=[]
    interfaceDict={}
    interfaceDetailDict={}
    interfaceConfigStartStop="Interface Configuration","Interface Group Configuration"
    interfaceConfig = collectConfigSection(input, interfaceConfigStartStop)
    logger.info("Building Interface List for %s" % sysName)
    for line in interfaceConfig:
        if "Interface Name..................................." in line:
            if "interfaceName"in interfaceDetailDict:
                interfaceList.append(copy.copy(interfaceDetailDict))
                interfaceDetailDict={}
            interfaceDetailDict['interfaceName'] = configLineSplit(line)
            interfaceDetailDict['keyId']=interfaceDetailDict['interfaceName']
        elif "MAC Address......................................" in line:
            interfaceDetailDict['interfaceMac'] = configLineSplit(line)
        elif "IP Address......................................." in line:
            interfaceDetailDict['interfaceIp'] = configLineSplit(line)
        elif "IP Netmask......................................." in line:
            interfaceDetailDict['interfaceNetmask'] = configLineSplit(line)
        elif "IP Gateway......................................." in line:
            interfaceDetailDict['interfaceGateway'] = configLineSplit(line)
        elif "External NAT IP State............................" in line:
            interfaceDetailDict['interfaceExNatIpState'] = configLineSplit(line)
        elif "External NAT IP Address.........................." in line:
            interfaceDetailDict['interfaceExNatIp'] = configLineSplit(line)
        elif "VLAN............................................." in line:
            interfaceDetailDict['interfaceVlan'] = configLineSplit(line)
        elif "Quarantine-vlan.................................." in line:
            interfaceDetailDict['interfaceQuarantineVlan'] = configLineSplit(line)
        elif "NAS-Identifier..................................." in line:
            interfaceDetailDict['interfaceNasId'] = configLineSplit(line)
        elif "Active Physical Port............................." in line:
            interfaceDetailDict['interfaceActivePort'] = configLineSplit(line)
        elif "Primary Physical Port............................" in line:
            interfaceDetailDict['interfacePrimaryPort'] = configLineSplit(line)
        elif "Backup Physical Port............................." in line:
            interfaceDetailDict['interfaceBackupPort'] = configLineSplit(line)
        elif "DHCP Proxy Mode.................................." in line:
            interfaceDetailDict['interfaceDhcpProxyMode'] = configLineSplit(line)
        elif "Primary DHCP Server.............................." in line:
            interfaceDetailDict['interfacePrimaryDhcp'] = configLineSplit(line)
        elif "Secondary DHCP Server............................" in line:
            interfaceDetailDict['interfaceSecondaryDhcp'] = configLineSplit(line)
        elif "DHCP Option 82..................................." in line:
            interfaceDetailDict['interfaceDhcpOption82'] = configLineSplit(line)
        elif "DHCP Option 82 bridge mode insertion............." in line:
            interfaceDetailDict['interfaceDhcpOption82Bridge'] = configLineSplit(line)
        elif "IPv4 ACL........................................." in line:
            interfaceDetailDict['interfaceIpv4Acl'] = configLineSplit(line)
        elif "mDNS Profile Name................................" in line:
            interfaceDetailDict['interfaceMdnsProfileName'] = configLineSplit(line)
        elif "AP Manager......................................." in line:
            interfaceDetailDict['interfaceApManager'] = configLineSplit(line)
        elif "Guest Interface.................................." in line:
            interfaceDetailDict['interfaceGuestInterface'] = configLineSplit(line)
        elif "L2 Multicast....................................." in line:
            interfaceDetailDict['interfaceL2Multicast'] = configLineSplit(line)
    interfaceList.append(copy.copy(interfaceDetailDict))
    interfaceDict['interfaceList']=interfaceList
    return interfaceDict
#########################################################################
# Build Interface Groups
#
#
#########################################################################
def buildInterfaceGroup(input,sysName):
    interfaceGroupList=[]
    interfaceGroupIntList=[]
    interfaceGroupIntConfig=[]
    interfaceGroupDict={}
    interfaceGroupDetailDict={}
    interfaceGroupConfigStartStop="Interface Group Configuration","WLAN Configuration"
    interfaceGroupConfig = collectConfigSection(input, interfaceGroupConfigStartStop)
    logger.info("Building Interface Group List for %s" % sysName)
    for line in interfaceGroupConfig:
        if "Interface Group Name............................." in line:
            if "interfaceGroupName" in interfaceGroupDetailDict:
                interfaceGroupList.append(copy.copy(interfaceGroupDetailDict))
                interfaceGroupDetailDict={}
            interfaceGroupDetailDict['interfaceGroupName'] = configLineSplit(line)
            interfaceGroupDetailDict['keyId'] = interfaceGroupDetailDict['interfaceGroupName']
        elif "Quarantine ......................................" in line:
            interfaceGroupDetailDict['interfaceGroupQuarantine'] = configLineSplit(line)
        elif "Number of Wlans using the Interface Group........ " in line:
            interfaceGroupDetailDict['interfaceGroupWlanInUse'] = configLineSplit(line)
        elif "Number of AP Groups using the Interface Group...." in line:
            interfaceGroupDetailDict['interfaceGroupApGroupInUse'] = configLineSplit(line)
        elif "Number of Interfaces Contained..................." in line:
            interfaceGroupDetailDict['interfaceGroupTotalInterfaces'] = configLineSplit(line)
        elif "mDNS Profile Name................................" in line:
            interfaceGroupDetailDict['interfaceGroupMdnsProfile'] = configLineSplit(line)
        elif "Failure-Detect Mode.............................." in line:
            interfaceGroupDetailDict['interfaceGroupFailureDetect'] = configLineSplit(line)
        elif "Interface Group Description...................... " in line:
            interfaceGroupDetailDict['interfaceGroupDescription'] = configLineSplit(line)
        elif "Interfaces Contained in this group .............." in line:
            if "interfaceGroupDescription" in interfaceGroupDetailDict:
                interfaceGroupIntConfig=[]
                interfaceGroupIntConfigStartStop="Interface Group Description...................... " + \
                                               str(interfaceGroupDetailDict['interfaceGroupDescription']), "Interface marked with"
                interfaceGroupIntConfig=collectConfigSection(interfaceGroupConfig, interfaceGroupIntConfigStartStop)
                for line in interfaceGroupIntConfig:
                    if "Interface Group Description......................" not in line:
                        if "Interfaces Contained in this group .............." not in line:
                            if line != "":
                                interfaceGroupIntList.append(line.strip().split()[0])
                interfaceGroupDetailDict['interfaceGroupList']=interfaceGroupIntList
                interfaceGroupIntList=[]
    interfaceGroupList.append(copy.copy(interfaceGroupDetailDict))
    interfaceGroupDict['interfaceGroupList']=interfaceGroupList
    return interfaceGroupDict

#########################################################################
# Build Advanced and SSC Config
#
#
#########################################################################
def buildApGroupConfig(input,sysName):
    apGroupDict={}
    apGroupList=[]
    apGroupDetailDict={}
    apGroupConfigStartStop="AP Location","Number of RF Profiles............................"
    apGroupConfig = collectConfigSection(input,apGroupConfigStartStop)
    logger.info("Building Ap Group Configuration for %s" % sysName)
    for line in apGroupConfig:
        if "Total Number of AP Groups........................" in line:
            apGroupDetailDict['apGroupTotal'] = configLineSplit(line)
        elif "Site Name........................................" in line:
            if "apGroupSiteName" in apGroupDetailDict:
                apGroupList.append(copy.copy(apGroupDetailDict))
                apGroupDetailDict = {}
            apGroupDetailDict['apGroupSiteName'] = configLineSplit(line)
            apGroupDetailDict['keyId']=configLineSplit(line)
            apGroupStart="Site Name........................................ " + apGroupDetailDict['apGroupSiteName']
        elif "Site Description................................." in line:
            apGroupDetailDict['apGroupSiteDescrip'] = configLineSplit(line)
        elif "NAS-identifier................................... " in line:
            apGroupDetailDict['apGroupNasId'] = configLineSplit(line)
        elif "Client Traffic QinQ Enable......................." in line:
            apGroupDetailDict['apGroupClientQinQ'] = configLineSplit(line)
        elif "DHCPv4 QinQ Enable..............................." in line:
            apGroupDetailDict['apGroupDhcpQinQ'] = configLineSplit(line)
        elif "AP Operating Class..............................." in line:
            apGroupDetailDict['apGroupApOperatingClass'] = configLineSplit(line)
        elif "Capwap Prefer Mode..............................." in line:
            apGroupDetailDict['apGroupCapwapPreferMode'] = configLineSplit(line)
        elif "2.4 GHz band....................................." in line:
            apGroupDetailDict['apGroup24RfProfile'] = configLineSplit(line)
        elif "5 GHz band......................................." in line:
            apGroupDetailDict['apGroup5RfProfile'] = configLineSplit(line)
        elif "WLAN ID" in line:
            apGroupWlanConfigStartStop=apGroupStart,"*"
            apGroupDetailDict['apGroupWLans']=buildApGroupWlanList(apGroupConfig,apGroupWlanConfigStartStop)
        elif "Lan Port configs" in line:
            apGroupLanConfigStartStop=apGroupStart,"-----"
            apGroupDetailDict['apGroupLans']=buildApGroupLanList(apGroupConfig,apGroupLanConfigStartStop)
        elif "External 3G/4G module configs" in line:
            apGroup3gConfigStartStop=apGroupStart,"AP Name"
            apGroupDetailDict['apGroup3g']=buildApGroup3gList(apGroupConfig,apGroup3gConfigStartStop)
    apGroupList.append(copy.copy(apGroupDetailDict))
    apGroupDict['apGroup']=apGroupList
    return apGroupDict
#########################################################################
# Build AP Group WLAN List
#
#######################################################################

def buildApGroupWlanList(input, configStartStop):
    apGroupWlanList = []
    apGroupWlanDict = {}
    apGroupSiteConfig = collectConfigSection(input, configStartStop)
    apGroupWlanConfigStartStop="WLAN ID","Lan Port configs"
    apGroupWlanConfig=collectConfigSection(apGroupSiteConfig,apGroupWlanConfigStartStop)
    for line in apGroupWlanConfig:
        if "WLAN ID" not in line:
            if "---" not in line:
                if "*" not in line:
                    if len(line.split()) > 4:
                        apGroupWlanDict['apGroupWlanId'] = line.strip().split()[0]
                        apGroupWlanDict['apGroupWlanInterface'] = line.strip().split()[1]
                        apGroupWlanDict['apGroupWlanNac'] = line.strip().split()[2]
                        apGroupWlanDict['apGroupWlanRadioPolicy'] = line.strip().split()[3]
                        apGroupWlanDict['apGroupWlanOpenDns'] = line.strip().split()[4]
                        apGroupWlanList.append(copy.copy(apGroupWlanDict))
                        apGroupWlanDict={}
                    elif len(line.split()) == 4:
                        apGroupWlanDict['apGroupWlanId'] = line.strip().split()[0]
                        apGroupWlanDict['apGroupWlanInterface'] = line.strip().split()[1]
                        apGroupWlanDict['apGroupWlanNac'] = line.strip().split()[2]
                        apGroupWlanDict['apGroupWlanRadioPolicy'] = line.strip().split()[3]
                        apGroupWlanDict['apGroupWlanOpenDns'] = ""
                        apGroupWlanList.append(copy.copy(apGroupWlanDict))
                        apGroupWlanDict={}
    return (apGroupWlanList)
#########################################################################
# Build AP Group Lan Port List
#
#######################################################################

def buildApGroupLanList(input, configStartStop):
    apGroupLanList = []
    apGroupLanDict = {}
    apGroupSiteConfig = collectConfigSection(input, configStartStop)
    apGroupLanConfigStartStop="Lan Port configs","External 3G/4G module configs"
    apGroupLanConfig=collectConfigSection(apGroupSiteConfig,apGroupLanConfigStartStop)
    for line in apGroupLanConfig:
        if "RLAN" not in line:
            if "configs" not in line:
                if "External" not in line:
                    if "---" not in line:
                        if len(line.split()) == 3:
                            apGroupLanDict['lan'] = line.strip().split()[0]
                            apGroupLanDict['status'] = line.strip().split()[1]
                            apGroupLanDict['rlan'] = line.strip().split()[2]
                            apGroupLanDict['poe'] = ""
                            apGroupLanList.append(copy.copy(apGroupLanDict))
                            apGroupLanDict={}
                        elif len(line.split()) > 3:
                            apGroupLanDict['lan'] = line.strip().split()[0]
                            apGroupLanDict['status'] = line.strip().split()[1]
                            apGroupLanDict['poe'] = line.strip().split()[2]
                            apGroupLanDict['rlan'] = line.strip().split()[3]
                            apGroupLanList.append(copy.copy(apGroupLanDict))
                            apGroupLanDict={}
    return (apGroupLanList)
#########################################################################
# Build AP Group 3g Port List
#
#######################################################################

def buildApGroup3gList(input, configStartStop):
    apGroup3gList = []
    apGroup3gDict = {}
    apGroupSiteConfig = collectConfigSection(input, configStartStop)
    apGroup3gConfigStartStop="External 3G/4G module configs","AP Name"
    apGroup3gConfig=collectConfigSection(apGroupSiteConfig,apGroup3gConfigStartStop)
    for line in apGroup3gConfig:
        if "RLAN" not in line:
            if "configs" not in line:
                if "---" not in line:
                    if len(line.split()) == 3:
                        apGroup3gDict['lan'] = line.strip().split()[0]
                        apGroup3gDict['status'] = line.strip().split()[1]
                        apGroup3gDict['rlan'] = line.strip().split()[2]
                        apGroup3gDict['poe'] = ""
                        apGroup3gList.append(copy.copy(apGroup3gDict))
                        apGroup3gDict={}
                    elif len(line.split()) > 3:
                        apGroup3gDict['lan'] = line.strip().split()[0]
                        apGroup3gDict['status'] = line.strip().split()[1]
                        apGroup3gDict['poe'] = line.strip().split()[2]
                        apGroup3gDict['rlan'] = line.strip().split()[3]
                        apGroup3gList.append(copy.copy(apGroup3gDict))
                        apGroup3gDict={}
    return (apGroup3gList)
#########################################################################
# Build RF Profiles
#
#
#########################################################################
def buildRfProfiles(input,sysName):
    rfProfileList=[]
    rfProfileDict={}
    rfProfileDetailDict={}
    rfProfileConfigStartStop="RF Profile","AP Config"
    rfProfileConfig = collectConfigSection(input, rfProfileConfigStartStop)
    logger.info("Building RF Profile Configuration for %s" % sysName)
    for line in rfProfileConfig:
        if "RF Profile name................................" in line:
            if "rfProfileName" in rfProfileDetailDict:
                rfProfileList.append(copy.copy(rfProfileDetailDict))
                rfProfileDetailDict={}
            rfProfileDetailDict['rfProfileName'] = configLineSplit(line)
            rfProfileDetailDict['keyId']=rfProfileDetailDict['rfProfileName']
        elif "Description......................................" in line:
            rfProfileDetailDict['rfProfileDescription'] = configLineSplit(line)
        elif "AP Group Name...................................." in line:
            rfProfileDetailDict['rfProfileApGroupName'] = configLineSplit(line)
        elif "Radio policy....................................." in line:
            rfProfileDetailDict['rfProfileRadioPolicy'] = configLineSplit(line)
        elif "11n-client-only.................................." in line:
            rfProfileDetailDict['rfProfile11nOnly'] = configLineSplit(line)
        elif "Transmit Power Threshold v1......................" in line:
            rfProfileDetailDict['rfProfileTpcV1'] = configLineSplit(line)
        elif "Transmit Power Threshold v2......................" in line:
            rfProfileDetailDict['rfProfileTpcV2'] = configLineSplit(line)
        elif "Min Transmit Power..............................." in line:
            rfProfileDetailDict['rfProfileMinTpc'] = configLineSplit(line)
        elif "Max Transmit Power..............................." in line:
            rfProfileDetailDict['rfProfileMaxTpc'] = configLineSplit(line)
        elif "802.11a 6M Rate.............................." in line:
            rfProfileDetailDict['rfProfileRate6m'] = configLineSplit(line)
        elif "802.11a 9M Rate.............................." in line:
            rfProfileDetailDict['rfProfileRate9m'] = configLineSplit(line)
        elif "802.11a 12M Rate............................." in line:
            rfProfileDetailDict['rfProfileRate12m'] = configLineSplit(line)
        elif "802.11a 18M Rate............................." in line:
            rfProfileDetailDict['rfProfileRate18m'] = configLineSplit(line)
        elif "802.11a 24M Rate............................." in line:
            rfProfileDetailDict['rfProfileRate24m'] = configLineSplit(line)
        elif "802.11a 36M Rate............................." in line:
            rfProfileDetailDict['rfProfileRate36m'] = configLineSplit(line)
        elif "802.11a 48M Rate............................." in line:
            rfProfileDetailDict['rfProfileRate48m'] = configLineSplit(line)
        elif "802.11a 54M Rate............................." in line:
            rfProfileDetailDict['rfProfileRate54m'] = configLineSplit(line)
        elif "802.11b/g 1M Rate............................" in line:
            rfProfileDetailDict['rfProfileRate1m'] = configLineSplit(line)
        elif "802.11b/g 2M Rate............................" in line:
            rfProfileDetailDict['rfProfileRate2m'] = configLineSplit(line)
        elif "802.11b/g 5.5M Rate.........................." in line:
            rfProfileDetailDict['rfProfileRate5m'] = configLineSplit(line)
        elif "802.11b/g 11M Rate..........................." in line:
            rfProfileDetailDict['rfProfileRate11m'] = configLineSplit(line)
        elif "802.11g 6M Rate.............................." in line:
            rfProfileDetailDict['rfProfileRate6m'] = configLineSplit(line)
        elif "802.11g 9M Rate.............................." in line:
            rfProfileDetailDict['rfProfileRate9m'] = configLineSplit(line)
        elif "802.11g 12M Rate............................." in line:
            rfProfileDetailDict['rfProfileRate12m'] = configLineSplit(line)
        elif "802.11g 18M Rate............................." in line:
            rfProfileDetailDict['rfProfileRate18m'] = configLineSplit(line)
        elif "802.11g 24M Rate............................." in line:
            rfProfileDetailDict['rfProfileRate24m'] = configLineSplit(line)
        elif "802.11g 36M Rate............................." in line:
            rfProfileDetailDict['rfProfileRate36m'] = configLineSplit(line)
        elif "802.11g 48M Rate............................." in line:
            rfProfileDetailDict['rfProfileRate48m'] = configLineSplit(line)
        elif "802.11g 54M Rate............................." in line:
            rfProfileDetailDict['rfProfileRate54m'] = configLineSplit(line)
        elif "Max Clients......................................" in line:
            rfProfileDetailDict['rfProfileMaxClients'] = configLineSplit(line)
        elif "Clients......................................" in line:
            rfProfileDetailDict['rfProfileClientTrapThres'] = configLineSplit(line)
        elif "Interference................................." in line:
            rfProfileDetailDict['rfProfileClientInterference'] = configLineSplit(line)
        elif "Noise........................................" in line:
            rfProfileDetailDict['rfProfileNoise'] = configLineSplit(line)
        elif "Utilization.................................." in line:
            rfProfileDetailDict['rfProfileUtilization'] = configLineSplit(line)
        elif "Multicast Data Rate.............................." in line:
            rfProfileDetailDict['rfProfileMulticastDataRate'] = configLineSplit(line)
        elif "Rx Sop Threshold................................." in line:
            rfProfileDetailDict['rfProfileRxSop'] = configLineSplit(line)
        elif "Cca Threshold...................................." in line:
            rfProfileDetailDict['rfProfileCca'] = configLineSplit(line)
        elif "Slot Admin State:................................" in line:
            rfProfileDetailDict['rfProfileSlotAdmin'] = configLineSplit(line)
        elif "State........................................" in line:
            rfProfileDetailDict['rfProfileFraState'] = configLineSplit(line)
        elif "Client Select Utilization Threshold.........." in line:
            rfProfileDetailDict['rfProfileClientSelectUtil'] = configLineSplit(line)
        elif "Client Reset Utilization Threshold..........." in line:
            rfProfileDetailDict['rfProfileClientReset'] = configLineSplit(line)
        elif "Probe Response..............................." in line:
            rfProfileDetailDict['rfProfileProbeResponse'] = configLineSplit(line)
        elif "Cycle Count.................................." in line:
            rfProfileDetailDict['rfProfileCycleCount'] = configLineSplit(line)
        elif "Cycle Threshold.............................." in line:
            rfProfileDetailDict['rfProfileCycleThres'] = configLineSplit(line)
        elif "Expire Suppression..........................." in line:
            rfProfileDetailDict['rfProfileExpireSuppression'] = configLineSplit(line)
        elif "Expire Dual Band............................." in line:
            rfProfileDetailDict['rfProfileExpireDualBand'] = configLineSplit(line)
        elif "Client Rssi.................................." in line:
            rfProfileDetailDict['rfProfileClientRssi'] = configLineSplit(line)
        elif "Client Mid Rssi.............................." in line:
            rfProfileDetailDict['rfProfileMidRssi'] = configLineSplit(line)
        elif "Denial......................................." in line:
            rfProfileDetailDict['rfProfileLoadBalanceDenial'] = configLineSplit(line)
        elif "Window......................................." in line:
            rfProfileDetailDict['rfProfileLoadBalanceWindow'] = configLineSplit(line)
        elif "Data........................................." in line:
            rfProfileDetailDict['rfProfileCoverageData'] = configLineSplit(line)
        elif "Voice........................................" in line:
            rfProfileDetailDict['rfProfileCoverageVoice'] = configLineSplit(line)
        elif "Minimum Client Level........................." in line:
            rfProfileDetailDict['rfProfileCoverageMinClient'] = configLineSplit(line)
        elif "Exception Level.............................." in line:
            rfProfileDetailDict['rfProfileCoverageExceptionLevel'] = configLineSplit(line)
        #Not Checking all channels as config spills on another line
        elif "DCA Channel List................................." in line:
            rfProfileDetailDict['rfProfileDcaChannel'] = configLineSplit(line)
        elif "DCA Bandwidth...................................." in line:
            rfProfileDetailDict['rfProfileDcaBandwidth'] = configLineSplit(line)
        elif "DCA Foreign AP Contribution......................" in line:
            rfProfileDetailDict['rfProfileForeignAp'] = configLineSplit(line)
        elif "MCS-00 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs00'] = configLineSplit(line)
        elif "MCS-01 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs01'] = configLineSplit(line)
        elif "MCS-02 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs02'] = configLineSplit(line)
        elif "MCS-03 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs03'] = configLineSplit(line)
        elif "MCS-04 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs04'] = configLineSplit(line)
        elif "MCS-05 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs05'] = configLineSplit(line)
        elif "MCS-06 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs06'] = configLineSplit(line)
        elif "MCS-07 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs07'] = configLineSplit(line)
        elif "MCS-08 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs08'] = configLineSplit(line)
        elif "MCS-09 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs09'] = configLineSplit(line)
        elif "MCS-10 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs10'] = configLineSplit(line)
        elif "MCS-11 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs11'] = configLineSplit(line)
        elif "MCS-12 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs12'] = configLineSplit(line)
        elif "MCS-13 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs13'] = configLineSplit(line)
        elif "MCS-14 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs14'] = configLineSplit(line)
        elif "MCS-15 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs15'] = configLineSplit(line)
        elif "MCS-16 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs16'] = configLineSplit(line)
        elif "MCS-17 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs17'] = configLineSplit(line)
        elif "MCS-18 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs18'] = configLineSplit(line)
        elif "MCS-19 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs19'] = configLineSplit(line)
        elif "MCS-20 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs20'] = configLineSplit(line)
        elif "MCS-21 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs21'] = configLineSplit(line)
        elif "MCS-22 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs22'] = configLineSplit(line)
        elif "MCS-23 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs23'] = configLineSplit(line)
        elif "MCS-24 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs24'] = configLineSplit(line)
        elif "MCS-25 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs25'] = configLineSplit(line)
        elif "MCS-26 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs26'] = configLineSplit(line)
        elif "MCS-27 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs27'] = configLineSplit(line)
        elif "MCS-28 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs28'] = configLineSplit(line)
        elif "MCS-29 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs29'] = configLineSplit(line)
        elif "MCS-30 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs30'] = configLineSplit(line)
        elif "MCS-31 Rate.................................." in line:
            rfProfileDetailDict['rfProfileRateMcs31'] = configLineSplit(line)
        elif "Client Network Preference......................." in line:
            rfProfileDetailDict['rfProfileClientNetworkPrefer'] = configLineSplit(line)
    rfProfileList.append(copy.copy(rfProfileDetailDict))
    rfProfileDict['rfProfile']=rfProfileList
    return rfProfileDict

#########################################################################
# Build 802.11a Network
#
#
#########################################################################
def build80211aConfig(input,sysName):
    network80211aDict={}
    network80211aDetailDict={}
    network80211aConfigStartStop="802.11a Configuration","802.11a Advanced Configuration"
    network80211aConfig = collectConfigSection(input, network80211aConfigStartStop)
    logger.info("Building 802.11a Configuration for %s" % sysName)
    for line in network80211aConfig:
            if "802.11a Network.................................." in line:
                network80211aDetailDict['network80211aStatus'] = configLineSplit(line)
            elif "11acSupport......................................" in line:
                network80211aDetailDict['network11AcSupport'] = configLineSplit(line)
            elif "11nSupport......................................." in line:
                network80211aDetailDict['network11NSupport'] = configLineSplit(line)
            elif "802.11a Low Band..........................." in line:
                network80211aDetailDict['network80211aLowBand'] = configLineSplit(line)
            elif "802.11a Mid Band..........................." in line:
                network80211aDetailDict['network80211aMidBand'] = configLineSplit(line)
            elif "802.11a High Band.........................." in line:
                network80211aDetailDict['network80211aHighBand'] = configLineSplit(line)
            elif "802.11a 6M Rate.............................." in line:
                network80211aDetailDict['network80211a6M'] = configLineSplit(line)
            elif "802.11a 9M Rate.............................." in line:
                network80211aDetailDict['network80211a9M'] = configLineSplit(line)
            elif "802.11a 12M Rate............................." in line:
                network80211aDetailDict['network80211a12M'] = configLineSplit(line)
            elif "802.11a 18M Rate............................." in line:
                network80211aDetailDict['network80211a18M'] = configLineSplit(line)
            elif "802.11a 24M Rate............................." in line:
                network80211aDetailDict['network80211a24M'] = configLineSplit(line)
            elif "802.11a 36M Rate............................." in line:
                network80211aDetailDict['network80211a36M'] = configLineSplit(line)
            elif "802.11a 48M Rate............................." in line:
                network80211aDetailDict['network80211a48M'] = configLineSplit(line)
            elif "802.11a 54M Rate............................." in line:
                network80211aDetailDict['network80211a54M'] = configLineSplit(line)
            elif "MCS 0........................................" in line:
                network80211aDetailDict['network80211aRateMcs0'] = configLineSplit(line)
            elif "MCS 1........................................" in line:
                network80211aDetailDict['network80211aRateMcs1'] = configLineSplit(line)
            elif "MCS 2........................................" in line:
                network80211aDetailDict['network80211aRateMcs2'] = configLineSplit(line)
            elif "MCS 3........................................" in line:
                network80211aDetailDict['network80211aRateMcs3'] = configLineSplit(line)
            elif "MCS 4........................................" in line:
                network80211aDetailDict['network80211aRateMcs4'] = configLineSplit(line)
            elif "MCS 5........................................" in line:
                network80211aDetailDict['network80211aRateMcs5'] = configLineSplit(line)
            elif "MCS 6........................................" in line:
                network80211aDetailDict['network80211aRateMcs6'] = configLineSplit(line)
            elif "MCS 7........................................" in line:
                network80211aDetailDict['network80211aRateMcs7'] = configLineSplit(line)
            elif "MCS 8........................................" in line:
                network80211aDetailDict['network80211aRateMcs8'] = configLineSplit(line)
            elif "MCS 9........................................" in line:
                network80211aDetailDict['network80211aRateMcs9'] = configLineSplit(line)
            elif "MCS 10......................................." in line:
                network80211aDetailDict['network80211aRateMcs10'] = configLineSplit(line)
            elif "MCS 11......................................." in line:
                network80211aDetailDict['network80211aRateMcs11'] = configLineSplit(line)
            elif "MCS 12......................................." in line:
                network80211aDetailDict['network80211aRateMcs12'] = configLineSplit(line)
            elif "MCS 13......................................." in line:
                network80211aDetailDict['network80211aRateMcs13'] = configLineSplit(line)
            elif "MCS 14......................................." in line:
                network80211aDetailDict['network80211aRateMcs14'] = configLineSplit(line)
            elif "MCS 15......................................." in line:
                network80211aDetailDict['network80211aRateMcs15'] = configLineSplit(line)
            elif "MCS 16......................................." in line:
                network80211aDetailDict['network80211aRateMcs16'] = configLineSplit(line)
            elif "MCS 17......................................." in line:
                network80211aDetailDict['network80211aRateMcs17'] = configLineSplit(line)
            elif "MCS 18......................................." in line:
                network80211aDetailDict['network80211aRateMcs18'] = configLineSplit(line)
            elif "MCS 19......................................." in line:
                network80211aDetailDict['network80211aRateMcs19'] = configLineSplit(line)
            elif "MCS 20......................................." in line:
                network80211aDetailDict['network80211aRateMcs20'] = configLineSplit(line)
            elif "MCS 21......................................." in line:
                network80211aDetailDict['network80211aRateMcs21'] = configLineSplit(line)
            elif "MCS 22......................................." in line:
                network80211aDetailDict['network80211aRateMcs22'] = configLineSplit(line)
            elif "MCS 23......................................." in line:
                network80211aDetailDict['network80211aRateMcs23'] = configLineSplit(line)
            elif "Nss=1: MCS 0-9 .............................." in line:
                network80211aDetailDict['network80211aNss1'] = configLineSplit(line)
            elif "Nss=2: MCS 0-9 .............................." in line:
                network80211aDetailDict['network80211aNss2'] = configLineSplit(line)
            elif "Nss=3: MCS 0-9 .............................." in line:
                network80211aDetailDict['network80211aNss3'] = configLineSplit(line)
            elif "A-MPDU Tx:" in line:
                network80211aDetailDict[''] = configLineSplit(line)
            elif "Priority 0..............................." in line:
                if "network80211aMpduP0" in network80211aDetailDict:
                    network80211aDetailDict['network80211aMsduP0'] = configLineSplit(line)
                else:
                    network80211aDetailDict['network80211aMpduP0'] = configLineSplit(line)
            elif "Priority 1..............................." in line:
                if "network80211aMpduP1" in network80211aDetailDict:
                    network80211aDetailDict['network80211aMsduP1'] = configLineSplit(line)
                else:
                    network80211aDetailDict['network80211aMpduP1'] = configLineSplit(line)
            elif "Priority 2..............................." in line:
                if "network80211aMpduP2" in network80211aDetailDict:
                    network80211aDetailDict['network80211aMsduP2'] = configLineSplit(line)
                else:
                    network80211aDetailDict['network80211aMpduP2'] = configLineSplit(line)
            elif "Priority 3..............................." in line:
                if "network80211aMpduP3" in network80211aDetailDict:
                    network80211aDetailDict['network80211aMsduP3'] = configLineSplit(line)
                else:
                    network80211aDetailDict['network80211aMpduP3'] = configLineSplit(line)
            elif "Priority 4..............................." in line:
                if "network80211aMpduP4" in network80211aDetailDict:
                    network80211aDetailDict['network80211aMsduP4'] = configLineSplit(line)
                else:
                    network80211aDetailDict['network80211aMpduP4'] = configLineSplit(line)
            elif "Priority 5..............................." in line:
                if "network80211aMpduP5" in network80211aDetailDict:
                    network80211aDetailDict['network80211aMsduP5'] = configLineSplit(line)
                else:
                    network80211aDetailDict['network80211aMpduP5'] = configLineSplit(line)
            elif "Priority 6..............................." in line:
                if "network80211aMpduP6" in network80211aDetailDict:
                    network80211aDetailDict['network80211aMsduP6'] = configLineSplit(line)
                else:
                    network80211aDetailDict['network80211aMpduP6'] = configLineSplit(line)
            elif "Priority 7..............................." in line:
                if "network80211aMpduP7" in network80211aDetailDict:
                    network80211aDetailDict['network80211aMsduP7'] = configLineSplit(line)
                else:
                    network80211aDetailDict['network80211aMpduP7'] = configLineSplit(line)
            elif "Aggregation scheduler...................." in line:
                network80211aDetailDict['network80211aMpduAgScheduler'] = configLineSplit(line)
            elif "Frame Burst.............................." in line:
                network80211aDetailDict['network80211aFrameBurst'] = configLineSplit(line)
            elif "Realtime Timeout....................." in line:
                network80211aDetailDict['network80211aRealtimeTimeout'] = configLineSplit(line)
            elif "Rifs Rx ....................................." in line:
                network80211aDetailDict['network80211aMsduRifsRx'] = configLineSplit(line)
            elif "Guard Interval .............................." in line:
                network80211aDetailDict['network80211aGuardInt'] = configLineSplit(line)
            elif "Beacon Interval.................................." in line:
                network80211aDetailDict['network80211aBeaconInt'] = configLineSplit(line)
            elif "CF Pollable mandatory............................" in line:
                network80211aDetailDict['network80211aCfPollMand'] = configLineSplit(line)
            elif "CF Poll Request mandatory........................" in line:
                network80211aDetailDict['network80211aCfPollRequest'] = configLineSplit(line)
            elif "CFP Period......................................." in line:
                network80211aDetailDict['network80211aCfpPeriod'] = configLineSplit(line)
            elif "CFP Maximum Duration............................." in line:
                network80211aDetailDict['network80211aCfpMaxDur'] = configLineSplit(line)
            elif "Default Channel.................................." in line:
                network80211aDetailDict['network80211aDefaultChannel'] = configLineSplit(line)
            elif "Default Tx Power Level..........................." in line:
                network80211aDetailDict['network80211aDefaultTx'] = configLineSplit(line)
            elif "DTPC  Status....................................." in line:
                network80211aDetailDict['network80211aDtpc'] = configLineSplit(line)
            elif "Fragmentation Threshold.........................." in line:
                network80211aDetailDict['network80211aFragThres'] = configLineSplit(line)
            elif "RSSI Low Check..................................." in line:
                network80211aDetailDict['network80211aRssiLow'] = configLineSplit(line)
            elif "RSSI Threshold..................................." in line:
                network80211aDetailDict['network80211aRssiThres'] = configLineSplit(line)
            elif "TI Threshold....................................." in line:
                network80211aDetailDict['network80211aTiThres'] = configLineSplit(line)
            elif "Legacy Tx Beamforming setting...................." in line:
                network80211aDetailDict['network80211aLegacyBeam'] = configLineSplit(line)
            elif "Traffic Stream Metrics Status...................." in line:
                network80211aDetailDict['network80211aTsm'] = configLineSplit(line)
            elif "Expedited BW Request Status......................" in line:
                network80211aDetailDict['network80211aExBandwidth'] = configLineSplit(line)
            elif "World Mode......................................." in line:
                network80211aDetailDict['network80211aWorldMode'] = configLineSplit(line)
            elif "dfs-peakdetect..................................." in line:
                network80211aDetailDict['network80211dfsPeakDetect'] = configLineSplit(line)
            elif "EDCA profile type................................" in line:
                network80211aDetailDict['network80211aEdcaProfile'] = configLineSplit(line)
            elif "Voice MAC optimization status...................." in line:
                network80211aDetailDict['network80211aVoiceMacOpt'] = configLineSplit(line)
            elif "Voice AC - Admission control (ACM)............" in line:
                network80211aDetailDict['voiceAdmissionControl'] = configLineSplit(line)
            elif "Voice Stream-Size............................." in line:
                network80211aDetailDict['voiceStreamSize'] = configLineSplit(line)
            elif "Voice Max-Streams............................." in line:
                network80211aDetailDict['voiceMaxStream'] = configLineSplit(line)
            elif "Voice max RF bandwidth........................" in line:
                network80211aDetailDict['voiceMaxRfBandwidth'] = configLineSplit(line)
            elif "Voice reserved roaming bandwidth.............." in line:
                network80211aDetailDict['voiceReserveBandwidth'] = configLineSplit(line)
            elif "Voice CAC Method ............................." in line:
                network80211aDetailDict['voiceCacMethod'] = configLineSplit(line)
            elif "Voice tspec inactivity timeout................" in line:
                network80211aDetailDict['voiceTspectTimeout'] = configLineSplit(line)
            elif "SIP based CAC ................................" in line:
                if "voiceSipCac" in network80211aDetailDict:
                    network80211aDetailDict['videoSipCac']=configLineSplit(line)
                else:
                    network80211aDetailDict['voiceSipCac'] = configLineSplit(line)
            elif "SIP Codec Type ..............................." in line:
                network80211aDetailDict['voiceSipCacCodec'] = configLineSplit(line)
            elif "SIP call bandwidth ..........................." in line:
                network80211aDetailDict['voiceSipCallBandwidth'] = configLineSplit(line)
            elif "SIP call bandwith sample-size ................" in line:
                network80211aDetailDict['voiceSipCallBandwidthSample'] = configLineSplit(line)
            elif "Video AC - Admission control (ACM)............" in line:
                network80211aDetailDict['videoAdmissionControl'] = configLineSplit(line)
            elif "Video max RF bandwidth........................" in line:
                network80211aDetailDict['videoMaxRfBandwidth'] = configLineSplit(line)
            elif "Video reserved roaming bandwidth.............." in line:
                network80211aDetailDict['videoReserveBandwidth'] = configLineSplit(line)
            elif "Video load-based CAC mode....................." in line:
                network80211aDetailDict['videoALoadCacMode'] = configLineSplit(line)
            elif "Video CAC Method ............................." in line:
                network80211aDetailDict['videoCacMethod'] = configLineSplit(line)
            elif "Best-effort AC - Admission control (ACM)......" in line:
                network80211aDetailDict['bestEffortAdmissionControl'] = configLineSplit(line)
            elif "Background AC - Admission control (ACM)......." in line:
                network80211aDetailDict['backGroupAdmissionControl'] = configLineSplit(line)
            elif "Maximum Number of Clients per AP Radio..........." in line:
                network80211aDetailDict['network80211aMaxClientsRadio'] = configLineSplit(line)
    network80211aDict['network80211a']=network80211aDetailDict
    return network80211aDict
#########################################################################
# Build 802.11a Airewave Configuration
#
#
#########################################################################
def build80211aAirewaveConfig(input,sysName):
    airewave80211aDict={}
    airewave80211aDetailDict={}
    network49enabled=False
    airewave80211aConfigStartStop="802.11a Airewave Director Configuration","802.11a CleanAir Configuration"
    airewave80211aConfig = collectConfigSection(input, airewave80211aConfigStartStop)
    #Used Channel List
    airewave80211aChannelConfigStartStop="802.11a 5 GHz Auto-RF Channel List",\
                                                    "Unused Channel List.........................."
    airewave80211aAllowedChannelConfig=collectConfigSection(airewave80211aConfig,airewave80211aChannelConfigStartStop)
    airewave80211a49AllowedChannelConfigStartStop="802.11a 4.9 GHz Auto-RF Channel List",\
                                                    "Unused Channel List.........................."
    airewave80211a49AllowedChannelConfig=collectConfigSection(airewave80211aConfig,airewave80211a49AllowedChannelConfigStartStop)
    #Unused Channel List
    airewave80211aUnusedChannelConfigStartStop = "Unused Channel List..........................", \
                                           "802.11a 4.9 GHz Auto-RF Channel List"
    airewave80211aUnusedChannelConfig = collectConfigSection(airewave80211aConfig,
                                                              airewave80211aUnusedChannelConfigStartStop)
    airewave80211a49ChannelConfigStartStop = "802.11a 4.9 GHz Auto-RF Channel List", \
                                                    "DCA Outdoor AP option.........................."
    airewave80211a49ChannelConfig = collectConfigSection(airewave80211aConfig,
                                                                airewave80211a49ChannelConfigStartStop)
    airwave80211a49UnusedChannelConfigStartStop="Unused Channel List..........................",\
                                                "DCA Outdoor AP option.........................."
    airwave80211a49UnusedChannelConfig=collectConfigSection(airewave80211a49ChannelConfig, \
                                                            airwave80211a49UnusedChannelConfigStartStop)
    logger.info("Building 802.11a Airewave Configuration for %s" % sysName)
    for line in airewave80211aConfig:
        if "Channel Update Logging........................." in line:
            airewave80211aDetailDict['channelUpdateLog'] = configLineSplit(line)
        elif "Coverage Profile Logging......................." in line:
            airewave80211aDetailDict['channelCoverageProfileLog'] = configLineSplit(line)
        elif "Foreign Profile Logging........................" in line:
            airewave80211aDetailDict['foreignProfileLog'] = configLineSplit(line)
        elif "Load Profile Logging..........................." in line:
            airewave80211aDetailDict['loadProfileLog'] = configLineSplit(line)
        elif "Noise Profile Logging.........................." in line:
            airewave80211aDetailDict['noiseProfileLog'] = configLineSplit(line)
        elif "Performance Profile Logging...................." in line:
            airewave80211aDetailDict['performanceProfileLog'] = configLineSplit(line)
        elif "TxPower Update Logging........................." in line:
            airewave80211aDetailDict['txPowerUpdateLog'] = configLineSplit(line)
        elif "802.11a Global Interference threshold.........." in line:
            airewave80211aDetailDict['global80211aIntThreshold'] = configLineSplit(line)
        elif "802.11a Global noise threshold................." in line:
            airewave80211aDetailDict['global80211aNoiseThreshold'] = configLineSplit(line)
        elif "802.11a Global RF utilization threshold........" in line:
            airewave80211aDetailDict['global80211aRfUtilThreshold'] = configLineSplit(line)
        elif "802.11a Global throughput threshold............" in line:
            airewave80211aDetailDict['global80211aTputThreshold'] = configLineSplit(line)
        elif "802.11a Global clients threshold..............." in line:
            airewave80211aDetailDict['global80211aClientsThreshold'] = configLineSplit(line)
        elif "802.11a Monitor Mode..........................." in line:
            airewave80211aDetailDict['monitorMode80211a'] = configLineSplit(line)
        elif "802.11a Monitor Mode for Mesh AP Backhaul......" in line:
            airewave80211aDetailDict['monitorMode80211aMesh'] = configLineSplit(line)
        elif "802.11a Monitor Channels......................." in line:
            airewave80211aDetailDict['monitor80211achannels'] = configLineSplit(line)
        elif "802.11a RRM Neighbor Discover Type............." in line:
            airewave80211aDetailDict['monitor80211aRrmDiscover'] = configLineSplit(line)
        elif "802.11a RRM Neighbor RSSI Normalization........" in line:
            airewave80211aDetailDict['monitor80211aRrmNeighRssi'] = configLineSplit(line)
        elif "802.11a AP Coverage Interval..................." in line:
            airewave80211aDetailDict['monitor80211aApCoverageInterval'] = configLineSplit(line)
        elif "802.11a AP Load Interval......................." in line:
            airewave80211aDetailDict['monitor80211aApLoadInterval'] = configLineSplit(line)
        elif "802.11a AP Monitor Measurement Interval........" in line:
            airewave80211aDetailDict['monitor80211aApMonitorMeasure'] = configLineSplit(line)
        elif "802.11a AP Neighbor Timeout Factor............." in line:
            airewave80211aDetailDict['monitor80211aApNeighborTimeout'] = configLineSplit(line)
        elif "802.11a AP Report Measurement Interval........." in line:
            airewave80211aDetailDict['monitor80211aApMeasurementInt'] = configLineSplit(line)
        elif "Transmit Power Assignment Mode................." in line:
            airewave80211aDetailDict['tpc80211aAssignmentMode'] = configLineSplit(line)
        elif "Transmit Power Update Interval................." in line:
            airewave80211aDetailDict['tpc80211aUpdateInterval'] = configLineSplit(line)
        elif "Transmit Power Threshold......................." in line:
            airewave80211aDetailDict['tpc80211aThreshold'] = configLineSplit(line)
        elif "Transmit Power Neighbor Count.................." in line:
            airewave80211aDetailDict['tpc80211aNeighCount'] = configLineSplit(line)
        elif "Min Transmit Power............................." in line:
            airewave80211aDetailDict['tpc80211aMinPower'] = configLineSplit(line)
        elif "Max Transmit Power............................." in line:
            airewave80211aDetailDict['tpc80211aMaxPower'] = configLineSplit(line)
        elif "Noise........................................" in line:
            if "tpc80211aNoise" in airewave80211aDetailDict:
                airewave80211aDetailDict['dca80211aNoise'] = configLineSplit(line)
            else:
                airewave80211aDetailDict['tpc80211aNoise'] = configLineSplit(line)
        elif "Interference................................." in line:
            if "tpc80211aInterference" in airewave80211aDetailDict:
                airewave80211aDetailDict['dca80211aInterference'] = configLineSplit(line)
            else:
                airewave80211aDetailDict['tpc80211aInterference'] = configLineSplit(line)
        elif "Load........................................." in line:
            if "tpc80211aLoad" in airewave80211aDetailDict:
                airewave80211aDetailDict['dca80211aLoad'] = configLineSplit(line)
            else:
                airewave80211aDetailDict['tpc80211aLoad'] = configLineSplit(line)
        elif "Device Aware................................." in line:
            if "tpc80211aDeviceAware" in airewave80211aDetailDict:
                airewave80211aDetailDict['dca80211aDeviceAware'] = configLineSplit(line)
            else:
                airewave80211aDetailDict['tpc80211aDeviceAware'] = configLineSplit(line)
        elif "Transmit Power Assignment Leader..............." in line:
            airewave80211aDetailDict['tpc80211aTpcLeader'] = configLineSplit(line)
        elif "Last Run......................................." in line:
            if "tpc80211aLastRun" in airewave80211aDetailDict:
                if "dca80211aLastRun" in airewave80211aDetailDict:
                    airewave80211aDetailDict['rfGroup80211aLastRun'] = configLineSplit(line)
                else:
                    airewave80211aDetailDict['dca80211aLastRun'] = configLineSplit(line)
            else:
                airewave80211aDetailDict['tpc80211aLastRun'] = configLineSplit(line)
        elif "Last Run Time.................................." in line:
            if "tpc80211aLastRunTime" in airewave80211aDetailDict:
                airewave80211aDetailDict['dca80211aLastRunTime'] = configLineSplit(line)
            else:
                airewave80211aDetailDict['tpc80211aLastRunTime'] = configLineSplit(line)
        elif "TPC Mode......................................." in line:
            airewave80211aDetailDict['tpc80211aMode'] = configLineSplit(line)
        elif "802.11a Coverage Hole Detection Mode..........." in line:
            airewave80211aDetailDict['chd80211aMode'] = configLineSplit(line)
        elif "802.11a Coverage Voice Packet Count............" in line:
            airewave80211aDetailDict['chd80211aVoicePacketCount'] = configLineSplit(line)
        elif "802.11a Coverage Voice Packet Percentage......." in line:
            airewave80211aDetailDict['chd80211aVoicePacketPercentage'] = configLineSplit(line)
        elif "802.11a Coverage Voice RSSI Threshold.........." in line:
            airewave80211aDetailDict['chd80211aVoiceRssi'] = configLineSplit(line)
        elif "802.11a Coverage Data Packet Count............." in line:
            airewave80211aDetailDict['chd80211aDataPacketCount'] = configLineSplit(line)
        elif "802.11a Coverage Data Packet Percentage........" in line:
            airewave80211aDetailDict['chd80211aDataPacketPercentage'] = configLineSplit(line)
        elif "802.11a Coverage Data RSSI Threshold..........." in line:
            airewave80211aDetailDict['chd80211aCoverageDataRssi'] = configLineSplit(line)
        elif "802.11a Global coverage exception level........" in line:
            airewave80211aDetailDict['chd80211aGlobalCoverageException'] = configLineSplit(line)
        elif "802.11a Global client minimum exception lev...." in line:
            airewave80211aDetailDict['chd80211aGlobalClientMinimum'] = configLineSplit(line)
        elif "802.11a OptimizedRoaming Mode.................." in line:
            airewave80211aDetailDict['optimizedRoaming80211aMode'] = configLineSplit(line)
        elif "802.11a OptimizedRoaming Reporting Interval...." in line:
            airewave80211aDetailDict['optimizedRoaming80211aReportingInterval'] = configLineSplit(line)
        elif "802.11a OptimizedRoaming Rate Threshold........" in line:
            airewave80211aDetailDict['optimizedRoaming80211aRateThreshold'] = configLineSplit(line)
        elif "802.11a OptimizedRoaming Hysteresis............" in line:
            airewave80211aDetailDict['optimizedRoaming80211aHysteresis'] = configLineSplit(line)
        elif "Channel Assignment Mode........................" in line:
            airewave80211aDetailDict['dca80211aChannelAssignment'] = configLineSplit(line)
        elif "Channel Update Interval........................" in line:
            airewave80211aDetailDict['dca80211aChannelUpdate'] = configLineSplit(line)
        elif "Anchor time (Hour of the day).................." in line:
            airewave80211aDetailDict['dca80211aAnchorTime'] = configLineSplit(line)
        elif "CleanAir Event-driven RRM option..............." in line:
            airewave80211aDetailDict['dca80211aCleanairRrm'] = configLineSplit(line)
        elif "Channel Assignment Leader......................" in line:
            airewave80211aDetailDict['dca80211aChannelAssignmentLeader'] = configLineSplit(line)
        elif "DCA Sensitivity Level.........................." in line:
            airewave80211aDetailDict['dca80211aSensitivityLevel'] = configLineSplit(line)
        elif "DCA 802.11n/ac Channel Width..................." in line:
            airewave80211aDetailDict['dca80211aChannelWidth'] = configLineSplit(line)
        elif "DCA Minimum Energy Limit......................." in line:
            airewave80211aDetailDict['dcaMinEnergyLimit'] = configLineSplit(line)
        elif "Minimum......................................" in line:
            if "dca80211aChannelEnergyLevelMin" in airewave80211aDetailDict:
                airewave80211aDetailDict['dca80211aChannelDwellMin'] = configLineSplit(line)
            else:
                airewave80211aDetailDict['dca80211aChannelEnergyLevelMin'] = configLineSplit(line)
        elif "Average......................................" in line:
            if "dca80211aChannelEnergyLevelAvg" in airewave80211aDetailDict:
                airewave80211aDetailDict['dca80211aChannelDwellAvg'] = configLineSplit(line)
            else:
                airewave80211aDetailDict['dca80211aChannelEnergyLevelAvg'] = configLineSplit(line)
        elif "Maximum......................................" in line:
            if "dca80211aChannelEnergyLevelMax" in airewave80211aDetailDict:
                airewave80211aDetailDict['dca80211aChannelDwellMax'] = configLineSplit(line)
            else:
                airewave80211aDetailDict['dca80211aChannelEnergyLevelMax'] = configLineSplit(line)
        elif "802.11a 4.9 GHz Auto-RF Channel List" in line:
            network49enabled = True

        elif "Allowed Channel List" in line:
            if network49enabled==True:
                if "dca80211aAllowChannelList" in airewave80211aDetailDict:
                    channelList = []
                    for line in airewave80211a49AllowedChannelConfig:
                        if "Auto-RF" not in line:
                            if "Allowed Channel List........................." in line:
                                channelList.append(configLineSplit(line))
                            elif "Allowed Channel List........................."not in line:
                                channelList.append(line.strip())
                            airewave80211aDetailDict['dca80211a49AllowChannelList']=''.join(channelList)
                else:
                    channelList = []
                    for line in airewave80211aAllowedChannelConfig:
                        if "Auto-RF" not in line:
                            if "Allowed Channel List........................." in line:
                                channelList.append(configLineSplit(line))
                            elif "Allowed Channel List........................." not in line:
                                channelList.append(line.strip())
                            airewave80211aDetailDict['dca80211aAllowChannelList']=''.join(channelList)
            else:
                channelList = []
                for line in airewave80211aAllowedChannelConfig:
                    if "Auto-RF" not in line:
                        if "Allowed Channel List........................." in line:
                            channelList.append(configLineSplit(line))
                        elif "Allowed Channel List........................." not in line:
                            channelList.append(line.strip())
                        airewave80211aDetailDict['dca80211aAllowChannelList'] = ''.join(channelList)
        elif "Unused Channel List.........................." in line:
            if network49enabled ==True:
                if "dca80211aUnusedChannelList" in airewave80211aDetailDict:
                    channelList = []
                    for line in airwave80211a49UnusedChannelConfig:
                        if "Unused Channel List.........................." in line:
                            channelList.append(configLineSplit(line))
                        else:
                            channelList.append(line.strip())
                        airewave80211aDetailDict['dca80211a49UnusedChannelList']=''.join(channelList)
                else:
                    channelList = []
                    for line in airewave80211aUnusedChannelConfig:
                        if "Unused Channel List.........................." in line:
                            channelList.append(configLineSplit(line))
                        else:
                            channelList.append(line.strip())
                        airewave80211aDetailDict['dca80211aUnusedChannelList']=''.join(channelList)
            #required for countries that do not support 4.9
            else:
                channelList = []
                airewave80211aUnusedChannelConfigStartStop="Unused Channel List..........................", \
                                           "DCA Outdoor AP option.........................."
                airewave80211aUnusedChannelConfig = collectConfigSection(airewave80211aConfig,
                                                                         airewave80211aUnusedChannelConfigStartStop)
                for line in airewave80211aUnusedChannelConfig:
                    if "Unused Channel List.........................." in line:
                        channelList.append(configLineSplit(line))
                    else:
                        channelList.append(line.strip())
                    airewave80211aDetailDict['dca80211aUnusedChannelList'] = ''.join(channelList)

        elif "DCA Outdoor AP option.........................." in line:
            airewave80211aDetailDict['dca80211aOutdoorApOption'] = configLineSplit(line)
        elif "RF Group Name.................................." in line:
            airewave80211aDetailDict['rfGroup80211aRfGropuName'] = configLineSplit(line)
        elif "RF Protocol Version(MIN)......................." in line:
            airewave80211aDetailDict['rfGroup80211aProtocolVersion'] = configLineSplit(line)
        elif "RF Packet Header Version......................." in line:
            airewave80211aDetailDict['rfGroup80211aPacketHeader'] = configLineSplit(line)
        elif "Group Role(Mode)..............................." in line:
            airewave80211aDetailDict['rfGroup80211aRole'] = configLineSplit(line)
        elif "Group State...................................." in line:
            airewave80211aDetailDict['rfGroup80211aState'] = configLineSplit(line)
        elif "Group Update Interval.........................." in line:
            airewave80211aDetailDict['rfGroup80211aUpdateInterval'] = configLineSplit(line)
        elif "Group Leader..................................." in line:
            airewave80211aDetailDict['rfGroup80211aLeader'] = configLineSplit(line)
        elif "................................." in line:
            airewave80211aDetailDict['rfGroup80211aMember'] = configLineSplit(line)
        elif "Maximum/Current number of Group Member........." in line:
            airewave80211aDetailDict['rfGroup80211aMaxMember'] = configLineSplit(line)
        elif "Maximum/Current number of AP..................." in line:
            airewave80211aDetailDict['rfGroup80211aMaxAp'] = configLineSplit(line)
    airewave80211aDict['airewave80211a']=airewave80211aDetailDict
    return airewave80211aDict

#########################################################################
# Build 802.11a Cleanair Config
#
#
#########################################################################
def build80211aCleanairConfig(input, sysName):
    cleanair80211aDict={}
    cleanair80211aDetailDict={}
    cleanair80211aConfigStartStop="802.11a CleanAir Configuration","802.11a CleanAir AirQuality Summary"
    cleanair80211aConfig = collectConfigSection(input, cleanair80211aConfigStartStop)
    logger.info("Building 802.11a Cleanair Configuration for %s" % sysName)
    for line in cleanair80211aConfig:
        if "Clean Air Solution..............................." in line:
            cleanair80211aDetailDict['cleanair80211aStatus'] = configLineSplit(line)
        elif "Air Quality Settings:" in line:
            cleanair80211aDetailDict[''] = configLineSplit(line)
        elif "Air Quality Reporting........................" in line:
            cleanair80211aDetailDict['cleanair80211aQualityReport'] = configLineSplit(line)
        elif "Air Quality Reporting Period (min)..........." in line:
            cleanair80211aDetailDict['cleanair80211aQualityReportPeriod'] = configLineSplit(line)
        elif "Air Quality Alarms..........................." in line:
            cleanair80211aDetailDict['cleanair80211aQualityReportAlarms'] = configLineSplit(line)
        elif "Air Quality Alarm Threshold................" in line:
            cleanair80211aDetailDict['cleanair80211aQualityReportThreshold'] = configLineSplit(line)
        elif "Unclassified Interference.................." in line:
            cleanair80211aDetailDict['cleanair80211aUnclassInt'] = configLineSplit(line)
        elif "Unclassified Severity Threshold............" in line:
            cleanair80211aDetailDict['cleanair80211aUnclassSeverity'] = configLineSplit(line)
        elif "Interference Device Settings:" in line:
            cleanair80211aDetailDict[''] = configLineSplit(line)
        elif "Interference Device Reporting................" in line:
            cleanair80211aDetailDict['cleanair80211aDeviceReport'] = configLineSplit(line)
        elif "Interference Device Types:" in line:
            cleanair80211aDetailDict[''] = configLineSplit(line)
        elif "TDD Transmitter.........................." in line:
            if "cleanair80211aDeviceTdd" in cleanair80211aDetailDict:
                cleanair80211aDetailDict['cleanair80211aAlarmTdd'] = configLineSplit(line)
            else:
                cleanair80211aDetailDict['cleanair80211aDeviceTdd'] = configLineSplit(line)
        elif "Jammer..................................." in line:
            if "cleanair80211aDeviceJammer" in cleanair80211aDetailDict:
                cleanair80211aDetailDict['cleanair80211aAlarmJammer'] = configLineSplit(line)
            else:
                cleanair80211aDetailDict['cleanair80211aDeviceJammer'] = configLineSplit(line)
        elif "Continuous Transmitter..................." in line:
            if "cleanair80211aDeviceContin" in cleanair80211aDetailDict:
                cleanair80211aDetailDict['cleanair80211aAlarmContin'] = configLineSplit(line)
            else:
                cleanair80211aDetailDict['cleanair80211aDeviceContin'] = configLineSplit(line)
        elif "DECT-like Phone.........................." in line:
            if "cleanair80211aDeviceDect" in cleanair80211aDetailDict:
                cleanair80211aDetailDict['cleanair80211aAlarmDect'] = configLineSplit(line)
            else:
                cleanair80211aDetailDict['cleanair80211aDeviceDect'] = configLineSplit(line)
        elif "Video Camera............................." in line:
            if "cleanair80211aDeviceCamera" in cleanair80211aDetailDict:
                cleanair80211aDetailDict['cleanair80211aAlarmCamera'] = configLineSplit(line)
            else:
                cleanair80211aDetailDict['cleanair80211aDeviceCamera'] = configLineSplit(line)
        elif "WiFi Inverted............................" in line:
            if "cleanair80211aDeviceWifiInverted" in cleanair80211aDetailDict:
                cleanair80211aDetailDict['cleanair80211aAlarmWifiInverted'] = configLineSplit(line)
            else:
                cleanair80211aDetailDict['cleanair80211aDeviceWifiInverted'] = configLineSplit(line)
        elif "WiFi Invalid Channel....................." in line:
            if "cleanair80211aDeviceInvalidCh" in cleanair80211aDetailDict:
                cleanair80211aDetailDict['cleanair80211aAlarmInvalidCh'] = configLineSplit(line)
            else:
                cleanair80211aDetailDict['cleanair80211aDeviceInvalidCh'] = configLineSplit(line)
        elif "SuperAG.................................." in line:
            if "cleanair80211aDeviceSuperAg" in cleanair80211aDetailDict:
                cleanair80211aDetailDict['cleanair80211aAlarmSuperAg'] = configLineSplit(line)
            else:
                cleanair80211aDetailDict['cleanair80211aDeviceSuperAg'] = configLineSplit(line)
        elif "Canopy..................................." in line:
            if "cleanair80211aDeviceCanopy" in cleanair80211aDetailDict:
                cleanair80211aDetailDict['cleanair80211aAlarmCanopy'] = configLineSplit(line)
            else:
                cleanair80211aDetailDict['cleanair80211aDeviceCanopy'] = configLineSplit(line)
        elif "WiMax Mobile............................." in line:
            if "cleanair80211aDeviceWimaxMobile" in cleanair80211aDetailDict:
                cleanair80211aDetailDict['cleanair80211aAlarmWimaxMobile'] = configLineSplit(line)
            else:
                cleanair80211aDetailDict['cleanair80211aDeviceWimaxMobile'] = configLineSplit(line)
        elif "WiMax Fixed.............................." in line:
            if "cleanair80211aDeviceWimaxFixed" in cleanair80211aDetailDict:
                cleanair80211aDetailDict['cleanair80211aAlarmWimaxFixed'] = configLineSplit(line)
            else:
                cleanair80211aDetailDict['cleanair80211aDeviceWimaxFixed'] = configLineSplit(line)
        elif "Interference Device Alarms..................." in line:
            cleanair80211aDetailDict['cleanair80211aDeviceAlarm'] = configLineSplit(line)
        elif "Interference Device Types Triggering Alarms:" in line:
            cleanair80211aDetailDict[''] = configLineSplit(line)
        elif "CleanAir ED-RRM State........................" in line:
            cleanair80211aDetailDict['cleanair80211aEdrrmState'] = configLineSplit(line)
        elif "CleanAir ED-RRM Sensitivity.................." in line:
            cleanair80211aDetailDict['cleanair80211aEdrrmSen'] = configLineSplit(line)
        elif "CleanAir ED-RRM Custom Threshold............." in line:
            cleanair80211aDetailDict['cleanair80211aEdrrmThreshold'] = configLineSplit(line)
        elif "CleanAir Rogue Contribution.................." in line:
            cleanair80211aDetailDict['cleanair80211aRogueContrib'] = configLineSplit(line)
        elif "CleanAir Rogue Duty-Cycle Threshold.........." in line:
            cleanair80211aDetailDict['cleanair80211aRogueDutyThres'] = configLineSplit(line)
        elif "CleanAir Persistent Devices state............" in line:
            cleanair80211aDetailDict['cleanair80211aPersistDeviceState'] = configLineSplit(line)
        elif "CleanAir Persistent Device Propagation......." in line:
            cleanair80211aDetailDict['cleanair80211aPersistDeviceProp'] = configLineSplit(line)
    cleanair80211aDict['cleanair80211a']=cleanair80211aDetailDict
    return cleanair80211aDict


#########################################################################
# Build 802.11b Config
#
#
#########################################################################
def build80211bConfig(input,sysName):
    network80211bList=[]
    network80211bDict={}
    network80211bDetailDict={}
    network80211bConfigStartStop="802.11b Configuration","802.11b Advanced Configuration"
    network80211bConfig = collectConfigSection(input, network80211bConfigStartStop)
    logger.info("Building 802.11b Configuration for %s" % sysName)
    for line in network80211bConfig:
            if "802.11b Network.................................." in line:
                network80211bDetailDict['network80211bStatus'] = configLineSplit(line)
            elif "11gSupport......................................." in line:
                network80211bDetailDict['network11gSupport'] = configLineSplit(line)
            elif "11nSupport......................................." in line:
                network80211bDetailDict['network11NSupport'] = configLineSplit(line)
            elif "802.11b/g 1M Rate............................" in line:
                network80211bDetailDict['network80211b1M'] = configLineSplit(line)
            elif "802.11b/g 2M Rate............................" in line:
                network80211bDetailDict['network80211b2M'] = configLineSplit(line)
            elif "802.11b/g 5.5M Rate.........................." in line:
                network80211bDetailDict['network80211b5M'] = configLineSplit(line)
            elif "802.11b/g 11M Rate.........................." in line:
                network80211bDetailDict['network80211b11M'] = configLineSplit(line)
            elif "802.11g 6M Rate.............................." in line:
                network80211bDetailDict['network80211g6M'] = configLineSplit(line)
            elif "802.11g 9M Rate.............................." in line:
                network80211bDetailDict['network80211g9M'] = configLineSplit(line)
            elif "802.11g 12M Rate............................." in line:
                network80211bDetailDict['network80211g12M'] = configLineSplit(line)
            elif "802.11g 18M Rate............................." in line:
                network80211bDetailDict['network80211g18M'] = configLineSplit(line)
            elif "802.11g 24M Rate............................." in line:
                network80211bDetailDict['network80211g24M'] = configLineSplit(line)
            elif "802.11g 36M Rate............................." in line:
                network80211bDetailDict['network80211g36M'] = configLineSplit(line)
            elif "802.11g 48M Rate............................." in line:
                network80211bDetailDict['network80211g48M'] = configLineSplit(line)
            elif "802.11g 54M Rate............................." in line:
                network80211bDetailDict['network80211g54M'] = configLineSplit(line)
            elif "MCS 0........................................" in line:
                network80211bDetailDict['network80211bRateMcs0'] = configLineSplit(line)
            elif "MCS 1........................................" in line:
                network80211bDetailDict['network80211bRateMcs1'] = configLineSplit(line)
            elif "MCS 2........................................" in line:
                network80211bDetailDict['network80211bRateMcs2'] = configLineSplit(line)
            elif "MCS 3........................................" in line:
                network80211bDetailDict['network80211bRateMcs3'] = configLineSplit(line)
            elif "MCS 4........................................" in line:
                network80211bDetailDict['network80211bRateMcs4'] = configLineSplit(line)
            elif "MCS 5........................................" in line:
                network80211bDetailDict['network80211bRateMcs5'] = configLineSplit(line)
            elif "MCS 6........................................" in line:
                network80211bDetailDict['network80211bRateMcs6'] = configLineSplit(line)
            elif "MCS 7........................................" in line:
                network80211bDetailDict['network80211bRateMcs7'] = configLineSplit(line)
            elif "MCS 8........................................" in line:
                network80211bDetailDict['network80211bRateMcs8'] = configLineSplit(line)
            elif "MCS 9........................................" in line:
                network80211bDetailDict['network80211bRateMcs9'] = configLineSplit(line)
            elif "MCS 10......................................." in line:
                network80211bDetailDict['network80211bRateMcs10'] = configLineSplit(line)
            elif "MCS 11......................................." in line:
                network80211bDetailDict['network80211bRateMcs11'] = configLineSplit(line)
            elif "MCS 12......................................." in line:
                network80211bDetailDict['network80211bRateMcs12'] = configLineSplit(line)
            elif "MCS 13......................................." in line:
                network80211bDetailDict['network80211bRateMcs13'] = configLineSplit(line)
            elif "MCS 14......................................." in line:
                network80211bDetailDict['network80211bRateMcs14'] = configLineSplit(line)
            elif "MCS 15......................................." in line:
                network80211bDetailDict['network80211bRateMcs15'] = configLineSplit(line)
            elif "MCS 16......................................." in line:
                network80211bDetailDict['network80211bRateMcs16'] = configLineSplit(line)
            elif "MCS 17......................................." in line:
                network80211bDetailDict['network80211bRateMcs17'] = configLineSplit(line)
            elif "MCS 18......................................." in line:
                network80211bDetailDict['network80211bRateMcs18'] = configLineSplit(line)
            elif "MCS 19......................................." in line:
                network80211bDetailDict['network80211bRateMcs19'] = configLineSplit(line)
            elif "MCS 20......................................." in line:
                network80211bDetailDict['network80211bRateMcs20'] = configLineSplit(line)
            elif "MCS 21......................................." in line:
                network80211bDetailDict['network80211bRateMcs21'] = configLineSplit(line)
            elif "MCS 22......................................." in line:
                network80211bDetailDict['network80211bRateMcs22'] = configLineSplit(line)
            elif "MCS 23......................................." in line:
                network80211bDetailDict['network80211bRateMcs23'] = configLineSplit(line)
            elif "MCS 24......................................." in line:
                network80211bDetailDict['network80211bRateMcs24'] = configLineSplit(line)
            elif "MCS 25......................................." in line:
                network80211bDetailDict['network80211bRateMcs25'] = configLineSplit(line)
            elif "MCS 26......................................." in line:
                network80211bDetailDict['network80211bRateMcs26'] = configLineSplit(line)
            elif "MCS 27......................................." in line:
                network80211bDetailDict['network80211bRateMcs27'] = configLineSplit(line)
            elif "MCS 28......................................." in line:
                network80211bDetailDict['network80211bRateMcs28'] = configLineSplit(line)
            elif "MCS 29......................................." in line:
                network80211bDetailDict['network80211bRateMcs29'] = configLineSplit(line)
            elif "MCS 30......................................." in line:
                network80211bDetailDict['network80211bRateMcs30'] = configLineSplit(line)
            elif "MCS 31......................................." in line:
                network80211bDetailDict['network80211bRateMcs31'] = configLineSplit(line)
            elif "Priority 0..............................." in line:
                if "network80211bMpduP0" in network80211bDetailDict:
                    network80211bDetailDict['network80211bMsduP0'] = configLineSplit(line)
                else:
                    network80211bDetailDict['network80211bMpduP0'] = configLineSplit(line)
            elif "Priority 1..............................." in line:
                if "network80211bMpduP1" in network80211bDetailDict:
                    network80211bDetailDict['network80211bMsduP1'] = configLineSplit(line)
                else:
                    network80211bDetailDict['network80211bMpduP1'] = configLineSplit(line)
            elif "Priority 2..............................." in line:
                if "network80211bMpduP2" in network80211bDetailDict:
                    network80211bDetailDict['network80211bMsduP2'] = configLineSplit(line)
                else:
                    network80211bDetailDict['network80211bMpduP2'] = configLineSplit(line)
            elif "Priority 3..............................." in line:
                if "network80211bMpduP3" in network80211bDetailDict:
                    network80211bDetailDict['network80211bMsduP3'] = configLineSplit(line)
                else:
                    network80211bDetailDict['network80211bMpduP3'] = configLineSplit(line)
            elif "Priority 4..............................." in line:
                if "network80211bMpduP4" in network80211bDetailDict:
                    network80211bDetailDict['network80211bMsduP4'] = configLineSplit(line)
                else:
                    network80211bDetailDict['network80211bMpduP4'] = configLineSplit(line)
            elif "Priority 5..............................." in line:
                if "network80211bMpduP5" in network80211bDetailDict:
                    network80211bDetailDict['network80211bMsduP5'] = configLineSplit(line)
                else:
                    network80211bDetailDict['network80211bMpduP5'] = configLineSplit(line)
            elif "Priority 6..............................." in line:
                if "network80211bMpduP6" in network80211bDetailDict:
                    network80211bDetailDict['network80211bMsduP6'] = configLineSplit(line)
                else:
                    network80211bDetailDict['network80211bMpduP6'] = configLineSplit(line)
            elif "Priority 7..............................." in line:
                if "network80211bMpduP7" in network80211bDetailDict:
                    network80211bDetailDict['network80211bMsduP7'] = configLineSplit(line)
                else:
                    network80211bDetailDict['network80211bMpduP7'] = configLineSplit(line)
            elif "Aggregation scheduler...................." in line:
                network80211bDetailDict['network80211bMpduAgScheduler'] = configLineSplit(line)
            elif "Frame Burst.............................." in line:
                network80211bDetailDict['network80211bFrameBurst'] = configLineSplit(line)
            elif "Realtime Timeout....................." in line:
                network80211bDetailDict['network80211bRealtimeTimeout'] = configLineSplit(line)
            elif "Non Realtime Timeout................." in line:
                network80211bDetailDict['network80211bNonRealtimeTimeout'] =configLineSplit(line)
            elif "A-MSDU Max Subframes ........................" in line:
                network80211bDetailDict['network80211bMsduMaxSubFrames'] = configLineSplit(line)
            elif "A-MSDU MAX Length ..........................." in line:
                network80211bDetailDict['network80211bMsduMaxLength'] =configLineSplit(line)
            elif "Rifs Rx ....................................." in line:
                network80211bDetailDict['network80211bMsduRifsRx'] = configLineSplit(line)
            elif "Guard Interval .............................." in line:
                network80211bDetailDict['network80211bGuardInt'] = configLineSplit(line)
            elif "Beacon Interval.................................." in line:
                network80211bDetailDict['network80211bBeaconInt'] = configLineSplit(line)
            elif "CF Pollable mandatory............................" in line:
                network80211bDetailDict['network80211bCfPollMand'] = configLineSplit(line)
            elif "CF Poll Request mandatory........................" in line:
                network80211bDetailDict['network80211bCfPollRequest'] = configLineSplit(line)
            elif "CFP Period......................................." in line:
                network80211bDetailDict['network80211bCfpPeriod'] = configLineSplit(line)
            elif "CFP Maximum Duration............................." in line:
                network80211bDetailDict['network80211bCfpMaxDur'] = configLineSplit(line)
            elif "Default Channel.................................." in line:
                network80211bDetailDict['network80211bDefaultChannel'] = configLineSplit(line)
            elif "Default Tx Power Level..........................." in line:
                network80211bDetailDict['network80211bDefaultTx'] = configLineSplit(line)
            elif "DTPC  Status....................................." in line:
                network80211bDetailDict['network80211bDtpc'] = configLineSplit(line)
            elif "Fragmentation Threshold.........................." in line:
                network80211bDetailDict['network80211bFragThres'] = configLineSplit(line)
            elif "RSSI Low Check..................................." in line:
                network80211bDetailDict['network80211bRssiLow'] = configLineSplit(line)
            elif "RSSI Threshold..................................." in line:
                network80211bDetailDict['network80211bRssiThres'] = configLineSplit(line)
            elif "Call Admission Limit  ..........................." in line:
                network80211bDetailDict['network80211bCallAdmissionLimit'] = configLineSplit(line)
            elif "G711 CU Quantum ................................." in line:
                network80211bDetailDict['network80211bG711CuQuantum'] = configLineSplit(line)
            elif "ED Threshold....................................." in line:
                network80211bDetailDict['network80211bEdThresh'] = configLineSplit(line)
            elif "PBCC mandatory..................................." in line:
                network80211bDetailDict['network80211bPbcc'] = configLineSplit(line)
            elif "Short Preamble mandatory........................." in line:
                network80211bDetailDict['network80211bShortPreamble'] = configLineSplit(line)
            elif "Short Retry Limit................................" in line:
                network80211bDetailDict['network80211bRtsThresh'] = configLineSplit(line)
            elif "EDCA profile type................................" in line:
                network80211bDetailDict['network80211bEdcaProfile'] = configLineSplit(line)
            elif "Legacy Tx Beamforming setting...................." in line:
                network80211bDetailDict['network80211bLegacyBeam'] = configLineSplit(line)
            elif "Traffic Stream Metrics Status...................." in line:
                network80211bDetailDict['network80211bTsm'] = configLineSplit(line)
            elif "Expedited BW Request Status......................" in line:
                network80211bDetailDict['network80211bExBandwidth'] = configLineSplit(line)
            elif "World Mode......................................." in line:
                network80211bDetailDict['network80211bWorldMode'] = configLineSplit(line)
            elif "Voice MAC optimization status...................." in line:
                network80211bDetailDict['network80211bVoiceMacOpt'] = configLineSplit(line)
            elif "Voice AC - Admission control (ACM)............" in line:
                network80211bDetailDict['voiceAdmissionControl'] = configLineSplit(line)
            elif "Voice Stream-Size............................." in line:
                network80211bDetailDict['voiceStreamSize'] = configLineSplit(line)
            elif "Voice Max-Streams............................." in line:
                network80211bDetailDict['voiceMaxStream'] = configLineSplit(line)
            elif "Voice max RF bandwidth........................" in line:
                network80211bDetailDict['voiceMaxRfBandwidth'] = configLineSplit(line)
            elif "Voice reserved roaming bandwidth.............." in line:
                network80211bDetailDict['voiceReserveBandwidth'] = configLineSplit(line)
            elif "Voice CAC Method ............................." in line:
                network80211bDetailDict['voiceCacMethod'] = configLineSplit(line)
            elif "Voice tspec inactivity timeout................" in line:
                network80211bDetailDict['voiceTspectTimeout'] = configLineSplit(line)
            elif "SIP based CAC ................................" in line:
                if "voiceSipCac" in network80211bDetailDict:
                    network80211bDetailDict['videoSipCac']=configLineSplit(line)
                else:
                    network80211bDetailDict['voiceSipCac'] = configLineSplit(line)
            elif "SIP Codec Type ..............................." in line:
                network80211bDetailDict['voiceSipCacCodec'] = configLineSplit(line)
            elif "SIP call bandwidth ..........................." in line:
                network80211bDetailDict['voiceSipCallBandwidth'] = configLineSplit(line)
            elif "SIP call bandwith sample-size ................" in line:
                network80211bDetailDict['voiceSipCallBandwidthSample'] = configLineSplit(line)
            elif "Video AC - Admission control (ACM)............" in line:
                network80211bDetailDict['videoAdmissionControl'] = configLineSplit(line)
            elif "Video max RF bandwidth........................" in line:
                network80211bDetailDict['videoMaxRfBandwidth'] = configLineSplit(line)
            elif "Video reserved roaming bandwidth.............." in line:
                network80211bDetailDict['videoReserveBandwidth'] = configLineSplit(line)
            elif "Video load-based CAC mode....................." in line:
                network80211bDetailDict['videoALoadCacMode'] = configLineSplit(line)
            elif "Video CAC Method ............................." in line:
                network80211bDetailDict['videoCacMethod'] = configLineSplit(line)
            elif "Best-effort AC - Admission control (ACM)......" in line:
                network80211bDetailDict['bestEffortAdmissionControl'] = configLineSplit(line)
            elif "Background AC - Admission control (ACM)......." in line:
                network80211bDetailDict['backGroupAdmissionControl'] = configLineSplit(line)
            elif "Maximum Number of Clients per AP................." in line:
                network80211bDetailDict['network80211bMaxClientsRadio'] = configLineSplit(line)
    network80211bDict['network80211b']=network80211bDetailDict
    return network80211bDict
#########################################################################
# Build 802.11b Airewave Configuration
#
#
#########################################################################
def build80211bAirewaveConfig(input,sysName):
    airewave80211bDict={}
    airewave80211bDetailDict={}
    airewave80211bConfigStartStop="802.11b Airewave Director Configuration","802.11b CleanAir Configuration"
    airewave80211bConfig = collectConfigSection(input, airewave80211bConfigStartStop)
    logger.info("Building 802.11b Airewave Configuration for %s" % sysName)
    for line in airewave80211bConfig:
        if "Channel Update Logging........................." in line:
            airewave80211bDetailDict['channelUpdateLog'] = configLineSplit(line)
        elif "Coverage Profile Logging......................." in line:
            airewave80211bDetailDict['channelCoverageProfileLog'] = configLineSplit(line)
        elif "Foreign Profile Logging........................" in line:
            airewave80211bDetailDict['foreignProfileLog'] = configLineSplit(line)
        elif "Load Profile Logging..........................." in line:
            airewave80211bDetailDict['loadProfileLog'] = configLineSplit(line)
        elif "Noise Profile Logging.........................." in line:
            airewave80211bDetailDict['noiseProfileLog'] = configLineSplit(line)
        elif "Performance Profile Logging...................." in line:
            airewave80211bDetailDict['performanceProfileLog'] = configLineSplit(line)
        elif "TxPower Update Logging........................." in line:
            airewave80211bDetailDict['txPowerUpdateLog'] = configLineSplit(line)
        elif "802.11b Global Interference threshold.........." in line:
            airewave80211bDetailDict['global80211bIntThreshold'] = configLineSplit(line)
        elif "02.11b Global noise threshold................." in line:
            airewave80211bDetailDict['global80211bNoiseThreshold'] = configLineSplit(line)
        elif "802.11b Global RF utilization threshold........" in line:
            airewave80211bDetailDict['global80211bRfUtilThreshold'] = configLineSplit(line)
        elif "802.11b Global throughput threshold............" in line:
            airewave80211bDetailDict['global80211bTputThreshold'] = configLineSplit(line)
        elif "802.11b Global clients threshold..............." in line:
            airewave80211bDetailDict['global80211bClientsThreshold'] = configLineSplit(line)
        elif "802.11b Monitor Mode..........................." in line:
            airewave80211bDetailDict['monitorMode80211b'] = configLineSplit(line)
        elif "802.11b Monitor Channels......................." in line:
            airewave80211bDetailDict['monitor80211bchannels'] = configLineSplit(line)
        elif "802.11b RRM Neighbor Discovery Type............" in line:
            airewave80211bDetailDict['monitor80211bRrmDiscover'] = configLineSplit(line)
        elif "802.11b RRM Neighbor RSSI Normalization........" in line:
            airewave80211bDetailDict['monitor80211bRrmNeighRssi'] = configLineSplit(line)
        elif "802.11b AP Coverage Interval..................." in line:
            airewave80211bDetailDict['monitor80211bApCoverageInterval'] = configLineSplit(line)
        elif "802.11b AP Load Interval......................." in line:
            airewave80211bDetailDict['monitor80211bApLoadInterval'] = configLineSplit(line)
        elif "802.11b AP Monitor Measurement Interval........" in line:
            airewave80211bDetailDict['monitor80211bApMonitorMeasure'] = configLineSplit(line)
        elif "802.11b AP Neighbor Timeout Factor............." in line:
            airewave80211bDetailDict['monitor80211bApNeighborTimeout'] = configLineSplit(line)
        elif "802.11b AP Report Measurement Interval........." in line:
            airewave80211bDetailDict['monitor80211bApMeasurementInt'] = configLineSplit(line)
        elif "Transmit Power Assignment Mode................." in line:
            airewave80211bDetailDict['tpc80211bAssignmentMode'] = configLineSplit(line)
        elif "Transmit Power Update Interval................." in line:
            airewave80211bDetailDict['tpc80211bUpdateInterval'] = configLineSplit(line)
        elif "Transmit Power Threshold......................." in line:
            airewave80211bDetailDict['tpc80211bThreshold'] = configLineSplit(line)
        elif "Transmit Power Neighbor Count.................." in line:
            airewave80211bDetailDict['tpc80211bNeighCount'] = configLineSplit(line)
        elif "Min Transmit Power............................." in line:
            airewave80211bDetailDict['tpc80211bMinPower'] = configLineSplit(line)
        elif "Max Transmit Power............................." in line:
            airewave80211bDetailDict['tpc80211bMaxPower'] = configLineSplit(line)
        elif "Noise........................................" in line:
            if "tpc80211bNoise" in airewave80211bDetailDict:
                airewave80211bDetailDict['dca80211bNoise'] = configLineSplit(line)
            else:
                airewave80211bDetailDict['tpc80211bNoise'] = configLineSplit(line)
        elif "Interference................................." in line:
            if "tpc80211bInterference" in airewave80211bDetailDict:
                airewave80211bDetailDict['dca80211bInterference'] = configLineSplit(line)
            else:
                airewave80211bDetailDict['tpc80211bInterference'] = configLineSplit(line)
        elif "Load........................................." in line:
            if "tpc80211bLoad" in airewave80211bDetailDict:
                airewave80211bDetailDict['dca80211bLoad'] = configLineSplit(line)
            else:
                airewave80211bDetailDict['tpc80211bLoad'] = configLineSplit(line)
        elif "Device Aware................................." in line:
            if "tpc80211bDeviceAware" in airewave80211bDetailDict:
                airewave80211bDetailDict['dca80211bDeviceAware'] = configLineSplit(line)
            else:
                airewave80211bDetailDict['tpc80211bDeviceAware'] = configLineSplit(line)
        elif "Transmit Power Assignment Leader..............." in line:
            airewave80211bDetailDict['tpc80211bTpcLeader'] = configLineSplit(line)
        elif "Last Run......................................." in line:
            if "tpc80211bLastRun" in airewave80211bDetailDict:
                if "dca80211bLastRun" in airewave80211bDetailDict:
                    airewave80211bDetailDict['rfGroup80211bLastRun'] = configLineSplit(line)
                else:
                    airewave80211bDetailDict['dca80211bLastRun'] = configLineSplit(line)
            else:
                airewave80211bDetailDict['tpc80211bLastRun'] = configLineSplit(line)
        elif "Last Run Time.................................." in line:
            if "tpc80211bLastRunTime" in airewave80211bDetailDict:
                airewave80211bDetailDict['dca80211bLastRunTime'] = configLineSplit(line)
            else:
                airewave80211bDetailDict['tpc80211bLastRunTime'] = configLineSplit(line)
        elif "TPC Mode......................................." in line:
            airewave80211bDetailDict['tpc80211bMode'] = configLineSplit(line)
        elif "802.11b Coverage Hole Detection Mode..........." in line:
            airewave80211bDetailDict['chd80211bMode'] = configLineSplit(line)
        elif "802.11b Coverage Voice Packet Count............" in line:
            airewave80211bDetailDict['chd80211bVoicePacketCount'] = configLineSplit(line)
        elif "802.11b Coverage Voice Packet Percentage......." in line:
            airewave80211bDetailDict['chd80211bVoicePacketPercentage'] = configLineSplit(line)
        elif "802.11b Coverage Voice RSSI Threshold.........." in line:
            airewave80211bDetailDict['chd80211bVoiceRssi'] = configLineSplit(line)
        elif "802.11b Coverage Data Packet Count............." in line:
            airewave80211bDetailDict['chd80211bDataPacketCount'] = configLineSplit(line)
        elif "802.11b Coverage Data Packet Percentage........" in line:
            airewave80211bDetailDict['chd80211bDataPacketPercentage'] = configLineSplit(line)
        elif "802.11b Coverage Data RSSI Threshold..........." in line:
            airewave80211bDetailDict['chd80211bCoverageDataRssi'] = configLineSplit(line)
        elif "802.11b Global coverage exception level........" in line:
            airewave80211bDetailDict['chd80211bGlobalCoverageException'] = configLineSplit(line)
        elif "802.11b Global client minimum exception lev...." in line:
            airewave80211bDetailDict['chd80211bGlobalClientMinimum'] = configLineSplit(line)
        elif "802.11b OptimizedRoaming Mode.................." in line:
            airewave80211bDetailDict['optimizedRoaming80211bMode'] = configLineSplit(line)
        elif "802.11b OptimizedRoaming Reporting Interval...." in line:
            airewave80211bDetailDict['optimizedRoaming80211bReportingInterval'] = configLineSplit(line)
        elif "802.11b OptimizedRoaming Rate Threshold........" in line:
            airewave80211bDetailDict['optimizedRoaming80211bRateThreshold'] = configLineSplit(line)
        elif "802.11b OptimizedRoaming Hysteresis............" in line:
            airewave80211bDetailDict['optimizedRoaming80211bHysteresis'] = configLineSplit(line)
        elif "Channel Assignment Mode........................" in line:
            airewave80211bDetailDict['dca80211bChannelAssignment'] = configLineSplit(line)
        elif "Channel Update Interval........................" in line:
            airewave80211bDetailDict['dca80211bChannelUpdate'] = configLineSplit(line)
        elif "Anchor time (Hour of the day).................." in line:
            airewave80211bDetailDict['dca80211bAnchorTime'] = configLineSplit(line)
        elif "CleanAir Event-driven RRM option..............." in line:
            airewave80211bDetailDict['dca80211bCleanairRrm'] = configLineSplit(line)
        elif "Channel Assignment Leader......................" in line:
            airewave80211bDetailDict['dca80211bChannelAssignmentLeader'] = configLineSplit(line)
        #elif "DCA Sensitivity Level.........................." in line:
        #    airewave80211bDetailDict['dca80211bSensitivityLevel'] = configLineSplit(line)
        elif "DCA Minimum Energy Limit......................." in line:
            airewave80211bDetailDict['dcaMinEnergyLimit'] = configLineSplit(line)
        elif "Minimum......................................" in line:
            if "dca80211bChannelEnergyLevelMin" in airewave80211bDetailDict:
                airewave80211bDetailDict['dca80211bChannelDwellMin'] = configLineSplit(line)
            else:
                airewave80211bDetailDict['dca80211bChannelEnergyLevelMin'] = configLineSplit(line)
        elif "Average......................................" in line:
            if "dca80211bChannelEnergyLevelAvg" in airewave80211bDetailDict:
                airewave80211bDetailDict['dca80211bChannelDwellAvg'] = configLineSplit(line)
            else:
                airewave80211bDetailDict['dca80211bChannelEnergyLevelAvg'] = configLineSplit(line)
        elif "Maximum......................................" in line:
            if "dca80211bChannelEnergyLevelMax" in airewave80211bDetailDict:
                airewave80211bDetailDict['dca80211bChannelDwellMax'] = configLineSplit(line)
            else:
                airewave80211bDetailDict['dca80211bChannelEnergyLevelMax'] = configLineSplit(line)
        # Used incorrect line description for allowed Channels
        #elif "Allowed Channel List" in line:
        #    airewave80211bDetailDict['dca80211bAllowChannelList'] = configLineSplit(line)
        elif "802.11b Auto-RF Allowed Channel List........... " in line:
            airewave80211bDetailDict['dca80211bAllowChannelList'] = configLineSplit(line)
        elif "Auto-RF Unused Channel List...................." in line:
            airewave80211bDetailDict['dca80211bUnusedChannelList']=configLineSplit(line)
        elif "RF Group Name.................................." in line:
            airewave80211bDetailDict['rfGroup80211bRfGropuName'] = configLineSplit(line)
        elif "RF Protocol Version(MIN)......................." in line:
            airewave80211bDetailDict['rfGroup80211bProtocolVersion'] = configLineSplit(line)
        elif "RF Packet Header Version......................." in line:
            airewave80211bDetailDict['rfGroup80211bPacketHeader'] = configLineSplit(line)
        elif "Group Role(Mode)..............................." in line:
            airewave80211bDetailDict['rfGroup80211bRole'] = configLineSplit(line)
        elif "Group State...................................." in line:
            airewave80211bDetailDict['rfGroup80211bState'] = configLineSplit(line)
        elif "Group Update Interval.........................." in line:
            airewave80211bDetailDict['rfGroup80211bUpdateInterval'] = configLineSplit(line)
        elif "Group Leader..................................." in line:
            airewave80211bDetailDict['rfGroup80211bLeader'] = configLineSplit(line)
        elif "................................." in line:
            airewave80211bDetailDict['rfGroup80211bMember'] = configLineSplit(line)
        elif "Maximum/Current number of Group Member........." in line:
            airewave80211bDetailDict['rfGroup80211bMaxMember'] = configLineSplit(line)
        elif "Maximum/Current number of AP..................." in line:
            airewave80211bDetailDict['rfGroup80211bMaxAp'] = configLineSplit(line)
    airewave80211bDict['airewave80211b']=airewave80211bDetailDict
    return airewave80211bDict
#########################################################################
# Build 802.11b Cleanair Config
#
#
#########################################################################
def build80211bCleanairConfig(input,sysName):
    cleanair80211bDict={}
    cleanair80211bDetailDict={}
    cleanair80211bConfigStartStop="802.11b CleanAir Configuration","802.11b CleanAir AirQuality Summary"
    cleanair80211bConfig = collectConfigSection(input, cleanair80211bConfigStartStop)
    logger.info("Building 802.11b Cleanair Configuration for %s" % sysName)
    for line in cleanair80211bConfig:
        if "Clean Air Solution..............................." in line:
            cleanair80211bDetailDict['cleanair80211bStatus'] = configLineSplit(line)
        elif "Air Quality Reporting........................" in line:
            cleanair80211bDetailDict['cleanair80211bQualityReport'] = configLineSplit(line)
        elif "Air Quality Reporting Period (min)..........." in line:
            cleanair80211bDetailDict['cleanair80211bQualityReportPeriod'] = configLineSplit(line)
        elif "Air Quality Alarms..........................." in line:
            cleanair80211bDetailDict['cleanair80211bQualityReportAlarms'] = configLineSplit(line)
        elif "Air Quality Alarm Threshold................" in line:
            cleanair80211bDetailDict['cleanair80211bQualityReportThreshold'] = configLineSplit(line)
        elif "Unclassified Interference.................." in line:
            cleanair80211bDetailDict['cleanair80211bUnclassInt'] = configLineSplit(line)
        elif "Unclassified Severity Threshold............" in line:
            cleanair80211bDetailDict['cleanair80211bUnclassSeverity'] = configLineSplit(line)
        elif "Interference Device Reporting................" in line:
            cleanair80211bDetailDict['cleanair80211bDeviceReport'] = configLineSplit(line)
        elif "TDD Transmitter.........................." in line:
            if "cleanair80211bDeviceTdd" in cleanair80211bDetailDict:
                cleanair80211bDetailDict['cleanair80211bAlarmTdd'] = configLineSplit(line)
            else:
                cleanair80211bDetailDict['cleanair80211bDeviceTdd'] = configLineSplit(line)
        elif "Jammer..................................." in line:
            if "cleanair80211bDeviceJammer" in cleanair80211bDetailDict:
                cleanair80211bDetailDict['cleanair80211bAlarmJammer'] = configLineSplit(line)
            else:
                cleanair80211bDetailDict['cleanair80211bDeviceJammer'] = configLineSplit(line)
        elif "Continuous Transmitter..................." in line:
            if "cleanair80211bDeviceContin" in cleanair80211bDetailDict:
                cleanair80211bDetailDict['cleanair80211bAlarmContin'] = configLineSplit(line)
            else:
                cleanair80211bDetailDict['cleanair80211bDeviceContin'] = configLineSplit(line)
        elif "DECT-like Phone.........................." in line:
            if "cleanair80211bDeviceDect" in cleanair80211bDetailDict:
                cleanair80211bDetailDict['cleanair80211bAlarmDect'] = configLineSplit(line)
            else:
                cleanair80211bDetailDict['cleanair80211bDeviceDect'] = configLineSplit(line)
        elif "Video Camera............................." in line:
            if "cleanair80211bDeviceCamera" in cleanair80211bDetailDict:
                cleanair80211bDetailDict['cleanair80211bAlarmCamera'] = configLineSplit(line)
            else:
                cleanair80211bDetailDict['cleanair80211bDeviceCamera'] = configLineSplit(line)
        elif "WiFi Inverted............................" in line:
            if "cleanair80211bDeviceWifiInverted" in cleanair80211bDetailDict:
                cleanair80211bDetailDict['cleanair80211bAlarmWifiInverted'] = configLineSplit(line)
            else:
                cleanair80211bDetailDict['cleanair80211bDeviceWifiInverted'] = configLineSplit(line)
        elif "WiFi Invalid Channel....................." in line:
            if "cleanair80211bDeviceInvalidCh" in cleanair80211bDetailDict:
                cleanair80211bDetailDict['cleanair80211bAlarmInvalidCh'] = configLineSplit(line)
            else:
                cleanair80211bDetailDict['cleanair80211bDeviceInvalidCh'] = configLineSplit(line)
        elif "SuperAG.................................." in line:
            if "cleanair80211bDeviceSuperAg" in cleanair80211bDetailDict:
                cleanair80211bDetailDict['cleanair80211bAlarmSuperAg'] = configLineSplit(line)
            else:
                cleanair80211bDetailDict['cleanair80211bDeviceSuperAg'] = configLineSplit(line)
        elif "Canopy..................................." in line:
            if "cleanair80211bDeviceCanopy" in cleanair80211bDetailDict:
                cleanair80211bDetailDict['cleanair80211bAlarmCanopy'] = configLineSplit(line)
            else:
                cleanair80211bDetailDict['cleanair80211bDeviceCanopy'] = configLineSplit(line)
        elif "WiMax Mobile............................." in line:
            if "cleanair80211bDeviceWimaxMobile" in cleanair80211bDetailDict:
                cleanair80211bDetailDict['cleanair80211bAlarmWimaxMobile'] = configLineSplit(line)
            else:
                cleanair80211bDetailDict['cleanair80211bDeviceWimaxMobile'] = configLineSplit(line)
        elif "WiMax Fixed.............................." in line:
            if "cleanair80211bDeviceWimaxFixed" in cleanair80211bDetailDict:
                cleanair80211bDetailDict['cleanair80211bAlarmWimaxFixed'] = configLineSplit(line)
            else:
                cleanair80211bDetailDict['cleanair80211bDeviceWimaxFixed'] = configLineSplit(line)
        elif "Bluetooth Link..........................." in line:
            if "cleanair80211bDeviceBluetoothLink" in cleanair80211bDetailDict:
                cleanair80211bDetailDict['cleanair80211bAlarmBluetoothLink'] = configLineSplit(line)
            else:
                cleanair80211bDetailDict['cleanair80211bDeviceBluetoothLink'] = configLineSplit(line)
        elif "Microwave Oven..........................." in line:
            if "cleanair80211bDeviceMicrowave" in cleanair80211bDetailDict:
                cleanair80211bDetailDict['cleanair80211bAlarmMicrowave'] = configLineSplit(line)
            else:
                cleanair80211bDetailDict['cleanair80211bDeviceMicrowave'] = configLineSplit(line)
        elif "802.11 FH................................" in line:
            if "cleanair80211bDeviceFh" in cleanair80211bDetailDict:
                cleanair80211bDetailDict['cleanair80211bAlarmFh'] = configLineSplit(line)
            else:
                cleanair80211bDetailDict['cleanair80211bDeviceFh'] = configLineSplit(line)
        elif "Bluetooth Discovery......................" in line:
            if "cleanair80211bDeviceBluetoothDis" in cleanair80211bDetailDict:
                cleanair80211bDetailDict['cleanair80211bAlarmBluetoothDis'] = configLineSplit(line)
            else:
                cleanair80211bDetailDict['cleanair80211bDeviceBluetoothDis'] = configLineSplit(line)
        elif "802.15.4................................." in line:
            if "cleanair80211bDevice802154" in cleanair80211bDetailDict:
                cleanair80211bDetailDict['cleanair80211bAlarm802154'] = configLineSplit(line)
            else:
                cleanair80211bDetailDict['cleanair80211bDevice802154'] = configLineSplit(line)
        elif "Microsoft Device........................." in line:
            if "cleanair80211bDeviceMicrosoft" in cleanair80211bDetailDict:
                cleanair80211bDetailDict['cleanair80211bAlarmMicrosoft'] = configLineSplit(line)
            else:
                cleanair80211bDetailDict['cleanair80211bDeviceMicrosoft'] = configLineSplit(line)
        elif "BLE Beacon..............................." in line:
            if "cleanair80211bDeviceBleBeacon" in cleanair80211bDetailDict:
                cleanair80211bDetailDict['cleanair80211bAlarmBleBeacon'] = configLineSplit(line)
            else:
                cleanair80211bDetailDict['cleanair80211bDeviceBleBeacon'] = configLineSplit(line)
        elif "Interference Device Alarms..................." in line:
            cleanair80211bDetailDict['cleanair80211bDeviceAlarm'] = configLineSplit(line)
        elif "CleanAir ED-RRM State........................" in line:
            cleanair80211bDetailDict['cleanair80211bEdrrmState'] = configLineSplit(line)
        elif "CleanAir ED-RRM Sensitivity.................." in line:
            cleanair80211bDetailDict['cleanair80211bEdrrmSen'] = configLineSplit(line)
        elif "CleanAir ED-RRM Custom Threshold............." in line:
            cleanair80211bDetailDict['cleanair80211bEdrrmThreshold'] = configLineSplit(line)
        elif "CleanAir Rogue Contribution.................." in line:
            cleanair80211bDetailDict['cleanair80211bRogueContrib'] = configLineSplit(line)
        elif "CleanAir Rogue Duty-Cycle Threshold.........." in line:
            cleanair80211bDetailDict['cleanair80211bRogueDutyThres'] = configLineSplit(line)
        elif "CleanAir Persistent Devices state............" in line:
            cleanair80211bDetailDict['cleanair80211bPersistDeviceState'] = configLineSplit(line)
        elif "CleanAir Persistent Device Propagation......." in line:
            cleanair80211bDetailDict['cleanair80211bPersistDeviceProp'] = configLineSplit(line)
    cleanair80211bDict['cleanair80211b']=cleanair80211bDetailDict
    return cleanair80211bDict

#########################################################################
# Build FRA Config
#
#
#########################################################################
def buildFraConfig(input,sysName):
    fraDict={}
    fraDetailDict={}
    fraConfigStartStop="RF Density Optimization Configurations","WLAN Configuration Information"
    fraConfig = collectConfigSection(input, fraConfigStartStop)
    logger.info("Building FRA Configuration for %s" % sysName)
    for line in fraConfig:
        if "FRA State........................................" in line:
            fraDetailDict['fraState'] = configLineSplit(line)
        elif "FRA Sensitivity.................................." in line:
            fraDetailDict['fraSensitivity'] = configLineSplit(line)
        elif "FRA Interval....................................." in line:
            fraDetailDict['fraInterval'] = configLineSplit(line)
        elif "Last Run......................................." in line:
            fraDetailDict['fraLastRun'] = configLineSplit(line)
        elif "Last Run Time.................................." in line:
            fraDetailDict['fraLastRunTime'] = configLineSplit(line)
        elif "Service Priority................................." in line:
            fraDetailDict['fraServicePriority'] = configLineSplit(line)
        elif "Macro to micro transition threshold............" in line:
            fraDetailDict['fraMacroMicroThreshold'] = configLineSplit(line)
        elif "micro to Macro transition threshold............" in line:
            fraDetailDict['fraMicroMacroThreshold'] = configLineSplit(line)
        elif "micro-Macro transition minimum client count...." in line:
            fraDetailDict['fraMicroMacroTransitionMinClienCount'] = configLineSplit(line)
        elif "micro-Macro transition client balancing win...." in line:
            fraDetailDict['fraMicroMacroClientBalanceWindow'] = configLineSplit(line)
        elif "Probe suppression mode........................." in line:
            fraDetailDict['fraProbeSuppressionMode'] = configLineSplit(line)
        elif "Probe suppression validity window.............." in line:
            fraDetailDict['fraProbeSuppressionValidity'] = configLineSplit(line)
        elif "Probe suppression aggregate window............." in line:
            fraDetailDict['fraProbeSuppressionAggregate'] = configLineSplit(line)
        elif "Probe suppression transition aggressiveness...." in line:
            fraDetailDict['fraProbeSuppressionTransitionAgg'] = configLineSplit(line)
        elif "Probe suppression hysteresis..................." in line:
            fraDetailDict['fraProbeSuppressionHysteresis'] = configLineSplit(line)
    fraDict['fra']=fraDetailDict
    return fraDict
#########################################################################
# Build Mobility Config
#
#########################################################################
def buildMobilityConfig(input,sysName):
    mobilityDict = {}
    mobilityDetailDict = {}
    mobilityMemberDict ={}
    mobilityMemberList=[]
    mobilityConfigStartStop = "Mobility Configuration", "Self Signed Certificate details"
    mobilityConfig = collectConfigSection(input, mobilityConfigStartStop)
    mobilityMemberConfigStartStop="Controllers configured in the Mobility Group", "Mobility Hash Configuration"
    mobilityMemberConfig=collectConfigSection(mobilityConfig, mobilityMemberConfigStartStop)
    logger.info("Building Mobility Configuration for %s" % sysName)
    for line in mobilityConfig:
        if "Mobility Protocol Port..........................." in line:
            mobilityDetailDict['mobilityProtocolPort'] = configLineSplit(line)
        elif "Default Mobility Domain.........................." in line:
            mobilityDetailDict['mobilityDefaultDomain'] = configLineSplit(line)
        elif "Multicast Mode .................................." in line:
            mobilityDetailDict['mobilityMulticastMode'] = configLineSplit(line)
        elif "Mobility Domain ID for 802.11r..................." in line:
            mobilityDetailDict['mobilityDomainId8011r'] = configLineSplit(line)
        elif "Mobility Keepalive Interval......................" in line:
            mobilityDetailDict['mobilityKeepaliveInterval'] = configLineSplit(line)
        elif "Mobility Keepalive Count........................." in line:
            mobilityDetailDict['mobilityKeepaliveCount'] = configLineSplit(line)
        elif "Mobility Group Members Configured................" in line:
            mobilityDetailDict['mobilityGroupMembersConfigured'] = configLineSplit(line)
        elif "Mobility Control Message DSCP Value.............." in line:
            mobilityDetailDict['mobilityControlMessageDscpValue'] = configLineSplit(line)
        elif "Controllers configured in the Mobility Group" in line:
            for line in mobilityMemberConfig:
                if "MAC Address" not in line:
                    if "Controllers configured in the Mobility Group" not in line:
                        if len(line.split()) > 3:
                            mobilityMemberDict['macAddress']=line.strip().split()[0]
                            mobilityMemberDict['ipAddress'] = line.strip().split()[1]
                            mobilityMemberDict['groupName'] = line.strip().split()[2]
                            mobilityMemberDict['multicastIp'] = line.strip().split()[3]
                            mobilityMemberList.append(copy.copy(mobilityMemberDict))
                            mobilityMemberDict={}
    mobilityDetailDict['mobilityMembers']=mobilityMemberList
    mobilityDict['mobility']=mobilityDetailDict
    return mobilityDict
#########################################################################
# Build Advanced and SSC Config
#
#
#########################################################################
def buildAdvancedConfig(input, sysName):
    advancedDict={}
    advancedDetailDict={}
    advancedConfigStartStop="Advanced Configuration","Interface Configuration"
    advancedConfig = collectConfigSection(input, advancedConfigStartStop)
    logger.info("Building Advanced Configuration for %s" % sysName)
    for line in advancedConfig:
        if "Probe request filtering.........................." in line:
            advancedDetailDict['probeRequestFiltering'] = configLineSplit(line)
        elif "Probes fwd to controller per client per radio...." in line:
            advancedDetailDict['probeFwdPerClientPerRadio'] = configLineSplit(line)
        elif "Probe request rate-limiting interval............." in line:
            advancedDetailDict['probeRequestRateLimit'] = configLineSplit(line)
        elif "Aggregate Probe request interval................." in line:
            advancedDetailDict['probeRequestAggregateInt'] = configLineSplit(line)
        elif "Increased backoff parameters for probe respon...." in line:
            advancedDetailDict['probeResponseBackoffParameters'] = configLineSplit(line)
        elif "EAP-Identity-Request Timeout (seconds)..........." in line:
            advancedDetailDict['eapIdRequestTimeout'] = configLineSplit(line)
        elif "EAP-Identity-Request Max Retries................." in line:
            advancedDetailDict['eapIdRequestMaxRetries'] = configLineSplit(line)
        elif "EAP Key-Index for Dynamic WEP...................." in line:
            advancedDetailDict['eapKeyIndexDynamicWep'] = configLineSplit(line)
        elif "EAP Max-Login Ignore Identity Response..........." in line:
            advancedDetailDict['eapMaxLoginIgnoreIdResponse'] = configLineSplit(line)
        elif "EAP-Request Timeout (seconds)...................." in line:
            advancedDetailDict['eapRequestTimeout'] = configLineSplit(line)
        elif "EAP-Request Max Retries.........................." in line:
            advancedDetailDict['eapRequestMaxRetries'] = configLineSplit(line)
        elif "EAPOL-Key Timeout (milliseconds)................." in line:
            advancedDetailDict['eapolKeyTimeout'] = configLineSplit(line)
        elif "EAPOL-Key Max Retries............................" in line:
            advancedDetailDict['eapolKeyMaxRetries'] = configLineSplit(line)
        elif "EAP-Broadcast Key Interval......................." in line:
            advancedDetailDict['eapBroadcastKeyInterval'] = configLineSplit(line)
        elif "Fastpath Packet Capture.........................." in line:
            advancedDetailDict['fastpathPacketCapture'] = configLineSplit(line)
        elif "Fastpath Fast Cache Control......................" in line:
            advancedDetailDict['fastpathFastCacheControl'] = configLineSplit(line)
        elif "Fastpath Fast Testmode..........................." in line:
            advancedDetailDict['fastpathFastTestmode'] = configLineSplit(line)
        elif "dot11-padding...................................." in line:
            advancedDetailDict['dot11Padding'] = configLineSplit(line)
        elif "padding-size....................................." in line:
            advancedDetailDict['dot11PaddingSize'] = configLineSplit(line)
        elif "ANQP 4-way state................................." in line:
            advancedDetailDict['anqp4wayState'] = configLineSplit(line)
        elif "GARP Broadcast state: ..........................." in line:
            advancedDetailDict['garpBroadcastState'] = configLineSplit(line)
        elif "GAS request rate limit .........................." in line:
            advancedDetailDict['gasRequestRateLimit'] = configLineSplit(line)
        elif "ANQP comeback delay in TUs(TU=1024usec).........." in line:
            advancedDetailDict['anqpComebackDelay'] = configLineSplit(line)
        elif "RFID Tag data Collection........................." in line:
            advancedDetailDict['rfidTagDataCollection'] = configLineSplit(line)
        elif "RFID  timeout...................................." in line:
            advancedDetailDict['rfidTimeout'] = configLineSplit(line)
        elif "RFID mobility...................................." in line:
            advancedDetailDict['rfidMobility'] = configLineSplit(line)
    advancedDict['advanced']=advancedDetailDict
    return advancedDict


#########################################################################
# Build Radius Config
#
#
#########################################################################
def buildRadiusConfig(input,sysName):
    radiusDict={}
    radiusDetailDict={}
    radiusConfigStartStop="RADIUS Configuration","TACACS Configuration"
    authServerConfigStartStop = "Authentication Servers", "Accounting Servers"
    acctServerConfigStartStop = "Accounting Servers", "TACACS Configuration"
    # Build RadiusConfig from Input
    radiusConfig=collectConfigSection(input,radiusConfigStartStop)
    #Collect Radius Config Section
    logger.info("Building Radius Configuration for %s" % sysName)
    for line in radiusConfig:
        if "Vendor Id Backward Compatibility................." in line:
            radiusDetailDict['vendorIdBack'] = configLineSplit(line)
        elif "Call Station Id Case............................." in line:
            radiusDetailDict['callStationIdCase'] = configLineSplit(line)
        elif "Acct Call Station Id Type........................" in line:
            radiusDetailDict['acctCallStationIdType'] = configLineSplit(line)
        elif "Auth Call Station Id Type........................" in line:
            radiusDetailDict['authCallStationIdType'] = configLineSplit(line)
        elif "Extended Source Ports Support...................." in line:
            radiusDetailDict['extendSourcePorts'] = configLineSplit(line)
        elif "Aggressive Failover.............................." in line:
            radiusDetailDict['aggressiveFail'] = configLineSplit(line)
        elif "Keywrap.........................................." in line:
            radiusDetailDict['keywrap'] = configLineSplit(line)
        elif "Test Mode...................................." in line:
            radiusDetailDict['testMode'] = configLineSplit(line)
        elif "Probe User Name.............................." in line:
            radiusDetailDict['probeUserName'] = configLineSplit(line)
        elif "Interval (in seconds)........................" in line:
            radiusDetailDict['interval'] = configLineSplit(line)
        elif "MAC Delimiter for Authentication Messages........" in line:
            radiusDetailDict['macDelimitAuth'] = configLineSplit(line)
        elif "MAC Delimiter for Accounting Messages............" in line:
            radiusDetailDict['macDelimitAcct'] = configLineSplit(line)
        elif "Authentication Servers" in line:
            radiusDetailDict['authServerList']=buildAaaServer(radiusConfig,authServerConfigStartStop)
        elif "Accounting Servers" in line:
            radiusDetailDict['acctServerList']=buildAaaServer(radiusConfig,acctServerConfigStartStop)
    radiusDict['radiusConfig']=radiusDetailDict
    return radiusDict

#########################################################################
# Build Radius Server List
#
#########################################################################
def buildAaaServer(input, configStartStop):
    aaaServerList=[]
    aaaDict={}
    wlcAaaServer=collectConfigSection(input, configStartStop)
    for line in wlcAaaServer:
        line = line.replace("*","")
        if "Server" not in line:
            if "---" not in line:
                if "....." not in line:
                    if len(line.split()) > 8:
                        aaaDict['radiusId']=line.strip().split()[0]
                        aaaDict['radiusType']=line.strip().split()[1]
                        aaaDict['radiusIp'] = line.strip().split()[2]
                        aaaDict['radiusPort'] = line.strip().split()[3]
                        aaaDict['radiusState'] = line.strip().split()[4]
                        aaaDict['radiusTimeOut'] = line.strip().split()[5]
                        aaaDict['radiusManagementTimeOut']= line.strip().split()[6]
                        aaaDict['radiusRfc3576'] = line.strip().split()[7]
                        aaaDict['radiusIpsec'] = " ".join(line.strip().split()[8:])
                        aaaServerList.append(copy.copy(aaaDict))
    return (aaaServerList)
#########################################################################
# Build TACACs Server List
#
#########################################################################
def buildTacacsConfig(input, sysName):
    tacacsDict={}
    tacacsDetailDict={}
    tacacsAllStartStop="TACACS Configuration", "LDAP Configuration"
    tacacsAuthStartStop="TACACS Configuration", "Authorization Servers"
    tacacsAuthorStartStop="Authorization Servers", "Accounting Servers"
    tacacsAcctStartStop="Accounting Servers", "LDAP Configuration"
    logger.info("Building TACACS Configuration for %s" % sysName)
    tacacsInput=collectConfigSection(input,tacacsAllStartStop)
    tacacsDetailDict['tacacsAuthServerList']=buildTacacsServerList(collectConfigSection(tacacsInput,tacacsAuthStartStop))
    tacacsDetailDict['tacacsAuthorServerList'] = buildTacacsServerList(collectConfigSection(tacacsInput, tacacsAuthorStartStop))
    tacacsDetailDict['tacacsAcctServerList'] = buildTacacsServerList(collectConfigSection(tacacsInput, tacacsAcctStartStop))
    tacacsDict['tacacs']=tacacsDetailDict
    return tacacsDict

#########################################################################
# Collect Configuration Section
#
#########################################################################
def collectConfigSection(input,startStop):
    configSection=[]
    gatherConfig=False
    for line in input:
        if isinstance(startStop,tuple):
            if startStop[0] in line:
                configSection.append(line)
                gatherConfig = True
            elif startStop[1] in line:
                if len(configSection) != 0:
                    break
            elif gatherConfig == True:
                configSection.append(line)
        else:
            if startStop in line:
                configSection.append(line)
                gatherConfig=True
            elif gatherConfig == True:
                configSection.append(line)
    return configSection

#########################################################################
# Build TACACs Server List
#
#########################################################################
def buildTacacsServerList(input):
    tacacsDict={}
    tacacsList=[]
    for line in input:
        if "TACACS" not in line:
            if "Server" not in line:
                if "---" not in line:
                    if len(line.split()) > 5:
                        tacacsDict['tacacsId']=line.strip().split()[0]
                        tacacsDict['tacacsIp'] = line.strip().split()[1]
                        tacacsDict['tacacsPort'] = line.strip().split()[2]
                        tacacsDict['tacacsState'] = line.strip().split()[3]
                        tacacsDict['tacacsTimeOut'] = line.strip().split()[4]
                        tacacsDict['tacacsManagementTimeOut']= line.strip().split()[5]
                        tacacsList.append(copy.copy(tacacsDict))

    return (tacacsList)

#########################################################################
# Build Local Eap Config
#
#
#########################################################################
def buildLocalEap(input,sysName):
    localEapDict={}
    localEapDetailDict={}
    localEapProfileDict={}
    localEapProfileList=[]
    localEapConfigStartStop="Local EAP Configuration","Dns Configuration"
    localEapConfigProfileStartStop="Configured EAP profiles", "EAP Method configuration"
    localEapConfig=collectConfigSection(input,localEapConfigStartStop)
    localEapConfigProfile=collectConfigSection(input,localEapConfigProfileStartStop)
    logger.info("Building Local EAP Configuration for %s" % sysName)
    for line in localEapConfig:
        if "Primary" in line:
            localEapDetailDict['eapDbSearchPrimary'] = " ".join(line.strip().split()[2:])
        elif "Active" in line:
            localEapDetailDict['activeTimeout'] = line.strip().split()[3]
    for line in localEapConfigProfile:
        if "Name ........................................" in line:
            localEapProfileDict['eapProfileName'] = configLineSplit(line)
        elif "Certificate issuer ........................" in line:
            localEapProfileDict['eapCertIssuer'] = configLineSplit(line)
        elif "Check against CA certificates ..........." in line:
            localEapProfileDict['eapCheckCa'] = configLineSplit(line)
        elif "Verify certificate CN identity .........." in line:
            localEapProfileDict['eapCheckCn'] = configLineSplit(line)
        elif "Check certificate date validity ........." in line:
            localEapProfileDict['eapCheckDateValid'] = configLineSplit(line)
        elif "Local certificate required .............." in line:
            localEapProfileDict['eapLocalCertReq'] = configLineSplit(line)
        elif "Client certificate required ............." in line:
            localEapProfileDict['eapClientCertReq'] = configLineSplit(line)
        elif "Enabled methods ..........................." in line:
            localEapProfileDict['eapEnabledMethods'] = configLineSplit(line)
        elif "Configured on WLANs ......................." in line:
            localEapProfileDict['eapConfiguredOnWlan'] = configLineSplit(line)
        elif "eapConfiguredOnWlan" in localEapProfileDict:
            localEapProfileList.append(copy.copy(localEapProfileDict))
            localEapProfileDict = {}

    localEapDetailDict['localEapProfiles']=localEapProfileList
    localEapDict['localEapConfig']=localEapDetailDict
    return localEapDict
#########################################################################
# Build DNS Config
#
#
#########################################################################
def buildDnsConfig(input,sysName):
    dnsConfig=[]
    dnsDict={}
    dnsDetailDict={}
    dnsConfigStartStop="Dns Configuration","Fallback Radio Shut configuration:"
    dnsConfig=collectConfigSection(input,dnsConfigStartStop)
    logger.info("Building DNS Configuration for %s" % sysName)
    for line in dnsConfig:
        if "Radius port......................................" in line:
            dnsDetailDict['dnsRadiusPort'] = configLineSplit(line)
        elif "Radius secret...................................." in line:
            dnsDetailDict['dnsRadiusSecret'] = configLineSplit(line)
        elif "Dns url.........................................." in line:
            if "radiusDnsUrl" in dnsDetailDict:
                dnsDetailDict['tacsDnsUrl'] = configLineSplit(line)
            else:
                dnsDetailDict['radiusDnsUrl'] = configLineSplit(line)
        elif "Dns timeout......................................" in line:
            if "radiusDnsTimeout" in dnsDetailDict:
                dnsDetailDict['tacsDnsTimeout'] = configLineSplit(line)
            else:
                dnsDetailDict['radiusDnsTimeout'] = configLineSplit(line)
        elif "Dns Serverip....................................." in line:
            if "radiusDnsServerIp" in dnsDetailDict:
                dnsDetailDict['tacsDnsServerIp'] = configLineSplit(line)
            else:
                dnsDetailDict['radiusDnsServerIp'] = configLineSplit(line)
        elif "Dns state........................................" in line:
            if "radiusDnsState" in dnsDetailDict:
                dnsDetailDict['tacsDnsState'] = configLineSplit(line)
            else:
                dnsDetailDict['radiusDnsState'] = configLineSplit(line)
        elif "Dns Auth Retransmit Timeout......................" in line:
            dnsDetailDict['dnsAuthRetransTimeout'] = configLineSplit(line)
        elif "Dns Acct Retransmit Timeout......................" in line:
            dnsDetailDict['dnsAcctRetransTimeout'] = configLineSplit(line)
        elif "Dns Auth Mgmt-Retransmit Timeout................." in line:
            dnsDetailDict['dnsManageRetransTimeout'] = configLineSplit(line)
        elif "Dns Network Auth................................." in line:
            dnsDetailDict['dnsNetworkAuth'] = configLineSplit(line)
        elif "Dns Mgmt Auth...................................." in line:
            dnsDetailDict['dnsMgmtAuth'] = configLineSplit(line)
        elif "Dns Network Acct................................." in line:
            dnsDetailDict['dnsNetworkAcct'] = configLineSplit(line)
        elif "Dns RFC 3576 Auth................................" in line:
            dnsDetailDict['dnsRFC3576Auth'] = configLineSplit(line)
    dnsDict['dnsConfiguration']=dnsDetailDict
    return dnsDict

#########################################################################
# Build FlexConnect Group Config
#
#
#########################################################################
def buildFlexGroupConfig(input,sysName):
    flexGroupDict={}
    flexGroupList=[]
    flexGroupDetailDict={}
    flexGroupConfigStartStop="FlexConnect Group Detail","Route  Info"
    flexGroupConfig = collectConfigSection(input,flexGroupConfigStartStop)
    logger.info("Building FlexConnect Group Configuration for %s" % sysName)
    for line in flexGroupConfig:
        if "FlexConnect Group Name - " in line:
            if "flexGroupName" in flexGroupDetailDict:
                flexGroupList.append(copy.copy(flexGroupDetailDict))
                flexGroupDetailDict = {}
            flexGroupDetailDict['flexGroupName'] = " ".join(line.strip().split()[4:])
            flexConfigStart=flexGroupDetailDict['flexGroupName']
            flexGroupDetailDict['keyId']=" ".join(line.strip().split()[4:])
        elif "Number of APs in Group:" in line:
            flexGroupDetailDict['flexGroupApCount'] = " ".join(line.strip().split()[4:])
        elif "Efficient AP Image Upgrade ..... " in line:
            flexGroupDetailDict['flexGroupEfficientUpgrade'] = configLineSplit(line)
        elif "Radius Retransmit Count........................." in line:
            flexGroupDetailDict['flexGroupRadiusRetrans'] = configLineSplit(line)
        elif "Active Radius Timeout..........................." in line:
            flexGroupDetailDict['flexGroupRadiusActiveTimeout'] = configLineSplit(line)
        elif "AP RADIUS server............" in line:
            flexGroupDetailDict['flexGroupApRadius'] = configLineSplit(line)
        elif "EAP-FAST Auth..............." in line:
            flexGroupDetailDict['flexGroupEapFast'] = configLineSplit(line)
        elif "LEAP Auth..................." in line:
            flexGroupDetailDict['flexGroupLeap'] = configLineSplit(line)
        elif "EAP-TLS Auth................" in line:
            flexGroupDetailDict['flexGroupEapTls'] = configLineSplit(line)
        elif "EAP-TLS CERT Download......." in line:
            flexGroupDetailDict['flexGroupEapTlsCertDnld'] = configLineSplit(line)
        elif "PEAP Auth..................." in line:
            flexGroupDetailDict['flexGroupPeap'] = configLineSplit(line)
        elif "Server Key Auto Generated..." in line:
            flexGroupDetailDict['flexGroupServerKeyGen'] = configLineSplit(line)
        elif "Server Key.................." in line:
            flexGroupDetailDict['flexGroupServerKey'] = configLineSplit(line)
        elif "Authority ID................" in line:
            flexGroupDetailDict['flexGroupAuthId'] = configLineSplit(line)
        elif "Authority Info.............." in line:
            flexGroupDetailDict['flexGroupAuthInfo'] = configLineSplit(line)
        elif "PAC Timeout................." in line:
            flexGroupDetailDict['flexGroupPacTimeout'] = configLineSplit(line)
        elif "Multicast on Overridden interface config: " in line:
            flexGroupDetailDict['flexGroupMulticastOverride'] = line.strip().split()[len(line.split())-1]
        elif "DHCP Broadcast Overridden interface config: " in line:
            flexGroupDetailDict['flexGroupDhcpBroadcastOverride'] = line.strip().split()[len(line.split())-1]
        elif "Number of User's in Group:" in line:
            flexGroupDetailDict['flexGroupUserCount'] = line.strip().split()[len(line.split())-1]
        elif "FlexConnect Vlan-name to Id Template name: " in line:
            flexGroupDetailDict['flexGroupVlanIdTemplate'] = line.strip().split()[len(line.split())-1]
        elif "Vlan Mode...................." in line:
            flexGroupDetailDict['flexGroupVlanMode'] = configLineSplit(line)
        elif "Override AP Config..........." in line:
            flexGroupDetailDict['flexGroupOverrideApConfig'] = configLineSplit(line)
        elif "Group-Specific FlexConnect Wlan-Vlan Mapping:" in line:
            wlanVlanMappingConfig=[]
            wlanVlanMappingStartStop=flexConfigStart,"FlexConnect vlan-name-id Summary"
            flexGroupDetailDict['wlanVlanMapping']=buildWlanVlanMapping(flexGroupConfig,wlanVlanMappingStartStop)
    flexGroupList.append(copy.copy(flexGroupDetailDict))
    flexGroupDict['flexGroup']=flexGroupList
    return flexGroupDict
#########################################################################
# Build WLAN Vlan Flex Mapping
#
#######################################################################

def buildWlanVlanMapping(input, configStartStop):
    wlanVlanMapList = []
    wlanVlanMapDict = {}
    apGroupSiteConfig = collectConfigSection(input, configStartStop)
    wlanVlanMapConfigStartStop="Group-Specific FlexConnect Wlan-Vlan Mapping:","WLAN ID   SSID"
    wlanVlanMapConfig=collectConfigSection(apGroupSiteConfig,wlanVlanMapConfigStartStop)
    for line in wlanVlanMapConfig:
        if "WLAN ID" not in line:
            if "---" not in line:
                if len(line.split()) == 2:
                    wlanVlanMapDict['wlanId'] = line.strip().split()[0]
                    wlanVlanMapDict['vlanId'] = line.strip().split()[1]
                    wlanVlanMapList.append(copy.copy(wlanVlanMapDict))
                    wlanVlanMapDict={}
    return (wlanVlanMapList)
#########################################################################
# Build QoS Info
#
#
#########################################################################
def buildQosInfo(input,sysName):
    qosConfigStartStop="Qos Queue Length Info","Mac Filter Info"
    qosConfig=collectConfigSection(input,qosConfigStartStop)
    qosDict={}
    qosDetailDict={}
    logger.info("Building QoS Configuration for %s" % sysName)
    for line in qosConfig:
        if "Platinum queue length............................" in line:
            qosDetailDict['platQueueLength'] = configLineSplit(line)
        elif "Gold queue length................................" in line:
            qosDetailDict['goldQueueLength'] = configLineSplit(line)
        elif "Silver queue length.............................." in line:
            qosDetailDict['silverQueueLength'] = configLineSplit(line)
        elif "Bronze queue length.............................." in line:
            qosDetailDict['bronzeQueueLength'] = configLineSplit(line)
        elif "Description......................................" in line:
            if "platDescription" in qosDetailDict :
                if "goldDescription" in qosDetailDict:
                    if "silverdescription" in qosDetailDict:
                        qosDetailDict['bronzeDescription']= configLineSplit(line)
                    else:
                        qosDetailDict['silverDescription']=configLineSplit(line)
                else:
                    qosDetailDict['goldDescription']= configLineSplit(line)
            else:
                qosDetailDict['platDescription'] = configLineSplit(line)
        elif "Maximum Priority................................." in line:
            if "platMaxPriority" in qosDetailDict :
                if "goldMaxPriority" in qosDetailDict:
                    if "silverMaxPriority" in qosDetailDict:
                        qosDetailDict['bronzeMaxPriority']= configLineSplit(line)
                    else:
                        qosDetailDict['silverMaxPriority']=configLineSplit(line)
                else:
                    qosDetailDict['goldMaxPriority']= configLineSplit(line)
            else:
                qosDetailDict['platMaxPriority'] = configLineSplit(line)
        elif "Unicast Default Priority........................." in line:
            if "platUnicastPriority" in qosDetailDict :
                if "goldUnicastPriority" in qosDetailDict:
                    if "silverUnicastPriority" in qosDetailDict:
                        qosDetailDict['bronzeUnicastPriority']= configLineSplit(line)
                    else:
                        qosDetailDict['silverUnicastPriority']=configLineSplit(line)
                else:
                    qosDetailDict['goldUnicastPriority']= configLineSplit(line)
            else:
                qosDetailDict['platUnicastPriority'] = configLineSplit(line)
        elif "Multicast Default Priority......................." in line:
            if "platMulticastPriority" in qosDetailDict :
                if "goldMulticastPriority" in qosDetailDict:
                    if "silverMulticastPriority" in qosDetailDict:
                        qosDetailDict['bronzeMulticastPriority']= configLineSplit(line)
                    else:
                        qosDetailDict['silverMulticastPriority']=configLineSplit(line)
                else:
                    qosDetailDict['goldMulticastPriority']= configLineSplit(line)
            else:
                qosDetailDict['platMulticastPriority'] = configLineSplit(line)
        elif "Average Data Rate................................" in line:
            if "platPerSsidAvgDataRate" in qosDetailDict:
                if "platPerClientAvgDataRate" in qosDetailDict:
                    if "goldPerSsidAvgDataRate" in qosDetailDict:
                        if "goldPerClientAvgDataRate" in qosDetailDict:
                            if "silverPerSsidAvgDataRate" in qosDetailDict:
                                if "silverPerClientAvgDataRate" in qosDetailDict:
                                    if "bronzePerSsidAvgDataRate" in qosDetailDict:
                                        qosDetailDict['bronzePerClientAvgDataRate']= configLineSplit(line)
                                    else:
                                        qosDetailDict['bronzePerSsidAvgDataRate'] = configLineSplit(line)
                                else:
                                    qosDetailDict['silverPerClientAvgDataRate'] = configLineSplit(line)
                            else:
                                qosDetailDict['silverPerSsidAvgDataRate'] = configLineSplit(line)
                        else:
                            qosDetailDict['goldPerClientAvgDataRate'] = configLineSplit(line)
                    else:
                        qosDetailDict['goldPerSsidAvgDataRate'] = configLineSplit(line)
                else:
                    qosDetailDict['platPerClientAvgDataRate']= configLineSplit(line)
            else:
                qosDetailDict['platPerSsidAvgDataRate'] = configLineSplit(line)
        elif "Average Realtime Data Rate......................." in line:
            if "platPerSsidAvgRealDataRate" in qosDetailDict:
                if "platPerClientAvgRealDataRate" in qosDetailDict:
                    if "goldPerSsidAvgRealDataRate" in qosDetailDict:
                        if "goldPerClientAvgRealDataRate" in qosDetailDict:
                            if "silverPerSsidAvgRealDataRate" in qosDetailDict:
                                if "silverPerClientAvgRealDataRate" in qosDetailDict:
                                    if "bronzePerSsidAvgRealDataRate" in qosDetailDict:
                                        qosDetailDict['bronzePerClientAvgRealDataRate'] = configLineSplit(line)
                                    else:
                                        qosDetailDict['bronzePerSsidAvgRealDataRate'] = configLineSplit(line)
                                else:
                                    qosDetailDict['silverPerClientAvgRealDataRate'] = configLineSplit(line)
                            else:
                                qosDetailDict['silverPerSsidAvgRealDataRate'] = configLineSplit(line)
                        else:
                            qosDetailDict['goldPerClientAvgRealDataRate'] = configLineSplit(line)
                    else:
                        qosDetailDict['goldPerSsidAvgRealDataRate'] = configLineSplit(line)
                else:
                    qosDetailDict['platPerClientAvgRealDataRate'] = configLineSplit(line)
            else:
                qosDetailDict['platPerSsidAvgRealDataRate'] = configLineSplit(line)
        elif "Burst Data Rate.................................." in line:
            if "platPerSsidBurstDataRate" in qosDetailDict:
                if "platPerClientBurstDataRate" in qosDetailDict:
                    if "goldPerSsidBurstDataRate" in qosDetailDict:
                        if "goldPerClientBurstDataRate" in qosDetailDict:
                            if "silverPerSsidBurstDataRate" in qosDetailDict:
                                if "silverPerClientBurstDataRate" in qosDetailDict:
                                    if "bronzePerSsidBurstDataRate" in qosDetailDict:
                                        qosDetailDict['bronzePerClientBurstDataRate'] = configLineSplit(line)
                                    else:
                                        qosDetailDict['bronzePerSsidBurstDataRate'] = configLineSplit(line)
                                else:
                                    qosDetailDict['silverPerClientBurstDataRate'] = configLineSplit(line)
                            else:
                                qosDetailDict['silverPerSsidBurstDataRate'] = configLineSplit(line)
                        else:
                            qosDetailDict['goldPerClientBurstDataRate'] = configLineSplit(line)
                    else:
                        qosDetailDict['goldPerSsidBurstDataRate'] = configLineSplit(line)
                else:
                    qosDetailDict['platPerClientBurstDataRate'] = configLineSplit(line)
            else:
                qosDetailDict['platPerSsidBurstDataRate'] = configLineSplit(line)
        elif "Burst Realtime Data Rate........................." in line:
            if "platPerSsidBurstRealDataRate" in qosDetailDict:
                if "platPerClientBurstRealDataRate" in qosDetailDict:
                    if "goldPerSsidBurstRealDataRate" in qosDetailDict:
                        if "goldPerClientBurstRealDataRate" in qosDetailDict:
                            if "silverPerSsidBurstRealDataRate" in qosDetailDict:
                                if "silverPerClientBurstRealDataRate" in qosDetailDict:
                                    if "bronzePerSsidBurstRealDataRate" in qosDetailDict:
                                        qosDetailDict['bronzePerClientBurstRealRealDataRate'] = configLineSplit(line)
                                    else:
                                        qosDetailDict['bronzePerSsidBurstRealDataRate'] = configLineSplit(line)
                                else:
                                    qosDetailDict['silverPerClientBurstRealDataRate'] = configLineSplit(line)
                            else:
                                qosDetailDict['silverPerSsidBurstRealDataRate'] = configLineSplit(line)
                        else:
                            qosDetailDict['goldPerClientBurstRealDataRate'] = configLineSplit(line)
                    else:
                        qosDetailDict['goldPerSsidBurstRealDataRate'] = configLineSplit(line)
                else:
                    qosDetailDict['platPerClientBurstRealDataRate'] = configLineSplit(line)
            else:
                qosDetailDict['platPerSsidBurstRealDataRate'] = configLineSplit(line)
        elif "protocol........................................." in line:
            if "platProtocol" in qosDetailDict:
                if "goldProtocol" in qosDetailDict:
                    if "silverProtocol" in qosDetailDict:
                        qosDetailDict['bronzeProtocol']= configLineSplit(line)
                    else:
                        qosDetailDict['silverProtocol']=configLineSplit(line)
                else:
                    qosDetailDict['goldProtocol']= configLineSplit(line)
            else:
                qosDetailDict['platProtocol'] = configLineSplit(line)
    qosDict['qos']=qosDetailDict
    return qosDict
#########################################################################
# Build Mac Filter Info
#
#########################################################################
def buildMacFilterInfo(input, sysName):
    macFilterList=[]
    macFilterDetailDict={}
    macFilterDict={}
    macFilterConfigStartStop="Mac Filter Info","Authorization List"
    macFilterConfig=collectConfigSection(input,macFilterConfigStartStop)
    logger.info("Building Mac Filter Information for %s" % sysName)
    for line in macFilterConfig:
        if "Mac Filter Info" not in line:
            if "MAC Address               WLAN Id          Description" not in line:
                if "---" not in line:
                    if len(line.split()) > 1:
                        macFilterDetailDict['macFilterMac']=line.strip().split()[0]
                        macFilterDetailDict['macFilterWlanId'] = line.strip().split()[1]
                        #Description is not a required field so we need to check first if its there
                        if len(line.split()) > 2:
                            macFilterDetailDict['macFilterDescription'] = line.strip().split()[2]
                        macFilterDetailDict['keyId']=macFilterDetailDict['macFilterMac']
                        macFilterList.append(copy.copy(macFilterDetailDict))
                        macFilterDetailDict={}
    macFilterDict['macFilters']=macFilterList
    return macFilterDict
#########################################################################
# Build Authorization List
#
#########################################################################
def buildAuthList(input,sysName):
    authList=[]
    authListDict={}
    authListDetailDict={}
    authListTableDict={}
    authListStartStop="Authorization List","Mac Addr                  Cert Type    Key Hash"
    authListConfig=collectConfigSection(input,authListStartStop)
    authTableConfigStartStop="Mac Addr                  Cert Type    Key Hash","Load Balancing Info"
    authTableConfig=collectConfigSection(input, authTableConfigStartStop)
    #Collect System Information Section
    logger.info("Building Authorization List for %s" % sysName)
    for line in authListConfig:
        if "Authorize MIC APs against Auth-list or AAA ......"in line:
            authListDetailDict['authMicAps']=line.strip().split()[8]
        elif "Authorize LSC APs against Auth-List ............." in line:
            authListDetailDict['authLscAps']=line.strip().split()[6]
        elif "AP with Manufacturing Installed Certificate...." in line:
            authListDetailDict['apMicAllowed']=line.strip().split()[5]
        elif "AP with Self-Signed Certificate................" in line:
            authListDetailDict['apSscAllowed']=line.strip().split()[4]
        elif "AP with Locally Significant Certificate........" in line:
            authListDetailDict['apLscAllowed']=line.strip().split()[5]
    for line in authTableConfig:
        if "Mac Addr" not in line:
            if "---" not in line:
                if len(line.split()) > 1:
                    authListTableDict['authListMacAddress']=line.strip().split()[0]
                    authListTableDict['authListCertType'] = line.strip().split()[1]
                    #Key Hash is not required field
                    if len(line.split()) > 2:
                        authListTableDict['authListKeyHash'] = line.strip().split()[2]
                    authListTableDict['keyId']=authListTableDict['authListMacAddress']
                    authList.append(copy.copy(authListTableDict))
                    authListTableDict={}

    authListDetailDict['authListEntries']=authList
    authListDict['authListConfig']=authListDetailDict
    return authListDict
#########################################################################
# Build Load Balancing Info
#
#########################################################################
def buildLoadBalanceInfo(input,sysName):
    loadBalanceDict={}
    loadBalanceDetailDict={}
    loadBalanceConfigStartStop="Load Balancing Info","DHCP Info"
    loadBalanceConfig = collectConfigSection(input,loadBalanceConfigStartStop)
    logger.info("Building Load Balance Information for %s" % sysName)
    #Collect System Information Section
    for line in loadBalanceConfig:
        if "Aggressive Load Balancing........................"in line:
            loadBalanceDetailDict['aggressiveLoadBalanceType']=configLineSplit(line)
        elif "Aggressive Load Balancing Window................." in line:
            loadBalanceDetailDict['aggressiveLoadBalanceWindow']=configLineSplit(line)
        elif "Aggressive Load Balancing Denial Count..........." in line:
            loadBalanceDetailDict['aggressiveLoadBalanceDenial']=configLineSplit(line)
        elif "Aggressive Load Balancing Uplink Threshold......" in line:
            loadBalanceDetailDict['aggressiveLoadBalanceUplink']=configLineSplit(line)
    loadBalanceDict['loadBalance']=loadBalanceDetailDict
    return loadBalanceDict
#########################################################################
# Build WPS Config Summary
#
#########################################################################
def buildWpsConfig(input,sysName):
    wpsDict={}
    wpsDetailDict={}
    wpsConfigStartStop="WPS Configuration Summary","Custom Web Configuration"
    wpsConfig = collectConfigSection(input,wpsConfigStartStop)
    logger.info("Building WPS Configuration for %s" % sysName)
    for line in wpsConfig:
        if "Auto-Immune...................................." in line:
            wpsDetailDict['autoImmune'] = configLineSplit(line)
        elif "Auto-Immune by aWIPS Prevention................" in line:
            wpsDetailDict['autoImmuneAwips'] = configLineSplit(line)
        elif "Excessive 802.11-association failures.........." in line:
            wpsDetailDict['excessiveAssociation'] = configLineSplit(line)
        elif "Excessive 802.11-authentication failures......." in line:
            wpsDetailDict['excessiveAuth'] = configLineSplit(line)
        elif "Excessive 802.1x-authentication................" in line:
            wpsDetailDict['excessive8021x'] = configLineSplit(line)
        elif "IP-theft......................................." in line:
            wpsDetailDict['ipTheft'] = configLineSplit(line)
        elif "Excessive Web authentication failure..........." in line:
            wpsDetailDict['excessiveWebAuth'] = configLineSplit(line)
        elif "Maximum 802.1x-AAA failure attempts............" in line:
            wpsDetailDict['max8021x'] = configLineSplit(line)
        elif "Signature Processing..........................." in line:
            wpsDetailDict['signatureProcess'] = configLineSplit(line)
        elif "Global Infrastructure MFP state................" in line:
            wpsDetailDict['globalMfpState'] = configLineSplit(line)
        elif "AP Impersonation detection....................." in line:
            wpsDetailDict['apImpersonation'] = configLineSplit(line)
        elif "Controller Time Source Valid..................." in line:
            wpsDetailDict['controllerSourceTimeValid'] = configLineSplit(line)
    wpsDict['wps']=wpsDetailDict
    return wpsDict
#########################################################################
# Build WLAN MFP Status
#
#########################################################################
def buildWlanMfp(input,sysName):
    mfpList=[]
    mfpDict={}
    mfpDetailDict={}
    mfpConfigStartStop="WLAN ID  WLAN Name                  Status     Protection","Custom Web Configuration"
    mfpConfig=collectConfigSection(input,mfpConfigStartStop)
    logger.info("Building MFP Configuration for %s" % sysName)
    for line in mfpConfig:
        if "Protection" not in line:
            if "---" not in line:
                if len(line.split()) == 4:
                    mfpDetailDict['wlanId']=line.strip().split()[0]
                    mfpDetailDict['wlanName']=line.strip().split()[1]
                    mfpDetailDict['wlanStatus'] = line.strip().split()[2]
                    mfpDetailDict['clientProtection'] = " ".join(line.strip().split()[3:])
                    mfpDetailDict['keyId']=mfpDetailDict['wlanId']
                    mfpList.append(copy.copy(mfpDetailDict))
                    mfpDetailDict={}
                elif len(line.split()) == 5:
                    mfpDetailDict['wlanId']=line.strip().split()[0]
                    mfpDetailDict['wlanName']=line.strip().split()[1:2]
                    mfpDetailDict['wlanStatus'] = configLineSplit(line)
                    mfpDetailDict['clientProtection'] = " ".join(line.strip().split()[4:])
                    mfpDetailDict['keyId'] = mfpDetailDict['wlanId']
                    mfpList.append(copy.copy(mfpDetailDict))
                    mfpDetailDict={}
    mfpDict['mfpList']=mfpList
    return mfpDict
#########################################################################
# Build Custom Web
#
#########################################################################
def buildCustomWeb(input,sysName):
    webDict={}
    webDetailDict={}
    webConfigStartStop="Custom Web Configuration","Configuration Per Profile:"
    webConfig = collectConfigSection(input,webConfigStartStop)
    logger.info("Building Custom Web Configuration for %s" % sysName)
    for line in webConfig:
        if "Radius Authentication Method....................." in line:
            webDetailDict['webRadiusAuthMethod'] = configLineSplit(line)
        elif "Cisco Logo......................................." in line:
            webDetailDict['webCiscoLogo'] = configLineSplit(line)
        elif "CustomLogo......................................." in line:
            webDetailDict['webCustomLogo'] = configLineSplit(line)
        elif "Custom Title....................................." in line:
            webDetailDict['webCustomTitle'] = configLineSplit(line)
        elif "Custom Message..................................." in line:
            webDetailDict['webCustomMessage'] = configLineSplit(line)
        elif "Custom Redirect URL.............................." in line:
            webDetailDict['webCustomRedirectUrl'] = configLineSplit(line)
        elif "Web Authentication Type.........................." in line:
            webDetailDict['webAuthType'] = configLineSplit(line)
        elif "Logout-popup....................................." in line:
            webDetailDict['webLogoutPop'] = configLineSplit(line)
        webDict['customWeb']=webDetailDict
    return webDict
#########################################################################
# Build Rogue Configuration
#
#########################################################################
def buildRogueConfig(input,sysName):
    rogueConfigStartStop="Rogue AP Configuration","Rogue Rule Configuration"
    rogueRuleConfigStartStop="Rogue Rule Configuration","Media-Stream Configuration"
    rogueConfig=collectConfigSection(input,rogueConfigStartStop)
    rogueRuleConfig=collectConfigSection(input,rogueRuleConfigStartStop)
    rogueDict={}
    rogueDetailDict={}
    rogueRuleDict={}
    rogueRuleList=[]
    logger.info("Building Rogue Configuration for %s" % sysName)
    for line in rogueConfig:
        if "Rogue Detection Security Level..................." in line:
            rogueDetailDict['rogueSecLevel'] = configLineSplit(line)
        elif "Rogue Pending Time..............................." in line:
            rogueDetailDict['roguePendingTime'] = configLineSplit(line)
        elif "Rogue on wire Auto-Contain......................." in line:
            rogueDetailDict['rogueWireAuto'] = configLineSplit(line)
        elif "Rogue using our SSID Auto-Contain................" in line:
            rogueDetailDict['rogueOurSsidAutoContain'] = configLineSplit(line)
        elif "Valid client on rogue AP Auto-Contain............" in line:
            rogueDetailDict['validClientonRogueAuto'] = configLineSplit(line)
        elif "Rogue AP timeout................................." in line:
            rogueDetailDict['rogueApTimeout'] = configLineSplit(line)
        elif "Rogue Detection Report Interval.................." in line:
            rogueDetailDict['rogueDetectReportInt'] = configLineSplit(line)
        elif "Rogue Detection Min Rssi........................." in line:
            rogueDetailDict['rogueDetectMinRssi'] = configLineSplit(line)
        elif "Rogue Detection Transient Interval..............." in line:
            rogueDetailDict['rogueDetectTransient'] = configLineSplit(line)
        elif "Rogue Detection Client Num Thershold............." in line:
            rogueDetailDict['rogueDetectClientNum'] = configLineSplit(line)
        elif "Rogue Location Discovery Protocol................" in line:
            rogueDetailDict['rldp'] = configLineSplit(line)
        elif "RLDP Schedule Config............................." in line:
            rogueDetailDict['rldpScheduleConfig'] = configLineSplit(line)
        elif "RLDP Scheduling Operation........................" in line:
            rogueDetailDict['rldpScheduleOp'] = configLineSplit(line)
        elif "RLDP Retry......................................." in line:
            rogueDetailDict['rldpRetry'] = configLineSplit(line)
        elif "Containment Level................................" in line:
            rogueDetailDict['rogueContainLevel'] = configLineSplit(line)
        elif "monitor_ap_only.................................." in line:
            rogueDetailDict['monitorAPonly'] = configLineSplit(line)
        elif "Detect and report Ad-Hoc Networks................" in line:
            rogueDetailDict['detectAdhoc'] = configLineSplit(line)
        elif "Auto-Contain Ad-Hoc Networks....................." in line:
            rogueDetailDict['autocontainAdhoc'] = configLineSplit(line)
        elif "Validate rogue clients against AAA..............." in line:
            rogueDetailDict['validateRogueClientsAaa'] = configLineSplit(line)
        elif "Validate rogue clients against MSE..............." in line:
            rogueDetailDict['validateRogueClientsMse'] = configLineSplit(line)
    for line in rogueRuleConfig:
        if "Rogue Rule Configuration" not in line:
            if "Class Type" not in line:
                if "---" not in line:
                    if len(line.split()) >7:
                        rogueRuleDict['rogueRulePriority']=line.strip().split()[0]
                        rogueRuleDict['rogueRuleName'] = line.strip().split()[1]
                        rogueRuleDict['rogueRuleState'] = line.strip().split()[2]
                        rogueRuleDict['rogueRuleClassType'] = line.strip().split()[3]
                        rogueRuleDict['rogueRuleNotify'] = line.strip().split()[4]
                        rogueRuleDict['rogueRuleState'] = line.strip().split()[5]
                        rogueRuleDict['rogueRuleMatch'] = line.strip().split()[6]
                        rogueRuleDict['rogueRuleHitCount'] = line.strip().split()[7]
                        rogueRuleDict['keyId'] = rogueRuleDict['rogueRuleName']
                        rogueRuleList.append(copy.copy(rogueRuleDict))
                        rogueRuleDict={}
    rogueDetailDict['rogueRules']=rogueRuleList
    rogueDict['rogueConfig']=rogueDetailDict
    return rogueDict

#########################################################################
# Build Media Stream Configuration
#
#########################################################################
def buildMediaStreamConfig(input,sysName):
    mediaConfigStartStop="Media-Stream Configuration","WLC Voice Call Statistics"
    mediaConfig=collectConfigSection(input,mediaConfigStartStop)
    mediaDict={}
    mediaDetailDict={}
    streamList = []
    streamDict = {}
    logger.info("Building Media Stream Configuration for %s" % sysName)
    for line in mediaConfig:
        if "Multicast-direct State..........................." in line:
            mediaDetailDict['multicastState'] = configLineSplit(line)
        elif "Allowed WLANs...................................." in line:
            mediaDetailDict['mediastreamAllowedWlans'] = configLineSplit(line)
        elif "URL.............................................." in line:
            mediaDetailDict['mediastreamUrl'] = configLineSplit(line)
        elif "E-mail..........................................." in line:
            mediaDetailDict['mediastreamEmail'] = configLineSplit(line)
        elif "Phone............................................" in line:
            mediaDetailDict['mediastreamPhone'] = configLineSplit(line)
        elif "Note............................................." in line:
            mediaDetailDict['mediastreamNote'] = configLineSplit(line)
        elif "State............................................" in line:
            mediaDetailDict['mediastreamState'] = configLineSplit(line)
        elif "Multicast-direct................................." in line:
            if 'mediastream24State' in mediaDetailDict:
                mediaDetailDict['mediastream5State'] = configLineSplit(line)
            else:
                mediaDetailDict['mediastream24State'] = configLineSplit(line)
        elif "Best Effort......................................" in line:
            if 'mediastream24BestEffortState' in mediaDetailDict:
                mediaDetailDict['mediastream5BestEffortState'] = configLineSplit(line)
            else:
                mediaDetailDict['mediastream24BestEffortState'] = configLineSplit(line)
        elif "Video Re-Direct.................................." in line:
            if 'videoRedirect24' in mediaDetailDict:
                mediaDetailDict['videoRedirect5'] = configLineSplit(line)
            else:
                mediaDetailDict['videoRedirect24'] = configLineSplit(line)
        elif "Max Allowed Streams Per Radio...................." in line:
            if 'maxStreams24PerRadio' in mediaDetailDict:
                mediaDetailDict['maxStreams5PerRadio'] = configLineSplit(line)
            else:
                mediaDetailDict['maxStreams24PerRadio'] = configLineSplit(line)
        elif "Max Allowed Streams Per Client..................." in line:
            if 'maxStreams24PerClient' in mediaDetailDict:
                mediaDetailDict['maxStreams5PerClient'] = configLineSplit(line)
            else:
                mediaDetailDict['maxStreams24PerClient'] = configLineSplit(line)
        elif "Max Video Bandwidth.............................." in line:
            if 'max24VideoBandwidth' in mediaDetailDict:
                mediaDetailDict['max5VideoBandwidth'] = configLineSplit(line)
            else:
                mediaDetailDict['max24VideoBandwidth'] = configLineSplit(line)
        elif "Max Voice Bandwidth.............................." in line:
            if 'max24VoiceBandwidth' in mediaDetailDict:
                mediaDetailDict['max5VoiceBandwidth'] = configLineSplit(line)
            else:
                mediaDetailDict['max24VoiceBandwidth'] = configLineSplit(line)
        elif "Max Media Bandwidth.............................." in line:
            if 'max24MediaBandwidth' in mediaDetailDict:
                mediaDetailDict['max5MediaBandwidth'] = configLineSplit(line)
            else:
                mediaDetailDict['max24MediaBandwidth'] = configLineSplit(line)
        elif "Min PHY Rate....................................." in line:
            if 'min24PhyRate' in mediaDetailDict:
                mediaDetailDict['min5PhyRate'] = configLineSplit(line)
            else:
                mediaDetailDict['min24PhyRate'] = configLineSplit(line)
        elif "Max Retry Percentage............................." in line:
            if 'max24RetryPercentage' in mediaDetailDict:
                mediaDetailDict['max5RetryPercentage'] = configLineSplit(line)
            else:
                mediaDetailDict['max24RetryPercentage'] = configLineSplit(line)
        elif "Stream Name" in line:
            streamConfigStartStop="Stream Name","URL..."
            streamConfig=collectConfigSection(mediaConfig,streamConfigStartStop)
            # Collect System Information Section
            for line in streamConfig:
                if "Stream Name" not in line:
                    if "---" not in line:
                        if len(line.split()) > 3:
                            streamDict['mediaStreamName'] = line.strip().split()[0]
                            streamDict['mediaStreamStartIp'] = line.strip().split()[1]
                            streamDict['mediaStreamEndIp'] = line.strip().split()[2]
                            streamDict['mediaStreamOperationStatus'] = line.strip().split()[3]
                            streamDict['keyId'] = streamDict['mediaStreamName']
                            streamList.append(copy.copy(streamDict))
            mediaDetailDict['streams']=streamList
    mediaDict['mediaStream']=mediaDetailDict
    return mediaDict

#########################################################################
# Build Ipv6 Config
#
#########################################################################
def buildIpv6Config(input,sysName):
    ipv6Dict={}
    ipv6DetailDict={}
    ipv6ConfigStartStop="WLC IPv6 Summary","mDNS Service Summary"
    ipv6Config = collectConfigSection(input,ipv6ConfigStartStop)
    logger.info("Building IPv6 Summary for %s" % sysName)
    for line in ipv6Config:
        if "Global Config..............................." in line:
            ipv6DetailDict['ipv6GlobalConfig'] = configLineSplit(line)
        elif "Reachable-lifetime value...................." in line:
            ipv6DetailDict['ipv6LifetimeValue'] = configLineSplit(line)
        elif "Stale-lifetime value........................" in line:
            ipv6DetailDict['ipv6StaleLifeValue'] = configLineSplit(line)
        elif "Down-lifetime value........................." in line:
            ipv6DetailDict['ipv6DownLifeValue'] = configLineSplit(line)
        elif "RA Throttling..............................." in line:
            ipv6DetailDict['ipv6RaThrottle'] = configLineSplit(line)
        elif "RA Throttling allow at-least................" in line:
            ipv6DetailDict['ipv6RaThrottleAllowLeast'] = configLineSplit(line)
        elif "RA Throttling allow at-most................." in line:
            ipv6DetailDict['ipv6RaThrottleAllowMost'] = configLineSplit(line)
        elif "RA Throttling max-through..................." in line:
            ipv6DetailDict['ipv6ThrottleMaxThrough'] = configLineSplit(line)
        elif "RA Throttling throttle-period..............." in line:
            ipv6DetailDict['ipv6ThrottlePeriod'] = configLineSplit(line)
        elif "RA Throttling interval-option..............." in line:
            ipv6DetailDict['ipv6ThrottleInterval'] = configLineSplit(line)
        elif "NS Mulitcast CacheMiss Forwarding..........." in line:
            ipv6DetailDict['ipv6NsMulticastCacheMiss'] = configLineSplit(line)
        elif "NA Mulitcast Forwarding....................." in line:
            ipv6DetailDict['ipv6NsMulticastForward'] = configLineSplit(line)
        elif "IPv6 Capwap UDP Lite........................" in line:
            ipv6DetailDict['ipv6CapUdpLite'] = configLineSplit(line)
        elif "Operating System IPv6 state ................" in line:
            ipv6DetailDict['ipv6OperatingSystem'] = configLineSplit(line)
    ipv6Dict['ipv6Config']=ipv6DetailDict
    return ipv6Dict
#########################################################################
# Build mDNS Config
#
#########################################################################
def buildMdnsConfig(input,sysName):
    mdnsConfigStartStop="mDNS Service Summary","PMIPv6 Global Configuration"
    mdnsServicesConfigStartStop="Service-Name","mDNS service-group Summary"
    mdnsApConfigStartStop="mDNS AP Summary", "PMIPv6 Global Configuration"
    wlcApMdns=collectConfigSection(input, mdnsApConfigStartStop)
    mdnsConfig=collectConfigSection(input,mdnsConfigStartStop)
    mdnsServicesConfig=collectConfigSection(input,mdnsServicesConfigStartStop)
    mdnsDict={}
    mdnsDetailDict={}
    mdnsServicesDict={}
    mdnsServicesList=[]
    mdnsApDict={}
    mdnsApList=[]
    logger.info("Building mDNS Configuration for %s" % sysName)
    for line in mdnsConfig:
        if "Number of Services.............................." in line:
            mdnsDetailDict['mdnsServiceTotal'] = configLineSplit(line)
        elif "Mobility learning status ........................" in line:
            mdnsDetailDict['mdnsMobilityLearning'] = configLineSplit(line)
        elif "Access Policy Status............................" in line:
            mdnsDetailDict['mdnsAccessPolicyStatus'] = configLineSplit(line)
        elif "Total number of mDNS Policies...................." in line:
            mdnsDetailDict['mdnsTotalPolicy'] = configLineSplit(line)
        elif "Number of Admin configured Policies.............." in line:
            mdnsDetailDict['mdnsAdminPolicies'] = configLineSplit(line)
    for line in mdnsServicesConfig:
        if "Service-Name" not in line:
            if "---" not in line:
                if "*" not in line:
                    if len(line.split()) > 4:
                        mdnsServicesDict['mdnsServiceName'] = line.strip().split()[0]
                        mdnsServicesDict['mdnsLss'] = line.strip().split()[1]
                        mdnsServicesDict['mdnsOrigin'] = line.strip().split()[2]
                        mdnsServicesDict['mdnsNoSp'] = line.strip().split()[3]
                        mdnsServicesDict['mdnsServiceString'] = line.strip().split()[4]
                        mdnsServicesDict['keyId'] = mdnsServicesDict['mdnsServiceName']
                        mdnsServicesList.append(copy.copy(mdnsServicesDict))
                        mdnsServicesDict={}
    mdnsDetailDict['mdnsServices']=mdnsServicesList
    for line in wlcApMdns:
        if "Number of mDNS APs............................." in line:
            mdnsDetailDict['mdnsApCount']=configLineSplit(line)
        elif "AP Name" not in line:
            if "---" not in line:
                if len(line.split()) >3:
                    mdnsApDict['mdnsApName']=line.strip().split()[0]
                    mdnsApDict['mdnsApMac'] = line.strip().split()[1]
                    mdnsApDict['mdnsApVlanCount'] = line.strip().split()[2]
                    mdnsApDict['mdnsAPVlanIdentifiers'] = " ".join(line.strip().split()[3:])
                    mdnsApDict['keyId'] = mdnsApDict['mdnsApName']
                    mdnsApList.append(copy.copy(mdnsApDict))
                    mdnsApDict={}
        mdnsDetailDict['mdnsAps']=mdnsApList
    mdnsDict['mdnsConfig']=mdnsDetailDict
    return mdnsDict
#########################################################################
# Build Certificate Config
#
#########################################################################
def buildCert(input,sysName):
    certConfigStartStop="WLAN Express Setup Information."
    certConfig = collectConfigSection(input,certConfigStartStop)
    certDict={}
    certDetailDict={}
    logger.info("Building Certificate Information for %s" % sysName)
    for line in certConfig:
        if "WLAN Express Setup - ............................" in line:
            certDetailDict['wlanExpressEnabled'] = configLineSplit(line)
        elif "Web Administration Certificate..................." in line:
            certDetailDict['webAdminCertType'] = configLineSplit(line)
        elif "Web Authentication Certificate..................." in line:
            certDetailDict['webAuthCertType'] = configLineSplit(line)
        elif "Certificate compatibility mode:.................." in line:
            certDetailDict['certCompatibilityMode'] = configLineSplit(line)
        elif "Lifetime Check Ignore for MIC ..................." in line:
            certDetailDict['lifetimeCheckIgnoreMic'] = configLineSplit(line)
        elif "Lifetime Check Ignore for SSC ..................." in line:
            certDetailDict['lifetimeCheckIgnoreSsc'] = configLineSplit(line)
    certDict['certConfig']=certDetailDict
    return certDict
#########################################################################
#  Line Split Function used for configs with ....
#
#
#########################################################################
def configLineSplit(input):
    list1 = re.split(r'\.\.+', input)
    value = (list1[len(list1) - 1]).strip()
    return value

#########################################################################
#  Config parse
#
#
#########################################################################
def configParse(input,isGolden):
    config={}
    endConfig={}
    zipTempDir="Configs/temp/"
    checkList = [buildWlanList,
                 buildRedundancyInfo,
                 buildApBundleInfo,
                 buildNtpServer,
                 buildSwitchConfig,
                 buildNetworkInfo,
                 buildPortSummary,
                 buildInterfaces,
                 buildInterfaceGroup,
                 buildApGroupConfig,
                 buildRfProfiles,
                 build80211aConfig,
                 build80211aAirewaveConfig,
                 build80211aCleanairConfig,
                 build80211bConfig,
                 build80211bAirewaveConfig,
                 build80211bCleanairConfig,
                 buildFraConfig,
                 buildMobilityConfig,
                 buildAdvancedConfig,
                 buildRadiusConfig,
                 buildTacacsConfig,
                 buildLocalEap,
                 buildDnsConfig,
                 buildFlexGroupConfig,
                 buildQosInfo,
                 buildMacFilterInfo,
                 buildAuthList,
                 buildLoadBalanceInfo,
                 buildWpsConfig,
                 buildWlanMfp,
                 buildCustomWeb,
                 buildRogueConfig,
                 buildMediaStreamConfig,
                 buildIpv6Config,
                 buildMdnsConfig,
                 buildCert]
    #Pass Golden or Test as Name depending on value passed to function
    if isGolden==True:
        # Open File to be tested
        myFileTest = open(input, 'r')
        # Read file into a list
        myConfig = [i for i in myFileTest]
        # Close file
        myFileTest.close()
        sysInfo = buildSysInfo(myConfig)
        config.update(sysInfo)
        sysName = "golden"
        for item in checkList:
            config.update(item(myConfig, sysName))
        endConfig[sysName] = config
        logger.info("Building Configurations for %s has been completed!" % sysName)
    else:
        if zipfile.is_zipfile(input):

            zipConfig=zipfile.ZipFile(input,'r')
            configList = zipConfig.namelist()
            zipConfig.extractall(zipTempDir)
            zipConfig.close()
            for myConfig in configList:
                if "MACOSX" not in myConfig:
                    # Open File to be tested
                    myFileTest = open(zipTempDir + myConfig, 'r')
                    # Read file into a list
                    runConfig = [i for i in myFileTest]
                    # Close file
                    myFileTest.close()
                    sysInfo = buildSysInfo(runConfig)
                    config.update(sysInfo)
                    sysName = sysInfo['sysInfo']['sysName']
                    logger.info("Building Configs for %s", sysName)
                    for item in checkList:
                        config.update(item(runConfig, sysName))
                    endConfig[sysName] = config
                    config={}
                    logger.info("Building Configs for %s Completed", sysName)


        else:
            # Open File to be tested
            myFileTest = open(input, 'r')
            # Read file into a list
            myConfig = [i for i in myFileTest]
            # Close file
            myFileTest.close()
            sysInfo = buildSysInfo(myConfig)
            config.update(sysInfo)
            sysName = sysInfo['sysInfo']['sysName']
            for item in checkList:
                config.update(item(myConfig, sysName))
            endConfig[sysName] = config

        logger.info("Building Configurations for %s has been completed!" % sysName)

    return endConfig

#########################################################################
#  Run Config removing AP configuration
#
#
#########################################################################
def collectConfigNoAps(input):
    #split config into 2 sections
    configSection1StartStop="System Inventory","AP Config"
    configSection1=collectConfigSection(input,configSection1StartStop)
    configSection2StartStop="802.11a Configuration"
    configSection2=(input,configSection2StartStop)
    configFull=configSection1 + configSection2
    return configFull

#########################################################################
# Compare Config Section
#
#
#########################################################################
def configSectionCompare(inputGolden,inputTest,keyBase,uniqueId,cfg):
    goldenCompleteList = []
    testCompleteList = []
    inputChecks=cfg['functions'][keyBase]
    checkResults={}
    checkResultsDetail={}
    checkResultsSingle = {}
    checkResultsSingleList=[]
    checkResultsNotInTest=[]
    checkResultsNotInGolden=[]
    failResults={}
    failResultsList=[]
    failResultsSingle={}
    failResultsDetail={}
    if len(inputGolden) < 2:
        checkResults[keyBase] = "Not Configured"
        logger.warning("Golden contains no configuration for %s"%keyBase)
    else:
        if isinstance(inputGolden, list):
            for item in inputGolden:
                if len(item) > 0:
                    goldenCompleteList.append(item[uniqueId])
            for item in inputTest:
                if len(item) > 0:
                    testCompleteList.append(item[uniqueId])
            intersectCompleteList = list(set(goldenCompleteList) & set(testCompleteList))
            for item in testCompleteList:
                if item not in goldenCompleteList:
                    logger.warning(keyBase + " " + item + " in Test but not in Golden Config")
                    checkResultsNotInGolden.append(item)
            checkResultsDetail['NotInGolden'] = checkResultsNotInGolden
            for item in goldenCompleteList:
                if item not in testCompleteList:
                    logger.warning(keyBase + " " + item + " in Golden but not in Test Config")
                    checkResultsNotInTest.append(item)
            checkResultsDetail['NotInTest'] = checkResultsNotInTest
            for item in sorted(intersectCompleteList):
                goldenList = filter(lambda x: x[uniqueId] == item, inputGolden)
                testList = filter(lambda x: x[uniqueId] == item, inputTest)
                for item in goldenList:
                    logger.debug("------------------")
                    logger.debug(keyBase + " " + item[uniqueId])
                    logger.debug("------------------")
                    for key in item.keys():
                        if key == 'keyId':
                            checkResultsSingle['keyId'] = item[key]
                        if key in inputChecks:
                            if key in testList[0]:
                                if item[key] == testList[0][key]:
                                    logger.debug(key + " Check Passed")
                                    checkResultsSingle[key] = {'pass': {'golden': goldenList[0][key], 'test': testList[0][key]}}
                                else:
                                    logger.warning(key + " Check Failed")
                                    checkResultsSingle[key]={'fail': {'golden': goldenList[0][key], 'test': testList[0][key]}}
                            else:
                                logger.warning(key + " Check Failed")
                                checkResultsSingle[key] = {'fail': {'golden': goldenList[0][key], 'test': ""}}

                    checkResultsSingleList.append(copy.copy(checkResultsSingle))
                    checkResultsSingle = {}


        else:
            logger.debug("------------------")
            logger.debug(keyBase + " Checks")
            logger.debug("------------------")
            for item in inputGolden.keys():
                if item in inputTest.keys():
                    if item == 'keyId':
                        checkResultsDetail['keyId'] = inputGolden[item]

                    elif item in inputChecks:
                        if inputGolden[item] == inputTest[item]:
                            logger.debug(item + " Check Passed")
                            checkResultsDetail[item] = {'pass': {'golden': inputGolden[item], 'test': inputTest[item]}}
                        else:
                            logger.warning(item + " Check Failed")
                            checkResultsDetail[item] = {'fail': {'golden': inputGolden[item], 'test': inputTest[item]}}
    for item in sorted(checkResultsNotInTest):
        notInGoldenList = filter(lambda x: x[uniqueId] == item, inputGolden)
        logger.debug("------------------")
        logger.debug(keyBase + item )
        for item in notInGoldenList:
            for key in item.keys():
                if key == 'keyId':
                    checkResultsSingle['keyId'] = item[key]
                elif key in inputChecks:
                    logger.warning(key + " Check Failed")
                    checkResultsSingle[key] = {'fail': {'golden': notInGoldenList[0][key], 'test' : "None"}}
                    failResultsSingle[key]= {'fail': {'golden': notInGoldenList[0][key], 'test' : "None"}}
            checkResultsSingleList.append(copy.copy(checkResultsSingle))
            checkResultsSingle = {}

    checkResultsDetail[uniqueId]=checkResultsSingleList
    checkResults[keyBase] = checkResultsDetail
    return checkResults
#########################################################################
#  wlan Compare
#
#
#########################################################################
def wlanCompare(inputGolden,inputTest,cfg):
    goldenAllSsidList = []
    testAllSsidList = []
    inputCheckKeys=cfg['functions']['wlans']
    checkResults = {}
    checkResultsDetail = {}
    checkResultsSingle = {}
    checkResultsSingleList = []
    checkResultsNotInTest = []
    checkResultsNotInGolden = []
    failResultsSingle={}
    failResultsSingleList=[]
    failResultsDetail={}
    failResults={}
    for item in inputGolden['wlans']:
        if "ssid" in item:
            goldenAllSsidList.append((item['ssid'],item['profileName']))
    for item in inputTest['wlans']:
        if len(item) > 2:
            testAllSsidList.append((item['ssid'],item['profileName']))
    # in Test config but not in Golden Config
    for item in testAllSsidList:
        if item not in goldenAllSsidList:
            logger.warning(item[0] + " SSID in Test Config, but not in Golden Config")
            checkResultsNotInGolden.append(item)
        checkResultsDetail['NotInGolden'] = checkResultsNotInGolden
    # in Golden Config but not in test config
    for item in goldenAllSsidList:
        if item not in testAllSsidList:
            logger.warning(item[0] + " SSID in Golden Config, but not in Test Config")
            checkResultsNotInTest.append(item)
        checkResultsDetail['NotInTest'] = checkResultsNotInTest
    # get intersection between golden & test SSID Lists
    intersectionSsid=list(set(goldenAllSsidList) & set(testAllSsidList))
    for item in sorted(intersectionSsid):
        goldenSsidList = filter(lambda x: x['profileName'] == item[1], inputGolden['wlans'])
        testSsidList = filter(lambda x: x['profileName'] == item[1], inputTest['wlans'])
        for item in goldenSsidList:
            logger.debug("------------------")
            logger.debug("SSID: " + item['ssid']  + " Profile Name: " + item['profileName'])
            for key in item.keys():
                if key == 'keyId':
                    checkResultsSingle['keyId'] = item[key]
                elif key in inputCheckKeys:
                    if key in testSsidList[0]:
                        if item[key] == testSsidList[0][key]:
                            logger.debug(key + " Check Passed")
                            checkResultsSingle[key] = {
                                'pass': {'golden': goldenSsidList[0][key], 'test': testSsidList[0][key]}}
                        else:
                            logger.warning(key + " Check Failed")
                            checkResultsSingle[key] = {
                                'fail': {'golden': goldenSsidList[0][key], 'test': testSsidList[0][key]}}
                            failResultsSingle[key] = {
                                'fail': {'golden': goldenSsidList[0][key], 'test': testSsidList[0][key]}}
            checkResultsSingleList.append(copy.copy(checkResultsSingle))
            checkResultsSingle = {}
            failResultsSingleList.append(copy.copy(checkResultsSingle))
            failResultsSingle = {}
    for item in sorted(checkResultsNotInTest):
        notInGoldenSsidList = filter(lambda x: x['profileName'] == item[1], inputGolden['wlans'])
        for item in notInGoldenSsidList:
            logger.debug("------------------")
            logger.debug("SSID: " + item['ssid']  + " Profile Name: " + item['profileName'])
            for key in item.keys():
                if key == 'keyId':
                    checkResultsSingle['keyId'] = item[key]
                elif key in inputCheckKeys:
                    logger.warning(key + " Check Failed")
                    checkResultsSingle[key] = {'fail': {'golden': notInGoldenSsidList[0][key], 'test' : "None"}}
                    failResultsSingle[key]= {'fail': {'golden': notInGoldenSsidList[0][key], 'test' : "None"}}
            checkResultsSingleList.append(copy.copy(checkResultsSingle))
            checkResultsSingle = {}
            failResultsSingleList.append(copy.copy(checkResultsSingle))
            failResultsSingle = {}
    failResultsDetail['wlanList']=failResultsSingleList
    failResults['wlans']=failResultsDetail
    checkResultsDetail['wlanList']=checkResultsSingleList
    checkResults['wlans']=checkResultsDetail
    return checkResults
#########################################################################
#  Full Compare
#
#
#########################################################################
def configFullCompare(inputGolden,inputTest,cfg):
    inputChecks=cfg['functions']
    checkResults={}
    finalResults={}
    golden=inputGolden['golden']

    #iterate through checks enabled in config file\
    logger.info("Starting Configuration Checks")
    for config in inputTest.keys():
        for check in inputChecks.keys():
            if check in inputGolden['golden'].keys():
                if check == "apGroup":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='apGroup', uniqueId='apGroupSiteName',
                                             cfg=cfg))
                    # checkResults.update(configSectionCompare(inputGolden['golden'][check],inputTest[config][check],keyBase='apGroup',uniqueId='apGroupSiteName',cfg=cfg))
                elif check == "advanced":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='advanced', uniqueId='', cfg=cfg))
                elif check == "airewave80211a":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='airewave80211a', uniqueId='', cfg=cfg))
                elif check == "airewave80211b":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='airewave80211b', uniqueId='', cfg=cfg))
                elif check == "apImageBundle":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='apImageBundle', uniqueId='', cfg=cfg))
                elif check == "authListConfig":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='authListConfig', uniqueId='', cfg=cfg))
                elif check == "certConfig":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='certConfig', uniqueId='', cfg=cfg))
                elif check == "cleanair80211a":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='cleanair80211a', uniqueId='', cfg=cfg))
                elif check == "cleanair80211b":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='cleanair80211b', uniqueId='', cfg=cfg))
                elif check == "customWeb":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='customWeb', uniqueId='', cfg=cfg))
                elif check == "dnsConfiguration":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='dnsConfiguration', uniqueId='', cfg=cfg))
                elif check == "flexGroup":
                    checkResults.update(configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='flexGroup', uniqueId='flexGroupName',
                                             cfg=cfg))
                elif check == "fra":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='fra', uniqueId='', cfg=cfg))
                elif check == "interfaceList":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='interfaceList', uniqueId='interfaceName',
                                             cfg=cfg))
                elif check=="interfaceGroupList":
                    checkResults.update(configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='interfaceGroupList', uniqueId='interfaceGroupName', cfg=cfg))
                elif check == "ipv6Config":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='ipv6Config', uniqueId='', cfg=cfg))
                elif check == "loadBalance":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='loadBalance', uniqueId='', cfg=cfg))
                elif check == "localEapConfig":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='localEapConfig', uniqueId='', cfg=cfg))
                elif check == "macFilters":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='macFilters', uniqueId='macFilterMac',
                                             cfg=cfg))
                elif check == "mdnsConfig":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='mdnsConfig', uniqueId='mdnsServices',
                                             cfg=cfg))
                elif check == "mediaStream":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='mediaStream', uniqueId='streams',
                                             cfg=cfg))
                elif check == "mobility":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='mobility', uniqueId='mobilityMembers',
                                             cfg=cfg))
                elif check == "network80211a":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='network80211a', uniqueId='', cfg=cfg))
                elif check == "network80211b":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='network80211b', uniqueId='', cfg=cfg))
                elif check == "networkInfo":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='networkInfo', uniqueId='', cfg=cfg))
                elif check == "ntpConfig":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='ntpConfig', uniqueId='', cfg=cfg))
                elif check == "portSummary":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='portSummary', uniqueId='portNumber',
                                             cfg=cfg))
                elif check == "qos":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='qos', uniqueId='', cfg=cfg))
                elif check == "radiusConfig":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='radiusConfig', uniqueId='', cfg=cfg))
                elif check == "redundancyConfig":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='redundancyConfig', uniqueId='', cfg=cfg))
                elif check == "rfProfile":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='rfProfile', uniqueId='rfProfileName',
                                             cfg=cfg))
                elif check == "rogueConfig":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='rogueConfig', uniqueId='', cfg=cfg))
                elif check == "switchDetail":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='switchDetail', uniqueId='', cfg=cfg))
                elif check == "sysInfo":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='sysInfo', uniqueId='', cfg=cfg))
                elif check == "tacacs":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='tacacs', uniqueId='', cfg=cfg))
                elif check == "wlans":
                    checkResults.update(wlanCompare(inputGolden['golden'], inputTest[config], cfg))
                elif check == "wlanMfp":
                    checkResults.update(
                        configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='wlanMfp', uniqueId='', cfg=cfg))
                elif check == "wps":
                    checkResults.update(configSectionCompare(inputGolden['golden'][check], inputTest[config][check], keyBase='wps', uniqueId='', cfg=cfg))
        finalResults[config]=checkResults
        checkResults={}
    logger.info("Configuration Checks Completed")
    #with open('results.txt', 'wt') as out:
    #    pprint(finalResults, stream=out)

    return finalResults


#########################################################################
# Write values to xls
#
# #########################################################################
def resultsToXls(input):
    resultsWorkbook = xlsxwriter.Workbook(("test.xlsx"))
    failFormat=resultsWorkbook.add_format({'bold': True, 'bg_color':'red'})
    headerFormat=resultsWorkbook.add_format({'bold': True, 'underline' : True, 'font_size': 14})
    subHeaderFormat = resultsWorkbook.add_format({'bold': True, 'font_size': 12, 'bg_color':'#00FF00'})
    numPercentFormat = resultsWorkbook.add_format()
    numPercentFormat.set_num_format(0x09)
    worksheetNames=[]
    startRow=2
    startCol=0
    dataRow=2
    dataCol=0
    worksheetSummary=resultsWorkbook.add_worksheet('Summary')
    logger.info("Generating Output Excel")
    for key in sorted(input.keys()):
        if key not in worksheetNames:
            worksheet=resultsWorkbook.add_worksheet(key)
            worksheetNames.append(key)
            worksheet.set_column('A:A', 25)
            worksheet.set_column('B:B', 15)
            worksheet.set_column('C:C', 25)
            worksheet.set_column('D:D', 25)
            worksheet.set_column('E:E', 15)
            worksheet.write(0, 0, 'Config Check', headerFormat)
            worksheet.write(0, 1, 'Test Result', headerFormat)
            worksheet.write(0, 2, 'Golden Config Value', headerFormat)
            worksheet.write(0, 3, 'Test Config Value', headerFormat)
            worksheet.conditional_format(0,1,10000,1,{'type': 'text',
                                                     'criteria': 'containing',
                                                     'value': 'fail',
                                                 'format':failFormat})
        headerList=input[key].keys()
        dictRecursion(input[key],startRow, startCol, worksheet,headerFormat,subHeaderFormat,headerList)
        worksheet.write('E1','Total Rows')
        worksheet.write('E2', 'Failed Checks')
        worksheet.write('E3', 'Passed Checks')
        worksheet.write('E4', 'Compliance %')
        worksheet.write_formula('F1', '=LOOKUP(2,1/(A:A<>""),ROW(A:A))')
        worksheet.write_formula('F2', '=COUNTIF(B1:INDIRECT(CONCATENATE("B",F1)), "fail")')
        worksheet.write_formula('F3', '=COUNTIF(B1:INDIRECT(CONCATENATE("B",F1)), "pass")')
        worksheet.write_formula('F4', '=F3/(F3+F2)', numPercentFormat)

    worksheetData=resultsWorkbook.add_worksheet('Data')
    worksheetData.set_column('A:A', 20)
    worksheetData.set_column('B:E', 15)
    dataHeader=('Controller Name','Total Rows','Total Checks', 'Total Fail', 'Total Pass')
    worksheetData.write_row('A1', dataHeader, subHeaderFormat)
    for item in worksheetNames:
        worksheetData.write(dataRow, 0, item)
        worksheetData.write(dataRow, 1, '=\'%s\'!F1' % (item))
        worksheetData.write(dataRow, 2, '=\'%s\'!F2 + \'%s\'!f3' %(item,item))
        worksheetData.write(dataRow, 3, '=\'%s\'!F2' % (item))
        worksheetData.write(dataRow, 4, '=\'%s\'!F3' % (item))
        dataRow +=1
    worksheetSummary.set_column('A:A', 25)
    worksheetSummary.write('A4','Total Controllers',subHeaderFormat)
    worksheetSummary.write('B4', len(worksheetNames))
    worksheetSummary.write('A5', 'Total Failed Checks',subHeaderFormat)
    worksheetSummary.write_formula('B5', '=sum(\'%s:%s\'!F2)'%(worksheetNames[0],worksheetNames[len(worksheetNames)-1]))
    worksheetSummary.write('A6', 'Total Passed Checks',subHeaderFormat)
    worksheetSummary.write_formula('B6', '=sum(\'%s:%s\'!F3)' % (worksheetNames[0], worksheetNames[len(worksheetNames) - 1]))
    worksheetSummary.write('A7', 'Total Compliance Percentage',subHeaderFormat)
    worksheetSummary.write_formula('B7', '=B6/(B5+B6)', numPercentFormat)
    failedChart=resultsWorkbook.add_chart({'type': 'pie'})
    failedChart.add_series({'categories': '=Data!$A$3:$A$500','values': '=Data!$D$3:$D$500'})
    worksheetSummary.insert_chart('D4', failedChart)
    resultsWorkbook.close()
    logger.info("Output Excel Generated Successfully")
#########################################################################
# Recursive Functiont to write values to xls
#
#########################################################################
def dictRecursion(input,startRow, startCol, worksheet, headerFormat, subHeaderFormat,headerList):
    global row
    global failureCount
    global totalCount
    failureCount=0
    totalCount=0
    row=startRow
    col=startCol
    returnValue=""
    printKeyList=['pass', 'fail', 'NotInTest', 'NotInGolden']
    if isinstance(input,dict):
        for key in sorted(input.keys()):
            if key in headerList:
                worksheet.write(row,col,key,headerFormat)
                row+=1
            if key not in printKeyList:
                worksheet.write(row, col, key)
                returnValue=input[key]
                dictRecursion(returnValue,row,col,worksheet,headerFormat,subHeaderFormat,headerList)
            elif key in printKeyList:
                if isinstance(input[key], dict):
                    worksheet.write(row,col+1, key)
                    if isinstance(input[key]['golden'],str):
                        worksheet.write(row,col+2, input[key]['golden'])
                    else:
                        worksheet.write(row, col + 2, "See Details")
                    if isinstance(input[key]['test'],str):
                        worksheet.write(row,col+3, input[key]['test'])
                    else:
                        worksheet.write(row, col + 3, "See Details")
                    row+=1

    elif isinstance(input, list):
        for item in input:
            if 'keyId' in item:
                worksheet.write(row, col, item['keyId'],subHeaderFormat)
                row+=1
            dictRecursion(item, row, col, worksheet,headerFormat,subHeaderFormat,headerList)

#########################################################################
#  Output to json and post to splunk
#
#
#########################################################################
def splunkExport(input):
    import requests
    import json
    import pprint
    data={}
    wlcNames=[]
    splunkServer="192.168.1.46"
    splunkPort="8088"
    pprint.pprint(input,width=1)
    for key in input.keys():
        data['event']={key : input[key]}
        headers = {
           'Authorization': 'Splunk 42C6ABE9-BDDA-4532-871A-896E2A9C05DD',
            }

        r=requests.post('https://192.168.1.46:8088/services/collector', headers=headers, json=data, verify=False)
        print(r)
#########################################################################
#  Main
#
#
#########################################################################
def main(**kwargs):
    #load Config
    if kwargs:
        args = kwargs
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument('runConfigGolden', help='Golden Configuration')
        parser.add_argument('runConfigTest', help='Single Test file or ZIP')
        args = parser.parse_args()
    with open("config.yaml", 'r') as ymlfile:
        cfg=yaml.load(ymlfile)

    golden=configParse(args.runConfigGolden,isGolden=True)
    test=configParse(args.runConfigTest,isGolden=False)
    results=configFullCompare(golden,test,cfg)
    resultsToXls(results)
    logger.info("Configuration Comparison Completed Successfully")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(str(e.message))
        os._exit(1)
