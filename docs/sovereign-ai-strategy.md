# Sovereign AI — analýza a návrh pro Finshape (~700 lidí, ~500 vývojářů, banking software)

> Verze: 2026-05-14 · Plánovací fáze · Připraveno k diskusi a rozhodnutí o pilotu (Q4 2026 / Q1 2027)

---

## 1. Context

**Proč to děláme:** Současný stack pro coding (Claude Code Team/Max + OpenAI ChatGPT Codex Enterprise pro ~400 vývojářů, ~120 z toho Codex Enterprise) má čtyři rostoucí tlaky najednou:

1. **Regulace (DORA, GDPR, ČNB)** — banking software vyžaduje data residency v EU, kontrolu nad third-party dependencies, plný audit trail. Anthropic/OpenAI = US providers s CLOUD Act expozicí; i jejich EU regiony jurisdikčně nejsou imunní.
2. **Kontrola nákladů** — současný spend $20-40k/měsíc roste, jak víc lidí přechází na premium plány (Claude Code Max $100-200/seat, Codex Enterprise $60+/seat). Trajektorie ukazuje na $60-120k/měsíc během 12-18 měsíců.
3. **Nezávislost na vendorech** — strategická obrana proti zdražování, změnám politik (rate limits, model deprecation, geografické restrikce), výpadkům.
4. **Customizace a IP** — možnost fine-tune na interní codebase, doménové znalosti bankingu, vlastní embeddings na interních repozitářích bez exfiltrace do USA.

**Cíl:** Hybridní architektura, kde **sovereign open-weight stack pokryje 70-80 % denní coding rutiny** (autocompletion, refactoring, code review, vysvětlení, jednoduché agentic úkoly), zatímco **Claude Opus / GPT-5 zůstanou pro nejtěžších 20-30 %** (multi-repo refactor, novel algoritmy, hluboké debugging). Žádný "big bang" — sovereign jako default, frontier proprietary jako escalation.

**Časový horizont:** Pilot Q4 2026 (20-50 vývojářů), produkce Q1 2027 (rollout na ~400), refresh cyklus 2028.

---

## 2. Současný stav (baseline)

| Položka | Odhad |
|---|---|
| Codex Enterprise (~120 seats × $60) | ~$7.2k/měs |
| Claude Team/Pro (~280 seats × $25-30) | ~$7-8k/měs |
| Claude Code Max upgrade (subset power-users) | ~$5-15k/měs |
| Premium overages, ad-hoc API | ~$3-10k/měs |
| **Total dnes** | **~$22-40k/měs** |
| **12-měsíční trajektorie (více premium)** | **~$60-120k/měs** |

Současný spend na 400 lidí je **$55-100/seat/měsíc**, což odpovídá ~$13/dev/active-day na intenzivní Claude Code využití (faros.ai benchmark).

---

## 3. Cílová architektura (hybrid Sovereign AI)

```
┌────────────────────────────────────────────────────────────────┐
│ ~400 vývojářů (Claude Code / Cline / Roo / Continue / vlastní) │
└──────────────────────────┬─────────────────────────────────────┘
                           │ OpenAI-compatible API
                ┌──────────▼──────────┐
                │   AI Gateway        │  ← LiteLLM nebo OpenRouter-style
                │   (Praha/EU, vlastní)│  ← auth, audit log, routing, billing
                └──┬──────┬───────────┘  ← prefix-cache aware routing
                   │      │
        ┌──────────┘      └─────────────┐
        ▼                               ▼
┌───────────────────┐         ┌──────────────────────┐
│ Sovereign primary │         │ Frontier fallback    │
│ (70-80 % trafiku) │         │ (20-30 % hard tasks) │
├───────────────────┤         ├──────────────────────┤
│ • Qwen3-Coder-480B│         │ • Claude Opus 4.7    │
│ • DeepSeek V4-Pro │         │ • GPT-5 / GPT-5-Codex│
│ • GLM-4.7         │         │ (přes existující     │
│ • Kimi K2.6       │         │  enterprise smlouvy) │
│ + cheap tier:     │         │                      │
│ • Qwen3-Coder-Next│         │                      │
│ • Codestral 25.08 │         │                      │
└───────────────────┘         └──────────────────────┘
```

**Klíčové vlastnosti gatewaye (build, ne buy):**
- OpenAI-compatible endpoint → Claude Code / Codex CLI / Cursor / Cline všechny fungují beze změny
- Per-user / per-team token budgety, denní/měsíční limity
- Routing rules: model podle úlohy (inline completion → Codestral; chat → GLM-4.7; agent loop → Qwen3-Coder-480B; hard refactor → Opus)
- Centralizovaný prefix cache (RadixAttention v SGLang dělá 70-95 % cache hit při Claude Code-style workloadu)
- Audit log pro DORA (kdo, kdy, jaký prompt, jaký model, output) — uložené v EU
- Cost dashboard per dev / per team / per repo

---

## 4. Doporučený model mix

| Tier | Model | Licence | Role | Hardware (FP8) |
|---|---|---|---|---|
| **Frontier sovereign (primární default)** | **Qwen3-Coder-480B-A35B** | Apache 2.0 ✓ | Default pro agentic coding (Claude Code-like) | 8×H100/H200, ~250 GB FP8 |
| Frontier sovereign (alternativa) | DeepSeek V4-Pro (1.6T/49B) | MIT ✓ | A/B vs Qwen; nejvyšší SWE-Bench (80.6) | 8×H200/B200, ~800 GB FP8 nebo INT4 |
| Specialista na long agent loop | Kimi K2.6 (1T/32B) | Modified MIT ⚠️ | Multi-step agent swarm, 300 sub-agents | 8×H200/MI300X, INT4 ~594 GB |
| Cost-optimized primary | GLM-4.7 (355B/32B) | MIT ✓ | Menší footprint, stále near-frontier | 4×H100 AWQ, ~180 GB |
| Cheap/fast tier (inline) | **Qwen3-Coder-Next (3B aktivních)** | Apache 2.0 ✓ | Autocompletion, sub-sekundová latence | 1×L40S / A100 |
| Cheap/fast tier (EU sovereignty plus) | **Codestral 25.08** | Mistral Commercial | FIM autocompletion, FR jurisdikce | 1×H100 |
| Frontier proprietary (eskalace) | Claude Opus 4.7, GPT-5/Codex | komerční | Hardest 20 % úloh | API |

**Doporučená výchozí kombinace:** Qwen3-Coder-480B (agentic default) + GLM-4.7 (chat/lehčí úlohy) + Codestral 25.08 (inline autocompletion) + Claude Opus (escalation).

**Pozor — EU AI Act enforcement 2. 8. 2026:** Modely čínského původu (Qwen, DeepSeek, GLM, Kimi) vyžadují interní zdůvodnění (security review, hash verifikace vah z HF, plně air-gapped runtime). Provenance compliance je řešitelná, ale ne automatická — počítat s 4-6 týdny právního review.

---

## 5. Scénáře hostingu — srovnání

Všechny ceny v USD/měsíc, EU jurisdikce, 400 vývojářů, ~50-60 souběžných agentic sessions v peaku, ~3.2B tokenů/den celkem (z toho ~30-60M output, ~85-95 % input cached při Claude Code-style workloadu).

### Scénář A — EU Serverless API (Nebius Token Factory + Mistral)

**Co to je:** Plně managed pay-per-token. Žádný hardware, žádný MLOps, OpenAI-compatible endpoint, EU region (Finsko/Nizozemsko). Nebius je jediný EU hyperscaler, který serveruje plné trillion-param modely (Qwen3-Coder-480B, DeepSeek-V3, Kimi K2, GLM) OOTB. Doplňkově Mistral La Plateforme (FR) pro Codestral inline.

| Položka | $/měs |
|---|---|
| Nebius Token Factory — Qwen3-Coder-480B ($0.22 in / $0.90 out), ~2 B tokenů vstup (80% cache), 30 M tokenů output | $8-12k |
| Mistral Codestral inline (~10 M output tokenů/den) | $1-2k |
| Anthropic Opus / OpenAI GPT-5 (escalation, 20% hard tasks) | $4-7k |
| AI Gateway hosting (1× server + monitoring) | $0.5k |
| **Celkem** | **~$14-22k/měs** |
| CapEx | **$0** |
| Time-to-launch | **2-4 týdny** |

**Pro:** Nulový operational risk; okamžitý start; škáluje na 0; ideální pro pilot; **levnější než váš dnešní spend**.
**Proti:** Sovereignty je "EU jurisdikce + DPA" (silné, ale ne plně air-gapped); per-token cena škáluje s růstem; throughput SLA závisí na tieru; menší schopnost fine-tuningu.
**DORA posture:** Solidní (Nebius má ISO 27001 + DORA addendum na enterprise tieru, Mistral má FR jurisdikci + plné DPA). Audit a CNB review by měly projít.

### Scénář B — Dedikované GPU u EU provideru (Nebius reserved / OVHcloud HGX)

**Co to je:** Pronajatý bare-metal nebo VM 8×H200 cluster, vy ho operujete (vLLM/SGLang), provider dodává HW + síť + DC. Reserved discount 30-50 %. **Nejlepší balanc pro vás (medium MLOps + 6-9 mes. timeline).**

Doporučení: **Nebius reserved (FI Mäntsälä, NL)** primární, **OVHcloud HGX (FR Roubaix, PL Warszawa)** sekundární. OVHcloud má **SecNumCloud + ISAE 3402 + explicitní DORA exit klauzule** — nejlepší banking-grade kontrakt v EU.

| Položka | $/měs |
|---|---|
| 4× 8×H200 reserved 12-měs (Nebius @ ~$5.4k/node) | $22k |
| Storage, sítě, monitoring, gateway, ops | $4k |
| Externí MLOps konzultanti (částečný úvazek) | $4k |
| Anthropic Opus / OpenAI GPT-5 (escalation) | $4-7k |
| **Celkem** | **~$34-37k/měs** |
| CapEx | **$0** |
| Time-to-launch | **6-10 týdnů** |

**Pro:** Plná kontrola nad modelem (fine-tuning, custom routing), žádný vendor lock-in na úrovni vah, predictable pricing, EU jurisdikce, žádný CapEx. Pokud spend poroste, marginalní cost je téměř nula (kapacita je fixní).
**Proti:** Vyšší fixní cost než Scénář A při nízkém využití; vyžaduje MLOps schopnost (částečně řešeno externí pomocí); SLA na hardware = závazek od poskytovatele, ne od vás.
**DORA posture:** Velmi silná u OVHcloud (SecNumCloud); silná u Nebius (ale potřeba review NL/FI jurisdikce). Audit-friendly.

### Scénář C — On-prem (4× 8×H200 v Praze nebo brněnském DC)

**Co to je:** Vlastní hardware ve vlastním (nebo colocation) DC. Maximální svrchovanost. Air-gapped možný. **Pro 6-9 měsíční pilot timeline je napjatý** (lead-time H200 8-12 týdnů + commissioning 4-6 týdnů), ale realizovatelný pokud objednávka jde do června 2026.

| Položka | 3-letá TCO | Měs. amortizováno (5 let) |
|---|---|---|
| 4× HGX H200 8-GPU servery (~$420k/ks) | $1.7M | $28k |
| Sítě (InfiniBand NDR), storage, řízení | $200k | $3.3k |
| Colo Praha (~40 kW @ €180/kW/měs all-in) | $250k | $4k |
| Power (~40 kW × 1.34 PUE × €0.15 × 8760) | $200k | $3.3k |
| NVIDIA AI Enterprise + HW support | $480k | $8k |
| Spares, MLOps staffing alokace | $320k | $5.4k |
| Anthropic/OpenAI escalation | – | $4-7k |
| **Celkem 3-letá TCO** | **~$3.15M** | **~$56-60k/měs** |
| **Stejné, 5-letá TCO** | **~$3.5M** | **~$48-52k/měs** |
| CapEx prvních 6 měsíců | **~$2.0M** | – |
| Time-to-launch | **4-7 měsíců** | – |

**Pro:** Maximální sovereignty (full air-gap možný), nejlepší pro DORA/CNB review, po roce 5 marginalní náklady ~$15-20k/měs (jen power+colo+escalation), strategická aktiva. Možnost spustit i tréninkové úlohy (fine-tuning na interní codebase).
**Proti:** Vysoký CapEx upfront ($2M), inflexibilita (těžké škálovat dolů), HW lead-time + commissioning posunou go-live blíž Q1 2027 ne Q4 2026, vyšší MLOps zátěž (refresh cyklus za 3-4 roky).
**Hedge tip:** Rezervovat 1-2 nody **HGX B200** (delivery Q4 2026/Q1 2027) jako next-gen refresh, pokud poptávka poroste.

### Scénář D — Hyperscaler EU region (AWS Bedrock / Azure / GCP)

**Co to je:** Cloud-native, EU region, ale **US-vlastněný provider**.

| Položka | $/měs |
|---|---|
| AWS P5 / Azure ND-H100-v5 / GCP A3 Mega (4× 8×H100 ekvivalent) | $120-180k |
| Bedrock/OpenAI per-token alternativa | $20-40k |
| Anthropic/OpenAI escalation | $4-7k |
| **Celkem** | **~$25-200k/měs (záleží na modelu)** |

**Pro:** Pohodlí, integrace s existující cloud infrastrukturou, snadný start.
**Proti:** **CLOUD Act se aplikuje i na ESC (AWS European Sovereign Cloud)** — internal audit a CNB to označí jako residual sovereignty risk. Cena na bare-metal je 3-5× horší než EU specializované providery. **Nedoporučeno jako primární** — pouze pokud máte existující enterprise commitment (např. Azure pro celý zbytek firmy).

---

## 6. Konsolidované rozpočtové srovnání

Časový horizont: **3 roky**, kumulativní náklady.

| Scénář | Měs. cost | 3-letá TCO | vs dnešní spend ($30k baseline) | vs trajektorie ($90k za 12 měs.) |
|---|---|---|---|---|
| **Dnes (jen Claude+Codex)** | $30k → $90k | $1.5-2.5M | – | – |
| **A. EU Serverless (Nebius+Mistral)** | $14-22k | $0.6-0.8M | **−40 až −50 %** | **−75 až −80 %** |
| **B. Dedikované GPU (Nebius/OVH reserved)** | $34-37k | $1.2-1.3M | +15 % | **−55 až −60 %** |
| **C. On-prem 4× 8×H200** | $48-60k amort. + $2M CapEx upfront | $3.0-3.5M | +60 až +100 % | **−15 až −40 %** |
| **D. Hyperscaler EU** | $25-200k | $1-7M | mix | mix |

**Klíčový insight:** Pokud váš spend zůstane na $30k/měs, **on-prem se nevyplatí** — Scénář A nebo B vyhrají. Pokud spend roste podle trajektorie ke $90k+/měs (což sám očekáváte), pak **on-prem začíná dávat smysl od 18-24 měsíců**, ale Scénář B (dedikovaný GPU rental) je stále velmi konkurenceschopný a flexibilnější.

---

## 7. Doporučená cesta (fázovaná)

### Fáze 1 — Pilot (Q3-Q4 2026, ~3 měsíce, ~$40-60k total)

- **Scénář A**: Nebius Token Factory + Mistral La Plateforme + LiteLLM gateway na 1 EU VM
- 20-50 vývojářů (různé týmy, různé use-cases: backend, frontend, infra)
- Sběr metrik: tokeny/dev/den, cache hit rate, SWE-Bench na interních úlohách, NPS, % úloh eskalujících na Opus
- Paralelně: HW kapacity plan + RFP pro Scénář B (Nebius/OVHcloud reserved), legal review čínských modelů (EU AI Act 2. 8. 2026)

**Výstup pilotu:** Rozhodnutí Scénář B vs C, finální výběr modelového mixu, throughput sizing pro production.

### Fáze 2 — Produkce (Q1 2027, rollout 400 dev)

**Doporučení: Scénář B (Nebius reserved 4× 8×H200, FI)** s OVHcloud (Roubaix) jako sekundárním regionem pro DR.

- Kontrakt 12-24 měsíců reserved
- Vlastní AI gateway v EU VPS (Praha, Hetzner/OVH)
- vLLM pro Qwen3-Coder-480B + Codestral; SGLang pro DeepSeek/Kimi (A/B)
- Prefix-cache aware routing, EAGLE-3 speculative decoding
- DORA-ready audit log, retention 6 let
- Hybrid routing: 70-80 % sovereign, 20-30 % Anthropic/OpenAI

**Měs. budget:** ~$35k stabilní (vs trajektorie $80-100k+ pure-commercial). **Roční úspora $400-700k.**

### Fáze 3 — Vyhodnocení on-prem (Q3 2027)

Po 6-9 měsících production na Scénáři B vyhodnotit, jestli on-prem (Scénář C) dává smysl. Tehdy bude:
- Lepší ekonomika H200/B200 (refresh ceny klesly)
- Reálná data o utilizaci, ne odhady
- Možnost pre-objednat B300 NVL nebo Rubin generation

Pokud spend na Scénáři B přesáhne $50k/měs stabilně, on-prem začíná dávat finanční smysl + posiluje DORA posture.

---

## 8. Alternativy, pokud ceny porostou / něco selže

| Riziko | Mitigace |
|---|---|
| Anthropic/OpenAI zdraží escalation tier 2× | Snížit eskalaci ze 30 % na 15 %, posílit GLM-4.7/Kimi K2.6 jako "near-frontier" |
| Nebius / EU API zdraží | Migrace na dedikovaný GPU rental (Scénář B) — Nebius i OVHcloud nabízejí stejnou cestu, **váhy modelů máte vždy s sebou** |
| EU AI Act zakáže čínské modely | Přepnout primární na Llama 4-Coder (až vyjde) + Codestral; degradace SWE-Bench ~5-10 bodů |
| OVHcloud / Nebius má výpadek | Multi-region: primary Nebius FI, secondary OVHcloud FR (oboje schopni serverovat stejné Qwen/DeepSeek), gateway routuje automaticky |
| Vývojáři nepřijmou kvalitu sovereign modelu | Zvýšit % eskalace na Opus pro nespokojené týmy, zachovat Claude Code Max licence jako fallback (degradace, ne nahrazení) |
| MLOps team nestíhá | Posílit externí kontrakt (Nebius/OVHcloud nabízejí managed inference); ve worst case rollback na čistý Scénář A |
| Trh GPU zkolabuje a Blackwell/Rubin výrazně zlevní | Plánovaný refresh 2028 — Scénář B umožňuje migraci bez sunk-cost (žádný CapEx) |

**Klíčové principy:**
1. **Váhy modelů jsou portovatelné** — pokud máte Qwen3-Coder-480B stažený, můžete přejít mezi Nebius / OVHcloud / on-prem za týdny, ne měsíce.
2. **Gateway je vaše vlastní** — vendor lock-in je minimální (LiteLLM open-source).
3. **Hybrid znamená graceful degradation** — pokud sovereign selže, eskalace na Anthropic je transparentní pro vývojáře.

---

## 9. Kritické položky k vybudování (pre-pilot)

| # | Co | Kdo | Kdy |
|---|---|---|---|
| 1 | AI Gateway (LiteLLM + audit + per-user budgets) | Platform team | Týdny 1-3 |
| 2 | Nebius enterprise kontrakt + DPA review | Procurement + Legal | Týdny 1-4 |
| 3 | Legal review čínských modelů (Qwen/DeepSeek/GLM/Kimi) vs EU AI Act 2.8.2026 | Legal + Security | Týdny 1-6 |
| 4 | Hash-verifikace vah z Hugging Face (supply-chain integrity) | Security | Týden 4 |
| 5 | Pilot rollout (Claude Code config → gateway endpoint) pro 20-50 dev | DevEx | Týdny 4-6 |
| 6 | Metrics dashboard (per-dev tokeny, cache hit, NPS, escalation %) | Platform team | Týden 6 |
| 7 | RFP pro Scénář B (Nebius / OVHcloud / DataCrunch reserved) | Procurement | Týdny 6-10 |
| 8 | DORA risk assessment pro sovereign stack | Compliance | Týdny 8-12 |

---

## 10. Verifikace (jak otestovat end-to-end)

**Pilot validation kritéria:**

1. **Kvalita** — sovereign model dokáže obsloužit ≥70 % denních úloh bez nutnosti eskalace na Opus. Měřeno: % requestů, kde dev manuálně přepne na Claude Opus po prvním pokusu Qwen/GLM.
2. **Latence** — P50 TTFT ≤ 800 ms, P50 decode ≥ 30 tok/s/user. Měřeno: gateway metrics.
3. **Throughput** — Cluster zvládne 50+ souběžných agentic sessions bez degradace. Měřeno: load test (vLLM `--benchmarks`).
4. **Cost** — Měsíční náklad pilotu (20-50 dev) extrapolován na 400 dev je ≤ 50 % současného Claude+Codex spendu. Měřeno: Nebius invoice + LiteLLM cost tracking.
5. **SWE-Bench na interních úlohách** — Tým připraví 50 reprezentativních úloh z reálných PRs, spustí přes sovereign vs Opus, hodnotí kvalitu blind reviewem.
6. **Cache hit rate** — Target ≥ 70 % na production workloadu (klíčový ekonomický KPI).
7. **DORA audit trail** — Compliance ověří, že 100 % requestů má kompletní záznam (user, prompt hash, model, timestamp, cost, EU region).

**Go/no-go rozhodnutí na konci pilotu:** Pokud všech 7 kritérií ✓ → Fáze 2 (production). Pokud 1-2 selžou → iterace na pilotu. Pokud ≥ 3 selžou → reset, znovu evaluovat model mix.

---

## 11. Otevřené otázky pro finalizaci

- **Skutečný současný spend** — pokud máte exportované invoices z Anthropic/OpenAI z posledních 3 měsíců, zpřesní to baseline pro ROI kalkulaci (vyšel jsem z $30k mid-point, ale realistická čísla mohou změnit ekonomiku Scénáře C vs B).
- **Datacenter preference** — Praha vs Frankfurt vs Helsinki ovlivní výběr providera (Nebius je primárně FI/NL, OVHcloud má FR/PL, ale ne CZ).
- **Banking-specific compliance review** — kdo vlastně určuje (CNB?), jestli "EU residency v Nizozemsku" stačí, nebo je preference "EU residency v ČR".
- **Existující framework smlouvy** — pokud již máte enterprise vztah s některým z hyperscaler (AWS/Azure/GCP), může to změnit ekonomiku Scénáře D.

---

## 12. Next actions po schválení směru

Tento dokument je **strategický návrh, ne implementace**. Pokud souhlasíte:

1. Vytvořit nový repo `finshape/sovereign-ai-gateway` s LiteLLM základem (Apache 2.0)
2. Vytvořit dokument `docs/sovereign-ai/RFC-001-pilot-architecture.md` v `finshape-financial-intelligence` (nebo dedikované compliance repo)
3. Iniciovat procurement workflow s Nebius + OVHcloud (paralelně, 2 nabídky)
4. Iniciovat legal review (EU AI Act + DORA addendum pro každý zvažovaný model)

Implementační detaily a kód budou předmětem samostatných tiketů a PR po schválení směru.

---

## Zdroje a podklady

- Modely a benchmarky: SWE-Bench Verified leaderboard, Qwen/Hugging Face, DeepSeek HF, GLM HF, Kimi K2.6 release notes, Codestral 25.08 announcement
- EU providers: Nebius Token Factory pricing, OVHcloud AI Endpoints + HGX bare-metal, Scaleway/IONOS/Mistral La Plateforme pricing pages
- Inference performance: vLLM/SGLang docs, DeepSeek-V3 H100/H200 benchmark studies, EAGLE-3 / MTP speculative decoding production data
- Hardware ceny + lead-times: Jarvislabs H100/H200 guides, SemiAnalysis Blackwell shipment, ServeTheHome Gaudi3
- Colocation Praha: TTC Teleport, Voxility, DataCenterHawk EU 2026 fundamentals
- Regulační: IAPP DORA+GDPR guide, EU AI Act enforcement timeline (2. 8. 2026), AWS ESC sovereignty assessment

Vizuální shrnutí: viz [`sovereign-ai-strategy.html`](./sovereign-ai-strategy.html) (samostatná HTML stránka s grafy — otevřete v prohlížeči).
