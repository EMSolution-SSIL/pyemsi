export type WorkflowSlideLanguage = "en" | "ja";

export type WorkflowSlideChecklistItem = {
    id: string;
    label: string;
    detail?: string;
};

export type WorkflowSlideChecklistScene = {
    type: "checklist";
    id: string;
    checklistItemId: string;
    durationInFrames: number;
};

export type WorkflowSlideVideoScene = {
    type: "video";
    id: string;
    checklistItemId: string;
    assetSrc: string;
    durationInFrames: number;
};

export type WorkflowSlideScene = WorkflowSlideChecklistScene | WorkflowSlideVideoScene;

export type WorkflowSlideContent = {
    language: WorkflowSlideLanguage;
    checklistTitle: string;
    checklistItems: WorkflowSlideChecklistItem[];
    scenes: WorkflowSlideScene[];
};

export type WorkflowSlideProps = {
    content: WorkflowSlideContent;
};

export const getWorkflowSlideDurationInFrames = (
    content: WorkflowSlideContent,
): number => {
    return content.scenes.reduce(
        (total, scene) => total + scene.durationInFrames,
        0,
    );
};