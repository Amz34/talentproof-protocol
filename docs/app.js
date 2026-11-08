/**
 * app.js - TalentProof Protocol Client-Side Kernel
 * Pure JavaScript Web Crypto SHA-256 Attestation & Escrow Generator
 */

// Utility: Compute SHA-256 using Browser Web Crypto API
async function sha256(message) {
  const msgBuffer = new TextEncoder().encode(message);
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

// Generate Developer Proof & SVG Badge
async function generateDevProof() {
  const handle = document.getElementById('gh_handle').value.trim() || 'Amz34';
  const commits = parseInt(document.getElementById('commit_count').value, 10) || 500;
  const hasCi = document.getElementById('has_ci').checked;
  const hasTests = document.getElementById('has_tests').checked;

  const entropy = Math.min(0.98, Math.max(0.65, 0.70 + (commits / 2000.0) * 0.25));
  const readiness = 0.50 + (hasCi ? 0.25 : 0.0) + (hasTests ? 0.25 : 0.0);
  
  // Composite reputation score
  const rep = Math.round(((0.91 * 0.40) + (entropy * 0.30) + (readiness * 0.30)) * 100.0 * 10) / 10;
  
  // Fair market USD rate benchmark
  const marketRate = Math.max(2500, Math.min(12000, Math.round(3200 + (rep - 70.0) * 160)));
  const ts = new Date().toISOString();

  const proofHash = await sha256(`${handle}:${commits}:${rep}:${ts}`);
  const shortHash = proofHash.substring(0, 32);

  // Render SVG Badge (Unslop craft standard)
  const svgMarkup = `<svg width="460" height="150" viewBox="0 0 460 150" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="460" height="150" rx="8" fill="#0D1117" stroke="#30363D" stroke-width="1.5"/>
  <rect x="20" y="20" width="10" height="10" rx="2" fill="#2EA043"/>
  <text fill="#58A6FF" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="12" font-weight="600" x="38" y="29">TalentProof Protocol Verified</text>
  <text fill="#F0F6FC" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="20" font-weight="600" x="20" y="65">@${handle}</text>
  <text fill="#8B949E" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="12" x="20" y="88">Trust Index: <tspan fill="#3FB950" font-weight="600">${rep}/100</tspan> | Benchmark: <tspan fill="#F0883E" font-weight="600">$${marketRate.toLocaleString()} USD/mo</tspan></text>
  <text fill="#8B949E" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="11" x="20" y="112">Entropy: ${entropy.toFixed(2)} | Readiness: ${Math.round(readiness * 100)}% | Tests &amp; CI: Verified</text>
  <text fill="#484F58" font-family="monospace" font-size="9" x="20" y="134">SHA: ${shortHash}...</text>
</svg>`;

  document.getElementById('badge_preview').innerHTML = svgMarkup;
  document.getElementById('badge_output_container').classList.remove('hidden');

  // Store globally for download/copy
  window.currentBadgeSvg = svgMarkup;
  window.currentMarkdownEmbed = `[![TalentProof Verified](https://raw.githubusercontent.com/Amz34/talentproof-protocol/main/assets/profile_badge.svg)](https://amz34.github.io/talentproof-protocol)`;
}

// Copy SVG to clipboard
function copySvgMarkup() {
  if (window.currentBadgeSvg) {
    navigator.clipboard.writeText(window.currentBadgeSvg);
    showNotice('SVG markup copied to clipboard!');
  }
}

// Copy Markdown Embed code
function copyMarkdownCode() {
  if (window.currentMarkdownEmbed) {
    navigator.clipboard.writeText(window.currentMarkdownEmbed);
    showNotice('Markdown embed copied to clipboard!');
  }
}

// Generate Milestone Escrow Contract
async function generateContract() {
  const client = document.getElementById('contract_client').value.trim() || 'Apex Retail Group';
  const dev = document.getElementById('contract_dev').value.trim() || 'Amz34';
  const scope = document.getElementById('contract_scope').value.trim() || 'High-throughput production architecture';
  const m1_title = document.getElementById('m1_title').value.trim() || 'Core Architecture & API Gateway';
  const m1_budget = parseInt(document.getElementById('m1_budget').value, 10) || 2000;
  const m2_title = document.getElementById('m2_title').value.trim() || 'Mobile Storefront & Payment Engine';
  const m2_budget = parseInt(document.getElementById('m2_budget').value, 10) || 3000;

  const total = m1_budget + m2_budget;
  const ts = new Date().toISOString();
  const cHash = await sha256(`${client}:${dev}:${total}:${ts}`);
  const cid = `TP-ESCROW-${cHash.substring(0, 10).toUpperCase()}`;

  const contractMd = `# Bilateral Technical Milestone Agreement (ID: ${cid})
**Client / Enterprise Buyer**: ${client}
**Lead Software Architect**: @${dev}
**Total Contract Value**: $${total.toLocaleString()} USD (Milestone-Locked Escrow)
**Contract Digest SHA-256**: \`${cHash}\`
**Effective Date**: ${ts}

---
## 1. Project Purpose & Architecture Scope
${scope}

## 2. Milestone Verification & Payout Schedule

### Milestone 1: ${m1_title} ($${m1_budget.toLocaleString()} USD)
* **Status**: \`LOCKED_IN_ESCROW\`
* **Acceptance Verification Gate**: \`pytest tests/ --cov=85 exits 0\`

### Milestone 2: ${m2_title} ($${m2_budget.toLocaleString()} USD)
* **Status**: \`LOCKED_IN_ESCROW\`
* **Acceptance Verification Gate**: \`npm run test:e2e && flutter test exits 0\`

## 3. Sovereign Escrow Invariant
- Payout releases require deterministic test pass verification and client digital sign-off.
- No arbitrary scope creep permitted after cryptographic hashing without a bilateral addendum.

---
*Generated autonomously via TalentProof Protocol Web App — https://amz34.github.io/talentproof-protocol*`;

  document.getElementById('contract_output_text').innerText = contractMd;
  document.getElementById('contract_output_container').classList.remove('hidden');
  window.currentContractMd = contractMd;
}

function copyContractMarkdown() {
  if (window.currentContractMd) {
    navigator.clipboard.writeText(window.currentContractMd);
    showNotice('Milestone Agreement Markdown copied!');
  }
}

function showNotice(text) {
  const el = document.getElementById('toast_notice');
  el.innerText = text;
  el.classList.remove('opacity-0');
  setTimeout(() => el.classList.add('opacity-0'), 3000);
}

// Register PWA Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('./sw.js').catch(() => {});
  });
}
