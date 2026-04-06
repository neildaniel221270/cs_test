import ssl
import httpx
import truststore
from huggingface_hub import snapshot_download, set_client_factory

def client_factory() -> httpx.Client:
    ctx = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    return httpx.Client(
        verify=ctx,
        follow_redirects=True,
        timeout=60.0,
        trust_env=True,
    )

set_client_factory(client_factory)

snapshot_download(
    repo_id="NousResearch/Nous-Hermes-2-Mistral-7B-DPO",
    local_dir=r"models\llm\Nous-Hermes-2-Mistral-7B-DPO",
    allow_patterns=[
        "*.json",
        "*.safetensors",
        "*.model",
        "*.py",
        "README.md",
        "LICENSE*",
    ],
)