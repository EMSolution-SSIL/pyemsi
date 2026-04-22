import type { IntroductionSlideContent } from "./types";

export const introductionSlideJapaneseContent: IntroductionSlideContent = {
    language: "ja",
    title: "pyemsiとは？",
    audioSrc: "introductionJP.wav",
    bullets: [
        "EMSolution向けのPythonベースのポストプロセッサ",
        "VTKによるインタラクティブな3次元可視化。VTKは科学技術向けの可視化ツールキットです",
        "Matplotlibによる出力結果のプロット。MatplotlibはPythonの代表的な描画ライブラリです",
        "PythonスクリプトとJupyter Notebook対応。対話的な解析にも利用できます",
    ],
    transcript: [
        "pyemsiは、EMSolution向けのPythonベースのポストプロセッサです。",
        "主なポスト処理機能を、ひとつの環境にまとめています。",
        "VTKベースのワークフローにより、電磁界結果をインタラクティブに三次元可視化でき、出力結果はMatplotlibでプロットできます。",
        "さらに、高度なpyemsolワークフローのためのPythonスクリプト環境を備えており、同じAPIをJupyter Notebook環境から利用できます。",
    ],
};