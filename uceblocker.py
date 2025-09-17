#!/usr/bin/env python3
import os, sys, json, urllib.request, configparser

def read_config():
    config = configparser.ConfigParser(allow_no_value=True)
    config.read('config.ini')
    config_values = {
        'exceptions': config.get('Exceptions', 'domains'),
        'trap_users': config.get('Extra', 'trap_users'),
        'sponsors': config.get('Extra', 'sponsors'),
        'reject_message_outbound': config.get('Messages', 'outbouncemsg'),
        'reject_message_inbound': config.get('Messages', 'inbouncemsg'),
        'reject_message_trap_users_out':config.get('Messages', 'trap_users_out'),
        'reject_message_trap_users_in':config.get('Messages', 'trap_users_in'),
        'reject_message_sponsors_in':config.get('Messages', 'sponsors_in'),
        'reject_message_sponsors_out':config.get('Messages', 'sponsors_out'),
        'reject_file_path': config.get('Postfix', 'rejectpath'),
        'branding': config.get('Branding', 'enabled'),
        'branding_text': config.get('Branding', 'text'),
        'postmap': config.get('Postfix', 'postmap'),
        'sudo': config.get('System', 'sudo'),
        'redirmail': config.get('Postfix', 'redirmail')
    }
    return config_values

def msg_builder(domain, msg):
    if config_data['branding']:
        return "{} REJECT 550 {} {}\n".format(domain, msg, config_data['branding_text'])
    else:
        return "{} REJECT 550 {}\n".format(domain, msg)

def check_domain(domain):
    if config_data['exceptions'] != None:
        if domain in config_data['exceptions'].split(","):
            return False
        else:
            return True
    else:
        return True

def redir_sensors(domain):
    return "#{} redirection\n@{} {}\n".format(domain, domain, config_data['redirmail'])

def extract_domain(url):
    url = url.split("://", 1)[-1]
    url = url.split("/", 1)[0]
    url = url.split(":", 1)[0]
    if url.startswith("www."):
        url = url[4:]

    return url.lower()

def process_data(data,buildwhat):
    tmp=""
    if buildwhat == "sensors":
        for i in data:
            tmp+=redir_sensors(i['domain'])
            subdomains = i.get("subdomains",[])
            for s in subdomains:
                tmp+=redir_sensors(s)
    else:
        for i in data:
            if check_domain(extract_domain(i['url'])):
                tmp+=msg_builder(extract_domain(i['url']), config_data[buildwhat])
    return tmp

def postmap(file):
    try:
        os.system('{} {} hash:{}/{}'.format(config_data['sudo'], config_data['postmap'], config_data['reject_file_path'], file))
    except Exception as e:
        sys.exit(e)

def write_file(file,content):
    with open("{}/{}".format(config_data['reject_file_path'],file), 'w') as f:
        f.write(content)
    postmap(file)

url = 'https://uceprotect.wtf/uceprotect.json'
data = None

if __name__ == "__main__":
    try:
        config_data = read_config()
    except Exception as e:
        sys.exit(e)

    try:
        print("Trying to download data from https://uceprotect.wtf...")
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'furit-systems/uceblocker')
        data = urllib.request.urlopen(req).read()
    except Exception as e:
        sys.exit(e)
    
    uce_customers = json.loads(data)['customers']
    uce_sensors = json.loads(data)['domains']
    trap_users = json.loads(data)['trap_users']
    sponsors = json.loads(data)['sponsors']
    
    write_file("senders",process_data(uce_customers, "reject_message_inbound"))
    write_file("recipients",process_data(uce_customers, "reject_message_outbound"))
    write_file("sensors",process_data(uce_sensors, "sensors"))
    
    if config_data['trap_users']:
        print("We're going after the trap users too...")
        write_file("trap_users_sender", process_data(trap_users, "reject_message_trap_users_in"))
        write_file("trap_users_recipient", process_data(trap_users, "reject_message_trap_users_out"))
    if config_data['sponsors']:
        print("We're going after the sponsors too...")
        write_file("sponsors_sender", process_data(sponsors, "reject_message_sponsors_in"))
        write_file("sponsors_recipient", process_data(sponsors, "reject_message_sponsors_out"))