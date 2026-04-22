import type { IntroductionSlideContent } from "./types";

export const introductionSlideEnglishContent: IntroductionSlideContent = {
    language: "en",
    title: "What is pyemsi?",
    audioSrc: "introductionEN.wav",
    bullets: [
        "Python-based postprocessor for EMSolution",
        "Interactive 3D field visualization with VTK, a scientific visualization toolkit",
        "Output plotting with Matplotlib, the standard Python plotting library",
        "Python scripting and Jupyter Notebook support for interactive analysis",
    ],
    transcript: [
        "pyemsi is a Python-based postprocessor for EMSolution.",
        "It combines the main postprocessing tasks in one environment.",
        "It provides interactive 3D field visualization through a VTK-based workflow, and it draws output plots with Matplotlib.",
        "It also offers a Python scripting environment for advanced pyemsol workflows, and the same API can be used in Jupyter notebooks.",
    ],
};