# OpenClash / Mihomo Codex Network Fix - 2026-06-24

## Summary

Codex on the local server was intermittently failing with TLS/stream errors when traffic went through the iStoreOS OpenClash side router:

```text
stream disconnected before completion: Connection reset by peer (os error 104)
stream disconnected before completion: tls handshake eof
OpenSSL SSL_connect: SSL_ERROR_SYSCALL
```

Final stable path after investigation:

```text
local server 192.168.31.53
-> default gateway 192.168.31.2
-> iStoreOS OpenClash
-> OpenAI policy group SG
-> SG-02 node
-> chatgpt.com / Codex backend
```

The temporary local-server Mihomo path was used to isolate the problem, but it is now stopped. The side-router OpenClash path is the active path.

```text
server mihomo.service: inactive
server local proxy ports 127.0.0.1:7890 / 9090: not listening
```

Expected raw curl result for the Codex backend endpoint is HTTP `405`; this is considered success for connectivity tests because TLS completed and the request reached the backend.

## Symptom Timeline

1. Local Mac using Clash Verge could access Codex normally.
2. The local server using the side router path intermittently failed with `connection reset`, `tls handshake eof`, or `SSL_ERROR_SYSCALL`.
3. iStoreOS OpenClash logs showed node dial timeouts to `147.90.41.x` for the subscription node entry domains.
4. Directly deploying Mihomo on the local server and rewriting the node `server:` fields made the same nodes stable.
5. Applying the same rewrite persistently inside OpenClash fixed the side-router path.
6. After switching the server gateway back to `192.168.31.2`, transparent side-router tests succeeded.

## Root Cause

Mac Clash Verge had a working profile that included host alias rewrites:

```yaml
hosts:
  cfe48a32-e278-11f01.334837632.xyz: ec9773ec-6946-11f11.334837632.xyz
  cfe48a32-e278-11f02.334837632.xyz: ec9773ec-6946-11f12.334837632.xyz
  cfe48a32-e278-11f03.334837632.xyz: ec9773ec-6946-11f13.334837632.xyz
```

The server and iStoreOS OpenClash configs originally used the `cfe48a32-*` node entry names directly. Those resolved to `147.90.41.x`, whose proxy ports frequently timed out.

The verified working target names resolve differently and are reachable:

```text
ec9773ec-6946-11f12.334837632.xyz:14947 OK
```

For the local server Mihomo, `hosts:` domain-to-domain mapping was not enough for these `anytls` nodes, so the node `server:` fields were rewritten directly from `cfe48a32-*` to `ec9773ec-*`.

Important distinction:

```text
DNS mode Fake-IP vs Redir-Host was not the primary root cause.
The primary root cause was that the side-router OpenClash config missed the same node-entry alias rewrite that Mac Clash Verge had.
```

## Local Server Changes

Temporary diagnostic path: installed user-level Mihomo:

```text
/home/justin/.local/bin/mihomo
version: v1.19.27
config: /home/justin/.config/mihomo/config.yaml
proxy: 127.0.0.1:7890
api/dashboard: 0.0.0.0:9090
dashboard ui: http://192.168.31.53:9090/ui/
```

Created user service:

```bash
systemctl --user status mihomo.service
systemctl --user restart mihomo.service
```

Temporary Codex environment used only for local-Mihomo testing:

```bash
export HTTPS_PROXY=http://127.0.0.1:7890
export HTTP_PROXY=http://127.0.0.1:7890
export ALL_PROXY=http://127.0.0.1:7890
export NO_PROXY=localhost,127.0.0.1,::1
```

This proved that the subscription nodes themselves were usable when their `server:` fields were rewritten to the working `ec9773ec-*` targets.

The final active setup does not use local-server Mihomo:

```bash
systemctl --user stop mihomo.service
systemctl --user is-active mihomo.service
```

Expected final state:

```text
inactive
```

If the side-router path breaks again, local-server Mihomo can be restarted as a fallback:

```bash
systemctl --user start mihomo.service
```

Temporary route used during local-Mihomo isolation testing:

```bash
sudo nmcli connection modify r2s-proxy \
  ipv4.gateway 192.168.31.1 \
  ipv4.dns "192.168.31.1,223.5.5.5" \
  ipv4.ignore-auto-dns yes

sudo nmcli connection up r2s-proxy
```

Final route after returning to the side-router path:

```text
default via 192.168.31.2 dev enp107s0 metric 50
DNS on enp107s0: 192.168.31.2 223.5.5.5
```

## iStoreOS OpenClash Changes

Added a persistent custom overwrite block to:

```text
/etc/openclash/custom/openclash_custom_overwrite.sh
```

Purpose:

```text
cfe48a32-e278-11f01.334837632.xyz -> ec9773ec-6946-11f11.334837632.xyz
cfe48a32-e278-11f02.334837632.xyz -> ec9773ec-6946-11f12.334837632.xyz
cfe48a32-e278-11f03.334837632.xyz -> ec9773ec-6946-11f13.334837632.xyz
```

The custom overwrite rewrites proxy `server` entries after OpenClash generates its runtime config. It logged:

```text
Codex Server Alias Rewrite: 30 proxy server entries rewritten
```

Backups were created on iStoreOS before editing:

```text
/etc/openclash/custom/openclash_custom_overwrite.sh.bak.20260624172450
/etc/openclash/v2.yaml.bak.server-rewrite.20260624172450
```

OpenAI group was set to `SG` after restart.

## Verification

Local server Mihomo after rewrite:

```text
Codex backend URL 20/20 successful
TLS connect time around 0.10s - 0.12s
curl result: code=405, err=
```

The `405` is expected for raw curl against the Codex backend endpoint; the important part is that TLS succeeds and there is no reset/eof.

iStoreOS OpenClash after persistent rewrite and restart:

```text
SG delay: 467ms
US delay: 966ms
OpenAI delay: 234ms
OpenAI now: SG
OpenAI alive: true
```

## Useful Commands

Check local server Mihomo:

```bash
ssh codex-linux 'systemctl --user status mihomo.service --no-pager'
ssh codex-linux 'ss -lntp | grep -E "127\\.0\\.0\\.1:7890|:9090"'
```

Check server proxy:

```bash
ssh codex-linux '
HTTPS_PROXY=http://127.0.0.1:7890 \
HTTP_PROXY=http://127.0.0.1:7890 \
ALL_PROXY=http://127.0.0.1:7890 \
NO_PROXY=localhost,127.0.0.1,::1 \
curl -sS -o /dev/null -w "code=%{http_code} remote=%{remote_ip} tls=%{time_appconnect} err=%{errormsg}\n" \
https://chatgpt.com/backend-api/codex/responses
'
```

Check iStoreOS rewrite:

```bash
ssh root@192.168.31.2 '
grep -n "Codex Server Alias Rewrite" /tmp/openclash.log | tail
grep -nE "server: (cfe48a32|ec9773ec)" /etc/openclash/v2.yaml | head
'
```

Check OpenClash OpenAI group:

```bash
AUTH=$(ssh root@192.168.31.2 "awk '/^secret:/{print \\$2; exit}' /etc/openclash/v2.yaml")
curl -H "Authorization: Bearer $AUTH" \
  "http://192.168.31.2:9090/proxies/OpenAI/delay?timeout=8000&url=https%3A%2F%2Fchatgpt.com"
```

## Troubleshooting Runbook

Use this sequence if Codex again reports `stream disconnected`, `connection reset`, `tls handshake eof`, or `SSL_ERROR_SYSCALL`.

### 1. Confirm Which Path The Server Is Using

```bash
ssh codex-linux '
ip route get 1.1.1.1
ip route
resolvectl dns 2>/dev/null || cat /etc/resolv.conf
'
```

Expected side-router path:

```text
1.1.1.1 via 192.168.31.2 dev enp107s0
DNS includes 192.168.31.2
```

If it shows `192.168.31.1`, the server is bypassing the side router. That is useful as a control test, but it is not testing OpenClash transparent proxying.

### 2. Confirm Server Local Mihomo Is Not Accidentally Being Used

```bash
ssh codex-linux '
systemctl --user is-active mihomo.service || true
ss -lntp 2>/dev/null | grep -E "127\\.0\\.0\\.1:7890|:9090" || true
env | grep -Ei "https?_proxy|all_proxy|no_proxy" || true
'
```

Expected side-router-only state:

```text
mihomo.service: inactive
no 127.0.0.1:7890 listener
no HTTPS_PROXY / HTTP_PROXY / ALL_PROXY required for Codex
```

If local Mihomo is active and the app has proxy env vars, the test may be using local Mihomo instead of the side router.

### 3. Test The Codex Endpoint From The Server Without Proxy Env Vars

```bash
ssh codex-linux '
env -u HTTPS_PROXY -u HTTP_PROXY -u ALL_PROXY -u https_proxy -u http_proxy -u all_proxy \
curl -sS --connect-timeout 8 --max-time 25 -o /dev/null \
  -w "code=%{http_code} remote=%{remote_ip} tls=%{time_appconnect} total=%{time_total} err=%{errormsg}\n" \
  https://chatgpt.com/backend-api/codex/responses
'
```

Expected good result:

```text
code=405
remote=198.18.x.x
err=
```

Interpretation:

```text
405: expected success for this raw endpoint test
198.18.x.x: OpenClash Fake-IP/transparent proxy path is being used
tls > 0 and err empty: TLS completed
total around 0.2s - 0.8s: normal
total around 20s but code=405: slow response, but not a reset/eof failure
code=000 with TLS EOF/reset: real connectivity failure
```

### 4. Verify OpenClash Is Matching chatgpt.com To OpenAI

```bash
ssh root@192.168.31.2 '
grep "192.168.31.53" /tmp/openclash.log 2>/dev/null | grep "chatgpt.com" | tail -20
'
```

Expected:

```text
192.168.31.53 --> chatgpt.com:443
match DomainSuffix(chatgpt.com)
using OpenAI[SG-02]
```

If traffic is matching `DIRECT`, `Final`, or the wrong policy group, check OpenClash rules and the OpenAI strategy group selection.

### 5. Check Whether The Node Alias Rewrite Is Still Applied

```bash
ssh root@192.168.31.2 '
grep "Codex Server Alias Rewrite" /tmp/openclash.log 2>/dev/null | tail
grep -nE "server: (cfe48a32|ec9773ec)" /etc/openclash/v2.yaml | head -20
'
```

Expected:

```text
Codex Server Alias Rewrite: 30 proxy server entries rewritten
server: ec9773ec-...
```

Warning sign:

```text
server: cfe48a32-...
```

If `cfe48a32-*` appears in active proxy entries, OpenClash may have regenerated the config without applying the custom overwrite. Check:

```bash
ssh root@192.168.31.2 '
sed -n "/Codex Server Alias Rewrite/,/RUBY/p" /etc/openclash/custom/openclash_custom_overwrite.sh
'
```

Then restart OpenClash:

```bash
ssh root@192.168.31.2 '/etc/init.d/openclash restart'
```

### 6. Check OpenAI Policy Group Health

```bash
AUTH=$(ssh root@192.168.31.2 "awk '/^secret:/{print \\$2; exit}' /etc/openclash/v2.yaml")
curl -H "Authorization: Bearer $AUTH" \
  "http://192.168.31.2:9090/proxies/OpenAI/delay?timeout=10000&url=https%3A%2F%2Fchatgpt.com"
```

Expected:

```json
{"delay":200}
```

The exact delay varies. Failure here means OpenClash itself cannot reach `chatgpt.com` through the selected OpenAI strategy group.

### 7. Compare Against Local Mihomo As A Control

Only use this as a fallback/control path:

```bash
ssh codex-linux '
systemctl --user start mihomo.service
HTTPS_PROXY=http://127.0.0.1:7890 \
HTTP_PROXY=http://127.0.0.1:7890 \
ALL_PROXY=http://127.0.0.1:7890 \
NO_PROXY=localhost,127.0.0.1,::1 \
curl -sS --connect-timeout 8 --max-time 25 -o /dev/null \
  -w "code=%{http_code} remote=%{remote_ip} tls=%{time_appconnect} total=%{time_total} err=%{errormsg}\n" \
  https://chatgpt.com/backend-api/codex/responses
'
```

If local Mihomo works but side-router OpenClash fails, compare:

```text
node server field rewrite
OpenAI policy group selection
DNS/Fake-IP behavior
OpenClash logs for 147.90.41.x timeouts
```

After using it as a control, stop it again if the target architecture is side-router-only:

```bash
ssh codex-linux 'systemctl --user stop mihomo.service'
```

## Decision Tree

```text
Codex fails
|
|-- Server route is not 192.168.31.2?
|   `-- You are not testing the side router. Fix or note the route first.
|
|-- curl without proxy env returns code=405 and remote=198.18.x.x?
|   `-- Side-router path is basically working. Slow 20s responses are upstream/node latency, not reset/eof.
|
|-- curl returns code=000 with TLS EOF/reset?
|   |
|   |-- OpenClash logs show 147.90.41.x timeout?
|   |   `-- Alias rewrite failed or subscription regenerated active config. Re-check custom overwrite.
|   |
|   |-- OpenClash logs show wrong policy group?
|   |   `-- Fix OpenAI strategy group/rules.
|   |
|   `-- OpenClash OpenAI delay test fails?
|       `-- Selected node/group is unhealthy. Switch SG/US node and retest.
|
`-- Local Mihomo works but side router fails?
    `-- Compare node server fields and OpenClash generated runtime config.
```

## Final Resolution

The final solution is:

```text
1. Keep the server using side-router gateway 192.168.31.2.
2. Keep OpenClash OpenAI policy group on SG, currently SG-02.
3. Keep the OpenClash custom overwrite that rewrites cfe48a32-* node server fields to ec9773ec-*.
4. Keep server local Mihomo stopped unless it is needed as a diagnostic fallback.
5. Treat HTTP 405 from the Codex backend curl test as success.
6. Treat occasional post-TLS 20s slow responses as latency symptoms, not the original reset/eof failure.
```

## 2026-06-24 Side Router Stability Retest

At 2026-06-24 17:39-17:42 CST, the local server was checked before testing. It was not actually using the side router as the active default gateway:

```text
default via 192.168.31.1 dev enp107s0 metric 50
default via 192.168.31.2 dev enp107s0 proto static metric 100
```

So the transparent side-router path from the server could not be verified without changing the server route with sudo. The server does not currently allow passwordless sudo for Codex.

OpenClash itself was verified on iStoreOS:

```text
OpenAI alive: true
OpenAI now: SG
chatgpt.com matched OpenAI[SG-02]
runtime proxy server entries use ec9773ec-* after rewrite
```

OpenClash core delay test to the OpenAI strategy group:

```text
50/50 successful
delay range observed: about 197ms - 585ms
```

Router-local real curl test to the Codex endpoint:

```text
Test 1, high-frequency 50 requests: 49/50 successful
Only failure: HTTP response timeout after TLS was established, not TLS EOF/reset

Test 2, 30 requests with 1s interval: 30/30 successful
One slow request returned 405 after about 20.36s total time
Typical TLS appconnect: about 0.39s - 0.55s
Typical total time: about 0.53s - 0.85s
```

Interpretation: after the alias rewrite, OpenClash no longer shows the previous `147.90.41.x` node-dial timeouts for `chatgpt.com`. The remaining observed instability is rare post-TLS response delay/timeout under repeated requests, not the earlier handshake EOF/reset pattern.

## 2026-06-24 Server Switched Back To Side Router

After switching the local server back to the side router, routing and DNS were:

```text
default via 192.168.31.2 dev enp107s0 metric 50
default via 192.168.31.2 dev enp107s0 proto static metric 100
DNS on enp107s0: 192.168.31.2 223.5.5.5
```

Transparent server-side test with all proxy environment variables removed:

```text
Endpoint: https://chatgpt.com/backend-api/codex/responses
Result: 50/50 successful
Remote IP reported by curl: 198.18.0.5
Typical TLS appconnect: about 0.10s - 0.13s
Typical total time: about 0.22s - 0.46s
Slow responses over 3s: 1
Slowest observed successful response: about 20.02s
```

OpenClash logs confirmed the server traffic path:

```text
192.168.31.53 --> chatgpt.com:443
match DomainSuffix(chatgpt.com)
using OpenAI[SG-02]
```

The local server Mihomo service was then stopped temporarily:

```text
systemctl --user stop mihomo.service
mihomo.service status: inactive
127.0.0.1:7890 / 9090 no longer listening
```

Post-stop smoke test:

```text
12/12 successful
Remote IP reported by curl: 198.18.0.5
One slow successful response: about 19.63s
No TLS EOF/reset observed
```
