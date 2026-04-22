import "./index.css";
import { Composition, Folder } from "remotion";
import { InstallationSlide } from "./installation-slide/InstallationSlide";
import { installationSlideEnglishContent } from "./installation-slide/installationSlideEN";
import { installationSlideJapaneseContent } from "./installation-slide/installationSlideJP";
import { getInstallationSlideDurationInFrames } from "./installation-slide/types";
import { IntroductionSlide } from "./introduction-slide/IntroductionSlide";
import { introductionSlideEnglishContent } from "./introduction-slide/introductionSlideEN";
import { introductionSlideJapaneseContent } from "./introduction-slide/introductionSlideJP";
import { WelcomeSlide } from "./welcome-slide/WelcomeSlide";
import { welcomeSlideEnglishContent } from "./welcome-slide/welcomeSlideEN";
import { welcomeSlideJapaneseContent } from "./welcome-slide/welcomeSlideJP";
import { WorkflowSlide } from "./workflow-slide/WorkflowSlide";
import { getWorkflowSlideDurationInFrames } from "./workflow-slide/types";
import { workflowSlideEnglishContent } from "./workflow-slide/workflowSlideEN";
import { workflowSlideJapaneseContent } from "./workflow-slide/workflowSlideJP";

const FPS = 30;
const HD_WIDTH = 1600;
const HD_HEIGHT = 1000;

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Folder name="Welcome-Slide">
        <Composition
          id="WelcomeSlide-English"
          component={WelcomeSlide}
          durationInFrames={60}
          fps={FPS}
          width={HD_WIDTH}
          height={HD_HEIGHT}
          defaultProps={{ content: welcomeSlideEnglishContent }}
        />
        <Composition
          id="WelcomeSlide-Japanese"
          component={WelcomeSlide}
          durationInFrames={60}
          fps={FPS}
          width={HD_WIDTH}
          height={HD_HEIGHT}
          defaultProps={{ content: welcomeSlideJapaneseContent }}
        />
      </Folder>

      <Folder name="Introduction-Slide">
        <Composition
          id="IntroductionSlide-English"
          component={IntroductionSlide}
          durationInFrames={800}
          fps={FPS}
          width={HD_WIDTH}
          height={HD_HEIGHT}
          defaultProps={{ content: introductionSlideEnglishContent }}
        />
        <Composition
          id="IntroductionSlide-Japanese"
          component={IntroductionSlide}
          durationInFrames={1100}
          fps={FPS}
          width={HD_WIDTH}
          height={HD_HEIGHT}
          defaultProps={{ content: introductionSlideJapaneseContent }}
        />
      </Folder>

      <Folder name="Installation-Slide">
        <Composition
          id="InstallationSlide-English"
          component={InstallationSlide}
          durationInFrames={getInstallationSlideDurationInFrames(
            installationSlideEnglishContent,
          )}
          fps={FPS}
          width={HD_WIDTH}
          height={HD_HEIGHT}
          defaultProps={{ content: installationSlideEnglishContent }}
        />
        <Composition
          id="InstallationSlide-Japanese"
          component={InstallationSlide}
          durationInFrames={getInstallationSlideDurationInFrames(
            installationSlideJapaneseContent,
          )}
          fps={FPS}
          width={HD_WIDTH}
          height={HD_HEIGHT}
          defaultProps={{ content: installationSlideJapaneseContent }}
        />
      </Folder>

      <Folder name="Workflow-Slide">
        <Composition
          id="WorkflowSlide-English"
          component={WorkflowSlide}
          durationInFrames={getWorkflowSlideDurationInFrames(
            workflowSlideEnglishContent,
          )}
          fps={FPS}
          width={HD_WIDTH}
          height={HD_HEIGHT}
          defaultProps={{ content: workflowSlideEnglishContent }}
        />
        <Composition
          id="WorkflowSlide-Japanese"
          component={WorkflowSlide}
          durationInFrames={getWorkflowSlideDurationInFrames(
            workflowSlideJapaneseContent,
          )}
          fps={FPS}
          width={HD_WIDTH}
          height={HD_HEIGHT}
          defaultProps={{ content: workflowSlideJapaneseContent }}
        />
      </Folder>
    </>
  );
};
