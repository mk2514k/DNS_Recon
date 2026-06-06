# DNS Recon Tool

A Python-based DNS reconnaissance tool that combines **subdomain brute-forcing** with an **AXFR zone transfer attempt**. Two techniques, one script — brute-force finds subdomains by guessing, zone transfer asks the DNS server to just hand everything over.

---

## What This Tool Does

Most domains have more than just a `www` — there's often `mail`, `vpn`, `staging`, `internal` and more sitting underneath. This tool tries to find them two ways:

- **Brute-force:** Takes a wordlist of common subdomain names, builds each one (e.g. `mail.example.com`), and fires a DNS query at it. If it resolves to an IP, it's real.
- **AXFR zone transfer:** Asks the domain's nameserver for a full copy of its DNS records. This is a legitimate feature meant for DNS server syncing — but if the server is misconfigured, it hands over every single record it holds. One request, full map of the domain.

Threading means both DNS lookups run concurrently — up to 50 at a time — rather than waiting on each one before starting the next.

---

## Concepts Demonstrated

- DNS resolution and record types (A, NS)
- AXFR zone transfers — what they are, why misconfigurations matter
- Wordlist-based enumeration
- Python threading with `ThreadPoolExecutor`
- CLI argument parsing with `argparse`
- Exception handling for network timeouts and DNS errors

---

## Requirements

```bash
pip install dnspython
```

You'll also need a subdomain wordlist. The one used here is `subdomains-top1million-5000.txt` from [SecLists](https://github.com/danielmiessler/SecLists/tree/master/Discovery/DNS) — too large to include in the repo, download separately.

---

## Usage

```bash
# AXFR attempt + brute-force
python Subdomain_finder.py zonetransfer.me -w Subdomains-top1million-5000.txt

# More threads (faster)
python Subdomain_finder.py zonetransfer.me -w Subdomains-top1million-5000.txt -t 50

# Brute-force only, skip AXFR
python Subdomain_finder.py zonetransfer.me -w Subdomains-top1million-5000.txt --no-axfr

# Save output to file
python Subdomain_finder.py zonetransfer.me -w Subdomains-top1million-5000.txt > results.txt
```

`zonetransfer.me` is a domain intentionally set up to allow zone transfers — it's the standard target for testing this technique safely and legally.

---

## Results

The AXFR against `zonetransfer.me` returned a full zone dump — 35 records including subdomains like `vpn`, `staging`, `internal`, `cmdexec`, and `owa`. On a real misconfigured server, this would be a significant finding.

The brute-force returned 0 hits against `zonetransfer.me` — the wordlist guesses didn't match the actual subdomains. This is expected behaviour and demonstrates why zone transfers are so much more powerful than brute-forcing when available.

---

## Files

| File | Description |
|------|-------------|
| `Subdomain_finder.py` | Main script |
| `bruteforce_only.txt` | Brute-force only run — no AXFR, 20 threads, 8 subdomains found |
| `more_threads.txt` | Full run with 50 threads — AXFR + brute-force |
| `bruteforce_axfr.txt` | Standard run output |
