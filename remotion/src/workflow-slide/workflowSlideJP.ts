import type { WorkflowSlideContent } from "./types";

const placeholderAssetSrc = "downloading-pyemsi.mp4";

export const workflowSlideJapaneseContent: WorkflowSlideContent = {
    language: "ja",
    checklistTitle: "pyemsi ワークフロー",
    checklistItems: [
        {
            id: "open-workspace",
            label: "ワークスペースを開く",
            detail: "シミュレーション用フォルダーを開き、Explorer や各種ツールの基準フォルダーを設定します。",
        },
        {
            id: "run-simulation",
            label: "シミュレーションを実行",
            detail: "EMSolution の入力 JSON を開き、Run を押して External Terminal から pyemsol を起動します。",
        },
        {
            id: "convert-femap",
            label: "FEMAP ファイルを変換",
            detail: "最新の FEMAP メッシュと結果ファイルを VTK 出力へ変換し、可視化に備えます。",
        },
        {
            id: "field-plot",
            label: "Field Plot",
            detail: "変換済みの .pvd 結果を読み込み、Field Plot ダイアログでスカラーやベクトル表示を構成します。",
        },
        {
            id: "output-plot",
            label: "Output Plot",
            detail: "output.json から波形プロットを作成し、プレビュー後に pyemsi 内で開きます。",
        },
    ],
    scenes: [
        {
            type: "checklist",
            id: "checklist-open-workspace",
            checklistItemId: "open-workspace",
            durationInFrames: 120,
        },
        {
            type: "video",
            id: "video-open-workspace",
            checklistItemId: "open-workspace",
            assetSrc: "open-workspace.mp4",
            durationInFrames: 300,
        },
        {
            type: "checklist",
            id: "checklist-run-simulation",
            checklistItemId: "run-simulation",
            durationInFrames: 120,
        },
        {
            type: "video",
            id: "video-run-simulation",
            checklistItemId: "run-simulation",
            assetSrc: "run-simulation.mp4",
            durationInFrames: 630,
        },
        {
            type: "checklist",
            id: "checklist-convert-femap",
            checklistItemId: "convert-femap",
            durationInFrames: 120,
        },
        {
            type: "video",
            id: "video-convert-femap",
            checklistItemId: "convert-femap",
            assetSrc: "convert-femap.mp4",
            durationInFrames: 840,
        },
        {
            type: "checklist",
            id: "checklist-field-plot",
            checklistItemId: "field-plot",
            durationInFrames: 120,
        },
        {
            type: "video",
            id: "video-field-plot",
            checklistItemId: "field-plot",
            assetSrc: "field-plot.mp4",
            durationInFrames: 2070,
        },
        {
            type: "checklist",
            id: "checklist-output-plot",
            checklistItemId: "output-plot",
            durationInFrames: 120,
        },
        {
            type: "video",
            id: "video-output-plot",
            checklistItemId: "output-plot",
            assetSrc: "output-plot.mp4",
            durationInFrames: 1290,
        },
    ],
};