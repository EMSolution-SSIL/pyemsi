export type IntroductionSlideLanguage = "en" | "ja";

export type IntroductionSlideItem = {
    label: string;
    intro: string;
    points: string[];
    iconSrc: string;
};

export type IntroductionSlideContent = {
    language: IntroductionSlideLanguage;
    title: string;
    items: IntroductionSlideItem[];
};

export type IntroductionSlideProps = {
    content: IntroductionSlideContent;
};

const INTRO_TITLE_BUFFER_FRAMES = 45;
const INTRO_ITEM_DWELL_FRAMES = 300;
const INTRO_OUTRO_BUFFER_FRAMES = 45;

export const getIntroductionSlideDurationInFrames = (
    content: IntroductionSlideContent,
): number => {
    return (
        INTRO_TITLE_BUFFER_FRAMES +
        content.items.length * INTRO_ITEM_DWELL_FRAMES +
        INTRO_OUTRO_BUFFER_FRAMES
    );
};