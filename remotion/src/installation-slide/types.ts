export type InstallationSlideLanguage = "en" | "ja";

export type InstallationChecklistItem = {
    id: string;
    label: string;
    detail?: string;
};

export type InstallationChecklistScene = {
    type: "checklist";
    id: string;
    checklistItemId: string;
    durationInFrames: number;
};

export type InstallationVideoScene = {
    type: "video";
    id: string;
    checklistItemId: string;
    assetSrc: string;
    durationInFrames: number;
};

export type InstallationScene = InstallationChecklistScene | InstallationVideoScene;

export type InstallationSlideContent = {
    language: InstallationSlideLanguage;
    checklistItems: InstallationChecklistItem[];
    scenes: InstallationScene[];
};

export type InstallationSlideProps = {
    content: InstallationSlideContent;
};

export const getInstallationSlideDurationInFrames = (
    content: InstallationSlideContent,
): number => {
    return content.scenes.reduce(
        (total, scene) => total + scene.durationInFrames,
        0,
    );
};