import type { IntroductionSlideContent } from "./types";

export const introductionSlideEnglishContent: IntroductionSlideContent = {
    language: "en",
    title: "What is pyemsi?",
    items: [
        {
            label: "EMSolution Postprocessor",
            intro: "pyemsi starts from EMSolution output and turns electromagnetic analysis results into a Python-friendly postprocessing workflow.",
            points: [
                "Built around EMSolution result files and FEMAP Neutral (.neu) data.",
                "Supports postprocessing for electric-machine and electromagnetic field studies.",
                "Prepares simulation data for downstream visualization and analysis in Python.",
            ],
            iconSrc: "EMSolution_icon.svg",
        },
        {
            label: "VTK Visualization",
            intro: "pyemsi uses PyVista to make 3D field and mesh inspection feel direct, visual, and interactive.",
            points: [
                "Leverages PyVista's high-level interface to the Visualization Toolkit (VTK).",
                "Works well for mesh exploration, and large spatial datasets.",
                "Brings scalar, vector, and contour visualization into a Python workflow,",
                "Adds sampling and data extraction to support deeper analysis and custom visualizations.",
            ],
            iconSrc: "pyvista_logo.png",
        },
        {
            label: "Matplotlib",
            intro: "pyemsi uses Matplotlib to turn `output` file content into readable 2D plots and 3D surface views for fast postprocessing.",
            points: [
                "Builds 2D engineering plots directly from output-file data.",
                "Creates 3D surfaces when field values are easier to inspect spatially.",
                "Keeps plotting and analysis in the same Python postprocessing workflow.",
            ],
            iconSrc: "matplotlib-logo.svg",
        },
        {
            label: "Jupyter notebooks",
            intro: "pyemsi fits naturally into notebooks for exploratory analysis, automation, and shareable computational documents.",
            points: [
                "Jupyter supports over 40 programming languages and rich interactive output.",
                "The same pyemsi workflow can move between scripts and notebooks.",
                "Notebook-based analysis is easy to share, revisit, and extend.",
            ],
            iconSrc: "Jupyter_logo.svg",
        },
    ],
};