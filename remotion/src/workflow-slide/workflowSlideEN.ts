import type { WorkflowSlideContent } from "./types";

const placeholderAssetSrc = "downloading-pyemsi.mp4";

export const workflowSlideEnglishContent: WorkflowSlideContent = {
    language: "en",
    checklistTitle: "pyemsi Workflow",
    checklistItems: [
        {
            id: "open-workspace",
            label: "Open Workspace",
            detail: "Open the simulation folder so Explorer, tabs, and tools resolve files from the correct workspace.",
        },
        {
            id: "run-simulation",
            label: "Run Simulation",
            detail: "Open the EMSolution input JSON and click Run to launch pyemsol in the External Terminal.",
        },
        {
            id: "convert-femap",
            label: "Convert FEMAP Files",
            detail: "Convert the latest FEMAP mesh and result files to VTK output for downstream visualization.",
        },
        {
            id: "field-plot",
            label: "Field Plot",
            detail: "Load the converted .pvd result and build scalar, contour, or vector views in the Field Plot dialog.",
        },
        {
            id: "output-plot",
            label: "Output Plot",
            detail: "Build waveform plots from output.json, preview them live, and open the figure inside pyemsi.",
        },
    ],
    scenes: [
        {
            type: "checklist",
            id: "checklist-open-workspace",
            checklistItemId: "open-workspace",
            durationInFrames: 120,
        },
        {
            type: "video",
            id: "video-open-workspace",
            checklistItemId: "open-workspace",
            assetSrc: "open-workspace.mp4",
            durationInFrames: 300,
        },
        {
            type: "checklist",
            id: "checklist-run-simulation",
            checklistItemId: "run-simulation",
            durationInFrames: 120,
        },
        {
            type: "video",
            id: "video-run-simulation",
            checklistItemId: "run-simulation",
            assetSrc: "run-simulation.mp4",
            durationInFrames: 630,
        },
        {
            type: "checklist",
            id: "checklist-convert-femap",
            checklistItemId: "convert-femap",
            durationInFrames: 120,
        },
        {
            type: "video",
            id: "video-convert-femap",
            checklistItemId: "convert-femap",
            assetSrc: "convert-femap.mp4",
            durationInFrames: 840,
        },
        {
            type: "checklist",
            id: "checklist-field-plot",
            checklistItemId: "field-plot",
            durationInFrames: 120,
        },
        {
            type: "video",
            id: "video-field-plot",
            checklistItemId: "field-plot",
            assetSrc: "field-plot.mp4",
            durationInFrames: 2070,
        },
        {
            type: "checklist",
            id: "checklist-output-plot",
            checklistItemId: "output-plot",
            durationInFrames: 120,
        },
        {
            type: "video",
            id: "video-output-plot",
            checklistItemId: "output-plot",
            assetSrc: "output-plot.mp4",
            durationInFrames: 1290,
        },
    ],
};