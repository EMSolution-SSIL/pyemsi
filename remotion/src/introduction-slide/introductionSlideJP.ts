import type { IntroductionSlideContent } from "./types";

export const introductionSlideJapaneseContent: IntroductionSlideContent = {
    language: "ja",
    title: "pyemsiとは？",
    items: [
        {
            label: "EMSolution Postprocessor",
            intro: "pyemsiはEMSolutionの出力を起点にして、電磁界解析結果をPythonで扱いやすい後処理ワークフローへつなげます。",
            points: [
                "EMSolutionの結果ファイルやFEMAP Neutral（.neu）データを扱えます。",
                "電気機器や電磁界解析の後処理フローに合わせやすい構成です。",
                "可視化や追加解析へ進むためのPython側の入口を整えます。",
            ],
            iconSrc: "EMSolution_icon.svg",
        },
        {
            label: "VTK Visualization",
            intro: "pyemsiはPyVistaを利用して、三次元の場やメッシュの確認を直感的で対話的な体験にします。",
            points: [
                "Visualization Toolkit（VTK）をPythonらしく扱える高水準APIを活用します。",
                "メッシュ確認や大規模な空間データの探索に向いています。",
                "スカラー、ベクトル、等高線の可視化をPythonワークフローへ取り込みます。",
                "サンプリングやデータ抽出にも対応し、より深い解析やカスタム可視化につなげられます。",
            ],
            iconSrc: "pyvista_logo.png",
        },
        {
            label: "Matplotlib",
            intro: "pyemsiはMatplotlibを使って、`output`ファイルの内容を読みやすい2Dプロットや3Dサーフェス表示へ変換できます。",
            points: [
                "outputファイルのデータから2Dのエンジニアリングプロットを直接作成できます。",
                "場の値を空間的に確認したいときは3Dサーフェスとして表示できます。",
                "可視化と解析を同じPython後処理ワークフローの中で完結できます。",
            ],
            iconSrc: "matplotlib-logo.svg",
        },
        {
            label: "Jupyter notebooks",
            intro: "pyemsiはNotebook環境にも自然に入り、探索的解析、自動化、共有可能な計算ドキュメント作成を支えます。",
            points: [
                "Jupyterは40以上の言語と多様なインタラクティブ出力を支えています。",
                "同じpyemsiの流れをスクリプトとNotebookの両方で使えます。",
                "解析内容を共有しやすく、あとから再利用や拡張もしやすくなります。",
            ],
            iconSrc: "Jupyter_logo.svg",
        },
    ],
};