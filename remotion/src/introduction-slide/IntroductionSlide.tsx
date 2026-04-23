import {
    AbsoluteFill,
    Img,
    interpolate,
    spring,
    staticFile,
    useCurrentFrame,
    useVideoConfig,
} from "remotion";
import type { IntroductionSlideProps } from "./types";

const INTRO_TITLE_BUFFER_FRAMES = 45;
const INTRO_ITEM_DWELL_FRAMES = 300;

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

export const IntroductionSlide: React.FC<IntroductionSlideProps> = ({ content }) => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();
    const isJapanese = content.language === "ja";
    const sequenceFrame = Math.max(frame - INTRO_TITLE_BUFFER_FRAMES, 0);
    const hasActiveItem = frame >= INTRO_TITLE_BUFFER_FRAMES;
    const activeIndex = hasActiveItem
        ? Math.min(
            Math.floor(sequenceFrame / INTRO_ITEM_DWELL_FRAMES),
            content.items.length - 1,
        )
        : -1;
    const activeItem = activeIndex >= 0 ? content.items[activeIndex] : null;
    const activeItemStart = activeIndex >= 0
        ? INTRO_TITLE_BUFFER_FRAMES + activeIndex * INTRO_ITEM_DWELL_FRAMES
        : INTRO_TITLE_BUFFER_FRAMES;

    const panelEntrance = spring({
        fps,
        frame: frame + 10,
        config: {
            damping: 15,
            mass: 0.95,
            stiffness: 115,
        },
    });

    const titleEntrance = spring({
        fps,
        frame: frame + 4,
        config: {
            damping: 16,
            mass: 0.9,
            stiffness: 120,
        },
    });

    const rightPanelEntrance = spring({
        fps,
        frame: frame - activeItemStart,
        config: {
            damping: 15,
            mass: 0.92,
            stiffness: 118,
        },
    });

    const iconEntrance = spring({
        fps,
        frame: frame - activeItemStart,
        config: {
            damping: 15,
            mass: 0.88,
            stiffness: 120,
        },
    });

    const introEntrance = spring({
        fps,
        frame: frame - (activeItemStart + 28),
        config: {
            damping: 18,
            mass: 1,
            stiffness: 86,
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
                    padding: "50px",
                }}
            >
                <div
                    style={{
                        width: "100%",
                        height: "100%",
                        display: "flex",
                        alignItems: "stretch",
                        gap: 28,
                        padding: "72px 84px",
                        borderRadius: 44,
                        background: "rgba(255, 255, 255, 0.60)",
                        boxShadow: "0 32px 90px rgba(16, 36, 63, 0.12)",
                        backdropFilter: "blur(14px)",
                        opacity: interpolate(panelEntrance, [0, 1], [0, 1]),
                        transform: `translateY(${interpolate(panelEntrance, [0, 1], [34, 0])}px) scale(${interpolate(panelEntrance, [0, 1], [0.96, 1])})`,
                    }}
                >
                    <div
                        style={{
                            display: "flex",
                            flexDirection: "column",
                            justifyContent: "flex-start",
                            gap: 50,
                            width: "40%",
                        }}
                    >
                        <div
                            style={{
                                display: "flex",
                                flexDirection: "column",
                                gap: 18,
                                opacity: interpolate(titleEntrance, [0, 1], [0, 1]),
                                transform: `translateY(${interpolate(titleEntrance, [0, 1], [22, 0])}px)`,
                            }}
                        >
                            <div
                                style={{
                                    fontSize: isJapanese ? 72 : 69,
                                    fontWeight: 800,
                                    lineHeight: 1.04,
                                    letterSpacing: isJapanese ? 0 : -1.8,
                                }}
                            >
                                {content.title}
                            </div>
                        </div>

                        <div
                            style={{
                                display: "flex",
                                flexDirection: "column",
                                gap: 16,
                                paddingRight: 8,
                            }}
                        >
                            {content.items.map((item, index) => {
                                const itemStart = INTRO_TITLE_BUFFER_FRAMES + index * INTRO_ITEM_DWELL_FRAMES;
                                const itemEntrance = spring({
                                    fps,
                                    frame: frame - itemStart,
                                    config: {
                                        damping: 17,
                                        mass: 0.9,
                                        stiffness: 120,
                                    },
                                });

                                const isVisible = frame >= itemStart;
                                const isActive = index === activeIndex;

                                return (
                                    <div
                                        key={item.label}
                                        style={{
                                            display: "flex",
                                            alignItems: "center",
                                            gap: 18,
                                            padding: "18px 20px",
                                            borderRadius: 22,
                                            background: isActive
                                                ? "rgba(230, 238, 255, 0.98)"
                                                : "rgba(255, 255, 255, 0.78)",
                                            border: isActive
                                                ? "2px solid rgba(79, 120, 214, 0.28)"
                                                : "2px solid rgba(16, 36, 63, 0.06)",
                                            boxShadow: isActive
                                                ? "0 20px 44px rgba(73, 118, 214, 0.16)"
                                                : "0 18px 40px rgba(16, 36, 63, 0.08)",
                                            opacity: isVisible
                                                ? interpolate(itemEntrance, [0, 1], [0, 1])
                                                : 0,
                                            transform: isVisible
                                                ? `translateX(${interpolate(itemEntrance, [0, 1], [28, 0])}px)`
                                                : "translateX(28px)",
                                        }}
                                    >
                                        <div
                                            style={{
                                                width: 42,
                                                height: 42,
                                                borderRadius: 14,
                                                display: "flex",
                                                alignItems: "center",
                                                justifyContent: "center",
                                                background: isActive
                                                    ? "#4f78d6"
                                                    : index % 2 === 0
                                                        ? "rgba(111, 152, 255, 0.18)"
                                                        : "rgba(255, 157, 135, 0.18)",
                                                color: isActive
                                                    ? "#ffffff"
                                                    : index % 2 === 0
                                                        ? "#4564b8"
                                                        : "#c86d57",
                                                flexShrink: 0,
                                                fontSize: 22,
                                                fontWeight: 800,
                                            }}
                                        >
                                            {index + 1}
                                        </div>
                                        <div
                                            style={{
                                                fontSize: isJapanese ? 27 : 30,
                                                fontWeight: isActive ? 700 : 600,
                                                lineHeight: 1.28,
                                            }}
                                        >
                                            {item.label}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    <div
                        style={{
                            width: "60%",
                            display: "flex",
                            alignItems: "flex-start",
                            opacity: activeItem
                                ? interpolate(rightPanelEntrance, [0, 1], [0, 1])
                                : 0,
                            transform: activeItem
                                ? `translateY(${interpolate(rightPanelEntrance, [0, 1], [26, 0])}px)`
                                : "translateY(26px)",
                        }}
                    >
                        <div
                            style={{
                                width: "100%",
                                display: "flex",
                                flexDirection: "column",
                                justifyContent: "flex-start",
                                padding: "12px",
                            }}
                        >
                            {activeItem ? (
                                <>
                                    <div
                                        style={{
                                            display: "flex",
                                            alignItems: "flex-start",
                                            justifyContent: "center",
                                            marginBottom: 22,
                                        }}
                                    >
                                        <div
                                            style={{
                                                display: "flex",
                                                alignItems: "center",
                                                justifyContent: "center",
                                                flexShrink: 0,
                                                opacity: interpolate(iconEntrance, [0, 1], [0, 1]),
                                                transform: `scale(${interpolate(iconEntrance, [0, 1], [0.82, 1])}) translateY(${interpolate(iconEntrance, [0, 1], [18, 0])}px)`,
                                            }}
                                        >
                                            <Img
                                                src={staticFile(activeItem.iconSrc)}
                                                style={{
                                                    maxWidth: 700,
                                                    height: 250,
                                                    objectFit: "contain",
                                                }}
                                            />
                                        </div>
                                    </div>

                                    <div
                                        style={{
                                            marginTop: 10,
                                            opacity: interpolate(introEntrance, [0, 1], [0, 1]),
                                            transform: `translateY(${interpolate(introEntrance, [0, 1], [24, 0])}px)`,
                                        }}
                                    >
                                        <div
                                            style={{
                                                fontSize: isJapanese ? 28 : 31,
                                                fontWeight: 600,
                                                lineHeight: 1.44,
                                                color: "rgba(16, 36, 63, 0.9)",
                                            }}
                                        >
                                            {activeItem.intro}
                                        </div>
                                    </div>

                                    <div
                                        style={{
                                            display: "flex",
                                            flexDirection: "column",
                                            marginTop: 24,
                                        }}
                                    >
                                        {activeItem.points.map((point, index) => {
                                            const pointEntrance = spring({
                                                fps,
                                                frame: frame - (activeItemStart + 60 + index * 40),
                                                config: {
                                                    damping: 18,
                                                    mass: 1,
                                                    stiffness: 84,
                                                },
                                            });

                                            return (
                                                <div
                                                    key={point}
                                                    style={{
                                                        display: "flex",
                                                        alignItems: "flex-start",
                                                        gap: 16,
                                                        padding: "12px 0",
                                                        opacity: interpolate(pointEntrance, [0, 1], [0, 1]),
                                                        transform: `translateX(${interpolate(pointEntrance, [0, 1], [30, 0])}px)`,
                                                    }}
                                                >
                                                    <div
                                                        style={{
                                                            width: 12,
                                                            height: 12,
                                                            marginTop: 11,
                                                            borderRadius: 999,
                                                            background: index % 2 === 0 ? "#6f98ff" : "#ff9d87",
                                                            flexShrink: 0,
                                                        }}
                                                    />
                                                    <div
                                                        style={{
                                                            fontSize: isJapanese ? 22 : 24,
                                                            fontWeight: 500,
                                                            lineHeight: 1.45,
                                                            color: "rgba(16, 36, 63, 0.82)",
                                                        }}
                                                    >
                                                        {point}
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>

                                </>
                            ) : null}
                        </div>
                    </div>
                </div>
            </AbsoluteFill>
        </AbsoluteFill>
    );
};