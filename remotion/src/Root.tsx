import "./index.css";
import { Composition, Folder, Sequence } from "remotion";
import { InstallationSlide } from "./installation-slide/InstallationSlide";
import { installationSlideEnglishContent } from "./installation-slide/installationSlideEN";
import { installationSlideJapaneseContent } from "./installation-slide/installationSlideJP";
import { getInstallationSlideDurationInFrames } from "./installation-slide/types";
import { IntroductionSlide } from "./introduction-slide/IntroductionSlide";
import { introductionSlideEnglishContent } from "./introduction-slide/introductionSlideEN";
import { introductionSlideJapaneseContent } from "./introduction-slide/introductionSlideJP";
import { getIntroductionSlideDurationInFrames } from "./introduction-slide/types";
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
const WELCOME_SLIDE_DURATION_IN_FRAMES = 90;

type FinalVideoSlides = {
  welcome: typeof welcomeSlideEnglishContent;
  introduction: typeof introductionSlideEnglishContent;
  installation: typeof installationSlideEnglishContent;
  workflow: typeof workflowSlideEnglishContent;
};

const getFinalVideoDurationInFrames = (slides: FinalVideoSlides) => {
  return (
    WELCOME_SLIDE_DURATION_IN_FRAMES +
    getIntroductionSlideDurationInFrames(slides.introduction) +
    getInstallationSlideDurationInFrames(slides.installation) +
    getWorkflowSlideDurationInFrames(slides.workflow)
  );
};

const FinalVideo: React.FC<{ slides: FinalVideoSlides }> = ({ slides }) => {
  const introductionFrom = WELCOME_SLIDE_DURATION_IN_FRAMES;
  const installationFrom =
    introductionFrom +
    getIntroductionSlideDurationInFrames(slides.introduction);
  const workflowFrom =
    installationFrom +
    getInstallationSlideDurationInFrames(slides.installation);

  return (
    <>
      <Sequence durationInFrames={WELCOME_SLIDE_DURATION_IN_FRAMES}>
        <WelcomeSlide content={slides.welcome} />
      </Sequence>
      <Sequence
        from={introductionFrom}
        durationInFrames={getIntroductionSlideDurationInFrames(
          slides.introduction,
        )}
      >
        <IntroductionSlide content={slides.introduction} />
      </Sequence>
      <Sequence
        from={installationFrom}
        durationInFrames={getInstallationSlideDurationInFrames(
          slides.installation,
        )}
      >
        <InstallationSlide content={slides.installation} />
      </Sequence>
      <Sequence
        from={workflowFrom}
        durationInFrames={getWorkflowSlideDurationInFrames(slides.workflow)}
      >
        <WorkflowSlide content={slides.workflow} />
      </Sequence>
    </>
  );
};

const englishFinalVideoSlides: FinalVideoSlides = {
  welcome: welcomeSlideEnglishContent,
  introduction: introductionSlideEnglishContent,
  installation: installationSlideEnglishContent,
  workflow: workflowSlideEnglishContent,
};

const japaneseFinalVideoSlides: FinalVideoSlides = {
  welcome: welcomeSlideJapaneseContent,
  introduction: introductionSlideJapaneseContent,
  installation: installationSlideJapaneseContent,
  workflow: workflowSlideJapaneseContent,
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Folder name="Final-Video">
        <Composition
          id="FinalVideo-English"
          component={FinalVideo}
          durationInFrames={getFinalVideoDurationInFrames(
            englishFinalVideoSlides,
          )}
          fps={FPS}
          width={HD_WIDTH}
          height={HD_HEIGHT}
          defaultProps={{ slides: englishFinalVideoSlides }}
        />
        <Composition
          id="FinalVideo-Japanese"
          component={FinalVideo}
          durationInFrames={getFinalVideoDurationInFrames(
            japaneseFinalVideoSlides,
          )}
          fps={FPS}
          width={HD_WIDTH}
          height={HD_HEIGHT}
          defaultProps={{ slides: japaneseFinalVideoSlides }}
        />
      </Folder>

      <Folder name="Welcome-Slide">
        <Composition
          id="WelcomeSlide-English"
          component={WelcomeSlide}
          durationInFrames={WELCOME_SLIDE_DURATION_IN_FRAMES}
          fps={FPS}
          width={HD_WIDTH}
          height={HD_HEIGHT}
          defaultProps={{ content: welcomeSlideEnglishContent }}
        />
        <Composition
          id="WelcomeSlide-Japanese"
          component={WelcomeSlide}
          durationInFrames={WELCOME_SLIDE_DURATION_IN_FRAMES}
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
          durationInFrames={getIntroductionSlideDurationInFrames(
            introductionSlideEnglishContent,
          )}
          fps={FPS}
          width={HD_WIDTH}
          height={HD_HEIGHT}
          defaultProps={{ content: introductionSlideEnglishContent }}
        />
        <Composition
          id="IntroductionSlide-Japanese"
          component={IntroductionSlide}
          durationInFrames={getIntroductionSlideDurationInFrames(
            introductionSlideJapaneseContent,
          )}
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
