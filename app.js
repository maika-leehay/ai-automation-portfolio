/**
 * AI Automation Portfolio - Mekaoui Abdelmounaim
 * Core Application Logic & Interactive Engines (Optimized English Edition)
 */

document.addEventListener('DOMContentLoaded', () => {
  initThemeEngine();
  initNeuralCanvas();
  initSciFiHudMenu();
  initWorkflowSimulator();
  initRoiCalculator();
  initFaqAccordion();
  initBookingModal();
  initAuditForm();
  initAiConcierge();
});

/* ==========================================================================
   1. Theme Switcher Engine (Light / Dark)
   ========================================================================== */
function initThemeEngine() {
  const themeToggle = document.getElementById('hudThemeToggle');
  const themeIcon = document.getElementById('themeIcon');
  const themeLabel = document.getElementById('themeLabel');

  let currentTheme = localStorage.getItem('user_theme') || 'dark';

  function applyTheme(theme) {
    currentTheme = theme;
    localStorage.setItem('user_theme', theme);
    document.documentElement.setAttribute('data-theme', theme);

    if (theme === 'light') {
      if (themeIcon) themeIcon.textContent = '🌙';
      if (themeLabel) themeLabel.textContent = 'DARK';
    } else {
      if (themeIcon) themeIcon.textContent = '☀️';
      if (themeLabel) themeLabel.textContent = 'LIGHT';
    }
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
      applyTheme(nextTheme);
      showToast(nextTheme === 'light' ? '☀️ Holographic Light Mode Activated' : '🌙 Cyber Dark Mode Activated');
    });
  }

  applyTheme(currentTheme);
}

/* ==========================================================================
   2. Neural Particle Network Canvas
   ========================================================================== */
function initNeuralCanvas() {
  const canvas = document.getElementById('neuralCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let width, height;
  let particles = [];
  const particleCount = window.innerWidth < 768 ? 30 : 65;
  const maxDistance = 130;
  const mouse = { x: null, y: null, radius: 140 };

  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  }

  window.addEventListener('resize', resize);
  resize();

  window.addEventListener('mousemove', (e) => {
    mouse.x = e.x;
    mouse.y = e.y;
  });

  window.addEventListener('mouseleave', () => {
    mouse.x = null;
    mouse.y = null;
  });

  class Particle {
    constructor() {
      this.x = Math.random() * width;
      this.y = Math.random() * height;
      this.vx = (Math.random() - 0.5) * 0.7;
      this.vy = (Math.random() - 0.5) * 0.7;
      this.radius = Math.random() * 2 + 1;
      this.alpha = Math.random() * 0.5 + 0.2;
    }

    update() {
      this.x += this.vx;
      this.y += this.vy;

      if (this.x < 0 || this.x > width) this.vx *= -1;
      if (this.y < 0 || this.y > height) this.vy *= -1;

      // Mouse interaction
      if (mouse.x != null && mouse.y != null) {
        const dx = mouse.x - this.x;
        const dy = mouse.y - this.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < mouse.radius) {
          const force = (mouse.radius - dist) / mouse.radius;
          const angle = Math.atan2(dy, dx);
          this.x -= Math.cos(angle) * force * 2;
          this.y -= Math.sin(angle) * force * 2;
        }
      }
    }

    draw(isLight) {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
      ctx.fillStyle = isLight
        ? `rgba(2, 132, 199, ${this.alpha * 0.8})`
        : `rgba(0, 240, 255, ${this.alpha})`;
      ctx.fill();
    }
  }

  for (let i = 0; i < particleCount; i++) {
    particles.push(new Particle());
  }

  function animate() {
    ctx.clearRect(0, 0, width, height);
    const isLight = document.documentElement.getAttribute('data-theme') === 'light';

    for (let i = 0; i < particles.length; i++) {
      particles[i].update();
      particles[i].draw(isLight);

      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < maxDistance) {
          const opacity = (1 - dist / maxDistance) * (isLight ? 0.2 : 0.25);
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = isLight
            ? `rgba(2, 132, 199, ${opacity})`
            : `rgba(0, 240, 255, ${opacity})`;
          ctx.lineWidth = 0.8;
          ctx.stroke();
        }
      }
    }

    requestAnimationFrame(animate);
  }

  animate();
}

/* ==========================================================================
   3. Space Sci-Fi Tactical Menu & Drone Tracker
   ========================================================================== */
function initSciFiHudMenu() {
  const header = document.getElementById('siteHeader');
  const navMenu = document.getElementById('scifiNavMenu');
  const navLinks = document.querySelectorAll('.scifi-nav-link');
  const drone = document.getElementById('hudSpaceDrone');
  const mobileBtn = document.getElementById('scifiMobileBtn');
  const navWrapper = document.querySelector('.hud-nav-wrapper');
  const soundToggle = document.getElementById('hudSoundToggle');
  const warpBtn = document.querySelector('.scifi-warp-btn');

  let sfxEnabled = true;
  let audioCtx = null;

  function getAudioContext() {
    if (!audioCtx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        audioCtx = new AudioContext();
      }
    }
    if (audioCtx && audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
    return audioCtx;
  }

  function playHoverSound() {
    if (!sfxEnabled) return;
    const ctx = getAudioContext();
    if (!ctx) return;
    try {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(880, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(1760, ctx.currentTime + 0.04);
      gain.gain.setValueAtTime(0.04, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.04);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.04);
    } catch (e) { }
  }

  function playClickSound() {
    if (!sfxEnabled) return;
    const ctx = getAudioContext();
    if (!ctx) return;
    try {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(1200, ctx.currentTime);
      osc.frequency.setValueAtTime(600, ctx.currentTime + 0.03);
      gain.gain.setValueAtTime(0.06, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.08);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.08);
    } catch (e) { }
  }

  function playWarpSound() {
    if (!sfxEnabled) return;
    const ctx = getAudioContext();
    if (!ctx) return;
    try {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(150, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(2400, ctx.currentTime + 0.35);
      gain.gain.setValueAtTime(0.08, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.4);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.4);
    } catch (e) { }
  }

  if (soundToggle) {
    soundToggle.addEventListener('click', () => {
      sfxEnabled = !sfxEnabled;
      if (sfxEnabled) {
        soundToggle.classList.remove('muted');
        soundToggle.querySelector('.sfx-icon').textContent = '🔊';
        soundToggle.querySelector('.sfx-label').textContent = 'SFX: ON';
        playClickSound();
        showToast('🔊 Tactical Audio FX Enabled');
      } else {
        soundToggle.classList.add('muted');
        soundToggle.querySelector('.sfx-icon').textContent = '🔇';
        soundToggle.querySelector('.sfx-label').textContent = 'SFX: MUTED';
        showToast('🔇 Audio FX Muted');
      }
    });
  }

  if (header) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 30) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }
      updateActiveSection();
    });
  }

  function moveDroneToElement(el) {
    if (!drone || !el || window.innerWidth < 1100) return;
    const deckRect = header.querySelector('.hud-nav-container').getBoundingClientRect();
    const targetRect = el.getBoundingClientRect();
    const targetX = targetRect.left - deckRect.left + (targetRect.width / 2) - 10;
    const targetY = targetRect.top - deckRect.top - 14;
    drone.style.transform = `translate3d(${targetX}px, ${targetY}px, 0)`;
  }

  let activeLink = navLinks[0];

  navLinks.forEach(link => {
    link.addEventListener('mouseenter', () => {
      moveDroneToElement(link);
      playHoverSound();
    });

    link.addEventListener('click', () => {
      activeLink = link;
      navLinks.forEach(l => l.classList.remove('active'));
      link.classList.add('active');
      playClickSound();
      if (navWrapper) navWrapper.classList.remove('mobile-open');
      if (mobileBtn) mobileBtn.classList.remove('open');
    });
  });

  if (navMenu) {
    navMenu.addEventListener('mouseleave', () => {
      if (activeLink) moveDroneToElement(activeLink);
    });
  }

  if (navLinks.length > 0) {
    setTimeout(() => {
      moveDroneToElement(navLinks[0]);
    }, 500);
  }

  if (warpBtn) {
    warpBtn.addEventListener('mouseenter', playHoverSound);
    warpBtn.addEventListener('click', () => {
      playWarpSound();
    });
  }

  if (mobileBtn && navWrapper) {
    mobileBtn.addEventListener('click', () => {
      mobileBtn.classList.toggle('open');
      navWrapper.classList.toggle('mobile-open');
      playClickSound();
    });
  }

  const sections = ['services', 'simulator', 'roi-calculator', 'case-studies', 'process', 'faq'];

  function updateActiveSection() {
    const scrollPos = window.scrollY + 200;
    for (let i = sections.length - 1; i >= 0; i--) {
      const section = document.getElementById(sections[i]);
      if (section && section.offsetTop <= scrollPos) {
        const correspondingLink = document.querySelector(`.scifi-nav-link[href="#${sections[i]}"]`);
        if (correspondingLink && correspondingLink !== activeLink) {
          navLinks.forEach(l => l.classList.remove('active'));
          correspondingLink.classList.add('active');
          activeLink = correspondingLink;
          moveDroneToElement(correspondingLink);
        }
        break;
      }
    }
  }
}

/* ==========================================================================
   4. Interactive Live AI Workflow Simulator
   ========================================================================== */
function initWorkflowSimulator() {
  const pipelineSelector = document.getElementById('pipelineSelector');
  const runBtn = document.getElementById('runSimulationBtn');
  const consoleOutput = document.getElementById('consoleOutput');

  if (!pipelineSelector || !runBtn || !consoleOutput) return;

  const pipelines = {
    'lead-gen': {
      nodes: [
        { title: 'Inbound Trigger', desc: 'Webhook captures new form lead from web', status: 'Triggered' },
        { title: 'AI Reasoning Agent', desc: 'Claude 3.5 evaluates ICP score & company data', status: 'AI Reasoning' },
        { title: 'Validation & Guardrails', desc: 'JSON schema verification & anti-hallucination check', status: 'Guardrails Passed' },
        { title: 'Multi-System Action', desc: 'Syncs CRM, schedules demo & alerts Slack', status: 'Complete' }
      ],
      logs: [
        { tag: 'TRIGGER', text: 'New inbound webhook event received: { company: "NexusTech", size: "50-200" }' },
        { tag: 'AI_AGENT', text: 'Claude 3.5 analyzing prospect metadata... ICP Match Score: 96/100 (Tier-1 Enterprise).' },
        { tag: 'GUARDRAIL', text: 'Executing schema check: Email verified, no disposable domain detected.' },
        { tag: 'SYNC', text: 'Created Deal #9482 in HubSpot CRM -> Pipeline: High Priority Inbound.' },
        { tag: 'SUCCESS', text: 'Autonomous workflow finished in 680ms. Notification dispatched to #sales-vip.' }
      ]
    },
    'invoice-rag': {
      nodes: [
        { title: 'PDF Ingestion', desc: 'Multimodal scanner receives 48-page vendor invoice', status: 'Document Ready' },
        { title: 'GPT-4o Vision', desc: 'Extracts line items, tax IDs, and payment terms', status: 'OCR Extraction' },
        { title: 'ERP Match Check', desc: 'Compares line items against Purchase Order #PO-882', status: 'Reconciled' },
        { title: 'QuickBooks Sync', desc: 'Schedules approved ACH transfer with audit logs', status: 'Complete' }
      ],
      logs: [
        { tag: 'TRIGGER', text: 'Ingested raw multi-page PDF (Freight_Manifest_Inv_8829.pdf, 3.8MB).' },
        { tag: 'VISION_AI', text: 'GPT-4o parsed 42 line items. Total invoice amount: $128,450.00 USD.' },
        { tag: 'VALIDATION', text: 'PO-882 match confirmed with 100% item matching and 0% discrepancy.' },
        { tag: 'ERP_WRITE', text: 'Posted expense ledger entry in QuickBooks Online API (Status: Approved).' },
        { tag: 'SUCCESS', text: 'End-to-end invoice reconciliation executed in 1.14s without human input.' }
      ]
    },
    'support-agent': {
      nodes: [
        { title: 'Customer Chat Query', desc: 'User asks complex API authentication question', status: 'Inbound Message' },
        { title: 'Vector RAG Search', desc: 'Pinecone retrieves authenticated developer docs', status: 'Semantic Search' },
        { title: 'Safety Verification', desc: 'Validates API key redaction & response tone', status: 'Sanitized' },
        { title: 'Instant Stream Reply', desc: 'Answers with exact code snippet in 320ms', status: 'Resolved' }
      ],
      logs: [
        { tag: 'TRIGGER', text: 'Incoming support ticket #3910 via Web Widget: "How to rotate API keys?"' },
        { tag: 'RAG_QUERY', text: 'Pinecone top_k=3 vector similarity search returned /docs/auth/key-rotation (score: 0.94).' },
        { tag: 'AI_AGENT', text: 'Synthesized tailored answer with step-by-step curl command.' },
        { tag: 'GUARDRAIL', text: 'Anti-hallucination check: 100% grounded in official docs.' },
        { tag: 'SUCCESS', text: 'Customer resolved in 410ms. CSAT projected: 5.0/5.0.' }
      ]
    },
    'market-intel': {
      nodes: [
        { title: 'Scheduled Cron Trigger', desc: 'Monitors competitor pricing & product releases', status: 'Scraping Triggered' },
        { title: 'Multi-Agent Swarm', desc: '3 CrewAI agents extract pricing tables & feature diffs', status: 'Deep Analysis' },
        { title: 'Insight Synthesis', desc: 'Summarizes strategic threat level and action items', status: 'Report Generated' },
        { title: 'Executive Brief', desc: 'Dispatches PDF digest to Slack & Notion database', status: 'Complete' }
      ],
      logs: [
        { tag: 'TRIGGER', text: 'Daily competitive intelligence cron triggered at 06:00:00 UTC.' },
        { tag: 'SWARM', text: 'Agent 1 (Scraper) & Agent 2 (Financial Analyst) evaluated 14 target competitor pages.' },
        { tag: 'AI_AGENT', text: 'Detected new enterprise tier pricing change on Competitor X ($499 -> $799/mo).' },
        { tag: 'WRITE_DB', text: 'Updated Competitor Matrix database in Notion API.' },
        { tag: 'SUCCESS', text: 'Morning Intelligence Brief dispatched to #exec-leadership Slack channel.' }
      ]
    }
  };

  function updatePipelineUI(pipelineKey) {
    const data = pipelines[pipelineKey] || pipelines['lead-gen'];
    if (!data) return;

    for (let i = 0; i < 4; i++) {
      const nodeEl = document.getElementById(`node-${i + 1}`);
      const titleEl = document.getElementById(`node${i + 1}-title`);
      const descEl = document.getElementById(`node${i + 1}-desc`);

      if (nodeEl && titleEl && descEl) {
        nodeEl.classList.remove('active', 'completed');
        titleEl.textContent = data.nodes[i].title;
        descEl.textContent = data.nodes[i].desc;
        const statusBadge = nodeEl.querySelector('.node-status-badge');
        if (statusBadge) statusBadge.textContent = 'Standby';
        const stepNum = nodeEl.querySelector('.node-step-indicator span');
        if (stepNum) stepNum.textContent = `STEP 0${i + 1}`;
      }
    }
  }

  pipelineSelector.addEventListener('change', (e) => {
    updatePipelineUI(e.target.value);
  });

  let isRunning = false;

  runBtn.addEventListener('click', () => {
    if (isRunning) return;
    isRunning = true;
    runBtn.disabled = true;

    const currentPipeline = pipelines[pipelineSelector.value] || pipelines['lead-gen'];

    runBtn.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="spin"><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/></svg>
      <span>Executing Pipeline...</span>
    `;

    consoleOutput.innerHTML = '';

    // Reset nodes
    for (let i = 1; i <= 4; i++) {
      const node = document.getElementById(`node-${i}`);
      if (node) {
        node.classList.remove('active', 'completed');
        const badge = node.querySelector('.node-status-badge');
        if (badge) badge.textContent = 'Queued';
      }
    }

    let step = 0;

    function executeStep() {
      if (step < 4) {
        const activeNode = document.getElementById(`node-${step + 1}`);
        if (activeNode) {
          activeNode.classList.add('active');
          const badge = activeNode.querySelector('.node-status-badge');
          if (badge) badge.textContent = 'Executing...';
        }

        const log = currentPipeline.logs[step];
        const logEl = document.createElement('div');
        logEl.className = 'log-entry';
        const now = new Date().toLocaleTimeString();

        const timeSpan = document.createElement('span');
        timeSpan.className = 'log-time';
        timeSpan.textContent = `[${now}]`;

        const tagSpan = document.createElement('span');
        tagSpan.className = 'log-tag exec';
        tagSpan.textContent = log.tag;

        const textSpan = document.createElement('span');
        textSpan.className = 'log-text';
        textSpan.textContent = log.text;

        logEl.appendChild(timeSpan);
        logEl.appendChild(document.createTextNode(' '));
        logEl.appendChild(tagSpan);
        logEl.appendChild(document.createTextNode(' '));
        logEl.appendChild(textSpan);

        consoleOutput.appendChild(logEl);
        consoleOutput.scrollTop = consoleOutput.scrollHeight;

        setTimeout(() => {
          if (activeNode) {
            activeNode.classList.remove('active');
            activeNode.classList.add('completed');
            const badge = activeNode.querySelector('.node-status-badge');
            if (badge) badge.textContent = '✓ ' + currentPipeline.nodes[step].status;
          }
          step++;
          executeStep();
        }, 750);
      } else {
        const finalLog = currentPipeline.logs[4];
        if (finalLog) {
          const logEl = document.createElement('div');
          logEl.className = 'log-entry';
          const now = new Date().toLocaleTimeString();

          const timeSpan = document.createElement('span');
          timeSpan.className = 'log-time';
          timeSpan.textContent = `[${now}]`;

          const tagSpan = document.createElement('span');
          tagSpan.className = 'log-tag success';
          tagSpan.textContent = 'COMPLETE';

          const textSpan = document.createElement('span');
          textSpan.className = 'log-text';
          textSpan.textContent = finalLog.text;

          logEl.appendChild(timeSpan);
          logEl.appendChild(document.createTextNode(' '));
          logEl.appendChild(tagSpan);
          logEl.appendChild(document.createTextNode(' '));
          logEl.appendChild(textSpan);

          consoleOutput.appendChild(logEl);
          consoleOutput.scrollTop = consoleOutput.scrollHeight;
        }

        runBtn.disabled = false;
        runBtn.innerHTML = `
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5 3 19 12 5 21 5 3"/></svg>
          <span>Run Live Simulation</span>
        `;
        isRunning = false;
        showToast('Autonomous pipeline executed successfully!');
      }
    }

    executeStep();
  });
}

/* ==========================================================================
   5. Interactive B2B AI ROI Calculator
   ========================================================================== */
function initRoiCalculator() {
  const teamSizeRange = document.getElementById('teamSizeRange');
  const hourlyRateRange = document.getElementById('hourlyRateRange');
  const hoursPerWeekRange = document.getElementById('hoursPerWeekRange');

  const teamSizeDisplay = document.getElementById('teamSizeDisplay');
  const hourlyRateDisplay = document.getElementById('hourlyRateDisplay');
  const hoursPerWeekDisplay = document.getElementById('hoursPerWeekDisplay');

  const annualSavingsVal = document.getElementById('annualSavingsVal');
  const hoursReclaimedVal = document.getElementById('hoursReclaimedVal');
  const paybackVal = document.getElementById('paybackVal');
  const roiMultiplierVal = document.getElementById('roiMultiplierVal');
  const weeklyCapacityVal = document.getElementById('weeklyCapacityVal');

  if (!teamSizeRange || !annualSavingsVal) return;

  function calculate() {
    const team = parseInt(teamSizeRange.value, 10);
    const rate = parseInt(hourlyRateRange.value, 10);
    const hours = parseInt(hoursPerWeekRange.value, 10);

    teamSizeDisplay.textContent = `${team} ${team === 1 ? 'Employee' : 'Employees'}`;
    hourlyRateDisplay.textContent = `$${rate} / hr`;
    hoursPerWeekDisplay.textContent = `${hours} Hours / wk`;

    // Conservative 78% automation efficiency
    const totalWeeklyManualHours = team * hours;
    const weeklyReclaimed = Math.round(totalWeeklyManualHours * 0.78);
    const annualReclaimed = weeklyReclaimed * 52;
    const annualGrossSavings = annualReclaimed * rate;

    // Projected Payback & Multiplier
    const estimatedBuildCost = Math.min(35000, Math.max(7500, Math.round(annualGrossSavings * 0.12)));
    const paybackDays = Math.max(14, Math.round((estimatedBuildCost / (annualGrossSavings / 365))));
    const multiplier = (annualGrossSavings / estimatedBuildCost).toFixed(1);

    // Format outputs
    annualSavingsVal.textContent = `$${annualGrossSavings.toLocaleString()}`;
    hoursReclaimedVal.textContent = `${annualReclaimed.toLocaleString()} hrs`;
    paybackVal.textContent = `< ${paybackDays} Days`;
    roiMultiplierVal.textContent = `${multiplier}x`;
    weeklyCapacityVal.textContent = `+${weeklyReclaimed} hrs/wk`;
  }

  teamSizeRange.addEventListener('input', calculate);
  hourlyRateRange.addEventListener('input', calculate);
  hoursPerWeekRange.addEventListener('input', calculate);

  const claimRoiBtn = document.getElementById('claimRoiBtn');
  if (claimRoiBtn) {
    claimRoiBtn.addEventListener('click', () => {
      const contactSection = document.getElementById('contact');
      if (contactSection) {
        contactSection.scrollIntoView({ behavior: 'smooth' });
        const nameField = document.getElementById('clientName');
        if (nameField) nameField.focus();
      }
    });
  }

  calculate();
}

/* ==========================================================================
   6. Interactive FAQ Accordion
   ========================================================================== */
function initFaqAccordion() {
  const items = document.querySelectorAll('.faq-item');
  items.forEach(item => {
    const question = item.querySelector('.faq-question');
    if (question) {
      question.addEventListener('click', () => {
        const isActive = item.classList.contains('active');
        items.forEach(other => other.classList.remove('active'));
        if (!isActive) {
          item.classList.add('active');
        }
      });
    }
  });
}

/* ==========================================================================
   7. Booking Modal Controller
   ========================================================================== */
function initBookingModal() {
  const modal = document.getElementById('bookingModal');
  const openBtn = document.getElementById('openBookingModalBtn');
  const heroBookingBtn = document.getElementById('heroBookingBtn');
  const closeBtn = document.getElementById('closeModalBtn');
  const slotButtons = document.querySelectorAll('.cal-slot-btn');
  const confirmSlotBtn = document.getElementById('confirmSlotBtn');

  if (!modal) return;

  function openModal() {
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    modal.classList.remove('open');
    document.body.style.overflow = '';
  }

  if (openBtn) openBtn.addEventListener('click', openModal);
  if (heroBookingBtn) heroBookingBtn.addEventListener('click', openModal);
  if (closeBtn) closeBtn.addEventListener('click', closeModal);

  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('open')) {
      closeModal();
    }
  });

  slotButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      slotButtons.forEach(b => {
        b.style.borderColor = 'var(--border-subtle)';
        b.style.background = 'rgba(255,255,255,0.05)';
        b.style.color = '#fff';
      });
      btn.style.borderColor = 'var(--accent-cyan)';
      btn.style.background = 'rgba(0, 240, 255, 0.15)';
      btn.style.color = 'var(--accent-cyan)';
    });
  });

  if (confirmSlotBtn) {
    confirmSlotBtn.addEventListener('click', () => {
      closeModal();
      showToast('🎉 Strategy Call Reserved! Calendar invite sent to your email.');
    });
  }
}

/* ==========================================================================
   8. On-Page Discovery Audit Form (Secured & Rate Limited)
   ========================================================================== */
function initAuditForm() {
  const auditForm = document.getElementById('auditForm');
  if (!auditForm) return;

  let lastSubmitTime = 0;

  auditForm.addEventListener('submit', (e) => {
    e.preventDefault();

    const now = Date.now();
    if (now - lastSubmitTime < 3000) {
      showToast('⚠️ Please wait a moment before resubmitting.');
      return;
    }
    lastSubmitTime = now;

    const nameInput = document.getElementById('clientName');
    const emailInput = document.getElementById('clientEmail');
    const goalInput = document.getElementById('automationGoal');

    const rawName = nameInput ? nameInput.value.trim().substring(0, 80) : '';
    const rawEmail = emailInput ? emailInput.value.trim().substring(0, 100) : '';
    const rawGoal = goalInput && goalInput.selectedOptions.length > 0 ? goalInput.selectedOptions[0].text : 'AI Automation';

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (rawEmail && !emailPattern.test(rawEmail)) {
      showToast('⚠️ Please enter a valid email address.');
      return;
    }

    const cleanName = rawName.replace(/[<>'"&]/g, '');
    const cleanGoal = rawGoal.replace(/[<>'"&]/g, '');

    showToast(`Thank you, ${cleanName}! Your AI audit request for "${cleanGoal}" has been submitted.`);
    auditForm.reset();

    // Open booking modal to finalize call time
    setTimeout(() => {
      const modal = document.getElementById('bookingModal');
      if (modal) {
        modal.classList.add('open');
        document.body.style.overflow = 'hidden';
      }
    }, 1200);
  });
}

/* ==========================================================================
   9. AI Concierge Chatbot Widget (English Enterprise Knowledge)
   ========================================================================== */
function initAiConcierge() {
  const aiToggle = document.getElementById('aiToggle');
  const aiChatWindow = document.getElementById('aiChatWindow');
  const closeChatBtn = document.getElementById('closeChatBtn');
  const chatInput = document.getElementById('chatInput');
  const sendChatBtn = document.getElementById('sendChatBtn');
  const chatMessages = document.getElementById('chatMessages');
  const quickPills = document.querySelectorAll('.quick-pill');

  if (!aiToggle || !aiChatWindow || !chatMessages) return;

  let isBotTyping = false;

  aiToggle.addEventListener('click', () => {
    aiChatWindow.classList.toggle('open');
  });

  if (closeChatBtn) {
    closeChatBtn.addEventListener('click', () => {
      aiChatWindow.classList.remove('open');
    });
  }

  function appendMessage(text, sender) {
    const msg = document.createElement('div');
    msg.className = `chat-msg ${sender}`;
    msg.textContent = text;
    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  const knowledge = {
    roi: "Mekaoui's AI automations typically pay for themselves within 30 to 45 days. By automating 75-90% of manual repetitive tasks, clients save an average of $150k - $400k annually. Try out the interactive ROI calculator above!",
    tech: "Mekaoui architects using modern enterprise AI tools: LangGraph, CrewAI, OpenAI GPT-4o, Claude 3.5 Sonnet, LlamaIndex, Pinecone, self-hosted n8n, Make, Supabase, Python FastAPI, and seamless CRM APIs (Salesforce/HubSpot).",
    sdr: "Our Autonomous SDR agents qualify inbound leads in under 30 seconds, research prospect company financials, score ICP alignment, and schedule calls directly on your team's calendar.",
    book: "You can book a direct 15-minute operational audit with Mekaoui right now! Click the 'Book Strategy Call' button in the top menu or use the interactive scheduler.",
    security: "Security is paramount. We implement zero-retention enterprise API endpoints, encrypted credentials vaults, SOC2 privacy compliance, and multi-layer anti-hallucination guardrails.",
    default: "Mekaoui Abdelmounaim specializes in custom autonomous AI agent systems, internal RAG knowledge bases, and enterprise workflow integrations. Would you like to schedule a 15-min discovery call to discuss your exact requirements?"
  };

  function getAiResponse(userText) {
    const lower = userText.toLowerCase();

    if (lower.includes('roi') || lower.includes('cost') || lower.includes('saving') || lower.includes('payback')) {
      return knowledge.roi;
    }
    if (lower.includes('tech') || lower.includes('stack') || lower.includes('tool') || lower.includes('framework') || lower.includes('langchain') || lower.includes('n8n')) {
      return knowledge.tech;
    }
    if (lower.includes('sdr') || lower.includes('lead') || lower.includes('sales') || lower.includes('outreach') || lower.includes('prospect')) {
      return knowledge.sdr;
    }
    if (lower.includes('book') || lower.includes('call') || lower.includes('meeting') || lower.includes('schedule') || lower.includes('audit')) {
      return knowledge.book;
    }
    if (lower.includes('sec') || lower.includes('priv') || lower.includes('safe') || lower.includes('guardrail')) {
      return knowledge.security;
    }

    return knowledge.default;
  }

  function handleSend() {
    if (isBotTyping) return;
    const text = chatInput.value.trim().substring(0, 300);
    if (!text) return;

    appendMessage(text, 'user');
    chatInput.value = '';
    isBotTyping = true;

    setTimeout(() => {
      const reply = getAiResponse(text);
      appendMessage(reply, 'bot');
      isBotTyping = false;
    }, 400);
  }

  sendChatBtn.addEventListener('click', handleSend);
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleSend();
  });

  quickPills.forEach(pill => {
    pill.addEventListener('click', () => {
      if (isBotTyping) return;
      const query = pill.getAttribute('data-query');
      if (query) {
        appendMessage(query, 'user');
        isBotTyping = true;
        setTimeout(() => {
          const reply = getAiResponse(query);
          appendMessage(reply, 'bot');
          isBotTyping = false;
        }, 300);
      }
    });
  });
}

/* ==========================================================================
   10. Toast Notifications
   ========================================================================== */
function showToast(message) {
  const toast = document.getElementById('toast');
  const toastMsg = document.getElementById('toastMsg');
  if (!toast || !toastMsg) return;

  toastMsg.textContent = message;
  toast.classList.add('show');

  setTimeout(() => {
    toast.classList.remove('show');
  }, 4000);
}
