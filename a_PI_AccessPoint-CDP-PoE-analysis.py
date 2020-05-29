# $language = "python"
# $interface = "1.0"

import argparse
import csv
import logging
import os
import sys

# Add script directory to the PYTHONPATH so we can import our modules (only if run from SecureCRT)
if 'crt' in globals():
    script_dir, script_name = os.path.split(crt.ScriptFullName)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir + '/../venv38/lib/python3.8/site-packages')
        sys.path.insert(0, script_dir)
else:
    script_dir, script_name = os.path.split(os.path.realpath(__file__))

# Now we can import our custom modules
from securecrt_tools import scripts
from builtins import input

# If this script is run from SecureCRT directly, use the SecureCRT specific class
if __name__ == "__builtin__":
    temp_msg = scripts.CRTScript(crt)
elif __name__ == "__main__":
    temp_msg = scripts.DebugScript(os.path.realpath(__file__))
else:
    temp_msg = None

import piapi

piapi.DEFAULT_API_URI = '/webacs/api/v4/'

# Create global logger so we can write debug messages from any function (if debug mode setting is enabled in settings).
logger = logging.getLogger("securecrt")

my_handler = logging.StreamHandler()
my_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(levelname)-5s %(asctime)-24s %(filename)s line %(lineno)-d %(funcName)s() :: %(message)s')
my_handler.setFormatter(formatter)

logger.addHandler(my_handler)

logger.debug("Starting execution of {0}".format(script_name))

# ################################################   SCRIPT LOGIC   ###################################################


def script_main(session):
    """
    | SINGLE device script
    | Morphed: Gordon Rogier grogier@cisco.com
    | Framework: Jamie Caesar jcaesar@presidio.com

    This script will

    :param session: A subclass of the sessions.Session object that represents this particular script session (either
                SecureCRTSession or DirectSession)
    :type session: sessions.Session

    """
    # Get script object that owns this session, so we can check settings, get textfsm templates, etc
    script = session.script

    # Start session with device, i.e. modify term parameters for better interaction (assuming already connected)
    session.start_cisco_session()

    # Validate device is running a supported OS
    session.validate_os(["AireOS"])

    # Get additional information we'll need
    get_ap_detail(session, to_cvs=True)

    # Return terminal parameters back to the original state.
    session.end_cisco_session()

def fetch_PI_AccessPointDetails(pi_username, pi_password, pi_host, pi_vd='', to_csv=''):

    api = piapi.PIAPI('https://{}/'.format(pi_host), pi_username, pi_password, virtual_domain=pi_vd, verify=False)
    AccessPointDetails = api.request("AccessPointDetails", concurrent_requests=2, hold=3)

    output = AccessPointDetails

    if to_csv:
        # define the header in the order want the data to appear
        header = ['name', 'model']
        # check to make sure we got all the keys noted... eg if we start to code more aspects for the output
        for entry in output:
            for this_key in entry:
                another_new_key = 'me'
                if this_key not in header: header.append(this_key)
        # open the file to write
        with open(to_csv, 'w', newline='') as output_csv:
            # create a csv_writer to format the output
            csv_writer = csv.DictWriter(output_csv, fieldnames=header)
            # write a header line
            csv_writer.writeheader()
            # step across each entry and write a row for it
            for entry in output:
                csv_writer.writerow(entry)

    return output

# ################################################  SCRIPT LAUNCH   ###################################################

# If this script is run from SecureCRT directly, use the SecureCRT specific class
if __name__ == "__builtin__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', metavar='username', type=str, dest='pi_username')
    parser.add_argument('-p', metavar='password', type=str, dest='pi_password')
    parser.add_argument('-s', type=str, metavar='server', dest='pi_host')
    parser.add_argument('-d', type=str, metavar='virtual_domain', dest='pi_vd')
    parser.add_argument('--to_csv', type=str, metavar='csv_filename', dest='to_csv')
    in_args = vars(parser.parse_args())

    # Get rid of any arg that has not been set at this point
    # curl_call = { k : in_args[k] for k in in_args if in_args[k] != None }

    fetch_PI_AccessPointDetails(**in_args)
    # Shutdown logging after
    logging.shutdown()

# If the script is being run directly vs being run via SecureCRT (nor imported)
elif __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', metavar='username', type=str, dest='pi_username')
    parser.add_argument('-p', metavar='password', type=str, dest='pi_password')
    parser.add_argument('-s', type=str, metavar='server', dest='pi_host')
    parser.add_argument('-d', type=str, metavar='virtual_domain', dest='pi_vd')
    parser.add_argument('--to_csv', type=str, metavar='csv_filename', dest='to_csv')
    in_args = vars(parser.parse_args())

    # Get rid of any arg that has not been set at this point
    # curl_call = { k : in_args[k] for k in in_args if in_args[k] != None }

    fetch_PI_AccessPointDetails(**in_args)

    # Shutdown logging after
    logging.shutdown()
