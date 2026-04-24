import type { ReactNode } from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/docs/installation">
            Docs
          </Link>
          <Link
            className="button button--outline button--secondary button--lg"
            to="/docs/api/installation">
            API
          </Link>
        </div>
      </div>
    </header>
  );
}

function HomepageVideos() {
  return (
    <section className={styles.videoSection}>
      <div className="container">
        <div className={styles.videoEmbed}>
          <div className={styles.videoFrame}>
            <iframe
              src="https://www.youtube.com/embed/FYmjsGyMiI0"
              title="pyemsi overview video in English"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              referrerPolicy="strict-origin-when-cross-origin"
              allowFullScreen
            />
          </div>
        </div>
      </div>
    </section>
  );
}

export default function Home(): ReactNode {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Description will go into a meta tag in <head />">
      <HomepageHeader />
      <main>
        <HomepageVideos />
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
