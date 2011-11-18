Examples
========

 * Add 0/1/ to the beginning of each port name on switch checks:

        circus rename_checks "(switch-va-3 port) (\d+)" "\1 0/1/\2"

 * Add graphs for all checks beginning switch-va-3 port:

        circus add_graphs switch "(switch-va-3) port (\S*)"

 * Add a http check for omniti.com:

        circus add_check http www.omniti.com "Ashburn, VA, US"

 * Add checks for all ports on a switch:

        circus add_switch 10.0.0.1 "Ashburn, VA US" public "switch-1"

    * The parameters are:
        * IP of the switch
        * Circonus agent to use
        * SNMP community name of the switch
        * The name to use for the switch in the check titles
        * (optional) a regex to match on to only add some ports
    * This check requires the snmp tools to be added locally and for you to be
      able to contact the switch directly via SNMP (it runs snmpwalk to find
      out what switch ports to add).
