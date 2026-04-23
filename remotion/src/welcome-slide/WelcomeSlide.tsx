import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type { WelcomeSlideProps } from "./types";

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

export const WelcomeSlide: React.FC<WelcomeSlideProps> = ({ content }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const iconEntrance = spring({
    fps,
    frame,
    config: {
      damping: 14,
      mass: 0.9,
      stiffness: 120,
    },
  });

  const titleEntrance = spring({
    fps,
    frame: frame - 8,
    config: {
      damping: 16,
      mass: 0.9,
      stiffness: 120,
    },
  });

  const iconOpacity = interpolate(iconEntrance, [0, 1], [0, 1]);
  const titleOpacity = interpolate(titleEntrance, [0, 1], [0, 1]);

  return (
    <AbsoluteFill style={shellStyle}>
      <div style={accentOrbStyle(520, 520, -110, -90, "rgba(179, 205, 255, 0.45)")} />
      <div style={accentOrbStyle(380, 380, 680, 40, "rgba(255, 205, 199, 0.38)")} />
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "center",
          padding: "120px 140px",
        }}
      >
        <div
          style={{
            width: "100%",
            maxWidth: 1000,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            gap: 56,
            padding: "92px 84px",
            borderRadius: 44,
            background: "rgba(255, 255, 255, 0.72)",
            boxShadow: "0 32px 90px rgba(16, 36, 63, 0.12)",
            backdropFilter: "blur(14px)",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              transform: `translateY(${interpolate(iconEntrance, [0, 1], [42, 0])}px) scale(${interpolate(iconEntrance, [0, 1], [0.82, 1])})`,
              opacity: iconOpacity,
            }}
          >
            <Img
              src={staticFile("Icon.svg")}
              style={{
                width: 350,
                height: 350,
                objectFit: "contain",
              }}
            />
          </div>

          <div
            style={{
              textAlign: "center",
              opacity: titleOpacity,
              transform: `translateY(${interpolate(titleEntrance, [0, 1], [26, 0])}px)`,
            }}
          >
            <div
              style={{
                fontSize: content.language === "ja" ? 84 : 92,
                fontWeight: 800,
                lineHeight: 1.05,
                letterSpacing: content.language === "ja" ? 0 : -2.2,
              }}
            >
              {content.title}
            </div>
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};