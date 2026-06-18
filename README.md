# DNS Recon Tool

**Tools:** Python 3, `dnspython`

**Environment:** Daily Driver- Fedora Linux, Niri compositer

**Part of:** Security Tooling Portfolio, built alongside CompTIA Network+ study

---

## What this is

The first time I ran an AXFR zone transfer against a deliberately misconfigured test domain and watched 35 DNS records- subdomains, internal hostnames, the lot- get dumped to my terminal from a single request, it was obvious why this is such a classic recon technique. AXFR is a legitimate DNS feature meant for syncing records between a domain's own nameservers, but if a server is misconfigured to allow it from anyone, it just hands over its entire zone file on request. This tool combines that with wordlist-based subdomain brute-forcing, so it covers both the "ask nicely and see if the server just tells you everything" approach and the "guess until something resolves" approach in one script.

---

## What it does

Most domains have far more than just `www` sitting underneath them — `mail`, `vpn`, `staging`, `internal`, and plenty more are common. This tool finds them two ways:

- **AXFR zone transfer**- asks the domain's nameserver for a full copy of its records. One request, full map of the domain, if the server's misconfigured enough to allow it.
- **Brute-force**- takes a wordlist of common subdomain names, builds each one (`mail.example.com`, `vpn.example.com`, etc.), and fires a DNS query at it. Anything that resolves is real.

Both DNS lookups run concurrently via threading, up to 50 at a time- rather than waiting on each query before starting the next.

```bash
pip install dnspython
```

You'll also need a subdomain wordlist, I used `subdomains-top1million-5000.txt` from [SecLists](https://github.com/danielmiessler/SecLists/tree/master/Discovery/DNS), too large to include directly in the repo so it needs downloading separately.

---

## How I built it

I built the AXFR attempt first since it's the simpler of the two techniques- query the domain's NS records to find its nameservers, then request a zone transfer from each one and see if any of them actually allow it. The brute-force piece came next, layered with `ThreadPoolExecutor` so dozens of subdomain guesses run at once instead of serially- at one subdomain per request with a real-world timeout, a 5,000-word list one-at-a-time would take far too long to be practical.

Testing against `zonetransfer.me` (a domain deliberately configured to allow AXFR, specifically for testing tools like this) returned a full zone dump- 35 records including subdomains like `vpn`, `staging`, `internal`, `cmdexec`, and `owa`. The brute-force pass against the same domain returned zero hits, because the wordlist guesses simply didn't match the actual subdomain names in use. That result wasn't a bug — it's exactly the point of including both techniques in one tool: zone transfer is dramatically more powerful when it's available, and brute-forcing is the fallback for when it isn't.

---

## What I took from this

The zero-hit brute-force result taught me more than a clean success would have. It's a direct demonstration of why AXFR misconfigurations are still treated as a real finding in 2026 rather than a relic from twenty years ago. A server that allows zone transfers gives up everything in one request; a server that doesn't forces an attacker into slow, incomplete guessing. That gap is exactly why this is one of the first things worth checking during external recon, and it's the kind of finding that's genuinely interesting from an offensive standpoint, not just a checkbox on a scan report.

---

## Files in this repo

| File | What it is |
|------|-----------|
| `Subdomain_finder.py` | Main script |
| `bruteforce_only.txt` | Brute-force only run — no AXFR, 20 threads, 8 subdomains found |
| `more_threads.txt` | Full run with 50 threads — AXFR + brute-force |
| `bruteforce_axfr.txt` | Standard run output |
| `subdomains-top1million-5000.txt` | Wordlist used (download from SecLists — see above) |
