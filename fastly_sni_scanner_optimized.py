
import ssl
import socket
import asyncio
import dns.resolver
import random
import re
import aiofiles

resolver = dns.resolver.Resolver()
resolver.lifetime = resolver.timeout = 2.0

async def fetch_fastly_snis():
    print("📄 Reading Fastly SNIs from local file: fastly_source.txt")
    try:
        async with aiofiles.open("fastly_source.txt", "r") as f:
            lines = await f.readlines()
        domains = set()
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                match = re.match(r"^[a-zA-Z0-9.-]+$", line)
                if match:
                    domains.add(line)
        print(f"✅ Loaded {len(domains)} domains from file")
        return list(domains)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return []

async def resolve_ip(domain):
    try:
        return resolver.resolve(domain, 'A')[0].to_text()
    except Exception:
        return None

async def tls_ok(ip, domain):
    ctx = ssl.create_default_context()
    ctx.minimum_version = ssl.TLSVersion.TLSv1_3
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, 443, ssl=ctx, server_hostname=domain), timeout=5)
        cert = writer.get_extra_info('ssl_object').getpeercert()
        sans = [e[1] for e in cert.get("subjectAltName", [])]
        writer.close()
        await writer.wait_closed()
        return domain in sans
    except Exception:
        return False

async def test_domain(domain, working, semaphore):
    async with semaphore:
        ip = await resolve_ip(domain)
        if not ip:
            print(f"Testing {domain} → No IP found ❌")
            return
        print(f"Testing {domain} → {ip}")
        if await tls_ok(ip, domain):
            print(" ✅ WORKS")
            working.append((domain, ip))
        else:
            print(" ❌ FAIL")

async def scan(limit=50):
    domains = await fetch_fastly_snis()
    random.shuffle(domains)
    working = []
    semaphore = asyncio.Semaphore(20)
    tasks = []

    print(f"\n🔍 Scanning up to {limit} Fastly domains...\n")
    for domain in domains[:limit]:
        tasks.append(test_domain(domain, working, semaphore))

    await asyncio.gather(*tasks)

    print("\n🧾 Working SNI / IP results:")
    for d, i in working:
        print(f"{d} → {i}")

    async with aiofiles.open("fastly_sni_working.txt", "w") as f:
        for d, i in working:
            await f.write(f"{d} {i}\n")

    print(f"\n📁 Saved {len(working)} entries → fastly_sni_working.txt")
    print(f"\nProudly made with ❤️  for all Iranians 🇮🇷")
    print(f"\n❄️  https://t.me/official_subzero 💙")

if __name__ == "__main__":
    
import sys
limit = int(sys.argv[1]) if len(sys.argv) > 1 else 50
asyncio.run(scan(limit))

