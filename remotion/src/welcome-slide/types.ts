export type WelcomeSlideLanguage = "en" | "ja";

export type WelcomeSlideContent = {
  language: WelcomeSlideLanguage;
  title: string;
};

export type WelcomeSlideProps = {
  content: WelcomeSlideContent;
};