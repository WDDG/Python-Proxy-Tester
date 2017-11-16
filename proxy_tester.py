# Proxy Tester.py
# developer: @bopped /// twitter : @backdoorcook
import requests, json, time, threading, sys, os, pprint, datetime, re, fnmatch

### config stuff ###

# proxy format for requests is user:pass@site:port
# some sites output this as site:port:user:pass
# if the proxies.dat is formatted that way - set the following to true
proxy_format_url =  'user:pass@site:port'
proxy_format_list = 'site:port:user:pass'
proxy_data_format = proxy_format_list
proxy_output_format = proxy_format_list
convert_proxy_data = (proxy_data_format != proxy_format_url)

proxy_list_file = 'proxies.dat'
site_list_file = 'sites.dat'
output_directory = 'output' # no trailing /
timeout = 120 # in seconds

export_working_proxies = True
archive_old_exports = True
working_proxies_file = '_working_proxies.dat'


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

def cmp_results(a,b):
    lhs = extract_ms(a)
    rhs = extract_ms(b)
    if lhs > rhs:
        return 1
    elif lhs == rhs:
        return 0
    else:
        return -1


def extract_ms(log):
    return int(re.search(r'\[(.+?)ms', log).group(1))


def extract_proxy(log):
    return log.split(' ')[1]


def format_proxy(proxy_url):
    global proxy_output_format
    proxy = get_proxy_from_url(proxy_url)

    if proxy_output_format == proxy_format_url:
        if proxy['pass'] != '' and proxy['user'] != '':
            return "{}:{}@{}:{}".format(proxy['user'],proxy['pass'],proxy['url'],proxy['port'])
        if proxy['user'] != '':
            return "{}@{}:{}".format(proxy['user'],proxy['url'],proxy['port'])
        return "{}:{}".format(proxy['url'],proxy['port'])
    elif proxy_output_format == proxy_format_list:
        parts = [p for p in proxy['url'],proxy['port'],proxy['user'],proxy['pass'] if p != '']
        return ':'.join(parts)


def get_proxy_from_url(url):
    proxy = {
        'user': '',
        'pass': '',
        'url': '',
        'port': ''
    }

    if '@' in url:
        parts = url.split('@')
        lhs = parts[0]
        if ':' in lhs:
            credentials = lhs.split(':')
            proxy['user'] = credentials[0]
            proxy['pass'] = credentials[1]
        else:
            proxy['user'] = lhs
        rhs = parts[1]
    else:
        rhs = url

    path = rhs.split(':')
    proxy['url'] = path[0]
    proxy['port'] = path[1]

    return proxy

def organize_archive():
    ## create /archive folder if we don't have it yet
    archive_path = "{}/archive/".format(os.getcwd())
    if not os.path.exists(archive_path):
        os.makedirs(archive_path)

    now = datetime.datetime.now()
    iso_timestamp = '{}'.format(now.strftime("%Y-%m-%dT%H:%M:%S:{}")).format(now.microsecond)
    # output_file = "{}/{}/{}.log".format(os.getcwd(), output_directory, iso_timestamp)

    old_file = "{}/{}/{}".format(os.getcwd(), output_directory, working_proxies_file)
    if os.path.exists(old_file):
        new_file = "{}{}.{}".format(archive_path, working_proxies_file, iso_timestamp)
        os.rename(old_file, new_file)

    ## move the old .dat files to /archive
    old_log_files = fnmatch.filter(os.listdir("{}/{}".format(os.getcwd(),output_directory)), '*.log')
    # print old_log_files
    for old_file_name in old_log_files:
        old_file = "{}/{}/{}".format(os.getcwd(), output_directory, old_file_name)
        new_file = "{}{}".format(archive_path, old_file_name)
        os.rename(old_file, new_file)

def print_results():
    global warnings_key, success_key, errors_key

    now = datetime.datetime.now()
    iso_timestamp = '{}'.format(now.strftime("%Y-%m-%dT%H:%M:%S:{}")).format(now.microsecond)
    output_file = "{}/{}/{}.log".format(os.getcwd(), output_directory, iso_timestamp)

    if export_working_proxies and archive_old_exports:
        organize_archive()

    with open(output_file, 'w') as f:
        f.write(line_separator('RESULTS'))

        for site, responses in results.iteritems():
            f.write(line_separator(site))
            ## print successes ##
            if responses[success_key] != []:
                f.write(line_separator(success_key))
                responses[success_key].sort(cmp_results)
                for success in responses[success_key]:
                    f.write("{}\n".format(success))

                if export_working_proxies:
                    output_proxies_file = "{}/{}/{}".format(os.getcwd(), output_directory, working_proxies_file)
                    with open(output_proxies_file, 'a') as fp:
                        fp.write(line_separator(site))
                        for success in responses[success_key]:
                            fp.write("{}\n".format(format_proxy(extract_proxy(success))))

            ## print warnings ##
            if responses[warnings_key] != []:
                f.write(line_separator(warnings_key))
                responses[warnings_key].sort(cmp_results)
                for warning in responses[warnings_key]:
                    f.write("{}\n".format(warning))
            ## print errors ##
            if responses[errors_key] != []:
                f.write(line_separator(errors_key))
                responses[errors_key].sort(cmp_results)
                for error in responses[errors_key]:
                    f.write("{}\n".format(error))

        ## print timeouts ##
        if len(request_set) > 0:
            f.write(line_separator("timeouts"))
            for attempt in request_set:
                f.write("{}\n".format(attempt))
    
    


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
        request_id = "{}:{}".format(proxy,site) 
        request_set.add(request_id)
        response = s.get(site)
        if response.status_code == 200:
            # print response.history
            url = get_history(response.url, response.history)
            output = '[{}ms] {} ({}) -- OK ({})'.format(millis()-start, proxy, url, response.status_code)
            print '{}:{}'.format(url, response.status_code)
            add_response(success_key, site, output)
            request_set.discard(request_id)

        elif response.status_code != 200:
            output = '[{}ms] {} ({}) -- Status ({}:{})'.format(millis()-start, proxy, site, response.status_code, response.reason)
            print '{}:{}'.format(site, response.reason)
            add_response(warnings_key, site, output)
            request_set.discard(request_id)

    except Exception as e:
        print '{}:{} -- Error'.format(site, proxy)
        output = '[{}ms] {} {} Got an error:\n{}' .format(millis()-start, proxy, site, e)
        add_response(errors_key, site, output)
        request_set.discard(request_id)
    
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
request_set = set()

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