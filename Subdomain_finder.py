#dns library install- pip install dnspython (done)

#queries + results
import dns.resolver 

#AXFR attempt
import dns.zone
import dns.query 

#passes target domain in from cmd line
import argparse 

#running multi DNS lookups
from concurrent.futures import ThreadPoolExecutor, as_completed

import dns.exception
import sys


#subdomain funct
def check_subdomain(domain, word) :
    subdomain = f"{word}.{domain}"
    try:
        answers = dns.resolver.resolve(subdomain, "A")
        ips = [str(r) for r in answers]
        return (subdomain, ips)
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout, dns.exception.DNSException):
        return None
    

#AXFR zone transfer funct
def attempt_zone_transfer(domain):
    print(f"\n[*] Attempting AXFR zone transfer for {domain}...")
    try: #looking up ns records
        ns_records = dns.resolver.resolve(domain, "NS")
        nameservers = [str(ns) for ns in ns_records]
    except Exception as e:
        print(f"[-] Could not retrieve NS records: {e}")
        return

    for ns in nameservers: #resolves ns ip & send AXFR request
        ns = ns.rstrip(".")
        print(f"[*] Trying nameserver: {ns}")
        try:
            ns_ip = str(dns.resolver.resolve(ns, "A")[0])
            zone = dns.zone.from_xfr(dns.query.xfr(ns_ip, domain, timeout=5))
            print(f"[!] Zone transfer SUCCESS on {ns} — records below:")
            for name in zone.nodes.keys(): #printed hits
                print(f"    {name}.{domain}")
            return
        except dns.exception.FormError: #if server config correctly
            print(f"[-] {ns} refused zone transfer (expected — server is configured correctly)")
        except Exception as e:
            print(f"[-] {ns} failed: {e}")


#brute-force scan
def run_subdomain_scan(domain, wordlist_path, threads=20):
    print(f"\n[*] Loading wordlist: {wordlist_path}") 
    try:
        with open(wordlist_path, "r") as f:
            words = [line.strip() for line in f if line.strip()] #read wl file in to word list
    except FileNotFoundError: #if inccorect file attached
        print(f"[-] Wordlist not found: {wordlist_path}")
        sys.exit(1)

    print(f"[*] Scanning {domain} with {len(words)} words using {threads} threads...\n")
    found = []

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(check_subdomain, domain, word): word for word in words} #create threadpool + submit words
        for future in as_completed(futures): #process result as completed
            result = future.result()
            if result:
                subdomain, ips = result
                print(f"[+] Found: {subdomain} -> {', '.join(ips)}") #hits added to found list
                found.append((subdomain, ips))

    return found


#parsing + main entry point
def main(): #build CLI interface
    parser = argparse.ArgumentParser(description="Subdomain finder with AXFR zone transfer attempt")
    parser.add_argument("domain", help="Target domain (e.g. example.com)")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to subdomain wordlist")
    parser.add_argument("-t", "--threads", type=int, default=20, help="Number of threads (default: 20)")
    parser.add_argument("--no-axfr", action="store_true", help="Skip zone transfer attempt")
    args = parser.parse_args()

    domain = args.domain.strip().lower()

    if not args.no_axfr:
        attempt_zone_transfer(domain)

    results = run_subdomain_scan(domain, args.wordlist, args.threads)

    print(f"\n[*] Scan complete. {len(results)} subdomain(s) found.")
    if results:
        print("\n--- Summary ---")
        for subdomain, ips in sorted(results):
            print(f"  {subdomain} -> {', '.join(ips)}")

if __name__ == "__main__": #execute file from terminal
    main()

#Run
    # Run brute-force only
        #python Subdomain_finder.py zonetransfer.me -w subdomains-top1million-5000.txt > axfr_only.txt
    
    # Run with AXFR + brute-force
        #python Subdomain_finder.py zonetransfer.me -w subdomains-top1million-5000.txt > bruteforce_axfr.txt

    # Run with more threads
        #python Subdomain_finder.py zonetransfer.me -w subdomains-top1million-5000.txt -t 50 > more_threads.txt

