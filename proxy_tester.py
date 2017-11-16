# Proxy Tester.py
# developer: @bopped /// twitter : @backdoorcook
import requests, json, time, threading, sys, os, pprint, datetime

### config stuff ###

# proxy format for requests is user:pass@site:port
# some sites output this as site:port:user:pass
# if the proxies.dat is formatted that way - set the following to true
convert_proxy_data = True
proxy_list_file = 'proxies.dat'
site_list_file = 'sites.dat'
output_directory = 'output' # no trailing /
timeout = 10 # in seconds


#Current Ms display
def millis():
    return int(round(time.time() * 1000))


#Current Time
def getCurrentTime():
    return time.strftime("%H:%M:%S")


def exit_tester(finished=False):
    global active
    print_results()
    if not finished:
        print "Timeout:{} seconds".format(timeout)
        print "{} thread requests still open.".format(active)
    os._exit(0)


# ip:port:username:pass -> username:pass@ip:port
def convert_proxy_link(link):
    p = link.split(':')
    if len(p) == 4:
        return '{}:{}@{}:{}'.format(p[2],p[3],p[0],p[1])
    elif len(p) == 3:
        return '{}@{}:{}'.format(p[2],p[0],p[1])
    elif len(p) == 2:
        return '{}:{}'.format(p[0],p[1]) 
    # return '{}:{}@{}:{}'.format(p[2],p[3],p[0],p[1])


def print_break(text):
    print("**************************************")
    print("****  {}".format(text))
    print("**************************************")

def line_separator(text):
    return "\n**************************************\n****  {}\n**************************************\n".format(text)

def print_results():
    global warnings_key, success_key, errors_key
    now = datetime.datetime.now()
    # filename = '%s/%s/%s %s:%s:%s.%s'%(now.year,now.month,now.day,now.hour,now.minute,now.second,now.microsecond)
    output_file = "{}/{}/{}".format(os.getcwd(), output_directory, now.strftime("%Y-%m-%dT%H:%M:%S:{}.dat")).format(now.microsecond)
    with open(output_file, 'w') as f:
        f.write(line_separator('RESULTS'))
        for site, responses in results.iteritems():
            f.write(line_separator(site))
            if responses[success_key] != []:
                f.write(line_separator(success_key))
                for success in responses[success_key]:
                    f.write("{}\n".format(success))
            if responses[warnings_key] != []:
                f.write(line_separator(warnings_key))
                for warning in responses[warnings_key]:
                    f.write("{}\n".format(warning))
            if responses[errors_key] != []:
                f.write(line_separator(errors_key))
                for error in responses[errors_key]:
                    f.write("{}\n".format(error))
            

def increment_active():
    global active
    active += 1


def decrement_active():
    global active
    active -= 1
    if active <= 0:
        exit_tester(finished=True)


def add_response(response_type, site, output):
    if site not in results:
        results[site] = {
            'successes': [],
            'warnings': [],
            'errors': []
            }
    results[site][response_type].append(output)


def get_history(final_url, history):
    if len(history) > 0:
        return("{} -> {}".format(history[0].url, final_url))
    return final_url


def sort(proxy, site, ):
    global warnings_key, success_key, errors_key
    proxies = {
        'http': 'http://' + proxy
        # 'https': 'http://' + proxy
    }
    s.proxies.update(proxies)
    start = millis()

    try:
        response = s.get(site)
        if response.status_code == 200:
            # print response.history
            url = get_history(response.url, response.history)
            output = '[{}ms] {} ({}) -- OK ({})'.format(millis()-start, proxy, url, response.status_code)
            print '{}:{}'.format(url, response.status_code)
            add_response(success_key, site, output)

        elif response.status_code != 200:
            output = '[{}ms] {} ({}) -- Status ({}:{})'.format(millis()-start, proxy, site, response.status_code, response.reason)
            print '{}:{}'.format(site, response.reason)
            add_response(warnings_key, site, output)

    except Exception as e:
        print '{}:{} -- Error'.format(site, proxy)
        output = '[{}ms] {} {} Got an error:\n{}' .format(millis()-start, proxy, site, e)
        add_response(errors_key, site, output)
    
    decrement_active()



def execute_app():
    global active
    if proxies == []:
        print ('0 Proxies loaded -- exiting')
        exit_tester(finished=True)

    if sites == []:
        print ("0 Sites loaded -- exiting")
        exit_tester(finished=True)

    
    threads = []
    for site in sites:
        # results_init(site)
        for proxy in proxies:
            p = threading.Thread(target=sort, args=(proxy,site))
            threads.append(p)
            p.start()
            increment_active()


### setup stuff ###

pp = pprint.PrettyPrinter(indent=4)
timer = threading.Timer(timeout, exit_tester)
timer.start()

proxies = []

with open(proxy_list_file) as f:
    lines = f.readlines()
    for line in lines:
        p = line.strip()
        if convert_proxy_data:
            p = convert_proxy_link(p)
        proxies.append(p)


sites = []

with open(site_list_file) as f:
    for site in f.readlines():
        sites.append(site.strip())


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.28 Safari/537.36'}
s = requests.session()
s.headers.update(headers)
s.trust_env=False


if len(proxies) > 1:
    print '[%s] We currently have %s Proxies Loaded' % (getCurrentTime(),len(proxies))

elif len(proxies) == 1:
    print '[%s] We currently have %s Proxy Loaded' % (getCurrentTime(),len(proxies))

active = 0

results = {}

success_key = 'successes'
warnings_key = 'warnings'
errors_key = 'errors'

## data format:
# results = {
#     {'site': {
        # 'successes': [
        #     'output1'
        # ],
        # 'warnings': [
        #     'output1'
        # ],
        # 'errors': [
        #     'output1'
        # ]                
        # }
#     }
# }



def main():
    try:
        execute_app()
    finally:
        pass

if __name__=='__main__':
    main()