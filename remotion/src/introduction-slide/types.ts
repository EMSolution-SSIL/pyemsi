export type IntroductionSlideLanguage = "en" | "ja";

export type IntroductionSlideContent = {
    language: IntroductionSlideLanguage;
    title: string;
    bullets: string[];
    transcript: string[];
    audioSrc: string;
};

export type IntroductionSlideProps = {
    content: IntroductionSlideContent;
};