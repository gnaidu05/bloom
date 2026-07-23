#!/usr/bin/env python3
"""Build editions/2026-07-23.html — 6 stories, 2 per desk."""
import re
from pathlib import Path

ROOT = Path("/home/user/bloom")
src = (ROOT / "editions/2026-07-22.html").read_text(encoding="utf-8")

# ---- Date swaps -----------------------------------------
src = src.replace(
    "<title>The Morning Bloom — July 22, 2026 — Pune Edition</title>",
    "<title>The Morning Bloom — July 23, 2026 — Pune Edition</title>")
src = src.replace(
    '<span class="chip date">Wednesday, July 22, 2026</span>',
    '<span class="chip date">Thursday, July 23, 2026</span>')
src = src.replace('Last updated 7:00 AM IST', 'Last updated 6:45 AM IST')
src = src.replace(
    'The Morning Bloom · Pune Edition · July 22, 2026 ·',
    'The Morning Bloom · Pune Edition · July 23, 2026 ·')

# ---- TOC -----------------------------------------------
toc = """      <ol>
        <li><a href="#s1">Google Releases Gemini 3.6 Flash with 17% Fewer Tokens</a></li>
        <li><a href="#s2">Microsoft and Mistral Expand Partnership with Multibillion-Dollar GPU Deal</a></li>
        <li><a href="#s3">AWS CloudFront Outage Takes Down Canvas, Blackboard, Hugging Face</a></li>
        <li><a href="#s4">Ransomware Groups Target Higher Ed and Government in July Wave</a></li>
        <li><a href="#s5">Tech Layoffs Surge—205,832 Cut Across 322 Events in 2026</a></li>
        <li><a href="#s6">AI Skills Now Essential in 75% of Tech Job Postings</a></li>
      </ol>"""
src = re.sub(r"      <ol>.*?</ol>", toc, src, count=1, flags=re.S)

# ---- Editor's note ------
note = """      <div class="ednote-body">
        <p>Every story below passed this morning's freshness audit — sourced to reporting dated
        July 14–23, 2026 (most from July 21–22). Today's brief runs leaner: two stories on each of
        our three desks — <strong>AI &amp; Technology</strong>, <strong>IT Industry</strong> and
        <strong>Recruitment &amp; HR</strong>.</p>
        <p>All of today's items are <strong>Search-verified</strong> — traced to search results and
        dated reporting rather than fully opened articles. Every Sources line links the original reporting.</p>
      </div>"""
src = re.sub(r"      <div class=\"ednote-body\">.*?</div>", note, src, count=1, flags=re.S)

# ---- Story cards -----------------------------------------------
def card(num, cid, theme, cat, h2, deck, svg, figcap, p1, p2, takeaways, why, sources, topics):
    tk = "\n".join(f"            <li>{t}</li>" for t in takeaways)
    tp = "\n".join(
        f'          <button type="button" class="topic" data-tag="{t}">#{t}</button>' for t in topics)
    return f"""    <!-- {num} -->
    <article class="card {theme} reveal" id="{cid}">
      <div class="storyhead"><span class="num">{num}</span><span class="cat">{cat}</span><span class="vtag search">Search-verified</span></div>
      <div class="storybody">
        <h2>{h2}</h2>
        <p class="deck">{deck}</p>
        <figure>
{svg}
          <figcaption>{figcap}</figcaption>
        </figure>
        <div class="copy">
          <p>{p1}</p>
          <p>{p2}</p>
        </div>
        <div class="takeaways">
          <h3>Key takeaways</h3>
          <ul>
{tk}
          </ul>
        </div>
        <div class="why">
          <h3>Why it matters</h3>
          <p>{why}</p>
        </div>
        <p class="sources">{sources}</p>
        <div class="topics" aria-label="Topics">
{tp}
        </div>
      </div>
    </article>"""

# Story 1: Google Gemini 3.6 Flash
svg1 = """          <svg viewBox="0 0 240 160" role="img" aria-label="Illustration of a speedometer maxing out, showing performance">
            <rect width="240" height="160" fill="#ecf3f5"/>
            <g transform="translate(120,85)">
              <circle cx="0" cy="0" r="48" fill="none" stroke="#0d7085" stroke-width="4"/>
              <path d="M-35 15 A48 48 0 0 1 35 15" fill="none" stroke="#d4e8ee" stroke-width="3"/>
              <g transform="rotate(-150)"><line x1="0" y1="-48" x2="0" y2="-54" stroke="#0d7085" stroke-width="2.5"/></g>
              <g transform="rotate(-90)"><line x1="0" y1="-48" x2="0" y2="-54" stroke="#0d7085" stroke-width="2.5"/></g>
              <g transform="rotate(-30)"><line x1="0" y1="-48" x2="0" y2="-54" stroke="#c14066" stroke-width="2.5"/></g>
              <g transform="rotate(30)"><line x1="0" y1="-48" x2="0" y2="-54" stroke="#c14066" stroke-width="2.5"/></g>
              <line x1="0" y1="0" x2="0" y2="-38" stroke="#c14066" stroke-width="3" stroke-linecap="round" transform="rotate(25)"/>
              <circle cx="0" cy="0" r="5" fill="#c14066"/>
            </g>
            <text x="120" y="150" text-anchor="middle" font-family="Georgia" font-size="9" font-style="italic" fill="#5b6b73">speed and efficiency</text>
          </svg>"""

s1 = card("01", "s1", "t-teal", "AI &amp; Technology",
    "Google Releases Gemini 3.6 Flash With 17% Fewer Output Tokens",
    "A faster, cheaper Gemini model with improved coding and computer-use performance; the Pro flagship still stuck in testing.",
    svg1, "Performance gains with lower cost.",
    "On July 21, Google DeepMind released Gemini 3.6 Flash, cutting output tokens by 17% compared to 3.5 Flash while improving performance. Output pricing dropped from $9.00 to $7.50 per million tokens (input stays at $1.50/M). On the DeepSWE coding benchmark, 3.6 Flash scores 49 percent, up from 37 percent for 3.5 Flash; computer-use capability improved to 83.0 percent on OSWorld-Verified.",
    "The release also included Gemini 3.5 Flash-Lite and a cybersecurity variant (3.5 Flash Cyber, restricted to governments). Notably, Gemini 3.5 Pro remains stuck in partner testing after multiple delays, while pre-training has begun on Gemini 4.",
    ["Google released Gemini 3.6 Flash on July 21 with 17% fewer output tokens and improved coding/computer-use.",
     "Output pricing drops to $7.50/M tokens; coding benchmark up to 49% (from 37%); context window 1M tokens, max output 64k.",
     "Gemini 3.5 Pro still delayed; Gemini 4 pre-training already underway."],
    "A leaner, faster model at lower cost shifts the economics of AI inference—lifting demand for engineers who can optimize prompt design and integrate multi-model pipelines to trade latency against cost. For enterprises, faster models mean real-time AI at scale becomes viable.",
    '<strong>Sources (July 21, 2026):</strong> <a href="https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-6-flash-3-5-flash-lite-3-5-flash-cyber/">Google — Introducing Gemini models</a> · <a href="https://techcrunch.com/2026/07/21/google-releases-three-new-gemini-models-but-no-3-5-pro/">TechCrunch — Gemini 3.6 Flash launch</a> · <a href="https://9to5google.com/2026/07/21/gemini-3-6-flash-launch/">9to5Google — Gemini releases</a>',
    ["GenAI", "ModelReleases", "Inference", "Google"])

# Story 2: Microsoft & Mistral partnership
svg2 = """          <svg viewBox="0 0 240 160" role="img" aria-label="Illustration of two hands shaking with a circuit pattern">
            <rect width="240" height="160" fill="#e9f0f8"/>
            <g transform="translate(120, 80)">
              <path d="M-30 -20 L-20 -10 Q-10 0 0 5 Q10 0 20 -10 L30 -20" fill="none" stroke="#0d7085" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M-30 20 L-20 10 Q-10 0 0 -5 Q10 0 20 10 L30 20" fill="none" stroke="#c97a10" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="-20" cy="-10" r="3.5" fill="#c14066"/>
              <circle cx="0" cy="5" r="3.5" fill="#c14066"/>
              <circle cx="20" cy="-10" r="3.5" fill="#c14066"/>
              <circle cx="-20" cy="10" r="3.5" fill="#4fb0c4"/>
              <circle cx="0" cy="-5" r="3.5" fill="#4fb0c4"/>
              <circle cx="20" cy="10" r="3.5" fill="#4fb0c4"/>
            </g>
            <text x="120" y="150" text-anchor="middle" font-family="Georgia" font-size="9" font-style="italic" fill="#5b6b73">partnership scales AI</text>
          </svg>"""

s2 = card("02", "s2", "t-navy", "AI &amp; Technology · Infrastructure",
    "Microsoft and Mistral Expand Partnership With Multibillion-Dollar GPU Commitment",
    "A GPU surge in Europe backed by thousands of Nvidia Vera Rubin chips; Mistral models now in Copilot Studio and Microsoft Foundry.",
    svg2, "Joint bet on European capacity.",
    "On July 21, Microsoft announced a multibillion-dollar investment to procure Nvidia GPUs and expand its collaboration with French AI startup Mistral. The deal spans expanded Europe-based GPU capacity, new Mistral models in Microsoft Foundry and Copilot Studio, and a common deployment model crossing Azure's public cloud, customer-controlled Azure Local systems, and fully disconnected environments.",
    "Mistral is scaling infrastructure with thousands of NVIDIA Vera Rubin GPUs for training, inference, and large-scale AI deployment. Mistral Medium 3.5 and OCR 4 are now available in Microsoft Foundry; Mistral Medium 3.5 is in Copilot Studio. The infrastructure expansion advances Microsoft's European Digital Commitments and Sovereign Cloud strategy.",
    ["Microsoft and Mistral announced a multibillion-dollar GPU procurement partnership on July 21.",
     "Thousands of Nvidia Vera Rubin GPUs will support training, inference, and deployment; Mistral models now in Copilot Studio and Foundry.",
     "Deployment model spans public cloud, customer-controlled Azure Local, and offline/disconnected environments."],
    "Sovereign cloud and data residency are becoming competitive differentiators. For the workforce, the expansion deepens demand for infrastructure, ML ops, and cloud-security engineers in Europe—and signals that geopolitical constraints are reshaping where AI training and inference happen.",
    '<strong>Sources (July 21, 2026):</strong> <a href="https://news.microsoft.com/source/2026/07/21/microsoft-and-mistral-expand-strategic-partnership-to-give-enterprises-and-regulated-industries-frontier-ai-they-can-control/">Microsoft — Mistral partnership expansion</a> · <a href="https://www.unite.ai/microsoft-widens-mistral-deal-to-court-regulated-ai-buyers/">Unite.AI — Microsoft expands Mistral deal</a> · <a href="https://qz.com/microsoft-mistral-ai-partnership-infrastructure-europe-072126">Quartz — GPU deal details</a>',
    ["CloudInfrastructure", "Partnerships", "SovereignCloud", "GPU"])

# Story 3: AWS CloudFront outage
svg3 = """          <svg viewBox="0 0 240 160" role="img" aria-label="Illustration of a cloud with a lightning bolt and downward arrows">
            <rect width="240" height="160" fill="#f8f4ed"/>
            <g transform="translate(120, 70)">
              <path d="M-35 -15 a20 20 0 0 1 35 -5 a20 20 0 0 1 15 25 Z" fill="#d1d5db" stroke="#999" stroke-width="1"/>
              <path d="M-8 10 L0 -10 L5 5 L8 -15" fill="none" stroke="#c14066" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
              <g fill="#c14066" opacity="0.6">
                <rect x="-28" y="20" width="6" height="14" rx="2"/>
                <rect x="-16" y="18" width="6" height="16" rx="2"/>
                <rect x="-4" y="22" width="6" height="12" rx="2"/>
                <rect x="8" y="20" width="6" height="14" rx="2"/>
              </g>
            </g>
            <text x="120" y="150" text-anchor="middle" font-family="Georgia" font-size="9" font-style="italic" fill="#5b6b73">cascade and impact</text>
          </svg>"""

s3 = card("03", "s3", "t-rose", "IT Industry · Infrastructure",
    "AWS CloudFront Outage Cascades Across Canvas, Blackboard, Hugging Face",
    "A three-hour control-plane failure took down educational, ML, and critical-infrastructure sites across the globe.",
    svg3, "One zone, global blast radius.",
    "On July 16, AWS CloudFront experienced a configuration loading failure in its VPC Origins feature, causing a global outage from 07:45 to 11:18 UTC (3 hours 33 minutes). The incident was triggered by a single Frankfurt availability zone hitting a capacity limit, which cascaded into a control-plane failure affecting all VPC Origins endpoints worldwide.",
    "High-profile targets went offline: Canvas and Blackboard (learning platforms), Hugging Face (ML hub), Coda (collaborative workspace), Ubiquiti, Doxy, Frontegg, TigerData, and the UK National Lottery. Dependent SaaS platforms and services saw knock-on disruptions. The July outages (this plus earlier AWS and Google Cloud incidents in the same month) underscore that regional failures now have global blast radius.",
    ["AWS CloudFront experienced a VPC Origins control-plane failure on July 16 (07:45–11:18 UTC).",
     "Canvas, Blackboard, Hugging Face, Coda, and others went offline for 3+ hours; triggered by a single Frankfurt zone capacity limit.",
     "July 2026 saw multiple major cloud outages—AWS CloudFront, AWS eu-central-1, Google VMware Engine."],
    "Single-cloud or single-region architectures are now untenable. Expect accelerated adoption of multi-cloud failover, chaos engineering, and regional backup strategies—lifting demand for SRE, platform, and FinOps engineers who can architect resilience at scale.",
    '<strong>Sources (July 16, 2026):</strong> <a href="https://blog.incidenthub.cloud/aws-cloudfront-outage-jul-16-2026">IncidentHub — CloudFront outage analysis</a> · <a href="https://www.techtimes.com/articles/320971/20260719/aws-cloudfront-took-down-canvas-blackboard-hugging-face-in-control-plane-failure.htm">TechTimes — Canvas, Blackboard down</a> · <a href="https://www.pagerly.io/blog/aws-cloudfront-outage-july-2026">Pagerly — Outage breakdown</a>',
    ["CloudInfrastructure", "Reliability", "Outages", "SRE"])

# Story 4: Ransomware
svg4 = """          <svg viewBox="0 0 240 160" role="img" aria-label="Illustration of a padlock with a warning symbol">
            <rect width="240" height="160" fill="#faf3f0"/>
            <g transform="translate(120, 75)">
              <rect x="-18" y="-8" width="36" height="30" rx="4" fill="none" stroke="#c14066" stroke-width="3"/>
              <circle cx="-9" cy="-12" r="9" fill="none" stroke="#c14066" stroke-width="3"/>
              <circle cx="9" cy="-12" r="9" fill="none" stroke="#c14066" stroke-width="3"/>
              <path d="M-8 8 L0 18 L8 8" fill="#c97a10"/>
              <circle cx="0" cy="12" r="4" fill="#c97a10"/>
            </g>
            <text x="120" y="150" text-anchor="middle" font-family="Georgia" font-size="9" font-style="italic" fill="#5b6b73">identity and access</text>
          </svg>"""

s4 = card("04", "s4", "t-amber", "IT Industry · Security",
    "Ransomware Wave Targets Higher Ed and Government in July",
    "NightSpire and other groups exploit identity and access controls; July 2026 sees credential-based attacks dominating the threat landscape.",
    svg4, "Stolen credentials, devastating impact.",
    "In July, ransomware groups escalated attacks on higher education and government institutions. Cedar Crest College reported a breach on July 16, with the NightSpire ransomware group claiming responsibility and publishing data online. The Town of Milford discovered unauthorized access to its systems, with investigation ongoing into data exposure and impact.",
    "July 2026's threat landscape is dominated by identity-first attacks: adversaries are logging in with stolen or compromised credentials rather than breaking in. Tata Electronics confirmed a June breach after the World Leaks group published 204,341 files (~630GB). New variants like 'GodDamn' ransomware use BYOVD (Bring Your Own Vulnerable Driver) tactics, and lone attackers are breaching AWS environments in 72 hours using AI-assisted reconnaissance.",
    ["NightSpire claimed Cedar Crest College breach on July 16; Town of Milford hit in same period.",
     "July 2026 ransomware wave dominated by credential-based attacks, not network intrusion.",
     "New tactics: BYOVD, AI-assisted reconnaissance, and pre-existing access abuse."],
    "Credential hygiene, identity verification, and privileged-access management are now board-level priorities. Expect spending surge in IAM, immutable backup, offline recovery, and incident response—and steep demand for security engineers and red-teamers who understand the modern attack surface.",
    '<strong>Sources (July 2026):</strong> <a href="https://www.cm-alliance.com/cybersecurity-blog/june-2026-biggest-cyber-attacks-data-breaches-ransomware-attacks">CM Alliance — Cyber breach roundup</a> · <a href="https://sharkstriker.com/blog/july-2026-data-breaches/">SharkStriker — July breaches</a> · <a href="https://www.darkreading.com/cyberattacks-data-breaches">Dark Reading — Latest incidents</a>',
    ["Cybersecurity", "Ransomware", "IdentitySecurity", "GovernmentTech"])

# Story 5: Tech layoffs
svg5 = """          <svg viewBox="0 0 240 160" role="img" aria-label="Illustration of declining bar chart with diverging arrows">
            <rect width="240" height="160" fill="#ecf0f5"/>
            <line x1="38" y1="125" x2="200" y2="125" stroke="#aeb8c0" stroke-width="2"/>
            <g fill="#1d3557" opacity="0.8">
              <rect x="48" y="65" width="20" height="60" rx="2"/>
              <rect x="78" y="85" width="20" height="40" rx="2"/>
              <rect x="108" y="100" width="20" height="25" rx="2"/>
              <rect x="138" y="55" width="20" height="70" rx="2"/>
            </g>
            <path d="M170 50 L195 100" stroke="#c14066" stroke-width="5" stroke-linecap="round" fill="none"/>
            <path d="M185 96 L200 105 L192 115" fill="none" stroke="#c14066" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
            <text x="120" y="150" text-anchor="middle" font-family="Georgia" font-size="9" font-style="italic" fill="#5b6b73">cuts accelerate</text>
          </svg>"""

s5 = card("05", "s5", "t-navy", "Recruitment &amp; HR",
    "Tech Layoffs Surge—205,832 Cut Across 322 Events Through July 22",
    "More than 1,000 job losses per day; Oracle's 21,000-role cut and Microsoft's new wave headline a sector in churn.",
    svg5, "Cuts and reorg, simultaneous.",
    "As of July 22, 2026, there have been 322 layoff events across the tech sector, eliminating 205,832 jobs and averaging approximately 1,014 cuts per day. Oracle remains the year's largest single cutter (21,000 roles, ~13% of workforce, disclosed June 23). Microsoft is in another round affecting 4,800 jobs (~2.1% of staff), with the Xbox division hit hardest (3,200 roles through fiscal 2027; 1,600 already cut by July 6). Monday.com is cutting 20% of workforce (630 people).",
    "The culprit cited repeatedly: AI. Companies are cutting or not backfilling roles in content creation, support, data entry, and basic coding as they pilot automation—even as many keep hiring for AI-adjacent roles (model engineering, ML ops, prompt design). The result is churn, not simple contraction. Tech is now nearly one-third of all U.S. layoffs year-to-date.",
    ["322 layoff events, 205,832 workers cut; tech layoffs average 1,014/day as of July 22.",
     "Oracle: 21,000 (13%); Microsoft: 4,800 (2.1%, Xbox hardest); Monday.com: 20% (630).",
     "AI and automation cited as primary driver; companies cutting routine roles while hiring AI specialists."],
    "Churn rewards adaptability and demonstrable AI fluency, and punishes workers in automatable roles. For employers, reorg cycles now happen continuously. For workers, pairing AI skills with human judgment—problem-solving, communication, leadership—is the difference between cutting and hiring pools.",
    '<strong>Sources (July 2026):</strong> <a href="https://tech.yahoo.com/general/article/tech-layoffs-2026-tracking-all-of-the-job-cuts-so-far-across-oracle-meta-microsoft-samsung-and-others-144545528.html">Yahoo Tech — 2026 layoffs tracker</a> · <a href="https://news.crunchbase.com/startups/tech-layoffs/">Crunchbase — Tech layoff news</a> · <a href="https://www.trueup.io/layoffs">TrueUp — Layoffs tracker</a>',
    ["Layoffs", "FutureOfWork", "AIandJobs", "Restructuring"])

# Story 6: AI skills in jobs
svg6 = """          <svg viewBox="0 0 240 160" role="img" aria-label="Illustration of two diverging paths with AI skills label">
            <rect width="240" height="160" fill="#e9f2f5"/>
            <circle cx="58" cy="88" r="8" fill="#1d3557"/>
            <path d="M64 82 L195 48" fill="none" stroke="#c97a10" stroke-width="5" stroke-linecap="round"/>
            <path d="M188 44 L200 47 L195 58" fill="none" stroke="#c97a10" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M64 94 L195 120" fill="none" stroke="#c14066" stroke-width="5" stroke-linecap="round" stroke-dasharray="6 4"/>
            <rect x="90" y="68" width="32" height="16" rx="8" fill="#0d7085"/>
            <text x="106" y="80" text-anchor="middle" font-family="Public Sans, Arial" font-size="10" font-weight="800" fill="#fff">AI</text>
            <text x="120" y="150" text-anchor="middle" font-family="Georgia" font-size="9" font-style="italic" fill="#5b6b73">the market splits</text>
          </svg>"""

s6 = card("06", "s6", "t-teal", "Recruitment &amp; HR",
    "AI Skills Now Sit in 75% of Tech Job Postings — Market Splits in Two",
    "Dice and PwC data show AI fluency moving to the center of hiring; a 'two-track' labor market emerges.",
    svg6, "AI fluency, the price of entry.",
    "AI skills appeared in 75% of U.S. tech job postings in June, up from 73% in May and 178% year-over-year, according to Dice. Agentic AI, RAG, vector databases, and prompt engineering cluster as the in-demand stack. In banking, Hugging Face competency grew fastest (+77% YoY). Overall tech postings rose 3% month-on-month and 27% year-on-year.",
    "But PwC's 2026 AI Jobs Barometer flags the flip side: a 'two-track' labour market in which 'professionalised' roles—where AI handles routine work and human judgment is emphasized—grow faster, lifting demand for judgment, creativity, and leadership alongside technical AI skills. The biggest 2026 hiring shift is skills-based hiring, where organizations prioritize fundamental skills over degrees, but expectations are higher.",
    ["AI skills in 75% of June tech postings (up 178% YoY); agentic AI, RAG, vector DBs, prompt engineering lead.",
     "Banking's fastest-growing skill: Hugging Face (+77% YoY); tech postings up 3% MoM, 27% YoY.",
     "Two-track market: 'professionalised' roles pairing AI with human judgment grow faster than specialist AI roles."],
    "AI fluency is now the price of entry for most tech roles. The signal for workers is clear: pair demonstrable AI skills with the uniquely human capabilities—judgment, communication, leadership—that AI can't automate. For employers, job specs and interviews are being rewritten around AI competency.",
    '<strong>Sources (2026):</strong> <a href="https://www.dice.com/hiring/recruitment/reports/dice-tech-job-report">Dice — July 2026 Tech Job Report</a> · <a href="https://www.pwc.com/gx/en/news-room/press-releases/2026/pwc-2026-ai-jobs-barometer.html">PwC — 2026 AI Jobs Barometer</a> · <a href="https://www.hrdive.com/news/dice-report-tech-hiring-AI/824902/">HR Dive — AI skills in job postings</a>',
    ["AISkills", "FutureOfWork", "Hiring", "SkillsDriven"])

stories = f"""  <!-- ═══ Desk 1 — AI & Technology ═══ -->
  <div class="section-head reveal" id="desk-ai">
    <span class="sec-label">AI &amp; Technology</span>
    <span class="sec-rule" aria-hidden="true"></span>
    <span class="sec-count">2 stories</span>
  </div>
  <div class="grid">

{s1}

{s2}

  </div>
  <!-- end AI & Technology grid -->

  <!-- ═══ Desk 2 — IT Industry ═══ -->
  <div class="section-head reveal" id="desk-it">
    <span class="sec-label">IT Industry</span>
    <span class="sec-rule" aria-hidden="true"></span>
    <span class="sec-count">2 stories</span>
  </div>
  <div class="grid">

{s3}

{s4}

  </div>
  <!-- end IT Industry grid -->

  <!-- ═══ Desk 3 — Recruitment & HR ═══ -->
  <div class="section-head reveal" id="desk-rec">
    <span class="sec-label">Recruitment &amp; HR</span>
    <span class="sec-rule" aria-hidden="true"></span>
    <span class="sec-count">2 stories</span>
  </div>
  <div class="grid">

{s5}

{s6}

  </div>
  <!-- end Recruitment & HR grid -->"""

# Replace stories section
start = src.index("  <!-- ═══ Desk 1 — AI & Technology ═══ -->")
end_marker = "  <!-- end Recruitment & HR grid -->"
end = src.index(end_marker) + len(end_marker)
src = src[:start] + stories + src[end:]

(ROOT / "editions/2026-07-23.html").write_text(src, encoding="utf-8")
print("wrote editions/2026-07-23.html")
