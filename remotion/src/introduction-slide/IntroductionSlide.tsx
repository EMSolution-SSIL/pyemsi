import {
    AbsoluteFill,
    interpolate,
    spring,
    useCurrentFrame,
    useVideoConfig,
} from "remotion";
import { Audio, staticFile } from "remotion";
import type { IntroductionSlideProps } from "./types";

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

    return (
        <AbsoluteFill style={shellStyle}>
            {content.audioSrc ? <Audio src={staticFile(content.audioSrc)} /> : null}
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
                            justifyContent: "center",
                            gap: 28,
                            width: "100%",
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
                                    fontSize: content.language === "ja" ? 88 : 92,
                                    fontWeight: 800,
                                    lineHeight: 1.02,
                                    letterSpacing: content.language === "ja" ? 0 : -2.2,
                                }}
                            >
                                {content.title}
                            </div>
                        </div>

                        <div
                            style={{
                                display: "flex",
                                flexDirection: "column",
                                gap: 18,
                                marginTop: 10,
                            }}
                        >
                            {content.bullets.map((bullet, index) => {
                                const bulletEntrance = spring({
                                    fps,
                                    frame: frame - (18 + index * 10),
                                    config: {
                                        damping: 17,
                                        mass: 0.9,
                                        stiffness: 120,
                                    },
                                });

                                return (
                                    <div
                                        key={bullet}
                                        style={{
                                            display: "flex",
                                            alignItems: "center",
                                            gap: 20,
                                            padding: "18px 22px",
                                            borderRadius: 22,
                                            background: "rgba(255, 255, 255, 0.68)",
                                            boxShadow: "0 18px 40px rgba(16, 36, 63, 0.08)",
                                            opacity: interpolate(bulletEntrance, [0, 1], [0, 1]),
                                            transform: `translateX(${interpolate(bulletEntrance, [0, 1], [28, 0])}px)`,
                                        }}
                                    >
                                        <div
                                            style={{
                                                width: 14,
                                                height: 14,
                                                borderRadius: 999,
                                                background:
                                                    index % 2 === 0 ? "#6f98ff" : "#ff9d87",
                                                flexShrink: 0,
                                            }}
                                        />
                                        <div
                                            style={{
                                                fontSize: content.language === "ja" ? 31 : 33,
                                                fontWeight: 600,
                                                lineHeight: 1.35,
                                            }}
                                        >
                                            {bullet}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>
            </AbsoluteFill>
        </AbsoluteFill>
    );
};