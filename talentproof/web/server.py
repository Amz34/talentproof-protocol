"""server.py - Zero-Dependency Embedded Web Dashboard for TalentProof Protocol."""

import http.server
import json
import socketserver
import urllib.parse
from talentproof.core.attestation import generate_dev_proof, render_svg_badge
from talentproof.core.matcher import match_candidate_to_job, JobRequisition
from talentproof.core.escrow_contract import create_milestone_contract, export_contract_markdown

PORT = 8089

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>TalentProof Protocol Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body { background-color: #0d1117; color: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }
    input { background-color: #161b22 !important; border-color: #30363d !important; color: #f0f6fc !important; }
    input:focus { border-color: #58a6ff !important; outline: none; }
  </style>
</head>
<body class="p-8 antialiased">
  <div class="max-w-5xl mx-auto">
    <!-- Header: Clean, quiet chrome -->
    <div class="flex items-center justify-between pb-6 border-b border-[#21262d]">
      <div>
        <h1 class="text-2xl font-semibold text-[#f0f6fc] tracking-tight">
          TalentProof Protocol
        </h1>
        <p class="text-sm text-[#8b949e] mt-1">Bilateral developer proof attestation and recruiter milestone escrow kernel.</p>
      </div>
      <div class="text-right">
        <span class="inline-flex items-center px-2.5 py-1 rounded text-xs font-mono bg-[#161b22] text-[#8b949e] border border-[#30363d]">
          v1.0.0 (mainnet)
        </span>
      </div>
    </div>

    <!-- 2 Column Grid: Developer Proof vs Bilateral Agreement -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
      
      <!-- Developer Proof Generator -->
      <div class="bg-[#161b22] border border-[#30363d] rounded-lg p-6">
        <h2 class="text-base font-semibold text-[#f0f6fc] mb-1">Developer Attestation</h2>
        <p class="text-xs text-[#8b949e] mb-5">Analyze code entropy, test coverage, and benchmark fair USD contractor rates.</p>
        
        <div class="space-y-4">
          <div>
            <label class="block text-xs text-[#8b949e] font-medium mb-1.5">GitHub Username</label>
            <input id="gh_handle" type="text" value="Amz34" class="w-full rounded px-3 py-2 text-sm border">
          </div>
          <button onclick="generateProof()" class="w-full bg-[#238636] hover:bg-[#2ea043] text-white text-sm font-medium py-2 rounded transition">
            Generate Cryptographic Proof
          </button>
        </div>

        <div id="proof_output" class="mt-6 hidden">
          <p class="text-xs text-[#8b949e] mb-2 font-medium">Verified Proof Badge:</p>
          <div id="badge_container" class="border border-[#30363d] rounded bg-[#0d1117] p-2 flex justify-center overflow-x-auto"></div>
        </div>
      </div>

      <!-- Bilateral Contract Generator -->
      <div class="bg-[#161b22] border border-[#30363d] rounded-lg p-6">
        <h2 class="text-base font-semibold text-[#f0f6fc] mb-1">Milestone Escrow Agreement</h2>
        <p class="text-xs text-[#8b949e] mb-5">Structure deterministic deliverable milestones with automated test verification.</p>
        
        <div class="space-y-4">
          <div>
            <label class="block text-xs text-[#8b949e] font-medium mb-1.5">Client / Enterprise Organization</label>
            <input id="client_name" type="text" value="Acme Enterprise" class="w-full rounded px-3 py-2 text-sm border">
          </div>
          <div>
            <label class="block text-xs text-[#8b949e] font-medium mb-1.5">Milestone Budget (USD)</label>
            <input id="budget_usd" type="number" value="3500" class="w-full rounded px-3 py-2 text-sm border">
          </div>
          <button onclick="createContract()" class="w-full bg-[#1f6feb] hover:bg-[#388bfd] text-white text-sm font-medium py-2 rounded transition">
            Generate Milestone Agreement
          </button>
        </div>

        <div id="contract_output" class="mt-6 hidden">
          <p class="text-xs text-[#8b949e] mb-2 font-medium">Agreement Markdown Digest:</p>
          <pre id="contract_text" class="bg-[#0d1117] border border-[#30363d] p-3 rounded text-xs text-[#c9d1d9] font-mono overflow-x-auto max-h-56"></pre>
        </div>
      </div>

    </div>

    <!-- Minimal quiet footer -->
    <div class="mt-12 text-center text-xs text-[#6e7681] border-t border-[#21262d] pt-6">
      TalentProof Protocol &bull; <a href="https://github.com/Amz34/talentproof-protocol" target="_blank" class="text-[#58a6ff] hover:underline">GitHub Repository</a> &bull; Apache 2.0
    </div>
  </div>

  <script>
    async function generateProof() {
      const handle = document.getElementById('gh_handle').value.trim();
      const res = await fetch(`/api/proof?handle=${encodeURIComponent(handle)}`);
      const data = await res.json();
      document.getElementById('badge_container').innerHTML = data.svg;
      document.getElementById('proof_output').classList.remove('hidden');
    }

    async function createContract() {
      const client = document.getElementById('client_name').value.trim();
      const budget = document.getElementById('budget_usd').value.trim();
      const handle = document.getElementById('gh_handle').value.trim();
      const res = await fetch(`/api/contract?client=${encodeURIComponent(client)}&dev=${encodeURIComponent(handle)}&budget=${budget}`);
      const data = await res.json();
      document.getElementById('contract_text').innerText = data.markdown;
      document.getElementById('contract_output').classList.remove('hidden');
    }
  </script>
</body>
</html>
"""


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif parsed.path == "/api/proof":
            params = urllib.parse.parse_qs(parsed.query)
            handle = params.get("handle", ["Anonymous"])[0]
            p = generate_dev_proof(handle)
            svg = render_svg_badge(p)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"proof": p.__dict__, "svg": svg}).encode("utf-8"))
        elif parsed.path == "/api/contract":
            params = urllib.parse.parse_qs(parsed.query)
            client = params.get("client", ["Acme"])[0]
            dev = params.get("dev", ["Amz34"])[0]
            budget = int(params.get("budget", [3000])[0])
            c = create_milestone_contract(
                client_name=client,
                developer_handle=dev,
                project_scope="End-to-end digital architecture delivery and production deployment.",
                milestone_specs=[
                    {"title": "Core Architecture Delivery", "deliverables": ["Backend & APIs"], "payout_usd": budget}
                ]
            )
            md = export_contract_markdown(c)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"contract": c.__dict__, "markdown": md}, default=str).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


def start_web_server(port=PORT):
    with socketserver.TCPServer(("127.0.0.1", port), DashboardHandler) as httpd:
        print(f"[TalentProof] Dashboard running on http://127.0.0.1:{port}")
        httpd.serve_forever()


if __name__ == "__main__":
    start_web_server()
