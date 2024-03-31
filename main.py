import tls_client, random, sys, console, concurrent.futures, bs4, time, threading
from tls_client import exceptions as tls_exceptions
from kasada import kasada, salamoonder


channel = input("Follow Channel: ")
tokens = input("Tokens file: ")
proxies = input("Proxies file: ")
threads = int(input("Threads Count: "))
salamoonderKey = input("Salamoonder.com API Key: ")
debug = input("Want to show Solving Kasada Message? (y/n): ")
if debug not in ["y", "n"]:
    sys.exit(console.error("Invalid input"))

with open(tokens, "r") as f:
    tokens = f.readlines()
with open(proxies, "r") as f:
    proxies = f.readlines()

lock = threading.Lock()

# pjs = "https://kick.com/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/p.js"
def follow(channel, token, retry=True):
    client = tls_client.Session(
        client_identifier=f"chrome120",
        random_tls_extension_order=True,
        ja3_string=",".join(["771", "-".join([str(random.randint(50, 52392)) for _ in range(15)]), "-".join("45-16-23-65281-35-65037-51-10-43-13-17513-5-0-11-18-27".split("-")), "29-23-24,0"])
    )
    pjs = "https://kick.com" + bs4.BeautifulSoup(client.get("https://kick.com").text, "html.parser").find_all("script", {"src": lambda s: s and s.endswith("p.js")})[0]["src"]
    if debug == "y":
        with lock:
            console.info(f"Solving Kasada...")
    solveKasada = salamoonder(pjs, salamoonderKey)
    # solveKasada = kasada(pjs, f"/api/v2/channels/{channel}/follow")
    headers = {
        'Host': 'kick.com',
        'x-kpsdk-cd': solveKasada["x-kpsdk-cd"],
        'x-kpsdk-ct': solveKasada["x-kpsdk-ct"],
        'Accept': 'application/json, text/plain, */*',
        'x-xsrf-token': client.cookies["XSRF-TOKEN"].replace("%3D", "="),
        'Authorization': f'Bearer {token}',
        'Sec-Fetch-Site': 'cross-site',
        'x-app-platform': 'iOS',
        'Accept-Language': 'en-US,en;q=0.9',
        'Sec-Fetch-Mode': 'cors',
        'x-kpsdk-v': 'j-0.0.0',
        'Origin': 'https://kick.com',
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        'x-app-version': '39.1.18',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Content-Type': 'application/json',
        # 'cookie': headersCookies()
    }
    try:
        req = client.post(f'https://kick.com/api/v2/channels/{channel}/follow', headers=headers, proxy=f"http://{random.choice(proxies).strip()}", timeout_seconds=20)
        if req.status_code == 422:
            with lock:
                console.error(f"Already followed {channel} | {token}")
        elif req.status_code != 200:
            with lock:
                console.error(f"Failed to follow {channel} with token {token} | {req.status_code}")
                if retry:
                    return follow(channel, token, False)
        else:
            with lock:
                console.success(f"Followed {channel}")
    except tls_exceptions.TLSClientExeption as err:
        if retry:
            console.error("Dead proxy, retrying...")
            return follow(channel, token, False)
        sys.exit(console.error("Probably dead proxy" + str(err)))


with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
    futures = [executor.submit(follow, channel, token.strip().split("|")[-1]) for token in tokens]
    for future in concurrent.futures.as_completed(futures):
        try:
            result = future.result()
        except Exception as err:
            print(str(err))