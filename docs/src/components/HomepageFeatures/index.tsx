import type { ReactNode } from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  Svg?: React.ComponentType<React.ComponentProps<'svg'>>;
  Png?: string;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'EMSolution Support',
    Svg: require('@site/static/img/EMSolution_icon.svg').default,
    description: (
      <>
        pyemsi provides seamless support for EMSolution output files. EMSolution is a powerful
        simulation engine for computational electromagnetics, enabling efficient, accurate, and
        fast simulation and optimization of electric machines. pyemsi converts EMSolution FEMAP
        Neutral (.neu) files to VTK formats for advanced visualization and analysis in Python.
      </>
    ),
  },
  {
    title: 'Jupyter Notebook Support',
    Svg: require('@site/static/img/Jupyter_logo.svg').default,
    description: (
      <>
        pyemsi provides full Jupyter Notebook integration for interactive computing and visualization.
        Jupyter supports over 40 programming languages and enables sharing of computational documents
        with rich, interactive output including HTML, images, and custom visualizations. Explore your
        electromagnetic simulation results interactively with 3D visualization directly in your notebooks.
      </>
    ),
  },
  {
    title: 'PyVista Visualization',
    Png: require('@site/static/img/pyvista_logo.png').default,
    description: (
      <>
        pyemsi leverages PyVista for powerful 3D plotting and mesh analysis through a streamlined
        interface for VTK. PyVista provides a Pythonic, well-documented API for rapid prototyping,
        analysis, and visual integration of spatially referenced datasets. Perfect for finite element
        analysis visualization, stress plots, and exploring complex electromagnetic simulation results.
      </>
    ),
  },
];

function Feature({ title, Svg, Png, description }: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        {Svg && <Svg className={styles.featureSvg} role="img" />}
        {Png && <img src={Png} className={styles.featurePng} alt={title} />}
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
