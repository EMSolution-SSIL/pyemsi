import BrowserOnly from '@docusaurus/BrowserOnly';
import React, {lazy, Suspense, type ReactNode} from 'react';

import styles from './styles.module.css';

const InputControlFileEditorClient = lazy(() => import('./InputControlFileEditorClient'));

function LoadingEditor(): ReactNode {
  return (
    <div className={styles.loading} role="status">
      Loading the input control file editor…
    </div>
  );
}

export default function InputControlFileEditor(): ReactNode {
  return (
    <BrowserOnly fallback={<LoadingEditor />}>
      {() => (
        <Suspense fallback={<LoadingEditor />}>
          <InputControlFileEditorClient />
        </Suspense>
      )}
    </BrowserOnly>
  );
}
