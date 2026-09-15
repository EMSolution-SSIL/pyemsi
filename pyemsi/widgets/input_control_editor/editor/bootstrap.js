const root = document.getElementById(
  'input-control-file-editor-root',
);

if (root) {
  const staticDirectory = new URL('.', import.meta.url);
  const bundleVersion = '__INPUT_CONTROL_EDITOR_BUNDLE_VERSION__';

  const stylesheet = document.createElement('link');
  stylesheet.rel = 'stylesheet';
  const stylesheetUrl = new URL(
    'editor.css',
    staticDirectory,
  );
  stylesheetUrl.searchParams.set('v', bundleVersion);
  stylesheet.href = stylesheetUrl.href;

  document.head.appendChild(stylesheet);

  const editorUrl = new URL('editor.js', staticDirectory);
  editorUrl.searchParams.set('v', bundleVersion);

  import(editorUrl.href);
}
