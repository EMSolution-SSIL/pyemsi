import {
    AbsoluteFill,
    OffthreadVideo,
    interpolate,
    spring,
    staticFile,
    useCurrentFrame,
    useVideoConfig,
} from "remotion";

export type WorkflowLanguage = "en" | "ja";

export type WorkflowChecklistItem = {
    id: string;
    label: string;
    detail?: string;
};

export type WorkflowChecklistSceneData = {
    checklistItemId: string;
};

export type WorkflowVideoSceneData = {
    assetSrc: string;
};

const shellStyle: React.CSSProperties = {
    background:
        "radial-gradient(circle at top, rgba(222, 232, 255, 0.95) 0%, rgba(245, 247, 251, 1) 38%, rgba(230, 235, 243, 1) 100%)",
    color: "#10243f",
    fontFamily: '"Aptos", "Segoe UI", "Yu Gothic UI", "Hiragino Sans", "Meiryo", sans-serif',
    overflow: "hidden",
};

const accentOrbStyle = (
    width: number,
    height: number,
    top: number,
    right: number,
    color: string,
): React.CSSProperties => ({
    position: "absolute",
    width,
    height,
    top,
    right,
    borderRadius: "50%",
    background: color,
    filter: "blur(10px)",
    opacity: 0.5,
});

const panelStyle: React.CSSProperties = {
    width: "100%",
    height: "100%",
    display: "flex",
    padding: "20px 78px",
    borderRadius: 44,
    background: "rgba(255, 255, 255, 0.62)",
    boxShadow: "0 32px 90px rgba(16, 36, 63, 0.12)",
    backdropFilter: "blur(14px)",
};

const contentWidthStyle: React.CSSProperties = {
    width: "100%",
    display: "flex",
    flexDirection: "column",
};

export const getWorkflowSceneStart = <T extends { durationInFrames: number }>(
    scenes: T[],
    index: number,
): number => {
    return scenes
        .slice(0, index)
        .reduce((total, scene) => total + scene.durationInFrames, 0);
};

export const getWorkflowChecklistItemLabel = <T extends WorkflowChecklistItem>(
    items: T[],
    checklistItemId: string,
): string => {
    const item = items.find((candidate) => candidate.id === checklistItemId);
    return item?.detail ?? item?.label ?? "";
};

const ChecklistCard: React.FC<{
    item: WorkflowChecklistItem;
    done: boolean;
    current: boolean;
    index: number;
    isJapanese: boolean;
}> = ({ item, done, current, index, isJapanese }) => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();

    const entrance = spring({
        fps,
        frame: frame - (10 + index * 8),
        config: {
            damping: 15,
            mass: 0.9,
            stiffness: 125,
        },
    });

    return (
        <div
            style={{
                display: "flex",
                alignItems: "flex-start",
                gap: 22,
                padding: "24px 26px",
                borderRadius: 28,
                background: done
                    ? "rgba(222, 242, 226, 0.95)"
                    : current
                        ? "rgba(224, 235, 255, 0.96)"
                        : "rgba(255, 255, 255, 0.82)",
                border: done
                    ? "2px solid rgba(72, 145, 88, 0.24)"
                    : current
                        ? "2px solid rgba(73, 118, 214, 0.3)"
                        : "2px solid rgba(16, 36, 63, 0.06)",
                boxShadow: current
                    ? "0 22px 48px rgba(73, 118, 214, 0.16)"
                    : "0 18px 40px rgba(16, 36, 63, 0.08)",
                opacity: interpolate(entrance, [0, 1], [0, 1]),
                transform: `translateX(${interpolate(entrance, [0, 1], [36, 0])}px)`,
            }}
        >
            <div
                style={{
                    width: 54,
                    height: 54,
                    borderRadius: 18,
                    flexShrink: 0,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 26,
                    fontWeight: 800,
                    background: done
                        ? "#4d9c5f"
                        : current
                            ? "#4f78d6"
                            : "rgba(111, 152, 255, 0.16)",
                    color: done || current ? "#ffffff" : "#3d5d97",
                }}
            >
                {done ? "✓" : index + 1}
            </div>
            <div
                style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: 8,
                    minWidth: 0,
                }}
            >
                <div
                    style={{
                        fontSize: isJapanese ? 34 : 36,
                        fontWeight: 700,
                        lineHeight: 1.2,
                    }}
                >
                    {item.label}
                </div>
                {item.detail ? (
                    <div
                        style={{
                            fontSize: isJapanese ? 22 : 24,
                            lineHeight: 1.4,
                            color: "rgba(16, 36, 63, 0.74)",
                        }}
                    >
                        {item.detail}
                    </div>
                ) : null}
            </div>
        </div>
    );
};

export const WorkflowChecklistSceneView: React.FC<{
    title: string;
    items: WorkflowChecklistItem[];
    scene: WorkflowChecklistSceneData;
    language: WorkflowLanguage;
}> = ({ title, items, scene, language }) => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();
    const isJapanese = language === "ja";

    const panelEntrance = spring({
        fps,
        frame: frame + 8,
        config: {
            damping: 15,
            mass: 0.95,
            stiffness: 115,
        },
    });

    const titleEntrance = spring({
        fps,
        frame: frame + 2,
        config: {
            damping: 16,
            mass: 0.9,
            stiffness: 120,
        },
    });

    return (
        <AbsoluteFill style={shellStyle}>
            <div style={accentOrbStyle(520, 520, -110, -90, "rgba(179, 205, 255, 0.45)")} />
            <div style={accentOrbStyle(380, 380, 680, 40, "rgba(255, 205, 199, 0.38)")} />
            <AbsoluteFill
                style={{
                    alignItems: "center",
                    justifyContent: "center",
                    padding: "30px 50px",
                }}
            >
                <div
                    style={{
                        ...panelStyle,
                        opacity: interpolate(panelEntrance, [0, 1], [0, 1]),
                        transform: `translateY(${interpolate(panelEntrance, [0, 1], [34, 0])}px) scale(${interpolate(panelEntrance, [0, 1], [0.96, 1])})`,
                    }}
                >
                    <div style={{ ...contentWidthStyle, gap: 26 }}>
                        <div
                            style={{
                                display: "flex",
                                flexDirection: "column",
                                gap: 12,
                                opacity: interpolate(titleEntrance, [0, 1], [0, 1]),
                                transform: `translateY(${interpolate(titleEntrance, [0, 1], [22, 0])}px)`,
                            }}
                        >
                            <div
                                style={{
                                    fontSize: isJapanese ? 78 : 82,
                                    fontWeight: 800,
                                    lineHeight: 1.05,
                                    letterSpacing: isJapanese ? 0 : -2,
                                }}
                            >
                                {title}
                            </div>
                        </div>

                        <div
                            style={{
                                display: "grid",
                                gridTemplateColumns: "1fr",
                                gap: 18,
                                marginTop: 8,
                            }}
                        >
                            {items.map((item, index) => {
                                const currentIndex = items.findIndex(
                                    (candidate) => candidate.id === scene.checklistItemId,
                                );
                                const isCompleted = index < currentIndex;
                                const isCurrent = item.id === scene.checklistItemId;

                                return (
                                    <ChecklistCard
                                        key={item.id}
                                        item={item}
                                        done={isCompleted}
                                        current={isCurrent}
                                        index={index}
                                        isJapanese={isJapanese}
                                    />
                                );
                            })}
                        </div>
                    </div>
                </div>
            </AbsoluteFill>
        </AbsoluteFill>
    );
};

export const WorkflowVideoSceneView: React.FC<{
    sceneTitle: string;
    scene: WorkflowVideoSceneData;
    language: WorkflowLanguage;
}> = ({ sceneTitle, scene, language }) => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();
    const isJapanese = language === "ja";

    const panelEntrance = spring({
        fps,
        frame: frame + 8,
        config: {
            damping: 15,
            mass: 0.95,
            stiffness: 115,
        },
    });

    const textEntrance = spring({
        fps,
        frame: frame + 2,
        config: {
            damping: 16,
            mass: 0.9,
            stiffness: 120,
        },
    });

    return (
        <AbsoluteFill style={shellStyle}>
            <div style={accentOrbStyle(520, 520, -110, -90, "rgba(179, 205, 255, 0.45)")} />
            <div style={accentOrbStyle(380, 380, 680, 40, "rgba(255, 205, 199, 0.38)")} />
            <AbsoluteFill
                style={{
                    alignItems: "center",
                    justifyContent: "center",
                    padding: "20px",
                }}
            >
                <div
                    style={{
                        width: "100%",
                        height: "100%",
                        display: "flex",
                        flexDirection: "column",
                        gap: 5,
                        opacity: interpolate(panelEntrance, [0, 1], [0, 1]),
                        transform: `translateY(${interpolate(panelEntrance, [0, 1], [34, 0])}px) scale(${interpolate(panelEntrance, [0, 1], [0.96, 1])})`,
                    }}
                >
                    <div
                        style={{
                            flex: 1,
                            minHeight: 0,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                        }}
                    >
                        <div
                            style={{
                                height: "95%",
                                position: "relative",
                                borderRadius: 40,
                                overflow: "hidden",
                                boxShadow: "0 26px 60px rgba(16, 36, 63, 0.18)",
                            }}
                        >
                            <OffthreadVideo
                                pauseWhenBuffering
                                src={staticFile(scene.assetSrc)}
                                style={{
                                    width: "100%",
                                    height: "100%",
                                    objectFit: "contain",
                                }}
                            />
                        </div>
                    </div>

                    <div
                        style={{
                            width: "100%",
                            display: "flex",
                            flexDirection: "column",
                            gap: 14,
                            padding: "0 12px",
                        }}
                    >
                        <div
                            style={{
                                display: "flex",
                                flexDirection: "column",
                                gap: 10,
                                opacity: interpolate(textEntrance, [0, 1], [0, 1]),
                                transform: `translateY(${interpolate(textEntrance, [0, 1], [22, 0])}px)`,
                            }}
                        >
                            <div
                                style={{
                                    maxWidth: 1180,
                                    fontSize: isJapanese ? 24 : 28,
                                    fontWeight: 400,
                                    lineHeight: 1.45,
                                    letterSpacing: 0,
                                    color: "rgba(16, 36, 63, 0.8)",
                                }}
                            >
                                {sceneTitle}
                            </div>
                        </div>
                    </div>
                </div>
            </AbsoluteFill>
        </AbsoluteFill>
    );
};