import { AbsoluteFill, Sequence } from "remotion";
import {
    WorkflowChecklistSceneView,
    WorkflowVideoSceneView,
    getWorkflowChecklistItemLabel,
    getWorkflowSceneStart,
} from "../shared/WorkflowSceneViews";
import type {
    WorkflowSlideChecklistItem,
    WorkflowSlideProps,
    WorkflowSlideScene,
} from "./types";

export const WorkflowSlide: React.FC<WorkflowSlideProps> = ({ content }) => {
    return (
        <AbsoluteFill>
            {content.scenes.map((scene, index) => {
                const start = getWorkflowSceneStart<WorkflowSlideScene>(content.scenes, index);
                const sceneTitle = getWorkflowChecklistItemLabel<WorkflowSlideChecklistItem>(
                    content.checklistItems,
                    scene.checklistItemId,
                );

                return (
                    <Sequence
                        key={scene.id}
                        from={start}
                        durationInFrames={scene.durationInFrames}
                        premountFor={scene.type === "video" ? 20 : 0}
                    >
                        {scene.type === "checklist" ? (
                            <WorkflowChecklistSceneView
                                title={content.checklistTitle}
                                items={content.checklistItems}
                                scene={scene}
                                language={content.language}
                            />
                        ) : (
                            <WorkflowVideoSceneView
                                sceneTitle={sceneTitle}
                                scene={scene}
                                language={content.language}
                            />
                        )}
                    </Sequence>
                );
            })}
        </AbsoluteFill>
    );
};