import React, {type SVGProps} from 'react';

export type EditorIconName =
  | 'add'
  | 'apply'
  | 'cancel'
  | 'circuit'
  | 'close'
  | 'copy'
  | 'delete'
  | 'down'
  | 'edit'
  | 'external'
  | 'format'
  | 'fullscreen'
  | 'fullscreenExit'
  | 'network'
  | 'open'
  | 'save'
  | 'splitClose'
  | 'up';

interface EditorIconProps extends Omit<SVGProps<SVGSVGElement>, 'name'> {
  name: EditorIconName;
}

export default function EditorIcon({name, className, ...props}: EditorIconProps) {
  const paths = {
    add: <><path d="M12 5v14"/><path d="M5 12h14"/></>,
    apply: <path d="m5 12 4 4L19 6"/>,
    cancel: <><path d="m6 6 12 12"/><path d="m18 6-12 12"/></>,
    circuit: <><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 8h2v3H7z"/><path d="M15 8h2v3h-2z"/><path d="M7 15h2v1H7z"/><path d="M15 15h2v1h-2z"/><path d="M9 9.5h6"/><path d="M9 15.5h6"/></>,
    close: <><path d="m6 6 12 12"/><path d="m18 6-12 12"/></>,
    copy: <><rect width="13" height="13" x="9" y="9" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></>,
    delete: <><path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="m19 6-1 14H6L5 6"/><path d="M10 11v5"/><path d="M14 11v5"/></>,
    down: <><path d="M12 5v14"/><path d="m18 13-6 6-6-6"/></>,
    edit: <><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L8 18l-4 1 1-4Z"/></>,
    external: <><path d="M15 3h6v6"/><path d="m10 14 11-11"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></>,
    format: <><path d="M4 6h16"/><path d="M7 12h10"/><path d="M10 18h4"/></>,
    fullscreen: <><path d="M8 3H3v5"/><path d="M16 3h5v5"/><path d="M8 21H3v-5"/><path d="M16 21h5v-5"/></>,
    fullscreenExit: <><path d="M3 8h5V3"/><path d="M21 8h-5V3"/><path d="M3 16h5v5"/><path d="M21 16h-5v5"/></>,
    network: <><circle cx="5" cy="12" r="2"/><circle cx="19" cy="5" r="2"/><circle cx="19" cy="19" r="2"/><path d="m7 11 10-5"/><path d="m7 13 10 5"/></>,
    open: <><path d="M3 6h6l2 2h10v11H3Z"/><path d="m3 19 3-8h15"/></>,
    save: <><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2Z"/><path d="M17 21v-8H7v8"/><path d="M7 3v5h8"/></>,
    splitClose: <><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M12 3v18"/><path d="m15.5 9 3 3-3 3"/></>,
    up: <><path d="M12 19V5"/><path d="m6 11 6-6 6 6"/></>,
  } satisfies Record<EditorIconName, React.ReactNode>;

  return (
    <svg
      aria-hidden="true"
      className={className}
      fill="none"
      focusable="false"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2"
      {...props}>
      {paths[name]}
    </svg>
  );
}
