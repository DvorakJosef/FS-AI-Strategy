# Sovereign AI — analýza a návrh pro Finshape (~700 lidí, ~500 vývojářů, banking software)

> Verze: 2026-05-14 (v4 — full TCO včetně lidské práce, CZ-realistic) · Strategický návrh pro diskuzi s vedením, procurementem, compliance a CFO

> **v3 → v4 update:** v3 počítala jen infrastructure cost (Nebius/OVHcloud/HW), ne lidskou práci.
> Po dotazu uživatele doplněna sekce 5.5 s plnou TCO včetně FTE a transition costu, kalibrováno na CZ trh
> (~$95-130k/rok fully-loaded senior engineer v Praze, ne $150k+ US/west-EU). Tím se ekonomika výrazně mění:
> **Scénář A není okamžitá úspora, je to investice s ROI 12-24 měsíců.** Strategická hodnota (sovereignty,
> vendor independence, DORA compliance) zůstává; cost-only argument je slabší než v3 implikovala.

---

## 1. Context

**Proč to děláme:** Současný coding stack (Claude Code Team/Max + OpenAI ChatGPT Codex Enterprise pro ~400 vývojářů, ~120 z toho Codex Enterprise) má čtyři dlouhodobé tlaky:

1. **Regulace (DORA, GDPR, ČNB)** — banking software vyžaduje data residency v EU, kontrolu nad third-party dependencies, plný audit trail. Anthropic/OpenAI = US providers s CLOUD Act expozicí.
2. **Kontrola nákladů (revidováno v4)** — současný spend ~$350-450k/rok (~$30-37k/měs, ~$70-95/seat/měsíc). Sovereign infrastruktura je levnější (~$170-260k/rok pro Scénář A), ALE po započtení lidské práce (1-2 FTE platform/MLOps, harness adaptace, transition productivity tax) se rok 1 sovereignu **vyrovná baselineu nebo je mírně dražší**. Reálná úspora ~$25-195k/rok nastává od roku 2+. Detail v sekci 5.5.
3. **Nezávislost na vendorech** — strategická obrana proti zdražování, změnám politik, výpadkům.
4. **Customizace a IP** — fine-tune na interní codebase, doménové znalosti bankingu.

**Cíl:** Hybridní architektura, kde **sovereign open-weight stack pokryje 70-80 % denní coding rutiny**, zatímco **Claude Opus / GPT-5 zůstanou pro nejtěžších 20-30 %**. Sovereign jako default, frontier proprietary jako escalation.

**Časový horizont:** Fáze 0 strategic decision Q3 2026, Pilot Q4 2026 (15-30 vývojářů), produkční rollout Scénáře A Q1-Q2 2027 (~400 dev), Scénář B podle T-B triggeru (Q4 2027 - 2028).

---

## 2. Současný stav (baseline)

| Položka | Hodnota |
|---|---|
| Roční subscription spend (2026-05-14) | **~$350-450k / rok ≈ $30-37k / měs** |
| Implicitní lidská práce (seat management, billing) | ~0.1-0.2 FTE ≈ $10-20k/rok |
| **Baseline full TCO** | **~$360-470k/rok** |
| Počet aktivních AI uživatelů | ~400 |
| Průměr na seat | ~$70-95 / seat / měsíc |
| Mix licencí (orientačně) | ~120 Codex Enterprise + ~280 Claude Team/Pro + subset Claude Code Max |
| 12-měsíční pesimistický odhad bez akce | ~$500-700k / rok ($42-58k / měs) |

**Klíčové implikace:**
- $70-95/seat/měsíc průměr značí, že významná část týmu je už dnes na premium tier.
- Sovereign **infra** je dnes levnější (~$170-260k/rok pro Scénář A), ale **full TCO včetně FTE** je rovnocenné v rok 1.
- Reálná cost benefit přichází v rok 2+ (~$25-195k/rok úspora, mid-point ~$110k).
- Strategická hodnota (sovereignty, DORA, vendor independence) je hlavní argument; čistý cost-saving je sekundární.

---

## 3. Cílová architektura (hybrid Sovereign AI)

```
┌────────────────────────────────────────────────────────────────┐
│ ~400 vývojářů (Cline / Roo / Aider / opencode / Crush)         │
│ (transition z Claude Code → open-source harness — viz sekce 5.5)│
└──────────────────────────┬─────────────────────────────────────┘
                           │ OpenAI-compatible API
                ┌──────────▼──────────┐
                │   AI Gateway        │  ← LiteLLM
                │   (Praha/EU, vlastní)│  ← auth, audit log, routing
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

**Klíčové vlastnosti:**
- OpenAI-compatible endpoint → ostatní harness fungují bez Claude Code
- Per-user / per-team budgety, audit log pro DORA
- Routing rules per task type (inline → Codestral, agent → Qwen, chat → GLM)
- Centralizovaný prefix cache (RadixAttention 70-95 % hit)

---

## 4. Doporučený model mix

| Tier | Model | Licence | Role | Hardware (FP8) |
|---|---|---|---|---|
| **Frontier sovereign (default)** | **Qwen3-Coder-480B-A35B** | Apache 2.0 ✓ | Agentic coding default | 8×H100/H200, ~250 GB FP8 |
| Frontier sovereign (alt) | DeepSeek V4-Pro (1.6T/49B) | MIT ✓ | A/B; SWE-Bench 80.6 | 8×H200/B200, ~800 GB FP8 |
| Long agent loop | Kimi K2.6 (1T/32B) | Modified MIT ⚠️ | 300 sub-agents | 8×H200/MI300X |
| Cost-optimized primary | GLM-4.7 (355B/32B) | MIT ✓ | Chat & lehčí úlohy | 4×H100 AWQ |
| Cheap/fast (inline) | **Qwen3-Coder-Next (3B aktivních)** | Apache 2.0 ✓ | Autocompletion | 1×L40S / A100 |
| Cheap/fast (EU sov+) | **Codestral 25.08** | Mistral Commercial | FIM, FR jurisdikce | 1×H100 |
| Frontier proprietary | Claude Opus 4.7, GPT-5/Codex | komerční | Hardest 20 % úloh | API |

**Doporučená výchozí kombinace:** Qwen3-Coder-480B + GLM-4.7 + Codestral 25.08 + Claude Opus escalation.

**EU AI Act enforcement 2. 8. 2026:** Modely čínského původu vyžadují interní zdůvodnění (security review, hash verifikace vah z HF, plně air-gapped runtime). 4-6 týdnů právního review.

---

## 5. Scénáře hostingu — infrastructure-only srovnání

(Lidská práce a transition cost jsou v sekci 5.5.)

### Scénář A — EU Serverless API (Nebius Token Factory + Mistral)

| Položka | $/měs |
|---|---|
| Nebius Token Factory — Qwen3-Coder-480B + Kimi K2.6 + GLM (~2 B tokenů vstup 80% cache, 30 M output) | $8-12k |
| Mistral Codestral inline (~10 M output tokenů/den) | $1-2k |
| Anthropic Opus / OpenAI GPT-5 (escalation, 20% hard tasks) | $4-7k |
| AI Gateway hosting | $0.5k |
| **Celkem infra** | **~$14-22k/měs ≈ $170-260k/rok** |
| CapEx | **$0** |
| Time-to-launch | **2-4 týdny** |

**Pro:** Nulový operational risk; okamžitý start; škáluje na 0; ideální pro pilot.
**Proti:** "EU jurisdikce + DPA" sovereignty (silné, ale ne plně air-gapped); per-token cena škáluje s růstem.

### Scénář B — Dedikované GPU (Nebius reserved / OVHcloud HGX)

| Položka | $/měs |
|---|---|
| 4× 8×H200 reserved 12-měs (Nebius @ ~$5.4k/node) | $22k |
| Storage, sítě, monitoring, gateway, ops | $4k |
| Externí MLOps konzultanti (částečný úvazek, podpora interní MLOps) | $4k |
| Anthropic Opus / OpenAI GPT-5 (escalation) | $4-7k |
| **Celkem infra** | **~$34-37k/měs ≈ $410-440k/rok** |
| CapEx | **$0** |
| Time-to-launch | **6-10 týdnů** |

**Pro:** Plná kontrola, fine-tuning, EU jurisdikce, žádný CapEx, strop ceny při růstu.
**Proti:** Při nízkém využití dražší než A; vyžaduje MLOps FTE.

### Scénář C — On-prem (4× 8×H200 v Praze)

Stejné jako v3: ~$3.15M 3-letá TCO, +$2M CapEx upfront. **Vyplatí se až při $1M+/rok stabilním baselineu.**

### Scénář D — Hyperscaler EU

**Nedoporučeno** kvůli CLOUD Act expozici.

---

## 5.5 Lidská práce & transition cost (CZ-realistic) — NOVÉ v4

Čísla v sekci 5 jsou **infrastructure-only**. Reálná TCO musí zahrnovat:
(1) FTE pro provoz, (2) jednorázovou harness adaptaci (přechod Claude Code → open-source), (3) change management & training pro 400 dev, (4) productivity tax během transition.

### 5.5.1 Kalibrace mzdových sazeb (Praha, banking software, 2026)

Senior engineer v Praze, fully loaded (gross + ~34 % payroll taxes + benefits + overhead):

| Role | TC gross/rok | Fully loaded náklad zaměstnavatele |
|---|---|---|
| Senior platform / DevOps engineer | ~€70-85k | **~$95-115k/rok** |
| Senior MLOps engineer (CZ premium, malý talent pool) | ~€85-100k | **~$115-130k/rok** |
| Senior DevEx engineer | ~€60-75k | **~$80-100k/rok** |
| Senior backend developer | ~€65-80k | **~$90-110k/rok** |
| Hourly fully loaded (interní senior) | — | **~$50-58/h** |
| Externí konzultant senior MLOps | 2000-3000 CZK/h | **~$85-130/h** |
| Externí konzultant senior platform | 1500-2500 CZK/h | **~$65-105/h** |

Fully-loaded CZ senior engineer = ~60-75 % US/west-EU ekvivalentu.

### 5.5.2 Co se musí udělat při přechodu Claude Code → open-source harness

Claude Code je proprietary CLI šitý Anthropicem na Claude modely. Sovereign cesta vyžaduje:

| Komponenta | Co | Effort |
|---|---|---|
| **Harness volba/fork** | Cline / Roo / Aider / opencode / Crush — vybrat + případně forknout. Žádný open-source harness není 1:1 ekvivalent Claude Code (chybí MCP, hooks, subagent dispatch, slash commands). | 80-200 h |
| **System prompts adaptace** | Claude má svá specifika (XML thinking, tool_use). Qwen3-Coder má harmony format, GLM-4.7 má jiný tool-call template. Per model. | 120-300 h |
| **Tool-use plumbing** | Transformace mezi modely. Edge cases: parallel calls, error recovery. | 100-200 h |
| **Diff aplikace + file mgmt** | Claude Code má robust diff engine. Open-source alternativy mají jiná chování. | 60-150 h |
| **MCP integrace** | Claude Code má MCP servery. Open-source většinou ne. | 100-250 h |
| **Slash commands, hooks, subagents** | Claude Code feature. Vlastní implementace. | 60-150 h |
| **Evaluation suite** | Internal SWE-Bench (50 reálných úloh) + regression testing. | 80-150 h |
| **Pre-prod integrace** | PR review, CI hooks, linting workflows. | 40-100 h |
| **Celkem harness adaptace** | | **~640-1500 h** |

Mix interní (~$55/h) + externí (~$95/h) v poměru 60/40 → **~$45-115k jednorázové, plus 0.2-0.3 FTE údržba** (model updates, breaking changes upstream).

### 5.5.3 FTE allocation per scénář

| Role | Scénář A | Scénář B (po T-B) | Scénář C (po T-C) |
|---|---|---|---|
| Platform engineer (gateway, monitoring, billing) | 0.5-1.0 FTE | 1.0 FTE | 1.0 FTE |
| MLOps engineer (vLLM/SGLang, model serving) | 0.0-0.2 FTE (serverless) | 1.0 FTE | 1.5 FTE |
| DevEx engineer (harness, training, support) | 0.5 → 0.25 FTE | 0.25 FTE | 0.25 FTE |
| DC ops / HW lifecycle | 0 | 0 | 0.5-1.0 FTE |
| **Total FTE ongoing (rok 2+)** | **~0.75-1.45 FTE** | **~2.25 FTE** | **~3.25-4.25 FTE** |
| **Roční náklad CZ rates (mid-point)** | **~$80-150k/rok** | **~$240-260k/rok** | **~$355-475k/rok** |

Část lze absorbovat existujícím platform/DevOps týmem, část vyžaduje nový headcount:
- Scénář A: 0.5 absorbováno + 0.5 nový headcount = ~$50-70k nový roční náklad
- Scénář B: + 1.0 FTE MLOps premium = ~+$115-130k nový roční náklad
- Scénář C: + 1-2 FTE DC ops = ~+$200k nový roční náklad

**CZ talent pool risk:** Senior MLOps s vLLM/SGLang/CUDA expertise je v ČR vzácný. Hiring 6-9 měs. + ramp-up 3-6 měs. = 9-15 měs. od decision do plné produktivity. Krátkodobě externí konzultanti ($85-130/h).

### 5.5.4 Change management & training

Rollout na 400 dev:
- DevEx + Platform 200-400 h × $55/h interní = ~$11-22k
- Externí materiály, workshop: ~$5-10k
- Internal champions program (10-15 vývojářů): absorbováno
- **Total change management jednorázové: ~$15-35k**

### 5.5.5 Productivity tax během transition

- Realistic: 400 dev × 5 % × 10 týdnů × 40 h × $52/h = **~$42k**
- Worst case: 400 dev × 10 % × 14 týdnů × 40 h × $52/h = **~$117k**
- Best case (smooth rollout): **~$15-30k**
- **Realistický range: $40-100k jednorázové**

Pilot ve Fázi 1 (15-30 dev) tento risk redukuje.

### 5.5.6 Plná TCO (CZ kontextu)

**Scénář A — rok 1 (transition):**

| Položka | Náklad |
|---|---|
| Infrastructure (Nebius + Mistral + escalation) | $170-260k |
| Platform FTE (0.5-1.0, mix nový + absorbováno) | $50-115k |
| DevEx FTE 0.5 (jen rok 1) | $40-50k |
| Harness adaptace (jednorázové) | $45-115k |
| Change management & training (jednorázové) | $15-35k |
| Productivity tax (jednorázové) | $40-100k |
| **Celkem rok 1** | **~$360-675k** |

**Scénář A — rok 2+ (ongoing):**

| Položka | Náklad |
|---|---|
| Infrastructure | $170-260k |
| Platform FTE 0.5-1.0 | $50-115k |
| DevEx FTE 0.25 | $20-25k |
| Harness maintenance (0.2 FTE) | $15-25k |
| **Celkem rok 2+** | **~$255-425k/rok** |

vs baseline $360-470k/rok full TCO:
- **Rok 1: rovnocenné až mírně dražší** (-$110k až +$315k vs baseline)
- **Rok 2+: úspora ~$25-195k/rok** (mid-point ~$110k/rok)
- **3-letá TCO Scénáře A: ~$870-1525k**, vs baseline $1080-1410k → break-even ke 3 rokům

**Scénář B — ongoing (po T-B):**

| Položka | Náklad |
|---|---|
| Infrastructure (Nebius/OVHcloud reserved) | $410-440k |
| Platform FTE 1.0 | $100-115k |
| MLOps FTE 1.0 (CZ premium, nový headcount) | $115-130k |
| DevEx FTE 0.25 | $20-25k |
| Harness/eval maintenance (0.3 FTE) | $25-30k |
| **Celkem ongoing rok 2+** | **~$670-740k/rok** |

vs baseline: **vyplatí se jen pokud spend by jinak rostl ke $700-900k/rok**. Pokud baseline stagnuje, B = sovereignty premium ~$220-380k/rok.

### 5.5.7 Co tahle ekonomika znamená pro doporučení

Strategický argument zůstává:
- DORA compliance, vendor independence, banking IP customization = strategická hodnota, kterou cost-only TCO nezachycuje
- Skrytá rizika baseline (rate-limit produktivita, vendor concentration) přidávají kvantifikovatelné ~$200-500k/rok rizika
- Sovereign dává zastropování při budoucím růstu (1M+ subscription scenarios)

Cost-only argument je slabší než v3 implikovala:
- "Úspora ~$130-200k/rok" z v3 platila jen pro infrastructure
- **Rok 1: cost-neutral nebo mírná investice** (~$0-300k)
- **Rok 2+: úspora ~$25-195k/rok** (mid ~$110k)
- **ROI break-even: 12-24 měsíců**

**Pro stakeholdery: toto NENÍ cost-saving move; je to strategický posun s mírnou cost benefit v dlouhodobém horizontu.** Pokud chcete čistou úsporu rychle, sovereign není nástroj. Pokud chcete sovereignty + dlouhodobou nezávislost + odolnost vůči AI vendor turbulencím, sovereign dává smysl i s touto upravenou TCO.

---

## 6. Break-even analýza — full TCO včetně lidské práce (v4)

**Výchozí stav:** baseline full TCO ~$360-470k/rok ($350-450k subscription + ~$10-20k implicit FTE).

| Scénář | Rok 1 (s transition) | Rok 2+ ongoing | 3-letá TCO | vs baseline ($410k) |
|---|---|---|---|---|
| **A. EU Serverless** | ~$360-675k | **~$255-425k/rok** | **~$870-1525k** | Rok 1 ≈ stejné, rok 2+ úspora ~$25-195k/rok |
| **B. Dedikovaný GPU rental** | ~$700-800k | **~$670-740k/rok** | **~$2.0-2.3M** | Dražší o $220-390k/rok (vyplatí se jen při růstu) |
| **C. On-prem (5-letá amort.)** | + $2M CapEx | ~$935-1100k/rok | $4.9M + $2M | Jen při $1M+/rok stabilním baselineu |
| **D. Hyperscaler EU** | mix | mix | mix | ❌ CLOUD Act |

### 6.1 Break-even body

| Akce | Spustit když | Logika |
|---|---|---|
| **A → spuštění** | Spend ≥ $350k/rok **A** ochota investovat ~$0-300k v roce 1 pro úsporu $25-195k/rok od roku 2+ **A/NEBO** strategická hodnota sovereignty/DORA/vendor independence | Cost-only: rok 1 ≈ break-even, rok 2+ úspora; ROI 12-24 měs. |
| **A → B přechod** | Spend roste ke $700k+/rok subscription **NEBO** Scénář A nestačí kapacitně **NEBO** fine-tuning vyžadován | B je dražší než A (~+$400k/rok), vyplatí se jen při růstu nebo strategickém benefitu |
| **B → C přechod** | Spend na Scénáři B by přesáhl $1M/rok **A** Scénář B utilizace 75 %+ | On-prem TCO ~$935-1100k/rok |

### 6.2 Sensitivity — růstové scénáře (full TCO)

| Trajektorie subscription baseline | Subscription | Scénář A rok 2+ | Optimální |
|---|---|---|---|
| Stagnuje | $350-450k | $255-425k | **A** úspora $25-195k/rok + sovereignty |
| Mírný růst | $500-600k | $275-450k | **A** úspora $150-300k/rok |
| Silný růst | $700-900k | $350-550k | **A** úspora $350-500k/rok, **B** úspora $0-200k/rok |
| Extrémní | $1M+ | $500-700k | **B** dává smysl (kapacita zastropována) |

### 6.3 Sensitivity — co když Anthropic/OpenAI zdraží

| Zdražení (2 roky) | Subscription | Scénář A ongoing | Závěr |
|---|---|---|---|
| +20 % (inflace) | $420-540k | $255-425k | **A** úspora $0-285k/rok |
| +50 % (Max → $150) | $525-675k | $275-450k | **A** úspora $75-400k/rok |
| 2× (politická change) | $700-900k | $300-475k | **A** silně vyhrává, **B** rovnocenný |

### 6.4 Skrytá rizika baseline

- **DORA non-compliance cost** — pokud current stack neprochází DORA, remediace může přidat $50-150k/rok jen na compliance overhead. Sovereign řeší strukturálně.
- **Rate limit & throttling cost** — vývojáři ztrácejí čas, když Max hit limit. 400 dev × 5 % limit-affected × 30 min/den × $52/h fully loaded ≈ ~$200-400k/rok ztracené produktivity.
- **Vendor concentration risk** — pokud Anthropic změní enterprise terms (např. omezí Czech banking sector), migrace s sovereign = týden. Bez sovereign = měsíce + productivity loss.

---

## 7. Decision triggers — kdy aktivovat kterou fázi (v4)

| Trigger | Status k 2026-05-14 | Akce |
|---|---|---|
| **T-A: Spustit Scénář A (pilot + rollout)** | ⚖️ **Strategic decision** — cost-only argument slabý (rok 1 break-even, rok 2+ úspora ~$25-195k/rok). Spouštět když: (a) sovereignty/DORA hodnota stojí za ~$0-300k rok-1 investici **NEBO** (b) trajektorie spendu míří ke $500k+ rychle | Pokud go: pilot 15-30 dev Q4 2026, rollout Q1-Q2 2027 |
| **T-B: Přejít na Scénář B** | ⏳ 18-30 měs. (později než v3 odhad — full TCO B výrazně dražší) | RFP a kontrakt-ready hned, aktivace jen při růstu nebo strategickém benefitu |
| **T-C: Aktivovat Scénář C (on-prem)** | ⏳ Nepravděpodobné v 36 měs. | Vyhodnotit 2028+ jen pokud spend $1M+/rok stabilně |
| **T-reg: Regulační vynucení** | ❓ Vyžaduje DORA gap assessment — prioritní úkol Fáze 0 | Pokud T-reg padne, cost-only logika přestává platit |

---

## 8. Doporučená cesta (fázovaná, v4)

### Fáze 0 — Strategic decision + DORA assessment (Q3 2026, 6-8 týdnů, ~$15-25k)

Před spuštěním pilotu mít strategickou jasno:
- **DORA gap assessment** pro current Claude+Codex stack — určuje, jestli T-reg padne
- **Vedení Finshape strategicky potvrdí** ochotu investovat $0-300k rok-1 pro úsporu $25-195k/rok od roku 2+ + sovereignty/vendor-independence benefit
- **Kalibrace FTE absorpce** — kolik z 0.5-1.0 platform FTE absorbuje existující tým, kolik vyžaduje nový headcount
- **Legal review čínských modelů** (EU AI Act 2. 8. 2026)

**Decision gate Fáze 0 → Fáze 1:** Pokud strategická hodnota + cost rationale potvrzeny, pokračovat. Pokud ne, zastavit nebo pivot na "compliance-only" minimal sovereign (jen pro regulovaná data).

### Fáze 1 — Pilot Scénáře A (Q4 2026, 3-4 měsíce, ~$80-130k full TCO)

- **Scénář A** přes vlastní LiteLLM gateway + open-source harness
- **15-30 vývojářů** napříč týmy
- Modely: Qwen3-Coder-480B + GLM-4.7 + Codestral 25.08 + Claude Opus escalation
- **Harness adaptace** (zásadní v této fázi) — výběr & customizace open-source harness, system prompts, tool-use, MCP integrace
- Souběžně: RFP pro Scénář B (kontrakt-ready), Internal SWE-Bench eval suite

**FTE allocation Fáze 1:**
- 1.0 FTE platform engineer × 3-4 měs = ~$25-40k
- 0.5 FTE DevEx × 3-4 měs = ~$11-17k
- 0.2 FTE legal/security × 3-4 měs = ~$5-10k
- Externí MLOps konzultant ~50-100 h × $100/h = ~$5-10k
- Infrastructure cost pilotu (Nebius pay-per-token + Mistral + gateway): ~$5-15k
- Harness adaptace jednorázové: ~$25-50k engineering (interní + externí)
- **Total Fáze 1 full TCO: ~$80-130k**

**Validation kritéria (success = jdeme do Fáze 2):**
1. Sovereign obslouží ≥ 70 % denních úloh bez manuální eskalace
2. P50 TTFT ≤ 800 ms, decode ≥ 30 tok/s/user
3. NPS pilotních vývojářů ≥ neutralní
4. Per-user cost extrapolovaný na 400 dev ≤ $425k/rok full TCO
5. DORA audit trail úplný
6. Harness stabilní (žádné regression vs Claude Code)
7. SWE-Bench interní: ≥ 75 % kvality Claude Opus
8. Prefix-cache hit rate ≥ 70 %

**Go/no-go:** ≥ 6/8 kritérií ✓ → Fáze 2 rollout.

### Fáze 2 — Produkční rollout Scénáře A (Q1-Q2 2027)

- Plný rollout ~400 vývojářů přes Nebius Token Factory
- Hybrid routing 70-80 % sovereign / 20-30 % escalation
- **FTE allocation:**
  - Platform 0.5-1.0 FTE (~$50-115k/rok)
  - DevEx 0.5 FTE rok 1, 0.25 FTE rok 2+ (~$25-50k/rok)
  - Harness maintenance 0.2 FTE (~$15-25k/rok)
- **Rok 1 (transition) full TCO: ~$360-675k** (rovnocenné s baseline $360-470k nebo mírně dražší)
- **Rok 2+ (ongoing) full TCO: ~$255-425k/rok** (úspora ~$25-195k/rok, mid ~$110k)
- Kontrakt-ready pro Scénář B, aktivace 4-8 týdnů po T-B

### Fáze 3 — Přechod na Scénář B (po T-B, Q4 2027 - 2028)

Spouští se, když:
- Subscription baseline (bez sovereign) by rostl ke $700k+/rok **NEBO**
- Scénář A nestačí kapacitně **NEBO**
- Fine-tuning na banking codebase vyžadován

**FTE allocation B:**
- + MLOps engineer 1.0 FTE (CZ premium, nový headcount, ~$115-130k/rok)
- + Platform 0.5 FTE pro on-call (~$50k/rok)
- Migration jednorázové ~$30-60k

**Full TCO B:** ~$670-740k/rok (vs A ~$255-425k/rok).

### Fáze 4 — Vyhodnocení Scénáře C (2028+, only-if)

Jen pokud spend $1M+/rok stabilně + Scénář B utilizace 75 %+.

**Klíčové principy:** Hybrid routing + portable model weights = reverzibilita. **FTE je nejcennější a nejhůře reverzibilní investice** — nehiring před validovaným pilotem.

---

## 9. Risk mitigace

| Riziko | Mitigace |
|---|---|
| Anthropic/OpenAI zdraží 2-3× | Snížit eskalaci, posílit GLM-4.7/Kimi K2.6 jako near-frontier |
| Nebius / EU API zdraží | Migrace na Scénář B — váhy modelů portovatelné |
| EU AI Act zakáže čínské modely | Llama 4-Coder + Codestral; degradace SWE-Bench 5-10 bodů |
| Provider výpadek | Multi-region: Nebius FI + OVHcloud FR |
| Vývojáři nepřijmou kvalitu | Pilot odhalí dřív; Claude Code Max zůstává fallback |
| MLOps team nestíhá | Pilot = serverless. B+ externí konzultanti během hiringu |
| GPU trh zlevní | Žádný CapEx v Fázích 1-2 |
| **Harness adaptace selže** (nové v4) | Pilot ověří. Backup: zůstat na Claude Code pro 30 % traffic, sovereign jen pro 70 % via gateway. |
| **CZ MLOps hiring delay** (nové v4) | Externí konzultanti $85-130/h jako bridge. Začít hiring v Q3 2026 (Fáze 0). |
| **Productivity tax horší než odhad** (nové v4) | Champions program, pomalejší rollout (po týmech), preserved Claude Code fallback. |

---

## 10. Critical items pro pilot (Fáze 1, Q4 2026) — full TCO

| # | Co | Kdo | Kdy | Odhad (CZ rates) |
|---|---|---|---|---|
| 1 | **AI Gateway (LiteLLM)** + audit, budgety, prefix-cache routing | Platform team (1.0 FTE) | Týdny 1-3 | ~$10-15k engineering + $1-2k/měs hosting |
| 2 | **Spend tracking dashboard** + T-B trigger watch | Platform team | Týdny 2-3 | ~$3-5k engineering |
| 3 | **Nebius + Mistral kontrakt + DPA** + endpoint setup | Procurement + Legal + Platform | Týdny 1-4 | ~$5-8k legal + setup |
| 4 | **Legal review čínských modelů** (EU AI Act) | Legal + Security | Týdny 1-6 | ~$5-10k legal/external |
| 5 | **Harness adaptace** (klíčové) — open-source harness, system prompts, tool-use, MCP, eval | Platform + DevEx + externí MLOps | Týdny 2-12 | ~$25-50k (mix) |
| 6 | **Pilot rollout** — config přes gateway pro 15-30 dev | DevEx (0.5 FTE) | Týdny 4-6 | interní (v FTE allocation) |
| 7 | **DORA gap assessment** | Compliance | Týdny 4-10 | interní + ~$5-10k externí audit |
| 8 | **RFP pro Scénář B** | Procurement | Týdny 8-12 | ~$3-5k legal |
| 9 | **Internal SWE-Bench eval set** (50 úloh) | Platform + engineering (50-80 h) | Týdny 4-8 | ~$3-5k interní |

**Celkový náklad pilotu (Fáze 1) full TCO:** ~$80-130k. Vůči ~$400k/rok baselineu = ~20-30 % roční investice pro validaci go/no-go.

---

## 11. Verifikace (jak ověřit pilot a rollout)

**Fáze 1 — pilot success kritéria (go/no-go pro Fázi 2):**

1. **Kvalita** — sovereign ≥ 70 % denních úloh bez manuální eskalace
2. **Latence** — P50 TTFT ≤ 800 ms, decode ≥ 30 tok/s/user
3. **NPS pilotních vývojářů** ≥ neutralní
4. **Per-user cost extrapolovaný** — full TCO na 400 dev ≤ $425k/rok
5. **SWE-Bench interní** — sovereign ≥ 75 % kvality Claude Opus
6. **DORA audit trail** — 100 % requestů
7. **Prefix-cache hit rate** ≥ 70 %
8. **Harness stabilita** — žádné regression v dev workflow

**Go/no-go:** ≥ 6/8 ✓ → Fáze 2.

**Fáze 2 — produkční rollout success kritéria (po 3-6 měs.):**

1. Roční full TCO ≤ $425k/rok rok 2+ (vs $360-470k baseline)
2. Eskalace na Anthropic/OpenAI ≤ 30 %
3. Zero compliance incidents v 90-day window
4. Vývojář NPS neklesl meziročně více než 5 bodů
5. Platform FTE allocation v plánu (≤ 1.0 FTE Platform + ≤ 0.25 FTE DevEx ongoing)

---

## 12. Otevřené otázky před spuštěním

- **Composition $350-450k/rok** — kolik Codex Enterprise vs Claude Team vs Max vs API overages?
- **Trajektorie premium adopce** — kolik dev je dnes na Claude Code Max a kolik na něj chce přejít?
- **DORA / CNB current posture** — má Finshape aktuální DORA gap assessment? Pokud non-compliant, T-reg může předběhnout T-A.
- **Banking IP fine-tune hodnota** — kvantifikace přes A/B test ve Fázi 1.
- **DC preference** — Praha/Frankfurt/Helsinki?
- **FTE absorpce** — kolik z 0.5-1.0 platform FTE může existující platform team absorbovat?
- **Hiring readiness** — kolik měsíců trvá hire 1 senior MLOps v ČR? Mzdové rozpočtové prostory?

---

## 13. Next actions po schválení této verze plánu

**Fáze 0 (Q3 2026, 6-8 týdnů, ~$15-25k):**
1. **DORA gap assessment** pro current Claude+Codex stack — výsledek určuje, jestli sovereign jde nezávisle na cost ROI
2. **Vedení Finshape strategicky potvrdí** ochotu investovat $0-300k rok-1 pro úsporu $25-195k/rok od roku 2+ + sovereignty/vendor-independence
3. **Kalibrace FTE absorpce** — co existující tým absorbuje, co vyžaduje nový headcount
4. **Legal kick-off:** EU AI Act review pro Qwen/DeepSeek/GLM/Kimi/Codestral

**Fáze 1 pilot (Q4 2026, 3-4 měsíce, ~$80-130k full TCO):**
1. Vytvořit nový repo `finshape/ai-gateway` s LiteLLM základem
2. Iniciovat procurement workflow s Nebius a Mistral La Plateforme + RFP pro Scénář B
3. **Harness adaptace** — výběr open-source harness (Cline / Roo / Aider / opencode / Crush), system prompts, tool-use plumbing, MCP integrace, eval harness
4. Pilot rollout pro 15-30 vývojářů. Měření 8 KPIs.
5. Externí MLOps konzultant (advisory) pro vLLM/SGLang fundamentals

**Po pilotu (Q1-Q2 2027):**
- Pokud 6/8 kritérií splněno → rollout Scénáře A na ~400 dev
- Rok 1 full TCO ~$360-675k (rovnocenné s baseline), rok 2+ ~$255-425k/rok (úspora ~$25-195k/rok mid ~$110k)
- Kontrakt-ready pro Scénář B (aktivace 4-8 týdnů po T-B)

**Hiring strategie:**
- Začít hned (Q3 2026) hledat 1.0 FTE senior platform/MLOps engineer — CZ talent pool malý, timeline 6-9 měs.
- Externí konzultanti ($85-130/h CZ) jako gap-filler

---

## Zdroje a podklady

- Modely a benchmarky: SWE-Bench Verified leaderboard, Qwen/HF, DeepSeek HF, GLM HF, Kimi K2.6, Codestral 25.08
- EU providers: Nebius Token Factory pricing, OVHcloud HGX bare-metal, Mistral La Plateforme
- Inference: vLLM/SGLang docs, DeepSeek-V3 H100/H200 benchmarks, EAGLE-3 speculative decoding
- Hardware: Jarvislabs H100/H200 guides, SemiAnalysis Blackwell shipment
- Colocation: TTC Teleport Praha, DataCenterHawk EU 2026
- Regulační: IAPP DORA+GDPR guide, EU AI Act enforcement 2. 8. 2026, AWS ESC sovereignty
- CZ mzdové sazby: PayLab/Profesia 2026, Czech IT salary survey (Hays/Robert Half)

Vizuální shrnutí: viz [`sovereign-ai-strategy.html`](./sovereign-ai-strategy.html).
