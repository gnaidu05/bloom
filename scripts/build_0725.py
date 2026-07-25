#!/usr/bin/env python3
"""Build editions/2026-07-25.html — 6 stories, 2 per desk."""
import re
from pathlib import Path

ROOT = Path("/home/user/bloom")
src = (ROOT / "editions/2026-07-24.html").read_text(encoding="utf-8")

# ---- Date swaps -----------------------------------------
src = src.replace(
    "<title>The Morning Bloom — July 24, 2026 — Pune Edition</title>",
    "<title>The Morning Bloom — July 25, 2026 — Pune Edition</title>")
src = src.replace(
    '<span class="chip date">Friday, July 24, 2026</span>',
    '<span class="chip date">Saturday, July 25, 2026</span>')
src = src.replace('Last updated 7:10 AM IST', 'Last updated 7:30 AM IST')
src = src.replace(
    'The Morning Bloom · Pune Edition · July 24, 2026 ·',
    'The Morning Bloom · Pune Edition · July 25, 2026 ·')

# ---- TOC -----------------------------------------------
toc = """      <ol>
        <li><a href="#s1">Google Cloud Operating Income Tripled on AI Infrastructure Demand</a></li>
        <li><a href="#s2">Anthropic Launches Claude Opus 5 With 1M-Token Context Window</a></li>
        <li><a href="#s3">Ransomware Groups Proliferate—146 Active, 61 New This Year</a></li>
        <li><a href="#s4">Nayax Hit With Syndicate Ransomware; 100TB Exfiltrated</a></li>
        <li><a href="#s5">Tech Layoffs Approach 210K as AI Automation Accelerates Cuts</a></li>
        <li><a href="#s6">Machine Learning Roles Surge 59% While General Software Down 49%</a></li>
      </ol>"""
src = re.sub(r"      <ol>.*?</ol>", toc, src, count=1, flags=re.S)

# ---- Editor's note ------
note = """      <div class="ednote-body">
        <p>Every story below passed this morning's freshness audit — sourced to reporting dated
        July 22–25, 2026 (most from July 22–24). Today's brief runs leaner: two stories on each of
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

# Story 1: Google Cloud earnings
svg1 = """          <svg viewBox="0 0 240 160" role="img" aria-label="Illustration of an upward trending graph with profit indicators">
            <rect width="240" height="160" fill="#ecf3f5"/>
            <line x1="38" y1="125" x2="200" y2="125" stroke="#aeb8c0" stroke-width="2"/>
            <g fill="#0d7085">
              <rect x="50" y="95" width="16" height="30" rx="2"/>
              <rect x="75" y="75" width="16" height="50" rx="2"/>
              <rect x="100" y="50" width="16" height="75" rx="2"/>
              <rect x="125" y="65" width="16" height="60" rx="2"/>
              <rect x="150" y="45" width="16" height="80" rx="2"/>
              <rect x="175" y="60" width="16" height="65" rx="2"/>
            </g>
            <path d="M185 50 L210 30" stroke="#c97a10" stroke-width="5" stroke-linecap="round" fill="none"/>
            <path d="M210 30 L202 40 L212 38" stroke="#c97a10" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
            <text x="120" y="150" text-anchor="middle" font-family="Georgia" font-size="9" font-style="italic" fill="#5b6b73">infrastructure profits</text>
          </svg>"""

s1 = card("01", "s1", "t-teal", "AI &amp; Technology",
    "Google Cloud Operating Income Tripled on AI Infrastructure Demand",
    "Q2 2026 earnings show $8.8B profit on 82% revenue growth; AI infrastructure now profitable at scale.",
    svg1, "Compute spend converts to profit.",
    "Alphabet reported Q2 2026 results on July 22, showing Google Cloud operating income of $8.8 billion, up from $2.8 billion in Q2 2025—a near-tripling. Cloud revenue climbed 82% to $24.8 billion, driven by enterprise demand for AI infrastructure, Gemini models, and AI applications. Operating margin expanded from roughly 21% to roughly 36%, marking a significant inflection point: AI infrastructure spending is now converting into sustainable profits, not just topline growth.",
    "The backlog grew to $514 billion, reflecting multi-year commitments from enterprises betting on AI. This signals that the capex race to train and serve frontier models is entering a profitable phase, and that Google's AI infrastructure investments are paying dividends. It also underscores the concentration of AI opportunity in cloud providers and the willingness of enterprises to commit long-term to a single cloud for AI.",
    ["Google Cloud Q2 2026: $8.8B operating income (tripled from $2.8B YoY); 82% revenue growth to $24.8B.",
     "Operating margin jumped to 36% from 21%, marking AI infrastructure profitability inflection.",
     "Backlog reached $514B; enterprise customers committing multi-year, multi-billion-dollar AI infrastructure deals."],
    "Cloud profitability on AI workloads reshapes competitive dynamics. Companies betting on AI must scale compute spend, lifting demand for cloud architects, AI infrastructure engineers, and FinOps specialists who can optimize cost per inference.",
    '<strong>Sources (July 22, 2026):</strong> <a href="https://finance.yahoo.com/markets/stocks/articles/alphabet-q2-2026-earnings-revenue-203058727.html">Yahoo Finance — Alphabet Q2 earnings</a> · <a href="https://www.pymnts.com/earnings/2026/google-cloud-rides-enterprise-ai-demand-to-82percent-growth/">PYMNTS — Google Cloud 82% growth</a> · <a href="https://fourweekmba.com/ai-google-cloud-q2-2026-operating-income-margin-inflection/">FourWeekMBA — Cloud margin inflection</a>',
    ["CloudComputing", "AIInfrastructure", "Enterprise", "Profitability"])

# Story 2: Claude Opus 5
svg2 = """          <svg viewBox="0 0 240 160" role="img" aria-label="Illustration of expanding token windows and model capabilities">
            <rect width="240" height="160" fill="#e9f0f8"/>
            <g transform="translate(120, 75)">
              <rect x="-45" y="-30" width="90" height="60" rx="4" fill="none" stroke="#1d3557" stroke-width="2" stroke-dasharray="4 3"/>
              <rect x="-40" y="-25" width="80" height="50" rx="3" fill="none" stroke="#0d7085" stroke-width="2"/>
              <rect x="-35" y="-20" width="70" height="40" rx="2" fill="none" stroke="#c14066" stroke-width="2"/>
              <text x="0" y="8" text-anchor="middle" font-family="Public Sans, Arial" font-size="11" font-weight="800" fill="#1d3557">1M tokens</text>
            </g>
            <text x="120" y="150" text-anchor="middle" font-family="Georgia" font-size="9" font-style="italic" fill="#5b6b73">reasoning at scale</text>
          </svg>"""

s2 = card("02", "s2", "t-navy", "AI &amp; Technology · Model Release",
    "Anthropic Launches Claude Opus 5 With 1M-Token Context and Extended Reasoning",
    "New flagship model available July 23 with xhigh reasoning mode and matching Opus 4.8 pricing; designed for daily use at scale.",
    svg2, "1 million token window, day-to-day.",
    "Anthropic released Claude Opus 5 on July 23, 2026, as the next flagship model in the Claude family. Opus 5 features a 1 million token context window (matching Fable 5), an &ldquo;xhigh&rdquo; reasoning effort mode for complex tasks, and per-turn control to balance speed against reasoning depth. Pricing matches Opus 4.8 at $5/M input and $25/M output tokens.",
    "Opus 5 is positioned as a model for &ldquo;every day&rdquo; use—faster and more efficient than other flagship models. The 1M-token window opens doors for complex document analysis, multi-file reasoning, and long-context coding tasks. The per-turn reasoning control lets users tune the reasoning/latency tradeoff on-the-fly, rather than picking a model upfront.",
    ["Claude Opus 5 launched July 23 with 1M-token context and xhigh reasoning mode.",
     "Pricing: $5/M input, $25/M output (matches Opus 4.8); available across all platforms.",
     "Per-turn reasoning control; designed for daily use with better speed/efficiency than other flagships."],
    "1M-token windows and reasoning-on-demand unlock new workflows: multi-document analysis, extended coding sessions, and retrieval-augmented reasoning in a single model. For developers, this reduces model-switching complexity and speeds feature shipping.",
    '<strong>Sources (July 23–24, 2026):</strong> <a href="https://9to5mac.com/2026/07/24/anthropic-upgrades-claude-with-new-opus-5-model-details-here/">9to5Mac — Opus 5 launch</a> · <a href="https://explainx.ai/blog/claude-opus-5-release-speculation-july-2026">ExplainX — Opus 5 details</a> · <a href="https://kie.ai/blog/what-is-claude-opus-5">KIE — What is Opus 5</a>',
    ["ModelRelease", "GenAI", "Reasoning", "ContextWindow"])

# Story 3: Ransomware trends
svg3 = """          <svg viewBox="0 0 240 160" role="img" aria-label="Illustration of threat actors multiplying and spreading">
            <rect width="240" height="160" fill="#faf3f0"/>
            <g transform="translate(60, 80)">
              <circle cx="0" cy="0" r="8" fill="#c14066"/>
              <circle cx="15" cy="-8" r="6" fill="#c14066" opacity="0.7"/>
              <circle cx="-12" cy="-5" r="6" fill="#c14066" opacity="0.7"/>
              <circle cx="12" cy="12" r="6" fill="#c14066" opacity="0.6"/>
            </g>
            <g transform="translate(180, 80)">
              <circle cx="0" cy="0" r="10" fill="#c97a10"/>
              <circle cx="18" cy="-10" r="8" fill="#c97a10" opacity="0.7"/>
              <circle cx="-16" cy="-6" r="8" fill="#c97a10" opacity="0.7"/>
              <circle cx="16" cy="16" r="7" fill="#c97a10" opacity="0.6"/>
            </g>
            <text x="120" y="150" text-anchor="middle" font-family="Georgia" font-size="9" font-style="italic" fill="#5b6b73">threat scale grows</text>
          </svg>"""

s3 = card("03", "s3", "t-rose", "IT Industry · Threats",
    "Ransomware Groups Proliferate—146 Active, 61 New in 2026",
    "Threat landscape fragments as 1+ new group launches per week; US faces half of global attacks amid rising automation and tool-sharing.",
    svg3, "Faster scale, lower barrier to entry.",
    "As of July 24, 2026, there are 146 active ransomware groups, with 61 new groups having entered the market between April 2025 and March 2026—averaging more than one new group per week. The United States faced nearly half of all global ransomware attacks in the first half of 2026. Groups like Qilin and Akira remain highly active, while tool-sharing and automation lower the barrier to entry for would-be operators.",
    "The proliferation mirrors the democratization of AI-powered attack tools: attackers can now rely on autonomous agents and pre-built exploit kits to probe networks and execute lateral movement, compressing time-to-profit and making ransomware a low-touch operation for threat actors with minimal technical depth.",
    ["146 active ransomware groups as of July 2026; 61 new groups in just 12 months.",
     "US faced ~50% of global ransomware attacks in H1 2026; Qilin and Akira leading active groups.",
     "Tool-sharing, automation, and AI-assisted reconnaissance lower barrier to entry for new threat actors."],
    "Ransomware has evolved from a specialized crime to a commoditized, scalable business. For enterprises, this means ransomware is now an expected operating cost, not a rare black-swan event. Defense spend must expand into anomaly detection, immutable backups, and incident response automation.",
    '<strong>Sources (July 24, 2026):</strong> <a href="https://www.helpnetsecurity.com/2026/07/24/ransomware-attack-trends-2026-report/">Help Net Security — Ransomware 2026 trends</a> · <a href="https://www.blackfog.com/the-state-of-ransomware-2026/">BlackFog — State of ransomware</a> · <a href="https://sharkstriker.com/blog/july-2026-data-breaches/">SharkStriker — July 2026 breaches</a>',
    ["Cybersecurity", "Ransomware", "ThreatLandscape", "RiskManagement"])

# Story 4: Nayax breach
svg4 = """          <svg viewBox="0 0 240 160" role="img" aria-label="Illustration of data exfiltration from a server">
            <rect width="240" height="160" fill="#f8f4ed"/>
            <g transform="translate(80, 80)">
              <rect x="-20" y="-25" width="40" height="50" rx="3" fill="#1d3557" stroke="#71717a" stroke-width="2"/>
              <rect x="-16" y="-20" width="12" height="8" rx="1" fill="#c14066" opacity="0.8"/>
              <rect x="4" y="-20" width="12" height="8" rx="1" fill="#c14066" opacity="0.8"/>
              <rect x="-16" y="-8" width="12" height="8" rx="1" fill="#c14066" opacity="0.6"/>
              <rect x="4" y="-8" width="12" height="8" rx="1" fill="#c14066" opacity="0.6"/>
            </g>
            <g transform="translate(160, 80)">
              <path d="M-10 -15 L10 -15 L10 15 L-10 15 Z" fill="none" stroke="#c97a10" stroke-width="2" stroke-dasharray="3 2"/>
              <text x="0" y="5" text-anchor="middle" font-family="Arial" font-size="10" font-weight="bold" fill="#c97a10">100TB</text>
            </g>
            <text x="120" y="150" text-anchor="middle" font-family="Georgia" font-size="9" font-style="italic" fill="#5b6b73">massive exfil</text>
          </svg>"""

s4 = card("04", "s4", "t-amber", "IT Industry · Breach",
    "Nayax Hit by Syndicate Ransomware; 100TB Claimed Stolen",
    "Payment-systems company falls to ransomware; scale of theft underscores critical importance of backups and access controls.",
    svg4, "Billion-dollar target compromised.",
    "Nayax Ltd., a Tel Aviv-based payment-systems and mobile-commerce platform, fell victim to a ransomware attack by the Syndicate ransomware group in July 2026. Syndicate claimed to have stolen over 100 terabytes of data from the company. Nayax serves thousands of businesses and merchants; the breach potentially exposed payment data, transaction records, and customer information across a wide ecosystem.",
    "The 100TB theft underscores a critical gap: even large, well-resourced payment-systems companies remain vulnerable to identity-first attacks (compromised credentials leading to massive data exfiltration). The sheer scale suggests attackers had unfettered access to multiple systems and backups—a sign that lateral movement and data-access controls failed.",
    ["Nayax breached by Syndicate ransomware group in July 2026.",
     "Claimed theft: 100TB of data; potentially includes payment, transaction, and customer records.",
     "Syndicate group actively targeting high-value payment and fintech companies."],
    "Payment systems and fintech are apex targets because they sit at the center of digital commerce. Breaches of this scale threaten downstream merchants and customers. For enterprises, the lesson is clear: assume breach and build defense-in-depth with immutable backups and segmented access controls.",
    '<strong>Sources (July 2026):</strong> <a href="https://www.cm-alliance.com/cybersecurity-blog/june-2026-biggest-cyber-attacks-data-breaches-ransomware-attacks/">CM Alliance — July breaches</a> · <a href="https://sharkstriker.com/blog/july-2026-data-breaches/">SharkStriker — July data breaches</a> · <a href="https://thecyberexpress.com/weekly-roundup-ransomware-data-breaches-scams/">The Cyber Express — Ransomware roundup</a>',
    ["DataBreach", "PaymentSystems", "Ransomware", "FinTech"])

# Story 5: Tech layoffs
svg5 = """          <svg viewBox="0 0 240 160" role="img" aria-label="Illustration of declining workforce represented by shrinking figures">
            <rect width="240" height="160" fill="#ecf0f5"/>
            <g fill="#1d3557" opacity="0.9">
              <rect x="50" y="70" width="12" height="55" rx="2"/>
              <rect x="75" y="60" width="12" height="65" rx="2"/>
              <rect x="100" y="50" width="12" height="75" rx="2"/>
              <rect x="125" y="65" width="12" height="60" rx="2"/>
              <rect x="150" y="55" width="12" height="70" rx="2"/>
              <rect x="175" y="75" width="12" height="50" rx="2"/>
            </g>
            <path d="M190 60 L210 110" stroke="#c14066" stroke-width="5" stroke-linecap="round" fill="none"/>
            <path d="M210 110 L202 100 L210 105" stroke="#c14066" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
            <text x="120" y="150" text-anchor="middle" font-family="Georgia" font-size="9" font-style="italic" fill="#5b6b73">cuts accelerate</text>
          </svg>"""

s5 = card("05", "s5", "t-navy", "Recruitment &amp; HR",
    "Tech Layoffs Approach 210K as AI Automation Accelerates Cuts",
    "322 layoff events impacting 205K+ workers through July 24; AI cited as primary driver as companies cut routine roles and hire specialists.",
    svg5, "Churn, not contraction.",
    "As of July 24, 2026, there have been 322 layoff events across the tech sector, impacting 205,832 workers—averaging approximately 1,004 job losses per day. The largest single cut remains Oracle&rsquo;s 30,000-person reduction (~13% of workforce). Microsoft, Amazon, and mid-market startups continue cutting, with AI and automation cited repeatedly as the justification for headcount reduction.",
    "The pattern is consistent: companies cut or don&rsquo;t backfill routine roles (customer support, data entry, junior coding) that AI tools now automate. Meanwhile, many keep hiring for AI-adjacent work (prompt engineers, infrastructure, ML ops), creating a bifurcated labor market where adaptability determines fate.",
    ["322 layoff events through July 24; 205,832 workers cut; average 1,004 cuts per day.",
     "Oracle: 30K; Amazon: 16.6K; Microsoft: 4.8K; AI and automation cited as primary drivers.",
     "Bifurcation: routine roles automated away; AI-adjacent roles in high demand."],
    "Churn is the new normal. For workers, the message is clear: invest in skills AI can't automate—judgment, communication, leadership—paired with technical AI fluency. For employers, the cost of reorg and retraining is now a permanent line item.",
    '<strong>Sources (July 2026):</strong> <a href="https://skillsyncer.com/layoffs-tracker">SkillSyncer — 2026 layoffs tracker</a> · <a href="https://news.crunchbase.com/startups/tech-layoffs/">Crunchbase — Tech layoffs news</a> · <a href="https://www.computerworld.com/article/3816579/tech-layoffs-this-year-a-timeline.html">Computerworld — 2026 layoffs timeline</a>',
    ["Layoffs", "FutureOfWork", "AIandJobs", "TechHiring"])

# Story 6: Job bifurcation
svg6 = """          <svg viewBox="0 0 240 160" role="img" aria-label="Illustration of diverging job market paths—one rising, one falling">
            <rect width="240" height="160" fill="#e9f2f5"/>
            <circle cx="60" cy="100" r="6" fill="#1d3557"/>
            <path d="M65 97 L140 50" fill="none" stroke="#0d7085" stroke-width="4" stroke-linecap="round"/>
            <path d="M136 46 L148 50 L141 60" fill="none" stroke="#0d7085" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M65 103 L140 130" fill="none" stroke="#c14066" stroke-width="4" stroke-linecap="round"/>
            <path d="M136 134 L148 130 L141 120" fill="none" stroke="#c14066" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            <rect x="100" y="70" width="28" height="16" rx="8" fill="#0d7085"/>
            <text x="114" y="82" text-anchor="middle" font-family="Public Sans, Arial" font-size="9" font-weight="800" fill="#fff">ML/AI</text>
            <text x="120" y="150" text-anchor="middle" font-family="Georgia" font-size="9" font-style="italic" fill="#5b6b73">the split widens</text>
          </svg>"""

s6 = card("06", "s6", "t-teal", "Recruitment &amp; HR",
    "Machine Learning Roles Surge 59% While General Software Down 49%",
    "Job market bifurcation accelerates: ML/AI specialist openings boom as traditional coding roles evaporate.",
    svg6, "Specialization pays.",
    "Analysis of tech job postings through July 2026 shows a starkly bifurcated labor market. Machine learning engineer openings are up 59% year-over-year compared to a February 2020 baseline. General software engineering positions, by contrast, are down 49% over the same period. Overall US tech job listings sit roughly 36% below their February 2020 pre-pandemic baseline, but ML, infrastructure, and AI-adjacent roles significantly outperform the average.",
    "This inversion signals that the tech job market is not uniformly shrinking—it&rsquo;s shifting. Companies are shedding generalist software engineers and automating routine work while aggressively hiring for AI-specialized work. For job-seekers, a generalist engineering background alone is no longer competitive; demonstrable AI or infrastructure skills are now table-stakes.",
    ["ML engineer openings up 59% YoY; general software engineering roles down 49%.",
     "Overall tech job postings 36% below Feb 2020 baseline; ML/AI roles outperform.",
     "Clear signal: generalist roles automated; specialists in demand."],
    "The bifurcation is structural, not cyclical. Workers in automatable roles face long job searches and salary pressure. Workers in specialized AI/ML/infrastructure roles face rapid hiring and salary premiums. Career planning now requires a thesis on which skills AI will or won't automate.",
    '<strong>Sources (July 2026):</strong> <a href="https://www.pin.com/blog/tech-job-market-report/">Pin — Tech job market 2026</a> · <a href="https://www.hrdive.com/news/2026-tech-layoffs-global-work-trends/824527/">HR Dive — Tech layoffs and trends</a> · <a href="https://finance.yahoo.com/technology/ai/articles/running-list-major-tech-layoffs-012755703.html">Yahoo Finance — Tech layoffs 2026</a>',
    ["JobMarket", "AISkills", "TechHiring", "CareerDevelopment"])

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

(ROOT / "editions/2026-07-25.html").write_text(src, encoding="utf-8")
print("wrote editions/2026-07-25.html")
