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
    body { background-color: #0b0f19; color: #e2e8f0; font-family: ui-sans-serif, system-ui, sans-serif; }
  </style>
</head>
<body class="p-8">
  <div class="max-w-5xl mx-auto">
    <div class="flex items-center justify-between pb-6 border-b border-gray-800">
      <div>
        <h1 class="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
          <span class="p-2 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded-lg text-xl">🛡️</span>
          TalentProof Protocol
        </h1>
        <p class="text-gray-400 mt-1">Sovereign 2-Way Developer Proof &amp; Recruiter Milestone Escrow Kernel</p>
      </div>
      <div class="text-right">
        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-emerald-950 text-emerald-400 border border-emerald-800">
          ● Mainnet Ready (v1.0.0)
        </span>
      </div>
    </div>

    <!-- 2 Column Grid: Dev Verification vs Enterprise Contract -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8">
      
      <!-- Developer Proof Generator -->
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-6 shadow-xl">
        <h2 class="text-xl font-bold text-emerald-400 mb-2">1. Developer Proof Attestation</h2>
        <p class="text-sm text-gray-400 mb-4">Benchmark GitHub code entropy, test coverage, and fair USD market value.</p>
        
        <div class="space-y-4">
          <div>
            <label class="block text-xs uppercase text-gray-400 font-semibold mb-1">GitHub Username</label>
            <input id="gh_handle" type="text" value="Amz34" class="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-white">
          </div>
          <button onclick="generateProof()" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-2.5 rounded-lg transition">
            Generate Cryptographic Proof Card
          </button>
        </div>

        <div id="proof_output" class="mt-6 hidden">
          <h3 class="text-xs uppercase tracking-wider text-gray-400 mb-2">Verified Proof Badge Preview:</h3>
          <div id="badge_container" class="border border-gray-800 rounded-lg overflow-hidden flex justify-center bg-black/40 p-2"></div>
        </div>
      </div>

      <!-- Enterprise Contract & Matcher -->
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-6 shadow-xl">
        <h2 class="text-xl font-bold text-sky-400 mb-2">2. Bilateral Escrow Generator</h2>
        <p class="text-sm text-gray-400 mb-4">Structure milestone contracts with automated acceptance tests &amp; USD payouts.</p>
        
        <div class="space-y-4">
          <div>
            <label class="block text-xs uppercase text-gray-400 font-semibold mb-1">Client / Company Name</label>
            <input id="client_name" type="text" value="Acme Enterprise" class="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-white">
          </div>
          <div>
            <label class="block text-xs uppercase text-gray-400 font-semibold mb-1">Milestone Budget (USD)</label>
            <input id="budget_usd" type="number" value="3500" class="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-white">
          </div>
          <button onclick="createContract()" class="w-full bg-sky-600 hover:bg-sky-500 text-white font-semibold py-2.5 rounded-lg transition">
            Generate Sealed Milestone Agreement
          </button>
        </div>

        <div id="contract_output" class="mt-6 hidden">
          <h3 class="text-xs uppercase tracking-wider text-gray-400 mb-2">Contract Agreement Markdown:</h3>
          <pre id="contract_text" class="bg-black/60 p-3 rounded text-xs text-gray-300 overflow-x-auto max-h-56"></pre>
        </div>
      </div>

    </div>

    <!-- Live Architecture Footer -->
    <div class="mt-12 text-center text-xs text-gray-500 border-t border-gray-800 pt-6">
      Open-Source Kernel powered by <a href="https://github.com/Amz34/talentproof-protocol" target="_blank" class="text-emerald-400 hover:underline">TalentProof Protocol</a> | Apache 2.0 License
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
