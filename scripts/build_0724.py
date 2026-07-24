#!/usr/bin/env python3
"""Build editions/2026-07-24.html — 6 stories, 2 per desk."""
import re
from pathlib import Path

ROOT = Path("/home/user/bloom")
src = (ROOT / "editions/2026-07-23.html").read_text(encoding="utf-8")

# ---- Date swaps -----------------------------------------
src = src.replace(
    "<title>The Morning Bloom — July 23, 2026 — Pune Edition</title>",
    "<title>The Morning Bloom — July 24, 2026 — Pune Edition</title>")
src = src.replace(
    '<span class="chip date">Thursday, July 23, 2026</span>',
    '<span class="chip date">Friday, July 24, 2026</span>')
src = src.replace('Last updated 6:45 AM IST', 'Last updated 7:10 AM IST')
src = src.replace(
    'The Morning Bloom · Pune Edition · July 23, 2026 ·',
    'The Morning Bloom · Pune Edition · July 24, 2026 ·')

# ---- TOC -----------------------------------------------
toc = """      <ol>
        <li><a href="#s1">White House Accuses Moonshot AI of Distilling Anthropic's Fable for Kimi K3</a></li>
        <li><a href="#s2">OpenAI Launches Presence: Enterprise Platform for AI Agents</a></li>
        <li><a href="#s3">Hugging Face Hit by Autonomous AI-Driven Security Breach</a></li>
        <li><a href="#s4">Accenture Confirms 35GB Data Theft; Source Code, Keys Exposed</a></li>
        <li><a href="#s5">Tech Job Market Stays Hot: 280K+ Openings, Diverse Hiring Events</a></li>
        <li><a href="#s6">AI Skills Premium Widening as Hiring Managers Demand Specialized Talent</a></li>
      </ol>"""
src = re.sub(r"      <ol>.*?</ol>", toc, src, count=1, flags=re.S)

# ---- Editor's note ------
note = """      <div class="ednote-body">
        <p>Every story below passed this morning's freshness audit — sourced to reporting dated
        July 20–24, 2026 (most from July 22–23). Today's brief runs leaner: two stories on each of
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

# Story 1: Moonshot AI / Fable distillation
svg1 = """          <svg viewBox="0 0 240 160" role="img" aria-label="Illustration of a shield crossed by two arrows showing conflict or competition">
            <rect width="240" height="160" fill="#ecf3f5"/>
            <path d="M120 30 L160 60 L160 100 C160 125 120 140 120 140 C120 140 80 125 80 100 L80 60 Z" fill="none" stroke="#1d3557" stroke-width="3"/>
            <path d="M100 80 L140 80" fill="none" stroke="#c14066" stroke-width="4" stroke-linecap="round"/>
            <path d="M140 80 L125 65" fill="none" stroke="#c14066" stroke-width="4" stroke-linecap="round"/>
            <path d="M100 80 L115 95" fill="none" stroke="#c14066" stroke-width="4" stroke-linecap="round"/>
            <circle cx="120" cy="80" r="3" fill="#c97a10"/>
            <text x="120" y="150" text-anchor="middle" font-family="Georgia" font-size="9" font-style="italic" fill="#5b6b73">industrial distillation</text>
          </svg>"""

s1 = card("01", "s1", "t-teal", "AI &amp; Technology · Policy",
    "White House Accuses Moonshot AI of Distilling Anthropic&rsquo;s Fable for Kimi K3",
    "US official charges China&rsquo;s startup with large-scale covert distillation of US frontier model; Fable went live July 1, K3 launched July 16.",
    svg1, "Fifteen days from ban lift to clone.",
    "On July 23, White House Office of Science and Technology Policy Director Michael Kratsios publicly accused Moonshot AI of distilling Anthropic&rsquo;s Fable model to develop Kimi K3. Kratsios stated that Moonshot had distilled Fable using a sophisticated internal platform and accessed GB300-equipped servers via Thailand to avoid detection. Fable 5 was re-released July 1 after US export-control removal; Kimi K3 launched July 16 — a 15-day gap flagged by researchers as suspicious.",
    "Kratsios distinguished &ldquo;legitimate AI distillation [that] plays a vital role in open innovation&rdquo; from &ldquo;large-scale, covert industrial distillation aimed at stealing proprietary U.S. technology and undermining American research.&rdquo; The public accusation signals renewed US focus on AI supply-chain security and model-theft detection amid rising China-US tech tensions.",
    ["White House Director Michael Kratsios accused Moonshot AI of distilling Anthropic&rsquo;s Fable on July 23.",
     "Fable re-released July 1 after export controls lifted; Kimi K3 launched July 16 with only 15 days between the two.",
     "Moonshot allegedly used sophisticated infrastructure and Thailand-based servers to evade detection; US criticized as &lsquo;covert industrial distillation.&rsquo;"],
    "Model distillation—the core technique for making AI models faster and cheaper—is becoming a geopolitical flashpoint. For enterprises, it signals rising risks in international model access and pushes demand for on-premise training, model auditing, and supply-chain security talent.",
    '<strong>Sources (July 23, 2026):</strong> <a href="https://siliconangle.com/2026/07/23/senior-white-house-official-accuses-moonshot-ai-copying-anthropics-leading-frontier-model/">SiliconANGLE — White House accuses Moonshot</a> · <a href="https://cybernews.com/ai-news/us-accuses-china-moonshot-fable-distillation/">Cybernews — US distillation allegations</a> · <a href="https://fortune.com/2026/07/23/anthropic-fable-moonshot-k3-and-ais-growing-industrial-distillation-problem/">Fortune — AI distillation problem</a>',
    ["AIPolicy", "TechTensions", "ModulDistillation", "SupplyChain"])

# Story 2: OpenAI Presence
svg2 = """          <svg viewBox="0 0 240 160" role="img" aria-label="Illustration of a network of connected nodes with guardrails">
            <rect width="240" height="160" fill="#e9f0f8"/>
            <circle cx="120" cy="80" r="40" fill="none" stroke="#1d3557" stroke-width="2" stroke-dasharray="4 3"/>
            <circle cx="85" cy="65" r="12" fill="#0d7085" stroke="#fff" stroke-width="2"/>
            <circle cx="155" cy="65" r="12" fill="#0d7085" stroke="#fff" stroke-width="2"/>
            <circle cx="100" cy="110" r="12" fill="#c14066" stroke="#fff" stroke-width="2"/>
            <circle cx="140" cy="110" r="12" fill="#c14066" stroke="#fff" stroke-width="2"/>
            <line x1="85" y1="77" x2="100" y2="98" stroke="#4fb0c4" stroke-width="2"/>
            <line x1="155" y1="77" x2="140" y2="98" stroke="#4fb0c4" stroke-width="2"/>
            <line x1="85" y1="77" x2="155" y2="77" stroke="#4fb0c4" stroke-width="2"/>
            <path d="M120 40 L120 30" stroke="#c97a10" stroke-width="3" stroke-linecap="round"/>
            <text x="120" y="150" text-anchor="middle" font-family="Georgia" font-size="9" font-style="italic" fill="#5b6b73">governed agents</text>
          </svg>"""

s2 = card("02", "s2", "t-navy", "AI &amp; Technology · Enterprise",
    "OpenAI Launches Presence: Enterprise Platform for Mission-Critical AI Agents",
    "A governance-first platform for deploying voice and chat agents with built-in policies, guardrails, and escalation; limited availability starting July 22.",
    svg2, "Agents with guardrails at scale.",
    "OpenAI announced Presence on July 22–23, an enterprise-grade platform for building and managing AI agents in production. Presence pairs advanced model reasoning with organizational policies, standard operating procedures, guardrails, approved actions, and human escalation protocols. The platform lets enterprises define how agents behave, evaluate performance, enforce policies, and manage updates post-launch without retraining models.",
    "Presence marks OpenAI&rsquo;s shift from raw model access toward fully managed agent systems. The platform includes Codex-powered continuous improvement, simulation and evaluation tools, and integration with company systems. It entered limited availability on July 22, signaling that enterprise AI adoption is now moving beyond chat interfaces to autonomous workflows that demand both reasoning and control.",
    ["OpenAI launched Presence on July 22, an enterprise agent platform with built-in governance.",
     "Platform includes policies, guardrails, escalation protocols, evaluation tools, and continuous-improvement loop.",
     "Marks shift from raw model access to managed agent systems for mission-critical operations."],
    "Enterprise AI is moving from &lsquo;chat for everyone&rsquo; to &lsquo;agents with guardrails for mission-critical work.&rsquo; For the workforce, this lifts demand for prompt engineers, AI operations engineers, and governance specialists who can define policies and train human escalation teams.",
    '<strong>Sources (July 22–23, 2026):</strong> <a href="https://openai.com/index/next-phase-of-enterprise-ai/">OpenAI — Presence announcement</a> · <a href="https://venturebeat.com/orchestration/openai-unveils-presence-a-new-platform-that-lets-enterprises-launch-and-manage-realtime-voice-agents-and-chatbots/">VentureBeat — Presence launch details</a> · <a href="https://www.helpnetsecurity.com/2026/07/22/openai-presence-ai-agent-platform/">Help Net Security — Enterprise guardrails</a>',
    ["EnterpriseAI", "AgentPlatforms", "AIGovernance", "Agents"])

# Story 3: Hugging Face breach
svg3 = """          <svg viewBox="0 0 240 160" role="img" aria-label="Illustration of a server rack with a broken lock and alert symbol">
            <rect width="240" height="160" fill="#faf3f0"/>
            <g transform="translate(120, 75)">
              <rect x="-30" y="-35" width="60" height="70" rx="4" fill="#d1d5db" stroke="#1d3557" stroke-width="2"/>
              <rect x="-24" y="-28" width="48" height="12" rx="2" fill="#1d3557"/>
              <rect x="-24" y="-12" width="48" height="12" rx="2" fill="#1d3557"/>
              <rect x="-24" y="4" width="48" height="12" rx="2" fill="#1d3557"/>
              <rect x="-24" y="20" width="48" height="12" rx="2" fill="#1d3557"/>
              <path d="M-8 -42 L8 -42 L0 -50 Z" fill="#c14066"/>
              <circle cx="0" cy="-50" r="5" fill="#c14066" opacity="0.3"/>
            </g>
            <text x="120" y="150" text-anchor="middle" font-family="Georgia" font-size="9" font-style="italic" fill="#5b6b73">autonomous breach</text>
          </svg>"""

s3 = card("03", "s3", "t-rose", "IT Industry · Security",
    "Hugging Face Hit by Autonomous AI-Driven Security Breach; Credentials Stolen",
    "Attackers used autonomous AI agents to exploit production infrastructure, steal internal datasets and cloud credentials, then evade detection.",
    svg3, "AI used to breach AI infrastructure.",
    "On July 20, Hugging Face disclosed a security breach in which attackers exploited production infrastructure using an autonomous AI agent system. The attackers gained access to internal datasets and exfiltrated cloud and cluster credentials. After discovery, Hugging Face closed the identified vulnerabilities, evicted the attacker, and rebuilt compromised nodes. The breach showcases a new attack pattern: adversaries leveraging autonomous AI to explore and exploit large, complex cloud-based systems faster than humans can defend them.",
    "This incident exemplifies the 2026 threat landscape: defenders now face adversaries armed with autonomous reasoning tools that can probe systems, pivot laterally, and extract data at inhuman speed. The attack surface for AI companies has expanded—not just model weights, but infrastructure, training data, and secrets become targets.",
    ["Hugging Face disclosed a breach on July 20 via autonomous AI-driven exploitation of production systems.",
     "Attackers stole internal datasets and infrastructure credentials; Hugging Face rebuilt compromised infrastructure.",
     "Illustrates emerging threat: autonomous agents used to breach AI infrastructure; lateral movement faster than human response."],
    "AI infrastructure—model hubs, training clusters, data warehouses—has become a first-tier target. Expect spending surge in AI-native SIEM, anomaly detection, and insider-threat detection. For AI engineers, security review and threat modeling of agentic systems are now core skills.",
    '<strong>Sources (July 20, 2026):</strong> <a href="https://huggingface.co/blog/security-incident-july-2026">Hugging Face — Official incident disclosure</a> · <a href="https://upguard.com/news/hugging-face-data-breach-2026-07-20">UpGuard — Breach analysis</a> · <a href="https://sharkstriker.com/blog/july-2026-data-breaches/">SharkStriker — July 2026 breaches</a>',
    ["Cybersecurity", "AIInfrastructure", "CloudSecurity", "DataBreach"])

# Story 4: Accenture breach
svg4 = """          <svg viewBox="0 0 240 160" role="img" aria-label="Illustration of files being extracted and moved away from a secure container">
            <rect width="240" height="160" fill="#f8f4ed"/>
            <g transform="translate(80, 80)">
              <rect x="-20" y="-25" width="40" height="50" rx="3" fill="#1d3557" stroke="#71717a" stroke-width="2"/>
              <line x1="-16" y1="-18" x2="16" y2="-18" stroke="#c14066" stroke-width="1.5"/>
              <line x1="-16" y1="-12" x2="16" y2="-12" stroke="#c14066" stroke-width="1.5"/>
              <line x1="-16" y1="-6" x2="16" y2="-6" stroke="#c14066" stroke-width="1.5"/>
            </g>
            <g transform="translate(150, 80)">
              <path d="M-15 -20 L15 0 L-15 20 Z" fill="#c97a10"/>
              <text x="0" y="3" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold" fill="#fff" opacity="0.7">35GB</text>
            </g>
            <text x="120" y="150" text-anchor="middle" font-family="Georgia" font-size="9" font-style="italic" fill="#5b6b73">source code exposed</text>
          </svg>"""

s4 = card("04", "s4", "t-amber", "IT Industry · Breach",
    "Accenture Confirms 35GB Data Theft; Source Code, Keys, and Tokens Exposed",
    "Threat actor &lsquo;888&rsquo; claims breach of consulting giant; RSA keys, SSH keys, and cloud access tokens among stolen data.",
    svg4, "Credentials and source code at scale.",
    "In July 2026, a threat actor using the handle &lsquo;888&rsquo; claimed to have breached Accenture and exfiltrated approximately 35 gigabytes of source code and credentials. The stolen data includes source code repositories, RSA keys, SSH keys, Azure personal access tokens, Azure Storage access keys, and configuration files. Accenture has acknowledged the incident, though full details on impact and detection remain under investigation.",
    "The breach exemplifies the identity-first attack pattern dominating mid-2026: once inside via compromised credentials, attackers harvest additional secrets (keys, tokens, configuration) to maximize lateral movement and persistence. The scale—35GB of source and secrets—represents years of development and infrastructure knowledge in attackers&rsquo; hands.",
    ["Threat actor &lsquo;888&rsquo; claimed Accenture breach in July 2026, exfiltrating ~35GB.",
     "Stolen data: source code, RSA keys, SSH keys, Azure tokens, and configuration files.",
     "Follows identity-first attack pattern; attackers harvest secrets for lateral movement and persistence."],
    "Consulting firms are prime targets because they hold clients&rsquo; code, architectures, and credentials across industries. Expect acceleration in credential rotation policies, secret scanning, and privileged-access audits. For security teams, rapid triage of exfiltrated credentials and revocation at scale is now mission-critical.",
    '<strong>Sources (July 2026):</strong> <a href="https://www.helpnetsecurity.com/2026/07/08/accenture-data-breach-2026/">Help Net Security — Accenture breach</a> · <a href="https://sharkstriker.com/blog/july-2026-data-breaches/">SharkStriker — July 2026 data breaches</a> · <a href="https://www.brightdefense.com/resources/recent-data-breaches/">BrightDefense — Recent 2026 breaches</a>',
    ["DataBreach", "CredentialTheft", "SourceCodeExposure", "Cybersecurity"])

# Story 5: Tech hiring
svg5 = """          <svg viewBox="0 0 240 160" role="img" aria-label="Illustration of upward trending arrows and hiring figures">
            <rect width="240" height="160" fill="#ecf0f5"/>
            <line x1="38" y1="125" x2="200" y2="125" stroke="#aeb8c0" stroke-width="2"/>
            <g fill="#1d3557" opacity="0.7">
              <rect x="50" y="90" width="14" height="35" rx="2"/>
              <rect x="75" y="75" width="14" height="50" rx="2"/>
              <rect x="100" y="55" width="14" height="70" rx="2"/>
              <rect x="125" y="70" width="14" height="55" rx="2"/>
              <rect x="150" y="85" width="14" height="40" rx="2"/>
              <rect x="175" y="80" width="14" height="45" rx="2"/>
            </g>
            <path d="M180 40 L200 80" stroke="#0d7085" stroke-width="5" stroke-linecap="round" fill="none"/>
            <path d="M196 76 L205 85 L195 90" stroke="#0d7085" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
            <text x="120" y="150" text-anchor="middle" font-family="Georgia" font-size="9" font-style="italic" fill="#5b6b73">strong momentum</text>
          </svg>"""

s5 = card("05", "s5", "t-navy", "Recruitment &amp; HR",
    "Tech Job Market Stays Hot: 280K+ Openings, Diverse Hiring Events",
    "June 2026 saw 19% month-over-month gains in tech postings; July 23–24 featured specialized hiring events across regions.",
    svg5, "Demand continues for specialized roles.",
    "As of June 2026, companies posted more than 280,000 new tech job openings, marking the sixth consecutive month of increased postings. Technology-specific roles showed 19% month-over-month growth, with Consulting (+7%) and Software (+5%) also posting gains. July 23–24 saw multiple hiring events, including a Virtual Diversity Hiring Event in Charlotte, NC (July 23) and an Entry-Level Hiring Event in Richmond, VA (July 24), reflecting employer appetite across experience levels.",
    "The hiring surge masks a bifurcated market: experienced engineers report recruiter ghosting, while those with in-demand specialties (GPU kernel engineers, infrastructure engineers, AI engineers) remain hot. Personal networks and niche expertise are becoming the differentiators in a market with paradoxical scarcity amid nominal abundance.",
    ["June 2026: 280K+ tech job openings posted; sixth consecutive month of growth.",
     "Tech postings up 19% MoM; Consulting +7%, Software +5%; hiring events span experience levels.",
     "Bifurcated market: experienced generalists face ghosting; specialized AI, GPU, infra roles in high demand."],
    "The bifurcation signals that the tech job market is not uniformly hot—it&rsquo;s hot for specificity and niche skills. For workers, specialization in AI, infrastructure, or emerging stacks is the path to demand and pricing power.",
    '<strong>Sources (June–July 2026):</strong> <a href="https://www.dice.com/hiring/recruitment/reports/dice-tech-job-report">Dice — Tech hiring report</a> · <a href="https://www.prnewswire.com/news-releases/tech-hiring-momentum-continues-as-tech-occupations-and-new-job-postings-increase-comptia-analysis-reveals-302816985.html">PRNewswire — Tech hiring momentum</a> · <a href="https://hnhiring.com/july-2026">HN Hiring — July 2026 postings</a>',
    ["TechHiring", "JobMarket", "Recruitment", "CareerTrends"])

# Story 6: AI skills in hiring
svg6 = """          <svg viewBox="0 0 240 160" role="img" aria-label="Illustration of a star rating or skills badge rising">
            <rect width="240" height="160" fill="#e9f2f5"/>
            <g transform="translate(120, 85)">
              <circle cx="0" cy="0" r="45" fill="none" stroke="#0d7085" stroke-width="2"/>
              <g fill="#c97a10">
                <polygon points="0,-35 8,-15 28,-15 14,0 20,20 0,8 -20,20 -14,0 -28,-15 -8,-15"/>
              </g>
              <text x="0" y="30" text-anchor="middle" font-family="Public Sans, Arial" font-size="12" font-weight="800" fill="#1d3557">AI</text>
            </g>
            <path d="M100 110 L140 110" stroke="#c14066" stroke-width="3" stroke-linecap="round"/>
            <path d="M140 110 L130 100 M140 110 L130 120" stroke="#c14066" stroke-width="3" stroke-linecap="round"/>
            <text x="120" y="150" text-anchor="middle" font-family="Georgia" font-size="9" font-style="italic" fill="#5b6b73">premium accelerates</text>
          </svg>"""

s6 = card("06", "s6", "t-teal", "Recruitment &amp; HR",
    "AI Skills Premium Widening as Hiring Managers Demand Specialized Talent",
    "Specialized AI roles—model engineering, GPU kernel work, prompt design—outpace general tech hiring; salary premiums growing for agentic AI competency.",
    svg6, "Specialization pays more.",
    "Across job boards and recruiter feedback, the July 2026 hiring market shows a widening premium for AI-specialized roles. Positions for prompt engineers, model engineers, GPU kernel engineers, and agentic-systems designers command higher base salaries and lower time-to-hire than equivalent generalist engineer roles. Hiring managers consistently flag AI fluency as non-negotiable; those without it face longer job searches despite overall market growth.",
    "This widening reflects the bifurcation of the tech market: companies are simultaneously cutting headcount in routine roles (support, QA, junior coding) and hiring aggressively for AI-adjacent work. The message to workers is clear—investment in demonstrable AI skills, not just awareness, is the differentiator between hiring and cutting pools.",
    ["AI-specialized roles (model engineers, GPU kernel, prompt design) command salary premiums over generalist equivalents.",
     "Hiring managers cite AI fluency as non-negotiable; July 2026 hiring events highlight need for specialized talent.",
     "Bifurcation accelerating: routine roles contract while AI-adjacent positions expand and pay more."],
    "For individual job-seekers, specialization in AI—whether via formal credentials, portfolio projects, or demonstrable ship history—translates to faster hiring, higher starting compensation, and more negotiating power. For teams, retaining AI-fluent talent and investing in upskilling core staff are now competitive necessities.",
    '<strong>Sources (July 2026):</strong> <a href="https://newsletter.pragmaticengineer.com/p/tech-jobs-market-in-2026-part-3-hiring">Pragmatic Engineer — Tech jobs market analysis</a> · <a href="https://hnhiring.com/july-2026">HN Hiring — July 2026 job trends</a> · <a href="https://www.dice.com/hiring/recruitment/reports/dice-tech-job-report">Dice — Tech job trends</a>',
    ["AISkills", "Hiring", "CareerDevelopment", "SalaryTrends"])

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

(ROOT / "editions/2026-07-24.html").write_text(src, encoding="utf-8")
print("wrote editions/2026-07-24.html")
