"""
This script provides several functions for interacting with the Tableau
licensing server. The two most important functions are the retire_license() and
activate_license() functions.


All steps taken from this documentation provided by Tableau
http://a.pomf.se/hteuav.docx
"""
import os
import subprocess
import sys

tableau_dir = '/Applications/Tableau.app/Contents'
cust_binary = "%s/Frameworks/FlexNet/custactutil" % tableau_dir
tableau_url = 'https://licensing.tableausoftware.com:443/flexnet'\
              '/services/ActivationService?wsdl'

tableau_key = 'REPLACE WITH YOUR TABLEAU KEY'


def install_flex_agent():
    """
    install_flex_agent()

    Installs the FlexNet licensing agent needed to activate/retire licenses
    """
    if not os.path.exists('/Library/Preferences/FLEXnet Publisher'):
        try:
            print 'Installing FLEXnet Licensing agent'
            subprocess.call(
                "/usr/sbin/installer -pkg %s/Installers"
                '/\"Tableau FLEXNet.pkg\" -target /'
                % tableau_dir, shell=True
            )
        except Exception as e:
            print "An error occured while installing FLEXnet: %s" % e
            sys.exit(1)


def get_installed_licenses():
    """
    get_installed_licenses()

    Executes the custactutil binary to get the active licenses on a system
    """
    return subprocess.check_output("%s -view" % cust_binary, shell=True)


def retire_license(active_licenses):
    """
    retire_license(active_licenses)

    Loops through the licenses passed into the function and retires each one
    against the Tableau licensing servers
    """
    for line in active_licenses.split('\n'):
        if 'Fulfillment ID:' in line:
            fulfil_id = line.split()[2]

            # Retire each ID
            retire_cmd = "%s -return %s -reason 1 -comm "\
                "soap -commServer %s" % (cust_binary, fulfil_id, tableau_url)

            # Delete trial IDs, those cannot be retired
            if 'LOCAL_TRIAL_FID' in fulfil_id:
                retire_cmd = "%s -delete %s" % (cust_binary, fulfil_id)

            print "Retiring %s" % fulfil_id
            subprocess.call(retire_cmd, shell=True)


def activate_license(tableau_key):
    """
    activate_license(tableau_key)

    Activates the passed in license against the Tableau licensing server
    """
    # Apply the new license
    apply_new_license_cmd = "%s -served -comm soap -commServer "\
                            "%s -entitlementID %s" % (
                                cust_binary, tableau_url, tableau_key
                            )

    print "Activating new License"
    subprocess.call(apply_new_license_cmd, shell=True)


if __name__ == '__main__':
        install_flex_agent()
        active_licenses = get_installed_licenses()
        retire_license(active_licenses)
        activate_license(tableau_key)
