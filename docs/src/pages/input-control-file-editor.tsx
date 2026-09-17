import type { ReactNode } from 'react';
import Heading from '@theme/Heading';
import Layout from '@theme/Layout';

import InputControlFileEditor from '@site/src/components/InputControlFileEditor';

const description =
  'Open, inspect, compare, and edit EMSolution input control files as JSON, YAML, or TOML in your browser.';

export default function InputControlFileEditorPage(): ReactNode {
  return (
    <Layout title="Input Control File Editor" description={description}>
      <main className="container margin-vert--sm">
        <InputControlFileEditor />
        <p>
          Open one or more EMSolution input control files to inspect and edit
          them with the same Monaco editor used by Visual Studio Code. Switch
          each editor pane between JSON, YAML, and compatible TOML while using
          breadcrumbs to move through nested objects and arrays, or split the
          editor to compare two files side by side. Files always save as JSON;
          YAML and TOML comments are not included in the saved file. Recognized
          Recognized EMSolution input files also provide a unified Field Source
          editor for coils, current and potential sources, magnets, component
          networks, source series, power supplies, and external-circuit
          matrices—even when the Field Source array has not been created yet.
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
