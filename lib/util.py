"""Various utility functions"""
import logging
import sys

def confirm(text="OK to continue?"):
    response = None
    while response not in ['Y', 'y', 'N', 'n']:
        response = raw_input("%s (y/n) " % text)
    if response in ['Y', 'y']:
        return True
    return False

def get_agent(api, agent_name):
    rv = api.list_agents()
    agents = dict([(i['name'], i['agent_id']) for i in rv])
    try:
        return agents[agent_name]
    except KeyError:
        logging.error("Invalid/Unknown Agent: %s" % agent_name)
        print "Valid Agents:"
        for a in agents:
            print "   %s" % a
        sys.exit(1)
