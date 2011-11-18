Examples
========

 * Add 0/1/ to the beginning of each port name on switch checks:

        circus rename_checks "(switch-va-3 port) (\d+)" "\1 0/1/\2"

 * Add graphs for all checks beginning switch-va-3 port:

        circus add_graphs switch "(switch-va-3) port (\S*)"

 * Add a http check for omniti.com:

        circus add_check http www.omniti.com "Ashburn, VA, US"
