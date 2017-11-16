import pprint, datetime, os, fnmatch


test_proxy_format = False
test_file_moving = True

if test_proxy_format:

    pp = pprint.PrettyPrinter(indent=4)

    proxies = ['omgit369:57OMGIT@us1.coppedproxies.com:33128',
                'omgitsu@us1.coppedproxies.com:33128',
                'us1.coppedproxies.com:33128']

    proxy_format_url =  'user:pass@site:port'
    proxy_format_list = 'site:port:user:pass'
    proxy_output_format = proxy_format_list

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

    for p in proxies:
        print format_proxy(p)

if test_file_moving:
    archive_old_outputs = True
    archive_director = 'archive' # no trailing /
    output_directory = 'output' # no trailing /
    export_working_proxies = True
    working_proxies_file = '_working_proxies.dat'

    now = datetime.datetime.now()
    iso_timestamp = '{}'.format(now.strftime("%Y-%m-%dT%H:%M:%S:{}")).format(now.microsecond)
    output_file = "{}/{}/{}.log".format(os.getcwd(), output_directory, iso_timestamp)

    if export_working_proxies and archive_old_outputs:
        ## create /archive folder if we don't have it yet
        archive_path = "{}/archive/".format(os.getcwd())
        if not os.path.exists(archive_path):
            os.makedirs(archive_path)

        ## move previous proxies.dat
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
