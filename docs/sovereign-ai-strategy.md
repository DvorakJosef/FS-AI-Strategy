# Sovereign AI — analýza a návrh pro Finshape (~700 lidí, ~500 vývojářů, banking software)

> Verze: 2026-05-14 (v3 — opravený baseline) · Strategický návrh pro diskuzi s vedením, procurementem a compliance

> **Poznámka k verzování:** v1 (původní) předpokládala současný spend ~$30k/měs s trajektorií ke $90k/měs.
> Skutečný současný spend podle uživatele je ~$350-450k/rok (~$30-37k/měs) s pesimistickou trajektorií ke
> ~$500-700k/rok. Tato verze sjednocuje matematiku. Doporučení v jádru zůstává: Scénář A je už dnes ekonomicky
> přínosný, Scénář B je rovnocenný a dává cap při dalším růstu.

---

## 1. Context

**Proč to děláme:** Současný coding stack (Claude Code Team/Max + OpenAI ChatGPT Codex Enterprise pro ~400 vývojářů, ~120 z toho Codex Enterprise) má čtyři dlouhodobé tlaky:

1. **Regulace (DORA, GDPR, ČNB)** — banking software vyžaduje data residency v EU, kontrolu nad third-party dependencies, plný audit trail. Anthropic/OpenAI = US providers s CLOUD Act expozicí; i jejich EU regiony jurisdikčně nejsou imunní.
2. **Kontrola nákladů** — současný spend ~$350-450k/rok je v rozsahu, kde **Scénář A (serverless) je už dnes přímo levnější** o ~$130-200k/rok. Pokud trajektorie poroste, výhoda se zvětšuje.
3. **Nezávislost na vendorech** — strategická obrana proti zdražování, změnám politik (rate limits, model deprecation, geografické restrikce), výpadkům.
4. **Customizace a IP** — fine-tune na interní codebase, doménové znalosti bankingu, vlastní embeddings na interních repozitářích bez exfiltrace do USA.

**Cíl:** Hybridní architektura, kde **sovereign open-weight stack pokryje 70-80 % denní coding rutiny** (autocompletion, refactoring, code review, vysvětlení, jednoduché agentic úkoly), zatímco **Claude Opus / GPT-5 zůstanou pro nejtěžších 20-30 %** (multi-repo refactor, novel algoritmy, hluboké debugging). Sovereign jako default, frontier proprietary jako escalation.

**Časový horizont:** Pilot Q4 2026 (15-30 vývojářů), produkční rollout Scénáře A Q1-Q2 2027 (~400 dev), přechod na Scénář B podle decision triggeru (Q3-Q4 2027 nebo později), vyhodnocení on-prem 2028+.

---

## 2. Současný stav (baseline)

| Položka | Hodnota |
|---|---|
| Skutečný roční spend (2026-05-14) | **~$350-450k / rok ≈ $30-37k / měs** |
| Počet aktivních AI uživatelů | ~400 |
| Průměr na seat | **~$70-95 / seat / měsíc** |
| Mix licencí (orientačně) | ~120 Codex Enterprise/ChatGPT Business + ~280 Claude Team/Pro + subset Claude Code Max |
| Trajektorie podle uživatele | "spotřeba postupně roste, víc lidí přechází na premium plány" |
| 12-měsíční pesimistický odhad bez akce | **~$500-700k / rok ($42-58k / měs)** |

**Klíčové implikace:**
- $70-95/seat/měsíc průměr značí, že významná část týmu už dnes využívá premium tier (Claude Code Max, Codex Enterprise heavy users).
- **Scénář A (serverless) je v této chvíli ekonomicky výhodný** — ~$170-260k/rok vs $350-450k → úspora ~$100-200k/rok hned po rolloutu.
- **Scénář B (dedikovaný GPU)** je rovnocenný s baseline ($400-440k/rok vs $350-450k), ale zastropuje cenu při dalším růstu (marginal cost téměř nula nad fixní kapacitu) a dává plnou sovereignty.
- **Scénář C (on-prem)** stále vyžaduje další růst spendu nebo strategickou hodnotu (fine-tuning, max sovereignty) k zdůvodnění.

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
| **Celkem** | **~$14-22k/měs ≈ $170-260k/rok** |
| CapEx | **$0** |
| Time-to-launch | **2-4 týdny** |

**Pro:** Nulový operational risk; okamžitý start; škáluje na 0; **ekonomicky levnější už dnes** (~$130-200k/rok úspora vs baseline); ideální pro pilot.
**Proti:** Sovereignty je "EU jurisdikce + DPA" (silné, ale ne plně air-gapped); per-token cena škáluje s růstem; throughput SLA závisí na tieru; menší schopnost fine-tuningu.
**DORA posture:** Solidní (Nebius má ISO 27001 + DORA addendum na enterprise tieru, Mistral má FR jurisdikci + plné DPA). Audit a CNB review by měly projít.

### Scénář B — Dedikované GPU u EU provideru (Nebius reserved / OVHcloud HGX)

**Co to je:** Pronajatý bare-metal nebo VM 8×H200 cluster, vy ho operujete (vLLM/SGLang), provider dodává HW + síť + DC. Reserved discount 30-50 %. Cena se odpoutá od usage — kapacitní strop.

Doporučení: **Nebius reserved (FI Mäntsälä, NL)** primární, **OVHcloud HGX (FR Roubaix, PL Warszawa)** sekundární. OVHcloud má **SecNumCloud + ISAE 3402 + explicitní DORA exit klauzule** — nejlepší banking-grade kontrakt v EU.

| Položka | $/měs |
|---|---|
| 4× 8×H200 reserved 12-měs (Nebius @ ~$5.4k/node) | $22k |
| Storage, sítě, monitoring, gateway, ops | $4k |
| Externí MLOps konzultanti (částečný úvazek) | $4k |
| Anthropic Opus / OpenAI GPT-5 (escalation) | $4-7k |
| **Celkem** | **~$34-37k/měs ≈ $410-440k/rok** |
| CapEx | **$0** |
| Time-to-launch | **6-10 týdnů** |

**Pro:** Plná kontrola nad modelem (fine-tuning, custom routing), žádný vendor lock-in na úrovni vah, predictable pricing, EU jurisdikce, žádný CapEx. **Stejný náklad jako baseline, ale strop ceny při růstu** — pokud usage poroste, marginal cost je téměř nula.
**Proti:** Při nízkém využití vyšší fixní cost než Scénář A; vyžaduje MLOps schopnost (částečně řešeno externí pomocí); SLA na hardware = závazek od poskytovatele, ne od vás.
**DORA posture:** Velmi silná u OVHcloud (SecNumCloud); silná u Nebius (ale potřeba review NL/FI jurisdikce). Audit-friendly.

### Scénář C — On-prem (4× 8×H200 v Praze nebo brněnském DC)

**Co to je:** Vlastní hardware ve vlastním (nebo colocation) DC. Maximální svrchovanost. Air-gapped možný.

| Položka | 3-letá TCO | Měs. amortizováno (5 let) |
|---|---|---|
| 4× HGX H200 8-GPU servery (~$420k/ks) | $1.7M | $28k |
| Sítě (InfiniBand NDR), storage, řízení | $200k | $3.3k |
| Colo Praha (~40 kW @ €180/kW/měs all-in) | $250k | $4k |
| Power (~40 kW × 1.34 PUE × €0.15 × 8760) | $200k | $3.3k |
| NVIDIA AI Enterprise + HW support | $480k | $8k |
| Spares, MLOps staffing alokace | $320k | $5.4k |
| Anthropic/OpenAI escalation | – | $4-7k |
| **Celkem 3-letá TCO** | **~$3.15M** | **~$56-60k/měs ≈ $670-720k/rok** |
| **Stejné, 5-letá TCO** | **~$3.5M** | **~$48-52k/měs ≈ $580-625k/rok** |
| CapEx prvních 6 měsíců | **~$2.0M** | – |
| Time-to-launch | **4-7 měsíců** | – |

**Pro:** Maximální sovereignty (full air-gap možný), nejlepší pro DORA/CNB review, po roce 5 marginalní náklady ~$15-20k/měs (jen power+colo+escalation), strategická aktiva. Možnost spustit i tréninkové úlohy (fine-tuning na interní codebase).
**Proti:** Vysoký CapEx upfront ($2M), inflexibilita (těžké škálovat dolů), HW lead-time + commissioning. **Vyplatí se až když by spend na Scénáři B stabilně přesáhl $600-700k/rok.**

### Scénář D — Hyperscaler EU region (AWS Bedrock / Azure / GCP)

**Co to je:** Cloud-native, EU region, ale **US-vlastněný provider** — CLOUD Act se aplikuje i na ESC (AWS European Sovereign Cloud). **Nedoporučeno pro banking compliance.**

---

## 6. Break-even analýza — kdy který scénář dává finanční smysl

**Výchozí stav:** ~$350-450k / rok subscription spend (mid-point ~$400k/rok ≈ $33k/měs).

| Scénář | Roční náklad | Vs baseline ($400k) | Závěr |
|---|---|---|---|
| **A. EU Serverless** | ~$170-260k | **−35 až −58 % (úspora $90-230k/rok)** | ✅ Levnější už dnes |
| **B. Dedikovaný GPU rental** | ~$410-440k | ±0 až +10 % (≈ rovnocenný) | ⚖️ Stejný náklad, sovereignty + cap |
| **C. On-prem (5-letá amort.)** | ~$580-625k + $2M CapEx | +45-55 % | ❌ Vyplatí se až při spendu ~$600k+/rok |
| **D. Hyperscaler EU** | $300k - $2.4M | mix | ❌ CLOUD Act |

### 6.1 Break-even body (kdy přepnout v rámci sovereign cesty)

| Akce | Spustit když | Logika |
|---|---|---|
| **A → spuštění** | Spend ≥ $250k/rok | Při $350-450k baseline (~$70-95/seat/měs) je A pod hranicí, **dnes ✓** |
| **A → B přechod** | Spend roste ke $420k+/rok (~$35k/měs) **NEBO** vlastní GPU dává jiné benefity (fine-tune, kapacita guaranteed, větší sovereignty) | B = fixní strop ceny; A roste s usage |
| **B → C přechod** | Spend na Scénáři B by dlouhodobě přesáhl $700k/rok **A** Scénář B utilizace 75 %+ | On-prem se vyplatí jen při vysoké, stabilní zátěži |

### 6.2 Sensitivity — co se stane při různých scénářích růstu

| Růstová trajektorie (next 24 měs.) | Roční spend | Optimální volba |
|---|---|---|
| Stagnuje na současné úrovni | $350-450k | **A** (úspora $90-230k/rok) |
| Mírný růst (více Max plans) | $500-600k | **A** nebo přechod **A → B** podle utilizace |
| Silný růst (plošná Max adopce, heavy usage) | $700-900k | **B** (úspora $270-450k/rok, kapacita zastropována) |
| Extrémní (Codex Enterprise heavy + Max + API overages) | $1M+ | **B nebo C** |

### 6.3 Sensitivity — co když Anthropic/OpenAI zdraží

| Zdražení (2 roky) | Roční spend | Optimální volba |
|---|---|---|
| +20 % (běžná inflace) | $420-540k | **A** vyhrává silně, **B** mírně |
| +50 % (Max stoupne na $150) | $525-675k | **A** masivně vyhrává, **B** vyhrává |
| 2× (politická change, EU regulace) | $700-900k | **B** je no-brainer; **C** v úvahu |

### 6.4 Skrytá rizika baseline (ne v ceně dnes)

- **DORA non-compliance cost** — pokud současný US-vázaný stack neprochází DORA reviewem, fixed cost remediace (extra DPA, audit, doplňková kontrola) může přidat $50-150k/rok jen na compliance overhead. Sovereign tento problém řeší strukturálně.
- **Rate limit & throttling cost** — vývojáři ztrácejí čas, když Claude Code Max hit limit. Při průměrné mzdě $80/h a 30 min/den × 400 dev × 5 % limit-affected → ~$400k/rok ztracené produktivity. Sovereign cluster nemá tento problém.
- **Vendor concentration risk** — pokud Anthropic změní enterprise terms (např. omezí Czech banking sector), schopnost migrovat za týden = $0 (sovereign ready) vs měsíce (subscription cancelled, productivity = 0).

---

## 7. Decision triggers — kdy aktivovat kterou fázi

| Trigger | Status k 2026-05-14 | Akce |
|---|---|---|
| **T-A: Spustit Scénář A (pilot)** | ✅ **už splněno** ($400k/rok > $250k práh) | Spustit pilot 15-30 dev v Q4 2026 |
| **T-B: Přejít na Scénář B (dedikovaný GPU)** | ⏳ Pravděpodobně do 12-18 měs. podle trajektorie | RFP a kontrakt-ready vzít hned, aktivace po validaci A |
| **T-C: Aktivovat Scénář C (on-prem)** | ⏳ Nepravděpodobné v 24 měs. horizontu | Vyhodnotit 2028 podle reálných dat z B |
| **T-reg: Regulační vynucení** | ❓ Vyžaduje DORA gap assessment | Pokud T-reg padne, T-A/T-B se zrychlí na týdny |

---

## 8. Doporučená cesta (fázovaná)

### Fáze 1 — Pilot Scénáře A (Q4 2026, 3-4 měsíce, ~$30-50k total)

- **Scénář A** (Nebius Token Factory + Mistral La Plateforme) přes vlastní LiteLLM gateway
- **15-30 vývojářů** napříč týmy (backend, frontend, infra) — různé use cases pro reprezentativní data
- Modely: Qwen3-Coder-480B (primární agentic) + GLM-4.7 (chat) + Codestral 25.08 (inline autocomplete) + Claude Opus jako escalation
- Souběžně: RFP pro Scénář B (kontrakt-ready), legal review čínských modelů, DORA gap analysis

**Validation kritéria** (success → jdeme do Fáze 2):
1. Sovereign obslouží ≥ 70 % denních úloh bez manuální eskalace na Opus
2. P50 TTFT ≤ 800 ms, decode ≥ 30 tok/s/user
3. NPS pilotních vývojářů ≥ neutralní
4. Per-user měsíční cost extrapolovaný na 400 dev ≤ $260k/rok
5. DORA audit trail je úplný

**Náklad pilotu:** ~$30-50k total na 3-4 měsíce. Vůči $350-450k/rok baselineu marginální.

### Fáze 2 — Produkční rollout Scénáře A (Q1-Q2 2027, ~$210-260k/rok)

- Plný rollout na ~400 vývojářů přes Nebius Token Factory
- Hybrid routing v gatewayi: 70-80 % sovereign, 20-30 % Anthropic/OpenAI escalation
- **Roční náklad ~$210-260k vs baseline $350-450k → úspora ~$130-200k/rok**
- Kontrakt-ready pro Scénář B (Nebius reserved nebo OVHcloud), aktivace v 4-8 týdnech, jakmile padne T-B

### Fáze 3 — Přechod na Scénář B (po T-B, pravděpodobně Q3-Q4 2027)

Spouští se, když:
- Spend na Scénáři A vystoupá ke $35-40k/měs **NEBO**
- Usage stabilně překračuje serverless throughput SLA **NEBO**
- Potřeba fine-tuningu na interní banking codebase (vyžaduje dedikovanou kapacitu)

**Náklad:** ~$420-440k/rok (rovnocenný současnému baseline, ale predictable + sovereignty + capacity headroom).

### Fáze 4 — Vyhodnocení Scénáře C (2028+, only-if)

Pouze pokud spend stabilně překračuje $600-700k/rok a Scénář B utilizace je vysoká.

**Klíčový princip:** Hybrid routing + portable model weights = každá fáze je reverzibilní a triggery (sekce 7) řídí timing.

---

## 9. Risk mitigace

| Riziko | Mitigace |
|---|---|
| Anthropic/OpenAI zdraží escalation tier 2-3× | Snížit eskalaci v sovereign fázi, posílit GLM-4.7/Kimi K2.6 jako "near-frontier" |
| Nebius / EU API zdraží během pilotu | Migrace na dedikovaný GPU rental (Scénář B) — Nebius i OVHcloud nabízejí stejnou cestu, **váhy modelů jsou portovatelné** |
| EU AI Act zakáže čínské modely | Přepnout primární na Llama 4-Coder (až vyjde) + Codestral; degradace SWE-Bench ~5-10 bodů |
| OVHcloud / Nebius má výpadek | Multi-region: primary Nebius FI, secondary OVHcloud FR (oboje schopni serverovat stejné Qwen/DeepSeek), gateway routuje automaticky |
| Vývojáři nepřijmou kvalitu sovereign modelu | Pilot odhalí dřív, než se utopí kapitál; Claude Code Max zůstává v gatewayi jako fallback (degradace, ne nahrazení) |
| MLOps team nestíhá | Pilot = serverless, žádný GPU cluster → minimální zátěž. Scénář B+ externí kontrakt (managed inference) |
| Trh GPU zkolabuje a Blackwell/Rubin výrazně zlevní | Žádný CapEx ve Fázích 1-2 — flexibilita zachována |

**Klíčové principy:**
1. **Váhy modelů jsou portovatelné** — pokud máte Qwen3-Coder-480B stažený, můžete přejít mezi Nebius / OVHcloud / on-prem za týdny.
2. **Gateway je vaše vlastní** — vendor lock-in je minimální (LiteLLM open-source).
3. **Hybrid znamená graceful degradation** — pokud sovereign selže, eskalace na Anthropic je transparentní pro vývojáře.
4. **Triggers řídí cash flow** — žádná velká investice bez splněného triggeru.

---

## 10. Critical items pro pilot (Fáze 1, Q4 2026)

| # | Co | Kdo | Kdy | Odhad nákladu |
|---|---|---|---|---|
| 1 | **AI Gateway (LiteLLM)** — multi-provider routing, audit log, per-user budgety, cost dashboard, prefix-cache aware routing | Platform team | Týdny 1-3 | ~$6-10k engineering + $1-2k/měs hosting |
| 2 | **Spend tracking dashboard** — metriky per-dev / per-team / per-repo. T-B trigger watch. | Platform team | Týdny 2-3 | ~$2-3k engineering |
| 3 | **Nebius Token Factory + Mistral La Plateforme** kontrakt + DPA, OpenAI-compatible endpoint setup | Procurement + Legal + Platform | Týdny 1-4 | ~$3-5k legal review + setup |
| 4 | **Legal review čínských modelů** vs EU AI Act 2. 8. 2026 — Qwen, DeepSeek, GLM, Kimi. Governance package. | Legal + Security | Týdny 1-6 | ~$5-10k legal/external |
| 5 | **Pilot rollout** — Claude Code / Codex CLI config přes gateway endpoint pro 15-30 dev | DevEx | Týdny 4-6 | interní |
| 6 | **DORA gap assessment** pro current state (Claude+Codex US providers) i target state (sovereign) | Compliance | Týdny 4-10 | interní |
| 7 | **RFP pro Scénář B** (Nebius reserved, OVHcloud HGX) — kontrakt-ready do konce pilotu, aktivace po T-B | Procurement | Týdny 8-12 | ~$3-5k legal |
| 8 | **Internal SWE-Bench evaluation set** — 50 reprezentativních úloh z reálných PRs pro blind review sovereign vs Opus | Platform team + interní engineering | Týdny 4-8 | interní |

---

## 11. Verifikace (jak ověřit pilot a rollout)

**Fáze 1 — pilot success kritéria (go/no-go pro Fázi 2):**

1. **Kvalita** — sovereign model obsluhuje ≥ 70 % denních úloh u pilotních vývojářů bez manuální eskalace na Opus.
2. **Latence** — P50 TTFT ≤ 800 ms, P50 decode ≥ 30 tok/s/user.
3. **NPS pilotních vývojářů** ≥ neutralní (sběr po 4-6 týdnech).
4. **Per-user cost** — extrapolovaný náklad sovereign na 400 dev ≤ $260k/rok (úspora vs baseline).
5. **SWE-Bench na interních úlohách** — sovereign dosáhne ≥ 75 % kvality Claude Opus na 50 internal tasks blind review.
6. **DORA audit trail** — 100 % requestů má kompletní záznam v EU.
7. **Prefix-cache hit rate** — ≥ 70 % na production-like workloadu.

**Go/no-go rozhodnutí:** ≥ 5/7 kritérií ✓ → Fáze 2 rollout.

**Fáze 2 — produkční rollout success kritéria** (měřeno po 3-6 měs. provozu):

1. Roční run-rate cost ≤ $260k/rok (vs $350-450k baseline) → úspora 25-40 %
2. Eskalace na Anthropic/OpenAI ≤ 30 %
3. Zero compliance incidents v 90-day window
4. Vývojář NPS neklesl meziročně

---

## 12. Otevřené otázky před spuštěním

- **Composition $350-450k/rok** — kolik je z toho Codex Enterprise (přes ChatGPT Business) vs Claude Team vs Claude Code Max vs API overages? Pomáhá při triggerwatch — který vendor zdraží má jaký dopad.
- **Trajektorie premium adopce** — kolik vývojářů je už dnes na Claude Code Max ($100-200/seat) a kolik na něj chce přejít? Pokud trend k 100 % Max, T-B se urychlí.
- **DORA / CNB current posture** — má Finshape aktuální DORA gap assessment, kde figurují AI tools? Pokud non-compliant, T-reg trigger může předběhnout T-A.
- **Banking IP fine-tune hodnota** — má smysl nechat sovereign model trénovat na interní banking codebase? Kvantifikace přes A/B test ve Fázi 1.
- **DC preference** — Praha/Frankfurt/Helsinki? Nebius primárně FI/NL, OVHcloud má FR/PL/DE, ale ne CZ — limit pro on-prem Scénář C.

---

## 13. Next actions po schválení tohoto plánu

**Týdny 1-12 (Fáze 1 pilot, Q4 2026):**
1. Vytvořit nový repo `finshape/ai-gateway` s LiteLLM základem (Apache 2.0) — multi-provider routing, audit, prefix-cache aware routing, cost dashboard.
2. Iniciovat procurement workflow s Nebius (primární) a Mistral La Plateforme (Codestral inline) + souběžně RFP pro Scénář B (Nebius reserved + OVHcloud HGX).
3. Iniciovat legal review (EU AI Act + DORA addendum pro Qwen/DeepSeek/GLM/Kimi/Codestral).
4. Pilot rollout pro 15-30 vývojářů přes gateway.

**Po pilotu (Q1-Q2 2027):**
- Pokud kritéria splněna → rollout Scénáře A na ~400 dev → **roční úspora ~$130-200k**.
- Souběžně připravený kontrakt Scénáře B (aktivace 4-8 týdnů po T-B triggeru).

---

## Zdroje a podklady

- Modely a benchmarky: SWE-Bench Verified leaderboard, Qwen/Hugging Face, DeepSeek HF, GLM HF, Kimi K2.6 release notes, Codestral 25.08 announcement
- EU providers: Nebius Token Factory pricing, OVHcloud AI Endpoints + HGX bare-metal, Scaleway/IONOS/Mistral La Plateforme pricing pages
- Inference performance: vLLM/SGLang docs, DeepSeek-V3 H100/H200 benchmark studies, EAGLE-3 / MTP speculative decoding production data
- Hardware ceny + lead-times: Jarvislabs H100/H200 guides, SemiAnalysis Blackwell shipment, ServeTheHome Gaudi3
- Colocation Praha: TTC Teleport, Voxility, DataCenterHawk EU 2026 fundamentals
- Regulační: IAPP DORA+GDPR guide, EU AI Act enforcement timeline (2. 8. 2026), AWS ESC sovereignty assessment

Vizuální shrnutí: viz [`sovereign-ai-strategy.html`](./sovereign-ai-strategy.html).
