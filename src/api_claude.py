"""Study 5 on Claude through the Message Batches API (50% of standard price). Anthropic SDK only.

Usage:
  python src/api_claude.py dry                 # count requests and show one, no network
  python src/api_claude.py submit              # create the batch; its id is saved to results/api_claude_batch.txt
  python src/api_claude.py collect             # wait for the batch, then write results/ml_ and s3_ files

Credentials come from the environment (ANTHROPIC_API_KEY, or an `ant auth login` profile). No sampling parameters
are sent (the API rejects them); effort is set explicitly to the model's default. No refusal fallback is used, so
every reply comes from the named model; a refusal is recorded as a missing sample.
"""
import os
import sys
import time

from api_plan import RES, collect, requests

MODEL = "claude-opus-5-5"
LABEL = "claude_opus55"
EFFORT = "medium"
MAX_TOKENS = 16000
BATCH_FILE = os.path.join(RES, "api_claude_batch.txt")


def params(text):
    return {"model": MODEL, "max_tokens": MAX_TOKENS, "output_config": {"effort": EFFORT},
            "messages": [{"role": "user", "content": text}]}


def submit():
    import anthropic
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    client = anthropic.Anthropic()
    batch = client.messages.batches.create(requests=[
        Request(custom_id=cid, params=MessageCreateParamsNonStreaming(**params(text))) for cid, text in requests()])
    with open(BATCH_FILE, "w") as fh:
        fh.write(batch.id + "\n")
    print("batch", batch.id, batch.processing_status)


def gather():
    import anthropic

    client = anthropic.Anthropic()
    batch_id = open(BATCH_FILE).read().strip()
    while True:
        batch = client.messages.batches.retrieve(batch_id)
        if batch.processing_status == "ended":
            break
        print("status", batch.processing_status, "processing", batch.request_counts.processing, flush=True)
        time.sleep(60)
    replies, counts = {}, {}
    for result in client.messages.batches.results(batch_id):
        kind = result.result.type
        if kind == "succeeded" and result.result.message.stop_reason != "refusal":
            msg = result.result.message
            replies[result.custom_id] = "".join(b.text for b in msg.content if b.type == "text")
            kind = msg.stop_reason
        elif kind == "succeeded":
            kind = "refusal"
        counts[kind] = counts.get(kind, 0) + 1
    print("results:", counts)
    collect(LABEL, MODEL, replies)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "dry"
    if cmd == "submit":
        submit()
    elif cmd == "collect":
        gather()
    else:
        reqs = requests()
        print(len(reqs), "requests to", MODEL, "effort", EFFORT)
        print(params(reqs[0][1]))
