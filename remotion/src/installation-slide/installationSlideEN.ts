import type { InstallationSlideContent } from "./types";

export const installationSlideEnglishContent: InstallationSlideContent = {
    language: "en",
    checklistItems: [
        {
            id: "download",
            label: "Download the latest Windows installer",
            detail: "Get the latest pyemsi setup executable from GitHub Releases.",
        },
        {
            id: "install",
            label: "Install the pyemsi GUI application",
            detail: "Run the installer, review options, and finish the setup.",
        },
        {
            id: "pyemsol",
            label: "Install pyemsol inside pyemsi",
            detail: "Use the built-in IPython terminal and install the wheel with %pip.",
        },
        {
            id: "verify",
            label: "Verify the installation",
            detail: "Launch pyemsi, open the terminal, and confirm pyemsol works.",
        },
    ],
    scenes: [
        {
            type: "checklist",
            id: "checklist-download-pending",
            checklistItemId: "download",
            durationInFrames: 120,
        },
        {
            type: "video",
            id: "video-download",
            checklistItemId: "download",
            assetSrc: "downloading-pyemsi.mp4",
            durationInFrames: 290,
        },
        {
            type: "checklist",
            id: "checklist-download-complete",
            checklistItemId: "install",
            durationInFrames: 120,
        },
        {
            type: "video",
            id: "video-install",
            checklistItemId: "install",
            assetSrc: "installing-pyemsi.mp4",
            durationInFrames: 1020,
        },
        {
            type: "checklist",
            id: "checklist-install-complete",
            checklistItemId: "pyemsol",
            durationInFrames: 120,
        },
        {
            type: "video",
            id: "video-pyemsol",
            checklistItemId: "pyemsol",
            assetSrc: "installing-pyemsol.mp4",
            durationInFrames: 810,
        },
        {
            type: "checklist",
            id: "checklist-pyemsol-complete",
            checklistItemId: "verify",
            durationInFrames: 120,
        },
        {
            type: "video",
            id: "video-verify",
            checklistItemId: "verify",
            assetSrc: "verify-pyemsol.mp4",
            durationInFrames: 920,
        },
    ],
};