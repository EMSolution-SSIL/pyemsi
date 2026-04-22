import {
    AbsoluteFill,
    Sequence,
} from "remotion";
import type {
    InstallationChecklistItem,
    InstallationScene,
    InstallationSlideProps,
} from "./types";
import {
    WorkflowChecklistSceneView,
    WorkflowVideoSceneView,
    getWorkflowChecklistItemLabel,
    getWorkflowSceneStart,
} from "../shared/WorkflowSceneViews";

export const InstallationSlide: React.FC<InstallationSlideProps> = ({ content }) => {
    return (
        <AbsoluteFill>
            {content.scenes.map((scene, index) => {
                const start = getWorkflowSceneStart<InstallationScene>(content.scenes, index);
                const sceneTitle = getWorkflowChecklistItemLabel<InstallationChecklistItem>(
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
                                title="Installation Steps"
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