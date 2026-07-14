import type { ReactNode } from 'react';
import Heading from '@theme/Heading';
import Layout from '@theme/Layout';

import InputControlFileEditor from '@site/src/components/InputControlFileEditor';

const description =
  'Open, inspect, compare, edit, and save EMSolution input control JSON files in your browser.';

export default function InputControlFileEditorPage(): ReactNode {
  return (
    <Layout title="Input Control File Editor" description={description}>
      <main className="container margin-vert--sm">
        <InputControlFileEditor />
        <p>
          Open one or more EMSolution input control files to inspect and edit
          them with the same Monaco editor used by Visual Studio Code. Use the
          breadcrumbs to move through nested objects and arrays, or split the
          editor to compare two files side by side.
        </p>
        <div className="alert alert--info" role="note">
          <strong>Your files stay private.</strong> Files are read and edited
          locally in your browser. Their contents are not uploaded, stored by
          this website, or sent to a server. For browser security, individually
          selected files expose their filename but not their full path.
        </div>
      </main>
    </Layout>
  );
}
