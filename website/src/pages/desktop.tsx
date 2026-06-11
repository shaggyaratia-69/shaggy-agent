import React from 'react';
import Layout from '@theme/Layout';
import styles from './desktop.module.css';

const installCommand = 'curl -fsSL https://raw.githubusercontent.com/shaggyaratia-69/shaggy-agent/main/install.sh | bash';

const platforms = [
  {
    icon: '',
    meta: 'macOS 12+',
    title: 'Mac OS',
    text: 'Install Shaggy locally on your Mac and keep your agent data under your own control.',
    href: 'https://raw.githubusercontent.com/shaggyaratia-69/shaggy-agent/main/install.sh',
    action: 'Install via terminal',
  },
  {
    icon: '⊞',
    meta: 'Windows 10/11',
    title: 'Windows',
    text: 'Use Shaggy from a Windows terminal with the same local-first setup and customer-ready command flow.',
    href: '/user-guide/windows-native',
    action: 'View Windows setup',
  },
  {
    icon: '🐧',
    meta: 'Any distro / WSL',
    title: 'Linux',
    text: 'Run Shaggy on Linux or WSL with a clean command-line install and isolated local configuration.',
    href: '/user-guide/windows-wsl-quickstart',
    action: 'View Linux setup',
  },
];

const features = [
  {
    n: '#1 Connect',
    icon: '✦',
    title: 'Lives Everywhere',
    text: 'Telegram, Signal, Discord, Slack, email, CLI, and local desktop workflows — one operator across the surfaces your business actually uses.',
  },
  {
    n: '#2 Remember',
    icon: '◆',
    title: 'Persistent Memory',
    text: 'Shaggy keeps useful preferences, workflows, and local operating knowledge so it gets sharper over time without exposing private data by default.',
  },
  {
    n: '#3 Schedule',
    icon: '◷',
    title: 'Focused Automation',
    text: 'Natural-language schedules for reports, briefings, checks, follow-ups, and local business routines that need to run consistently.',
  },
  {
    n: '#4 Delegate',
    icon: '▣',
    title: 'Tasks Multiplied',
    text: 'Spin up isolated subagents for coding, research, QA, and cleanup while the main operator keeps the business outcome in view.',
  },
  {
    n: '#5 Search',
    icon: '⌕',
    title: 'Browse and Build',
    text: 'Use web search, browser automation, files, terminal, image tools, voice, and MCP integrations from one local-first agent command center.',
  },
  {
    n: '#6 Protect',
    icon: '⛨',
    title: 'Private by Default',
    text: 'Designed around local control: secrets stay out of public installers, customer data stays local unless you intentionally send it somewhere.',
  },
];

function TerminalPreview() {
  return (
    <div className={styles.terminalCard} aria-label="Shaggy terminal preview">
      <div className={styles.terminalTop}>
        <span className={styles.dot} />
        <span className={styles.dot} />
        <span className={styles.dot} />
      </div>
      <div className={styles.terminalBody}>
        <pre className={styles.ascii}>{`╔════════════════════════════════╗
║        SHAGGY THE AGENT        ║
║  premium local AI command hub  ║
╚════════════════════════════════╝`}</pre>
        <p className={styles.cmdLine}><span className={styles.prompt}>$</span><span>shaggy setup</span></p>
        <p className={styles.cmdLine}><span className={styles.ok}>✓</span><span>local profile ready</span></p>
        <p className={styles.cmdLine}><span className={styles.ok}>✓</span><span>tools, skills, memory loaded</span></p>
        <p className={styles.cmdLine}><span className={styles.muted}>→</span><span>private operator mode active</span></p>
      </div>
    </div>
  );
}

export default function DesktopPage(): JSX.Element {
  return (
    <Layout
      title="Shaggy Desktop"
      description="Install Shaggy The Agent on macOS, Windows, and Linux. A premium local AI command center for business operators."
    >
      <main className={styles.desktopPage}>
        <section className={styles.hero}>
          <div className={styles.heroInner}>
            <div>
              <div className={styles.eyebrow}>Feature Preview · Desktop</div>
              <h1 className={styles.heroTitle}>Shaggy <span>The Agent</span></h1>
              <p className={styles.heroSubtitle}>
                A premium local AI command center for operators who want automation, memory,
                tools, messaging, and business execution without casually leaking private data.
              </p>
              <div className={styles.heroActions}>
                <a className={styles.primaryButton} href="#install">Install Shaggy</a>
                <a className={styles.secondaryButton} href="/getting-started/quickstart">Read the docs</a>
              </div>
            </div>
            <TerminalPreview />
          </div>
        </section>

        <section id="install" className={styles.platforms} aria-label="Install options">
          {platforms.map((platform) => (
            <article className={styles.platformCard} key={platform.title}>
              <div>
                <div className={styles.platformArt}>{platform.icon}</div>
                <p className={styles.platformMeta}>{platform.meta}</p>
                <h2>{platform.title}</h2>
                <p>{platform.text}</p>
              </div>
              <a className={styles.downloadButton} href={platform.href}>{platform.action} →</a>
            </article>
          ))}
        </section>

        <section className={styles.features}>
          <div className={styles.sectionHeader}>
            <div className={styles.eyebrow}>What it does</div>
            <h2>One agent. Every surface. Local-first control.</h2>
            <p>
              Shaggy is built for real operating work: messaging, research, coding, files,
              schedules, dashboards, skills, and follow-through — tied together in one assistant.
            </p>
          </div>
          <div className={styles.featureGrid}>
            {features.map((feature) => (
              <article className={styles.featureCard} key={feature.title}>
                <div className={styles.featureNumber}>{feature.n}</div>
                <div className={styles.featureIcon}>{feature.icon}</div>
                <h3>{feature.title}</h3>
                <p>{feature.text}</p>
              </article>
            ))}
          </div>
        </section>

        <section className={styles.cta}>
          <div className={styles.ctaBox}>
            <div>
              <h2>Install from terminal.</h2>
              <p>
                Keep the public installer simple. Protect real access with setup, activation,
                local credentials, and customer-specific configuration.
              </p>
            </div>
            <code className={styles.codePill}>{installCommand}</code>
          </div>
        </section>
      </main>
    </Layout>
  );
}
