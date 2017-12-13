# $language = "python"
# $interface = "1.0"

import os
import sys
import logging

# Add script directory to the PYTHONPATH so we can import our modules (only if run from SecureCRT)
if 'crt' in globals():
    script_dir, script_name = os.path.split(crt.ScriptFullName)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
else:
    script_dir, script_name = os.path.split(os.path.realpath(__file__))

# Now we can import our custom modules
from securecrt_tools import scripts
from securecrt_tools import sessions
import s_cdp_to_csv

# Create global logger so we can write debug messages from any function (if debug mode setting is enabled in settings).
logger = logging.getLogger("securecrt")
logger.debug("Starting execution of {}".format(script_name))


# ################################################   SCRIPT LOGIC   ###################################################

def script_main(script):
    """
    | MULTIPLE device script
    | Author: Jamie Caesar
    | Email: jcaesar@presidio.com

    This script will grab the detailed CDP information from each Cisco IOS or NX-OS device in the provided device list
    CSV file and export each to a CSV file containing the important information, such as Remote Device hostname, model
    and IP information, in addition to the local and remote interfaces that connect the devices.

    :param script: A subclass of the scripts.Script object that represents the execution of this particular script
                   (either CRTScript or DirectScript)
    :type script: scripts.Script
    """
    # Create logger instance so we can write debug messages (if debug mode setting is enabled in settings).
    logger = logging.getLogger("securecrt")
    logger.debug("Starting execution of {}".format(script_name))

    session = script.get_main_session()

    # If this is launched on an active tab, disconnect before continuing.
    logger.debug("<M_SCRIPT> Checking if current tab is connected.")
    if session.is_connected():
        logger.debug("<M_SCRIPT> Existing tab connected.  Stopping execution.")
        raise scripts.ScriptError("This script must be launched in a not-connected tab.")

    # Load a device list
    device_list = script.import_device_list()
    if not device_list:
        return

    check_mode = True
    # # #########################################  START CHECK MODE SECTION  ###########################################
    # # Ask if this should be a test run (generate configs only) or full run (push updates to devices)
    # # Comment out or remove the entire CHECK MODE SECTION if you don't want to prompt for check mode
    # check_mode_message = "Do you want to run this script in check mode? (Only generate configs)\n" \
    #                      "\n" \
    #                      "Yes = Connect to device and write change scripts to a file ONLY\n" \
    #                      "No = Connect to device and PUSH configuration changes"
    # message_box_design = ICON_QUESTION | BUTTON_YESNOCANCEL
    # logger.debug("Prompting the user to run in check mode.")
    # result = script.message_box(check_mode_message, "Run in Check Mode?", message_box_design)
    # if result == IDYES:
    #     logger.debug("<M_SCRIPT> Received 'True' for Check Mode.")
    #     check_mode = True
    # elif result == IDNO:
    #     logger.debug("<M_SCRIPT> Received 'False' for Check Mode.")
    #     check_mode = False
    # else:
    #     return
    # ###########################################  END CHECK MODE SECTION  #############################################

    # ###########################################  START JUMP BOX SECTION  #############################################
    # Check settings if we should use a jumpbox.  If so, prompt for password (and possibly missing values)
    use_jumpbox = script.settings.getboolean("Global", "use_jumpbox")

    if use_jumpbox:
        jumpbox = script.settings.get("Global", "jumpbox_host")
        j_username = script.settings.get("Global", "jumpbox_user")
        j_ending = script.settings.get("Global", "jumpbox_prompt_end")

        if not jumpbox:
            jumpbox = script.prompt_window("Enter the HOSTNAME or IP for the jumpbox".format(jumpbox))
            script.settings.update("Global", "jumpbox_host", j_username)

        if not j_username:
            j_username = script.prompt_window("Enter the USERNAME for {}".format(jumpbox))
            script.settings.update("Global", "jumpbox_user", j_username)

        j_password = script.prompt_window("Enter the PASSWORD for {}".format(j_username), hide_input=True)

        if not j_ending:
            j_ending = script.prompt_window("Enter the last character of the jumpbox CLI prompt")
            script.settings.update("Global", "jumpbox_prompt_end", j_ending)

    # #############################################  END JUMP BOX SECTION  #############################################

    # #########################################  START DEVICE CONNECT LOOP  ############################################

    # We are not yet connected to a jump box.  This will be updated later in the code if needed.
    jump_connected = False
    # Create a filename to keep track of our connection logs, if we have failures.  Use script name without extension
    failed_log = session.create_output_filename("{}-LOG".format(script_name.split(".")[0]), include_hostname=False)

    for device in device_list:
        hostname = device['hostname']
        protocol = device['protocol']
        username = device['username']
        password = device['password']
        enable = device['enable']

        if jumpbox:
            if "ssh" in protocol.lower():
                try:
                    if not jump_connected:
                        session.connect_ssh(jumpbox, j_username, j_password, prompt_endings=[j_ending])
                        jump_connected = True
                    session.ssh_via_jump(hostname, username, password)
                    per_device_work(session, check_mode, enable)
                    session.disconnect_via_jump()
                except (sessions.ConnectError, sessions.InteractionError) as e:
                    error_msg = e.message
                    with open(failed_log, 'a') as logfile:
                        logfile.write("Connect to {} failed: {}\n".format(hostname, error_msg))
                    session.disconnect()
                    jump_connected = False
            elif protocol.lower() == "telnet":
                try:
                    if not jump_connected:
                        session.connect_ssh(jumpbox, j_username, j_password, prompt_endings=[j_ending])
                        jump_connected = True
                    session.telnet_via_jump(hostname, username, password)
                    per_device_work(session, check_mode, enable)
                    session.disconnect_via_jump()
                except (sessions.ConnectError, sessions.InteractionError) as e:
                    with open(failed_log, 'a') as logfile:
                        logfile.write("Connect to {} failed: {}\n".format(hostname, e.message))
                    session.disconnect()
                    jump_connected = False
        else:
            try:
                session.connect(hostname, username, password, protocol=protocol)
                per_device_work(session, check_mode, enable)
                session.disconnect()
            except sessions.ConnectError as e:
                with open(failed_log, 'a') as logfile:
                    logfile.write("Connect to {} failed: {}\n".format(hostname, e.message))
            except sessions.InteractionError as e:
                with open(failed_log, 'a') as logfile:
                    logfile.write("Failure on {}: {}\n".format(hostname, e.message))

    # If we are still connected to our jump box, disconnect.
    if jump_connected:
        session.disconnect()

    # ##########################################  END DEVICE CONNECT LOOP  #############################################


def per_device_work(session, check_mode, enable_pass):
    """
    This function contains the code that should be executed on each device that this script connects to.  It is called
    after establishing a connection to each device in the loop above.

    You can either put your own code here, or if there is a single-device version of a script that performs the correct
    task, it can be imported and called here, essentially making this script connect to all the devices in the chosen
    CSV file and then running a single-device script on each of them.
    """
    s_cdp_to_csv.script_main(session)


# ################################################  SCRIPT LAUNCH   ###################################################

# If this script is run from SecureCRT directly, use the SecureCRT specific class
if __name__ == "__builtin__":
    # Initialize script object
    crt_script = scripts.CRTScript(crt)
    # Run script's main logic against the script object
    script_main(crt_script)
    # Shutdown logging after
    logging.shutdown()

# If the script is being run directly, use the simulation class
elif __name__ == "__main__":
    # Initialize script object
    direct_script = scripts.DirectScript(os.path.realpath(__file__))
    # Run script's main logic against the script object
    script_main(direct_script)
    # Shutdown logging after
    logging.shutdown()